---
name: porting-artifacts
description: "Ports a skill, subagent or instruction file between Claude Code, Antigravity and OpenCode, keeping its behavior while rewriting fields, tool names, model tiers, paths and invocation syntax for the target. Use when asked to port, convert, adapt or migrate an agent or skill to another platform, or to start a new platform folder in stablehand. Not for creating new artifacts or same-platform edits."
argument-hint: "[artifact path] [target platform]"
---
<!-- stablehand-lint: ignore S024 -->

A port keeps the contract and changes the mechanics. Nothing that names the source platform's tools or syntax may survive in the result, and nothing that was restricted may become permissive.

Reference material (read the source and target cards in full before mapping):
- `${CLAUDE_PLUGIN_ROOT}/references/claude-code.md`
- `${CLAUDE_PLUGIN_ROOT}/references/antigravity.md`
- `${CLAUDE_PLUGIN_ROOT}/references/opencode.md`
- `${CLAUDE_PLUGIN_ROOT}/references/targets.md`: the target repo and access to it.
- `${CLAUDE_PLUGIN_ROOT}/references/coexistence.md`: where the port may live without leaking into other platforms.
- `${CLAUDE_PLUGIN_ROOT}/references/writing-for-agents.md`: model calibration for the target.

## Process

0. **Target.** Establish where the port goes: a target repository or a stablehand `platforms/<target>/` folder. Never write a project's port into stablehand. If the target is outside the working directory, ask the user to run `/add-dir <path>` first.
   - **Confirm** in one line: `Target: <path> · Platform: <platform> · Porting: <artifact> → <target platform>`.

1. **Identify** the source artifact(s), the source platform, the target platform, and the target folder (a project or a stablehand `platforms/<target>/` folder). If a card may be stale for the fields involved, delegate the question to the `stablehand:platform-researcher` agent before mapping.

2. **Extract the contract.**
   - Use the existing one if there is one (stablehand: `contracts/<kind>/<id>.md`).
   - Otherwise write ≤ 10 lines from the source: purpose, triggers, inputs, outputs, must-nots, and for agents the permissions it has.

3. **Map**, field by field, using the cards' tables:
   - **Frontmatter.** Keep supported fields; translate the equivalents; record dropped fields as **lossy**. Examples:
     - Claude `disable-model-invocation: true` → OpenCode `metadata.opencode/autoinvoke: "false"`; Antigravity has no exact equivalent (state "run only when asked" in the description).
     - Claude `user-invocable: false` → Antigravity `disable-slash-command: true`.
   - **Tools.** Abstract capability → target names:
     - Claude `Read, Grep, Glob` → Antigravity `[view_file, grep_search, find_by_name]` → OpenCode `permission` with `edit: deny`, `bash: deny`, `shell: deny`, `webfetch: deny`, `websearch: deny`, `task: deny` (`bash` and `shell` always together, see the OpenCode card).
     - A restricted shell (a Claude hook, or the source's intent such as "only `git diff`") becomes an exact allow-list on OpenCode, e.g. `bash` and `shell` both set to `{"*": deny, "git diff --staged": allow}`. Avoid trailing wildcards that admit writing flags (`git diff --output=<file>`).
     - Write/execute access maps the same way. Read-only must stay read-only.
   - **Model tier:**
     - same as the caller → `inherit` / `inherit` / omit;
     - fast → `haiku` / `flash` / `deepseek/deepseek-flash`;
     - strongest → `opus` / `pro` / `deepseek/deepseek-v4-pro`.
   - **Invocation syntax in the body:**
     - loading a skill: Claude "Use the Skill tool to load `x`" → Antigravity "invoke `/x`, or read its SKILL.md" → OpenCode "call the skill tool with name `x`";
     - delegation: Agent tool → `invoke_subagent` / `@x` → the Task tool / `@x`.
   - **Paths.** Replace `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PLUGIN_ROOT}` and `$ARGUMENTS` with paths relative to the skill folder, stated explicitly ("the script `scripts/<name>.py` in this skill's folder").
   - **Placement.** Choose the target location from `coexistence.md`, so the port is not also loaded by another platform.

4. **Calibrate** for the target model (see `writing-for-agents.md`):
   - DeepSeek (OpenCode): numbered single-action steps, exact commands, output templates, an explicit output language.
   - Antigravity: double-quote every frontmatter string, and give explicit stop conditions.

5. **Validate** with the target platform's rules:
   `uv run "${CLAUDE_PLUGIN_ROOT}/skills/validating-artifacts/scripts/lint.py" --platform <target> <paths>`
   For Antigravity agents, an unknown tool name is an error: it can hang the agent.

6. **Write `PORT-NOTES.md`** next to the result (for a stablehand port: `platforms/<target>/PORT-NOTES.md`). Record:
   - source path and version;
   - the date;
   - mapping decisions;
   - lossy items;
   - behavior not yet tested on the target.

7. **Hand off testing.** You cannot run the target platform from here. Give the user a ready-to-paste prompt for the target agent: "Run the eval scenarios in <path> following `eval-protocol.md`, using <runner command for the target>, and report the results table."

8. **Report in the final message.** `PORT-NOTES.md` is the record, not a substitute for the report. A pointer such as "see PORT-NOTES.md" is not enough. End with:
   ```
   Ported: <path of each ported artifact>
   Lossy:
   - <field or capability>: <mapped to … | dropped, because …>   (or "none")
   Untested on <target> until this prompt is run there:
   <the full hand-off prompt from step 7>
   ```

## Porting stablehand itself
To bring stablehand to a platform, follow `platforms/<target>/BOOTSTRAP.md` in the stablehand repo. It runs this same procedure for every contract, then `uv run tools/sync.py` and the validator.

## Done when
- [ ] The target validator reports no errors
- [ ] Every source capability is mapped or listed as lossy in PORT-NOTES
- [ ] No source-platform tool names or invocation syntax remain in the body
- [ ] Permissions are equal or stricter than the source
- [ ] The test hand-off prompt is delivered
- [ ] The final message lists the lossy items and contains the full hand-off prompt
