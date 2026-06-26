"""
Prompt engineering framework definitions based on Anthropic's training content.

Defines the 10-element checklist and 5-part prompt structure.
"""

from dataclasses import dataclass, field


@dataclass
class PromptElement:
    name: str
    description: str
    required: bool
    xml_tag: str
    guidance: str
    example: str = ""


PROMPT_ELEMENTS = [
    PromptElement(
        name="Task Context",
        description="1-2 sentences establishing the role and high-level task description",
        required=True,
        xml_tag="task_context",
        guidance=(
            "Start with WHO the AI should be and WHAT it should do at a high level. "
            "This sets the frame for everything that follows. Keep it to 1-2 sentences."
        ),
        example=(
            "You are a senior Python developer specializing in API design. "
            "Your task is to review code for security vulnerabilities and suggest fixes."
        ),
    ),
    PromptElement(
        name="Tone Context",
        description="The communication style and tone for responses",
        required=False,
        xml_tag="tone",
        guidance=(
            "Specify the desired tone: formal, casual, technical, friendly, etc. "
            "Include any audience-specific considerations."
        ),
        example="Respond in a professional but approachable tone, suitable for a junior developer audience.",
    ),
    PromptElement(
        name="Background Data",
        description="Background data, documents, images, or reference material",
        required=False,
        xml_tag="background",
        guidance=(
            "Include any reference material the AI needs: documentation snippets, "
            "data schemas, API specs, or domain knowledge. Wrap each distinct piece "
            "in its own XML sub-tag for clarity."
        ),
        example=(
            "<api_spec>\n"
            "  POST /users — Creates a new user\n"
            "  GET /users/{id} — Returns user by ID\n"
            "</api_spec>"
        ),
    ),
    PromptElement(
        name="Detailed Task Description & Rules",
        description="Specific instructions, constraints, and rules for the task",
        required=True,
        xml_tag="instructions",
        guidance=(
            "Be explicit about what to do and what NOT to do. "
            "Use numbered lists for multi-step processes. "
            "Include constraints, edge cases, and quality criteria."
        ),
        example=(
            "1. Review each function for SQL injection vulnerabilities\n"
            "2. Check for proper input validation on all user-facing endpoints\n"
            "3. Do NOT modify any existing tests\n"
            "4. Flag any hardcoded credentials"
        ),
    ),
    PromptElement(
        name="Examples",
        description="Few-shot examples demonstrating the expected input/output pattern",
        required=False,
        xml_tag="examples",
        guidance=(
            "Provide 1-3 concrete examples of input → output pairs. "
            "Examples are the most powerful way to steer Claude's behavior. "
            "Wrap each example in its own <example> tag."
        ),
        example=(
            "<example>\n"
            "  Input: def get_user(id): return db.execute(f\"SELECT * FROM users WHERE id={id}\")\n"
            "  Output: VULNERABILITY: SQL injection. Use parameterized queries instead.\n"
            "  Fix: def get_user(id): return db.execute(\"SELECT * FROM users WHERE id=?\", (id,))\n"
            "</example>"
        ),
    ),
    PromptElement(
        name="Conversation History",
        description="Prior context or conversation turns to maintain continuity",
        required=False,
        xml_tag="history",
        guidance=(
            "Include relevant prior conversation turns if this is a multi-turn interaction. "
            "This helps maintain context and avoid repetition. "
            "Only include turns that are relevant to the current request."
        ),
        example="",
    ),
    PromptElement(
        name="Immediate Task",
        description="The specific, immediate request or question",
        required=True,
        xml_tag="request",
        guidance=(
            "State exactly what you want done RIGHT NOW. "
            "This is the action item — clear, specific, and unambiguous. "
            "If the task is complex, break it into numbered sub-tasks."
        ),
        example="Review the attached pull request diff and identify all security vulnerabilities, ranked by severity.",
    ),
    PromptElement(
        name="Chain of Thought",
        description="Instructions to think step by step for complex reasoning",
        required=False,
        xml_tag="thinking",
        guidance=(
            "For complex tasks, instruct Claude to think step by step. "
            "You can either ask it to show its reasoning or use a <thinking> tag. "
            "This improves accuracy on multi-step problems."
        ),
        example="Think through each potential vulnerability step by step before providing your assessment.",
    ),
    PromptElement(
        name="Output Formatting",
        description="The desired structure and format of the response",
        required=False,
        xml_tag="output_format",
        guidance=(
            "Specify exactly how the output should be structured: "
            "markdown, JSON, bullet points, tables, specific sections, etc. "
            "Use an example of the desired format if possible."
        ),
        example=(
            "Format your response as:\n"
            "## Findings\n"
            "- **[SEVERITY]** description (file:line)\n"
            "## Recommended Fixes\n"
            "```python\n"
            "# corrected code\n"
            "```"
        ),
    ),
    PromptElement(
        name="Prefilled Response",
        description="Starter text to guide the beginning of the response",
        required=False,
        xml_tag="prefill",
        guidance=(
            "Pre-fill the start of Claude's response to steer its output format. "
            "This is putting words in Claude's mouth to ensure it starts correctly. "
            "Only works with the API — not needed for interactive use."
        ),
        example="## Security Review Report\n\n### Summary\n",
    ),
]


@dataclass
class PromptStructureStep:
    order: int
    name: str
    description: str
    maps_to_elements: list[str] = field(default_factory=list)


PROMPT_STRUCTURE = [
    PromptStructureStep(
        order=1,
        name="Role & Task Overview",
        description="1-2 sentences to establish role and high-level task description",
        maps_to_elements=["Task Context", "Tone Context"],
    ),
    PromptStructureStep(
        order=2,
        name="Dynamic / Retrieved Content",
        description="Background data, documents, and reference material wrapped in XML tags",
        maps_to_elements=["Background Data", "Conversation History"],
    ),
    PromptStructureStep(
        order=3,
        name="Detailed Task Instructions",
        description="Specific rules, constraints, and step-by-step instructions",
        maps_to_elements=["Detailed Task Description & Rules", "Immediate Task", "Chain of Thought"],
    ),
    PromptStructureStep(
        order=4,
        name="Examples (Optional)",
        description="Few-shot examples demonstrating expected behavior",
        maps_to_elements=["Examples"],
    ),
    PromptStructureStep(
        order=5,
        name="Output Format & Critical Reminders",
        description="Output formatting instructions and repeated critical constraints",
        maps_to_elements=["Output Formatting", "Prefilled Response"],
    ),
]


BEST_PRACTICES = [
    "Use XML tags (<tag></tag>) to clearly delimit different sections of your prompt.",
    "Be specific and explicit — ambiguity leads to inconsistent results.",
    "Put the most important instructions at the beginning AND end of long prompts.",
    "Use examples (few-shot) to demonstrate exactly what you want — they're the most powerful steering tool.",
    "For complex reasoning, ask Claude to think step by step before answering.",
    "Specify what NOT to do, not just what to do — constraints prevent common failure modes.",
    "Keep role descriptions to 1-2 sentences — longer ones dilute focus.",
    "Wrap dynamic/variable content in XML tags so Claude knows what's data vs. instructions.",
    "Test your prompt with edge cases before deploying.",
    "For long prompts, repeat critical instructions at the end.",
]
