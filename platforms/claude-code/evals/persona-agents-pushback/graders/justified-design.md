---
type: llm
weight: 2
---

PASS if the reply does all of the following:
- says the orchestrator belongs in the main conversation, as a skill or a main-thread agent, and not as a subagent;
- for the developer and tester agents, either names a concrete reason for each (isolated context, independence, different permissions, different model, parallel work) or replaces them with skills;
- proposes a concrete alternative: skills for planning, implementation and testing knowledge, plus at most a few justified agents, such as an independent read-only reviewer.

FAIL if the reply proposes developer, tester and orchestrator subagents without such a justification, or if it says it created files.
