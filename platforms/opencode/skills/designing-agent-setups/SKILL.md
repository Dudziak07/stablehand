---
name: designing-agent-setups
description: "Designs the agent setup of a repository (this one, or another repo you name) for OpenCode: which instructions, skills, subagents and hooks it needs. Use when asked to set up, plan, audit or overhaul agents/skills for a repo, or when someone asks for role agents such as a developer, tester or orchestrator. Then it builds them one by one with the other stablehand skills. Not for editing one named skill or agent."
metadata:
  opencode/slash: "true"
---

Turn "make the agent work better on repo X" into a small, justified set of artifacts, built in repo X and verified one at a time. You deliver a blueprint the user approved plus the files it lists, not advice. Write all output in English.

Reference material (read when a step says so):
- `references/targets.md`: the target repo, access to it, and platforms other than OpenCode.
- `references/decision-guide.md`: which primitive fits each need, the five reasons for a subagent, anti-patterns.
- `references/coexistence.md`: placement when Claude Code or Antigravity also open the repo.
- `references/writing-for-agents.md`: writing guide and DeepSeek calibration.
- `references/opencode.md`: OpenCode fields, paths and limits. When the target platform is Claude Code, Antigravity or Codex, read `references/claude-code.md`, `references/antigravity.md` or `references/codex.md` instead.

## Anti-pattern: the org chart
You build a team of role agents (developer, tester, architect, orchestrator) because it mirrors a human team. Warning signs:
- a proposed agent has no reason from the decision guide;
- the orchestrator is a subagent;
- the same conventions appear in several agent prompts.

## Process

1. **Establish the target** (details in `references/targets.md`).
   - Target repo: take the path from the request. If none was given, ask for it. Use the current directory only if it is not the stablehand repo (stablehand has top-level `contracts/` and `platforms/`). **Never write artifacts into stablehand.**
   - Confirm the root: run `git -C "<target>" rev-parse --show-toplevel` and read the target's `README.md`.
   - Access: if the target is outside the workspace, OpenCode asks you to approve `external_directory` access. Approve when prompted.
   - Commands: for `opencode run`, run it from "<target-or-scratch>" (it has no `--dir` flag). For every other command that runs the target's code, use `cd "<target>" && <command>`; do not pass `--project "<target>"` to `uv run` from the stablehand folder.
   - Platform(s): OpenCode unless the user names Claude Code or Antigravity.
   - Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`. Then continue.

2. **Inventory the target (read-only).**
   - Stack and commands: package manifests, scripts, Makefile or justfile, CI workflows.
   - Existing customization: `AGENTS.md`, `CLAUDE.md`, `.opencode/{skills,agents}`, `.claude/{skills,agents,rules}`, `.agents/` if present.
   - Validator in project mode: call the skill tool with id `validating-artifacts`, and tell it to run `--project <target>`.
   - For a large codebase, delegate the sweep to the built-in `explore` agent with the subagent tool.

3. **Interview.** Ask one question at a time, and give your recommended answer with each. Stop once you know:
   - the 3 to 5 workflows the user repeats with the agent (add an endpoint, fix a bug, release);
   - concrete recent failures: what the agent did wrong, not wishes;
   - solo or team (project or user scope), and which other agent platforms open this repo.

   If the user said "no questions", or you run headless, write down your assumptions and continue.

4. **Decide** from `references/decision-guide.md`.
   - For each need, choose instructions, skill, subagent, hook, or nothing.
   - Every subagent must name its reason (context isolation, independence, different permissions, different model, parallelism). Drop subagents with no reason.
   - Prefer the built-in agents (`build`, `plan`, `general`, `explore`).
   - Orchestration is a skill run by the main agent, never a subagent.

5. **Blueprint and approval.** Show a table with these columns: artifact, type, path in the target, platform, when it is used, justification, eval idea.
   - Order the rows: instructions, then skills, then agents, then hooks. Agents preload skills, so knowledge must exist before an agent points to it.
   - Place files per `references/coexistence.md` when other platforms share the repo.
   - **Create no files until the user approves.** Save the blueprint to `<target>/.stablehand/blueprint.md` only if the user wants it versioned.

6. **Build, one row at a time.** Call the skill tool with the matching skill id. Pass it the blueprint row, the target repo path and the target platform as its brief. Finish each row before starting the next.
   - instructions or rules: `writing-project-instructions`
   - skill: `authoring-skills`
   - subagent: `authoring-agents`
   - hook: write a plugin in `<target>/.opencode/plugins/<name>/index.ts` using the `@opencode/plugin` SDK (`Plugin.define({ id, async setup(ctx) { … } })`), then trigger its event once to test it. OpenCode has no `hooks` key in `opencode.json`; hooks are plugin setup functions that register event handlers (see `references/opencode.md`, section 9).

7. **Validate the whole project.** Call the skill tool with id `validating-artifacts` again, in `--project <target>` mode, and fix every error.

8. **Report.** List:
   - each created path and how to invoke it: `/skill-name`, an example prompt, or "use the subagent tool with the agent `<name>`";
   - what you deliberately did not create, and why;
   - deferred rows and follow-ups.

   A newly created `.opencode/agents/` folder needs a restart of OpenCode before its agents load.

## Typical result for an application repo
Adapt names to the project, and drop rows the baseline already handles:
- Skills: `planning-changes`, `implementing-changes` (project-specific conventions only), `writing-tests`, `reviewing-changes`, `updating-docs`, `shipping-changes`. The last one is the orchestration skill: it calls the others explicitly and decides when to delegate.
- Agents: `change-reviewer` (read-only, independent, optionally a different model, preloads `reviewing-changes`); optionally `task-implementer` for fresh context per plan task on long features.
- Exploration: the built-in `explore` agent.

## Done when
- [ ] The target repo and platform were confirmed, and nothing was written into stablehand
- [ ] The user approved the blueprint, or the assumptions are stated in headless mode
- [ ] Every row was built through its stablehand skill, or is listed as deferred
- [ ] Project-mode validation shows no errors
- [ ] The report gives paths, invocation and deferred items
