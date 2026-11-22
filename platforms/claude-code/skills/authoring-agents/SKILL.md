---
name: authoring-agents
description: "Creates or improves one subagent/custom agent for a given repository and platform (Claude Code by default; Antigravity or OpenCode on request), but only when an agent is warranted: isolated context, independence, different permissions, a different model or parallel work. Use when someone needs an agent for this or another repo, or asks to create, fix or debug one, including role agents (developer, tester, reviewer). Not for orchestrators, knowledge (skills) or porting."
argument-hint: "[target repo path] [what the agent should do]"
---

A subagent is a separate worker with its own context, tools and model. Build one only when that separation is the point. Everything else is a skill.

Reference material:
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: the target repo, access to it, and target platforms other than Claude Code.
- `${CLAUDE_PLUGIN_ROOT}/references/decision-guide.md`: the five reasons and the anti-patterns.
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`, sections 3–4: fields, tools, model tiers, delegation. For other target platforms, read `antigravity.md` (section 4–5) or `opencode.md` (sections 3–5) in the same folder instead.
- `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`: the "Agent prompts" section.
- `${CLAUDE_PLUGIN_ROOT}/references/eval-protocol.md`: benchmark format and the decision rule.

## Anti-pattern: the persona agent
You create a "developer", "tester" or "architect" agent because the user named a role. Warning signs:
- you cannot state which of the five reasons applies;
- the agent's prompt is mostly project knowledge;
- the orchestrator is a subagent.

## Process

0. **Target** (details in `targets.md`).
   - **Target repo.** Take it from the request or `$ARGUMENTS`; ask if it is missing. Use the current directory only if it is not the stablehand repo. **Never write the agent into stablehand.**
   - **Access.** If the target is outside the working directory, ask the user to run `/add-dir <path>` first.
   - **Target platform.** Claude Code by default. For **Antigravity or OpenCode**:
     - write the file from that platform's card: the folder, the fields, tool names from its tool table (an unknown Antigravity tool can hang the agent), the model values, and OpenCode `permission` instead of tools;
     - validate with `--platform <target>`;
     - skip the runs in step 5, but still write the benchmarks;
     - end with a ready-to-paste prompt that runs them on the target platform.
   - **Confirm** in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Justify.**
   - Name the reason(s): context isolation, independence, different permissions, different model, parallelism.
   - Check the built-ins first (`Explore`, `Plan`, `general-purpose`).
   - If no reason applies, say so plainly, then use the Skill tool to load `stablehand:authoring-skills` and build a skill instead.
   - If the user insists on a persona agent, explain the cost: context loss at hand-off, and duplicated knowledge. Then offer the thin variant: an agent whose prompt is only role + procedure + output format, with `skills:` preloading the knowledge.
   - Orchestrators are never subagents. Propose an orchestration skill, or `claude --agent <name>` for a main-thread agent.

2. **Contract.** Write these down before drafting:
   - **Responsibility:** one sentence.
   - **Description** (the delegation trigger): when the main agent should hand off. Add "Use proactively when …" only if automatic delegation is wanted.
   - **Inputs:** what the caller must pass in the delegation prompt. The agent starts with no conversation history.
   - **Output format:** an exact template. Only the final message returns, so make it compact and structured.
   - **Tools, least privilege.**
     - Start from `Read, Grep, Glob`.
     - Add `Edit`, `Write` or `Bash` only when the job writes or runs something. Restrict `Bash` with a frontmatter `PreToolUse` hook: a specifier such as `Bash(git diff *)` in `tools` restricts nothing.
     - Reviewers and researchers get no `Edit`/`Write`. A reviewer that must run read-only commands (`git diff --staged`) gets `Bash` only behind a hook that allows exactly those commands.
   - **Model:** `inherit` by default. Use `haiku` for cheap sweeps and `opus` for hard judgment. Don't pin full IDs: DeepSeek and other compatible endpoints remap or reject them.
   - **Skills to preload:** knowledge lives in skills, not in the prompt (max 32).
   - **Isolation and permissions:** `isolation: worktree` for agents that edit in parallel; `permissionMode` only when there is a reason, and never `bypassPermissions` without explicit approval.
   - **Benchmarks:** 3–5 tasks with expected results, saved in `<target>/.stablehand/evals/agents/<name>/scenarios/`. **Never put them under `.claude/agents/`**: that folder is scanned recursively.

3. **Draft** `<target>/.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md` (user).
   - Frontmatter: `name`, `description` (double-quoted), and only the fields the contract needs.
   - Body skeleton, under ~150 lines:
     - role and goal (2–3 lines);
     - inputs expected;
     - procedure (numbered);
     - output template;
     - constraints (what it must not do, when to stop and return).

4. **Validate.**
   `uv run "${CLAUDE_PLUGIN_ROOT}/skills/validating-artifacts/scripts/lint.py" --platform claude-code <agent-file>`
   Fix every error.

5. **Test.**
   - **Benchmarks:** run each one headless in the target repo, delegating explicitly:
     `cd "<target>" && claude -p "Use the <name> agent to: <task>" --output-format stream-json --verbose`
     Compare against the expected results. In-session delegation only sees the target's agents if the target is the working directory.
   - **Auto-delegation:** run 2 natural prompts that do not name the agent:
     `uv run "${CLAUDE_PLUGIN_ROOT}/skills/evaluating-artifacts/scripts/run_triggers.py" --repo "<target>" --agent <name> --should "<prompt 1>" --should "<prompt 2>"`
     A pass is an `Agent` call whose `subagent_type` is the name. Delegation is not deterministic: if 1 of 2 prompts delegates, strengthen the description (natural phrasings, "use proactively") and re-run.
   - If `claude` is not on PATH, ask the user for the CLI path; the IDE extensions bundle one.
   - Iterate at most 3 times and save `results/<date>.md`.

6. **Independent review.** Use the Agent tool with `subagent_type: "stablehand:artifact-reviewer"`. Pass:
   - the agent file and the contract;
   - the absolute paths of the **target** platform's card (`claude-code.md`, `antigravity.md` or `opencode.md` in `${CLAUDE_PLUGIN_ROOT}/references/`) and of `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`.

   Fix blocking findings. After fixing, run the reviewer once more on the fixed artifact and record its final verdict in the results file.

7. **Hand over:** update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`), then report the path, the stated justification, how to invoke the agent, the benchmark results, and any restart needed.

## Common shapes
| Shape | Tools | Model | Returns |
|---|---|---|---|
| Reviewer | `Read, Grep, Glob`, + `Bash` only behind a frontmatter `PreToolUse` hook that allows read-only commands (specifiers like `Bash(git diff *)` in `tools` do not restrict anything) | inherit or a different tier | numbered findings by severity, each with file:line and fix. Write fragile checks as mechanical steps ("grep every model field in the schema and the writers"), not as headings; a vague check gets skipped when there is no diff. |
| Implementer | inherit (or explicit edit + test commands), `isolation: worktree` when parallel | inherit | summary, changed files, test command + result |
| Researcher | `Read, Grep, Glob, WebSearch, WebFetch` | `haiku` / `sonnet` | sourced findings with URLs |

## Done when
- [ ] The agent is in the target repo (or user scope), in the target platform's folder, and nothing was written into stablehand
- [ ] The justification is stated (one or more of the five reasons)
- [ ] The validator reports no errors
- [ ] The benchmarks meet the decision rule and auto-delegation was checked. For another target platform, the hand-off prompt is delivered and the hand-over says "untested on <platform>".
- [ ] The reviewer has no open blocking findings
- [ ] The user approved the agent
