---
name: designing-agent-setups
description: "Designs the agent setup for a repository: which instructions, skills, subagents and hooks it needs on Antigravity, Claude Code or OpenCode. Then it builds them one by one with the other stablehand skills. Use when asked to set up, plan, audit or overhaul agents and skills for a repository, or when asked for role agents (developer, tester, orchestrator). Not for authoring or fixing one named skill or agent, general coding tasks, or platform reference questions."
---

Turn "make the agent work better on repo X" into a small, justified set of artifacts, built in repo X and verified one at a time. You deliver a blueprint the user approved plus the files it lists, not advice.

Reference material (read when a step says so):
- `references/targets.md`: establishing the target repository, access to it outside the workspace, and target platforms.
- `references/decision-guide.md`: selecting the right primitive, five reasons for a subagent, anti-patterns.
- `references/coexistence.md`: avoiding collisions when multiple platforms open the same repository.
- `references/writing-for-agents.md`: writing descriptions that route, body structure, safety checkpoints.
- `references/antigravity.md`: Antigravity locations, fields, triggers, tool names and limits.
- `references/claude-code.md`: Claude Code conventions when designing for Claude Code.
- `references/opencode.md`: OpenCode conventions when designing for OpenCode.
- `references/codex.md`: OpenAI Codex CLI conventions when designing for Codex.

## Anti-pattern: the org chart
You build a team of role agents (developer, tester, architect, orchestrator) because it mirrors a human team. Warning signs:
- a proposed agent has no reason from the decision guide;
- the orchestrator is a subagent;
- the same conventions appear in several agent prompts.

## Process

1. **Establish the target** (details in `references/targets.md`).
   - **Target repository.** Take the path from the user's prompt; if missing, ask for it. Use the current directory only if it is not the stablehand repo (stablehand has top-level `contracts/` and `platforms/`). **Never write artifacts into stablehand itself.**
   - **Access & Workspace.** In Antigravity, read and write files using absolute paths. When running commands in the target, ensure the target folder is added to the workspace (multi-root workspace in App/IDE, or `agy --add-dir <target>` / `/add-dir` in CLI) or launch `agy` from the target folder.
   - **Platform(s).** Antigravity by default, unless the user specifies Claude Code or OpenCode.
   - **Root.** Confirm the repository root: the git root (`git -C <path> rev-parse --show-toplevel`) and its README.
   - **Confirmation.** Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

2. **Inventory the target (read-only).**
   - Collect stack and commands: package manifests, scripts, build tools, CI workflows.
   - Collect existing customizations: `AGENTS.md`, `GEMINI.md`, `.agents/rules/`, `.agents/skills/`, `.agents/agents/`, `.agents/plugins/`, and any `.claude/` or `.opencode/` folders.
   - Run the validator in project mode:
     Determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from the directory containing this `SKILL.md`. Run:
     `uv run "<absolute-path-to-scripts/lint.py>" --project "<target>"`
     or invoke `/stablehand:validating-artifacts`.
   - For large codebase sweeps, delegate to the built-in `research` subagent via `invoke_subagent`.

3. **Interview.** Ask one question at a time and give your recommended answer with each. Stop once you know:
   - the 3–5 workflows the user repeats with the agent (e.g., add an endpoint, fix a bug, run migrations);
   - concrete recent failures: what the agent did wrong, not general wishes;
   - solo or team use (project scope `.agents/` vs global `~/.gemini/config/`), and which other platforms open this repository.

   If the user specified "no questions" or you run headlessly, write down your assumptions and proceed.

4. **Decide.** Read `references/decision-guide.md`.
   - For each need, choose instructions, a path-scoped rule, a skill, a subagent, a hook, or nothing.
   - Every subagent must satisfy at least one of the five reasons: context isolation, independence, different permissions, a different model, or parallelism. Drop subagents with no reason.
   - Prefer built-in agents (`research`, `browser`) and Antigravity's built-in multi-agent orchestrators (`/run-workflow`, `/swarm`, `/boost`, `/teamwork`, and Orchestrator model mode) over custom orchestrator agents.
   - Orchestration is a skill run in the main conversation, never a subagent.

5. **Blueprint and approval.** Present a table with these columns:
   `Artifact | Type | Path in target | Platform | When used | Justification | Eval idea`
   - Order the rows: instructions → skills → agents → hooks. Agents preload skills, so knowledge must exist before an agent points to it.
   - Check `references/coexistence.md` for proper placement if other platforms share the repository.
   - **Do not create any files until the user approves the blueprint.** Save the blueprint to `<target>/.stablehand/blueprint.md` only if the user wants it versioned.

6. **Build, one row at a time.** Load the matching stablehand skill explicitly. Pass it the blueprint row, target repository path, and target platform as its brief. Finish each row before starting the next:
   - instructions or rules → invoke `/stablehand:writing-project-instructions` or read its `SKILL.md`
   - skill → invoke `/stablehand:authoring-skills` or read its `SKILL.md`
   - subagent → invoke `/stablehand:authoring-agents` or read its `SKILL.md`
   - hook → write to `<target>/.agents/hooks.json` directly and verify by triggering its event once.

7. **Validate the whole project.** Re-run the project-mode validator command from step 2 and resolve all errors.

8. **Report.** Provide:
   - each created path and how to invoke it (`/<skill>`, `/stablehand:<skill>`, or `invoke_subagent` / `@<agent>`);
   - what was deliberately not created, and why;
   - deferred rows and suggested follow-ups.

## Typical result for an application repository
Adapt names to the project and drop rows the baseline already handles:
- **Skills:** `planning-changes`, `implementing-changes` (project conventions only), `writing-tests`, `reviewing-changes`, `updating-docs`, `shipping-changes`. `shipping-changes` is the orchestration skill: it sequences the others explicitly and decides when to delegate.
- **Agents:**
  - `change-reviewer`: read-only, independent, optionally a different model; preloads `reviewing-changes`.
  - `task-implementer`: optional; fresh context per task on long features.
- **Exploration:** built-in `research` subagent.

## Done when
- [ ] The target repository and platform were confirmed, and nothing was written into stablehand
- [ ] The user approved the blueprint, or assumptions were stated in headless mode
- [ ] Every row was built through its stablehand skill, or is listed as deferred
- [ ] Project-mode validation shows zero errors
- [ ] The report lists paths, invocation instructions, and deferred items
