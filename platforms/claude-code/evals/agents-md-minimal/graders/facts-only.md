---
type: llm
weight: 2
focus:
  source: file
  path: AGENTS.md
---

PASS if all of the following hold:
- the file contains the four given facts: uv with Python 3.12, `uv run pytest -q`, `uv run ruff check .`, and the migrations rule with `uv run alembic revision --autogenerate`;
- it adds no generic advice (such as "write clean code" or "follow best practices") and no invented commands or conventions;
- it is at most 40 lines.

FAIL if any given fact is missing, if invented content or generic advice appears, or if the file is longer than 40 lines.
