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
