---
type: llm
weight: 2
---

Judge the conversation's final message, together with the file content shown in the trace.

PASS if all of the following hold:
- the ported agent stays read-only through OpenCode `permission` rules: edits denied, and shell denied except `git diff`-style commands;
- its body keeps the review contract: findings as a numbered list ordered by severity, each with file:line and a concrete fix;
- the final message lists what could not be carried over, or how `color` and `model` were mapped;
- the final message gives a prompt or instructions for testing the agent inside OpenCode.

FAIL if edits or unrestricted shell are allowed, if the review contract is lost, or if the port is presented as tested.
