# Platform card: Google Antigravity

Last verified: 2026-11-26. Versions checked: App 2.38.0 (changelog), IDE 2.8.0 (docs; 2.7.0 local), CLI `agy` 1.5.17 (changelog; 1.5.5 local).

Antigravity moves fast. When a detail matters and may be stale, ask the `platform-researcher` agent to re-check it.

Primary sources:
- `antigravity.google/docs` (`customization-discovery`, `skills`, `rules`, `subagents`, `plugins`, `build-plugins`, `hooks`, `mcp`, `models`, `permissions`, `sandbox`, `dynamic-workflows`, `slash-commands`, `cli/headless`, `cli/reference`, `cli/commands/agents`, `migration/workflows-to-skills`, `changelog`);
- `antigravity.google/schemas/v1/plugin.json`;
- local `agy` 1.5.5 (`--help`, `models`, `plugin validate`, `-p ... --output-format stream-json`);
- the built-in `agy-customizations` and `plugin` skill docs.

## Contents
1. Surfaces and roots
2. Instructions and rules
3. Skills
4. Agents
5. Tools and model tiers
6. Plugins, hooks, MCP
7. Testing
8. Gotchas

## 1. Surfaces and roots
- **Surfaces:**
  - **App** (2.x desktop, v2.38.0; remote tunnel and panel updates; supports Remote SSH to 64-bit Linux hosts);
  - **IDE** (VS Code fork, actively maintained, v2.8.0);
  - **CLI `agy`** (Go, closed source, near-daily releases, v1.5.17 — altscreen mouse cursor/selection, enterprise `.git`/`.env` boundary fix, `/model` fallback refinements);
  - **IDE extensions** (VS Code, Visual Studio, Eclipse, JetBrains, Android Studio, Zed, Xcode, plus any editor via **`agy acp`**);
  - **Python SDK** (`google-antigravity`).

  All share one harness, and subagents are documented for the App, CLI, IDE, and IDE extensions (VS Code, Visual Studio, Eclipse).
- **Workspace root:** `.agents/`, discovered by walking **up** from the workspace folder to the repo root (`.git`). Legacy names `.agent/`, `_agents/` and `_agent/` still work. Antigravity does **not** search subfolders below the workspace folder (e.g., opening the repo root does not load `src/routes/AGENTS.md`, even when editing files there).
- **Workspace boundaries for execution:** `run_command` requires `Cwd` to be located within an active workspace folder. When working on an external target repository, add the target folder to the workspace (multi-root workspace in App/IDE, or `agy --add-dir <path>` / `/add-dir` in CLI) or run commands directly from a scratch copy of the target via `agy -p`. In CLI `auto` mode (default since `v1.5.7` where the OS terminal sandbox is available — Linux namespaces, macOS Seatbelt, Windows 11 24H2 Aug 2026+ Process Security Environments), CLI 1.5.14 allows reading files outside the workspace without prompting; CLI 1.5.16 also allows creating/editing outside without prompting when targeting a VCS repo (Git, Jujutsu, Mercurial) or making strictly additive edits.
- **Personal / global root:** `~/.gemini/config/`, shared by App, IDE and CLI, plus `~/.gemini/{AGENTS,GEMINI}.md`.
  - Antigravity 1.x used `~/.gemini/antigravity/`, which old codelabs still show.
  - CLI also loads skills from `~/.gemini/antigravity-cli/skills/` and `~/.gemini/skills/`, plus `~/.agents/skills/` (CLI 1.5.16+), which the App does not read. In the CLI, `~/.gemini/antigravity-cli/skills/` and `~/.gemini/skills/` outrank all other scopes and are not hidden by manifest `exclude` lists. Prefer `~/.gemini/config/skills/` for cross-surface use.
