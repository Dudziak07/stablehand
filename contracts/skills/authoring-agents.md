---
id: authoring-agents
kind: skill
version: 2026.11.1
references: [targets.md, decision-guide.md, writing-for-agents.md, eval-protocol.md, coexistence.md, "@all-platforms"]
---
# authoring-agents

## Purpose
Create or improve **one** subagent or custom agent for a target repository and target platform (default: the host platform). Write it only after proving that an agent is the right primitive.

## Triggers
- **Should:**
  - "create/design a subagent";
  - "make a reviewer/researcher/implementer agent";
  - "add a developer/tester agent";
  - "fix this agent file";
  - "why doesn't Claude delegate to my agent".
- **Should not:**
  - orchestration (that is a skill or a primary agent, routed through `designing-agent-setups`);
  - procedures or knowledge (that is `authoring-skills`);
  - porting (that is `porting-artifacts`).

## Inputs
- The target repository path and the target platform.
- A brief: the job, why it needs an agent, and what it should return.

## Procedure
0. **Target.** Establish the target repo, access to it, and the platform, following `targets.md`. If the target platform is not the host, draft and validate for the target, skip the runs in step 5, and hand off the benchmark prompt instead.
1. **Justify.**
   - The agent must meet at least one of the five reasons in `decision-guide.md`.
   - Check the built-in agents first.
   - If no reason applies, explain why and switch to `authoring-skills`.
   - If the user insists on a persona agent, explain the cost. Then offer the thin variant that only loads skills.
2. **Contract.** Write down each of these:
   - one responsibility;
   - when to delegate (the description);
   - the inputs the caller must pass (the agent starts with no history);
   - the exact output format (only the final message returns);
   - least-privilege tools;
   - a model tier;
   - the skills to preload (knowledge lives in skills);
   - isolation and permission settings;
   - 3–5 benchmark tasks with expected results.
3. **Draft.** Write the agent file per the platform card:
   - Frontmatter: only the fields that are needed.
   - Body: role, procedure, output template, constraints, and when to stop and return.
   - Keep the body under ~150 lines.
4. **Validate** with the bundled linter.
5. **Test.**
   - Run each benchmark through explicit delegation and compare the results with the expected ones.
   - Run 2 natural prompts through the real loader to check automatic delegation.
   - Iterate at most 3 times.
6. **Review** with the artifact-reviewer agent, giving it the **target** platform's card, and fix blocking findings. After fixing, run the reviewer once more on the fixed artifact and record its final verdict in the results file.
7. **Hand over.** Update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`), then give:
   - the path;
   - how to invoke the agent;
   - the benchmark results;
   - any restart or reload needed.

## Outputs
- The agent file in the platform's location.
- Benchmarks and results under `.stablehand/evals/agents/<name>/`.

## Done when
- The justification is stated.
- The validator reports no errors.
- The benchmarks meet the decision rule.
- Automatic delegation was checked.
- The reviewer has no open blocking findings.
- The user approved the agent.

## Must not
- Create an orchestrator subagent.
- Grant write tools or an unrestricted shell to a reviewer or researcher. If the review needs read-only commands (for example `git diff --staged`), allow exactly those through the platform's enforcement: a hook that rejects everything else, or an exact allow-list whose patterns cannot admit writing flags such as `--output`.
- Copy knowledge into the prompt that belongs in a skill.
- Pin full model IDs without a reason.
- Put eval files inside the platform's agents folder.

## Platform adaptation
- **Access to a target repository outside the workspace** (`targets.md`).
- **Agent file location and fields.** Claude `.claude/agents/*.md`; Antigravity `.agents/agents/*.md` with `tools` from the Antigravity tool list; OpenCode `.opencode/agents/<name>.md` with `mode` and `permissions`.
- **Mapping tools and model tiers.** Abstract → platform, as in the card.
- **Explicit delegation syntax:** `@"name (agent)"`, `@name`, `invoke_subagent`.
- **The real-loader check command** for the platform.

## Evals
`persona-agents-pushback`, `port-reviewer-to-opencode` (the target side)
