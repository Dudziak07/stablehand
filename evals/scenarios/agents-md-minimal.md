---
id: agents-md-minimal
kind: behavior
runs: 3
targets: [writing-project-instructions]
---
## Prompt
Write an AGENTS.md for this repo. Claude Code and OpenCode both use it. Facts:
- Python 3.12, managed by uv.
- Run tests with `uv run pytest -q`.
- Lint with `uv run ruff check .`.
- Never edit files in `migrations/` by hand; generate them with `uv run alembic revision --autogenerate`.

Work non-interactively and write the file directly.

## Setup
None.

## Expected (all must hold)
- `writing-project-instructions` is loaded. *(mechanism: with-artifact arm only)*
- `AGENTS.md` exists and contains `uv run pytest -q`, `uv run ruff check .` and `alembic revision --autogenerate`.
- The file holds facts only: no generic advice (such as "write clean code" or "follow best practices") and no tutorial prose.
- The file is at most 40 lines.
- It has no YAML frontmatter.

## Must not
- Invent commands or conventions that the prompt did not give.

## Checks
- deterministic:
  - `AGENTS.md` exists;
  - regex `uv run pytest -q`;
  - regex `alembic revision --autogenerate`;
  - regex `^---` is absent at the start.
- judge: PASS if every line is a stated fact, a command or a boundary, with no generic advice or invented content, and the file is short. FAIL otherwise.
