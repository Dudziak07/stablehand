# Contracts

A contract states **what** a stablehand skill or agent must do. Each platform folder decides **how**: field names, tool names, invocation syntax and file paths differ per platform, but the behavior must not.

## Rules

1. **Behavior changes start here.** Edit the contract and set its `version` to the next stablehand release (see Versioning below). Then update every platform implementation. A platform that hasn't caught up shows the older version in `platforms/README.md`.
2. **Write implementations against the contract, not against another platform's implementation.** The Claude Code folder is the reference port. It is not the specification.
3. **Every contract names the eval scenarios that prove it.** Scenarios live in `evals/scenarios/`.
4. **Contracts are platform-neutral.** Write "load the skill", "delegate to the reviewer agent", "run the validator". Never write `Skill tool`, `invoke_subagent` or `skill({...})`; those belong in implementations.
5. **Artifacts go to a target repository.** stablehand is normally opened in its own repository, and the user names the repo the artifacts are for. Every authoring contract starts by establishing the target repo, access to it, and the target platform (`shared/references/targets.md`), and never writes into stablehand itself.

## Format

```markdown
---
id: <name, equal to the implementation folder/file name>
kind: skill | agent
version: <YYYY.M.N: the release that last changed this contract>
references: [<files from shared/references/>, "@platform" for the host platform card, "@all-platforms" for every card]
---
# <id>
## Purpose
## Triggers            (skills: should / should-not; agents: when the main agent delegates)
## Inputs
## Procedure           (neutral, numbered)
## Outputs
## Done when
## Must not
## Platform adaptation (what each implementation must map)
## Evals               (scenario ids)
```

## Versioning

stablehand uses one calendar version, `YYYY.M.N`, for the whole repository: contracts, the Claude plugin and the Antigravity plugin. The marketplace entry carries no version, because Claude Code reads it from `plugin.json` first.
- `YYYY.M` is the year and month of the release; the month has no leading zero (`2026.9.0`, not `2026.09.0`), so the version is also valid SemVer.
- `N` counts releases within that month, starting at 0.
- A contract's `version` is the release that last changed it. The plugin manifests carry the current release, which is never older than the newest contract. `tools/tests` checks both.
- The version says when a release was made, not how current the platform knowledge is. Each platform card in `shared/references/` has its own `Last verified: YYYY-MM-DD` line. `uv run tools/lint.py --cards shared/references` warns when a card is older than 90 days.

`references` drives `tools/sync.py`. In per-skill mode, it copies exactly these files into `skills/<id>/references/`.

## Index

| Contract | Kind | Role |
|---|---|---|
| [designing-agent-setups](skills/designing-agent-setups.md) | skill | Entry point: inventories a project, interviews the user, produces an approved blueprint, then builds it in order |
| [authoring-skills](skills/authoring-skills.md) | skill | Test-first creation or improvement of one skill |
| [authoring-agents](skills/authoring-agents.md) | skill | Justify, specify, write and test one subagent |
| [writing-project-instructions](skills/writing-project-instructions.md) | skill | Minimal always-loaded instructions and rules |
| [porting-artifacts](skills/porting-artifacts.md) | skill | Move a skill/agent/instruction file to another platform without changing behavior |
| [evaluating-artifacts](skills/evaluating-artifacts.md) | skill | Build and run trigger tests and behavior scenarios against a baseline |
| [validating-artifacts](skills/validating-artifacts.md) | skill | Static checks with the bundled linter, including cross-platform collisions |
| [artifact-reviewer](agents/artifact-reviewer.md) | agent | Independent read-only review of one artifact |
| [scenario-runner](agents/scenario-runner.md) | agent | Executes one eval scenario in isolation and reports verbatim |
| [platform-researcher](agents/platform-researcher.md) | agent | Re-verifies platform formats against official sources |
