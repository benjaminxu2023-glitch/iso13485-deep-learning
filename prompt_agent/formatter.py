"""
Prompt formatter — assembles prompt components into a well-structured prompt with XML tags.
"""

from .framework import PROMPT_ELEMENTS, PROMPT_STRUCTURE


def wrap_xml(tag: str, content: str, indent: int = 0) -> str:
    prefix = "  " * indent
    if "\n" in content:
        lines = content.rstrip("\n").split("\n")
        inner = "\n".join(f"{prefix}  {line}" for line in lines)
        return f"{prefix}<{tag}>\n{inner}\n{prefix}</{tag}>"
    return f"{prefix}<{tag}>{content}</{tag}>"


def format_prompt(components: dict[str, str]) -> str:
    """Assemble prompt components into a structured prompt following the 5-part structure."""
    sections = []

    # Part 1: Role & Task Overview
    task_context = components.get("Task Context", "").strip()
    tone = components.get("Tone Context", "").strip()
    if task_context:
        sections.append(task_context)
    if tone:
        sections.append(tone)

    # Part 2: Dynamic / Retrieved Content
    background = components.get("Background Data", "").strip()
    history = components.get("Conversation History", "").strip()
    if background:
        sections.append(wrap_xml("background", background))
    if history:
        sections.append(wrap_xml("history", history))

    # Part 3: Detailed Task Instructions
    instructions = components.get("Detailed Task Description & Rules", "").strip()
    request = components.get("Immediate Task", "").strip()
    thinking = components.get("Chain of Thought", "").strip()
    if instructions:
        sections.append(wrap_xml("instructions", instructions))
    if request:
        sections.append(wrap_xml("request", request))
    if thinking:
        sections.append(wrap_xml("thinking", thinking))

    # Part 4: Examples
    examples = components.get("Examples", "").strip()
    if examples:
        sections.append(wrap_xml("examples", examples))

    # Part 5: Output Format & Critical Reminders
    output_format = components.get("Output Formatting", "").strip()
    prefill = components.get("Prefilled Response", "").strip()
    if output_format:
        sections.append(wrap_xml("output_format", output_format))

    # Repeat critical instructions at end for long prompts
    total_len = sum(len(s) for s in sections)
    if total_len > 1500 and instructions:
        sections.append(wrap_xml("reminder", "IMPORTANT: " + instructions.split("\n")[0]))

    result = "\n\n".join(sections)

    if prefill:
        result += "\n\n---\n[Prefilled response start]\n" + prefill

    return result


def validate_components(components: dict[str, str]) -> list[str]:
    """Check for missing required elements and return warnings."""
    warnings = []
    required_elements = [e for e in PROMPT_ELEMENTS if e.required]

    for element in required_elements:
        value = components.get(element.name, "").strip()
        if not value:
            warnings.append(f"Missing required element: {element.name} — {element.description}")

    if not components.get("Examples", "").strip():
        warnings.append(
            "Tip: Adding examples (few-shot) is the most powerful way to steer Claude's behavior."
        )

    return warnings


def format_checklist(components: dict[str, str]) -> str:
    """Generate a checklist showing which elements are filled."""
    lines = []
    for element in PROMPT_ELEMENTS:
        value = components.get(element.name, "").strip()
        status = "x" if value else " "
        req = " (required)" if element.required else ""
        lines.append(f"[{status}] {element.name}{req}")
    return "\n".join(lines)


def export_prompt(components: dict[str, str], filepath: str) -> None:
    """Export the formatted prompt to a file."""
    prompt = format_prompt(components)
    warnings = validate_components(components)

    with open(filepath, "w") as f:
        if warnings:
            f.write("<!-- Prompt Warnings:\n")
            for w in warnings:
                f.write(f"  - {w}\n")
            f.write("-->\n\n")

        f.write("# Generated Prompt\n\n")
        f.write("## Checklist\n")
        f.write("```\n")
        f.write(format_checklist(components))
        f.write("\n```\n\n")
        f.write("## Prompt\n\n")
        f.write("```\n")
        f.write(prompt)
        f.write("\n```\n")
