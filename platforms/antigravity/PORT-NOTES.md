# Port Notes: Google Antigravity

- **Date:** 2026-10-23
- **Last reviewed:** 2026-11-21 (Gemini 4 Neon; App 2.34.0 docs, IDE 2.8.0 docs / 2.7.0 local, CLI `agy` 1.5.14 changelog / 1.5.5 local)
- **Source contracts:** 2026.10.0 (updated to 2026.10.1; manifest 2026.11.0)
- **Author:** Antigravity agent (Gemini 3.8 Flash)
- **Target environment:** Antigravity IDE 2.5.5 (VS Code 1.107.0) / App 2.0.10 (ProductVersion of %LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe) / CLI `agy 1.4.5` (reviewed 2026-11-21 against App 2.34.0, IDE 2.8.0 / 2.7.0 local, CLI `agy 1.5.14` / `1.5.5` local)

---

## 1. Access to Targets Outside the Workspace

During bootstrap investigation of Antigravity behavior on external repositories:
- **File inspection and reads (`view_file`):** Accepts absolute paths anywhere on the local filesystem accessible by user OS permissions.
- **File creation and edits (`write_to_file`, `replace_file_content`, `multi_replace_file_content`):** Accepts absolute paths directly and automatically creates parent directories when required.
- **Command execution (`run_command`):** In Antigravity IDE, `run_command` requires `Cwd` to be located within an active workspace folder. For external target repositories, the recommended approach is to add the target folder to the workspace (multi-root workspace in Antigravity IDE) or execute tests via CLI `agy` invoked directly from the target folder (`agy -p "<prompt>" --output-format json`).

---

## 2. Per-Contract Mapping Decisions and Lossy Items

### `designing-agent-setups`
- **Mapping:** Implemented as `skills/designing-agent-setups/SKILL.md`. Exploration role delegated to built-in `research` subagent. Subagent justification enforced through 5 reasons in `references/decision-guide.md`.
- **Lossy items:** Claude `$ARGUMENTS` and `argument-hint` frontmatter fields are unsupported in Antigravity and dropped. Target paths are passed in the prompt or clarified interactively.
- **Untested behavior:** Interactive slash command stacking with plugin skills (`/plan /stablehand:designing-agent-setups`).

