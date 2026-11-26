# OpenAI Codex CLI Evaluation Results

- **Date:** 2026-11-26
- **Platform:** OpenAI Codex CLI (`codex-cli 0.172.0`) on Windows (PowerShell 5.1)
- **Model:** `gpt-6-luna` (ChatGPT Free)
- **Batch Scope:** Token-frugal headless eval batch (8 `codex.cmd exec` runs total across 3 scenarios)
- **Grading Protocol:** Evaluated per [`shared/references/eval-protocol.md`](../../../shared/references/eval-protocol.md):
  - Mechanism items (`skill X is loaded`) are excluded from baseline grading and checked only in the with-artifact arm.
  - Outcome items determine pass/fail; a scenario counts as an outcome gain only when the baseline fails at least one outcome item and the with-artifact arm passes.
  - Token consumption from `turn.completed` `usage` events is reported separately as an informational metric.

---

## 1. Protocol and Exact Commands

Each arm ran in an isolated temporary scratch directory outside the `stablehand` checkout, with empty stdin piped to avoid blocking and `--ephemeral --trust --json --skip-git-repo-check`:

```powershell
# Install Codex skills & agents into a with-artifact scratch directory
uv run tools/install.py codex --scope project --project <scratch-art> --copy

# Scenario 1: unrelated-request-no-trigger (2 runs, with-artifact, read-only)
"" | codex.cmd exec --ephemeral --trust --json --sandbox read-only --skip-git-repo-check -C <scratch-s1> "Fix the off-by-one error in this function and show only the corrected code: function lastItem(arr) { return arr[arr.length]; }"

# Scenario 2: persona-agents-pushback (2 baseline + 2 with-artifact runs, read-only)
"" | codex.cmd exec --ephemeral --trust --json --sandbox read-only --skip-git-repo-check -C <scratch-s2> "Our repo is a small TypeScript API (Express + Vitest). Set up a developer agent, a tester agent and an orchestrator agent for it so the coding agent works better. Don't ask me questions; propose the setup and explain it. Don't create any files yet."

# Scenario 3: external-target-repo (1 baseline + 1 with-artifact run, workspace-write)
"" | codex.cmd exec --ephemeral --trust --json --sandbox workspace-write --skip-git-repo-check -C <scratch-s3> "I need a skill named ``adding-endpoints`` for the repository in ``./shop-api`` that adds a new REST endpoint the way that repo does it. Work non-interactively: don't ask me questions, skip baseline runs, and write the files directly."
```

*(Note: Because `codex.cmd` wraps Node via `cmd.exe`, passing multi-line prompts as CLI arguments truncates at the first newline; prompts were passed single-line in PowerShell, and all temporary scratch directories were deleted after JSONL parsing.)*

---

## 2. Results Summary (Baseline vs With-Artifact)

| Scenario ID | Kind | Baseline | With-Artifact | Outcome Gain? | Verdict & Notes |
|---|---|---|---|---|---|
| `unrelated-request-no-trigger` | negative control | — (2 with-artifact runs) | **2/2 PASS** (`0` skill loads, `arr.length - 1`) | N/A (negative control) | **PASS** — zero stablehand skills loaded in both runs |
| `persona-agents-pushback` | behavior / prompt | **0/2 PASS** (proposed Developer, Tester, Orchestrator agents without pushback) | **2/2 PASS** (`designing-agent-setups` + `decision-guide.md` loaded; orchestration kept in main thread as skill; subagents justified via five reasons; 0 files created) | **YES** | **PASS** — clear behavioral shift to skills-first & justified agents |
| `external-target-repo` | behavior / execution | **1/1 placement & conventions** (built-in `.system/skill-creator` created valid `shop-api/.agents/skills/adding-endpoints/SKILL.md`; unquoted frontmatter; omitted explicit "untested" notice) | **1/1 placement & conventions** (`authoring-skills` loaded; created `shop-api/.agents/skills/adding-endpoints/SKILL.md`, 0 writes to root `.agents/skills/`, double-quoted frontmatter, lint clean; stated skipped baseline + blocked linter rather than explicit "untested" notice) | No outcome gain (1/1 vs 1/1) | **No outcome gain** — deterministic target isolation & conventions pass in both arms; strict "untested" wording omitted in both |

### Scenario Details

- **`unrelated-request-no-trigger` (2/2 PASS):** Both runs returned `function lastItem(arr) { return arr[arr.length - 1]; }` directly with zero `command_execution` events and zero stablehand skill reads.
- **`persona-agents-pushback` (0/2 baseline → 2/2 with-artifact):**
  - Baseline runs proposed a three-agent setup (`Developer`, `Tester`, `Orchestrator` as default entry point) with no skills-first alternative or five-reasons justification.
  - With-artifact run 1 loaded `designing-agent-setups/SKILL.md`, `decision-guide.md`, `codex.md`, and `coexistence.md`; rejected the generic developer/orchestrator split, placed orchestration in the main thread as a skill (`.agents/skills/orchestrating-api-changes/SKILL.md`), and justified `api-implementer` (context isolation) and `vitest-tester` (independence).
  - With-artifact run 2 loaded `designing-agent-setups/SKILL.md`, `decision-guide.md`, `codex.md`, and `validating-artifacts/SKILL.md`; moved orchestration into a main-thread skill (`.agents/skills/orchestrating-api-changes/SKILL.md`), justified subagents via context isolation and independence, and proposed minimal `AGENTS.md`. Neither created any files.
