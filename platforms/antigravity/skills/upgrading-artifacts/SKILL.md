---
name: "upgrading-artifacts"
description: "Audits and upgrades existing skills, subagents, rules, and instruction files in a target repository after a stablehand, platform, or model update, treating missing manifests as unknown legacy versions. Use when asked to refresh, upgrade, audit, or rewrite old skills or agents for a newer model or platform version. Not for creating new artifacts from scratch or porting between platforms."
---

Audit and upgrade existing artifacts in a target repository against the current platform card and model guidance. Never write target artifacts into stablehand, and never edit any artifact before the user approves the upgrade plan.

Reference material (bundled inside this skill's folder):
- `references/antigravity.md`: current Antigravity fields, canonical Cortex tool names, and limits.
- `references/writing-for-agents.md`: current model calibration and progressive disclosure rules.
- `references/eval-protocol.md`: A/B evals and decision rules.
- `references/decision-guide.md`: when to keep, rewrite, or retire an agent or skill.
- `references/coexistence.md`: safe placement across platforms.
- `references/targets.md`: establishing the target repository and access.

## Process

0. **Target.** Establish the target repository and platform (`references/targets.md`). In Antigravity, `run_command` requires the target repository to be in the active workspace (multi-root workspace or `agy --add-dir`). Confirm in one line:
   `Target: <path> · Platform: <platform> · Upgrading: <scope>`

1. **Inventory & manifest (read-only).**
   - Read `<target>/.stablehand/manifest.json` if it exists. If missing, or if an artifact is absent from it, record its version as `unknown (legacy)`.
   - Discover existing skills, agents, rules, and instruction files across the target's customization folders.
   - Determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from this `SKILL.md` directory and run:
     `uv run "<absolute-path-to-scripts/lint.py>" --project "<target>"`
   - Read `references/antigravity.md` and `references/writing-for-agents.md`. If a relevant field may be stale relative to `Last verified`, delegate a check to `platform-researcher` via `invoke_subagent`.

2. **Review.** For each artifact in scope, delegate to `artifact-reviewer` via `invoke_subagent`, passing the artifact path plus absolute paths to the target platform card and `references/writing-for-agents.md`. Identify deprecated fields, model-facing tool aliases (`read_file`, `edit_file`, `write_file`) in agent `tools:`, legacy model workarounds (such as `"Think step-by-step"` boilerplate), or oversized always-loaded instructions.

3. **Upgrade plan (approval gate).** Present a table with one row per artifact:
   `Path | Recorded version | Findings | Action (keep / patch / rewrite / retire) | Reason`
   **Wait for explicit user approval before editing or deleting any file.**

4. **Execute approved actions** (one artifact at a time):
   - **`keep`:** leave unchanged.
   - **`patch`:** apply minimal mechanic/schema fixes, run `lint.py --platform <target> "<path>"`, and re-run `artifact-reviewer` via `invoke_subagent`.
   - **`rewrite`:** extract a ≤ 10-line behavior contract from the old artifact, write a clean replacement calibrated for the current platform and model (`references/writing-for-agents.md`), run `lint.py`, run an A/B eval in a scratch copy or git worktree (baseline vs old artifact vs new artifact via `scenario-runner` and `agy -p ... --output-format stream-json`, unless the user explicitly skips testing—then mark `"untested"`), and run `artifact-reviewer`.
   - **`retire`:** verify baseline passes without the artifact (or record user override), then remove the artifact.

5. **Update manifest.** Create or update `<target>/.stablehand/manifest.json` with `stablehand_version` and per-artifact `kind`, `platform`, `card_verified`, `target_model`, and `updated_at`, removing retired entries.

6. **Hand over.** Report paths kept, patched, rewritten, or retired; validator, A/B eval, and reviewer outcomes; manifest update status; and any untested items.

## Done when
- [ ] The upgrade plan was approved before any file was edited
- [ ] All patched or rewritten artifacts pass `lint.py` with zero errors and have no open blocking reviewer findings
- [ ] Rewritten artifacts were A/B tested against baseline and old version (or explicitly marked `"untested"` on user request)
- [ ] `<target>/.stablehand/manifest.json` reflects the current state
