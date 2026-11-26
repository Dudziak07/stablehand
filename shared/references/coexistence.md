# Coexistence: projects used by more than one platform

The platforms read each other's folders. A skill tailored for one platform can leak into another, and OpenCode rejects duplicate skill names. Read this before placing artifacts in a repository that more than one harness opens.

Last verified: 2026-10-21 (Antigravity paths re-verified 2026-11-21; OpenCode re-verified 2026-11-22 on v2.3.2; Codex verified 2026-11-26 on codex-cli 0.172.0; sources in each platform card).

## Who reads what — project scope

| Path | Claude Code | Antigravity | OpenCode | Codex |
|---|---|---|---|---|
| `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` | yes | no | `CLAUDE.md` only as fallback when no `AGENTS.md` exists | no |
| `AGENTS.md` | yes, **only if no CLAUDE.md** sits in the same directory (v2.1.277+ default) | yes (also `.agents/AGENTS.md`) | yes | yes (also `AGENTS.override.md`) |
| `AGENTS.override.md` | no | no | no | yes (overrides sibling `AGENTS.md`) |
| `GEMINI.md` | no | yes | no | no |
| `.claude/rules/*.md` | yes | no | no (unless listed in `instructions`) | no |
| `.agents/rules/*.md` | no | yes | no | no |
| `.claude/skills/` | yes | no | **yes** (disable with `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`) | no |
| `.agents/skills/` | **no** | yes | **yes** | **yes** |
| `.opencode/skills/` | no | no | yes | no |
| `.agents/plugins/<p>/` | no | yes (namespaced `/<p>:<skill>`) | no | no (Codex uses `.agents/plugins/marketplace.json`) |
| `.claude/agents/` | yes (Cursor and VS Code read it too) | no | no | no |
| `.agents/agents/` | no | yes | no | no |
| `.opencode/agents/` | no | no | yes | no |
| `.codex/agents/*.toml` | no | no | no | yes |
| `.codex/config.toml` | no | no | no | yes |
| `.agent/` (singular, legacy) | no | legacy, still read | no | no |

## Who reads what — user scope

| Path | Claude Code | Antigravity | OpenCode | Codex |
|---|---|---|---|---|
| `~/.claude/CLAUDE.md` | yes | no | fallback when `~/.config/opencode/AGENTS.md` is missing (disable: `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1`) | no |
| `~/.claude/skills/` | yes | no | **yes** (disable: `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`) | no |
| `~/.claude/agents/` | yes | no | no | no |
| Claude plugin cache (`~/.claude/plugins/cache/…`) | yes | no | no | no |
| `~/.agents/skills/` | no | no | yes | yes |
| `~/.gemini/config/{skills,agents,rules,plugins}`, `~/.gemini/config/{AGENTS,GEMINI}.md`, `~/.gemini/{AGENTS,GEMINI}.md` (CLI also loads `~/.gemini/antigravity-cli/skills/` and `~/.gemini/skills/`; prefer `~/.gemini/config/` so App and CLI share them) | no | yes | no | no |
| `~/.config/opencode/{skills,agents,AGENTS.md}` | no | no | yes | no |
| `~/.codex/{agents/*.toml,AGENTS.md,config.toml}` | no | no | no | yes |

`OPENCODE_DISABLE_CLAUDE_CODE=1` turns off all `.claude` compatibility in OpenCode at once.

## Collision rules

1. **OpenCode allows duplicate skill IDs** across `.opencode/skills`, `.claude/skills`, `.agents/skills` and their user-level counterparts, and the later-registered source wins (override): built-in < `.claude/skills` < `.agents/skills` < `~/.config/opencode/skills` < project `.opencode/skills` < explicit `skills` entries. Two tailored variants with the same ID still fight over that ID, so keep them apart or hide one.
2. **`.agents/skills` is shared by Antigravity, OpenCode, and Codex.** Anything placed there must work on all of them that open the repo, or be kept in another platform's native directory (`.agents/plugins/<p>/` for Antigravity, `.opencode/skills/` for OpenCode).
3. **Claude Code ignores AGENTS.md when CLAUDE.md exists** in the same directory (default mode). If both files are needed, start CLAUDE.md with `@AGENTS.md`.

## Recommended layouts

### Single platform
Use only that platform's native folders (see its card). Nothing else to do.

### Several platforms, tailored variants (stablehand's default)

| Platform | Skills | Agents | Instructions |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `.claude/agents/` | `CLAUDE.md` that starts with `@AGENTS.md` (or only AGENTS.md) |
| Antigravity | workspace plugin `.agents/plugins/<set>/skills/` — keeps them out of OpenCode's and Codex's view | `.agents/plugins/<set>/agents/` (App/CLI) or `.agents/agents/` | `AGENTS.md` (+ `.agents/rules/` for scoped rules) |
| OpenCode | `.opencode/skills/` | `.opencode/agents/` | `AGENTS.md` |
| Codex | `.agents/skills/` (if portable/Codex-only; keep `.opencode/skills/` for OpenCode) | `.codex/agents/*.toml` | `AGENTS.md` (+ `AGENTS.override.md`) |

Plus: run OpenCode with `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` so it doesn't also load the Claude variants. When Codex and OpenCode share a repo, keep OpenCode-specific skills in `.opencode/skills/` (which overrides `.agents/skills/`) and Codex skills in `.agents/skills/`.

### Several platforms, one portable version

When a skill's text is genuinely identical everywhere (no tool names, no platform invocation syntax):
- put it in `.agents/skills/` (Antigravity + OpenCode + Codex) **and** `.claude/skills/` (Claude Code);
- run OpenCode with `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` so it sees one copy.

Agents are never portable as files (fields, tool names, file format — Markdown vs TOML — and model values differ); always generate one file per platform.

## Installing stablehand itself
Claude Code gets it as a plugin, Antigravity as a plugin under `~/.gemini/config/plugins/` (or `.agents/plugins/` in workspace), OpenCode gets copies/links in `~/.config/opencode/` (or `.opencode/`), and Codex gets skills in `~/.agents/skills/` (or `.agents/skills/`) and TOML agents in `~/.codex/agents/` (or `.codex/agents/`). Note that OpenCode also reads `~/.agents/skills/` and `.agents/skills/`, so installing stablehand for both OpenCode and Codex in the same scope means OpenCode will see Codex's `.agents/skills/` variants alongside `.opencode/skills/`.
