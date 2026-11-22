---
name: evaluating-artifacts
description: "Builds and runs evals for a repository's OpenCode skills and subagents: trigger tests, behavior scenarios and agent benchmarks, compared against a run without the artifact. It records a ship/iterate/drop decision. Use when asked to test, benchmark, compare versions of, or check triggering of a skill or agent in this or another repo. Not for running the project's own test suite or for format checks."
metadata:
  opencode/slash: "true"
---

Judge an artifact by what a run shows, never by reading it. Every result must be repeatable from the commands you record. Write all output in English.

Reference material:
- `references/eval-protocol.md`: file formats, the loop, the decision rule, and the OpenCode runner row.
- `references/targets.md`: the target repo and access to it.
- `references/opencode.md`, sections 2 and 7: the skill tool call and the headless `opencode run` command.

## Process

0. **Target.** All runs happen in the repository that owns the artifact (the target), not in stablehand.
   - Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.
   - If the target is outside the workspace, approve the `external_directory` prompt.
   - Commands: for `opencode run`, run it from "<target-or-scratch>" (it has no `--dir` flag). For every other command that runs the target's code, use `cd "<target>" && <command>`; do not pass `--project "<target>"` to `uv run` from the stablehand folder.
   - Artifacts for Claude Code or Antigravity cannot be run from here. Write the eval files, then give a ready-to-paste prompt that runs them on that platform.

1. **Locate or create the eval set** in `<target>/.stablehand/evals/skills/<name>/` or `<target>/.stablehand/evals/agents/<name>/`:
   - skills: `triggers.yaml` and `scenarios/*.md`;
   - agents: benchmark scenarios.

   Write missing files in the protocol's format before running anything.

2. **Plan the runs.** Decide which scenarios, how many runs (1 to explore, 3 to decide), and which models. Use `--model deepseek/deepseek-flash` for a cheap pass and `--model deepseek/deepseek-v4-pro` for a stronger one. If the plan exceeds about 10 runs, show the count and get a go-ahead.

3. **Behavior runs (isolated, through the runner agent).** For each scenario, run both arms with the subagent tool and the agent `scenario-runner`:
   - baseline arm: mode `baseline`;
   - with-artifact arm: mode `with-artifact`, plus the artifact path.

   Give the runner a working directory that is a git worktree of the target (`git -C "<target>" worktree add "<scratch>" HEAD`) or a scratch copy. If `git -C "<target>" status --porcelain` is non-empty, use a scratch copy instead of a worktree. Never the target checkout, and never stablehand. Keep the scratch for step 4; remove it afterwards.

4. **Real-loader runs (triggers and delegation).** Run each prompt against the scratch copy of the target, never the target checkout, with the bundled read-only probe.
   - Install the artifact under test into the scratch: copy a skill to `<scratch>/.opencode/skills/<name>/` or an agent file to `<scratch>/.opencode/agents/<name>.md`.
   - Install the probe: copy `trigger-probe.md` into `<scratch>/.opencode/agents/`. Take it from the `agents/` folder beside the installed `skills/` folder (for a workspace install: `<stablehand>/.opencode/agents/trigger-probe.md`; in the checkout: `platforms/opencode/agents/trigger-probe.md`). Without this copy OpenCode cannot find the agent when `opencode run` starts in "<scratch>".
   - Run each prompt:
     `opencode run "<prompt>" --format json --agent trigger-probe --model deepseek/deepseek-flash`
   - For a skill, a pass is a `skill` call whose id is the skill.
   - For an agent, a pass is a `subagent` call that selects the agent.
   - If a batch is interrupted (for example by a usage limit), continue from the first missing run and do not redo completed ones.

5. **Grade.** Apply the deterministic checks first (files, regexes, commands), then the judge rubric. When independence matters, use the subagent tool with the agent `artifact-reviewer` as the judge, passing the transcripts and the rubric.

6. **Record** `results/<YYYY-MM-DD>.md`:
   - the table: scenario or trigger, baseline, with artifact, notes;
   - the exact commands and the model;
   - the decision (ship, iterate or drop) against the decision rule.

## Must not
- Change the artifact and the scenarios in the same iteration; change one and re-run.
- Grade the artifact by reading it instead of running it.
- Run large batches without telling the user the count.

## Done when
- [ ] Every planned run completed, or its failure is explained
- [ ] The results file has the table, commands, model and decision
- [ ] The decision follows the rule in `references/eval-protocol.md`
