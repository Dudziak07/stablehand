# Platform card: OpenCode (with DeepSeek)

Last verified: 2026-10-21. When a detail matters and may be stale, ask the `platform-researcher` agent to re-check it.

Primary sources:
- opencode.ai/docs/{skills, agents, permissions, rules, commands, providers, cli, plugins};
- the models.dev catalog (provider `deepseek`);
- api-docs.deepseek.com.

## Contents
1. Instructions
2. Skills
3. Agents
4. Permissions (tools)
5. Models (DeepSeek)
6. Commands
7. Testing
8. Gotchas
9. Hooks (plugins)

## 1. Instructions
- **Project:** `AGENTS.md`, found by walking up from the working directory. If there is no AGENTS.md, OpenCode falls back to `CLAUDE.md`.
- **Global:** `~/.config/opencode/AGENTS.md`. If it is missing, OpenCode falls back to `~/.claude/CLAUDE.md`.
- **More files:** list them in the `instructions` array in `opencode.json` (paths, globs or URLs). They are added on top of AGENTS.md.
- **Turning off Claude compatibility:**
  - `OPENCODE_DISABLE_CLAUDE_CODE=1` turns off all `.claude` support;
  - `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1` stops reading `~/.claude/CLAUDE.md`;
  - `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` stops reading `.claude/skills`.

## 2. Skills
- **Locations**, each as `<name>/SKILL.md`:
  - `.opencode/skills/`
  - `~/.config/opencode/skills/`
  - `.claude/skills/` and `~/.claude/skills/` (Claude compatibility)
  - `.agents/skills/` and `~/.agents/skills/`

  Project paths are searched from the working directory up to the git worktree root. **Names must be unique across all locations.**
- **Frontmatter:** only the Agent Skills standard fields are read.

  | Field | Notes |
  |---|---|
  | `name` | required. Lowercase-hyphen and equal to the folder name. |
  | `description` | required, 1–1024 chars. The model chooses skills from it. |
  | `license`, `compatibility` | optional |
  | `metadata` | string→string map. OpenCode keys: `opencode/slash: "true"` exposes the skill as `/name` in the TUI; `opencode/autoinvoke: "false"` hides it from automatic selection (it can still be loaded by exact name). |

  Claude-only keys (`when_to_use`, `disable-model-invocation`, `allowed-tools`, `context`, …) are ignored. Encode the same intent in `metadata` and `permission` instead.
- **Invocation:**
  - The model calls the `skill` tool: `skill({ name: "x" })`. Available skills are listed in that tool's description.
  - To load another skill from inside a skill, say so explicitly: "call the skill tool with name `x`".
- **Access control:** `permission.skill` patterns in `opencode.json` or in an agent's frontmatter, with the values `allow`, `ask` or `deny`. Setting `tools: { skill: false }` hides skills entirely for that agent.
- **Bundled files:** refer to them by relative path from SKILL.md and state that they live in the skill's folder.

## 3. Agents
- **Locations:**
  - `.opencode/agents/<name>.md` (project) or `~/.config/opencode/agents/<name>.md` (user). **The file name is the agent name.**
  - Agents can also be defined under the `agent` key of `opencode.json`.
- **Frontmatter:**

  | Field | Values / notes |
  |---|---|
  | `description` | required. Used for automatic delegation. |
  | `mode` | `primary` (switch to it with Tab), `subagent` (invoked via the Task tool or `@name`), `all` (the default) |
  | `model` | `provider/model-id`. Primary agents default to the global model. **Subagents default to the model of the primary that invoked them.** |
  | `temperature`, `top_p` | sampling. Ignored by DeepSeek in thinking mode. |
  | `steps` | maximum agentic iterations. Replaces the deprecated `maxSteps`. |
  | `permission` | per-tool rules (section 4). Use this instead of `tools`. |
  | `tools` | **deprecated**. Boolean on/off map. |
  | `hidden` | hides a subagent from the `@` menu (subagents only) |
  | `disable` | `true` disables the agent |
  | `prompt` | system prompt from a file: `{file:./prompt.md}`. Otherwise the body is the prompt. |
  | `color` | hex, or one of `primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info` |
  | other keys | passed to the provider as model options, e.g. `reasoningEffort` |

- **Built-ins:**
  - primary agents: `build` (all tools) and `plan` (edits restricted);
  - subagents: `general`, `explore` (read-only) and `scout` (external docs and dependencies).
- **Orchestration:** for an orchestrator, use a `mode: primary` agent or a skill, never a subagent. `permission.task` controls which subagents an agent may launch.
- **CLI:** `opencode agent create` (it takes `--path`, `--description`, `--mode`, `--permissions` and `--model`, which make it non-interactive) and `opencode agent list`.

## 4. Permissions (tools)
Permission keys and what each pattern matches:

| Key | Pattern matches |
|---|---|
| `read` | the file path. `*.env` is denied by default. |
| `edit` | all file changes (edit, write, patch) |
| `glob` | the glob pattern |
| `grep` | the regex |
| `bash` and `shell` | parsed shell commands. **Write both, with the same rules** (see below). |
| `task` | the subagent type |
| `skill` | the skill name |
| `lsp` | — |
| `question` | — |
| `webfetch` | the URL |
| `websearch` | — |
| `external_directory` | paths outside the project. Defaults to `ask`. |
| `doom_loop` | the same call repeated 3 times. Defaults to `ask`. |

