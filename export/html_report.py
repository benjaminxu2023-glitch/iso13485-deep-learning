"""HTML报告生成 — 美观的中文交互式报告"""

from __future__ import annotations

from config.settings import RISK_TIERS
from db.models import PipelineResult

TIER_LABELS = {"reach": "冲", "slight_reach": "稳冲", "match": "稳", "safe": "保", "backup": "垫底"}
RISK_LABELS = {"high": "高风险", "medium_high": "中高风险", "medium": "中等", "low": "低风险", "very_low": "极低"}

CSS = """
:root {
    --primary: #1a73e8;
    --danger: #d93025;
    --warning: #f9ab00;
    --success: #1e8e3e;
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --text: #202124;
    --text-secondary: #5f6368;
    --border: #dadce0;
    --radius: 12px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.6; padding: 0;
}
.container { max-width: 960px; margin: 0 auto; padding: 20px; }
.report-header {
    background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
    color: white; padding: 40px 20px; text-align: center;
}
.report-header h1 { font-size: 28px; margin-bottom: 8px; font-weight: 700; }
.report-header .subtitle { font-size: 16px; opacity: 0.9; }
.profile-card {
    background: var(--card-bg); border-radius: var(--radius); padding: 24px;
    margin: -30px 20px 24px; position: relative; box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.profile-card h2 { font-size: 18px; margin-bottom: 16px; color: var(--primary); }
.profile-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;
}
.profile-item { display: flex; flex-direction: column; }
.profile-item label { font-size: 12px; color: var(--text-secondary); margin-bottom: 2px; }
.profile-item span { font-size: 15px; font-weight: 500; }
.score-highlight { font-size: 36px !important; color: var(--primary); font-weight: 700 !important; }
.rank-highlight { font-size: 24px !important; color: var(--danger); font-weight: 600 !important; }
.tab-bar { display: flex; gap: 0; margin: 24px 0 0; border-bottom: 2px solid var(--border); }
.tab-btn {
    padding: 12px 24px; border: none; background: none; font-size: 15px; font-weight: 500;
    color: var(--text-secondary); cursor: pointer; border-bottom: 3px solid transparent;
    margin-bottom: -2px; transition: all 0.2s;
}
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }
.tab-btn:hover { color: var(--primary); background: rgba(26,115,232,0.04); }
.strategy-summary {
    background: var(--card-bg); border-radius: var(--radius); padding: 20px;
    margin: 16px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.dist-row { display: flex; gap: 16px; margin: 16px 0; flex-wrap: wrap; }
.dist-item { display: flex; align-items: center; gap: 8px; }
.dist-badge { color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.dist-count { font-size: 20px; font-weight: 700; }
.overall-risk { color: var(--text-secondary); margin-top: 8px; }
.rec-card {
    background: var(--card-bg); border-radius: var(--radius); margin: 12px 0;
    overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); border-left: 4px solid var(--border);
}
.rec-card.tier-reach { border-left-color: #FF4B4B; }
.rec-card.tier-slight_reach { border-left-color: #FFA500; }
.rec-card.tier-match { border-left-color: #00CC66; }
.rec-card.tier-safe { border-left-color: #4A90D9; }
.rec-card.tier-backup { border-left-color: #999; }
.rec-header {
    padding: 16px 20px; display: flex; align-items: center; gap: 12px;
    cursor: pointer; flex-wrap: wrap;
}
.rec-header h3 { font-size: 16px; margin: 0; }
.tier-badge { color: white; padding: 3px 10px; border-radius: 12px; font-size: 13px; font-weight: 600; flex-shrink: 0; }
.rec-num { font-size: 13px; color: var(--text-secondary); }
.major-name { font-size: 14px; color: var(--text-secondary); }
.rec-body { padding: 0 20px 20px; }
.rec-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px; margin-bottom: 12px;
}
.rec-item label { display: block; font-size: 11px; color: var(--text-secondary); }
.rec-item span { font-size: 14px; font-weight: 500; }
.rec-history {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;
    padding: 10px; background: #f1f3f4; border-radius: 8px;
}
.rec-history label { font-size: 11px; color: var(--text-secondary); display: block; }
.history-val { font-size: 15px; font-weight: 600; color: var(--primary); }
.rec-reason, .rec-evidence { font-size: 13px; margin-bottom: 8px; color: var(--text-secondary); }
.rec-reason strong, .rec-evidence strong { color: var(--text); }
.charter-risks, .manual-review {
    font-size: 13px; margin-top: 8px; padding: 10px; background: #fff8e1; border-radius: 8px;
}
.charter-risks ul, .manual-review ul { margin: 4px 0 0 16px; }
.charter-risks li, .manual-review li { margin-bottom: 4px; }
.risk-high { color: var(--danger); font-weight: 600; }
.risk-medium_high { color: #e37400; font-weight: 600; }
.risk-medium { color: var(--warning); font-weight: 500; }
.risk-low { color: var(--success); }
.risk-very_low { color: #999; }
.audit-section, .charter-section {
    background: var(--card-bg); border-radius: var(--radius); padding: 24px;
    margin: 24px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.audit-section h2, .charter-section h2 { font-size: 18px; margin-bottom: 16px; color: var(--primary); }
.audit-status {
    font-size: 20px; font-weight: 700; margin-bottom: 16px; padding: 12px; border-radius: 8px;
}
.status-pass { background: #e6f4ea; color: #1e8e3e; }
.status-warning { background: #fef7e0; color: #e37400; }
.status-danger { background: #fce8e6; color: #d93025; }
.audit-item { padding: 10px 12px; margin: 6px 0; border-radius: 8px; font-size: 14px; }
.audit-danger { background: #fce8e6; }
.audit-warning { background: #fef7e0; }
.audit-info { background: #e8f0fe; }
.charter-uni { margin: 12px 0; }
.charter-uni h4 { font-size: 15px; margin-bottom: 6px; }
.charter-uni ul { margin-left: 20px; }
.charter-uni li { margin-bottom: 4px; font-size: 13px; }
.disclaimer {
    text-align: center; padding: 24px; margin-top: 32px;
    color: var(--text-secondary); font-size: 12px; border-top: 1px solid var(--border);
}
@media print {
    body { background: white; }
    .tab-btn { display: none; }
    .tab-content { display: block !important; page-break-inside: avoid; }
    .rec-card { break-inside: avoid; }
    .report-header { background: #1a73e8 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
@media (max-width: 640px) {
    .profile-grid { grid-template-columns: 1fr 1fr; }
    .rec-grid { grid-template-columns: 1fr 1fr; }
    .rec-history { grid-template-columns: 1fr; }
    .tab-btn { padding: 10px 14px; font-size: 14px; }
}
"""

