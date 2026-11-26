---
name: "designing-agent-setups"
description: "Designs the agent setup of a repository (instructions, skills, subagents, hooks) for OpenAI Codex CLI or another target platform, then builds each approved artifact in the target repository. Use when setting up, auditing, or overhauling a repo's customization or asking for role agents. Not for editing one named skill or agent."
---

Turn "make the agent work better on repo X" into a small, justified set of artifacts, built in repo X and verified one at a time. Deliver an approved blueprint plus the files it lists, not advice. Write all output in English.

Reference material (read when a step says so):
- `references/targets.md`: establishing the target repo, access (`--add-dir`, `-C`), and non-host platforms.
- `references/decision-guide.md`: choosing primitives, the five reasons for a subagent, and anti-patterns.
- `references/coexistence.md`: placement when Claude Code, Antigravity, or OpenCode also open the repo.
- `references/writing-for-agents.md`: concise instruction and skill style.
- `references/codex.md`, `references/claude-code.md`, `references/antigravity.md`, `references/opencode.md`: platform cards.

## Process

1. **Establish the target** (`references/targets.md`).
   - Target repo: take the path from the request (ask if missing). Never write artifacts into `stablehand`.
   - Confirm root: `git -C "<target>" rev-parse --show-toplevel` and read `<target>/README.md`.
   - Platform(s): Codex by default unless the user names another platform.
   - Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.
2. **Inventory (read-only).**
   - Inspect manifests, build/test/lint scripts, and CI workflows.
   - List existing customization: `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `GEMINI.md`, `.agents/`, `.codex/`, `.claude/`, `.opencode/`.
   - Invoke `$validating-artifacts` in `--project "<target>"` mode.
   - For large codebases, delegate the sweep to the built-in `explorer` subagent.
3. **Interview.** Ask one question at a time with a recommended answer until you know the 3-5 repeated workflows, concrete recent failures, solo vs team scope, and other platforms used. In headless mode, state assumptions instead.
4. **Decide** (`references/decision-guide.md`). Every proposed subagent must name one of the five reasons; drop persona agents with no reason. Prefer built-in `explorer` / `worker` over custom duplicates. Orchestration belongs in a skill, never a subagent.
5. **Blueprint & approval.** Present a table (`Artifact | Type | Path | Platform | When used | Justification | Eval idea`) ordered `instructions -> skills -> agents -> hooks`, following `references/coexistence.md`. **Create no files until the user approves.**
6. **Build one row at a time** by invoking the matching skill (`$writing-project-instructions`, `$authoring-skills`, `$authoring-agents`) or writing `hooks/hooks.json` for hooks.
7. **Validate.** Invoke `$validating-artifacts` again with `--project "<target>"` and fix all errors.
8. **Report.** List created paths, how to invoke each artifact (`$<skill>`, agent name, etc.), what was skipped and why, and follow-ups.

## Done when
- [ ] Target repo and platform confirmed; nothing written into `stablehand`
- [ ] Blueprint approved (or assumptions stated in headless mode) before any edits
- [ ] Every row built through its matching skill or explicitly deferred
- [ ] Project-mode validation exits 0 with no errors
