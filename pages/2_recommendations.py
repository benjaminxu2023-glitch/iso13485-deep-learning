import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import RISK_TIERS, STRATEGY_LABELS

st.title("推荐结果")

if "pipeline_result" not in st.session_state:
    st.warning("请先在「考生信息」页面完成分析")
    st.stop()

result = st.session_state["pipeline_result"]
student = st.session_state["student_profile"]

st.markdown(f"""
**考生概况**: {student.province.upper()} | 分数 {student.score} | 排名 {student.rank} | 选科 {', '.join(student.all_subjects())}
""")

st.markdown("---")

tab_labels = [f"{s.strategy_label}（{len(s.recommendations)}个志愿）" for s in result.strategies]
tabs = st.tabs(tab_labels)

for tab, strategy in zip(tabs, result.strategies):
    with tab:
        st.markdown(f"**策略说明**: {strategy.summary}")
        st.markdown(f"**整体风险**: {strategy.overall_risk}")

        dist_cols = st.columns(5)
        tier_keys = ["reach", "slight_reach", "match", "safe", "backup"]
        for col, tier_key in zip(dist_cols, tier_keys):
            tier_info = RISK_TIERS[tier_key]
            count = strategy.tier_distribution.get(tier_key, 0)
            col.metric(
                tier_info["label"],
                count,
                help=tier_info["description"],
            )

        st.markdown("---")

        if not strategy.recommendations:
            st.info("该策略下暂无推荐志愿")
            continue

        rows = []
        for i, rec in enumerate(strategy.recommendations, 1):
            tier_info = RISK_TIERS.get(rec.tier, {"label": rec.tier})
            ranks_str = " / ".join(str(r) for r in rec.historical_min_ranks) if rec.historical_min_ranks else "-"
            rows.append({
                "序号": i,
                "分层": tier_info["label"],
                "院校": rec.university_name,
                "专业": rec.major_name,
                "城市": rec.city or "-",
                "历年最低排名": ranks_str,
                "今年计划": rec.current_year_plan_count or "-",
                "学费": f"{rec.tuition}元" if rec.tuition else "-",
                "风险等级": rec.risk_level,
            })

        df = pd.DataFrame(rows)

        def _color_tier(val):
            colors = {"冲": "#FF4B4B", "稳冲": "#FFA500", "稳": "#00CC66", "保": "#4A90D9", "垫底": "#999999"}
            bg = colors.get(val, "")
            return f"background-color: {bg}; color: white; font-weight: bold" if bg else ""

        styled = df.style.map(_color_tier, subset=["分层"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("志愿详情")

        for rec in strategy.recommendations:
            tier_info = RISK_TIERS.get(rec.tier, {"label": rec.tier, "color": "#666"})
            with st.expander(f"{tier_info['label']} | {rec.university_name} — {rec.major_name}"):
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.markdown(f"**城市**: {rec.city or '未知'}")
                    st.markdown(f"**校区**: {rec.campus or '未知'}")
                    st.markdown(f"**学费**: {rec.tuition}元/年" if rec.tuition else "**学费**: 待确认")
                    st.markdown(f"**选科要求**: {', '.join(rec.subject_requirements) if rec.subject_requirements else '不限'}")
                with detail_col2:
                    st.markdown(f"**今年招生计划**: {rec.current_year_plan_count or '待确认'}人")
                    ranks_str = " → ".join(str(r) for r in rec.historical_min_ranks) if rec.historical_min_ranks else "无数据"
                    st.markdown(f"**历年最低排名**: {ranks_str}")
                    scores_str = " → ".join(str(s) for s in rec.historical_min_scores) if rec.historical_min_scores else "无数据"
                    st.markdown(f"**历年最低分数**: {scores_str}")

                st.markdown(f"**推荐理由**: {rec.reason}")
                st.markdown(f"**数据依据**: {rec.evidence}")

                if rec.manual_review_items:
                    st.markdown("**需人工复核**:")
                    for item in rec.manual_review_items:
                        st.markdown(f"- {item}")

                if rec.charter_risks:
                    st.markdown("**章程风险提示**:")
                    for risk in rec.charter_risks:
                        severity_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        icon = severity_colors.get(risk.severity, "⚪")
                        st.markdown(f"- {icon} [{risk.risk_type}] {risk.detail}")
