# Shared evals

The evals in this folder test **stablehand itself**. They are written once, platform-neutral, and every platform implementation translates them into its own runner. That way "same behavior on every platform" is something you can measure, not just something you claim.

- `triggers.yaml`: should and should-not prompts for each stablehand skill.
- `scenarios/*.md`: behavior scenarios in the format described in `shared/references/eval-protocol.md`.

## Translations per platform

| Platform | Where | Run |
|---|---|---|
| Claude Code | `platforms/claude-code/evals/<case>/` (`claude plugin eval` format) | `claude plugin eval platforms/claude-code --allow-tools Write Edit --scaffold` |
| Antigravity | [`platforms/antigravity/evals/`](../platforms/antigravity/evals/), results in `RESULTS.md` | `agy -p` runs + `scenario-runner` |
| OpenCode | [`platforms/opencode/evals/`](../platforms/opencode/evals/), results in `RESULTS.md` | `opencode run --format json` runs + `scenario-runner` |

When you change a scenario here, update every translation in the same change.

## Scenario index

| Scenario | Targets | What it proves |
|---|---|---|
| [persona-agents-pushback](scenarios/persona-agents-pushback.md) | designing-agent-setups, authoring-agents | Role agents are challenged and replaced by a justified design |
| [skill-for-migrations](scenarios/skill-for-migrations.md) | authoring-skills, validating-artifacts | A side-effecting skill is user-invoked, has its checkpoint before the first side effect, and is valid |
| [port-reviewer-to-opencode](scenarios/port-reviewer-to-opencode.md) | porting-artifacts | A Claude agent becomes an idiomatic OpenCode agent and stays read-only |
| [unrelated-request-no-trigger](scenarios/unrelated-request-no-trigger.md) | all skills | stablehand stays out of ordinary coding work |
| [agents-md-minimal](scenarios/agents-md-minimal.md) | writing-project-instructions | Instructions contain only non-inferable facts and verified commands |
| [external-target-repo](scenarios/external-target-repo.md) | authoring-skills | The main flow: a skill requested for another repo lands in that repo and encodes its real conventions |