### `authoring-skills`
- **Mapping:** Implemented as `skills/authoring-skills/SKILL.md`. Test-first RED/GREEN workflow using `scenario-runner` in isolation.
- **Lossy items:**
  - Claude `disable-model-invocation: true` has no boolean frontmatter counterpart in Antigravity (Antigravity's `disable-slash-command` does the opposite: it hides from the `/` menu while allowing model invocation). As specified in `shared/references/antigravity.md`, side-effecting skills express restriction by instructing the model in the description to execute only upon explicit user request.
  - Claude `allowed-tools` is unsupported in Antigravity skill frontmatter and dropped (generates `S012` warning if present).
- **Untested behavior:** High-concurrency batch execution via `agy -p` in CI.

### `authoring-agents`
- **Mapping:** Implemented as `skills/authoring-agents/SKILL.md`. Generates `.agents/agents/<name>.md` with Antigravity-specific tool names and model tiers (`inherit`, `flash`, `pro`).
- **Lossy items:**
  - Claude `disallowedTools`, `permissionMode: bypassPermissions`, `color`, and `isolation: worktree`.
- **Untested behavior:** Deeply nested subagent calls exceeding 3 levels.

### `writing-project-instructions`
- **Mapping:** Implemented as `skills/writing-project-instructions/SKILL.md`. Canonical file is `AGENTS.md` (no frontmatter). Path-scoped rules map to `.agents/rules/*.md` using `trigger: glob` and `globs:`.
- **Lossy items:** Claude-specific `.claude/rules/*.md` format with `paths:`.
- **Untested behavior:** Automatic demotion of rules when exceeding the shared 20,000-token budget.

### `porting-artifacts`
- **Mapping:** Implemented as `skills/porting-artifacts/SKILL.md`. Uses `<!-- stablehand-lint: ignore S024 -->` to permit necessary cross-platform tool references in explanations.
- **Lossy items:** None in the skill itself.
- **Untested behavior:** Automatic conversion of non-standard vendor MCP server definitions.

### `evaluating-artifacts`
- **Mapping:** Implemented as `skills/evaluating-artifacts/SKILL.md`. Behavior testing runs through `scenario-runner` subagent; trigger testing uses `agy -p "<prompt>" --output-format json`.
- **Lossy items:** Packaged suite runner (`claude plugin eval`) is Claude-only; Antigravity relies on deterministic eval scenarios + real-loader prompt checks.
- **Untested behavior:** Automated parsing of `agy -p` output on older versions (< 1.2.0).

### `validating-artifacts`
- **Mapping:** Implemented as `skills/validating-artifacts/SKILL.md`. Script is vendored by `tools/sync.py` into `scripts/lint.py`.
- **Lossy items:** Claude `allowed-tools: Bash(uv run *)` dropped.
- **Untested behavior:** Execution on environments lacking `uv` using bare Python 3.11 with global PyYAML.

### Agents (`artifact-reviewer`, `scenario-runner`, `platform-researcher`)
- **Mapping:**
  - `artifact-reviewer.md`: read-only tools (`view_file`, `grep_search`, `find_by_name`, `list_dir`), `model: inherit`.
  - `scenario-runner.md`: full working toolset (`view_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `list_dir`, `find_by_name`, `grep_search`, `run_command`, `command_status`, `search_web`, `read_url_content`), `model: inherit`. Configured with `commandExecutionPolicy: sandbox` and `inheritCustomizations: false` to ensure test runs run isolated without polluting parent configurations.
  - `platform-researcher.md`: read-only tools + web tools (`search_web`, `read_url_content`, `view_file`, `grep_search`, `list_dir`, `find_by_name`), `model: flash`.
- **Lossy items:** Claude agent fields (`disallowedTools`, `permissionMode`, `color`, `effort`).
- **Untested behavior:** Subagent invocation on Antigravity IDE surfaces that lack custom subagent UI tabs.

---

## 3. Card Corrections (Resolved)

The observations noted regarding `shared/references/antigravity.md` were verified on the running live environment (agy 1.4.5, App 2.0.10, IDE 2.5.5) and applied to `shared/references/antigravity.md` and `tools/lint.py`:

1. **Observed vs Documented Tools (Section 5):**
   - *Status:* Verified and resolved.
   - *Evidence / Sources:* In active Antigravity IDE (VS Code fork) and runtime tool declarations, `find_by_name`, `list_dir`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `search_web`, and `read_url_content` are primary documented tools. Moved from `AG_TOOLS_OBSERVED` to `AG_TOOLS_DOCUMENTED` in `tools/lint.py` and updated in `shared/references/antigravity.md`.

2. **Workspace Boundaries for Commands (Section 1 & targets.md):**
   - *Status:* Verified and resolved.
   - *Evidence / Sources:* In the Antigravity IDE runtime, file-reading and file-writing tools operate freely across filesystem paths, but `run_command` strictly enforces workspace boundary checks (`Cwd must be within user's workspace`). External target execution requires adding the directory to the workspace (as a multi-root workspace folder) or running the harness from that external target directory directly via `agy -p`. Updated in `shared/references/antigravity.md` sections 1 and 5.

3. **Plugin Registration & Discovery (Section 6 & Testing):**
   - *Status:* Verified and resolved.
   - *Evidence / Sources:* `agy plugin install <path>` installs and enables the plugin globally into `~/.gemini/config/plugins/<name>`. For workspace isolation without modifying global state, linking `<target>/.agents/plugins/<name>` (via `uv run tools/install.py antigravity --scope workspace` or directory junction) enables discovery. Updated in `shared/references/antigravity.md` section 6.

---

## 4. Review & Refresh (2026-11-21)

Re-verified against live `https://antigravity.google/docs/*.md`, `https://antigravity.google/schemas/v1/plugin.json`, local `agy 1.5.5` (`--help`, `models`, `plugin validate`, `-p ... --output-format stream-json`), and local Antigravity IDE `2.7.0`:

1. **`disable-model-invocation` in skills:** Now documented for Antigravity plugins (`docs/build-plugins`), resolving the previous lossy gap in `authoring-skills` and `porting-artifacts`. Side-effecting skills now set `disable-model-invocation: true` while keeping "run only when explicitly requested" in `description` as defense-in-depth on older surfaces.
2. **Model tier `flash_lite`:** Now documented across `docs/build-plugins` and `docs/dynamic-workflows` alongside `inherit`, `flash`, and `pro`. Added to `shared/references/antigravity.md`, `tools/lint.py` (`AG_MODELS`), `authoring-agents`, `evaluating-artifacts`, `validating-artifacts`, and `porting-artifacts`.
3. **Canonical vs. model-facing tool names:** Gemini 4 / App 2.x prompts can expose model-facing aliases (`read_file`, `edit_file`, `write_file`), while custom agent `tools:` frontmatter, `hooks.json` matchers, and `agy --output-format stream-json` (`init.tools`) require canonical Cortex names (`view_file`, `replace_file_content`, `multi_replace_file_content`, `write_to_file`, `manage_task`). Replaced legacy `command_status` with `manage_task` in `scenario-runner.md` and `authoring-agents`, documented the expanded tool table in `shared/references/antigravity.md`, and added alias-hint error checking (`A031`) in `tools/lint.py`.
4. **`plugin.json` v1 schema & `assets/logo.svg`:** Upgraded `platforms/antigravity/plugin.json` to `https://antigravity.google/schemas/v1/plugin.json` (adding `$schema`, `displayName`, `logo`, `suggestedPrompts`, `author`, `homepage`, `repository`, `license`, `keywords`), created `assets/logo.svg`, and updated `tools/lint.py` to validate the full v1 schema and `.antigravity-plugin/plugin.json`.
5. **Headless trigger/delegation output format:** `agy -p ... --output-format json` only outputs a summary envelope without tool steps; switched real-loader trigger and delegation checks in `shared/references/antigravity.md`, `eval-protocol.md`, `targets.md`, skills, and `evals/*.md` to `--output-format stream-json` (NDJSON `step_update` events).
6. **Surfaces, CLI scopes, and rules:** Removed the outdated claim that Antigravity IDE stopped updating in 2026-08 (v2.8.0 is current; IDE extensions and `agy acp` added), clarified CLI-only skill folders (`~/.gemini/antigravity-cli/skills/`, `~/.gemini/skills/`), documented `.gemini/config.json` `personal_customization_dir`, `@[label](path)` vs `@filename` includes, and noted that CLI does not support `trigger: manual` `@`-mentions.
