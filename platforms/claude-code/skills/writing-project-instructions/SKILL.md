---
name: writing-project-instructions
description: "Writes, trims or audits the always-loaded instructions of a given repository (CLAUDE.md, AGENTS.md, .claude/rules, Antigravity rules) so they hold only facts the agent cannot infer from the code. Use when asked to create, update, shorten or clean up CLAUDE.md or AGENTS.md for this or another repo, add a path-specific rule, or share instructions between Claude Code and other agents. Not for task procedures (use authoring-skills) or human docs."
argument-hint: "[target repo path]"
---

Every line in an always-loaded file costs context on every task. Keep only facts the agent can't infer from the repo, and verify every command you write down.

Reference material:
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: the target repo and access to it.
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`, section 1: files, imports, `.claude/rules`, AGENTS.md behavior.
- `${CLAUDE_PLUGIN_ROOT}/references/coexistence.md`: which file other platforms read.
- `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`: what to leave out.

## Process

0. **Target.**
   - **Target repo.** Take it from the request or `$ARGUMENTS`; ask if it is missing. Use the current directory only if it is not the stablehand repo. Never write into stablehand.
   - **Access.** If the target is outside the working directory, ask the user to run `/add-dir <path>` first.
   - **Confirm** in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Inventory the target.** Read the existing `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `.claude/rules/`, `.agents/rules/`, the README, manifests and scripts, and CI. Ask which agent platforms open the repo, if that isn't known.

2. **Collect candidate facts**:
   - **Commands:** build, test, a single test, lint, format, run locally.
   - **Non-obvious conventions:** naming, layering, error handling the code doesn't make evident.
   - **Boundaries:** never edit generated files or migrations by hand; secrets live in X.
   - **Gotchas** from real incidents, with the symptom.
   - **Pointers:** where docs, specs or fixtures live.

3. **Filter.** Remove:
   - anything inferable from the code or config;
   - general good practice ("write clean code");
   - tutorials;
   - procedures used only for some tasks. These become skills; leave at most a one-line pointer.

   Verify each command against the scripts; run it when it is safe and fast.

4. **Choose files** (see `coexistence.md`):
   - **Claude Code only:** `CLAUDE.md`.
   - **Shared with Antigravity/OpenCode:** `AGENTS.md` is canonical. Claude Code reads AGENTS.md only when no CLAUDE.md is in that directory. If Claude-only facts are needed, create `CLAUDE.md` starting with `@AGENTS.md`, then the Claude-only lines.
   - **Facts for some paths only:** `.claude/rules/<topic>.md` with frontmatter `paths: ["migrations/**"]`. On Antigravity, use `.agents/rules/<topic>.md` with `trigger: glob` and `globs:` (see `antigravity.md`, section 2).
   - **Personal, not shared:** `CLAUDE.local.md` (gitignored).

5. **Write.** Use short imperative lines under a few headings (Commands, Conventions, Boundaries, Gotchas). Target ≤ 150 lines in total; the evidence says long context files cost more than they help. No frontmatter in AGENTS.md.

6. **Validate.**
   `uv run "${CLAUDE_PLUGIN_ROOT}/skills/validating-artifacts/scripts/lint.py" --platform claude-code <file>`
   For a shared setup, add `--project <root>`.

7. **Test in a fresh session.** Ask 3 questions the file must answer, from the target root, for example:
   `cd "<target>" && claude -p "What command runs a single test file here? Answer with the command only."`
   Wrong or vague answers mean the fact is missing or buried; fix and re-ask.

8. **Report:** update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`), then list the file(s) written, line counts, and what you removed and why.

## Done when
- [ ] Every line is a non-inferable fact, a verified command, a boundary, or a pointer
- [ ] The total is within ~150 lines; procedures have moved to skills
- [ ] The CLAUDE.md ↔ AGENTS.md bridge is correct for the platforms in use
- [ ] The validator is clean and the fresh-session questions are answered correctly
