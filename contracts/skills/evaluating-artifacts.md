---
id: evaluating-artifacts
kind: skill
version: 2026.10.0
references: [targets.md, eval-protocol.md, "@platform"]
---
# evaluating-artifacts

## Purpose
Build and run evals for skills and agents: trigger tests, behavior scenarios and agent benchmarks. Each is compared against a run without the artifact, and the results are recorded so the decision is evidence-based and repeatable.

## Triggers
- **Should:**
  - "test/benchmark this skill";
  - "does my agent actually help";
  - "check if the skill triggers";
  - "compare v1 and v2 of this skill";
  - when another stablehand skill reaches its test step.
- **Should not:**
  - running the project's own unit tests;
  - static format checks (that is `validating-artifacts`).

## Inputs
- The artifact path.
- Existing eval files, if any.
- The model or models to test with.
- A run budget.

## Procedure
0. **Target.** All runs happen in the target repository (`targets.md`). Run only artifacts for the host platform. For other platforms, produce the hand-off prompt.
1. **Locate or create the eval set** under `<target>/.stablehand/evals/…`, following `eval-protocol.md`.
2. **Plan the runs:**
   - which scenarios;
   - how many runs (1 to explore, 3 to decide);
   - which runner.

   If the plan exceeds about 10 runs, show the count before starting.
3. **Baseline.** Run without the artifact. A behavior run uses the isolated scenario-runner agent; a trigger or delegation run uses the real loader.
4. **With artifact.** Run the same scenarios with the artifact.
5. **Grade.** Apply the deterministic checks first, then the judge rubric. Use the reviewer agent as judge when independence matters.
6. **Record.** Save `results/<date>.md`: the table, the exact commands, the model, and the decision (ship, iterate or drop).

## Outputs
- The eval files.
- The results file.
- A one-paragraph verdict.

## Done when
- Each planned run has completed, or its failure is explained.
- The results file is written with the commands and model.
- A decision is stated against the decision rule.

## Must not
- Grade the artifact by reading it instead of running it.
- Change the artifact and the scenarios in the same iteration.
- Run large batches without telling the user the count.

## Platform adaptation
Each platform maps the runner table in `eval-protocol.md` to its own commands:
- the agent invocation for the scenario-runner;
- the headless loader command and the fields to search in its output;
- the packaged suite runner, if any (Claude `claude plugin eval`).

## Evals
Covered indirectly by `skill-for-migrations` (via its test step).
