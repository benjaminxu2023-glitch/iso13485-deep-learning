"""
Interactive CLI prompt builder — guides users through constructing a well-structured prompt.
"""

import sys

from .formatter import export_prompt, format_checklist, format_prompt, validate_components
from .framework import BEST_PRACTICES, PROMPT_ELEMENTS, PROMPT_STRUCTURE
from .templates import get_template, list_templates


def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_section(text: str) -> None:
    print(f"\n--- {text} ---\n")


def get_multiline_input(prompt_text: str) -> str:
    print(f"{prompt_text}")
    print("  (Enter your text. Type 'END' on a new line when done, or press Enter to skip)")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        if not lines and line.strip() == "":
            return ""
        lines.append(line)
    return "\n".join(lines)


def show_framework_overview() -> None:
    print_header("Anthropic's Prompt Engineering Framework")

    print("The 5-Part Prompt Structure:")
    for step in PROMPT_STRUCTURE:
        elements = ", ".join(step.maps_to_elements)
        print(f"  {step.order}. {step.name}")
        print(f"     {step.description}")
        print(f"     Elements: {elements}")
        print()

    print("Best Practices:")
    for i, tip in enumerate(BEST_PRACTICES, 1):
        print(f"  {i}. {tip}")


def build_from_scratch() -> dict[str, str]:
    components: dict[str, str] = {}

    print_header("Building Your Prompt Step by Step")
    print("We'll walk through each element of a well-structured prompt.")
    print("Required elements are marked with *. You can skip optional ones.\n")

    for element in PROMPT_ELEMENTS:
        req = " *" if element.required else ""
        print_section(f"{element.name}{req}")
        print(f"  Purpose: {element.description}")
        print(f"  Guidance: {element.guidance}")

        if element.example:
            print(f"\n  Example:")
            for line in element.example.split("\n"):
                print(f"    {line}")

        print()
        value = get_multiline_input(f"  Your {element.name}:")

        if value.strip():
            components[element.name] = value
        elif element.required:
            print(f"  ⚠ This is a required element. Your prompt may be less effective without it.")

    return components


def build_from_template() -> dict[str, str]:
    templates = list_templates()

    print_header("Choose a Template")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t['name']} — {t['description']}")

    print()
    choice = input("Enter template number (or 'back' to build from scratch): ").strip()

    if choice.lower() == "back":
        return build_from_scratch()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(templates):
            key = templates[idx]["key"]
            components = get_template(key)
            if components:
                print(f"\nLoaded template: {templates[idx]['name']}")
                print("\nPre-filled components:")
                for name, value in components.items():
                    print(f"  - {name}: {value[:80]}...")

                print("\nYou can now customize any element.")
                customize = input("Customize elements? (y/n): ").strip().lower()

                if customize == "y":
                    for element in PROMPT_ELEMENTS:
                        current = components.get(element.name, "")
                        if current:
                            print_section(element.name)
                            print(f"  Current: {current[:120]}...")
                            change = input("  Change this? (y/n/Enter to keep): ").strip().lower()
                            if change == "y":
                                new_value = get_multiline_input(f"  New {element.name}:")
                                if new_value.strip():
                                    components[element.name] = new_value
                        else:
                            print_section(f"{element.name} (not set)")
                            add = input("  Add this element? (y/n): ").strip().lower()
                            if add == "y":
                                new_value = get_multiline_input(f"  {element.name}:")
                                if new_value.strip():
                                    components[element.name] = new_value

                return components
    except (ValueError, IndexError):
        pass

    print("Invalid choice. Starting from scratch.")
    return build_from_scratch()


def main() -> None:
    print_header("Prompt Agent — Build Perfect Prompts for Claude")
    print("Based on Anthropic's official prompt engineering framework.\n")
    print("Options:")
    print("  1. Build a prompt from scratch (guided)")
    print("  2. Start from a template")
    print("  3. View the framework overview")
    print("  4. Quick build (required elements only)")
    print()

    choice = input("Choose an option (1-4): ").strip()

    if choice == "3":
        show_framework_overview()
        print("\nReady to build a prompt now?")
        again = input("Start building? (y/n): ").strip().lower()
        if again != "y":
            return
        choice = input("From scratch (1) or template (2)? ").strip()

    if choice == "2":
        components = build_from_template()
    elif choice == "4":
        components = quick_build()
    else:
        components = build_from_scratch()

    print_header("Your Prompt")

    warnings = validate_components(components)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    print("Checklist:")
    print(format_checklist(components))
    print()

    prompt = format_prompt(components)
    print("Generated Prompt:")
    print("-" * 60)
    print(prompt)
    print("-" * 60)

    save = input("\nSave to file? Enter filename (or press Enter to skip): ").strip()
    if save:
        if not save.endswith(".md"):
            save += ".md"
        export_prompt(components, save)
        print(f"Saved to {save}")


def quick_build() -> dict[str, str]:
    """Build a prompt with only the 3 required elements."""
    components: dict[str, str] = {}

    print_header("Quick Build — Required Elements Only")

    required = [e for e in PROMPT_ELEMENTS if e.required]
    for element in required:
        print_section(element.name)
        print(f"  {element.guidance}")
        if element.example:
            print(f"\n  Example: {element.example[:120]}...")
        print()
        value = get_multiline_input(f"  Your {element.name}:")
        if value.strip():
            components[element.name] = value

    return components


if __name__ == "__main__":
    main()
