# Platform card: Claude Code

Last verified: 2026-10-21 against Claude Code 2.1.306. Formats change often. When a detail matters and may be stale, ask the `platform-researcher` agent to re-check it.

Primary sources: code.claude.com/docs/en/{skills, sub-agents, memory, plugins/manifest-reference, plugins/marketplace-reference, plugin-evals, agent-teams}; github.com/anthropics/claude-code/blob/main/CHANGELOG.md.

## Contents
0. Working on another repository
1. Instructions
2. Skills
3. Subagents
4. Tools and model tiers
5. Hooks
6. Plugins and distribution
7. Testing
8. Gotchas

## 0. Working on another repository
- To read and write a repo outside the working directory, run `/add-dir <path>` in the session, or start with `claude --add-dir <path>`. Use absolute paths.
- Its `.claude/skills` and `.claude/agents` load only in sessions started inside it. For trigger and delegation tests, run `cd "<target>" && claude -p …`.

## 1. Instructions
- **Project:** `CLAUDE.md` (repo root and every parent), `.claude/CLAUDE.md`, and `CLAUDE.local.md` for personal, gitignored notes.
- **User:** `~/.claude/CLAUDE.md`.
- **Imports:** `@path/to/file.md`, nested at most 4 hops.
- **Path-scoped rules:** `.claude/rules/*.md`, with an optional `paths:` frontmatter list of globs.
- **AGENTS.md** is read natively since v2.1.277, as `AGENTS.md` and `.claude/AGENTS.md` in the working directory and its parents. It is read **only when** that directory has no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md`.
  - To load both, start CLAUDE.md with `@AGENTS.md`. This works on every version and never loads the file twice.
  - Alternative: choose "claude-md-and-agents-md" under /config → Project instructions.
- **Audit:** `/doctor prompt-audit` (v2.1.283) audits instructions, skills and agents for patterns written for older models.

## 2. Skills

**Locations**, highest precedence first:
1. managed
2. `~/.claude/skills/<name>/SKILL.md`
3. `.claude/skills/<name>/SKILL.md`
4. nested `<subdir>/.claude/skills/`
5. plugin `skills/`

Claude Code does **not** read `.agents/skills/`.

**Frontmatter.** Unknown keys are ignored silently. Booleans also accept yes/no/on/off/1/0.

| Field | Meaning |
|---|---|
| `name` | Optional. Defaults to the folder name. Use `[a-z0-9-]`, ≤ 64 chars, equal to the folder. `<`, `>` and bidi characters are refused. |
| `description` | What the skill does and when to use it. The listing shows `description` + `when_to_use` truncated at **1,536 chars**. |
| `when_to_use` | Extra trigger text (Claude-only; other platforms ignore it). |
| `argument-hint`, `arguments` | Shown or parsed for `/name args`. |
| `disable-model-invocation` | `true` = only the user can run it (use for side effects). |
| `user-invocable` | `false` = hidden from the `/` menu; the model can still load it. |
| `allowed-tools` | **Pre-approves** tools while the skill runs, e.g. `Bash(uv run *)`. It does not restrict tools. |
| `disallowed-tools` | Removes tools while the skill runs. |
| `model`, `effort` | Model override and effort (`low`…`max`) for the skill's turn. |
| `context: fork` + `agent` | Runs the skill in a forked subagent context. In the background by default since v2.1.218; set `background: false` to wait. |
| `hooks` | Hooks scoped to the skill. |
| `paths` | Globs: auto-load only when matching files are involved. |
| `shell` | Shell for `!command` injections. |
| `license`, `compatibility`, `metadata` | Agent Skills standard fields. |
| `display-name`, `default-enabled`, `fallback` | Listing and enablement controls (v2.1.186). |

**Substitutions in the skill body:**
- `$ARGUMENTS`, `$N`, `$name`;
- `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`;
- `!command` for preprocessing.

**Invocation:**
- The model loads skills with the `Skill` tool. Naming another skill in prose does not reliably load it, so write "Use the Skill tool to load `<plugin>:<name>`".
- The user runs `/name`, or `/plugin:name` for plugin skills.
- `/reload-skills` reloads skills. `/skill-doctor` shows unused skills and their context cost.

**Size:** keep SKILL.md under 500 lines. Put references one level deep, and give any file over 100 lines a table of contents.

## 3. Subagents

**Locations**, highest precedence first:
1. managed
2. `--agents '<json>'`
3. `.claude/agents/` (scanned recursively; the closest file wins)
4. `~/.claude/agents/`
5. plugin `agents/`

The name comes from the `name` field. Subfolders in plugin agents become part of the ID (`plugin:folder:name`). A *new* `.claude/agents/` directory needs a session restart.

**Frontmatter.** Only `name` and `description` are required. Unknown keys are ignored, and a file with invalid YAML is skipped silently.

| Field | Values / notes |
|---|---|
| `name` | ≤ 256 chars, no `:`, must not start with `-`. Use kebab-case. |
| `description` | The delegation trigger. "Use proactively when …" encourages automatic delegation. |
| `tools` / `disallowedTools` | Comma string or YAML list of **bare tool names** (plus `mcp__server__*`). Omitting `tools` inherits everything. Specifiers do **not** narrow access: `Bash(git diff *)` in `tools` does not limit commands, and in `disallowedTools` it removes the whole tool. To allow only some commands, give `Bash` plus a frontmatter `PreToolUse` hook that exits 2 for anything else. This works for project/user agents only, and only in a trusted folder; plugin agents ignore hooks. Alternatively use `permissions.deny` in settings, which applies to the whole session. |
| `model` | `inherit` (default), `haiku`, `sonnet`, `opus`, `fable`, or a full model ID. |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` (`manual` is an alias for `default`). |
| `maxTurns` | Integer. When reached, the result is marked partial. |
| `skills` | Skills preloaded in full at start, at most 32. Teammates in agent teams don't get them. |
| `mcpServers`, `hooks` | Per-agent servers and hooks. **Ignored for plugin agents**, as is `permissionMode`. |
| `memory` | `user`, `project` or `local`: a persistent memory folder for the agent. |
| `background` | `true` runs the agent in the background. |
| `effort` | `low` … `max`. |
| `isolation` | `worktree`: a temporary git worktree, removed if unchanged. |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. |
| `initialPrompt` | First turn, auto-submitted when used as the main agent. |
| `omitClaudeMd` | Skip CLAUDE.md files (v2.1.271). |
| `autoCompactWindow` | 100000–1000000 (v2.1.296). |

