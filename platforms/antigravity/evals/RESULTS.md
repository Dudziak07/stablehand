# Antigravity Evaluation Results

- **Platform:** Google Antigravity
- **Environment:**
  - CLI: `agy` 1.4.5
  - App: `2.0.10`
  - IDE: `2.5.5` (VS Code `1.107.0`)
  - Model: `gemini-3.8-flash-medium`
- **Execution Mode:** Headless loader execution via `agy -p "<prompt>" --output-format json`
- **Runs per scenario:** 3 runs per arm (3 baseline, 3 with-plugin) across all 6 scenarios (36 runs total).
- **Grading Protocol:** Evaluated per `shared/references/eval-protocol.md`:
  - Mechanism items (`skill X is loaded`) are excluded from baseline grading; they apply only to the with-plugin arm.
  - Outcome items only determine whether an arm passes or fails.
  - A scenario counts as an outcome gain only if the baseline failed at least one outcome item and the with-plugin arm passed.
  - If the baseline passed every outcome item, the scenario is recorded as "no outcome gain".
  - Efficiency (latency and token consumption) is tracked and reported separately as an informational metric, not as pass/fail.

---

## 1. Protocol and Setup

Each scenario was executed across two arms:
1. **Baseline Arm (`baseline`):** Clean isolated workspace without any stablehand customizations.
2. **With-Plugin Arm (`with_plugin`):** Workspace containing stablehand linked via directory junction or workspace plugin.

Raw execution records and per-run detail are preserved in `evals/results/`.

---

## 2. Results Summary

| Scenario ID | Kind | Baseline Outcome Pass Rate | With-Plugin Pass Rate | Outcome Gain? | Evaluation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `unrelated-request-no-trigger` | negative control | 3/3 PASS (0 skills loaded) | 3/3 PASS (0 skills loaded) | N/A (negative control) | **PASS** |
| `persona-agents-pushback` | behavior / prompt | 0/3 PASS (failed 3 outcome items) | 3/3 PASS (rejected roles, skills-first) | **YES** | **PASS** |
| `external-target-repo` | behavior / execution | inconclusive (baseline contaminated) | 3/3 PASS (conventions & notice) | — (inconclusive) | **inconclusive on Antigravity: unconfined baseline finds stablehand on the host** |
| `skill-for-migrations` | behavior / safety | 0/3 PASS (missing checkpoint & notice) | 3/3 PASS (checkpoint, safe, linted) | **YES** | **PASS** |
| `agents-md-minimal` | behavior / instructions | 0/3 PASS (invented `-m` parameter) | 3/3 PASS (facts only, concise) | **YES** | **PASS** |
| `port-reviewer-to-opencode` | behavior / porting | 0/3 PASS (regraded: shell key ignored, wildcard) | 2/3 PASS (bash + shell, exact rules) | **YES** | **PASS** |

**Decision:** Ship the Antigravity port (`✅ implemented (evals: 3 runs)`). Outcome gain in 4 of 4 conclusive behavior scenarios, with 0 false activations on the negative control.

### `port-reviewer-to-opencode` Regrade and Re-run

Under the corrected enforcement rule (OpenCode 1.19.3 requires `bash` and rejects trailing wildcards such as `"git diff*"` that admit `--output=<file>`):

| Arm / Run | Permission Key | Shell Pattern Exact? | Read-Only Enforced? | Lint A049 | Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Old baseline #1 | `shell` only | No (`"git diff*"`) | FAIL | Error (A049) | **FAIL** |
| Old baseline #2 | `shell` only | No (`"git diff*"`) | FAIL | Error (A049) | **FAIL** |
| Old baseline #3 | `shell` only | No (`"git diff*"`) | FAIL | Error (A049) | **FAIL** |
| Old with-plugin #1 | `shell` only | No (`"git diff*"`) | FAIL | Error (A049) | **FAIL** |
| Old with-plugin #2 | `shell` only | No (`"git diff*"`) | FAIL | Error (A049) | **FAIL** |
| Old with-plugin #3 | `shell` only | No (`"git diff*"`) | FAIL | Error (A049) | **FAIL** |
| New with-plugin #1 | `bash` + `shell` (identical) | No (`"git diff *"`) | FAIL | Clean (0 errors) | **FAIL** |
| New with-plugin #2 | `bash` + `shell` (identical) | Yes (`"git diff --staged"`, `"git diff --staged -- *"`) | PASS | Clean (0 errors) | **PASS** |
| New with-plugin #3 | `bash` + `shell` (identical) | Yes (`"git diff --staged"`, `"git diff --staged -- *"`) | PASS | Clean (0 errors) | **PASS** |

- **Verdict:** Baseline pass rate 0/3 (all failed read-only enforcement: `shell` key ignored, non-exact wildcard). Re-run with-plugin pass rate 2/3 (meets the ≥ 2/3 pass threshold per `eval-protocol.md`). **Outcome gain: YES**.

