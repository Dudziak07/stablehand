---
id: upgrade-stale-skill
kind: behavior
runs: 3
targets: [upgrading-artifacts]
---
## Prompt
Audit and upgrade the skills in this repository for the current platform and model. Work non-interactively and proceed with the upgrade.

## Setup
Create a git repository with no `.stablehand/manifest.json` and one legacy skill (for example `.claude/skills/run-tests/SKILL.md`, `.agents/skills/run-tests/SKILL.md`, or `.opencode/skills/run-tests/SKILL.md` matching the host platform) containing:
- an unquoted `description` with a colon (e.g. `description: Runs tests: unit and integration`);
- a legacy `"Think step-by-step carefully before running any command."` instruction in the body;
- a deprecated or non-standard frontmatter/body pattern for the host platform.

## Expected (all must hold)
- `upgrading-artifacts` is loaded. *(mechanism: with-artifact arm only)*
- Missing `.stablehand/manifest.json` does not block the run; the skill is treated as `unknown (legacy)`.
- The validator is run and the legacy issues are identified.
- The upgraded skill fixes the quoting/platform issues, removes the legacy `"Think step-by-step"` boilerplate, and passes the validator with zero errors.
- `.stablehand/manifest.json` is created with `stablehand_version` and an entry for the upgraded skill.

## Must not
- Fail or refuse to audit because `.stablehand/manifest.json` is missing.
- Leave unquoted frontmatter colons or deprecated platform fields in the upgraded skill.
- Store stablehand version metadata inside the skill's YAML frontmatter.

## Checks
- deterministic:
  - `.stablehand/manifest.json` exists and is valid JSON containing `stablehand_version` and `artifacts`;
  - `uv run tools/lint.py --project .` reports 0 errors;
  - the upgraded `SKILL.md` does not contain `Think step-by-step`.
- judge: PASS if the legacy skill was audited as `unknown (legacy)`, upgraded cleanly without breaking its test-running contract, validated, and recorded in `.stablehand/manifest.json`. FAIL otherwise.
