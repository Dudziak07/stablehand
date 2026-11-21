---
name: writing-project-instructions
description: "Writes, trims or audits always-loaded project instructions (AGENTS.md, GEMINI.md, .agents/rules, CLAUDE.md) so they contain only non-inferable facts and verified commands. Use when asked to create, update, shorten or audit AGENTS.md, GEMINI.md or rules, add path-scoped rules, or align instructions across Antigravity, Claude Code and OpenCode. Not for task-specific procedures (use authoring-skills) or user documentation."
---

Every line in an always-loaded file costs context on every task. Keep only facts the agent cannot infer from the repository, and verify every command you write down.

Reference material (read when a step says so):
- `references/targets.md`: establishing the target repository and access to it.
- `references/coexistence.md`: which files are read by which platforms and avoiding collisions.
- `references/writing-for-agents.md`: what to omit and keeping always-loaded files concise.
- `references/antigravity.md`: Antigravity instruction files, rule triggers, 24 KB limits, and the 20k always-on budget.
- `references/claude-code.md`: Claude Code conventions when sharing instructions with Claude Code.
- `references/opencode.md`: OpenCode conventions when sharing instructions with OpenCode.

## Process

0. **Target.**
   - **Target repository.** Take it from the user's prompt; ask if missing. Use the current directory only if it is not the stablehand repo. Never write into stablehand.
   - **Access & Workspace.** `run_command` in Antigravity requires `Cwd` to be within the active workspace. When running commands in the target, ensure the target folder is added to the workspace (multi-root workspace in App/IDE, or `agy --add-dir <target>` / `/add-dir` in CLI) or launch `agy` from the target folder.
   - **Target platform.** Establish which platforms open the repo (Antigravity by default, or Claude Code / OpenCode).
   - **Confirmation.** Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Inventory the target.** Read existing `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md`, `CLAUDE.md`, `.claude/rules/`, README, package manifests, scripts, and CI configurations. Ask which platforms open the repository if not already known.

2. **Collect candidate facts**:
   - **Commands:** build, test, single test, lint, format, run locally.
   - **Non-obvious conventions:** architecture, naming, layering, error handling not self-evident from code.
   - **Boundaries:** never edit generated files or migrations by hand; secrets location.
   - **Gotchas:** scars from real incidents with their observed symptoms.
   - **Pointers:** locations of specs, fixtures, or schemas.

3. **Filter.** Eliminate:
   - anything inferable from code or configuration;
   - generic best practices ("write clean code");
   - tutorial or conceptual prose;
   - procedures used only for specific tasks (these become skills; leave at most a one-line pointer).

   Verify each command against repository files; execute fast, safe commands to confirm. Always run target commands from inside the target directory (`cd "<target>" && uv run …`, never `--project` from stablehand).

4. **Choose files** (see `references/coexistence.md`):
   - **Antigravity and shared canonical file:** `AGENTS.md` (at repo root, no frontmatter). Antigravity walks up from the workspace folder to the repository root, never down into subfolders; use `@[label](<path>)` to inline files (before the 24 KB limit) and `@<filename>` to reference canonical workspace paths.
   - **Antigravity path-scoped rules:** `.agents/rules/<topic>.md` with frontmatter:
     - `trigger: glob` and `globs: "src/db/**,migrations/**"` (comma-separated string, not a YAML list; quote patterns starting with `*`)
     - or `trigger: model_decision` with `description: "..."`
     - or `trigger: manual` for `@`-mention only (not supported in Antigravity CLI)
     - keep each file under 24 KB.
   - **Claude Code compatibility:** if Claude Code also opens the repository, create `CLAUDE.md` starting with `@AGENTS.md` followed by Claude-specific directives.
   - **OpenCode compatibility:** OpenCode reads `AGENTS.md` natively.

5. **Write.** Use short, imperative bullet points under distinct headings (Commands, Conventions, Boundaries, Gotchas). Keep total length ≤ 150 lines.

6. **Validate.**
   Determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from the directory containing this `SKILL.md`. Run:
   `uv run "<absolute-path-to-scripts/lint.py>" --platform antigravity "<file>"`
   or invoke `/stablehand:validating-artifacts`. For shared projects, add `--project "<target>"`.

7. **Test in a fresh session.** Ask 3 test questions the instructions must answer from the target repository root:
   `agy -p "What command runs a single test here? Answer with the command only."`
   Vague or incorrect answers mean the fact is missing or buried; refine and re-test.

8. **Report:** files created or updated, line counts, and what was removed with justifications.

## Done when
- [ ] Every line is a non-inferable fact, verified command, boundary, or pointer
- [ ] Total lines stay within ~150 lines; procedures are moved to skills
- [ ] Cross-platform instruction bridges (e.g. `CLAUDE.md` importing `@AGENTS.md`) are correct
- [ ] The validator reports zero errors and fresh-session questions succeed
