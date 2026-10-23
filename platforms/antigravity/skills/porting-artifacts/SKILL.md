---
name: porting-artifacts
description: "Ports skills, subagents or instruction files between Google Antigravity, Claude Code and OpenCode, preserving behavior while translating fields, tools, model tiers, paths and invocation syntax. Use when asked to port, convert, adapt or migrate an agent or skill to another platform, or when bootstrapping a new platform folder. Not for authoring new artifacts from scratch or same-platform edits."
---
<!-- stablehand-lint: ignore S024 -->

A port preserves the behavior contract while adapting to native mechanics. Nothing naming the source platform's tools or syntax may remain in the result, and permissions must never become more permissive.

Reference material (read source and target cards before mapping):
- `references/antigravity.md`: Antigravity fields, exact tool names, model tiers, and limits.
- `references/claude-code.md`: Claude Code conventions, tools, and frontmatter.
- `references/opencode.md`: OpenCode conventions, permissions, and modes.
- `references/coexistence.md`: safe placement preventing cross-platform contamination.
- `references/writing-for-agents.md`: model calibration and output formats.
- `references/targets.md`: establishing the destination repository and access.

## Process

0. **Target.** Establish where the port goes: a target repository or a stablehand `platforms/<target>/` folder, and access to it (`references/targets.md`). Never write a project's port into stablehand. In Antigravity, `run_command` requires the target repository to be within the active workspace (add the target folder to the workspace as a multi-root workspace folder) if commands will be executed in it.
   - **Confirmation.** Confirm in one line: `Target: <path> · Platform: <platform> · Building: port of <artifact> to <target platform>`.

1. **Identify** source artifact(s), source platform, target platform, and destination path (target repository or stablehand `platforms/<target>/`). If a card may be stale for the fields involved, delegate to `platform-researcher` using `invoke_subagent`.

2. **Extract the contract.**
   - Use the contract if available (`contracts/<kind>/<id>.md`).
   - Otherwise summarize in ≤ 10 lines: purpose, triggers, inputs, outputs, must-nots, and permissions.

3. **Map field-by-field** using platform card tables:
   - **Frontmatter.** Retain supported fields; translate equivalents; document dropped fields as **lossy**. Examples:
     - Claude `disable-model-invocation: true` → OpenCode `metadata.opencode/autoinvoke: "false"`; Antigravity: state "run only when requested" in the description.
     - Claude `user-invocable: false` → Antigravity `disable-slash-command: true`.
   - **Tools.** Map capabilities to target names:
     - Read-only: every write, shell and network capability is denied unless the source explicitly allowed it. Claude `Read, Grep, Glob` → Antigravity `[view_file, grep_search, find_by_name, list_dir]` → OpenCode `permission` with `edit: deny`, `bash: deny`, `shell: deny`, `webfetch: deny`, `websearch: deny`, `task: deny` (`bash` and `shell` always together, see the OpenCode card).
     - A restricted shell (a Claude hook or the source's intent such as "only `git diff`") becomes an exact allow-list on OpenCode, e.g. `bash` and `shell` both set to `{"*": deny, "git diff --staged": allow, "git diff --staged -- *": allow}`. Allow only these exact patterns: no `"git diff"` with a trailing `*` or ` *`, because any trailing wildcard admits writing flags such as `git diff --output=<file>`.
     - Write/execute access maps the same way. Read-only must stay read-only.
   - **Model tier (order: Claude / Antigravity / OpenCode):**
     - same as caller → `inherit` / `inherit` / omit;
     - fast → `haiku` / `flash` / `deepseek/deepseek-flash`;
     - strongest → `opus` / `pro` / `deepseek/deepseek-v4-pro`.
   - **Invocation syntax in body:**
     - loading a skill: Claude Skill tool → Antigravity "invoke `/<skill>` or read its `SKILL.md`" → OpenCode "call skill tool with name";
     - delegation: Claude Agent tool → Antigravity `invoke_subagent` / `@<agent>` → OpenCode Task tool / `@<agent>`.
   - **Paths.** Replace platform-specific variables with explicit relative paths (e.g., "the script in `scripts/<name>.py` inside this skill").
   - **Placement.** Consult `references/coexistence.md` to avoid unintentional loading.

4. **Calibrate** for the target model (`references/writing-for-agents.md`):
   - Gemini (Antigravity): double-quote every frontmatter string, state clear stop conditions and structured output templates.
   - DeepSeek (OpenCode): numbered single-action steps, exact commands, explicit language.

5. **Validate** using the target platform's rules:
   Determine the absolute path to `../validating-artifacts/scripts/lint.py` resolved from the directory containing this `SKILL.md`. Run:
   `uv run "<absolute-path-to-scripts/lint.py>" --platform <target> "<paths>"`
   or invoke `/stablehand:validating-artifacts`.

6. **Write `PORT-NOTES.md`** alongside the result. Include:
   - source path, version, and date;
   - mapping decisions;
   - lossy items;
   - untested behavior.

7. **Hand off testing.** Always provide a ready-to-paste test prompt for running the evals on the target platform:
   "Run the eval scenarios in `<path>` following `eval-protocol.md`, using `<target runner command>`, and report the results table."

8. **Report in the final message.** `PORT-NOTES.md` is the record, not a substitute for the report. A pointer such as "see PORT-NOTES.md" is not enough. End with:
   ```
   Ported: <path of each ported artifact>
   Lossy:
   - <field or capability>: <mapped to … | dropped, because …>   (or "none")
   Untested on <target> until this prompt is run there:
   <the full hand-off prompt from step 7>
   ```

## Porting stablehand itself
To bring stablehand to another platform, follow `platforms/<target>/BOOTSTRAP.md` in the stablehand repository.

## Done when
- [ ] The target validator reports zero errors
- [ ] Every source capability is mapped or listed as lossy in PORT-NOTES.md
- [ ] No source platform tool names or syntax remain in the body
- [ ] Permissions are equal to or stricter than the source
- [ ] The test hand-off prompt is delivered
- [ ] The final message lists the lossy items and contains the full hand-off prompt
- [ ] Never claim the port works without a run on the target platform
