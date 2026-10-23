---
name: authoring-skills
description: "Creates or improves one skill for a user's project repository and platform (OpenCode by default; Claude Code or Antigravity on request), then proves with evals that it changes the agent's behavior. Use when someone needs a skill for a repo, asks to write, scaffold, refactor or fix triggering of a project skill, or wants this conversation turned into a skill. Not for subagents, AGENTS.md/CLAUDE.md, or porting."
metadata:
  opencode/slash: "true"
---

A skill earns its place by changing behavior. Prove the failure first, write the minimum that fixes it, and stop when the re-test passes. Write all output in English.

Reference material:
- `references/targets.md`: the target repo, access to it, and target platforms other than OpenCode.
- `references/writing-for-agents.md`: read before drafting; DeepSeek calibration is in the last table.
- `references/opencode.md`, section 2: fields, locations, limits. When the target platform is Claude Code or Antigravity, read `references/claude-code.md` or `references/antigravity.md` instead.
- `references/eval-protocol.md`: eval file formats and the decision rule.
- `references/decision-guide.md`: when the request is really an agent, a rule or a hook.
- `references/coexistence.md`: placement when other platforms open the repo.

## Anti-pattern: the untested skill
You write the skill before watching the agent fail. Warning signs:
- there is no baseline record;
- the description explains *how* the skill works instead of *when* to use it;
- the body teaches things the model already does well.

## Process

0. **Target** (details in `references/targets.md`).
   - Target repo: take it from the request. If it is missing, ask. Use the current directory only if it is not the stablehand repo (stablehand has top-level `contracts/` and `platforms/`). **Never write the skill into stablehand.**
   - Access: if the target is outside the workspace, approve the `external_directory` prompt.
   - Commands: for `opencode run`, pass `--dir "<target-or-scratch>"`. For every other command that runs the target's code (tests, build, scripts), use `cd "<target>" && <command>`; do not pass `--project "<target>"` to `uv run` from the stablehand folder.
   - Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.
   - Target platform: OpenCode by default. For **Claude Code or Antigravity**:
     - draft from that platform's card;
     - put the skill in that platform's folder (respect `references/coexistence.md`);
     - validate with `--platform <target>`;
     - skip the runs in steps 2 and 5, but still write the eval files;
     - end with a ready-to-paste prompt that runs those evals on the target platform;
     - mark the hand-over "untested on <platform>".

1. **Brief.** Settle these before writing anything; ask the user only for what you cannot infer:
   - The job, and whether a skill is the right primitive (decision guide). Knowledge for every task belongs in instructions; isolation needs belong in an agent.
   - The name: kebab-case, at most 64 characters, gerund preferred (`applying-migrations`).
   - The type: workflow, reference, posture, or tool wrapper.
   - Who triggers it:
     - side effects (deploy, migrate, publish, post): add `metadata.opencode/autoinvoke: "false"` so it runs only when called;
     - background knowledge the user never calls: omit `metadata.opencode/slash` so it is not exposed as `/name`, and say in the description that it applies automatically.
   - Scope: project `<target>/.opencode/skills/<name>/` (shared through git) or user `~/.config/opencode/skills/<name>/`.
   - Overlap: list `<target>/.opencode/skills/`, `<target>/.claude/skills/`, `<target>/.agents/skills/`, `~/.config/opencode/skills/`, `~/.claude/skills/` and `~/.agents/skills/`. OpenCode loads all of them, and skill names must be unique across all of them. If an existing skill covers the job, improve it instead.
   - Turning the conversation into a skill: keep the steps that worked and the user's corrections; drop the dead ends.

2. **Baseline (RED).**
   1. Write the evals in `<target>/.stablehand/evals/skills/<name>/`: 3 realistic scenarios plus `triggers.yaml` (5 to 8 should, 5 to 8 near-miss should-not), in the format from `references/eval-protocol.md`.
   2. Create an isolated working directory for the target: if `git -C "<target>" status --porcelain` is empty, run `git -C "<target>" worktree add "<scratch>" HEAD`; otherwise copy the target to a scratch directory.
   3. Run 1 to 3 scenarios **without** the skill: use the task tool with the agent `scenario-runner`, mode `baseline`, working directory `<scratch>`. Never the target checkout itself.
   4. Record the failures verbatim, including the agent's own excuses.
   5. Keep `<scratch>` for step 5; do not delete it yet.
   6. If the baseline already passes, remove the scratch (`git -C "<target>" worktree remove "<scratch>"`, or delete the copy), tell the user the skill is not needed (or narrow it), and stop.
   7. If the user explicitly asks to skip testing, remove the scratch, skip this step and step 5, and say "untested" in the hand-over.

