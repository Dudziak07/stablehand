---
name: evaluating-artifacts
description: "Builds and runs evaluations for a repository's Antigravity skills and subagents: trigger sets, behavior scenarios and agent benchmarks, compared against a baseline without the artifact. Use when asked to test, benchmark, evaluate or compare versions of a skill or agent in a repository. Not for running project unit tests or static format validation."
---

Judge an artifact by what an execution run demonstrates, never merely by reading it. Every result must be repeatable from recorded commands.

Reference material:
- `references/eval-protocol.md`: file formats, evaluation loop, and decision rules.
- `references/targets.md`: target repository access and constraints.
- `references/antigravity.md`: Antigravity headless execution commands and runner options.

## Process

0. **Target.** All runs occur in the repository owning the artifact (the target), never in stablehand.
   - Read and write in the target repository using absolute paths or by adding it to the workspace.
   - **Access & Workspace.** `run_command` in Antigravity requires `Cwd` to be within the active workspace. When running commands in the target repository or in its worktree/scratch copy, ensure the target folder or scratch directory is added to the workspace (multi-root workspace in Antigravity IDE).
   - Artifacts for Claude Code or OpenCode cannot be executed locally. Write the eval files and hand off a prompt for that platform.
   - **Confirmation.** Confirm in one line: `Target: <path> · Platform: <platform> · Evaluating: <artifact>`.

1. **Locate or create the eval set** in `<target>/.stablehand/evals/skills/<name>/` or `<target>/.stablehand/evals/agents/<name>/`:
   - skills: `triggers.yaml` and `scenarios/*.md`
   - agents: benchmark scenarios
   Write missing files following `references/eval-protocol.md` before executing.

2. **Plan the runs.** Select scenarios, run counts (1 to explore, 3 for a ship decision), and model tiers (`inherit`, `flash`, `pro`). If planning more than ~10 runs, confirm with the user first.

3. **Behavior runs (in-session).** For each scenario, run both arms using `invoke_subagent` with `scenario-runner`:
   - **baseline arm:** mode `baseline` (the named artifact is ignored);
   - **with-artifact arm:** mode `with-artifact`, passing the artifact path.

   Assign `scenario-runner` a working directory that is a git worktree (`git -C <target> worktree add <scratch> HEAD`) or scratch copy of the target repository. Ensure the scratch directory is accessible within the workspace. Never run in the target checkout directly, and never in stablehand. Clean up the worktree or scratch copy afterwards.

4. **Real-loader runs (triggers and delegation).** Execute a two-arm protocol inside a scratch copy or git worktree of the target repository (never the live target checkout or stablehand):
   - **baseline arm:** Run `agy -p "<prompt>" --output-format json` in a clean scratch copy or worktree without the linked plugin/skill (or with the plugin excluded). Verify that the skill does NOT trigger.
   - **with-artifact arm:** Run `agy -p "<prompt>" --output-format json` in the scratch copy or worktree with the plugin or skill linked. Inspect the JSON output to verify skill activation or subagent delegation for positive triggers, and absence of activation for negative triggers.
   Clean up the scratch copy or worktree afterwards. If a batch is interrupted, resume from the first missing run without repeating completed runs.

5. **Grade.** Apply deterministic checks first (files exist, regex matches, commands exit 0), then the evaluation rubric. Run static format validation using the validator: determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from the directory containing this `SKILL.md` (or invoke `/stablehand:validating-artifacts`). When independent judgment is required, delegate grading to `artifact-reviewer` using `invoke_subagent`.

6. **Record** `results/<YYYY-MM-DD>.md`:
   - table: scenario/trigger, baseline result, with-artifact result, notes;
   - exact commands and models used;
   - decision (ship, iterate, or drop) based on the decision rule in `references/eval-protocol.md`;
   - a one-paragraph verdict for the user: what the artifact changes, where it falls short, and what to do next.

## Must not
- Change the artifact and the scenarios in the same iteration.
- Run anything in the live target checkout itself or in stablehand.
- Report a run you did not execute.
- Grade the artifact by reading it instead of running it.

## Done when
- [ ] Target confirmation was printed before executing runs
- [ ] Every planned run completed (baseline and with-artifact arms), or failure is explained
- [ ] The results file contains the table, commands, model, decision, and verdict
- [ ] The decision adheres to the decision rule in `references/eval-protocol.md`
