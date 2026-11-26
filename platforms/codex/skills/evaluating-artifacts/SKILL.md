---
name: "evaluating-artifacts"
description: "Builds and runs trigger tests, behavior scenarios, and agent benchmarks against a baseline without the artifact, recording results in .stablehand/evals/. Use when testing whether a skill or agent helps, checking triggers, or comparing versions. Not for running a project's unit tests or static linting."
---

An artifact is done when a run proves it changes behavior, not when it reads well. Write all output in English.

Reference material (in this skill's folder):
- `references/targets.md`: establishing the target repository and access to it.
- `references/eval-protocol.md`: scenario/trigger formats, decision rule, and reporting.
- `references/codex.md`: headless runner (`codex exec`) and sandbox options.

## Process

0. **Target.** All runs happen in a scratch copy or git worktree of the target repository (`references/targets.md`), never in the live checkout or in `stablehand`. Run artifacts only for the host platform (Codex); for other platforms, hand off the test prompt instead.
1. **Locate or create the eval set** under `<target>/.stablehand/evals/…` following `references/eval-protocol.md`.
2. **Plan the runs:** choose scenarios, run count (1 to explore, 3 to decide), and runner. If the plan exceeds ~10 runs, show the count to the user before starting.
3. **Baseline.** Run without the artifact:
   - behavior scenario: spawn `scenario-runner` in mode `baseline` against `<scratch>`.
   - trigger / real-loader check: run `codex exec --ephemeral --json --sandbox read-only -C "<scratch>" "<prompt>"` (on Windows use `codex.cmd`).
4. **With artifact.** Run the same scenarios with the artifact installed in `<scratch>` (mode `with-artifact` for `scenario-runner`, or `codex exec` for triggers).
5. **Grade.** Apply deterministic checks first, then the rubric. Spawn `artifact-reviewer` when an independent judge is needed.
6. **Record.** Save `results/<date>.md` with the comparison table, exact commands, model, and verdict (`ship`, `iterate`, or `drop`).

## Done when
- [ ] Every planned run completed or its failure is explained
- [ ] `results/<date>.md` records commands, model, and verdict against the decision rule