3. **Draft** `SKILL.md` with `references/writing-for-agents.md` open.
   - Description:
     - third person; when-to-use first, using phrasings from the trigger set;
     - a "Not for ..." clause for the near misses;
     - at most 500 characters, double-quoted.
   - Frontmatter: only `name`, `description`, and the `metadata` keys OpenCode reads (`opencode/slash`, `opencode/autoinvoke`). Quote every value.
   - Body:
     - one stance sentence;
     - an anti-pattern only if the baseline showed one;
     - numbered steps, one action each, each risky step ending in a verification;
     - exact commands for fragile steps, goals and criteria for judgment calls;
     - **a user checkpoint before the first irreversible or external side effect**;
     - a `Done when` list for workflows.
   - To load another skill from this one, write: call the skill tool with name `<name>`. Merely naming a skill does not load it.
   - Bulky material goes in `references/<topic>.md`, with a "read when ..." pointer. Scripts go in `scripts/` (Python through `uv run`, or Node; no bash-only scripts).

4. **Validate.** Call the skill tool with name `validating-artifacts`, and tell it to check the skill folder with `--platform opencode`. Fix every error and re-run until it is clean.

5. **Re-test (GREEN).**
   - Install the drafted skill into the scratch: create `<scratch>/.opencode/skills/<name>/` and copy `SKILL.md` plus its `references/` and `scripts/` folders (if any) there.
   - Install the probe into the scratch: create `<scratch>/.opencode/agents/` and copy `trigger-probe.md` into it. Take it from the `agents/` folder beside the installed `skills/` folder (for a workspace install: `<stablehand>/.opencode/agents/trigger-probe.md`; in the checkout: `platforms/opencode/agents/trigger-probe.md`). Without this copy OpenCode cannot find the agent from `--dir "<scratch>"`.
   - Verify both copies: `Get-ChildItem -Recurse "<scratch>/.opencode"` (or `find "<scratch>/.opencode" -type f`) lists the skill's `SKILL.md` and `agents/trigger-probe.md`.
   - Re-run the same scenarios with the task tool and the agent `scenario-runner`, in mode `with-artifact`, passing the skill folder path and the same `<scratch>` working directory.
   - Check triggers with the real loader **against a scratch copy of the target, never the target checkout**. Use the bundled read-only probe so a should-trigger prompt cannot write:
     `opencode run "<trigger prompt>" --format json --dir "<scratch>" --agent trigger-probe --model deepseek/deepseek-flash`
     In the JSON events, look for a `skill` call whose name is the skill. Run one prompt per trigger line.
   - If the target's code also has to run for a trigger, use `cd "<scratch>" && <command>`; never `--project "<target>"`.
   - Apply the decision rule from `references/eval-protocol.md`, change one thing per iteration, and stop after 3 iterations.
   - Save `results/<date>.md` in the eval folder.
   - Remove the scratch copy or worktree when done.

6. **Independent review.** Use the task tool with the agent `artifact-reviewer`. Pass:
   - the skill folder path and the brief;
   - the absolute paths of the **target** platform's card (`references/opencode.md`, `references/claude-code.md` or `references/antigravity.md` in this skill's folder) and of `references/writing-for-agents.md`;
   - the results file.

   Fix blocking findings. Tell the user about any you disagree with.

7. **Hand over.** Use this template:
```
Path: <skill folder>
Invoke: /<name> or "<example prompt>"
Baseline vs with-skill: <table>
Known gaps: <list, or "none">
Untested: <yes and why, or "no">
```
If the skill does not appear, restart OpenCode.

## Done when
- [ ] The skill is in the target repo (or user scope), in the target platform's folder, and nothing was written into stablehand
- [ ] The validator reports no errors for the target platform
- [ ] The with-skill run beats the baseline per the decision rule, or the user accepted the gap. If testing was skipped (on request, or because the target is another platform), the hand-over says "untested" and gives the hand-off prompt
- [ ] The trigger set passes
- [ ] The reviewer has no open blocking findings
- [ ] The user approved the final text
