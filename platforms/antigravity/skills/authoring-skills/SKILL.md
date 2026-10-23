---
name: authoring-skills
description: "Creates or improves one skill for a given repository and platform (Antigravity by default; Claude Code or OpenCode on request) and proves with evals that it changes the agent's behavior. Use when asked to write, scaffold, improve, refactor or fix triggering of a skill, or turn a conversation into a skill. Not for subagents, always-loaded instructions or rules, porting existing artifacts, or running a skill."
---

A skill earns its place by changing behavior. Prove the failure first, write the minimum that fixes it, and stop when the re-test passes.

Reference material (read when a step says so):
- `references/targets.md`: establishing the target repository, access to it, and handling targets on other platforms.
- `references/writing-for-agents.md`: guidance on descriptions, body structure, degrees of freedom, and safety checkpoints.
- `references/eval-protocol.md`: eval scenario structure, trigger sets, and the decision rule.
- `references/decision-guide.md`: deciding between a skill, an agent, a rule, or a hook.
- `references/coexistence.md`: avoiding cross-platform skill collisions.
- `references/antigravity.md`: Antigravity skill structure, frontmatter fields, slash commands, and limits.
- `references/claude-code.md`: Claude Code conventions when authoring for Claude Code.
- `references/opencode.md`: OpenCode conventions when authoring for OpenCode.

## Anti-pattern: the untested skill
You write the skill before watching the agent fail. Warning signs:
- there is no baseline record;
- the description explains *how* the skill works instead of *when* to use it;
- the body teaches things the model already does well.

## Process

0. **Target** (details in `references/targets.md`).
   - **Target repository.** Take it from the request; ask if missing. Use the current directory only if it is not the stablehand repo (stablehand has top-level `contracts/` and `platforms/`). **Never write the skill into stablehand.**
   - **Access & Workspace.** `run_command` in Antigravity requires `Cwd` to be within the active workspace. When running commands in the target, ensure the target folder is added to the workspace (multi-root workspace in Antigravity IDE) or launch `agy` from the target folder.
   - **Target platform.** Antigravity by default. For **Claude Code or OpenCode**:
     - draft from that platform's card;
     - place the skill in that platform's native location (respecting `references/coexistence.md`);
     - validate with `--platform <target>`;
     - skip local runs in steps 2 and 5, but write the eval files;
     - hand off a ready-to-paste prompt to run those evals on the target platform;
     - mark the hand-over as "untested on <platform>".
   - **Confirmation.** Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Brief.** Settle these before writing anything:
   - The job, and whether a skill is the right primitive (`references/decision-guide.md`). Always-on knowledge belongs in instructions; isolation needs belong in a subagent.
   - The name: kebab-case, ≤ 64 chars, gerund preferred (`applying-migrations`).
   - The type: workflow, reference, posture, or tool wrapper.
   - Invocation:
     - side effects (deploy, migrate, publish, post) → explicitly state "run only when requested" in description;
     - internal helper not intended as a slash command → `disable-slash-command: true`.
   - Scope: project `<target>/.agents/skills/<name>/` (or workspace plugin `<target>/.agents/plugins/<set>/skills/<name>/`) or user `~/.gemini/config/skills/<name>/`.
   - Overlap: check existing skills in the target. If an existing skill covers the job, improve it instead.
   - Turning a conversation into a skill: keep steps that worked and user corrections; omit dead ends.

2. **Baseline (RED).**
   - Write evals in `<target>/.stablehand/evals/skills/<name>/`: 3 realistic scenarios plus `triggers.yaml` (5–8 should, 5–8 near-miss should-not), following `references/eval-protocol.md`.
   - Run commands inside the target: always execute target code from inside the target directory (`cd "<target>" && uv run …`, never `--project` from stablehand).
   - Run 1–3 scenarios **without** the skill. Delegate to `scenario-runner` using `invoke_subagent` in mode `baseline`. The working directory must be a scratch copy or a git worktree of the target repo (e.g. `<target>/../<target>-stablehand-scratch` or `git -C <target> worktree add <scratch> HEAD`), never the target checkout itself. Ensure the scratch directory is added to the workspace so `run_command` can operate. Clean up the scratch copy or worktree afterwards.
   - Record failures verbatim, including the agent's excuses.
   - If the baseline already passes, inform the user that the skill is not needed (or narrow it) and stop.
   - If the user explicitly asks to skip testing, skip this step and step 5, and state "untested" in the hand-over.

3. **Draft** `SKILL.md` with `references/writing-for-agents.md` open.
   - Description:
     - third person; when-to-use first, using phrasings from the trigger set;
     - a "Not for …" clause for near misses;
     - ≤ 500 chars, double-quoted.
   - Frontmatter: only valid Antigravity fields (`name`, `description`, and `disable-slash-command` if needed).
   - Body:
     - one stance sentence;
     - an anti-pattern only if observed in baseline;
     - numbered steps, each risky step ending with a verification action;
     - exact commands for fragile steps, criteria for judgment calls;
     - **a user checkpoint before the first irreversible or external side effect**;
     - explicit stop conditions and a `Done when` checklist.
   - To invoke another skill from this one: tell the agent to invoke `/<skill>` or `/stablehand:<skill>`, or to read its `SKILL.md` by path. Never just mention the name in prose.
   - Bulky documentation goes in `references/<topic>.md`, with an explicit pointer. Executable scripts go in `scripts/` (Python via `uv run`, or Node; cross-platform, handling errors).

4. **Validate.**
   Determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from the directory containing this `SKILL.md`. Run:
   `uv run "<absolute-path-to-scripts/lint.py>" --platform antigravity "<skill-folder>"`
   or invoke `/stablehand:validating-artifacts`. Fix all errors and re-run until clean.

5. **Re-test (GREEN).**
   - Re-run the scenarios with `scenario-runner` via `invoke_subagent` in mode `with-artifact`, passing the skill folder path.
   - Check trigger prompts using the real loader:
     Run `agy -p "<prompt>" --output-format json` in a scratch copy or git worktree of the target repository (never in the live target checkout or stablehand). Ensure the scratch copy or worktree is added to the workspace if running in-session. Clean up the scratch copy or worktree afterwards.
   - Apply the decision rule from `references/eval-protocol.md`, change one thing per iteration, and stop after at most 3 iterations.
   - Save results to `<target>/.stablehand/evals/skills/<name>/results/<date>.md`.

6. **Independent review.** Delegate to `artifact-reviewer` using `invoke_subagent`. Pass:
   - the skill folder path and the brief;
   - absolute paths to the **target** platform's card (`references/antigravity.md`, `references/claude-code.md`, or `references/opencode.md`) and `references/writing-for-agents.md` inside this skill's folder;
   - the results file.
   Fix blocking findings. Tell the user about any you disagree with.

7. **Hand over.** Show the final `SKILL.md`, baseline vs with-skill table, invocation instructions (`/<name>` or `/<plugin>:<name>`), and known gaps.

## Done when
- [ ] The skill is in the target repo (or user scope), in the target platform's folder, and nothing was written into stablehand
- [ ] The validator reports zero errors for the target platform
- [ ] The with-skill run beats the baseline per the decision rule, or the user accepted the gap. If testing was skipped, the hand-over states "untested" and provides the hand-off prompt
- [ ] The trigger set passes
- [ ] The reviewer has no open blocking findings
- [ ] The user approved the final text
