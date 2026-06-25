"""PDF报告生成 — 使用reportlab，支持中文"""

from __future__ import annotations

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.settings import RISK_TIERS
from db.models import PipelineResult

_font_registered = False


def _register_fonts():
    global _font_registered
    if _font_registered:
        return
    import os
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("Chinese", path))
                _font_registered = True
                return
            except Exception:
                continue
    _font_registered = True


def _get_styles():
    _register_fonts()
    styles = getSampleStyleSheet()
    font_name = "Chinese" if _font_registered else "Helvetica"

    styles.add(ParagraphStyle(
        name="CNTitle",
        fontName=font_name,
        fontSize=18,
        leading=24,
        alignment=1,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="CNHeading",
        fontName=font_name,
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CNBody",
        fontName=font_name,
        fontSize=10,
        leading=14,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CNSmall",
        fontName=font_name,
        fontSize=8,
        leading=10,
        textColor=colors.grey,
    ))
    return styles


def generate_pdf(result: PipelineResult) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = _get_styles()
    elements = []

    elements.append(Paragraph("志愿质检员 — 审核报告", styles["CNTitle"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("考生信息", styles["CNHeading"]))
    student = result.student
    info_data = [
        ["省份", student.province, "分数", str(student.score)],
        ["排名", str(student.rank), "选科", ", ".join(student.all_subjects())],
        ["意向城市", ", ".join(student.preferred_cities[:3]), "策略", student.risk_preference],
    ]
    info_table = Table(info_data, colWidths=[60, 120, 60, 120])
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.9)),
        ("BACKGROUND", (2, 0), (2, -1), colors.Color(0.9, 0.9, 0.9)),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    for strategy in result.strategies:
        elements.append(Paragraph(f"{strategy.strategy_label}（{len(strategy.recommendations)}个志愿）", styles["CNHeading"]))
        elements.append(Paragraph(strategy.summary, styles["CNBody"]))

        if strategy.recommendations:
            header = ["序号", "分层", "院校", "专业", "排名", "风险"]
            rows = [header]
            for i, rec in enumerate(strategy.recommendations[:30], 1):
                tier_info = RISK_TIERS.get(rec.tier, {"label": rec.tier})
                ranks = "/".join(str(r) for r in rec.historical_min_ranks[:3]) if rec.historical_min_ranks else "-"
                rows.append([
                    str(i),
                    tier_info["label"],
                    rec.university_name[:8],
                    rec.major_name[:8],
                    ranks,
                    rec.risk_level,
                ])

            table = Table(rows, colWidths=[25, 30, 70, 70, 70, 50])
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.8, 0.8, 0.8)),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]))
            elements.append(table)

        elements.append(Spacer(1, 8))

    if result.audit_result:
        elements.append(Paragraph("审核结果", styles["CNHeading"]))
        status_text = {"pass": "通过", "warning": "需关注", "high_risk": "高风险", "invalid": "不合规"}
        elements.append(Paragraph(f"状态: {status_text.get(result.audit_result.status, '未知')}", styles["CNBody"]))
        for risk in result.audit_result.high_risks:
            elements.append(Paragraph(f"[高风险] {risk}", styles["CNBody"]))
        for warning in result.audit_result.warnings:
            elements.append(Paragraph(f"[警告] {warning}", styles["CNBody"]))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "免责声明：本系统仅提供参考建议，不保证录取结果。最终志愿填报以各省教育考试院官方信息为准。",
        styles["CNSmall"],
    ))

    doc.build(elements)
    return buf.getvalue()
