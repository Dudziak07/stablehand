---
name: "upgrading-artifacts"
description: "Audits and upgrades existing skills, subagents, rules, and instruction files in a target repository after a stablehand, platform, or model update, treating missing manifests as unknown legacy versions. Use when asked to refresh, upgrade, audit, or rewrite old skills or agents for a newer model or platform version. Not for creating new artifacts from scratch or porting between platforms."
metadata:
  opencode/slash: "true"
---

Audit and upgrade existing artifacts in a target repository against the current platform card and model guidance. Never write target artifacts into stablehand, and never edit any artifact before the user approves the upgrade plan. Write all output in English.

Reference material (in this skill's folder):
- `references/opencode.md`: current OpenCode V2 fields, `permissions` array, and DeepSeek notes.
- `references/writing-for-agents.md`: current model calibration and progressive disclosure rules.
- `references/eval-protocol.md`: A/B evals and decision rules.
- `references/decision-guide.md`: when to keep, rewrite, or retire an agent or skill.
- `references/coexistence.md`: safe placement across platforms.
- `references/targets.md`: establishing the target repository and access.

## Process

0. **Target.** Establish the target repository and platform (`references/targets.md`). If the target is outside the workspace, approve the `external_directory` prompt. Confirm in one line:
   `Target: <path> · Platform: <platform> · Upgrading: <scope>`

1. **Inventory & manifest (read-only).**
   1. Read `<target>/.stablehand/manifest.json` if it exists. If missing, or if an artifact is absent from it, record its version as `unknown (legacy)`.
   2. List existing skills, agents, rules, and instruction files across the target's customization folders.
   3. Call the `skill` tool with id `validating-artifacts` and check the target with `--project "<target>"`.
   4. Read `references/opencode.md` and `references/writing-for-agents.md`. If a relevant field may be stale relative to `Last verified`, use the `subagent` tool with agent `platform-researcher`.

2. **Review.** For each artifact in scope, use the `subagent` tool with agent `artifact-reviewer`, passing the artifact path plus absolute paths to `references/opencode.md` and `references/writing-for-agents.md`. Identify V1 deprecated `permission` maps or `bash`/`task` action names, `tools:` maps, legacy model workarounds (such as `"Think step-by-step"` boilerplate), or oversized `AGENTS.md` files.

3. **Upgrade plan (approval gate).** Present this table:
```
| Path | Recorded version | Findings | Action (keep/patch/rewrite/retire) | Reason |
```
   **Stop and wait for explicit user approval before editing or deleting any file.** (In non-interactive headless runs, state your assumptions and proceed.)

4. **Execute approved actions** (one artifact at a time):
   - **`keep`:** leave unchanged.
   - **`patch`:** apply minimal mechanic/schema fixes, validate with `validating-artifacts`, and re-run `artifact-reviewer`.
   - **`rewrite`:** extract a ≤ 10-line behavior contract from the old artifact, write a clean replacement calibrated for DeepSeek and OpenCode V2 (`references/writing-for-agents.md`), validate with `validating-artifacts`, run an A/B eval in a scratch copy or git worktree using `scenario-runner` and `opencode run ... --format json` (unless the user explicitly skips testing—then mark `"untested"`), and run `artifact-reviewer`.
   - **`retire`:** verify baseline passes without the artifact (or record user override), then remove the artifact.

5. **Update manifest.** Create or update `<target>/.stablehand/manifest.json` with `stablehand_version` and per-artifact `kind`, `platform`, `card_verified`, `target_model`, and `updated_at`, removing retired entries.

6. **Hand over.** Use this template:
```
Kept: <paths or "none">
Patched: <paths or "none">
Rewritten: <paths or "none">
Retired: <paths or "none">
Validation & Review: <pass/fail summary>
Manifest: <target>/.stablehand/manifest.json (updated)
Untested: <list or "none">
```

## Done when
- [ ] The upgrade plan was approved before any file was edited
- [ ] All patched or rewritten artifacts pass `validating-artifacts` with zero errors and have no open blocking reviewer findings
- [ ] Rewritten artifacts were A/B tested against baseline and old version (or explicitly marked `"untested"` on user request)
- [ ] `<target>/.stablehand/manifest.json` reflects the current state
