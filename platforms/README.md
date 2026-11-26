# Platforms

Each folder implements every contract in [`contracts/`](../contracts/) for one platform. The implementations behave the same and differ only in mechanics (fields, tool names, invocation, paths).

| Platform | Status | Contracts | Install |
|---|---|---|---|
| [claude-code](claude-code/) | ✅ reference implementation | 2026.11.1 | `uv run tools/install.py claude-code --scope workspace`, or the Claude plugin marketplace |
| [antigravity](antigravity/) | [✅ implemented (evals: 3 runs)](antigravity/evals/RESULTS.md) | 2026.11.1 | `uv run tools/install.py antigravity --scope workspace` |
| [opencode](opencode/) | [✅ implemented (evals: 3 runs)](opencode/evals/RESULTS.md) | 2026.11.1 | `uv run tools/install.py opencode --scope workspace` |
| [codex](codex/) | [✅ implemented (evals: 3-scenario batch)](codex/evals/RESULTS.md) | 2026.11.1 | `uv run tools/install.py codex --scope workspace` |

**Main flow:** open the stablehand repo in your tool and ask for a skill or agent for repository X. `--scope workspace` links the implementation into this checkout's own platform folders (gitignored), so the skills load as soon as the folder is opened.

## How a port is made

Each platform's own agent ports stablehand to that platform. It can run and test the result there, and it knows its platform's dialect.

1. Open the stablehand repo in the target platform.
2. Paste the prompt from `platforms/<p>/BOOTSTRAP.md`.
3. The agent implements every contract using the shared references, runs `uv run tools/sync.py` and the linter, translates `evals/scenarios/` into its own runner, and writes `PORT-NOTES.md`.
4. Review the result. Ideally, a different platform's agent cross-reviews it against the contracts.
5. Update the status row above.

## Adding a new platform

See [docs/adding-a-platform.md](../docs/adding-a-platform.md).
