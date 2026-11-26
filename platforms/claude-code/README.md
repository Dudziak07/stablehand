# stablehand for Claude Code

This is the reference implementation. It is a Claude Code plugin with 8 skills and 3 subagents, built against the contracts in [`contracts/`](../../contracts/).

## Use it from the stablehand repo (main flow)

```bash
uv run tools/install.py claude-code --scope workspace   # links this plugin into .claude/skills/stablehand
```

Open the stablehand folder in Claude Code (CLI or IDE) and accept the trust prompt. The skills load as `stablehand@skills-dir`; if the session was already open, run `/reload-plugins`. Give Claude access to the repository you are building for, with `/add-dir <path>` or `claude --add-dir <path>`, and ask: "I need a skill for <path> that …".

## Install globally (use it inside the target repo instead)

```bash
# from GitHub
claude plugin marketplace add Dudziak07/stablehand
claude plugin install stablehand@stablehand            # --scope project to share via the repo

# from a local checkout
claude plugin marketplace add /path/to/stablehand
claude plugin install stablehand@stablehand

# develop without installing
claude --plugin-dir /path/to/stablehand/platforms/claude-code
```

Inside a session, the same commands work as `/plugin marketplace add …` and `/plugin install …`.

## Use

| You say / type | What runs |
|---|---|
| "Set up agents and skills for this repo", `/stablehand:designing-agent-setups [path]` | Inventory → interview → approved blueprint → builds every row with the skills below |
| "Write a skill that …", `/stablehand:authoring-skills` | Test-first skill authoring |
| "Create a reviewer agent", `/stablehand:authoring-agents` | Justify → contract → agent file → benchmarks |
| "Trim our CLAUDE.md", `/stablehand:writing-project-instructions` | Minimal, verified instructions |
| "Port this agent to OpenCode", `/stablehand:porting-artifacts` | Platform-to-platform port + PORT-NOTES |
| "Test this skill", `/stablehand:evaluating-artifacts` | Baseline vs with-artifact runs, results file |
| "Lint this agent", `/stablehand:validating-artifacts` | Bundled linter, all three platforms |

The skills delegate to three agents: `stablehand:artifact-reviewer` (read-only review), `stablehand:scenario-runner` (isolated eval runs) and `stablehand:platform-researcher` (re-verifies platform formats on the web).

Requirements: [uv](https://docs.astral.sh/uv/) for the bundled linter (`uv run` installs PyYAML on the fly), and git for worktree-isolated eval runs.

## Layout

```
.claude-plugin/plugin.json
skills/<7 skills>/SKILL.md
skills/validating-artifacts/scripts/lint.py   generated from tools/lint.py
agents/<3 agents>.md
references/*.md                               generated from shared/references/
evals/<case>/prompt.md + graders/             claude plugin eval suite
```

Never edit the generated files. Edit the source, then run `uv run tools/sync.py` from the repo root.

## Evals

```bash
claude plugin eval platforms/claude-code --allow-tools Write Edit --scaffold
claude plugin eval platforms/claude-code --case persona-agents-pushback --runs 1   # one case, quick
```

`--scaffold` runs `external-target-repo/setup.sh`, which builds the fixture repository the case targets. It is a bash script that runs as you, outside the sandbox. Read it before you pass the flag.

The cases translate [`evals/scenarios/`](../../evals/scenarios/). Runs count against your plan's usage. Grant only `Write` and `Edit`: shell-granting cases need the OS sandbox, which native Windows lacks, so run those under WSL2.