**Body:** the system prompt. The agent starts with no conversation history and returns only its final message.

**Delegation:**
- The main agent delegates via the `Agent` tool (shown as `Task` in some SDK messages), either automatically from `description` or explicitly with `@"name (agent)"`.
- Per-call parameters include `isolation: "worktree"`, `effort`, and `run_in_background`.
- Resume a finished agent with `SendMessage`.
- Built-ins: `Explore` (read-only), `Plan`, `general-purpose`.
- Limits:
  - concurrency is capped at 20;
  - nested spawning is limited (docs say 3 levels, v2.1.217 notes say off by default), so never design an orchestrator as a subagent.

**Main-thread agent:** `claude --agent <name>`, or `"agent": "<name>"` in settings. The agent's prompt replaces the default system prompt.

**Creating agents:** the `/agents` wizard was removed in v2.1.198. Write files directly (this is what `authoring-agents` does).

## 4. Tools and model tiers

**Common tool names** (non-exhaustive):
- files and search: `Read`, `Write`, `Edit`, `NotebookEdit`, `Glob`, `Grep`;
- shell: `Bash`, `PowerShell` (Windows);
- web: `WebFetch`, `WebSearch`;
- agents and skills: `Agent`, `Skill`, `SendMessage`;
- other: `AskUserQuestion`, `TodoWrite`, and MCP tools named `mcp__<server>__<tool>`.

**Permission patterns:** `Bash(git diff *)`, `Read(./docs/**)`, `Agent(Explore)`.

| Abstract tier | Claude value |
|---|---|
| same as caller | `inherit` |
| fast / cheap | `haiku` |
| balanced | `sonnet` |
| strongest | `opus` (or `fable` where available) |

**Running on DeepSeek:**
- Set `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`, `ANTHROPIC_AUTH_TOKEN`, and the `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL` variables.
- DeepSeek maps `claude-opus*` to V4 Pro and any other `claude*` name to Flash; other unknown names return HTTP 400. Use tier aliases in agent files and avoid full IDs.
- Set the variables per process (a launcher script), never globally.

## 5. Hooks
- Configure hooks in `settings.json` under `hooks` (user, project or local), in a plugin's `hooks/hooks.json`, or in skill and agent frontmatter.
- Events include:
  - tool events: `PreToolUse`, `PostToolUse`;
  - session and prompt events: `UserPromptSubmit`, `SessionStart`, `Notification`;
  - stop events: `Stop`, `SubagentStop`;
  - other: `PreCompact`, plus agent-team events.