---

## 3. Efficiency Metrics

Efficiency metrics (runtime and token usage) are tracked separately and are not graded as pass/fail:

| Scenario ID | Baseline Avg Time | With-Plugin Avg Time | Time Delta | Baseline Avg Tokens | With-Plugin Avg Tokens | Token Delta |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `unrelated-request-no-trigger` | 2.73s | 2.77s | +0.04s (+1.6%) | 8,226 | 8,199 | -27 (-0.3%) |
| `persona-agents-pushback` | 35.74s | 60.94s | +25.20s (+70.5%) | 42,255 | 125,668 | +83,413 (+197.4%) |
| `external-target-repo` | — | 79.44s | — | — | 136,043 | — |
| `skill-for-migrations` | 110.43s | 88.87s | -21.56s (-19.5%) | 167,221 | 131,044 | -36,177 (-21.6%) |
| `agents-md-minimal` | 17.51s | 51.93s | +34.42s (+196.6%) | 38,409 | 98,229 | +59,820 (+155.7%) |
| `port-reviewer-to-opencode` | 571.01s | 285.01s | -286.00s (-50.1%) | 329,841 | 238,060 | -91,781 (-27.8%) |

*(Note: Baseline efficiency for `external-target-repo` is excluded because unconfined baseline runs escaped the scratch workspace and explored the host filesystem finding stablehand.)*

### Observations
- **Latency and token reductions in complex synthesis:** In `port-reviewer-to-opencode`, having the `porting-artifacts` skill eliminated unguided trial-and-error discovery of OpenCode schemas, reducing execution time by 50.1% and tokens by 27.8%. In `skill-for-migrations`, deterministic templates reduced execution time by 19.5% with 21.6% fewer tokens.
- **Architectural thoroughness:** In `persona-agents-pushback` and `agents-md-minimal`, the with-plugin arm used more tokens to analyze constraints and produce detailed, justified alternatives rather than superficial completions.
- **Negligible overhead on unrelated tasks:** On `unrelated-request-no-trigger`, duration and token consumption were virtually unchanged between arms (+0.04s, -27 tokens).

---

## 4. Caveats & Inconclusive Baseline

### Unconfined Baseline on Windows
`agy` on Windows does not enforce OS-level filesystem jail for command execution or drive path resolution. An unguided baseline model encountering an unfamiliar repository task will search parent directories, process tables, and user profile folders to locate reference implementations.

In `external-target-repo`, baseline runs left the temporary scratch workspace and read stablehand reference cards and skills directly from the host filesystem. Because the baseline arm could not be isolated from the reference artifacts, the scenario comparison is marked **inconclusive on Antigravity: unconfined baseline finds stablehand on the host** per `eval-protocol.md` and excluded from outcome gain calculations.

### OpenCode Permission Enforcement Key (bash vs shell)
OpenCode 1.19.3 enforces permissions only under `bash` and silently ignores `shell` (the key documented in OpenCode docs); valid read-only enforcement requires writing both `bash` and `shell` with identical exact rules and no trailing wildcards.

---

## 5. Verification 2026-10-23

Real end-to-end verification runs executed against `$env:TEMP\sh-ag-verify\demo-api` using the headless loader (`agy --dangerously-skip-permissions -p "<prompt>" --output-format json`):

| # | Prompt / Intent | Skill Loaded | Outcome & Artifacts | Status |
|---|---|---|---|---|
| 1 | Create read-only code review agent for `demo-api` reviewing staged changes against repo conventions | `authoring-agents` | Created `.agents/agents/code-reviewer.md` (read-only tools `view_file`, `grep_search`, `find_by_name`, `list_dir`), 3 benchmark scenarios, eval results in `.stablehand/evals/agents/code-reviewer/results/2026-10-23.md`. Linter: 0 errors/warnings. Reviewer: clean. Auto-delegation verified. | **PASS** |
| 2 | Add skill for `demo-api` adding a resource module the way the repo does it | `authoring-skills` | Created `.agents/skills/adding-resource-modules/SKILL.md` (dataclass in `src/demo_api/`, integer cents, test coverage). Evaluated against baseline (outcome gain on bloated dataclasses and dirty edits). Linter: 0 errors/warnings. Reviewer: clean. | **PASS** |
| 3 | Port `code-reviewer.md` to OpenCode | `porting-artifacts` | Created `.opencode/agents/code-reviewer.md` (`mode: subagent`, permission block with `edit: deny`, `shell: deny`, `webfetch: deny`, `websearch: deny`, `task: deny`), `.opencode/PORT-NOTES.md` documenting lossy items (name, tools, model, mainAgent/subagent) and untested prompt. Superseded: `shell` alone is not enforced on OpenCode 1.19.3 (lint A049 now flags it); see the `port-reviewer-to-opencode` re-run above. | **superseded** |

