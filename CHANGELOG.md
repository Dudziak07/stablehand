# Changelog

stablehand uses calendar versioning, `YYYY.M.N` (see [contracts/README.md](contracts/README.md#versioning)).

## 2026.11.0

Antigravity platform refresh (verified 2026-11-21 against App 2.34.0, IDE 2.8.0 / 2.7.0 local, CLI `agy` 1.5.14 / 1.5.5 local, and Gemini 4 Neon), linter upgrades, and maintainer self-check tooling.

- **Antigravity platform card & implementation (`shared/references/`, `platforms/antigravity/`):**
  - documented `disable-model-invocation: true` for user-invoked skills and `flash_lite` subagent tier (alongside `inherit`, `flash`, `pro`), updating `porting-artifacts` across all three platforms;
  - updated canonical Cortex tool list (`manage_task`, `schedule`, `send_message`, `manage_subagents`, `ask_question`, `generate_image`, `call_mcp_tool`, `run_workflow`, `list_permissions`, `ask_permission`), replaced legacy `command_status` with `manage_task` in `scenario-runner` and `authoring-agents`, and added explicit warnings against copying model-facing aliases (`read_file`, `edit_file`, `write_file`) into agent `tools:`;
  - upgraded `platforms/antigravity/plugin.json` to the official `v1` schema (`https://antigravity.google/schemas/v1/plugin.json`) with bundled `assets/logo.svg`, `displayName`, `suggestedPrompts`, `author`, `homepage`, `repository`, `license`, and `keywords`;
  - switched headless real-loader trigger/delegation commands across `antigravity.md`, `eval-protocol.md`, `targets.md`, skills, and `platforms/antigravity/evals/` to `--output-format stream-json` (NDJSON `step_update` events);
  - refreshed surfaces (`IDE` 2.8.0, IDE extensions, `agy acp`, Python SDK), built-in multi-agent orchestrators (`/run-workflow`, `/swarm`, `/boost`, `/teamwork`), CLI `--add-dir` / `/add-dir`, `SessionStart` hooks, `.gemini/config.json` `personal_customization_dir`, `@[label](path)` vs `@filename` includes, and CLI `auto` mode/sandbox notes;
  - added `antigravity.google/llms.txt` and `.md` page mirror pointers to `platform-researcher` across all three platforms.
- **Linter & tests (`tools/lint.py`, `tools/tests/test_lint.py`):**
  - added Antigravity support for `flash_lite`, `disable-model-invocation`, expanded documented tools, explicit `A031` error hints for model-facing aliases (`read_file`, `edit_file`, `write_file`), `.antigravity-plugin/plugin.json` precedence, and full `v1` `plugin.json` manifest validation (`M003`/`M004`);
  - updated `P002` deprecation wording for legacy workflows and added unit tests covering the new checks and shipped platform cleanliness.
- **Maintainer self-check (`.agents/skills/auditing-stablehand/`):**
  - added a repo-local, cross-platform self-check skill and `scripts/self_check.py` runner verifying sync, tool tests, card freshness, artifact linters, contract parity, version consistency, and native plugin validators.

## 2026.10.1

Fixes from the pre-release reviews on Antigravity and OpenCode.

- **`authoring-skills`:** when the baseline already passes, a skill is kept only on the user's explicit override. The results file and the hand-over then say "kept on user override, no measured gain".
- **`authoring-skills` and `authoring-agents`:** after fixing the reviewer's findings, the reviewer runs once more and its final verdict is recorded.
- **Antigravity:**
  - `agy --add-dir` documented for the CLI workspace;
  - `/skills` and `agy plugin list` do not show workspace plugin skills, so the install hint now points to `agy plugin validate`.
- **OpenCode:**
  - Windows PowerShell blocks the `opencode.ps1` and `pnpm.ps1` shims, so the docs point to `opencode.cmd` or `RemoteSigned`;
  - `opencode run --agent` selects only primary agents;
  - headless runs need a follow-up `--continue` to approve the plan;
  - a results claim about `git status` is corrected.

## 2026.10.0

First release.

- **Seven skills:** `designing-agent-setups`, `authoring-skills`, `authoring-agents`, `writing-project-instructions`, `porting-artifacts`, `evaluating-artifacts`, `validating-artifacts`.
- **Three agents:** `artifact-reviewer`, `scenario-runner`, `platform-researcher`.
- **Three platforms**, each implementing the same contracts:
  - Claude Code, the reference implementation, packaged as a plugin with a marketplace entry;
  - Google Antigravity (App, IDE, `agy` CLI), packaged as a plugin;
  - OpenCode, with DeepSeek model presets.
- **Evaluations.** Shared scenarios and trigger sets, translated per platform. Antigravity and OpenCode ran 3 runs per arm; see `platforms/*/evals/RESULTS.md`.
- **Tools:**
  - `lint.py`: a static linter for skills, agents, rules and instruction files on all three platforms, with cross-platform collision checks and a freshness check for platform cards;
  - `sync.py`: copies shared knowledge into each platform;
  - `install.py`: workspace, project and user scopes, with link or copy and a clean uninstall.
- **Platform findings built in:**
  - OpenCode 1.19 enforces shell restrictions only under the `bash` permission key, so stablehand writes `bash` and `shell` together (lint rule A049);
  - Antigravity's `run_command` requires the target folder to be in the workspace;
  - an unconfined baseline can find stablehand on the host, so such comparisons are reported as inconclusive.
