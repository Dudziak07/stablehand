---
name: "upgrading-artifacts"
description: "Audits and upgrades existing skills, subagents, rules, and instruction files in a target repository after a stablehand, platform, or model update, treating missing manifests as unknown legacy versions. Use when refreshing, auditing, or rewriting stale artifacts. Not for creating new artifacts from scratch or porting between platforms."
---

Audit and upgrade existing artifacts in a target repository against the current platform card and model guidance. Never write target artifacts into `stablehand`, and never edit any artifact before the user approves the upgrade plan. Write all output in English.

Reference material (in this skill's folder):
- `references/codex.md`: current OpenAI Codex CLI fields, `.codex/agents/*.toml`, `.agents/skills/`, and sandbox modes.
- `references/writing-for-agents.md`: current model calibration and progressive disclosure rules.
- `references/eval-protocol.md`: A/B evals and decision rules.
- `references/decision-guide.md`: when to keep, rewrite, or retire an agent or skill.
- `references/coexistence.md`: safe placement across platforms.
- `references/targets.md`: establishing the target repository and access.

## Process

0. **Target.** Establish the target repository and platform (`references/targets.md`). Confirm in one line:
   `Target: <path> · Platform: <platform> · Upgrading: <scope>`
1. **Inventory & manifest (read-only).**
   - Read `<target>/.stablehand/manifest.json` if it exists. If missing, or if an artifact is omitted, record its version as `unknown (legacy)`.
   - List existing skills, agents, rules, and instruction files across the target's folders (`references/coexistence.md`).
   - Invoke `$validating-artifacts` to check `--project "<target>"`.
   - Read `references/codex.md` and `references/writing-for-agents.md`. If a field may be stale relative to `Last verified`, spawn `platform-researcher`.
2. **Review.** For each artifact in scope, spawn `artifact-reviewer` with the artifact path plus absolute paths to `references/codex.md` and `references/writing-for-agents.md`. Flag deprecated fields, wrong tool/sandbox settings, legacy prompt boilerplate, or oversized `AGENTS.md` files.
3. **Upgrade plan (approval gate).** Present one row per artifact: `Path | Recorded version | Findings | Action (keep/patch/rewrite/retire) | Reason`. **Wait for explicit user approval before editing or deleting any file.**
4. **Execute approved actions** (one artifact at a time):
   - `keep`: leave unchanged.
   - `patch`: apply minimal schema/mechanic fixes, validate with `$validating-artifacts`, and re-run `artifact-reviewer`.
   - `rewrite`: extract a <= 10-line behavior contract, write a clean replacement calibrated per `references/writing-for-agents.md`, validate, run an A/B eval in a scratch copy or git worktree via `scenario-runner` and `codex exec --ephemeral --json` (unless the user explicitly skips testing — then mark `"untested"`), and run `artifact-reviewer`.
   - `retire`: verify baseline passes without the artifact (or record user override), then remove it.
5. **Update manifest.** Create or update `<target>/.stablehand/manifest.json` with `stablehand_version` and per-artifact `kind`, `platform`, `card_verified`, `target_model`, and `updated_at`, removing retired entries.
6. **Hand over.** Summarize `Kept`, `Patched`, `Rewritten`, `Retired`, validation/review outcomes, updated manifest path, and any untested items.

## Done when
- [ ] Upgrade plan was approved before any edits
- [ ] All patched/rewritten artifacts pass `$validating-artifacts` with zero errors and have no open blocking findings
- [ ] Rewritten artifacts were A/B tested (or marked `"untested"` on explicit user request)
- [ ] `<target>/.stablehand/manifest.json` is updated
