---
id: port-reviewer-to-opencode
kind: behavior
runs: 3
targets: [porting-artifacts]
---

## Prompt
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

## Setup
None.

## Expected (all must hold)
- `porting-artifacts` is loaded.
- `.opencode/agents/code-reviewer.md` exists.
- Its frontmatter has `mode: subagent` and a `description`.
- Read-only is enforced through `permission`: `edit: deny`, and shell denied except `git diff` patterns.
- It has no `tools:` key (deprecated in OpenCode), no Claude tool names and no `name:` key.
- The model is omitted (inherit) or set to a `deepseek/...` ID. It is never `sonnet`.
- The final message lists lossy items (for example, `color` mapped or dropped) and gives a hand-off prompt for testing in OpenCode.

## Must not
- Copy the Claude frontmatter unchanged.
- Grant edit or unrestricted shell.

## OpenCode run
```
opencode run "<the Prompt above>" --format json --dir "<scratch-project>"
```

## Checks
- deterministic:
  - the file exists;
  - regex `mode:\s*subagent`;
  - regex `edit:\s*deny`;
  - the regex `^tools:` is absent;
  - the regex `model:\s*sonnet` is absent.
- judge: PASS if the agent is read-only by permission and the body keeps the review contract (ordered findings with file:line and a fix). FAIL otherwise.
