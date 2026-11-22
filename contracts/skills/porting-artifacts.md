---
id: porting-artifacts
kind: skill
version: 2026.10.0
references: [targets.md, coexistence.md, writing-for-agents.md, "@all-platforms"]
---
# porting-artifacts

## Purpose
Move a skill, agent or instruction file from one platform to another. The behavior contract stays the same; fields, tool names, model tiers, paths and invocation syntax are rewritten for the target. The port also says what could not be carried over and how to test it on the target.

## Triggers
- **Should:**
  - "port/convert/adapt this agent/skill to OpenCode/Antigravity/Claude Code";
  - "make the same reviewer for our OpenCode setup";
  - "bring stablehand to a new platform".
- **Should not:**
  - creating something new (that is `authoring-skills` or `authoring-agents`);
  - same-platform edits.

## Inputs
- The source artifact path(s).
- The source platform.
- The target platform.
- The target project or folder.

## Procedure
0. **Target.** Establish where the port goes (a target repository or a stablehand `platforms/<p>/` folder) and access to it (`targets.md`).
1. **Load both platform cards.** If a card may be stale for the fields involved, ask the platform-researcher agent to re-check them.
2. **Extract the contract.** If one exists, use it (for example, a stablehand contract). Otherwise write a ≤ 10-line contract from the source:
   - purpose;
   - triggers;
   - inputs;
   - outputs;
   - must-nots.
3. **Map the artifact to the target platform.**
   - **Frontmatter fields.** Use the target card's table. Drop fields the target does not support and record each one as lossy.
   - **Tools.** Map abstract capability → target tool names or permission keys. Read-only means every write, shell and network capability is denied unless the source explicitly allowed it; a restricted source shell becomes an exact allow-list on the target.
   - **Model tier.** `inherit`, fast or strongest.
   - **Invocation syntax** in the body:
     - loading a skill (Claude Skill tool → Antigravity `/name` or read the SKILL.md → OpenCode `skill({id})`);
     - delegation (Agent tool → `invoke_subagent` → subagent / `@name`).
   - **Paths and substitutions.** Replace `${CLAUDE_SKILL_DIR}` and similar variables with paths relative to the skill folder, stated explicitly.
   - **Placement.** Use `coexistence.md` to avoid cross-loading.
4. **Calibrate** for the target's model family (`writing-for-agents.md`): more explicit steps and output templates for DeepSeek, quoted strings for Antigravity.
5. **Validate** with the bundled linter for the **target** platform.
6. **Write `PORT-NOTES.md`** beside the result, or append a section to it. Include:
   - the source, its version and date;
   - the mapping decisions;
   - lossy items;
   - untested behavior.
7. **Hand off testing.** Produce a ready-to-paste prompt for the target platform's agent. It runs the artifact's eval scenarios there and reports back.
8. **Report in the final message.** `PORT-NOTES.md` is the record, not a substitute for the report. The final message must contain:
   - the path of every ported artifact;
   - each lossy item, one line each (for example, `color` mapped or dropped), or "no lossy items";
   - the hand-off prompt itself, pasted in full;
   - that the port is untested on the target until that prompt has been run.

## Outputs
- The ported artifact(s).
- `PORT-NOTES.md`.
- The test hand-off prompt.
- A final message with the paths, the lossy items and the full hand-off prompt.

## Done when
- The target validator reports no errors.
- Every source capability is mapped or listed as lossy.
- The body contains no source-platform tool names or invocation syntax.
- The hand-off prompt exists.
- The final message lists the lossy items and contains the full hand-off prompt, not only a pointer to `PORT-NOTES.md`.

## Must not
- Claim the port works without a run on the target platform.
- Copy the source body unchanged when it names platform tools.
- Silently drop permissions; a read-only source must stay read-only.
- Place the port where the source platform will also load it.

## Platform adaptation
Every implementation carries all platform cards. The host-specific part is how the implementation itself runs the validator and the researcher.

## Evals
`port-reviewer-to-opencode`
