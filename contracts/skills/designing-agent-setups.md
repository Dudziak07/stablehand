---
id: designing-agent-setups
kind: skill
version: 2026.10.0
references: [targets.md, decision-guide.md, coexistence.md, writing-for-agents.md, "@all-platforms"]
---
# designing-agent-setups

## Purpose
The entry point of stablehand. It turns "make the agent work better on repo X" into a small, justified set of artifacts for the chosen platform and builds them one by one in **the target repository**, usually a repo other than stablehand. The deliverable is an **approved blueprint plus the artifacts it lists**, not advice.

## Triggers
- **Should:**
  - "set up agents/skills for this project";
  - "what customization should this repo have";
  - "create a developer/tester/orchestrator agent";
  - "our agent keeps doing X wrong in this repo, fix the setup";
  - "audit our CLAUDE.md/skills/agents".
- **Should not:**
  - writing or fixing one named skill or agent (go to the authoring skills directly);
  - general coding tasks;
  - questions about how a platform works.

## Inputs
- The target repository path. It is required when working from the stablehand repo.
- The target platform(s). Default: the host platform.
- Optional constraints from the user: team or solo use, "no questions".

## Procedure
1. **Target.** Establish the target repo, access to it, and the platform, following `targets.md`. Never write artifacts into stablehand. Confirm the root (git root, README).
2. **Inventory (read-only).**
   - Collect the stack and the build/test/lint commands from manifests, scripts and CI.
   - List the existing customization for all platforms (see `coexistence.md`).
   - Run the validator in project mode.
   - Delegate large codebase sweeps to the platform's built-in exploration agent.
3. **Interview.** Ask one question at a time, each with a recommended answer, until you know:
   - the 3–5 workflows the user repeats with the agent;
   - concrete recent failures;
   - project vs user scope;
   - which other platforms open this repo.

   In headless or "no questions" mode, state assumptions instead.
4. **Decide.** Choose a primitive for each need with `decision-guide.md`.
   - Every proposed agent must name its reason (one of the five). Drop agents with no reason.
   - Prefer built-in agents to custom duplicates.
5. **Blueprint.** Write one row per artifact: type, name, location, when used, justification, eval idea. Build order: instructions → skills → agents → hooks. **Get approval before creating files.**
6. **Build.** Handle one artifact at a time. Load the matching skill for each:
   - `writing-project-instructions`;
   - `authoring-skills`;
   - `authoring-agents`.

   Pass the blueprint row as the brief. Finish each artifact before starting the next.
7. **Validate.** Run the validator in project mode again and fix errors.
8. **Report.** List:
   - the paths created;
   - how to invoke each artifact;
   - what was deliberately not created, and why;
   - follow-ups.

## Outputs
- A blueprint (shown in chat; saved to `.stablehand/blueprint.md` if the user wants it versioned).
- The artifacts.
- The final report.

## Done when
- The blueprint is approved, or the assumptions are stated in headless mode.
- Every row is built through its authoring skill or explicitly deferred.
- The project-mode validator shows no errors.
- The report lists paths, invocation and deferred items.

## Must not
- Create persona agents (developer, tester, architect) without one of the five reasons.
- Define orchestration as a subagent.
- Write any file before the blueprint is approved.
- Paste the same knowledge into several artifacts.
- Duplicate built-in agents.

## Platform adaptation
- **Access to a target repository outside the workspace** (`targets.md`).
- **Loading the other stablehand skills.** Use the platform's explicit mechanism, never a mention in prose.
- **Built-in exploration agent:** Claude `Explore`, Antigravity `research`, OpenCode `explore`.
- **Validator invocation path.** Where the bundled linter lives on that platform.
- **Locations for the blueprint rows.** Taken from the host platform card and `coexistence.md`.
- **Argument passing for the project path.** For example Claude `$ARGUMENTS`.

## Evals
`persona-agents-pushback`, `unrelated-request-no-trigger`
