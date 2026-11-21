---
name: validating-artifacts
description: "Validates Antigravity, Claude Code and OpenCode skills, agents, rules and instruction files using a bundled static linter, and checks for cross-platform collisions. Use when asked to lint, check or validate agent artifacts, when a skill or agent fails to load, or before committing customizations. Not for behavior testing or linting application code."
---

Run the bundled static linter, fix all errors, and justify any warnings accepted. Because harnesses can ignore invalid files silently, this validation is an essential quality gate.

Reference material:
- `references/coexistence.md`: avoiding cross-platform naming and location collisions.
- `references/antigravity.md`: Antigravity artifact rules, tool names, and constraints.

The linter is `scripts/lint.py`, a generated copy of the toolkit linter: never edit it directly. It requires `uv` (or Python ≥ 3.11 with PyYAML).

Determine the absolute directory containing this `SKILL.md` file (`<skill-dir>`). Execute `uv run "<skill-dir>/scripts/lint.py" ...` using absolute paths for target artifacts without changing working directory into the skill folder.

Typical locations of `scripts/lint.py`:
- Workspace plugin: `<repo>/.agents/plugins/stablehand/skills/validating-artifacts/scripts/lint.py`
- Global plugin: `~/.gemini/config/plugins/stablehand/skills/validating-artifacts/scripts/lint.py`
- Local checkout: `platforms/antigravity/skills/validating-artifacts/scripts/lint.py`

## Commands
```bash
# Validate one skill folder, SKILL.md, agent file, rule, or instruction file:
uv run "<skill-dir>/scripts/lint.py" --platform antigravity "<target-path>"

# Validate a folder containing skills/, agents/, rules/ (e.g. a plugin):
uv run "<skill-dir>/scripts/lint.py" --platform antigravity "<plugin-folder>"

# Validate an entire repository (scans all platforms and checks collisions):
uv run "<skill-dir>/scripts/lint.py" --project "<target-repo>"
```
To validate artifacts for other platforms, use `--platform claude-code` or `--platform opencode`. Pass `--json` for structured output and `--strict` to fail on warnings. For Antigravity plugins, also run `agy plugin validate --strict "<plugin-folder>"` when `agy` is installed.

## Process
1. **Select mode:** choose single path, plugin folder, or `--project <target-repo>`. Use `--project` whenever multiple platforms share the repository.
2. **Run the linter:** exit code 0 indicates clean validation.
3. **Fix errors:**
   | Code | Meaning | Fix |
   |---|---|---|
   | S002 / A001 | Frontmatter missing or invalid YAML | Close `---` block; double-quote strings containing `: ` |
   | S005 | Name does not match folder | Rename folder or `name` field |
   | S020 | Linked reference or script missing | Create file or correct relative path |
   | A030 / A035 | Missing required agent field or invalid type | Supply required string or boolean |
   | A031 | Unknown Antigravity tool name | Use exact tool name from `references/antigravity.md` section 5 |
   | A033 | Invalid model tier | Use `inherit`, `flash_lite`, `flash`, or `pro` |
   | R001 | Invalid rule trigger | Use `always_on`, `model_decision`, `glob`, or `manual` |
   | P002 | Deprecated workflow folder | Migrate workflow to skill |
   | P003 | Duplicate skill name in OpenCode | Rename or set `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` |
4. **Address warnings:** fix each warning or document its justification. To suppress an approved warning on a file, add `<!-- stablehand-lint: ignore CODE -->`.
5. **Re-run:** continue until zero errors remain.

## Must not
- Edit the vendored `scripts/lint.py`. Changes go to `tools/lint.py` in the stablehand repo.
- Silence findings by deleting content without understanding them. Fix the cause, or keep the content and justify the warning.

## Done when
- [ ] The linter exits 0 (or exits 0 with `--strict` if requested)
- [ ] Every accepted warning has a clear justification in the response
