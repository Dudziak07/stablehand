---
description: A Claude agent becomes an idiomatic, still read-only OpenCode agent (evals/scenarios/port-reviewer-to-opencode.md).
tags: [porting-artifacts]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Port this Claude Code agent to OpenCode (we run OpenCode with DeepSeek). Write the result to `.opencode/agents/code-reviewer.md`. Work non-interactively.

```markdown
---
name: code-reviewer
description: "Independent read-only reviewer for staged changes. Use proactively after code changes, before committing."
tools: Read, Grep, Glob, Bash(git diff *)
model: sonnet
color: purple
---
You review the staged diff (`git diff --staged`). Report bugs, missing tests and security problems as a numbered list ordered by severity, each with file:line and a concrete fix. Never edit files.
```
