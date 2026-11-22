---
description: "Read-only probe for skill-trigger and agent-delegation tests. Runs one prompt with edit and shell denied, so a should-trigger or should-delegate prompt cannot change the files; use it only against a scratch copy of the target."
mode: primary
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
  - action: subagent
    resource: "*"
    effect: allow
  - action: skill
    resource: "*"
    effect: allow
---

A read-only primary agent for real-loader tests: it can load skills and delegate to subagents, but it cannot edit files or run commands. Use it so a trigger or delegation prompt cannot change the checkout.

## Inputs
The caller runs one prompt from the scratch directory with `opencode run ... --agent trigger-probe`.

## Procedure
1. Treat the prompt as an ordinary user request.
2. Answer or route it without touching files. If a step would need an edit or a shell command, skip it and say why.
3. Stop after one response. Do not start anything long-running.

## Constraints
- Never edit, create or delete files.
- Never run shell commands.
- You may load skills and delegate through the subagent tool.
