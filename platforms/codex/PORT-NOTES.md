# Port notes: OpenAI Codex CLI

- **Date:** 2026-11-26
- **Codex CLI version:** `0.172.0` (`codex-cli 0.172.0`)
- **Smoke-test model:** `gpt-6-luna` (ChatGPT Free)

## Mapping decisions

- **Skills:** placed under `.agents/skills/<id>/SKILL.md` (project) and `~/.agents/skills/<id>/SKILL.md` (user) using standard `name` + `description` double-quoted frontmatter. Invocation in skill bodies uses `$<id>`.
- **Subagents:** mapped from Markdown frontmatter to standalone TOML files under `.codex/agents/<id>.toml` (project) and `~/.codex/agents/<id>.toml` (user) using `name`, `description`, `sandbox_mode`, `model_reasoning_effort`, `nickname_candidates`, and `developer_instructions`:
  - `artifact-reviewer.toml`: `sandbox_mode = "read-only"`, `model_reasoning_effort = "high"`.
  - `scenario-runner.toml`: `sandbox_mode = "workspace-write"`, `model_reasoning_effort = "medium"`.
  - `platform-researcher.toml`: `sandbox_mode = "read-only"`, `model_reasoning_effort = "low"`.
- **Instructions:** `AGENTS.md` and `AGENTS.override.md` (plain Markdown, no YAML frontmatter).
- **Linter (`tools/lint.py`):** added `codex` platform support with `tomllib`-based TOML agent validation (`A050`–`A056`, `A003`, `S024`), `AGENTS.override.md` detection, and `.codex/agents/*.toml` project scanning.
- **Installer (`tools/install.py`):** added `codex` support across `workspace`, `project`, and `user` scopes, linking each skill into `.agents/skills/<id>` (preserving `.agents/skills/auditing-stablehand` in workspace scope) and copying `.codex/agents/*.toml`, with manifest tracking in `.codex/.stablehand-install.json`.

## Lossy items

- Codex custom agents control permissions via `sandbox_mode` (`read-only`, `workspace-write`, `danger-full-access`) rather than per-command shell allow-lists or per-tool lists. Fine-grained tool/command restrictions from Claude Code or OpenCode cannot be expressed directly in `.toml` agent files and rely on `read-only` sandboxing.
- Codex skills do not use Claude's `disable-model-invocation` / `user-invocable` or OpenCode's `metadata.opencode/*` keys; invocation control is expressed in `description`.

## Smoke-test observations (`codex-cli 0.172.0`)

- Installed into a temporary scratch project via `uv run tools/install.py codex --scope project --project <scratch> --copy` and ran `"" | codex.cmd exec --ephemeral --trust --sandbox read-only --skip-git-repo-check -C <scratch> "..."`:
  - Loaded without any config or TOML parse errors (`exit 0`, model `gpt-6-luna`).
  - Discovered all 8 `.agents/skills/*/SKILL.md` skills and all 3 `.codex/agents/*.toml` custom agents.
- Negative-control check (`"What is 2 + 2? Reply with only the number."` via `--json`): exited `0`, returned `"4"`, and triggered no stablehand skills.
- **Observed Windows / headless gotchas:**
  - `codex.ps1` is blocked by default Windows PowerShell 5.1 `ExecutionPolicy`; use `codex.cmd` or `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
  - `codex exec` reads additional input from stdin and blocks if stdin stays open; pipe empty input (`"" | codex.cmd exec ...`) in non-interactive runners.
  - Project-local `.codex/` config in an untrusted directory requires `--trust`.

## Headless evals (`codex-cli 0.172.0`, `gpt-6-luna`) & Untested

- Executed a token-frugal 8-run headless eval batch (see [evals/RESULTS.md](evals/RESULTS.md)):
  - `unrelated-request-no-trigger`: **2/2 PASS** (0 stablehand skills loaded).
  - `persona-agents-pushback`: **0/2 -> 2/2 PASS** (outcome gain; loaded `designing-agent-setups`, kept orchestration in main-thread skill, justified roles via the five reasons).
  - `external-target-repo`: **1/1 placement & conventions** in both arms (no outcome gain over built-in `.system/skill-creator`: both created valid `shop-api/.agents/skills/adding-endpoints/SKILL.md` with repo conventions and zero root writes, and both missed explicitly stating the created skill is *untested*, scoring `0/1` under strict judge grading; with-artifact loaded `authoring-skills`, used double-quoted frontmatter, and attempted `validating-artifacts`).
- **Remaining untested:** `skill-for-migrations`, `agents-md-minimal`, `port-reviewer-to-opencode`, 3-run replicates per arm across all 6 scenarios, and custom subagent natural-prompt delegation benchmarks (can be run later across ChatGPT Free windows or with a BYOK provider in `~/.codex/config.toml`).
- **Additional Windows / headless gotchas:** `codex.cmd` is a `cmd.exe` batch wrapper, so multi-line prompts passed as CLI arguments get truncated at the first newline; pass single-line prompts in headless runners. Inside Codex's Windows sandbox, `uv run` against an external global cache (`Z:\Cache\uv\.lock`) fails with an access-denied lock error.
