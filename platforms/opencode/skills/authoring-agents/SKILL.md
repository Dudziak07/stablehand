---
name: authoring-agents
description: "Creates or improves one subagent/custom agent for a given repository and platform (OpenCode by default; Claude Code or Antigravity on request), but only when an agent is warranted: isolated context, independence, different permissions, a different model or parallel work. Use when someone needs an agent for this or another repo, or asks to create, fix or debug one, including role agents (developer, tester, reviewer). Not for orchestrators, knowledge (skills) or porting."
metadata:
  opencode/slash: "true"
---

A subagent is a separate worker with its own context, permissions and model. Build one only when that separation is the point. Everything else is a skill. Write all output in English.

Reference material:
- `references/targets.md`: the target repo, access to it, and target platforms other than OpenCode.
- `references/decision-guide.md`: the five reasons and the anti-patterns.
- `references/opencode.md`, sections 3 and 4: fields, permissions, model tiers, delegation. When the target platform is Claude Code or Antigravity, read `references/claude-code.md` or `references/antigravity.md` instead.
- `references/writing-for-agents.md`: the "Agent prompts" section.
- `references/eval-protocol.md`: benchmark format and the decision rule.
- `references/coexistence.md`: placement when other platforms open the repo.

## Anti-pattern: the persona agent
You create a "developer", "tester" or "architect" agent because the user named a role. Warning signs:
- you cannot state which of the five reasons applies;
- the agent's prompt is mostly project knowledge;
- the orchestrator is a subagent.

## Process

0. **Target** (details in `references/targets.md`).
   - Target repo: take it from the request. If it is missing, ask. Use the current directory only if it is not the stablehand repo. **Never write the agent into stablehand.**
   - Access: if the target is outside the workspace, approve the `external_directory` prompt.
   - Commands: for `opencode run`, run it from "<target-or-scratch>" (it has no `--dir` flag). For every other command that runs the target's code, use `cd "<target>" && <command>`; do not pass `--project "<target>"` to `uv run` from the stablehand folder.
   - Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.
   - Target platform: OpenCode by default. For **Claude Code or Antigravity**:
     - write the file from that platform's card: the folder, the fields, the model values, and the permission model (OpenCode `permissions` replaces a tools list);
     - validate with `--platform <target>`;
     - skip the runs in step 5, but still write the benchmarks;
     - end with a ready-to-paste prompt that runs them on the target platform.

1. **Justify.**
   - Name the reason(s): context isolation, independence, different permissions, different model, parallelism.
   - Check the built-in agents first (`build`, `plan`, `general`, `explore`).
   - If no reason applies, say so plainly, then call the skill tool with id `authoring-skills` and build a skill instead.
   - If the user insists on a persona agent, explain the cost: context loss at hand-off, and duplicated knowledge. Then offer the thin variant: an agent whose prompt is only role + procedure + output format, which preloads the knowledge skills.
   - Orchestrators are never subagents. Propose an orchestration skill, or a `mode: primary` agent.

2. **Contract.** Write these down before drafting:
   - Responsibility: one sentence.
   - Description (the delegation trigger): when the main agent should hand off. Add "Use proactively when ..." only if automatic delegation is wanted.
   - Inputs: what the caller must pass in the delegation prompt. The agent starts with no conversation history.
   - Output format: an exact template. Only the final message returns, so make it compact and structured.
   - Permissions, least privilege:
     - start from read-only: deny `edit`, `shell`, `webfetch`, `websearch` and `subagent` via `permissions`, unless the source explicitly allowed one of them;
     - add `edit: allow`, or an exact shell allow-list, only when the job writes or runs something;
     - use the V2 `shell` action (the `bash` name is deprecated);
     - keep every shell pattern exact. A trailing wildcard such as `git diff*` or `git log *` also admits `--output=<file>`, which writes a file;
     - reviewers and researchers stay read-only.
   - Model: omit it to inherit the caller. Set `deepseek/deepseek-flash` for cheap sweeps and `deepseek/deepseek-v4-pro` for hard judgment. Always include the provider prefix.
   - Skills to preload: knowledge lives in skills, not in the prompt. List them in the body as "call the skill tool with id `<id>`".
   - Isolation and permissions: OpenCode agents run in the main workspace. Give a scratch working directory to agents that edit in parallel, and never grant broader permissions than the job needs.
   - Benchmarks: 3 to 5 tasks with expected results, saved in `<target>/.stablehand/evals/agents/<name>/scenarios/`. Never put them under `.opencode/agents/`.

