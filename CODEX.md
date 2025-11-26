# Codex Integration Guide
## Purpose
Document standardized instructions for leveraging code-generation agents like OpenAI Codex within this repository to generate and modify code safely and effectively.

## Repo Analysis
- Define instructions for agents to analyze the entire repository structure before making changes.
- Outline how to locate relevant files and gather context before generating or editing code.
- Emphasize respecting existing architecture, frameworks, and style conventions when generating new code or refactoring.

## Guardrails & Protocols
- Provide guardrails for migrations, database schema changes, and modifications to critical files.
- Specify protocols for safe file edits, commit practices, and error handling.
- Outline fallback strategies if code generation fails or produces unexpected results.

## Style Rules
- List code formatting rules (e.g., Biome/ESLint/Prettier for TypeScript/JavaScript and Ruff/Pyright for Python).
- Document naming conventions, test coverage requirements, and linting guidelines.
- Provide templates for scaffolding new components, pages, agents, or services to encourage consistent structure.

## Example System Prompt
Include a copy‑pasteable system prompt that instructs the Codex agent how to interact with the repository: how to search for files, read context, propose changes using pull requests, and adhere to the guardrails and style rules defined above.
