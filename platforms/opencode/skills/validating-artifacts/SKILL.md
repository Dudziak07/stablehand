---
name: validating-artifacts
description: "Checks skills, subagents, rules and instruction files against the formats OpenCode, Claude Code and Antigravity accept, and finds cross-platform collisions in a project, using a bundled linter. Use when asked to validate or lint agent artifacts, when a skill or agent does not load, or before committing them. Not for behavior testing or for linting application code."
metadata:
  opencode/slash: "true"
---

Run the bundled linter, fix every error, and explain any warning you accept. A file OpenCode cannot parse is skipped silently, so this check is the only early signal.

Reference material:
- `references/opencode.md`: OpenCode fields, permissions, paths and gotchas.
- `references/coexistence.md`: which folders each platform reads, and the cross-platform collisions the validator reports.

The linter is `scripts/lint.py`, bundled in this skill's folder next to this `SKILL.md`. It is a generated copy: never edit it. It needs uv (or any Python 3.11 or newer with PyYAML).

## Locate the linter
1. Take the base directory of this skill from the skill tool output, and look for `scripts/lint.py` under it.
2. If that is not available, check `<repo>/.opencode/skills/validating-artifacts/scripts/lint.py`, then `~/.config/opencode/skills/validating-artifacts/scripts/lint.py`.
3. Use the absolute path in every command below.

## Commands
```
# one skill folder, SKILL.md, agent file, rule or instruction file
uv run "<abs>/scripts/lint.py" --platform opencode "<absolute path>" ["<absolute path>" ...]

# a folder with skills/, agents/ or rules/ (for example this port)
uv run "<abs>/scripts/lint.py" --platform opencode "<absolute folder>"

# a whole project: all platforms found, plus collisions between them
uv run "<abs>/scripts/lint.py" --project "<absolute project root>"
```

Add `--platform claude-code` or `--platform antigravity` to check artifacts for those platforms. Add `--json` for machine output, and `--strict` to fail on warnings.

## Process

1. Choose the mode that covers everything you changed. Use `--project` whenever more than one platform opens the repo.
2. Run the command. Exit code 0 means no errors.
3. Fix each error at its cause. Common ones:

   | Code | Meaning | Fix |
   |---|---|---|
   | S002 / A001 | frontmatter missing or invalid YAML | close the `---` block; wrap a value that contains `: ` in double quotes |
   | S005 | name does not match the folder | rename one of them |
   | S020 | a linked file is missing | create it or fix the path |
   | S014 | `metadata.opencode/*` is not a string "true" or "false" | quote the value |
   | A040 / A042 / A046 / A049 | OpenCode agent field is missing or invalid | add `description`, use `mode: subagent`, and write `permissions` rules with the V2 actions (`shell`, `subagent`, `edit`) |
   | A043 | OpenCode model lacks a provider prefix | use `provider/model-id`, for example `deepseek/deepseek-flash` |
   | P003 | the same skill ID is reachable through two folders | rename one, or set `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` (see `references/coexistence.md`) |
   | I004 | CLAUDE.md hides AGENTS.md | start CLAUDE.md with `@AGENTS.md` |

4. For each warning, either fix it or state in one line why it is acceptable. To suppress a justified finding in one file, add `<!-- stablehand-lint: ignore CODE -->` anywhere in that file.
5. Re-run until there are no errors.

## Must not
- Silence findings by deleting content you do not understand; fix the cause or explain the accepted warning.
- Edit the bundled `scripts/lint.py`; change the source `tools/lint.py` in the stablehand repo instead.

## Done when
- [ ] The linter exits 0, or exits 0 with `--strict` if the user asked for strict mode
- [ ] Every accepted warning has a one-line reason in your reply
