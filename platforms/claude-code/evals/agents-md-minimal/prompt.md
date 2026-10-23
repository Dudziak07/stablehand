---
description: Instructions hold only stated facts and commands, briefly (evals/scenarios/agents-md-minimal.md).
tags: [writing-project-instructions]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Write an AGENTS.md for this repo. Claude Code and OpenCode both use it. Facts:
- Python 3.12, managed by uv.
- Run tests with `uv run pytest -q`.
- Lint with `uv run ruff check .`.
- Never edit files in `migrations/` by hand; generate them with `uv run alembic revision --autogenerate`.

Work non-interactively and write the file directly.
