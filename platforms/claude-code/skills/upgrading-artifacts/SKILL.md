---
name: "upgrading-artifacts"
description: "Audits and upgrades existing skills, subagents, rules, and instruction files in a target repository after a stablehand, platform, or model update, treating missing manifests as unknown legacy versions. Use when asked to refresh, upgrade, audit, or rewrite old skills or agents for a newer model or platform version. Not for creating new artifacts from scratch or porting between platforms."
argument-hint: "[target repo or artifact path]"
---

Audit and upgrade existing artifacts in a target repository against the current platform card and model guidance. Never write target artifacts into stablehand, and never edit any artifact before the user approves the upgrade plan.

Reference material:
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`: current Claude Code fields, tools, hooks, and limits.
- `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`: current model calibration and progressive disclosure rules.
- `${CLAUDE_PLUGIN_ROOT}/references/eval-protocol.md`: A/B evals and decision rules.
- `${CLAUDE_PLUGIN_ROOT}/references/decision-guide.md`: when to keep, rewrite, or retire an agent or skill.
- `${CLAUDE_PLUGIN_ROOT}/references/coexistence.md`: safe placement across platforms.
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: establishing the target repository and access.

## Process

0. **Target.** Establish the target repository and platform (`targets.md`). If the target is outside the working directory, ask the user to run `/add-dir <path>` first. Confirm in one line:
   `Target: <path> · Platform: <platform> · Upgrading: <scope>`

1. **Inventory & manifest (read-only).**
   - Read `<target>/.stablehand/manifest.json` if it exists. If missing, or if an artifact is not listed, record its version as `unknown (legacy)`.
   - Discover existing skills, subagents, rules, and instruction files across the target's customization folders.
   - Run the project-mode validator:
     `uv run "${CLAUDE_PLUGIN_ROOT}/skills/validating-artifacts/scripts/lint.py" --project "<target>"`
   - Read `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md` (or the target platform's card) and `writing-for-agents.md`. If a relevant field may have changed since the card's `Last verified` date, delegate a check to `stablehand:platform-researcher`.

2. **Review.** For each artifact in scope, use the Agent tool with `subagent_type: "stablehand:artifact-reviewer"`, passing the artifact path, the target platform card, and `writing-for-agents.md`. Identify deprecated fields, broken tool/hook syntax, legacy model workarounds (such as `"Think step-by-step"` boilerplate), or oversized always-loaded instructions.

3. **Upgrade plan (approval gate).** Present a table with one row per artifact:
   `Path | Recorded version | Findings | Action (keep / patch / rewrite / retire) | Reason`
   **Wait for explicit user approval before editing or deleting any file.**

4. **Execute approved actions** (one artifact at a time):
   - **`keep`:** leave unchanged.
   - **`patch`:** apply minimal mechanic/schema fixes, run `lint.py --platform <target> <path>`, and re-run `stablehand:artifact-reviewer`.
   - **`rewrite`:** extract a ≤ 10-line behavior contract from the old artifact, write a clean replacement calibrated for the current platform and model (`writing-for-agents.md`), run `lint.py`, run an A/B eval in a git worktree or scratch copy (baseline vs old artifact vs new artifact via `stablehand:scenario-runner` and `run_triggers.py`, unless the user explicitly skips testing—then mark `"untested"`), and run `stablehand:artifact-reviewer`.
   - **`retire`:** verify baseline passes without the artifact (or record user override), then remove the artifact.

5. **Update manifest.** Create or update `<target>/.stablehand/manifest.json` with `stablehand_version` and per-artifact `kind`, `platform`, `card_verified`, `target_model`, and `updated_at`, removing retired entries.

6. **Hand over.** Report paths kept, patched, rewritten, or retired; validator, A/B eval, and reviewer results; manifest update status; and any untested items.

## Done when
- [ ] The upgrade plan was approved before any file was edited
- [ ] All patched or rewritten artifacts pass `lint.py` with zero errors and have no open blocking reviewer findings
- [ ] Rewritten artifacts were A/B tested against baseline and old version (or explicitly marked `"untested"` on user request)
- [ ] `<target>/.stablehand/manifest.json` reflects the current state
