---
name: porting-artifacts
description: "Ports a skill, subagent or instruction file between OpenCode, Claude Code and Antigravity, keeping its behavior while rewriting fields, tool names, model tiers, paths and invocation syntax for the target. Use when asked to port, convert, adapt or migrate an agent or skill to another platform, or to start a new platform folder in stablehand. Not for creating new artifacts or same-platform edits."
metadata:
  opencode/slash: "true"
---
<!-- stablehand-lint: ignore S024 -->

A port keeps the contract and changes the mechanics. Nothing that names the source platform's tools or syntax may survive in the result, and nothing that was restricted may become permissive. Write all output in English.

Reference material (read the source and target cards in full before mapping):
- `references/opencode.md`
- `references/claude-code.md`
- `references/antigravity.md`
- `references/coexistence.md`: where the port may live without leaking into other platforms.
- `references/writing-for-agents.md`: model calibration for the target.
- `references/targets.md`: the target repo and access to it.

## Process

1. **Identify** the source artifact(s), the source platform, the target platform, and the target folder (a project or a stablehand `platforms/<target>/` folder). If a card may be stale for the fields involved, use the task tool with the agent `platform-researcher` before mapping.
   - Confirm in one line: `Target: <path> · Platform: <target platform> · Building: <what>`.
   - Access: if the target is outside the workspace, approve the `external_directory` prompt.

2. **Extract the contract.**
   - Use the existing one if there is one (stablehand: `contracts/<kind>/<id>.md`).
   - Otherwise write at most 10 lines from the source: purpose, triggers, inputs, outputs, must-nots, and for agents the permissions it has.

3. **Map**, field by field, using the cards' tables:
   - **Frontmatter.** Keep supported fields; translate the equivalents; record dropped fields as **lossy**. Examples:
     - Claude `disable-model-invocation: true` maps to OpenCode `metadata.opencode/autoinvoke: "false"`; Antigravity has no exact equivalent (state "run only when asked" in the description).
     - Claude `user-invocable: false` maps to Antigravity `disable-slash-command: true`.
   - **Tools.** Abstract capability to target names. Read-only means `edit`, `bash`/`shell`, `webfetch`, `websearch` and `task` are denied unless the source explicitly allowed them:
     - Claude `Read, Grep, Glob` maps to Antigravity `[view_file, grep_search, find_by_name]` and to OpenCode `permission: {edit: deny, bash: deny, shell: deny, webfetch: deny, websearch: deny, task: deny}`.
     - Write or execute access maps the same way. A restricted source shell becomes an exact allow-list on the target. Keep every pattern exact: never use a trailing wildcard such as `git diff*` or `git log *`, which also admits `--output=<file>`. For OpenCode, write **both** `bash` and `shell` with the card's reviewer example: `"*": deny`, then `"git diff --staged": allow` and `"git diff --staged -- *": allow`. OpenCode 1.19.3 enforces only `bash` and silently ignores `shell`.
   - **Model tier:**
     - same as the caller: inherit, inherit, omit;
     - fast: `haiku`, `flash`, `deepseek/deepseek-flash`;
     - strongest: `opus`, `pro`, `deepseek/deepseek-v4-pro`.
   - **Invocation syntax in the body:**
     - loading a skill: Claude's dedicated skill-loading step becomes Antigravity "invoke `/x`, or read its SKILL.md" and OpenCode "call the skill tool with name `x`";
     - delegation: Claude's delegation tool becomes `invoke_subagent` or `@x` in Antigravity, and the task tool or `@x` in OpenCode.
   - **Paths.** Replace the source platform's skill-dir and plugin-root variables, and its argument placeholders, with paths relative to the skill folder, stated explicitly ("the script `scripts/<name>.py` in this skill's folder").
   - **Placement.** Choose the target location from `references/coexistence.md`, so the port is not also loaded by another platform.

4. **Calibrate** for the target model (see `references/writing-for-agents.md`):
   - DeepSeek (OpenCode): numbered single-action steps, exact commands, output templates, an explicit output language.
   - Antigravity: double-quote every frontmatter string, and give explicit stop conditions.

5. **Validate** with the target platform's rules: call the skill tool with name `validating-artifacts`, and tell it the paths and `--platform <target>`. For Antigravity agents, an unknown tool name is an error: it can hang the agent.

6. **Write `PORT-NOTES.md`** next to the result (for a stablehand port: `platforms/<target>/PORT-NOTES.md`). Record:
   - source path and version;
   - the date;
   - mapping decisions;
   - lossy items;
   - behavior not yet tested on the target.

7. **Hand off testing.** You cannot run the target platform from here. Give the user a ready-to-paste prompt for the target agent: "Run the eval scenarios in <path> following the eval protocol bundled with the `evaluating-artifacts` skill, using the runner command for the target, and report the results table."

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
