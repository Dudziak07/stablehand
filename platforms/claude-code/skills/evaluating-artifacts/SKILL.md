---
name: evaluating-artifacts
description: "Builds and runs evals for a repository's Claude Code skills and subagents: trigger tests, behavior scenarios and agent benchmarks, compared against a run without the artifact. It records a ship/iterate/drop decision. Use when asked to test, benchmark, compare versions of, or check triggering of a skill or agent in this or another repo. Not for running the project's own test suite or for format checks."
argument-hint: "[artifact path in the target repo]"
---

Judge an artifact by what a run shows, never by reading it. Every result must be repeatable from the commands you record.

Reference material:
- `${CLAUDE_PLUGIN_ROOT}/references/eval-protocol.md`: file formats, the loop, the decision rule.
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: the target repo.
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`, section 7.

## Process

0. **Target.** All runs happen in the repository that owns the artifact (the target), not in stablehand.
   - If the target is outside the working directory, ask the user to run `/add-dir <path>`.
   - Artifacts for Antigravity or OpenCode cannot be run from here. Write the eval files, then give a ready-to-paste prompt that runs them on that platform.
   - **Confirm** in one line: `Target: <path> · Platform: <platform> · Evaluating: <artifact>`.

1. **Locate or create the eval set** in `<target>/.stablehand/evals/skills/<name>/` or `<target>/.stablehand/evals/agents/<name>/`:
   - skills: `triggers.yaml` and `scenarios/*.md`;
   - agents: benchmark scenarios.

   Write missing files in the protocol's format before running anything.

2. **Plan the runs.** Decide which scenarios, how many runs (1 to explore, 3 to decide), and which models. Use `--model` / `ANTHROPIC_MODEL`; for a DeepSeek profile, use the user's launcher. If the plan exceeds ~10 runs, show the count and get a go-ahead.

3. **Behavior runs (fast, in-session).** For each scenario, run both arms with the Agent tool and `subagent_type: "stablehand:scenario-runner"`:
   - **baseline arm:** mode `baseline`;
   - **with-artifact arm:** mode `with-artifact`, plus the artifact path.

   Give the runner a working directory that is a git worktree of the target (`git -C <target> worktree add <scratch> HEAD`) or a scratch copy. Never the target checkout, and never stablehand. Remove the worktree afterwards.

4. **Real-loader runs (triggers and delegation).** Run the bundled script against the target repo. It runs each prompt with `claude -p`, with edit tools disallowed, and checks for a `Skill` call naming the skill, or an `Agent` call naming the agent:
   `uv run "${CLAUDE_SKILL_DIR}/scripts/run_triggers.py" --repo "<target>" --triggers <triggers.yaml> --skill <name> --out <results.json>`
   - For agents, use `--agent <name> --should "<natural prompt>" --should-not "<prompt>"`.
   - If `claude` is not on PATH, add `--claude <path>`.
   - If a batch is interrupted (for example by a usage limit), re-run it with `--resume`.

   The script exits 0 only when every prompt behaved as expected.

5. **Packaged artifacts.** If the artifacts ship as a plugin, prefer the official runner. It reports a WITH vs WITHOUT delta per case:
   `claude plugin eval <plugin-dir> --allow-tools Write Edit`
   On native Windows, cases that need Bash or PowerShell must run in WSL2: there is no sandbox backend on Windows.

6. **Grade.** Apply the deterministic checks first (files, regexes, commands), then the judge rubric. When independence matters, delegate grading to `stablehand:artifact-reviewer` with the transcripts and the rubric.

7. **Record** `results/<YYYY-MM-DD>.md`:
   - the table: scenario/trigger, baseline, with artifact, notes;
   - the exact commands and the model;
   - the decision (ship, iterate or drop) against the decision rule;
   - a one-paragraph verdict for the user: what the artifact changes, where it falls short, and what to do next.

## Must not
- Change the artifact and the scenarios in the same iteration.
- Run anything in the target checkout itself or in stablehand.
- Report a run you did not execute.

## Done when
- [ ] Every planned run completed, or its failure is explained
- [ ] The results file has the table, commands, model and decision
- [ ] The decision follows the rule in `eval-protocol.md`
