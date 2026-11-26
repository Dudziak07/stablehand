---
name: "writing-project-instructions"
description: "Writes, trims, or audits always-loaded project instructions (AGENTS.md, AGENTS.override.md, CLAUDE.md, GEMINI.md, and rule files) so they hold only non-inferable facts and verified commands. Use when creating or cleaning up project instructions or rules. Not for task-specific procedures (use authoring-skills) or READMEs."
---

Always-loaded instructions share budget with every task. Keep only what the agent cannot infer from the codebase. Write all output in English.

Reference material (in this skill's folder):
- `references/targets.md`: establishing the target repo and access.
- `references/coexistence.md`: `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md` `@AGENTS.md` bridge, and rule paths.
- `references/writing-for-agents.md`: concise instruction style and budgets.
- `references/codex.md`, `references/claude-code.md`, `references/antigravity.md`, `references/opencode.md`: platform limits and rule formats.

## Process

0. **Target.** Establish the target repository and access (`references/targets.md`). Never write into `stablehand`.
1. **Inventory (read-only):** inspect existing `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `GEMINI.md`, rule files, `README.md`, manifests, and CI workflows.
2. **Collect candidate facts:** verified build/test/lint/single-test commands, non-obvious conventions, boundaries, real gotchas, and directory pointers.
3. **Filter:** remove inferable structure, generic advice, and multi-step procedures (move procedures to `authoring-skills`). Verify commands in the target repo.
4. **Choose files** per `references/coexistence.md`:
   - `AGENTS.md` as the shared canonical file across Codex, OpenCode, and Antigravity;
   - `AGENTS.override.md` only for local/temporary Codex overrides;
   - `CLAUDE.md` starting with `@AGENTS.md` when Claude Code also opens the repo;
   - scoped rules only for path-specific facts (`.claude/rules/*.md`, `.agents/rules/*.md`).
5. **Write.** Short imperative lines under clear headings, targeting <= 150 lines (and well under Codex's 32 KiB cap). No YAML frontmatter in `AGENTS.md` or `AGENTS.override.md`.
6. **Test & manifest.** In a fresh headless session (`codex exec --ephemeral --sandbox read-only -C "<target>" "<question>"`), ask 3 questions the file must answer. Validate with `$validating-artifacts`. Update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`).

## Done when
- [ ] Every line is a non-inferable fact or pointer with verified commands
- [ ] Size is within budget and bridges/rules follow `coexistence.md`
- [ ] Fresh-session questions pass and the validator reports no errors
