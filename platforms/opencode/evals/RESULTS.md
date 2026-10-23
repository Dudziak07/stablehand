# OpenCode port — eval results

- **Platform:** OpenCode 1.19.3 on Windows (PowerShell 5.1).
- **Model:** `deepseek/deepseek-flash`.
- **Environment:** `PSExecutionPolicyPreference=Bypass`; `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`; `--copy` where a linked install would ask for `external_directory`.
- **Method:** 3 runs per arm, graded with the decision rule in `shared/references/eval-protocol.md`. Raw per-run detail is kept in the gitignored `evals/results/`.

## Summary

| Scenario | Baseline | With artifact | Decision |
|---|---|---|---|
| `persona-agents-pushback` | 0/3 | 3/3 | ship |
| `unrelated-request-no-trigger` | 3/3 | 3/3 | ship (no skill fires) |
| `external-target-repo` | 0/3 | 3/3 | ship |
| `skill-for-migrations` | 0/3 | 2/3 | ship |
| `agents-md-minimal` | 3/3 | 3/3 | no outcome gain |
| `port-reviewer-to-opencode` | 0/3 | 3/3 | ship (re-graded, see below) |

The baseline for `agents-md-minimal` already passed every outcome item, so that scenario is not evidence for shipping `writing-project-instructions`; the skill is kept for the other scenarios and its static checks.

## Re-grade: `port-reviewer-to-opencode` (2026-10-23)

Re-run with the current `porting-artifacts` skill, with-artifact arm only, 3 runs, each in a fresh scratch project installed with `--copy`.

| Expected item | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| `porting-artifacts` loaded | pass | pass | pass |
| file exists | pass | pass | pass |
| `mode: subagent` and a description | pass | pass | pass |
| read-only: `edit: deny`; `bash` and `shell` identical exact `git diff` allow-list, no trailing wildcard | pass | pass | pass |
| no `tools:`, Claude tool names or `name:` | pass | pass | pass |
| model omitted or `deepseek/...` | pass | pass | pass |
| lossy items and a hand-off prompt | pass | pass | pass |

Every Expected item holds in 3/3 runs. Decision: **ship**.

Behavioral check (run 1): on a staged change, the produced reviewer was asked to run `git status` and `git diff --staged --output=x.txt`. Both are outside its allow-list and were denied, and no file appeared.

Corrected grading of the earlier arms:

- **Baseline: FAIL.** Its files used `bash: {"*": deny, "git diff*": allow}`, which 1.19.3 does enforce, but the wildcard admits `--output=<file>`. The baseline also kept `name:`, missed `mode:` in one run and listed no lossy items.
- **Old with-artifact (shell only): FAIL on enforcement.** 1.19.3 silently ignores `shell`, so the read-only rule did not hold.
- **Corrected with-artifact (above): PASS**, 3/3.

Caveat: on 1.19.3 the working key is `bash`; `shell` alone enforces nothing, so both keys must carry identical rules.
## Efficiency

| Scenario | Baseline (s) | With artifact (s) | Note |
|---|---|---|---|
| `persona-agents-pushback` | 54 | 40 | faster |
| `unrelated-request-no-trigger` | 20 | 15 | faster |
| `external-target-repo` | 46 | 176 | slower; full authoring flow |
| `skill-for-migrations` | 17 | 187 | slower; baseline skipped testing |
| `agents-md-minimal` | 29 | 40 | slower |
| `port-reviewer-to-opencode` | 25 | 55 | slower |

The authoring skills trade time for the required testing and review steps.

## Caveats

- `/name` in the TUI was not exercised headlessly; model-triggered loads were.
- Natural-prompt delegation of the shipped agents was not benchmarked separately.
- A user-scope install resolves the vendored linter the same way as the workspace and project installs, but was not run.
- On Windows, the `skill` tool needs `PSExecutionPolicyPreference=Bypass` only when the machine's execution policy blocks the Archive module.

## Verification 2026-10-23

From a fresh clone of this branch, workspace-installed for OpenCode, against a scratch `demo-api` repository:

| Check | Command shape | Result |
|---|---|---|
| Read-only agent | `opencode run "<request>" --format json --dir "<clone>" --auto` | `authoring-agents` loaded; agent written only in `demo-api`; clone clean; `validating-artifacts` ran. |
| Skill | same, then an explicit request to proceed after the baseline passed | `authoring-skills` loaded; skill written only in `demo-api`; GREEN trigger run fired 6/6 and near-misses 0/6. |
| Port | same | `porting-artifacts` loaded; `code-reviewer` written only in `demo-api`; clone clean; `validating-artifacts` ran. |
| Permission check | reviewer subagents in a scratch copy with a staged change | commands outside each reviewer's `bash` allow-list (such as `git diff --output=x.txt`) were denied; no file appeared; `edit: deny` removed the edit tools, so no file changed. |

The first skill request stopped correctly because the baseline already passed; a follow-up request asked to build and trigger-test the skill anyway. Trigger-probe was copied into the scratch's `.opencode/agents/` before probing, which is the fixed path.
