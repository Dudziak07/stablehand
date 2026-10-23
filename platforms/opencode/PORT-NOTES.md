# PORT-NOTES — stablehand for OpenCode

- **Date:** 2026-10-21
- **OpenCode version:** 1.19.3 (Windows; PowerShell 5.1)
- **Model used:** `deepseek/deepseek-flash` (DeepSeek V4.1 Flash) for the live evals
- **Source:** `contracts/` at 2026.10.0; reference implementation `platforms/claude-code/`

## What was built

Seven skills under `skills/<id>/SKILL.md` and four agents under `agents/<id>.md`: three per contract, plus the read-only `trigger-probe` used by real-loader tests. References are per-skill copies produced by `tools/sync.py` (`references/<file>.md`), plus the vendored linter at `skills/validating-artifacts/scripts/lint.py`. Evals are translated one file per scenario under `evals/`, with the run summary in `evals/RESULTS.md`.

## Mapping decisions

- **Skills.** Frontmatter is only `name`, `description` and `metadata`. Every skill sets `metadata.opencode/slash: "true"`, so it is available as `/name`. Authoring skills keep the default auto-invocation (no `opencode/autoinvoke: "false"`), matching the Claude reference, which does not disable model invocation for them; the generated *user* skill in `skill-for-migrations` still uses `opencode/autoinvoke: "false"`.
- **References.** OpenCode has no plugin-root variable, so each skill links its generated files as `references/<file>.md` relative to the skill folder (per-skill sync mode). No `${CLAUDE_*}` variables remain.
- **Validator.** The linter is vendored at `skills/validating-artifacts/scripts/lint.py`. Other skills delegate to the `validating-artifacts` skill instead of hard-coding a path across skills, because the install location differs between workspace, user and project scope. The `validating-artifacts` skill states that the linter is `scripts/lint.py` in its own folder.
- **Skill to skill.** "Call the skill tool with name `<id>`", per the platform card.
- **Delegation.** "Use the task tool with the agent `<id>`" (or `@<id>`).
- **Real loader.** Trigger and delegation probes run against a scratch copy of the target with the bundled read-only `trigger-probe` agent, so a should-trigger prompt cannot write:
  `opencode run "<prompt>" --format json --dir "<scratch>" --agent trigger-probe --model deepseek/deepseek-flash`
  Look for a `skill` call (trigger) or a `task` call (delegation). Work that must write (the external-authoring flow) runs from the stablehand checkout with the scratch target's absolute path in the prompt and `--auto` to approve `external_directory`:
  `opencode run "<prompt>" --format json --dir "<stablehand>" --model deepseek/deepseek-flash --auto`
  Then verify `git -C "<stablehand>" status --porcelain` is empty. The exact commands and outputs are in `evals/RESULTS.md`.
- **Target access and commands.** Approve the `external_directory` prompt. For `opencode run`, pass `--dir "<target-or-scratch>"`. For every other command that runs the target's code, use `cd "<target>" && <command>`; do not pass `--project "<target>"` to `uv run` from the stablehand folder.
- **Agents.** No `name` key (the file name is the name) and no deprecated `tools` key; `mode: subagent` plus `permission`.
  - `artifact-reviewer`: `edit`, `shell`, `webfetch`, `websearch` and `task` all `deny`; `read`, `glob`, `grep` stay at the default, so it is read-only. No model (inherits).
  - `platform-researcher`: `edit`, `shell` and `task` `deny`, `webfetch` and `websearch` `allow`; `model: deepseek/deepseek-flash`.
  - `scenario-runner`: default permissions, no model (inherits).
  - `trigger-probe`: `edit` and `shell` `deny`, `task` and `skill` `allow`; `mode: primary`, no model. Used for real-loader trigger and delegation runs against a scratch copy. It has no contract; it exists only to make those runs safe.

## Lossy items

- **`argument-hint`** (Claude skill field) has no OpenCode skill equivalent. Dropped; the user invokes `/name` and states the target in the prompt.
- **`allowed-tools`** (the Claude `validating-artifacts` pre-approves `Bash(uv run *)`) has no per-skill equivalent. Dropped; OpenCode controls tool access with `permission` in `opencode.json` or an agent's frontmatter, not on a skill. The exact `uv run` command is still printed, and the shell permission may prompt once.
- **Agent fields with no direct equivalent:** `color`, `permissionMode`, `isolation: worktree`, `maxTurns`, `skills` (preload) and `mcpServers` are dropped or re-expressed:
  - `tools` became `permission` (the `tools` key is deprecated in OpenCode).
  - Scenario isolation stays the caller's job (a git worktree or scratch copy of the target), as the contract already requires.
  - Preloaded skills are not a frontmatter feature; the agent body tells it to call the skill tool by name.
- **Model tier `inherit`** is expressed by omitting `model`, because subagents inherit the invoking primary's model.
- **`porting-artifacts` names source-platform tools** by design, to describe the mapping. It carries `<!-- stablehand-lint: ignore S024 -->` like the reference; the suppressed findings are the source and Antigravity tool names in the mapping table, which cannot be removed without losing the mapping.

## Untested behaviour

- **Eval runs.** The scenarios specify `runs: 3`; the evals were run 3 times per arm and graded with the decision rule. See `evals/RESULTS.md`.
- **`/name` in the TUI.** `metadata.opencode/slash: "true"` was not exercised headlessly; only model-triggered loads were.
- **`external_directory` interactive approval.** The external-authoring run used `--auto` (on a scratch target, with the stablehand checkout verified clean); the interactive prompt itself was not tested.
- **Auto-delegation of the agents.** Only explicit task-tool delegation was exercised (the external eval delegated to `artifact-reviewer`). Natural-prompt delegation was not benchmarked.
- **Vendored linter path outside the workspace.** The validator path was verified with the workspace and project installs; a user-scope install resolves the same way but was not run.
- **Windows host caveat.** OpenCode 1.19.3's `skill` tool fails on this machine unless `PSExecutionPolicyPreference=Bypass` is set, because it invokes `Expand-Archive` and the machine's execution policy blocks the Archive module. This is an environment issue, not a port issue; it does not affect hosts with a permissive policy. The evals set it.

## Card corrections

- **`bash` vs `shell` (2026-10-23).** OpenCode 1.19.3 enforces only the `bash` permission key and silently ignores `shell`, although the docs name `shell`. Reproduced with `shell: {"*": deny}` still running `git diff --output=x.txt`, while `bash: {"*": deny}` blocked it. The card now documents both keys; the shipped agents and the permission examples in these skills write both with identical rules. The linter rule A049 checks for the pair.

No other errors found. I checked `shared/references/opencode.md` against `tools/lint.py` and the live tool. These all matched: skill keys (`name`, `description`, `license`, `compatibility`, `metadata`); `metadata.opencode/*` as string `"true"`/`"false"`; agent name from the file name with no `name` key; the `mode` enum; `permission` keys with `allow`/`ask`/`deny`; `model` as `provider/model-id`; `steps` replacing `maxSteps`; and the `opencode run --format json` loader.

One non-error observation: the card allows descriptions of 1–1024 characters, while the repo's writing guide aims for 500 or fewer. The linter encodes both limits (error above 1024, info above 500). Every skill description in this port stays under 500 characters.