- **Values:** `allow`, `ask`, `deny`, or a map of `pattern → value`. The last matching rule wins, so put `"*"` first.
- **Patterns:** `*` and `?`. A leading `~` or `$HOME` expands to the home directory.
- **Merging:** agent rules merge over the global config and take precedence.
- **`bash` vs `shell`:** the docs name the key `shell`, but OpenCode 1.19.3 enforces only `bash` and silently ignores `shell`. Tested 2026-10-23: with `shell: {"*": deny}` an agent still ran `git diff --output=x.txt` and wrote the file; with `bash` the same rule blocked it. Write both keys with identical rules, so the agent stays restricted on releases that use either name. `--auto` does not override a `deny`.

Read-only reviewer example:
```yaml
permission:
  edit: deny
  bash:
    "*": deny
    "git diff --staged": allow
    "git diff --staged -- *": allow
  shell:
    "*": deny
    "git diff --staged": allow
    "git diff --staged -- *": allow
  webfetch: deny
  websearch: deny
  task: deny
```
Keep shell patterns exact. A trailing wildcard such as `"git diff*"` or `"git log *"` also admits `--output=<file>`, which writes a file. After `--`, git treats every argument as a path, so `"git diff --staged -- *"` is safe.

| Abstract capability | OpenCode permission key |
|---|---|
| read / search files | `read`, `glob`, `grep` |
| edit / create files | `edit` |
| run commands | `bash` + `shell` (same rules) |
| web | `webfetch`, `websearch` |
| delegate | `task` |
| load skills | `skill` |
| ask the user | `question` |

## 5. Models (DeepSeek)
- **Connecting:** `/connect` → DeepSeek, or set `DEEPSEEK_API_KEY`. `opencode models deepseek` lists the IDs.
- **Model IDs** (models.dev, 2026-10-21):

  | ID | Model | Notes |
  |---|---|---|
  | `deepseek/deepseek-flash` | DeepSeek V4.1 Flash (1017) | 1M context, vision, cheapest. The default choice. |
  | `deepseek/deepseek-v4-pro` | DeepSeek V4 Pro | no vision; for heavier text-only reasoning |
  | `deepseek/deepseek-v4-flash` | DeepSeek V4 Flash | earlier Flash version |

- **Tiers:**

  | Abstract tier | Value |
  |---|---|
  | same as caller | omit `model` (subagents inherit) |
  | fast / cheap | `deepseek/deepseek-flash` |
  | strongest | `deepseek/deepseek-v4-pro` |

- **DeepSeek specifics:**
  - Thinking is on by default. `temperature` is ignored in thinking mode.
  - Context caching is automatic, so keep system prompts and skill text byte-stable.
  - Off-peak pricing is half price.
  - DeepSeek models follow terse instructions less reliably than Claude. Use numbered steps, exact commands, explicit output templates, and state the output language.

## 6. Commands
- **Locations:** `.opencode/commands/<name>.md` and `~/.config/opencode/commands/`.
- **Frontmatter:** `description`, `agent`, `model`, `subtask`.
- **Body placeholders:** `$ARGUMENTS`, `$1`…, `` !`cmd` ``, `@file`.
- **Prefer skills** with `metadata.opencode/slash: "true"`, because they work on every platform. Use a command only for a thin launcher, such as one that runs a skill with a fixed agent and model.

## 7. Testing
- **Headless run:**
  ```
  opencode run "<prompt>" --format json [--agent <name>] [--model deepseek/deepseek-flash] [--dir <path>]
  ```
  `--format json` prints raw JSON events. Look in them for `skill` tool calls (trigger tests) and `task` calls (delegation).
- **Agents:** `opencode agent list` shows which agents loaded.
- **Evals:** there is no official runner. Use the stablehand eval protocol with `opencode run`. A `scenario-runner` subagent works for behavior runs.

## 8. Gotchas
- OpenCode also reads `.claude/skills/` and `.agents/skills/`. Same-named variants for other platforms collide. Use `.opencode/skills/` and set `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` (see `coexistence.md`).
- Claude tool names (`Read`, `Grep`, `Agent`, …) mean nothing here. Express capabilities through `permission` keys, and in prose say "read the file", "run the command".
- `tools:` in agent frontmatter is deprecated; use `permission`.
- The agent name is the file name. A `name:` key is not documented.
- Subagents silently inherit the invoking primary's model. Set `model` explicitly when a subagent needs a different tier.

## 9. Hooks (plugins)

There is no `hooks` key in `opencode.json`. Hooks are **plugins**: JavaScript or TypeScript modules that export a function returning handlers for events.
- **Locations:** `.opencode/plugins/` (project) and `~/.config/opencode/plugins/` (global) are loaded automatically. npm packages are listed in the `plugin` array of `opencode.json`.
- **Shape:** the plugin function receives `{ project, client, $, directory, worktree }` and returns an object such as `{ "tool.execute.before": async (input, output) => { … } }`. Throw to block a tool call.
- **Events:** `tool.execute.before`, `tool.execute.after`, `file.edited`, `session.idle`, `shell.env`, and more.
- **Source:** opencode.ai/docs/plugins (checked 2026-10-23).

Example that blocks reading `.env` files:
```ts
export const EnvProtection = async () => ({
  "tool.execute.before": async (input, output) => {
    if (input.tool === "read" && output.args.filePath.includes(".env")) {
      throw new Error("Do not read .env files")
    }
  },
})
```

