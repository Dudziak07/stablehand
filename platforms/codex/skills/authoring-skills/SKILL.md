---
name: "authoring-skills"
description: "Creates or improves one skill for a target repository and platform (Codex by default, or Claude Code, Antigravity, OpenCode on request), test-first with baseline and trigger checks. Use when asked to write, scaffold, refactor, or fix triggering of a skill. Not for subagents, AGENTS.md, or porting."
---

A skill earns its place by changing behavior. Prove the failure first, write the minimum that fixes it, and stop when the re-test passes. Write all output in English.

Reference material (in this skill's folder):
- `references/targets.md`: target repository, access, and non-host platforms.
- `references/writing-for-agents.md`: concise drafting rules.
- `references/eval-protocol.md`: scenario/trigger formats and decision rule.
- `references/decision-guide.md`: when to use instructions or a subagent instead.
- `references/coexistence.md`: safe placement across shared `.agents/skills/` and other platforms.
- `references/codex.md`, `references/claude-code.md`, `references/antigravity.md`, `references/opencode.md`: platform cards.

## Process

0. **Target** (`references/targets.md`). Confirm target repo, access, and platform in one line: `Target: <path> · Platform: <platform> · Building: <what>`. Never write into `stablehand`. If target != Codex, draft and lint for the target, skip steps 2 and 5, and hand off the eval prompt.
1. **Brief.** Confirm a skill fits (`references/decision-guide.md`), pick kebab-case name (<= 64 chars), type, scope (`.agents/skills/<name>/` or `~/.agents/skills/<name>/`), and check overlap across `.agents/skills/`.
2. **Baseline (RED).**
   - Write 3 scenarios + `triggers.yaml` under `<target>/.stablehand/evals/skills/<name>/` (`references/eval-protocol.md`).
   - Create an isolated git worktree or scratch copy `<scratch>` of `<target>`.
   - Spawn `scenario-runner` in mode `baseline` against `<scratch>` for 1-3 scenarios and record failures verbatim. If baseline already passes, stop (or keep only on explicit user override: record `"kept on user override, no measured gain"`).
3. **Draft** `SKILL.md` (`references/writing-for-agents.md`, `references/codex.md`):
   - Frontmatter: double-quoted `name` and `description` (triggers first, `"Not for ..."` exclusions, <= 500 chars).
   - Body: numbered steps with verifications, checkpoint before first side effect, `Done when` list, and relative links to `references/` or `scripts/`.
4. **Validate.** Invoke `$validating-artifacts` on the skill folder with `--platform <target>` and fix all errors.
5. **Re-test (GREEN).**
   - Install the skill into `<scratch>/.agents/skills/<name>/`.
   - Spawn `scenario-runner` in mode `with-artifact` against `<scratch>`.
   - Check triggers with the real loader: `codex exec --ephemeral --json --sandbox read-only --skip-git-repo-check -C "<scratch>" "<prompt>"`.
   - Iterate at most 3 times, save `results/<date>.md`, and clean up `<scratch>`.
6. **Review.** Spawn `artifact-reviewer` with the skill path, brief, target card path, `references/writing-for-agents.md`, and results file. Fix blocking findings and re-run reviewer once more.
7. **Hand over.** Update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`), then report path, invoke syntax (`$<name>`), baseline vs with-skill table, gaps, and untested status.

## Done when
- [ ] Validator reports zero errors for the target platform
- [ ] With-skill run beats baseline per `eval-protocol.md` (or marked `"untested"` / user override)
- [ ] Trigger set passes and `artifact-reviewer` has no open blocking findings