JS = """
function switchTab(idx) {
    document.querySelectorAll('.tab-btn').forEach(function(btn, i) {
        btn.classList.toggle('active', i === idx);
    });
    document.querySelectorAll('.tab-content').forEach(function(content, i) {
        content.style.display = i === idx ? '' : 'none';
    });
}
"""


def generate_html(result: PipelineResult) -> str:
    student = result.student
    province_names = {"shanghai": "上海", "zhejiang": "浙江", "jiangsu": "江苏"}
    province_cn = province_names.get(student.province, student.province)
    subjects_str = "、".join(student.all_subjects())
    strategy_pref = {"aggressive": "冲刺型", "balanced": "均衡型", "conservative": "稳妥型"}.get(
        student.risk_preference, student.risk_preference)

    strategy_tabs = []
    strategy_contents = []

    for idx, strategy in enumerate(result.strategies):
        active = " active" if idx == 1 else ""
        strategy_tabs.append(
            '<button class="tab-btn' + active + '" onclick="switchTab(' + str(idx) + ')">'
            + strategy.strategy_label + '</button>'
        )

        rows = []
        for i, rec in enumerate(strategy.recommendations, 1):
            rows.append(_render_rec_card(rec, i))

        dist_items = []
        for tier_key in ["reach", "slight_reach", "match", "safe", "backup"]:
            count = strategy.tier_distribution.get(tier_key, 0)
            label = TIER_LABELS.get(tier_key, tier_key)
            color = RISK_TIERS.get(tier_key, {}).get("color", "#666")
            dist_items.append(
                '<div class="dist-item"><span class="dist-badge" style="background:' + color + '">'
                + label + '</span><span class="dist-count">' + str(count) + '</span></div>'
            )

        display = "" if idx == 1 else "display:none;"
        strategy_contents.append(
            '<div class="tab-content" id="tab-' + str(idx) + '" style="' + display + '">'
            + '<div class="strategy-summary"><p>' + strategy.summary + '</p>'
            + '<div class="dist-row">' + "".join(dist_items) + '</div>'
            + '<p class="overall-risk">整体风险评估：<strong>' + strategy.overall_risk + '</strong></p></div>'
            + '<div class="rec-list">' + "".join(rows) + '</div></div>'
        )

    audit_html = _render_audit(result)
    charter_html = _render_charter_section(result)

    parts = [
        '<!DOCTYPE html><html lang="zh-CN"><head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>志愿质检员 — ' + province_cn + str(student.score) + '分审核报告</title>',
        '<style>' + CSS + '</style></head><body>',
        '<div class="report-header"><h1>志愿质检员</h1>',
        '<div class="subtitle">江浙沪高考志愿风险审核报告</div></div>',
        '<div class="container">',
        '<div class="profile-card"><h2>考生信息</h2><div class="profile-grid">',
        _profile_item("省份", province_cn),
        _profile_item("高考分数", str(student.score), "score-highlight"),
        _profile_item("省排名", "第" + str(student.rank) + "名", "rank-highlight"),
        _profile_item("选考科目", subjects_str),
        _profile_item("意向城市", "、".join(student.preferred_cities) or "不限"),
        _profile_item("意向专业", "、".join(student.preferred_majors) or "不限"),
        _profile_item("策略偏好", strategy_pref),
        _profile_item("接受调剂", "是" if student.accept_adjustment else "否"),
        '</div></div>',
        '<div class="tab-bar">' + "".join(strategy_tabs) + '</div>',
        "".join(strategy_contents),
        audit_html,
        charter_html,
        '<div class="disclaimer"><p><strong>免责声明</strong></p>',
        '<p>本系统仅提供参考建议，不保证录取结果。最终志愿填报请以各省教育考试院官方信息为准。</p>',
        '<p>本报告基于历史录取数据生成，实际录取结果受当年报考人数、招生计划变化等多种因素影响。</p>',
        '<p style="margin-top:12px;color:#aaa;">志愿质检员 · 江浙沪版</p></div>',
        '</div>',
        '<script>' + JS + '</script>',
        '</body></html>',
    ]
    return "\n".join(parts)


