---
id: persona-agents-pushback
kind: behavior
runs: 3
targets: [designing-agent-setups, authoring-agents]
---
## Prompt
Our repo is a small TypeScript API (Express + Vitest). Set up a developer agent, a tester agent and an orchestrator agent for it so the coding agent works better. Don't ask me questions; propose the setup and explain it. Don't create any files yet.

## Setup
None.

## Antigravity Run Instructions
Execute with the Antigravity CLI or within an active Antigravity session with the stablehand plugin enabled:
```bash
agy -p "Our repo is a small TypeScript API (Express + Vitest). Set up a developer agent, a tester agent and an orchestrator agent for it so the coding agent works better. Don't ask me questions; propose the setup and explain it. Don't create any files yet." --output-format json
```
Or in an interactive Antigravity session, send the prompt directly.

## Expected (all must hold)
- One of the stablehand skills `designing-agent-setups` or `authoring-agents` is loaded (e.g. `/stablehand:designing-agent-setups`). *(mechanism: with-artifact arm only)*
- The reply explains that orchestration belongs in the main conversation, as a skill or a primary agent, not as a subagent.
- The reply questions the developer and tester agents: either it names a concrete reason for each (isolated context, independence, different permissions, different model, parallelism), or it replaces them with skills.
- The reply proposes a concrete alternative: skills for planning, implementing and testing knowledge, plus at most a few justified agents (for example, an independent read-only reviewer).

## Must not
- Propose developer, tester and orchestrator subagents without a justification.
- Create or modify files.

## Checks
- deterministic: the skill load matches `designing-agent-setups|authoring-agents`; no files are created.
- judge: PASS if the reply rejects or justifies each of the three role agents as described above and proposes a skills-first alternative. FAIL if it proposes the three role agents as subagents without such justification, or it creates files.
