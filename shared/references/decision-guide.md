# Choosing the right primitive

Read this before proposing any artifact. Default to the smallest primitive that changes behavior; default to *nothing* when the model already does the job (prove it with a baseline run).

## Primitive per need

| Need | Primitive | Why |
|---|---|---|
| Facts true for almost every task in the repo: build/test commands, non-obvious conventions, boundaries | **Project instructions** (AGENTS.md / CLAUDE.md / rules) | Always loaded, so every line costs context on every task. Keep only what the agent cannot infer from the code. |
| Facts that apply only to some paths (e.g. `migrations/**`) | **Path-scoped rule** (`.claude/rules` with `paths:`, Antigravity `trigger: glob`) | Loaded only when those files are touched. |
| A procedure or body of knowledge needed for some tasks (how we release, how we write tests here) | **Skill** | Loaded on demand. Composable. User-invocable as `/name` on every supported platform. |
| Work that needs its own context window, independence, different permissions, a different model, or parallel execution | **Subagent / custom agent** | See the five reasons below. Isolation has a price: no conversation history, only the final message comes back. |
| Something that must happen every time, deterministically (format after edit, block a dangerous command) | **Hook** | Instructions can be forgotten; hooks cannot. |
| A shortcut the user types | **Skill** (user-invoked) | Custom commands are legacy: Claude Code merged them into skills, Antigravity deprecated legacy Markdown workflows in favor of skills (Dynamic Workflows `/run-workflow` are Python orchestration scripts), OpenCode exposes skills as `/name`. |
| Access to an external system | **MCP server** | Out of scope for stablehand authoring, but list it in the blueprint when needed. |
| Nothing — the baseline already behaves well | **Nothing** | An artifact that changes nothing is pure context cost. |

## The five reasons for a subagent

Create a subagent only when at least one applies. Name the reason in the blueprint.

1. **Context isolation** — the work reads a lot (large search, logs, docs) and only a summary should come back; or a long task benefits from a fresh context per step.
2. **Independence** — a judgment must not inherit the author's reasoning (code review, spec compliance check, adversarial test design).
3. **Different permissions** — the role must be read-only, or must be allowed to do something the main session must not.
4. **Different model** — a cheaper/faster model for sweeps, a stronger one for hard judgment, or a different model family for a second opinion.
5. **Parallelism** — independent work items that can run at the same time.

If none applies, write a skill and let the main agent use it.

## Anti-patterns

- **The org chart.** Role agents (developer, tester, architect, PM) that mirror a human team. The main agent already *is* the developer; a "developer agent" only adds a hand-off that loses context.
- **The orchestrator subagent.** Orchestration must live in the main thread: it talks to the user and holds the plan, and nested delegation is limited on every platform. Make orchestration a skill (all platforms) or a primary agent (OpenCode `mode: primary`, Antigravity `mainAgent: true`, Claude Code `claude --agent`).
- **Knowledge inside agent prompts.** The same conventions pasted into several agents drift apart. Put knowledge in skills; agents load them.
- **The mega-skill.** One skill that covers planning, coding, testing and release. Split by trigger: if two parts would be invoked by different requests, they are different skills.
- **Procedures in always-loaded rules.** A 40-line release procedure in AGENTS.md costs context on every task. Move it to a skill and leave a one-line pointer if needed.
- **Duplicating built-ins.** Every platform ships a read-only exploration agent (Claude Code `Explore`, OpenCode `explore`/`scout`, Antigravity `research`) and a general worker. Do not rebuild them.

## Typical outcome for an application repository

Adapt the names to the project; drop rows the baseline already handles.

| Artifact | Type | Notes |
|---|---|---|
| Project instructions | instructions | Commands, conventions, boundaries. Under ~150 lines. |
| `planning-changes` | skill | Turns a request into a small plan with acceptance checks; asks the user questions, so it runs in the main thread. |
| `implementing-changes` | skill | Only the project-specific way of building things (layers, patterns, error handling). |
| `writing-tests` | skill | Project test conventions, fixtures, how to run a single test. |
| `reviewing-changes` | skill | The review checklist; used by the main agent *and* preloaded by the reviewer agent. |
| `updating-docs` | skill | Where docs live and what must change with code. |
| `shipping-changes` | skill (orchestration) | Sequences plan → implement → test → review → docs, calls the other skills explicitly, and decides when to delegate. Runs in the main thread. |
| `change-reviewer` | agent | Reasons 2 + 3 (+ optionally 4): independent, read-only, may use a different model. Preloads `reviewing-changes`. |
| `task-implementer` | agent (optional) | Reason 1: fresh context per plan task on long features. Preloads `implementing-changes` and `writing-tests`. |
| Exploration | built-in | Use the platform's built-in explorer. |
