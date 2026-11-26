---
name: "porting-artifacts"
description: "Ports a skill, subagent, or instruction file between OpenAI Codex CLI, Claude Code, Antigravity, and OpenCode, preserving behavior while rewriting fields, sandbox/permissions, model tiers, and invocation syntax. Use when porting, adapting, or migrating artifacts between platforms. Not for new artifacts or same-platform edits."
---

A port keeps the contract and changes the mechanics. Nothing that names the source platform's tools or syntax may survive in the result, and nothing that was restricted may become permissive. Write all output in English.

Reference material (read source and target cards before mapping):
- `references/codex.md`
- `references/claude-code.md`
- `references/antigravity.md`
- `references/opencode.md`
- `references/coexistence.md`: placement without cross-loading.
- `references/writing-for-agents.md`: model calibration for the target.
- `references/targets.md`: target repo and access.

## Process

1. **Identify** source artifact(s), source platform, target platform, and target folder (`references/targets.md`). Confirm: `Target: <path> · Platform: <target platform> · Building: <what>`. If a card may be stale, spawn `platform-researcher` first.
2. **Extract the contract** from `contracts/<kind>/<id>.md` if present, or write a <= 10-line contract (purpose, triggers, inputs, outputs, must-nots, permissions).
3. **Map field by field** using the source and target cards:
   - **Agent format:** Markdown frontmatter (`claude-code`, `antigravity`, `opencode`) <-> TOML (`codex`: `name`, `description`, `developer_instructions`, `sandbox_mode`, `model_reasoning_effort`).
   - **Permissions / sandbox:** keep read-only sources read-only (`sandbox_mode = "read-only"` on Codex; `permissions` deny-all on OpenCode; read-only tool lists on Claude/Antigravity). Record any dropped fine-grained rule as lossy.
   - **Model tier:** `inherit` (omit `model` in Codex) | fast (`flash`/`flash_lite`/`haiku`/Codex `model_reasoning_effort = "low"`) | strongest (`pro`/`opus`/Codex `model_reasoning_effort = "high"`).
   - **Invocation & paths:** rewrite skill/subagent invocation syntax and replace platform variables with explicit relative paths.
   - **Placement:** follow `references/coexistence.md` so the source platform does not accidentally load the port.
4. **Calibrate** (`references/writing-for-agents.md`) for the target model family.
5. **Validate** by invoking `$validating-artifacts` with `--platform <target>` and fix all errors.
6. **Write `PORT-NOTES.md`** next to the result (source, date, mapping decisions, lossy items, untested behavior).
7. **Hand off testing** with a full ready-to-paste prompt for the target platform's agent to run evals there.
8. **Report** in the final message: ported paths, every lossy item (or `"none"`), and the full hand-off prompt verbatim.

## Done when
- [ ] Target validator exits 0 with no errors
- [ ] Every capability is mapped or listed as lossy in `PORT-NOTES.md` and the final message
- [ ] No source-platform tool names or invocation syntax remain, and permissions are equal or stricter
- [ ] Full test hand-off prompt is included in the final message
