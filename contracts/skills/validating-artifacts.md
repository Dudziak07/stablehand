---
id: validating-artifacts
kind: skill
version: 2026.10.0
references: [coexistence.md, "@platform"]
---
# validating-artifacts

## Purpose
Run static checks on skills, agents, rules and instruction files with the bundled linter, `scripts/lint.py`, a vendored copy of `tools/lint.py`. Explain the findings and fix the errors.

## Triggers
- **Should:**
  - "validate/lint this skill/agent";
  - "why doesn't my skill/agent load";
  - "check the project's agent setup for problems";
  - before committing agent artifacts;
  - when another stablehand skill reaches its validation step.
- **Should not:**
  - behavior testing (that is `evaluating-artifacts`);
  - linting the project's own source code.

## Inputs
- Path(s) to check, or a project directory.
- The target platform(s).

## Procedure
1. **Choose the mode:**
   - single artifact;
   - plugin or folder root;
   - `--project DIR`, which scans all of the platform's folders and checks cross-platform collisions.
2. **Run.** Use `uv run <path-to>/scripts/lint.py --platform <p> <paths>` or `--project <dir>`. Without uv, use any Python ≥ 3.11 with PyYAML installed.
3. **Fix.** Fix every error. Fix a warning, or explain why it is accepted.
4. **Re-run** until no errors remain.

## Outputs
- The linter report.
- A list of the fixes made, and of the warnings accepted with their reasons.

## Done when
- The linter exits 0, or `--strict` exits 0 if the user asked for strict mode.

## Must not
- Edit the vendored `scripts/lint.py`. Changes go to `tools/lint.py` in the stablehand repo.
- Silence findings by deleting content without understanding them.

## Platform adaptation
- **How the skill locates its own `scripts/lint.py`.** Claude `${CLAUDE_SKILL_DIR}`; elsewhere, the skill folder path stated explicitly.
- **Pre-approval of the `uv run` command,** where the platform supports it.

## Evals
Covered by `skill-for-migrations` and `port-reviewer-to-opencode` (both must end with a clean lint).