3. **Draft** `<target>/.opencode/agents/<name>.md` (project) or `~/.config/opencode/agents/<name>.md` (user).
   - Frontmatter: no `name` key (the file name is the agent ID), a double-quoted `description`, `mode: subagent`, and only the `permissions` and `model` fields the contract needs. Do not use the deprecated `tools` key.
   - Body, under about 150 lines:
     - role and goal (2 to 3 lines);
     - inputs expected;
     - procedure (numbered);
     - output template;
     - constraints (what it must not do, when to stop and return).

4. **Validate.** Call the skill tool with id `validating-artifacts`, and tell it to check the agent file with `--platform opencode`. Fix every error.

5. **Test.**
   - Create an isolated working directory: if `git -C "<target>" status --porcelain` is empty, run `git -C "<target>" worktree add "<scratch>" HEAD`; otherwise copy the target to a scratch directory.
   - Install the drafted agent into the scratch: create `<scratch>/.opencode/agents/` and copy the agent file to `<scratch>/.opencode/agents/<name>.md`.
   - Install the probe into the scratch: copy `trigger-probe.md` into `<scratch>/.opencode/agents/`. Take it from the `agents/` folder beside the installed `skills/` folder (for a workspace install: `<stablehand>/.opencode/agents/trigger-probe.md`; in the checkout: `platforms/opencode/agents/trigger-probe.md`). Without this copy OpenCode cannot find the agent when `opencode run` starts in "<scratch>".
   - Verify both copies: `Get-ChildItem -Recurse "<scratch>/.opencode"` (or `find "<scratch>/.opencode" -type f`) lists the new agent and `agents/trigger-probe.md`.
   - Benchmarks: run each one against the scratch copy, delegating explicitly and using the bundled read-only probe:
     `opencode run "Use the <name> agent to: <task>" --format json --agent trigger-probe --model deepseek/deepseek-flash`
     Compare against the expected results.
   - Auto-delegation: run 2 natural prompts that do not name the agent, also against the scratch copy with the probe:
     `opencode run "<natural prompt>" --format json --agent trigger-probe --model deepseek/deepseek-flash`
     A pass is a `task` call that selects the agent. Delegation is not deterministic: if 1 of 2 prompts delegates, strengthen the description (natural phrasings, "use proactively") and re-run.
   - Iterate at most 3 times and save `results/<date>.md`.
   - Remove the worktree or scratch copy when done.

6. **Independent review.** Use the subagent tool with the agent `artifact-reviewer`. Pass:
   - the agent file and the contract;
   - the absolute paths of the **target** platform's card (`references/opencode.md`, `references/claude-code.md` or `references/antigravity.md` in this skill's folder) and of `references/writing-for-agents.md`.

   Fix blocking findings. After fixing, run the reviewer once more on the fixed artifact and record its final verdict in the results file.

7. **Hand over.** Use this template:
```
Path: <agent file>
Invoke: use the subagent tool with the agent <name>, or @<name>
Justification: <one or more of the five reasons>
Benchmark results: <table>
Restart needed: <yes or no>
```

## Common shapes
| Shape | Permissions | Model | Returns |
|---|---|---|---|
| Reviewer | deny `edit` and `shell` (an exact shell allow-list such as `"git diff --staged"` and `"git diff --staged -- *"` may be allowed); deny `webfetch`, `websearch` and `subagent` | inherit or a different tier | numbered findings by severity, each with file:line and a fix |
| Implementer | inherit, plus `edit: allow` and the test commands it needs | inherit | summary, changed files, test command and result |
| Researcher | deny `edit` and `shell`; allow `webfetch` and `websearch` | `deepseek/deepseek-flash` | sourced findings with URLs |

## Done when
- [ ] The agent is in the target repo (or user scope), in the target platform's folder, and nothing was written into stablehand
- [ ] The justification is stated (one or more of the five reasons)
- [ ] The validator reports no errors
- [ ] The benchmarks meet the decision rule and auto-delegation was checked. For another target platform, the hand-off prompt is delivered and the hand-over says "untested on <platform>"
- [ ] The reviewer has no open blocking findings
- [ ] The user approved the agent
