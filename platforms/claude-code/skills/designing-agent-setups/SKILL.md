---
name: designing-agent-setups
description: "Designs the agent setup of a repository (this one, or another repo the user names): which instructions, skills, subagents and hooks it needs on Claude Code, Antigravity or OpenCode. Then it builds them one by one with the other stablehand skills. Use when asked to set up, plan, audit or overhaul agents/skills for a repo, or when someone asks for role agents such as a developer, tester or orchestrator agent. Not for editing one named skill or agent."
argument-hint: "[target repo path] [platform]"
---

Turn "make the agent work better on repo X" into a small, justified set of artifacts, built in repo X and verified one at a time. You deliver a blueprint the user approved plus the files it lists, not advice.

Reference material (read when a step says so):
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: the target repo, access to it, and platforms other than Claude Code.
- `${CLAUDE_PLUGIN_ROOT}/references/decision-guide.md`: which primitive fits each need, the five reasons for a subagent, anti-patterns.
- `${CLAUDE_PLUGIN_ROOT}/references/coexistence.md`: placement when Antigravity or OpenCode also open the repo.
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`: file locations, fields and limits. For other target platforms, use `antigravity.md` or `opencode.md` in the same folder instead.

## Anti-pattern: the org chart
You build a team of role agents (developer, tester, architect, orchestrator) because it mirrors a human team. Warning signs:
- a proposed agent has no reason from the decision guide;
- the orchestrator is a subagent;
- the same conventions appear in several agent prompts.

## Process

1. **Establish the target** (details in `targets.md`).
   - **Target repo.** Take the path from `$ARGUMENTS` or the request; if none was given, ask for it. Use the current directory only if it is not the stablehand repo (stablehand has top-level `contracts/` and `platforms/`). **Never write artifacts into stablehand.**
   - **Access.** If the target is outside the current working directory, ask the user to run `/add-dir <path>` (or restart with `claude --add-dir <path>`) before reading it.
   - **Platform(s).** Claude Code unless the user names Antigravity or OpenCode.
   - **Root.** Confirm the repository root: the git root (`git -C <path> rev-parse --show-toplevel`) and its README.
   - Confirm in one line: target path, platform(s), goal.

2. **Inventory the target (read-only).**
   - Stack and commands: package manifests, scripts, Makefile/justfile, CI workflows.
   - Existing customization: `CLAUDE.md`, `AGENTS.md`, `.claude/{skills,agents,rules,settings.json}`, and `.agents/`, `.opencode/` if present.
   - Run the validator in project mode:
     `uv run "${CLAUDE_PLUGIN_ROOT}/skills/validating-artifacts/scripts/lint.py" --project <target>`
   - For a large codebase, delegate the sweep to the built-in `Explore` agent and ask it for commands, conventions and hotspots.

3. **Interview.** Ask one question at a time and give your recommended answer with each. Stop once you know:
   - the 3–5 workflows the user repeats with the agent (add an endpoint, fix a bug, release…);
   - concrete recent failures: what the agent did wrong, not wishes;
   - solo or team (project vs user scope), and which other agent platforms open this repo.

   If the user said "no questions", or you run headless, write down your assumptions and continue.

4. **Decide.** Read `decision-guide.md`.
   - For each need, pick instructions, skill, subagent, hook, or nothing.
   - Every subagent must name its reason (context isolation, independence, different permissions, different model, parallelism). Drop subagents with no reason.
   - Prefer the built-ins (`Explore`, `Plan`, `general-purpose`).
   - Orchestration is a skill run by the main agent, never a subagent.

5. **Blueprint and approval.** Show a table with these columns: artifact · type · path in the target · platform · when it is used · justification · eval idea.
   - Order the rows: instructions → skills → agents → hooks. Agents preload skills, so knowledge must exist before an agent points to it.
   - Place files per `coexistence.md` if other platforms share the repo.
   - **Create no files until the user approves.** Save the blueprint to `<target>/.stablehand/blueprint.md` only if the user wants it versioned.

6. **Build, one row at a time.** Use the Skill tool to load the matching stablehand skill. Pass it the blueprint row, the target repo path and the target platform as its brief. Finish each row before starting the next.
   - instructions or rules → `stablehand:writing-project-instructions`
   - skill → `stablehand:authoring-skills`
   - subagent → `stablehand:authoring-agents`
   - hook → write it into the target's `.claude/settings.json` (Antigravity: `.agents/hooks.json`) directly, and test it by triggering its event once.

7. **Validate the whole project.** Run the project-mode command from step 2 again and fix every error.

8. **Report.** List:
   - each created path and how to invoke it (`/skill-name`, an example prompt, or `@"agent-name (agent)"`);
   - what you deliberately did not create, and why;
   - deferred rows and follow-ups.

   A newly created `.claude/agents/` directory needs a session restart before its agents load.

## Typical result for an application repo
Adapt names to the project and drop rows the baseline already handles:
- **Skills:** `planning-changes`, `implementing-changes` (project-specific conventions only), `writing-tests`, `reviewing-changes`, `updating-docs`, `shipping-changes`. The last one is the orchestration skill: it calls the others explicitly and decides when to delegate.
- **Agents:**
  - `change-reviewer`: read-only, independent, optionally a different model; preloads `reviewing-changes`.
  - `task-implementer`: optional; fresh context per plan task on long features.
- **Exploration:** the built-in `Explore` agent.

## Done when
- [ ] The target repo and platform were confirmed, and nothing was written into stablehand
- [ ] The user approved the blueprint, or assumptions are stated in headless mode
- [ ] Every row was built through its stablehand skill, or is listed as deferred
- [ ] Project-mode validation shows no errors
- [ ] The report gives paths, invocation and deferred items
