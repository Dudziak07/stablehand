---
name: authoring-agents
description: "Creates or improves one subagent or custom agent for a repository and platform (Antigravity by default; Claude Code or OpenCode on request), only when justified by one of the five reasons: isolated context, independence, different permissions, a different model or parallelism. Use when asked to create, design, fix or debug an agent or role agent (reviewer, researcher). Not for orchestrators, knowledge skills or porting."
---

A subagent is a separate worker with its own context, tools and model. Build one only when that separation is the point. Everything else is a skill.

Reference material (read when a step says so):
- `references/targets.md`: establishing the target repository and access outside the workspace.
- `references/decision-guide.md`: the five reasons for a subagent and role anti-patterns.
- `references/writing-for-agents.md`: drafting concise agent prompts, least privilege, and benchmark tasks.
- `references/eval-protocol.md`: benchmark scenario formats and the decision rule.
- `references/coexistence.md`: agent placement when multiple platforms share a repository.
- `references/antigravity.md`: Antigravity agent frontmatter, exact tool names, model tiers, and delegation mechanics.
- `references/claude-code.md`: Claude Code conventions when authoring for Claude Code.
- `references/opencode.md`: OpenCode conventions when authoring for OpenCode.

## Anti-pattern: the persona agent
You create a "developer", "tester" or "architect" agent because the user named a role. Warning signs:
- you cannot state which of the five reasons applies;
- the agent's prompt is mostly project knowledge;
- the orchestrator is a subagent.

## Process

0. **Target** (details in `references/targets.md`).
   - **Target repository.** Take it from the request; ask if missing. Use the current directory only if it is not the stablehand repo. **Never write the agent into stablehand.**
   - **Access & Workspace.** `run_command` in Antigravity requires `Cwd` to be within the active workspace. When running commands in the target, ensure the target folder is added to the workspace (multi-root workspace in Antigravity IDE) or launch `agy` from the target folder.
   - **Target platform.** Antigravity by default. For **Claude Code or OpenCode**:
     - write the file from that platform's card: folder, fields, valid tool names or permissions, model tiers;
     - validate with `--platform <target>`;
     - skip local runs in step 5, but write the benchmarks;
     - hand off a ready-to-paste prompt to run benchmarks on the target platform.
   - **Confirmation.** Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Justify.**
   - State the reason(s) explicitly: context isolation, independence, different permissions, a different model, or parallelism (`references/decision-guide.md`).
   - Check built-in subagents first (`research`, `browser`).
   - If no reason applies, state so plainly, then invoke `/stablehand:authoring-skills` or read its `SKILL.md` to build a skill instead.
   - If the user insists on a persona agent, explain the context overhead and duplication cost. Propose the thin variant: an agent whose prompt defines only role, procedure, and output format, preloading knowledge from `skills`.
   - Orchestration belongs in the main thread (primary agent or skill), never in a subagent.

2. **Contract.** Write down before drafting:
   - **Responsibility:** one clear sentence.
   - **Description:** when the planner should delegate. Use clear trigger phrases.
   - **Inputs:** what the caller must pass in the delegation prompt (the agent starts with no prior history).
   - **Output format:** an exact structured template. Only the final message returns.
   - **Tools (least privilege):**
     - Reviewer: read-only (`view_file`, `grep_search`, `find_by_name`, `list_dir`). Grant no write tools and no unrestricted shell. If the review role needs read-only commands (e.g. `git diff --staged`), allow read-only commands only through enforcement: a `PreToolUse` hook in `hooks.json` with a strict regex that rejects everything else, or an exact allow-list whose patterns cannot admit writing flags such as `--output`.
     - Researcher: read-only plus web (`search_web`, `read_url_content`, `view_file`, `grep_search`, `list_dir`, `find_by_name`).
     - Worker: add edit and execution tools (`replace_file_content`, `multi_replace_file_content`, `write_to_file`, `run_command`, `command_status`).
     - Use ONLY tool names from `references/antigravity.md` section 5. An unknown tool name can hang the agent.
   - **Model:** `inherit` by default; `flash` for fast sweeps; `pro` for complex reasoning.
   - **Benchmarks:** 3–5 tasks with expected outputs, saved in `<target>/.stablehand/evals/agents/<name>/scenarios/`.

3. **Draft** `<target>/.agents/agents/<name>.md` (or workspace plugin `<target>/.agents/plugins/<set>/agents/<name>.md` per `references/coexistence.md`).
   - Frontmatter: `name`, `description` (double-quoted), `tools`, `model`, `subagent: true`, `mainAgent: false`, and optional `skills:` (list of paths relative to the agent file used to preload domain knowledge).
   - Body skeleton (under ~150 lines):
     - role and objective;
     - inputs expected from caller;
     - numbered procedure;
     - exact output template;
     - constraints and stop conditions.

4. **Validate.**
   Determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from the directory containing this `SKILL.md`. Run:
   `uv run "<absolute-path-to-scripts/lint.py>" --platform antigravity "<agent-file>"`
   or invoke `/stablehand:validating-artifacts`. Resolve all errors.

5. **Test.**
   - Prepare a scratch copy or git worktree of the target repository (never run tests in the live target checkout or stablehand). Ensure it is added to the workspace if running commands in-session.
   - **Benchmarks:** run each benchmark with explicit delegation using `invoke_subagent` or:
     `agy -p "Use the <name> agent to: <task>" --output-format json` (started in the scratch copy or worktree).
     Compare against expected outputs.
   - **Auto-delegation:** test 2 natural prompts via real loader:
     `agy -p "<prompt>" --output-format json` (started in the scratch copy or worktree).
     Verify that the output records delegation to `<name>`.
   - Clean up the scratch copy or worktree afterwards.
   - Iterate at most 3 times and record `<target>/.stablehand/evals/agents/<name>/results/<date>.md`.

6. **Independent review.** Delegate to `artifact-reviewer` using `invoke_subagent`. Pass:
   - the agent file and the contract;
   - absolute paths to the **target** platform's card (`references/antigravity.md`, `references/claude-code.md`, or `references/opencode.md`) and `references/writing-for-agents.md` inside this skill's folder.
   Fix blocking findings. Tell the user about any you disagree with.

7. **Hand over:** file path, stated justification, how to invoke the agent (`invoke_subagent` or `@<name>`), benchmark results, and reload instructions. For another target platform, deliver the hand-off prompt and mark the hand-over "untested on <platform>".

## Done when
- [ ] The agent is in the target repository, in the target platform's folder, and nothing was written into stablehand
- [ ] The justification is explicitly stated from the five reasons
- [ ] The validator reports zero errors
- [ ] The benchmarks satisfy the decision rule and automatic delegation was verified. For another target platform, the hand-off prompt is delivered and the hand-over says "untested on <platform>".
- [ ] The reviewer has no open blocking findings
- [ ] The user approved the agent
