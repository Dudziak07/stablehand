---
id: authoring-skills
kind: skill
version: 2026.11.1
references: [targets.md, writing-for-agents.md, eval-protocol.md, decision-guide.md, coexistence.md, "@all-platforms"]
---
# authoring-skills

## Purpose
Create or improve **one** skill for a target repository and target platform (default: the host platform), test-first. The procedure:
1. Show how the agent fails without the skill.
2. Write the smallest skill that fixes that failure.
3. Validate it, re-test it, and have it reviewed independently.

## Triggers
- **Should:**
  - "write/create/scaffold a skill for X";
  - "turn what we just did into a skill";
  - "this skill doesn't trigger / is ignored";
  - "improve/refactor this SKILL.md".
- **Should not:**
  - subagent definitions (that is `authoring-agents`);
  - CLAUDE.md, AGENTS.md or rules (that is `writing-project-instructions`);
  - porting an existing skill to another platform (that is `porting-artifacts`);
  - using a skill.

## Inputs
- The target repository path and the target platform.
- A brief: the job, who triggers the skill (model or user), side effects, and scope (project or user).
- Optionally, the current conversation as source material.

## Procedure
0. **Target.** Establish the target repo, access to it, and the platform, following `targets.md`. If the target platform is not the host, draft and validate for the target, skip steps 2 and 5, and hand off the eval prompt instead.
1. **Brief.**
   - Confirm that a skill is the right primitive (`decision-guide.md`).
   - Pick the name: kebab-case, at most 64 characters, gerund preferred.
   - Pick the type: workflow, reference, posture or tool-wrapper.
   - Decide invocation. If the skill has side effects, make it user-invoked only.
   - Check existing skills for overlap. If one overlaps, improve it instead of adding a new one.
   - When converting a conversation, extract the steps that worked and the corrections the user made.
2. **Baseline (RED).**
   - Write the evals following `eval-protocol.md`: 3 realistic scenarios plus a trigger set (5–8 should, 5–8 near-miss should-not).
   - Run 1–3 scenarios without the skill through the scenario-runner agent, in isolation.
   - Record the failures verbatim.
   - If the baseline already passes, say so and stop, or narrow the skill. If the user still wants it, keep it only on their explicit say-so: record "kept on user override, no measured gain" in the results file and say the same in the hand-over. Suggest folding the guidance into the project instructions instead.
3. **Draft.**
   - Follow `writing-for-agents.md` and the platform card:
     - description first: triggers first, near-miss exclusions, double-quoted;
     - platform fields only on purpose;
     - body with a stop condition and verification steps;
     - degrees of freedom matched to how fragile each step is;
     - references one level deep;
     - scripts cross-platform.
   - Put the checkpoint before the first side effect.
4. **Validate.** Run the bundled linter on the skill folder and fix all errors.
5. **Re-test (GREEN).**
   - Re-run the same scenarios with the skill, then the trigger set, using the platform's real loader.
   - Iterate at most 3 times. Change one thing per iteration.
6. **Review.** Send the skill folder, the brief and the platform card to the artifact-reviewer agent. Fix blocking findings and report any disagreements. After fixing, run the reviewer once more on the fixed artifact and record its final verdict in the results file.
7. **Hand over.** Update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`), then give:
   - the final path;
   - baseline vs with-skill results;
   - how to invoke the skill;
   - known gaps.

## Outputs
- The skill folder in the platform's location.
- The eval files and results under `.stablehand/evals/skills/<name>/`.

## Done when
- The validator reports no errors.
- The with-skill run beats the baseline per the decision rule in `eval-protocol.md`, or the user explicitly accepted the gaps.
- The trigger set passes.
- The reviewer has no open blocking findings.
- The user approved the final text.

## Must not
- Write the skill before recording a baseline, unless the user explicitly asks to skip testing. If they do, the hand-over must say "untested".
- Summarize the workflow in the description.
- Add knowledge the model already has.
- Hard-code absolute paths or secrets.
- Place the skill where another platform will load it by accident (see `coexistence.md`).

## Platform adaptation
- **Access to a target repository outside the workspace** (`targets.md`).
- **Skill location and frontmatter extras.** For example, Claude `disable-model-invocation`, Antigravity `disable-slash-command`, and OpenCode `metadata.opencode/*`.
- **How to run the scenario-runner in isolation:** a git worktree of the target repo, created by the caller.
- **The real-loader trigger command** for the platform.
- **How the validator is invoked.**

## Evals
`skill-for-migrations`, `unrelated-request-no-trigger`
