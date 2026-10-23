---
name: authoring-skills
description: "Creates or improves one skill for a given repository and platform (Claude Code by default; Antigravity or OpenCode on request) and proves with evals that it changes the agent's behavior. Use when someone needs a skill for this or another repo, asks to write, scaffold, refactor or fix triggering of a skill, or wants the current conversation turned into a skill. Not for subagents, CLAUDE.md/AGENTS.md, or porting."
argument-hint: "[target repo path] [what the skill should do]"
---

A skill earns its place by changing behavior. Prove the failure first, write the minimum that fixes it, and stop when the re-test passes.

Reference material:
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: the target repo, access to it, and target platforms other than Claude Code.
- `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`: read before drafting.
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`, section 2: fields, locations, limits. For other target platforms, read `antigravity.md` or `opencode.md` in the same folder instead.
- `${CLAUDE_PLUGIN_ROOT}/references/eval-protocol.md`: eval file formats and the decision rule.
- `${CLAUDE_PLUGIN_ROOT}/references/decision-guide.md`: when the request is really an agent, a rule or a hook.

## Anti-pattern: the untested skill
You write the skill before watching the agent fail. Warning signs:
- there is no baseline record;
- the description explains *how* the skill works instead of *when* to use it;
- the body teaches things the model already does well.

## Process

0. **Target** (details in `targets.md`).
   - **Target repo.** Take it from the request or `$ARGUMENTS`; ask if it is missing. Use the current directory only if it is not the stablehand repo (stablehand has top-level `contracts/` and `platforms/`). **Never write the skill into stablehand.**
   - **Access.** If the target is outside the working directory, ask the user to run `/add-dir <path>` first.
   - **Target platform.** Claude Code by default. For **Antigravity or OpenCode**:
     - draft from that platform's card;
     - put the skill in that platform's folder (respecting `coexistence.md`);
     - validate with `--platform <target>`;
     - skip the runs in steps 2 and 5, but still write the eval files;
     - end with a ready-to-paste prompt that runs those evals on the target platform;
     - mark the hand-over "untested on <platform>".
   - **Confirm** in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Brief.** Settle these before writing anything; ask the user only for what you cannot infer:
   - The job, and whether a skill is the right primitive (decision guide). Knowledge for every task belongs in instructions; isolation needs belong in an agent.
   - The name: kebab-case, ≤ 64 chars, gerund preferred (`applying-migrations`).
   - The type: workflow, reference, posture, or tool wrapper.
   - Who triggers it:
     - side effects (deploy, migrate, publish, post) → `disable-model-invocation: true`;
     - background knowledge the user never calls → `user-invocable: false`.
   - Scope: project `<target>/.claude/skills/<name>/` (shared via git) or user `~/.claude/skills/<name>/`.
   - Overlap: list `<target>/.claude/skills/` and `~/.claude/skills/`. If an existing skill covers the job, improve it instead.
   - Turning the conversation into a skill: keep the steps that worked and the user's corrections; drop the dead ends.

2. **Baseline (RED).**
   - Write the evals in `<target>/.stablehand/evals/skills/<name>/`: 3 realistic scenarios plus `triggers.yaml` (5–8 should, 5–8 near-miss should-not), in the format from `eval-protocol.md`.
   - Run 1–3 scenarios **without** the skill. Use the Agent tool with `subagent_type: "stablehand:scenario-runner"`, mode `baseline`. Its working directory must be a scratch copy or a git worktree **of the target repo** (`git -C <target> worktree add <scratch> HEAD`), never the target checkout itself. Remove the worktree afterwards.
   - Record the failures verbatim, including the agent's own excuses.
   - If the baseline already passes, tell the user the skill isn't needed (or narrow it) and stop. If the user still wants it, keep it only on their explicit say-so: record "kept on user override, no measured gain" in the results file and say the same in the hand-over. Suggest folding the guidance into the project instructions instead.
   - If the user explicitly asks to skip testing, skip this step and step 5, and say "untested" in the hand-over.

3. **Draft** `SKILL.md` with `writing-for-agents.md` open.
   - Description:
     - third person; when-to-use first, using phrasings from the trigger set;
     - a "Not for …" clause for the near misses;
     - ≤ 500 chars, double-quoted.
   - Add Claude fields only on purpose:
     - `argument-hint` for skills the user runs with arguments;
     - `allowed-tools` to pre-approve the exact commands the skill runs (e.g. `Bash(uv run pytest *)`);
     - `paths` for file-scoped skills;
     - `context: fork` for heavy isolated work.
   - Body:
     - one stance sentence;
     - an anti-pattern only if the baseline showed one;
     - numbered steps, each risky step ending in a verification;
     - exact commands for fragile steps, goals and criteria for judgment calls;
     - **a user checkpoint before the first irreversible or external side effect**;
     - `Done when` for workflows.
   - To load another skill from this one, write "Use the Skill tool to load `<name>`". Merely naming a skill does not load it.
   - Bulky material goes in `references/<topic>.md`, with a "read when …" pointer. Scripts go in `scripts/` (Python via `uv run`, or Node; no bash-only scripts).

4. **Validate.**
   `uv run "${CLAUDE_PLUGIN_ROOT}/skills/validating-artifacts/scripts/lint.py" --platform claude-code <skill-folder>`
   Fix every error and re-run until it is clean.

5. **Re-test (GREEN).**
   - Re-run the same scenarios with `scenario-runner` in mode `with-artifact`, passing the skill folder path.
   - Check triggers with the real loader, in the target repo:
     `uv run "${CLAUDE_PLUGIN_ROOT}/skills/evaluating-artifacts/scripts/run_triggers.py" --repo "<target>" --triggers <triggers.yaml> --skill <name> --out <results.json>`
     It runs every prompt with `claude -p`, edits disabled, and checks for a `Skill` call naming the skill. If `claude` is not on PATH, ask the user for the CLI path (the IDE extensions bundle one) and pass `--claude <path>`.
   - Apply the decision rule from `eval-protocol.md`, change one thing per iteration, and stop after 3 iterations.
   - Save `results/<date>.md`.

6. **Independent review.** Use the Agent tool with `subagent_type: "stablehand:artifact-reviewer"`. Pass:
   - the skill folder path and the brief;
   - the absolute paths of the **target** platform's card (`claude-code.md`, `antigravity.md` or `opencode.md` in `${CLAUDE_PLUGIN_ROOT}/references/`) and of `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`;
   - the results file.

   Fix blocking findings. Tell the user about any you disagree with. After fixing, run the reviewer once more on the fixed artifact and record its final verdict in the results file.

7. **Hand over.** Show the final `SKILL.md`, the baseline vs with-skill table, how to invoke it (`/name` or example prompts), and known gaps. If the skill does not appear, run `/reload-skills`.

## Done when
- [ ] The skill is in the target repo (or user scope), in the target platform's folder, and nothing was written into stablehand
- [ ] The validator reports no errors for the target platform
- [ ] The with-skill run beats the baseline per the decision rule, or the user accepted the gap. If testing was skipped (on request, or because the target is another platform), the hand-over says "untested" and gives the hand-off prompt.
- [ ] The trigger set passes
- [ ] The reviewer has no open blocking findings
- [ ] The user approved the final text
