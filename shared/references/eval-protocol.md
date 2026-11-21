# Eval protocol for skills and agents

An artifact is done when a run shows it changes behavior for the better. Parsing cleanly or reading well does not count. This protocol is platform-neutral; the last section maps it to each platform's runner.

## Where evals live

In the target repository, the one that owns the artifact. Never in stablehand (see `targets.md`):

```
.stablehand/evals/
├── skills/<skill-name>/
│   ├── triggers.yaml
│   ├── scenarios/<id>.md
│   └── results/<YYYY-MM-DD>.md
└── agents/<agent-name>/
    ├── scenarios/<id>.md        # benchmark tasks
    └── results/<YYYY-MM-DD>.md
```

Never put eval files inside `.claude/agents/`: that folder is scanned recursively and loose `.md` files can be loaded as agents.

## triggers.yaml (skills)

```yaml
skill: writing-tests
should_trigger:          # 5–8 realistic phrasings, including indirect ones
  - "add tests for the invoice parser"
  - "this function has no coverage, fix that"
should_not_trigger:      # 5–8 near misses that share vocabulary
  - "run the test suite"
  - "why is this test flaky in CI?"
```

## scenarios/<id>.md

```markdown
---
id: parser-edge-cases
kind: behavior            # behavior (skills) | benchmark (agents)
runs: 3                   # 1 while exploring, 3 for a ship decision
---
## Prompt
<exactly what the user would type>

## Setup
<files or state the run needs; "none" if the prompt is self-contained>

## Expected (all must hold)
- <observable outcome 1>
- <observable outcome 2>

## Must not
- <observable failure>

## Checks
- deterministic: <file exists / regex on file / command exits 0>
- judge: PASS if <…>. FAIL if <…>.
```

Write outcomes that an observer can check without reading the model's mind: files, commands run, text in the final answer.

## The loop

1. **Baseline (RED).** Run every scenario *without* the artifact. Record what happened verbatim, especially the agent's own justifications for skipping steps. If the baseline already passes, the artifact is unnecessary; stop or narrow it.
2. **Draft** the smallest artifact that addresses the recorded failures.
3. **Re-test (GREEN).** Run the same scenarios *with* the artifact. Run the trigger set (skills) or the delegation prompts (agents).
4. **Iterate** at most 3 times. Each iteration changes one thing and re-runs only the affected scenarios.
5. **Record** the results file and the decision.

## Decision rule

| Check | Ship when |
|---|---|
| Behavior scenarios | every Expected item holds in ≥ 2 of 3 runs with the artifact, and the baseline failed at least one **outcome** item |
| should_trigger | ≥ 4 of 5 (or 80%) fire |
| should_not_trigger | none fire |
| Agent benchmarks | every task meets its expected output in ≥ 2 of 3 runs |

**Grading the baseline:**
- **Ignore mechanism items.** An item such as "skill X is loaded" or "agent X is delegated to" always fails without the artifact, so it proves nothing. It still counts for the with-artifact arm.
- **Use outcome items.** Only items about the result count for the comparison: files, commands, content, safety and boundaries.
- **If the baseline passes every outcome item**, the artifact adds no quality for that scenario. Say so ("no outcome gain"). Don't count the scenario as evidence for shipping.
- **Report efficiency separately.** Record time and tokens per arm. Gains there are worth reporting, but they are not pass/fail criteria unless the scenario sets an explicit limit.
- **Use only the scenario's items.** Never add criteria or penalties that are not in the scenario.
- **If the baseline could reach the artifact, the comparison is void.** Report the scenario as "inconclusive", not as "no outcome gain", and leave it out of the counts (see "Confine the baseline" below).

If a check fails after 3 iterations, ship only with the user's explicit consent and list the gap in the results file.

## results/<date>.md

```markdown
# <artifact> — <date> — platform <p> — model <m>
| Scenario / trigger | Baseline | With artifact | Notes |
|---|---|---|---|
Decision: ship | iterate | drop — <one line why>
```

## Runners per platform

Runs cost model usage. Before starting more than ~10 runs, tell the user how many will run.

| Purpose | Claude Code | Antigravity | OpenCode |
|---|---|---|---|
| Behavior run (fast) | `scenario-runner` subagent via the Agent tool | `scenario-runner` custom agent via `invoke_subagent` (App/CLI) | `scenario-runner` subagent via the Task tool / `@scenario-runner` |
| Real-loader run (triggers, delegation) | `cd "<target>" && claude -p "<prompt>" --output-format stream-json --verbose --max-turns 3`; look for a `Skill` call with the name, or an `Agent` call with that `subagent_type` | `agy -p "<prompt>" --output-format stream-json`, started in the target; look in NDJSON `step_update` events for `tool_name` / `tool_info` (skill file reads) and `subagent_info.subagents[].type_name` (delegation); pass `--model <slug>` and pin `--mode` (`v1.5.7+` defaults to `auto` where sandbox is available) | `opencode run "<prompt>" --format json --dir "<target>"`; look for a `skill` call with the name, or a `task` call |
| Packaged suite | `claude plugin eval <plugin-dir> --allow-tools Write Edit` (WITH vs WITHOUT delta; shell grants need WSL2 on Windows) | — | — |
| Model under test | `--model` / `ANTHROPIC_MODEL`; DeepSeek profile via env | `model:` in the runner agent, or `--model <slug>` / `--effort` in `agy -p` | `--model deepseek/deepseek-flash` |

**Isolation for behavior runs.** Give the runner a git worktree of the **target** repo (`git -C "<target>" worktree add "<scratch>" HEAD`) or a scratch copy, and remove it afterwards (`git -C "<target>" worktree remove "<scratch>"`).
- Built-in isolation options, such as Claude's `isolation: "worktree"`, create a worktree of the *current* repository. When you work from stablehand, that is the wrong repository.
- A worktree contains only **committed** files. If the code the scenario needs is untracked or uncommitted (common in student and prototype repos), use a scratch **copy** instead. Leave out `.venv`, databases and large assets.
- If you want a clean diff of what the run changed, run `git init` plus a baseline commit inside the scratch copy. That copy is throwaway; never commit in the target repo.

**Confine the baseline.** A baseline must not be able to reach the artifact under test, or anything that contains it. An agent with unrestricted file access will look for examples on its own. In the stablehand evals, baselines found stablehand by:
- reading `platforms/*/skills/` in a stablehand clone used as the working directory;
- leaving the scratch folder and listing parent folders, the user's home and other tools' session history (for example `~/.claude/projects/`), then opening the repository they found.

So:
- Never run the baseline inside a stablehand checkout or clone, or below a folder that holds runner scripts or other runs. Use an empty scratch folder (`git init`) and pass outside targets by absolute path.
- Use the platform's strictest confinement that still lets the run finish: workspace-only file access, no blanket permission skip. Prefer a disposable VM, container or separate OS user when the platform has no such option.
- After every baseline run, scan its log for paths outside the scratch folder. A run that read stablehand, the artifact, or another run's output does not count. Re-run it once confined. If that is impossible, mark the scenario "inconclusive on <platform>" and say why.

**Make batches resumable.** Runs can stop part-way, for example on a usage limit. Write each run's result to the results file as soon as it finishes, then continue from the first missing run. Don't redo completed ones.

Record the exact command and model in every results file, so the run can be repeated.
