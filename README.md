# Prompt Agent

Build perfect prompts for Claude Code, based on Anthropic's official prompt engineering framework.

## Quick Start

```bash
# Interactive prompt builder
python -m prompt_agent

# Or use programmatically
python -c "
from prompt_agent.templates import get_template
from prompt_agent.formatter import format_prompt
print(format_prompt(get_template('code_review')))
"
```

## Framework

Based on Anthropic's 10-element prompt checklist and 5-part structure:

**Required elements:**
1. Task Context — WHO the AI is and WHAT it does (1-2 sentences)
2. Detailed Task Description & Rules — specific instructions and constraints
3. Immediate Task — the specific action to take right now

**Optional elements:** Tone, Background Data, Examples, Conversation History, Chain of Thought, Output Formatting, Prefilled Response

**Prompt structure order:** Role → Dynamic Content (in XML tags) → Instructions → Examples → Output Format & Reminders

## Templates

Pre-built templates for common tasks:
- `code_review` — Review code for bugs and security issues
- `bug_fix` — Diagnose and fix bugs
- `feature_implementation` — Implement new features
- `documentation` — Write technical documentation
- `refactor` — Refactor code safely

## Project Structure

```
prompt_agent/
├── __init__.py      # Package definition
├── __main__.py      # CLI entry point
├── builder.py       # Interactive prompt builder
├── formatter.py     # XML tag formatting and assembly
├── framework.py     # Framework definitions (10 elements, 5-part structure)
└── templates.py     # Pre-built prompt templates
examples/
└── sample_prompts/  # Example output prompts
```
