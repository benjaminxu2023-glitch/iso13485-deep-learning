"""
Pre-built prompt templates for common Claude Code use cases.
"""


TEMPLATES = {
    "code_review": {
        "name": "Code Review",
        "description": "Review code for bugs, security issues, and best practices",
        "components": {
            "Task Context": (
                "You are a senior software engineer conducting a thorough code review. "
                "Your goal is to identify bugs, security vulnerabilities, and opportunities "
                "for improvement."
            ),
            "Tone Context": (
                "Be direct and constructive. Explain the 'why' behind each suggestion."
            ),
            "Detailed Task Description & Rules": (
                "1. Check for correctness bugs — logic errors, off-by-one, null handling\n"
                "2. Check for security vulnerabilities — injection, XSS, auth issues\n"
                "3. Check for performance issues — N+1 queries, unnecessary allocations\n"
                "4. Suggest simplifications where code is overly complex\n"
                "5. Do NOT nitpick style or formatting — focus on substance\n"
                "6. Rank findings by severity: CRITICAL > HIGH > MEDIUM > LOW"
            ),
            "Immediate Task": "Review the following code diff and provide your findings.",
            "Output Formatting": (
                "Format findings as:\n"
                "## [SEVERITY] Brief title\n"
                "**File:** path/to/file:line\n"
                "**Issue:** Description of the problem\n"
                "**Fix:** Suggested correction with code snippet"
            ),
            "Examples": (
                "<example>\n"
                "## [HIGH] SQL Injection in user lookup\n"
                "**File:** src/db/users.py:42\n"
                "**Issue:** User input interpolated directly into SQL query\n"
                "**Fix:**\n"
                "```python\n"
                "# Before\n"
                "cursor.execute(f\"SELECT * FROM users WHERE id={user_id}\")\n"
                "# After\n"
                "cursor.execute(\"SELECT * FROM users WHERE id=?\", (user_id,))\n"
                "```\n"
                "</example>"
            ),
        },
    },
    "bug_fix": {
        "name": "Bug Fix",
        "description": "Diagnose and fix a specific bug",
        "components": {
            "Task Context": (
                "You are a debugging specialist. Your task is to diagnose the root cause "
                "of a bug and provide a minimal, targeted fix."
            ),
            "Detailed Task Description & Rules": (
                "1. Reproduce the issue by understanding the steps/conditions that trigger it\n"
                "2. Identify the root cause — not just the symptom\n"
                "3. Provide the minimal fix — do not refactor surrounding code\n"
                "4. Explain WHY the fix works\n"
                "5. Identify if there are similar bugs elsewhere that should be fixed"
            ),
            "Immediate Task": "Diagnose and fix the bug described below.",
            "Chain of Thought": (
                "Think through the problem step by step:\n"
                "1. What is the expected behavior?\n"
                "2. What is the actual behavior?\n"
                "3. What code path leads to the actual behavior?\n"
                "4. What change corrects the code path?"
            ),
            "Output Formatting": (
                "Structure your response as:\n"
                "## Root Cause\n"
                "Brief explanation\n"
                "## Fix\n"
                "Code changes with explanation\n"
                "## Verification\n"
                "How to confirm the fix works"
            ),
        },
    },
    "feature_implementation": {
        "name": "Feature Implementation",
        "description": "Implement a new feature with proper architecture",
        "components": {
            "Task Context": (
                "You are a software architect and developer. Your task is to implement "
                "a new feature following existing codebase patterns and best practices."
            ),
            "Detailed Task Description & Rules": (
                "1. Study existing code patterns before writing new code\n"
                "2. Reuse existing utilities, types, and abstractions\n"
                "3. Follow the project's naming conventions and file structure\n"
                "4. Write minimal, focused code — no speculative features\n"
                "5. Add tests that cover the happy path and key edge cases\n"
                "6. Do NOT introduce new dependencies unless absolutely necessary"
            ),
            "Immediate Task": "Implement the feature described below.",
            "Output Formatting": (
                "Structure your response as:\n"
                "## Approach\n"
                "Brief description of how you'll implement it\n"
                "## Changes\n"
                "File-by-file list of modifications\n"
                "## Testing\n"
                "How to verify the feature works"
            ),
        },
    },
    "documentation": {
        "name": "Documentation",
        "description": "Write clear, useful documentation",
        "components": {
            "Task Context": (
                "You are a technical writer. Your task is to create clear, practical "
                "documentation that helps developers understand and use the code."
            ),
            "Tone Context": (
                "Write in a clear, concise style. Use active voice. "
                "Assume the reader is a competent developer but unfamiliar with this specific codebase."
            ),
            "Detailed Task Description & Rules": (
                "1. Start with a one-sentence summary of what the component does\n"
                "2. Include a quick-start example showing the most common use case\n"
                "3. Document parameters, return values, and exceptions\n"
                "4. Include edge cases and gotchas\n"
                "5. Do NOT document obvious things — focus on what's surprising or non-obvious\n"
                "6. Keep examples runnable and self-contained"
            ),
            "Immediate Task": "Write documentation for the component described below.",
        },
    },
    "refactor": {
        "name": "Refactoring",
        "description": "Refactor code for clarity, performance, or maintainability",
        "components": {
            "Task Context": (
                "You are a software engineer focused on code quality. Your task is to "
                "refactor code to improve its clarity, performance, or maintainability "
                "without changing its external behavior."
            ),
            "Detailed Task Description & Rules": (
                "1. Preserve all existing behavior — refactoring must be behavior-preserving\n"
                "2. Make one type of improvement at a time\n"
                "3. Ensure all existing tests still pass\n"
                "4. Prefer small, incremental changes over large rewrites\n"
                "5. Explain the motivation for each change\n"
                "6. Do NOT add new features during refactoring"
            ),
            "Immediate Task": "Refactor the code described below.",
            "Chain of Thought": (
                "Before refactoring, analyze:\n"
                "1. What makes this code hard to understand/maintain?\n"
                "2. What specific pattern or technique would improve it?\n"
                "3. What risks does the refactoring introduce?"
            ),
        },
    },
    "capa_review": {
        "name": "CAPA Review",
        "description": "Review CAPA records for ISO 13485 / FDA 21 CFR 820 compliance",
        "components": {
            "Task Context": (
                "You are a quality assurance specialist with deep expertise in ISO 13485, "
                "FDA 21 CFR 820, and CAPA (Corrective and Preventive Action) processes for "
                "medical device manufacturing. Your task is to review CAPA records for "
                "completeness, regulatory compliance, and effectiveness."
            ),
            "Tone Context": (
                "Be precise, objective, and regulatory-minded. Use the language of quality "
                "management systems. Flag deficiencies clearly but constructively — the goal "
                "is audit-readiness, not blame."
            ),
            "Background Data": (
                "<regulatory_requirements>\n"
                "  ISO 13485:2016 Section 8.5.2 — Corrective Action\n"
                "  ISO 13485:2016 Section 8.5.3 — Preventive Action\n"
                "  FDA 21 CFR 820.90 — Nonconforming Product\n"
                "  FDA 21 CFR 820.198 — Complaint Files\n"
                "  FDA 21 CFR 820.250 — Statistical Techniques\n"
                "</regulatory_requirements>\n"
                "\n"
                "<capa_lifecycle>\n"
                "  1. Identification — Source of the issue (complaint, audit, NCR, trend)\n"
                "  2. Evaluation — Risk assessment and impact analysis\n"
                "  3. Investigation — Root cause analysis (5-Why, Fishbone, Fault Tree)\n"
                "  4. Action Plan — Corrective and/or preventive actions with owners and deadlines\n"
                "  5. Implementation — Execution of the action plan\n"
                "  6. Verification — Confirm actions were implemented as planned\n"
                "  7. Effectiveness Check — Confirm the actions resolved the root cause\n"
                "  8. Closure — Final review and documentation\n"
                "</capa_lifecycle>"
            ),
            "Detailed Task Description & Rules": (
                "1. Review each CAPA record against ALL 8 lifecycle stages — flag any missing or incomplete stages\n"
                "2. Verify root cause analysis is thorough — superficial root causes (e.g., \"operator error\") are insufficient\n"
                "3. Check that corrective actions address the ROOT CAUSE, not just the symptom\n"
                "4. Verify preventive actions address similar/related risks across other processes or products\n"
                "5. Confirm effectiveness checks have objective, measurable criteria defined BEFORE implementation\n"
                "6. Check timelines — flag any CAPA open longer than 90 days without documented justification\n"
                "7. Verify risk assessment is documented using the organization risk matrix\n"
                "8. Ensure proper linkage to related records (complaints, NCRs, audits, DHR)\n"
                "9. Do NOT accept \"retraining\" as a standalone corrective action — it must be paired with systemic changes\n"
                "10. Verify all actions have assigned owners with specific completion dates"
            ),
            "Examples": (
                "<example>\n"
                "  <input>\n"
                "    CAPA-2024-042\n"
                "    Source: Customer complaint — intermittent sensor failure in glucose monitor\n"
                "    Root Cause: Operator error during soldering\n"
                "    Corrective Action: Retrain operators on soldering procedure\n"
                "    Effectiveness Check: No further complaints in 30 days\n"
                "  </input>\n"
                "  <output>\n"
                "    ## CAPA-2024-042 Review — DEFICIENT\n"
                "    ### Findings\n"
                "    | # | Stage | Status | Finding |\n"
                "    |---|-------|--------|---------|\n"
                "    | 1 | Root Cause | INADEQUATE | \"Operator error\" is superficial. Use 5-Why or Fishbone. |\n"
                "    | 2 | Corrective Action | INADEQUATE | Retraining alone is insufficient. Add systemic changes. |\n"
                "    | 3 | Preventive Action | MISSING | No preventive action documented. |\n"
                "    | 4 | Effectiveness Check | WEAK | \"No complaints in 30 days\" is not measurable. |\n"
                "    | 5 | Risk Assessment | MISSING | No documented risk assessment. |\n"
                "  </output>\n"
                "</example>"
            ),
            "Immediate Task": (
                "Review the CAPA record(s) provided below. For each CAPA, assess completeness "
                "against all 8 lifecycle stages, evaluate the quality of the root cause analysis, "
                "verify corrective/preventive actions are adequate, and determine if the CAPA is audit-ready."
            ),
            "Chain of Thought": (
                "For each CAPA record, work through these steps before writing your assessment:\n"
                "1. Identify which lifecycle stages are present and which are missing\n"
                "2. Evaluate whether the root cause analysis goes deep enough\n"
                "3. Check if corrective actions logically follow from the root cause\n"
                "4. Assess whether preventive actions extend beyond the immediate issue\n"
                "5. Determine if effectiveness criteria are objective and measurable\n"
                "6. Consider what an FDA auditor would flag during an inspection"
            ),
            "Output Formatting": (
                "For each CAPA reviewed, provide:\n"
                "## CAPA-[ID] Review — [COMPLIANT / DEFICIENT / NEEDS REVISION]\n"
                "### Summary\n"
                "One-sentence overall assessment.\n"
                "### Findings Table\n"
                "| # | Lifecycle Stage | Status | Finding |\n"
                "|---|----------------|--------|---------|\n"
                "### Recommended Actions\n"
                "Numbered list of specific actions to bring the CAPA to compliance.\n"
                "### Audit Risk Assessment\n"
                "HIGH / MEDIUM / LOW risk of FDA observation if audited in current state."
            ),
        },
    },
}


def list_templates() -> list[dict[str, str]]:
    return [
        {"key": key, "name": t["name"], "description": t["description"]}
        for key, t in TEMPLATES.items()
    ]


def get_template(key: str) -> dict[str, str] | None:
    template = TEMPLATES.get(key)
    if template:
        return dict(template["components"])
    return None
