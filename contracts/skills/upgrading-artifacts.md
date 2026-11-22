---
id: upgrading-artifacts
kind: skill
version: 2026.11.1
references: [targets.md, writing-for-agents.md, eval-protocol.md, decision-guide.md, coexistence.md, "@platform"]
---
# upgrading-artifacts

## Purpose
Audit and upgrade existing skills, subagents, rules, and instruction files in **a target repository** after a stablehand, platform, or model update. If `.stablehand/manifest.json` is missing or omits an artifact, treat that artifact's version as `unknown (legacy)` and audit it anyway. Supports minimal schema/mechanic patches, clean contract-first rewrites calibrated for newer models, and retiring artifacts that newer models no longer need.

## Triggers
- **Should:**
  - "upgrade/refresh/audit our existing skills or agents";
  - "update skills created with an older stablehand or model version";
  - "rewrite this old skill for the newer model";
  - "check if our `.claude` / `.agents` / `.opencode` artifacts are stale".
- **Should not:**
  - creating a brand-new skill or agent from scratch (that is `authoring-skills` or `authoring-agents`);
  - porting an artifact to a different platform (that is `porting-artifacts`);
  - running static format checks only (that is `validating-artifacts`).

## Inputs
- The target repository path (and optionally a specific artifact path to focus on).
- The target platform (default: the host platform, or all platforms present in the target).
- Optionally, a target model family or version if upgrading for a new model.

## Procedure
0. **Target.** Establish the target repository, access to it, and the target platform(s) (`targets.md`). Never write target artifacts into stablehand. Confirm in one line.
1. **Inventory & manifest (read-only).**
   - Read `<target>/.stablehand/manifest.json` if it exists. If missing, or if an artifact is absent from it, record that artifact's version as `unknown (legacy)`.
   - Discover existing skills, agents, rules, and instruction files in the target (using `coexistence.md` paths) and run the bundled validator in project mode (`--project`).
   - Read the target platform card and `writing-for-agents.md`. If the card may be stale for relevant fields, delegate a check to the `platform-researcher` agent.
2. **Review.**
   - Delegate each artifact in scope to the `artifact-reviewer` agent against the current platform card and `writing-for-agents.md`.
   - Flag: deprecated frontmatter/fields, broken tool or permission names, legacy model workarounds (such as "think step-by-step" boilerplate or redundant rules), or oversized always-loaded instructions.
3. **Upgrade plan (approval gate).**
   - Present one row per artifact: path, recorded version (or `unknown (legacy)`), findings, recommended action (`keep`, `patch`, `rewrite`, `retire`), and reason.
   - **Write nothing before the user approves the plan.**
4. **Execute approved actions** (one artifact at a time):
   - `keep`: leave unchanged.
   - `patch`: apply minimal mechanic/schema fixes, run the validator, and re-run `artifact-reviewer`.
   - `rewrite`: extract a ≤ 10-line behavior contract from the old artifact, write a clean replacement calibrated for the current platform and model (`writing-for-agents.md`), run the validator, run an A/B comparison in a scratch copy or git worktree (baseline vs old artifact vs new artifact — unless the user explicitly skips testing, in which case record "untested"), and run `artifact-reviewer`.
   - `retire`: verify baseline passes without the artifact (or record user override), then remove the artifact.
5. **Update manifest.** Create or update `<target>/.stablehand/manifest.json` with `stablehand_version` and per-artifact `kind`, `platform`, `card_verified`, `target_model`, and `updated_at`, removing retired entries.
6. **Hand over.** Report:
   - paths kept, patched, rewritten, or retired;
   - validator, A/B eval, and reviewer outcomes;
   - `.stablehand/manifest.json` updated;
   - any untested items or remaining warnings.

## Outputs
- Upgraded/rewritten artifacts in their native target locations.
- Updated `<target>/.stablehand/manifest.json` (and eval results under `.stablehand/evals/` when rewrites/retirements are tested).
- Final upgrade report.

## Done when
- The upgrade plan was approved before any file was edited.
- All patched or rewritten artifacts pass the validator with zero errors and have no open blocking reviewer findings.
- Rewritten artifacts were A/B tested against baseline and old version (or explicitly marked "untested" on user request).
- `<target>/.stablehand/manifest.json` reflects the current state.

## Must not
- Edit, rewrite, or delete any artifact before the user approves the upgrade plan.
- Fail or refuse to run when `.stablehand/manifest.json` is missing.
- Store stablehand tracking metadata inside skill or agent YAML frontmatter when it risks breaking platform loaders.
- Run evals in the live target checkout instead of a scratch copy or git worktree.

## Platform adaptation
- **Access to a target repository outside the workspace** (`targets.md`).
- **Validator invocation path** and `--project` mode.
- **Delegation syntax** to `artifact-reviewer`, `scenario-runner`, and `platform-researcher`.
- **Headless real-loader command** for A/B evals.

## Evals
`upgrade-stale-skill`
