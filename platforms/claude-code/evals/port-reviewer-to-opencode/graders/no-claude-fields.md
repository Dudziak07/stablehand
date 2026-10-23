---
type: regex
pattern: '^(tools|name):|model:\s*sonnet'
flags: m
match: not_contains
target:
  source: file
  path: .opencode/agents/code-reviewer.md
---
