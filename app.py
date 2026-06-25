import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="志愿质检员 — 江浙沪高考志愿审核系统",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("志愿质检员")
st.sidebar.caption("江浙沪高考志愿审核系统")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**核心理念**: 每一个志愿选择都应可审计

**功能特色**:
- 基于省排名的精准匹配
- 分省规则引擎
- 招生章程风险审查
- 冲/稳/保梯度分析
- 三种填报策略对比
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
⚠️ **免责声明**

本系统仅提供参考建议，不保证录取结果。
最终志愿填报以各省教育考试院官方信息为准。
""")

st.title("志愿质检员")
st.subheader("江浙沪高考志愿风险审核与决策支持系统")

st.markdown("""
### 使用说明

1. **填写信息** — 在「考生信息」页面填写基本信息和偏好
2. **查看推荐** — 系统根据排名匹配生成冲/稳冲/稳/保/垫底志愿
3. **风险审查** — 查看每个志愿的风险分析和章程审核结果
4. **导出报告** — 下载PDF或Excel格式的完整审核报告

### 我们回答四个关键问题

| 问题 | 说明 |
|------|------|
| **能不能报？** | 选科要求、批次资格、体检限制等硬性条件检查 |
| **值不值得报？** | 基于省排名的历史数据匹配和趋势分析 |
| **风险有多大？** | 冲刺概率、调剂风险、章程隐藏条件等 |
| **证据在哪里？** | 每个推荐都附带历史数据和推荐逻辑 |

---
*请在左侧导航栏进入「考生信息」页面开始使用*
""")

db_path = Path("data/gaokao.db")
if not db_path.exists():
    st.warning("数据库尚未初始化，请先运行 `python setup_db.py`")
