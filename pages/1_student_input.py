import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import PROVINCE_CONFIGS, MAJOR_CATEGORIES
from db.models import StudentProfile
from db.connection import get_db
from pipeline.orchestrator import run_pipeline

st.title("考生信息填写")

CITIES = [
    "杭州", "上海", "南京", "苏州", "宁波", "无锡", "合肥", "北京",
    "广州", "深圳", "成都", "武汉", "西安", "天津", "长沙", "厦门",
    "温州", "金华", "扬州", "南通", "常州", "嘉兴", "绍兴",
]

province_options = {"浙江": "zhejiang", "江苏": "jiangsu", "上海": "shanghai"}
province_display = st.selectbox("省份/直辖市", list(province_options.keys()))
province = province_options[province_display]
cfg = PROVINCE_CONFIGS[province]

col1, col2 = st.columns(2)
with col1:
    min_score, max_score = cfg["score_range"]
    score = st.number_input("高考分数", min_value=min_score, max_value=max_score, value=600, step=1)
with col2:
    rank = st.number_input("省排名（位次）", min_value=1, max_value=300000, value=20000, step=100)

st.markdown("---")
st.subheader("选科信息")

subject_category = None
subjects = []

if province == "jiangsu":
    subject_category = st.radio(
        "首选科目（物理/历史）",
        cfg["subject_categories"],
        horizontal=True,
    )
    subjects = st.multiselect(
        f"再选科目（从以下选择{cfg['elective_count']}门）",
        cfg["subject_pool"],
        max_selections=cfg["elective_count"],
    )
    if len(subjects) != cfg["elective_count"]:
        st.warning(f"请选择恰好{cfg['elective_count']}门再选科目")
else:
    subjects = st.multiselect(
        f"选考科目（从以下选择{cfg['elective_count']}门）",
        cfg["subject_pool"],
        max_selections=cfg["elective_count"],
    )
    if len(subjects) != cfg["elective_count"]:
        st.warning(f"请选择恰好{cfg['elective_count']}门选考科目")

st.markdown("---")
st.subheader("志愿偏好")

col3, col4 = st.columns(2)
with col3:
    preferred_cities = st.multiselect("意向城市", CITIES, default=["杭州", "上海", "南京"])
    preferred_majors = st.multiselect("意向专业类别", MAJOR_CATEGORIES)
with col4:
    rejected_majors_input = st.text_input("排除专业（逗号分隔）", "")
    rejected_majors = [m.strip() for m in rejected_majors_input.split(",") if m.strip()]

    risk_pref_labels = {"均衡型": "balanced", "冲刺型": "aggressive", "稳妥型": "conservative"}
    risk_display = st.selectbox("填报策略偏好", list(risk_pref_labels.keys()))
    risk_preference = risk_pref_labels[risk_display]

st.markdown("---")
st.subheader("其他条件")

col5, col6 = st.columns(2)
with col5:
    accept_adjustment = st.checkbox("接受专业调剂", value=True)
    accept_sino_foreign = st.checkbox("接受中外合作办学", value=False)
with col6:
    budget_limit = st.number_input("学费预算上限（元/年，0为不限）", min_value=0, value=0, step=1000)
    health_limits = st.text_input("体检限制（如色盲、色弱等，无则留空）", "")

career_direction = st.text_input("职业方向（选填）", "")

st.markdown("---")

can_submit = True
if province == "jiangsu":
    if len(subjects) != cfg["elective_count"] or not subject_category:
        can_submit = False
else:
    if len(subjects) != cfg["elective_count"]:
        can_submit = False

if st.button("开始分析", type="primary", disabled=not can_submit, use_container_width=True):
    try:
        profile_data = {
            "province": province,
            "score": score,
            "rank": rank,
            "subject_category": subject_category,
            "subjects": subjects,
            "preferred_cities": preferred_cities,
            "preferred_majors": preferred_majors,
            "rejected_majors": rejected_majors,
            "budget_limit": budget_limit if budget_limit > 0 else None,
            "accept_adjustment": accept_adjustment,
            "accept_sino_foreign": accept_sino_foreign,
            "risk_preference": risk_preference,
            "health_limits": health_limits if health_limits else None,
            "career_direction": career_direction if career_direction else None,
        }

        student = StudentProfile(**profile_data)

        with st.spinner("正在分析中，请稍候..."):
            conn = get_db()
            result = run_pipeline(student, conn)
            conn.close()

        st.session_state["pipeline_result"] = result
        st.session_state["student_profile"] = student

        st.success(f"分析完成！共生成{len(result.all_recommendations)}个推荐志愿")
        st.info("请在左侧导航栏进入「推荐结果」页面查看详细结果")

    except ValueError as e:
        st.error(f"输入错误: {e}")
    except Exception as e:
        st.error(f"分析过程中出错: {e}")