- **Personal folder in a shared repo:** `.gemini/config.json` at the repo root accepts `{"personal_customization_dir": "people/{user}"}` (`USER` or Windows `USERNAME`), overriding workspace `.agents/`.
- **Precedence, high to low:**
  1. repository personal directory (`.gemini/config.json`)
  2. workspace `.agents/` and its manifests, walking up to the repository root
  3. personal `~/.gemini/config/` and its manifests
  4. built-ins

  (In the CLI, `~/.gemini/antigravity-cli/skills/` and `~/.gemini/skills/` take priority over all four.) The higher entry wins a skill or agent name clash. Rules are cumulative and plugin skills are namespaced as `<plugin>:<skill>`.
- **Discovery manifests:** `skills.json`, `rules.json`, `agents.json`, `plugins.json` (in `.agents/` or `~/.gemini/config/`):
  - Top-level fields: `{"inherits": […], "entries": […], "exclude": […]}` (`exclude` hides matching items across scopes except CLI-only skill folders).
  - Entry / inherit object: `{"path", "include_only", "exclude"}`.
  - Entries are scanned one level deep; list nested items explicitly in `include_only` (no wildcards; no `~` expansion — use absolute paths for external folders).
  - Security (CLI 1.5.2+): workspace `.agents/plugins.json` and `.agents/skills.json` only load paths inside the workspace or repository root; `../`, absolute escapes, and external symlinks are skipped.

## 2. Instructions and rules
- **Always-on files** (no frontmatter), loaded from the workspace folder and parent directories up to the repository root (not from subfolders below the workspace): `AGENTS.md` or `GEMINI.md`, `.agents/AGENTS.md` or `.agents/GEMINI.md`.
- **Global files:**
  - `~/.gemini/{AGENTS,GEMINI}.md`;
  - `~/.gemini/config/{AGENTS,GEMINI}.md`;
  - `~/.gemini/config/rules/*.md`.
- **Rules:** `.agents/rules/*.md` (scanned flat; nested files must be listed in `rules.json`). Frontmatter:

  | `trigger` | Required extra field | Behavior |
  |---|---|---|
  | `always_on` | — | always injected |
  | `model_decision` | `description` | path + description injected; content read on demand |
  | `glob` | `globs` (or `glob`), comma-separated string | loaded for matching files; quote patterns starting with `*` so YAML does not treat `*` as an alias |
  | `manual` | — | loaded on `@`-mention only (**not supported in Antigravity CLI**) |

  Missing frontmatter or an invalid `trigger` (for example `alwaysOn`) is **silently discarded**.
- **Limits:**
  - 24,000 bytes (24 KB) per rule file, checked after expanding `@[label](path)` includes;
  - a shared **20,000-token** budget for global + `always_on` rules. Over budget, the largest files are demoted to one-line pointers (`- <path>: <description>`). Rules from built-in plugins are exempt.
- **File includes:**
  - `@[label](path)` **inlines** the target file (resolving relative paths from the rule file and expanding `~/`, stripping any YAML frontmatter) before the 24,000-byte limit check.
  - `@filename` does **not** inline; it resolves and rewrites to a canonical absolute workspace path (`@/workspace/path`).
- **Legacy workflows:** `.agents/workflows/` and `global_workflows/` are deprecated in favor of Agent Skills (`/migrate-workflows` in App 2.12+ converts them). The new workflow system is **Dynamic Workflows (`/run-workflow`)** (Python orchestration scripts).

## 3. Skills
- **Locations:**
  - workspace `.agents/skills/<name>/SKILL.md` (legacy `.agent/skills/`);
  - personal `~/.gemini/config/skills/<name>/` (CLI also loads `~/.gemini/antigravity-cli/skills/` and `~/.gemini/skills/`);
  - plugin `plugins/<p>/skills/<name>/`.
- **Frontmatter:**
  - `name`: lowercase-hyphen (`1–64` chars), matching the folder name. Optional for standalone skills (defaults to folder name; CLI `< 1.5.10` collapsed nameless skills to `SKILL`), required for plugins (`agy plugin validate --strict`) and Marketplace.
  - `description`: required (`1–1,024` chars); third person, says what and when.
  - Extras:
    - `disable-model-invocation: true` (`docs/build-plugins`): prevents automatic model invocation so the skill runs only via `/<name>`. For side-effecting skills, also state "run only when explicitly requested" in `description` as defense-in-depth across older surfaces;
    - `disable-slash-command: true` (CLI 1.1.12+): hidden from the `/` menu, the model can still use it;
    - `license`, `compatibility`, `metadata` (e.g. `metadata.icon` emoji).

  Unknown keys are tolerated. Keep to the Agent Skills standard fields plus these extras.