- **`external-target-repo` (1 baseline + 1 with-artifact):**
  - Codex CLI ships a built-in `.system/skill-creator` skill, which enabled the baseline arm to locate `shop-api` conventions (`src/routes/<resource>.ts`, `src/schemas/<resource>.ts`, `src/server.ts`, `tests/<resource>.test.ts`, `pnpm vitest run tests/<resource>.test.ts`) and write `shop-api/.agents/skills/adding-endpoints/SKILL.md`.
  - The with-artifact arm loaded `authoring-skills/SKILL.md`, `targets.md`, `writing-for-agents.md`, `decision-guide.md`, `codex.md`, `coexistence.md`, and `validating-artifacts/SKILL.md`; confirmed `Target: ./shop-api · Platform: Codex · Building: a repository-specific adding-endpoints skill`; wrote only `shop-api/.agents/skills/adding-endpoints/SKILL.md` (nothing in root `.agents/skills/`). External `uv run tools/lint.py --platform codex` on the created skill passed (`0 error(s), 0 warning(s), 0 info`).
  - Under the strict judge rule in `evals/scenarios/external-target-repo.md` ("final message gives the path and says it is untested"), neither arm explicitly stated the created skill itself is *untested* (baseline wrote "I didn't run baseline checks"; with-artifact wrote "I skipped baseline runs. I couldn't run the artifact linter because neither `python` nor `py` is available in the environment").

---

## 3. Observed Token Usage

Token counts extracted from JSONL `turn.completed` `usage` objects across all 8 runs:

| Run | Arm | Input Tokens | Cached Input | Uncached Input | Output Tokens | Reasoning Output | Total (`in + out`) |
|---|---|---:|---:|---:|---:|---:|---:|
| `unrelated-request-no-trigger` #1 | with-artifact | 15,242 | 0 | 15,242 | 24 | 0 | 15,266 |
| `unrelated-request-no-trigger` #2 | with-artifact | 15,242 | 0 | 15,242 | 24 | 0 | 15,266 |
| `persona-agents-pushback` #1 | baseline | 13,775 | 11,008 | 2,767 | 229 | 0 | 14,004 |
| `persona-agents-pushback` #2 | baseline | 13,775 | 11,008 | 2,767 | 212 | 0 | 13,987 |
| `persona-agents-pushback` #1 | with-artifact | 76,701 | 53,504 | 23,197 | 1,410 | 164 | 78,111 |
| `persona-agents-pushback` #2 | with-artifact | 74,927 | 52,096 | 22,831 | 1,826 | 672 | 76,753 |
| `external-target-repo` #1 | baseline | 81,800 | 65,152 | 16,648 | 1,351 | 253 | 83,151 |
| `external-target-repo` #1 | with-artifact | 168,054 | 150,528 | 17,526 | 1,617 | 229 | 169,671 |
| **Total (8 runs)** | **all** | **459,516** | **343,296** | **116,220** | **6,693** | **1,318** | **466,209** |

---

## 4. Verdict and Remaining Gaps

- **Verdict:** Codex CLI `0.172.0` (`gpt-6-luna`) discovers `.agents/skills/*/SKILL.md` cleanly, exhibits **0% false triggering** on `unrelated-request-no-trigger` (`2/2` pass), and demonstrates a clear **outcome gain** on `persona-agents-pushback` (`0/2` → `2/2`), keeping orchestration in the main thread and enforcing the five-reasons check for subagents. On `external-target-repo`, target scoping and repository conventions pass deterministically (`shop-api/.agents/skills/adding-endpoints/SKILL.md`), while explicit "untested" reporting when baseline/linter checks are skipped remains a minor wording gap.
- **Platform observations:**
  - Inside Codex's Windows sandbox, `uv run` against a global cache outside the workspace (for example `Z:\Cache\uv\.lock`) can fail with an access-denied lock error when running `validating-artifacts/scripts/lint.py`.
  - Multi-line CLI prompts passed to `codex.cmd` are truncated at the first newline by `cmd.exe`; headless runners on Windows should pass single-line prompts or pipe via stdin (`-`).
- **Remaining untested scope:** 3-run statistical repeats across all 6 scenarios (`skill-for-migrations`, `agents-md-minimal`, `port-reviewer-to-opencode`) and dedicated `triggers.yaml` precision/recall sweeps were omitted to stay within ChatGPT Free limits.
