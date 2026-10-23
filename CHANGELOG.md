# Changelog

stablehand uses calendar versioning, `YYYY.M.N` (see [contracts/README.md](contracts/README.md#versioning)).

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
