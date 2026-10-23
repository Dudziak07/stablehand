---
name: validating-artifacts
description: "Checks skills, subagents, rules and instruction files against the formats Claude Code, Antigravity and OpenCode accept, and finds cross-platform collisions in a project, using a bundled linter. Use when asked to validate or lint agent artifacts, when a skill or agent does not load, or before committing them. Not for behavior testing or for linting application code."
allowed-tools: Bash(uv run *)
---

Run the bundled linter, fix every error, and explain any warning you accept. A file Claude Code can't parse is skipped silently, so this check is the only early signal.

The linter is `${CLAUDE_SKILL_DIR}/scripts/lint.py`, a generated copy: never edit it. It needs uv (or any Python ≥ 3.11 with PyYAML).

## Commands
```
# one skill folder, SKILL.md, agent file, rule or instruction file
uv run "${CLAUDE_SKILL_DIR}/scripts/lint.py" --platform claude-code <path> [<path> ...]

# a folder with skills/, agents/, rules/ (e.g. a plugin)
uv run "${CLAUDE_SKILL_DIR}/scripts/lint.py" --platform claude-code <folder>

# a whole project: all platforms found, plus collisions between them
uv run "${CLAUDE_SKILL_DIR}/scripts/lint.py" --project <project-root>
```
Add `--platform antigravity` or `--platform opencode` to check artifacts for those platforms. Add `--json` for machine output and `--strict` to fail on warnings.

## Process
1. Pick the mode that covers everything you changed. Use `--project` whenever more than one platform opens the repo.
2. Run it. Exit 0 means no errors.
3. For each error, fix the cause. Common ones:

   | Code | Meaning | Fix |
   |---|---|---|
   | S002 / A001 | frontmatter missing or invalid YAML | close the `---` block; double-quote values that contain `: ` |
   | S005 | name ≠ folder | rename one of them |
   | S020 | linked file missing | create it or fix the path |
   | A016 / A033 / A042 | invalid enum value | use a value from the platform card |
   | A031 | unknown Antigravity tool (can hang the agent) | use a tool from `antigravity.md` section 5 |
   | P003 | OpenCode sees two skills with one name | rename one, or set `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` (see `coexistence.md`) |
   | I004 | CLAUDE.md hides AGENTS.md | start CLAUDE.md with `@AGENTS.md` |

4. For each warning, fix it or state in one line why it is acceptable. To suppress a justified finding in one file, add `<!-- stablehand-lint: ignore CODE -->`.
5. Re-run until there are no errors.

## Must not
- Silence a finding by deleting content you do not understand. Fix the cause, or keep the content and justify the warning.

## Done when
- [ ] The linter exits 0 (or exits 0 with `--strict`, if the user asked for it)
- [ ] Every accepted warning has a one-line reason in your reply
