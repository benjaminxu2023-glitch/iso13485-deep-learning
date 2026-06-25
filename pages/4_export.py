import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.title("导出报告")

if "pipeline_result" not in st.session_state:
    st.warning("请先在「考生信息」页面完成分析")
    st.stop()

result = st.session_state["pipeline_result"]
student = st.session_state["student_profile"]

st.markdown(f"""
**考生**: {student.province.upper()} | 分数 {student.score} | 排名 {student.rank}
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Excel报告")
    st.markdown("包含完整推荐列表、三种策略对比、风险审查详情")

    if st.button("生成Excel报告", type="primary", use_container_width=True):
        with st.spinner("正在生成Excel..."):
            try:
                from export.excel_report import generate_excel
                excel_bytes = generate_excel(result)
                st.download_button(
                    label="下载Excel报告",
                    data=excel_bytes,
                    file_name=f"志愿审核报告_{student.province}_{student.score}分.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"生成Excel失败: {e}")

with col2:
    st.subheader("PDF报告")
    st.markdown("包含考生信息、策略推荐、风险分析、免责声明")

    if st.button("生成PDF报告", type="primary", use_container_width=True):
        with st.spinner("正在生成PDF..."):
            try:
                from export.pdf_report import generate_pdf
                pdf_bytes = generate_pdf(result)
                st.download_button(
                    label="下载PDF报告",
                    data=pdf_bytes,
                    file_name=f"志愿审核报告_{student.province}_{student.score}分.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"生成PDF失败: {e}")

st.markdown("---")

st.subheader("离线选校工具")
st.markdown("生成一个可离线使用的HTML文件，包含江浙沪三地数据，支持智能推荐、手动选校、梯度检查")

if st.button("生成离线选校工具", type="secondary", use_container_width=True):
    with st.spinner("正在生成离线选校工具..."):
        try:
            from db.connection import get_db
            from export.select_tool import generate
            import tempfile
            from pathlib import Path

            conn = get_db()
            tmp = Path(tempfile.mktemp(suffix=".html"))
            generate(conn, tmp)
            conn.close()
            html_bytes = tmp.read_bytes()
            tmp.unlink()
            st.download_button(
                label="下载离线选校工具",
                data=html_bytes,
                file_name="选校工具_江浙沪.html",
                mime="text/html",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"生成失败: {e}")

st.markdown("---")
st.caption("⚠️ 本系统仅提供参考建议，不保证录取结果。最终志愿填报以各省教育考试院官方信息为准。")
