---
name: "validating-artifacts"
description: "Runs static checks on skills, agents, rules, and instruction files with the bundled linter, including cross-platform collisions and card freshness. Use when validating an artifact, debugging why a skill or agent does not load, checking a project's setup, or before committing. Not for behavior evals or linting application source code."
---

Run static checks with the bundled linter (`scripts/lint.py` inside this skill's folder, synced from `tools/lint.py`) and fix every error. Write all output in English.

Reference material (in this skill's folder):
- `references/coexistence.md`: cross-platform loading paths and collision rules.
- `references/codex.md`: OpenAI Codex CLI fields, paths, and limits.

## Process

1. **Choose the mode:**
   - single skill or agent: `uv run "<skill-dir>/scripts/lint.py" --platform <platform> <path>`
   - whole project (auto-detects platforms and checks collisions): `uv run "<skill-dir>/scripts/lint.py" --project "<target>"`
   - platform cards freshness: `uv run "<skill-dir>/scripts/lint.py" --cards "<cards-dir>" --strict`
   Add `--json` for structured output, or `--strict` to fail on warnings as well as errors.
2. **Run** the command (or with Python >= 3.11 and PyYAML installed if `uv` is unavailable).
3. **Fix** every error. Fix each warning or explain why it is accepted.
4. **Re-run** until the linter exits 0 (or `--strict` exits 0 when requested).

## Must not
- Edit the vendored `scripts/lint.py` copy; changes belong in `tools/lint.py` in the stablehand repo.
- Silence findings by deleting content without understanding them.
