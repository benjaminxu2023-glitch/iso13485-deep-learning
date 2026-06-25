import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.title("风险审查报告")

if "pipeline_result" not in st.session_state:
    st.warning("请先在「考生信息」页面完成分析")
    st.stop()

result = st.session_state["pipeline_result"]
student = st.session_state["student_profile"]

st.markdown("---")
st.subheader("整体审核结果")

audit = result.audit_result
if audit:
    status_map = {
        "pass": ("✅ 通过", "success"),
        "warning": ("⚠️ 需关注", "warning"),
        "high_risk": ("🔴 高风险", "error"),
        "invalid": ("❌ 不合规", "error"),
    }
    status_text, status_type = status_map.get(audit.status, ("未知", "info"))

    if status_type == "success":
        st.success(f"审核结果: {status_text}")
    elif status_type == "warning":
        st.warning(f"审核结果: {status_text}")
    else:
        st.error(f"审核结果: {status_text}")

    if audit.high_risks:
        st.markdown("### 🔴 高风险项")
        for risk in audit.high_risks:
            st.error(risk)

    if audit.warnings:
        st.markdown("### ⚠️ 警告项")
        for warning in audit.warnings:
            st.warning(warning)

    if audit.issues:
        st.markdown("### 📋 其他问题")
        for issue in audit.issues:
            st.info(issue)

    if not audit.high_risks and not audit.warnings and not audit.issues:
        st.success("未发现显著风险，志愿梯度合理")

st.markdown("---")
st.subheader("招生章程风险汇总")

charter_risks = result.charter_risks
if charter_risks:
    for uni_key, risks in charter_risks.items():
        with st.expander(f"📋 {uni_key} — {len(risks)}项风险"):
            for risk in risks:
                severity_badge = {"high": "🔴 高", "medium": "🟡 中", "low": "🟢 低"}
                badge = severity_badge.get(risk.severity, "⚪ 未知")
                st.markdown(f"- **{badge}** [{risk.risk_type}] {risk.detail}")
else:
    st.info("未发现需要特别关注的招生章程风险")

st.markdown("---")
st.subheader("志愿分层风险分析")

tier_groups = {}
for rec in result.all_recommendations:
    tier_groups.setdefault(rec.tier, []).append(rec)

tier_order = ["reach", "slight_reach", "match", "safe", "backup"]
tier_labels = {"reach": "冲刺", "slight_reach": "稳冲", "match": "稳妥", "safe": "安全", "backup": "垫底"}

for tier in tier_order:
    recs = tier_groups.get(tier, [])
    if not recs:
        continue
    label = tier_labels.get(tier, tier)
    high_risk_count = sum(1 for r in recs if r.risk_level in ("high",))
    with st.expander(f"{label}志愿 — {len(recs)}个（高风险{high_risk_count}个）"):
        for rec in recs:
            risk_icon = "🔴" if rec.risk_level == "high" else "🟡" if "medium" in rec.risk_level else "🟢"
            st.markdown(f"{risk_icon} **{rec.university_name}** — {rec.major_name}")
            if rec.charter_risks:
                for cr in rec.charter_risks:
                    st.caption(f"  ↳ {cr.risk_type}: {cr.detail}")

st.markdown("---")
st.caption("⚠️ 本系统仅提供参考建议，不保证录取结果。最终志愿填报以各省教育考试院官方信息为准。")