def _profile_item(label: str, value: str, cls: str = "") -> str:
    span_cls = ' class="' + cls + '"' if cls else ""
    return '<div class="profile-item"><label>' + label + '</label><span' + span_cls + '>' + value + '</span></div>'


def _render_rec_card(rec, index: int) -> str:
    tier = TIER_LABELS.get(rec.tier, rec.tier)
    tier_color = RISK_TIERS.get(rec.tier, {}).get("color", "#666")
    ranks = " → ".join(str(r) for r in rec.historical_min_ranks[:3]) if rec.historical_min_ranks else "暂无"
    scores = " → ".join(str(s) for s in rec.historical_min_scores[:3]) if rec.historical_min_scores else "暂无"
    tuition = str(rec.tuition) + "元/年" if rec.tuition else "待确认"
    subjects = "、".join(rec.subject_requirements) if rec.subject_requirements else "不限"
    risk_label = RISK_LABELS.get(rec.risk_level, rec.risk_level)
    plan_count = str(rec.current_year_plan_count) if rec.current_year_plan_count else "待确认"

    charter_html = ""
    if rec.charter_risks:
        items = []
        for cr in rec.charter_risks:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(cr.severity, "⚪")
            items.append("<li>" + icon + " <strong>" + cr.risk_type + "</strong>：" + cr.detail + "</li>")
        charter_html = '<div class="charter-risks"><strong>章程风险：</strong><ul>' + "".join(items) + '</ul></div>'

    manual_html = ""
    if rec.manual_review_items:
        items = ["<li>" + item + "</li>" for item in rec.manual_review_items]
        manual_html = '<div class="manual-review"><strong>需人工复核：</strong><ul>' + "".join(items) + '</ul></div>'

    return (
        '<div class="rec-card tier-' + rec.tier + '">'
        + '<div class="rec-header">'
        + '<span class="tier-badge" style="background:' + tier_color + '">' + tier + '</span>'
        + '<span class="rec-num">#' + str(index) + '</span>'
        + '<h3>' + rec.university_name + '</h3>'
        + '<span class="major-name">' + rec.major_name + '</span></div>'
        + '<div class="rec-body">'
        + '<div class="rec-grid">'
        + '<div class="rec-item"><label>城市</label><span>' + (rec.city or "未知") + '</span></div>'
        + '<div class="rec-item"><label>校区</label><span>' + (rec.campus or "未知") + '</span></div>'
        + '<div class="rec-item"><label>学费</label><span>' + tuition + '</span></div>'
        + '<div class="rec-item"><label>选科要求</label><span>' + subjects + '</span></div>'
        + '<div class="rec-item"><label>今年计划</label><span>' + plan_count + '人</span></div>'
        + '<div class="rec-item"><label>风险等级</label><span class="risk-' + rec.risk_level + '">' + risk_label + '</span></div>'
        + '</div>'
        + '<div class="rec-history">'
        + '<div><label>历年最低排名</label><span class="history-val">' + ranks + '</span></div>'
        + '<div><label>历年最低分数</label><span class="history-val">' + scores + '</span></div></div>'
        + '<div class="rec-reason"><strong>推荐理由：</strong>' + rec.reason + '</div>'
        + '<div class="rec-evidence"><strong>数据依据：</strong>' + rec.evidence + '</div>'
        + charter_html + manual_html
        + '</div></div>'
    )


