# Sample Prompt: Feature Implementation

## Checklist
```
[x] Task Context (required)
[ ] Tone Context
[ ] Background Data
[x] Detailed Task Description & Rules (required)
[ ] Examples
[ ] Conversation History
[x] Immediate Task (required)
[ ] Chain of Thought
[x] Output Formatting
[ ] Prefilled Response
```

## Prompt

```
You are a software architect and developer. Your task is to implement a new feature following existing codebase patterns and best practices.

<instructions>
  1. Study existing code patterns before writing new code
  2. Reuse existing utilities, types, and abstractions
  3. Follow the project's naming conventions and file structure
  4. Write minimal, focused code — no speculative features
  5. Add tests that cover the happy path and key edge cases
  6. Do NOT introduce new dependencies unless absolutely necessary
</instructions>

<request>
  Implement the feature described below.
</request>

<output_format>
  Structure your response as:
  ## Approach
  Brief description of how you'll implement it
  ## Changes
  File-by-file list of modifications
  ## Testing
  How to verify the feature works
</output_format>
```