- Use hooks for deterministic must-happen behavior, such as formatting after an edit or blocking a command.

## 6. Plugins and distribution

**Layout:**
```
.claude-plugin/plugin.json
skills/
agents/
hooks/hooks.json
.mcp.json
bin/        (added to the Bash PATH)
settings.json
```
A `CLAUDE.md` at the plugin root is **not** loaded.

**A plugin folder under `.claude/skills/`:** a folder in `<project>/.claude/skills/` that contains `.claude-plugin/plugin.json` loads as a whole plugin named `<name>@skills-dir` once the folder is trusted. Its skills appear as `/<name>:<skill>` and its agents as `<name>:<agent>`. This is how `install.py --scope workspace` wires stablehand. Source: observed on Claude Code 2.1.306, where the skills and agents resolved in an end-to-end run. No docs page describes it yet, so re-check it after major updates.

**plugin.json:**
- Only `name` is required. Other fields: `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, and component path overrides.
- `skills` adds to the default folder, while `agents` and `commands` replace it.
- Paths must start with `./` and stay inside the plugin root.

**marketplace.json** (at `.claude-plugin/marketplace.json`):
- Required: `name`, `owner.name`, and `plugins[]`, each with `name` + `source`.
- A `source` can be a relative path, `github`, `url`, `git-subdir`, `npm`, `archive` or `command`.
- Version resolution order: `version` in plugin.json → `version` in the marketplace entry → the git SHA.

**Names:**
- Plugin and marketplace names use `[A-Za-z0-9._-]`.
- Plugin names may not start with `claude-`, `anthropic-` or `cc-plugin-`.
- Reserved marketplace names include `agent-skills` and `claude-plugins-official`, and `npm`, `github` and similar.

**Commands:**
- Install: `claude plugin marketplace add <owner/repo | path>` → `claude plugin install <plugin>@<marketplace>`.
- Develop: `claude --plugin-dir <path>`.
- Check: `claude plugin validate <path> [--strict]`.
- Scaffold: `claude plugin init <name>`.
- Release: `claude plugin tag`.

**Third-party marketplaces:** auto-update is off by default.

## 7. Testing

**Trigger check.** Run headless and look for a `Skill` (or `Agent`) tool call with the artifact's name:
```
claude -p "<prompt>" --output-format stream-json --verbose --max-turns 3
```
Notes on headless runs:
- **Max turns.** When `--max-turns` is reached, the CLI exits **1** and reports `subtype: error_max_turns`. For a trigger test that is expected, not a failure.
- **`--allowed-tools` / `--disallowed-tools`.** Both are variadic. Pass each permission rule as its **own argument**, e.g. `--allowed-tools Read "Bash(git diff *)"`, and keep the flag last. A single comma-joined string breaks on the spaces inside patterns, so those tools get denied.
- **Approval prompts.** Headless runs cannot ask for approval. Any tool call that would need it is denied, so pre-approve exactly what the artifact needs.

**`claude plugin eval`** (v2.1.269+):
- **Suite layout:** suites live in the plugin's `evals/<case>/prompt.md` (frontmatter `max_turns`, `timeout_seconds`, `allowed_tools`, `model`, `tags`, `runs`; the body is the prompt) plus `graders/*.md`.
- **Graders:** `regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`.
- **Runs:** each case runs WITH and WITHOUT the plugin and reports the delta.
- **Tool grants:** grant write tools with `--allow-tools Write Edit`.
- **Windows:** granting Bash or PowerShell requires the OS sandbox, which native Windows lacks, so use WSL2 for those cases.

**Other tools:**
- The skill-creator plugin, if installed, has its own `evals/evals.json` format. It is not compatible with `claude plugin eval`.
- Isolated behavior runs: `scenario-runner` working in a git worktree of the target repo. The Agent tool's `isolation: "worktree"` only clones the *current* repository.

## 8. Gotchas
- A file with invalid frontmatter YAML is skipped silently. Run the validator after every edit.
- Use `allowed-tools` to pre-approve tools and `disallowed-tools` to remove them; the names don't make this obvious.
- Plugin agents ignore `hooks`, `mcpServers` and `permissionMode`.
- Skills in `.agents/skills/` are invisible to Claude Code.
- A long `description` + `when_to_use` is truncated at 1,536 chars in the listing. Put triggers first.
- Startup warns when all custom agent descriptions together exceed 15,000 tokens. Keep agent descriptions short.