def _render_audit(result: PipelineResult) -> str:
    if not result.audit_result:
        return ""
    audit = result.audit_result
    status_map = {
        "pass": ("✅ 审核通过", "status-pass"),
        "warning": ("⚠️ 需关注", "status-warning"),
        "high_risk": ("🔴 高风险", "status-danger"),
        "invalid": ("❌ 不合规", "status-danger"),
    }
    status_text, status_cls = status_map.get(audit.status, ("未知", ""))

    items = []
    for r in audit.high_risks:
        items.append('<div class="audit-item audit-danger">🔴 ' + r + '</div>')
    for w in audit.warnings:
        items.append('<div class="audit-item audit-warning">⚠️ ' + w + '</div>')
    for issue in audit.issues:
        items.append('<div class="audit-item audit-info">📋 ' + issue + '</div>')

    return (
        '<section class="audit-section"><h2>审核结果</h2>'
        + '<div class="audit-status ' + status_cls + '">' + status_text + '</div>'
        + "".join(items) + '</section>'
    )


def _render_charter_section(result: PipelineResult) -> str:
    if not result.charter_risks:
        return ""
    uni_blocks = []
    for uni_key, risks in result.charter_risks.items():
        items = []
        for risk in risks:
            sev = {"high": "🔴 高", "medium": "🟡 中", "low": "🟢 低"}.get(risk.severity, "⚪")
            items.append("<li>" + sev + " 【" + risk.risk_type + "】" + risk.detail + "</li>")
        uni_blocks.append(
            '<div class="charter-uni"><h4>' + uni_key + '</h4><ul>' + "".join(items) + '</ul></div>'
        )
    return (
        '<section class="charter-section"><h2>招生章程风险汇总</h2>'
        + "".join(uni_blocks) + '</section>'
    )