- **Folders:** `scripts/` (retains `0755` executable mode in Marketplace bundles), `references/`, `assets/`, `examples/`, `resources/`.
  - Link bundled files with relative paths from `SKILL.md`.
  - The docs suggest running scripts with `--help` rather than reading their source.
- **Invocation:**
  - The model sees name + description and reads `SKILL.md` when relevant.
  - Every skill (unless `disable-slash-command: true`) is also a slash command: `/name`, or `/<plugin>:<skill>` (or `/<skill>` from the plugin's UI/chips). Commands can be stacked (`/plan /grill-me …`).
  - Headless `-p` expands `/<skill>` unless `--disable-slash-commands` is passed.
  - In the App/IDE, skills appear in Customizations.
- **Loading another skill from a skill:** tell the agent explicitly to invoke `/<skill>` or to read that skill's `SKILL.md` by path. Naming it in prose is not reliable.
- **Limits:** `agy plugin validate` warns on a body over **24 KB**, on name/folder mismatch, and on duplicate names.
- **Reload:** files are reread before each turn; run `/skills reload` in CLI to refresh the `/` menu and `/skills` list.

## 4. Agents (custom subagents)
- **Surfaces:** App, CLI, IDE, and IDE extensions (VS Code, Visual Studio, Eclipse).
- **Locations:**
  - workspace `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md`;
  - global `~/.gemini/config/agents/…`;
  - plugin `plugins/<p>/agents/`.

  `agent.json` files are ignored; agents are Markdown with YAML frontmatter.
- **Frontmatter:**

  | Field | Type / default | Notes |
  |---|---|---|
  | `name` | string, required | unique (`kebab-case`) |
  | `description` | string, required | the planner uses it to decide when to delegate |
  | `tools` | string[], `[]` (`docs/subagents`) / all (`docs/build-plugins`) | **always list explicitly** for least privilege; canonical Cortex tool names only (section 5) — **a misspelled or unknown name can hang the subagent** |
  | `model` | `inherit` (default), `flash_lite`, `flash`, `pro` | |
  | `commandExecutionPolicy` | `off`, `auto`, `eager`, `sandbox` (default) | |
  | `mainAgent` | bool, default `true` | selectable as the primary agent |
  | `subagent` | bool, default `true` | invocable via `invoke_subagent` |
  | `skills`, `plugins`, `rules`, `agents`, `hooks` | string[] of paths | relative to the agent file, project, or absolute |
  | `mcpServers` | object[] | per-agent MCP server configs |
  | `hidden`, `inheritMcp`, `inheritCustomizations`, `excludeDefaultComponents` | bool | `inheritMcp` and `inheritCustomizations` default to `true` (since CLI 1.1.25 agents inherit ambient skills, rules, hooks and subagents by default) |

- **Body:** the system prompt, in Markdown. Google's example uses `# System Prompt` and `# Review Guidelines` headings.
- **Invocation:**
  - `invoke_subagent` (planner or explicit; supports `Workspace`: `inherit` / `branch` / `share`, and `Model`: `inherit` / `flash_lite` / `flash` / `pro`);
  - `@<agent> message` (CLI 1.2.9+ and App);
  - `agy --agent <name>` (as main agent);
  - `agy agents` (lists available agents) and the `/agents` panel;
  - in the App, subagent cards.
- **Built-ins:** `research` (codebase exploration), `browser` (App v2.30.0+ personal accounts can launch single/parallel `browser` subagents automatically; CLI and business/enterprise use `/browser`), `self` (a clone of the caller), `image-generator`.
- **Multi-agent orchestrators:** prefer built-ins over custom orchestrator subagents: **Orchestrator** model mode (frontier planner + fast executor), **`/run-workflow`** (Dynamic Workflows in bundled Python), **`/swarm`** (shared message board), **`/boost`** (deep reasoning, paid plans), and **`/teamwork`** (multi-milestone teams, paid plans).
- **Limits:**
  - nesting is capped at 10 levels;
  - subagents inherit the parent's command prefixes, file scopes and sandbox settings.
- **Transient agents:** `define_subagent` creates one at runtime.

## 5. Tools and model tiers

**Canonical vs. model-facing tool names.** Custom agent `tools:` frontmatter, `hooks.json` matchers, and `agy --output-format stream-json` (`init.tools`) use **canonical Cortex step names** (`view_file`, `replace_file_content`, `multi_replace_file_content`, `write_to_file`, etc.), even though Gemini 4 / App 2.x model prompts may expose model-facing aliases such as `read_file`, `edit_file`, and `write_file`. Always put canonical names in agent `tools:`.

| Capability | Antigravity tool | Status |
|---|---|---|
| read file | `view_file` | documented |
| edit file | `replace_file_content`, `multi_replace_file_content` | documented |
| create file | `write_to_file` | documented |
| list / find files | `list_dir`, `find_by_name` | documented |
| search text | `grep_search` | documented |
| run command | `run_command` | documented (requires workspace folder or `--add-dir`) |
| background tasks / schedule | `manage_task`, `schedule` | documented |
| permissions | `list_permissions`, `ask_permission` | documented |
| web | `search_web`, `read_url_content` | documented |
| delegate / collaborate | `invoke_subagent`, `define_subagent`, `send_message`, `manage_subagents` | documented |
| workflows & MCP | `run_workflow`, `call_mcp_tool` | documented |
| interaction / media | `ask_question`, `generate_image` | documented |
| browser | `browser_subagent` | observed (`init.tools`) |
| MCP resources & marketplace | `read_resource`, `list_resources`, `search_marketplace`, `list_plugin_accounts` | observed (`init.tools`) |
| notebook / sed helpers | `notebook_edit`, `notebook_execution`, `sed_file` | observed (`init.tools`) |
| legacy command follow-up | `command_status`, `send_command_input`, `read_terminal` | observed (`init.tools`; superseded by `manage_task`) |
| IDE binary symbols | `view_file_outline`, `view_code_item`, `codebase_search`, `task_boundary`, `notify_user` | binary (IDE 2.5.5) |

"Observed" and "binary" identifiers appear in `agy 1.5.5` `init.tools` or the shipped binary rather than the public `hooks`/`build-plugins` docs; confirm before relying on them (use `platform-researcher` or a quick test agent).

| Abstract tier | Antigravity value |
|---|---|
| same as caller | `inherit` |
| lightest / high-volume | `flash_lite` |
| fast / cheap | `flash` |
| strongest | `pro` |

Current CLI model slugs (`agy models`, checked 2026-11-24) include `gemini-4-neon-{low,medium,high,xhigh}` (default on eligible paid plans), `gemini-4-carbon-{low,medium,high}`, `gemini-4-argon-{low,medium,high}`, `gemini-4-hydrogen-{low,medium,high,xhigh}`, `gemini-pro-orchestrator` (Carbon), `gemini-pro-orchestrator-argon`, `gemini-pro-orchestrator-neon`, `gemini-3.8-flash-{low,medium,high}` (all plans), plus `claude-opus-5-5-*`, `claude-sonnet-5-5-*`, and `gpt-oss-120b-medium`.

## 6. Plugins, hooks, MCP
- **Plugin layout** (in a customization root, `.agents/plugins/` or `~/.gemini/config/plugins/`):
  ```
  plugins/<name>/
  ├── plugin.json                (or .antigravity-plugin/plugin.json in multi-tool repos)
  ├── README.md                  (optional pre-install Marketplace docs)
  ├── assets/logo.svg            (square 1:1 icon >= 128x128)
  ├── scripts/                   (retains 0755 permissions in Marketplace bundles)
  ├── skills/<skill>/SKILL.md
  ├── agents/<agent>.md          (App/CLI/IDE)
  ├── rules/                     (AGENTS.md always-on, or <rule>.md with trigger:)
  ├── hooks.json                 (MUST sit at plugin root, not hooks/hooks.json)
  └── mcp_config.json
  ```
- **`plugin.json` manifest** (official schema `https://antigravity.google/schemas/v1/plugin.json`, `additionalProperties: false`):
  - Supported fields: `$schema`, `name` (required by CLI/Marketplace; lowercase kebab-case required by Marketplace and `agy plugin validate --strict`), `displayName` (`display_name`), `description`, `version`, `disabled`, `logo` (relative `.png/.svg/.jpg/.jpeg/.webp` >= 128x128), `suggestedPrompts` (`suggested_prompts`, up to 3), `skills` (extra skill dirs), `author` (string or `{"name", "email", "url"}`), `homepage`, `repository`, `license`, `keywords`, `extensions`.
  - Deprecated (do not set): `source`, `sourcePath`, `source_path`.
  - `.antigravity-plugin/plugin.json` takes precedence over root `plugin.json` (and `.gemini-plugin/plugin.json` is also supported) in multi-tool repositories, while component folders stay at `<plugin-root>`.
- **Behavior and path variables:** plugin skills and tools are namespaced (`/<plugin>:<skill>`). Plugins never load `commands/` or `workflows/`. `${PLUGIN_ROOT}`, `${PLUGIN_DATA}`, and `${VARIABLE_NAME}` expand in `mcp_config.json`; `PLUGIN_ROOT` and `PLUGIN_DATA` are exported to MCP server and hook environments (hooks run with `cwd` = `<plugin-root>`, so use relative paths like `./scripts/...`).
- **Install and validate:**
  - drop the folder into a plugins root (workspace `.agents/plugins/` or global `~/.gemini/config/plugins/`);
  - or `agy plugin install <path | https://github.com/o/r[/tree/main/subdir] | plugin[@antigravity-plugins-official]>` (installs globally into `~/.gemini/config/plugins/<name>`);
  - or `agy plugin import [gemini|claude]`;
  - or for workspace isolation without modifying global configuration, link into `<target>/.agents/plugins/<name>` (via `uv run tools/install.py antigravity --scope workspace` or directory junction).

  Validate with `agy plugin validate [--strict] [--json] <dir|zip|https-url|github-url>` and inspect global installs with `agy plugin list --json`. In multi-tool repos, `agy plugin validate` warns on ignored other-tool files (`.mcp.json`, root `AGENTS.md`, shadowed root `plugin.json`); filter via `--json` or run without `--strict`.
- **Hooks:** `.agents/hooks.json`, `~/.gemini/config/hooks.json`, or `<plugin-root>/hooks.json`.
  - Events: `SessionStart`, `PreInvocation`, `PostInvocation`, `Stop` (flat handler arrays), and `PreToolUse`, `PostToolUse` (grouped `{matcher, hooks}` with tool-name regex).
  - Synchronous `type: "command"`, camelCase JSON on stdin/stdout, must exit `0` (non-zero fails open).
  - `PreToolUse` decisions: `allow`, `auto_approve`, `deny`, `ask`, `force_ask`, `deny_unless_prior_grant`, plus `overwrite` and `permissionOverrides`. `Stop` input includes `continuationActive` (CLI 1.5.6+).
- **MCP:** `mcp_config.json` (global `~/.gemini/config/`, workspace `.agents/`, or plugin):
  - `stdio` (`command`, `args`, `env`, `cwd`) or Streamable HTTP (`serverUrl`/`url`, `headers`; legacy HTTP+SSE and `httpUrl` unsupported).
  - Lazy loading is default (`call_mcp_tool`); set `tools.<name>.eager: true` for upfront registration; `timeoutSeconds` defaults to `180`s per call / `300`s connect; supports `enabledTools`/`disabledTools`, `authProviderType: "google_credentials"`, OAuth 2.0 PKCE (CIMD `https://antigravity.google/oauth/client-metadata.json`, DCR, or manual `oauth`), plugin `variables` (installs disabled until configured), and MCP Apps (`ui://`).
  - Plugin servers are namespaced `<plugin>_<server>`.

## 7. Testing
- **Real-loader trigger & delegation check:** run `agy -p "<prompt>" --output-format stream-json` (NDJSON), **not** `--output-format json` (which emits only a final summary envelope without intermediate tool steps).
  - Inspect `init` (`cwd`, `tools`, `permission_mode`, `model`, `agent`), `step_update` (`step_type: "tool"`, `tool_name`, `tool_info` for skill `SKILL.md` reads; `subagent_info.subagents[].type_name` for delegation), and `result` (`status`, `response`, `usage`, `duration_seconds`).
- **Multi-turn & headless flags:** `--input-format stream-json --output-format stream-json`, `--json-schema`, `--print-timeout`, `--model <slug>`, `--effort <low|medium|high|xhigh|max>`, `--mode <default|accept-edits|auto|plan>` (also supported with `--remote-agent` since CLI 1.5.15), `--sandbox`, `--settings <json|path>`, `--disable-slash-commands`, `--add-dir <path>` (repeatable), `-r`/`--resume <id>` (CLI 1.5.16 alias for `--conversation`). Note CLI `v1.5.7+` defaults `agy -p` to `auto` mode where the OS sandbox is available; pin `--mode` in CI and evals.
- **List what loaded:** `agy -p "/skills" --output-format json` lists standalone skills without an agent turn, but does **not** list plugin skills (`/<plugin>:<skill>`). `agy plugin list --json` shows only global installs, and `agy agents` lists available primary agents. To check a workspace plugin, run `agy plugin validate --strict <plugin folder>` and invoke one of its skills.
- **Interactive:** `/skills reload`, `/agents`, `/hooks`, `/mcp`, `/plugin`, `/thinking [on|off]` (live reasoning stream, CLI 1.5.15+), `/swarm` (includes Swarm Overview panel in CLI 1.5.15+), `@agent`.
- **Validation:** `agy plugin validate` checks `plugin.json` against the v1 schema, skill frontmatter/names/size (> 24 KB warnings), agent/rule/hook/MCP syntax, logo paths, and Claude-style `commands/` or top-level `"hooks"`.
- **Evals:** there is no official eval runner. Use the stablehand eval protocol with a `scenario-runner` subagent and `agy -p ... --output-format stream-json` runs.

## 8. Gotchas
- Before CLI 1.3.6, an unquoted `description:` containing `: ` broke loading of skills, rules and agents; YAML also breaks on unquoted leading `*` in `globs:`. Always double-quote frontmatter strings.
- An invalid or missing rule `trigger` is dropped silently, and an unknown tool name in an agent `tools:` list can hang the subagent. Lint before use.
- **Never paste model-facing aliases** (`read_file`, `edit_file`, `write_file`) into custom agent `tools:` frontmatter; use canonical Cortex names (`view_file`, `replace_file_content`, `multi_replace_file_content`, `write_to_file`).
- Discovery walks up from the workspace folder to the repo root, never down into subfolders below the workspace.
- `trigger: manual` rules cannot be `@`-mentioned in the CLI.
- `.agents/skills/` is also read by OpenCode and Codex. Keep Antigravity-tailored skills in a workspace plugin (`.agents/plugins/<set>/skills/`) when the repo is also used with OpenCode or Codex (see `coexistence.md`).
- Native Antigravity plugins must place `hooks.json` directly at `<plugin-root>/hooks.json`, never `hooks/hooks.json`.
- Google's own built-in skills are loose: underscores in folder names, missing frontmatter. Don't copy that style; follow the Agent Skills standard.
- Claude Code plugins are not consumed as-is: there are no `commands/`, and hooks/MCP filenames differ (`hooks.json` and `mcp_config.json` at plugin root).
- Windows UTF-8 BOM bugs in `plugin.json`, `hooks.json`, and agents were fixed in CLI 1.5.8–1.5.11, but still save files as UTF-8 without BOM.
