# Bootstrap: port stablehand to OpenAI Codex CLI

Open the stablehand repository root in OpenAI Codex CLI (`codex` or `codex.cmd`), and use the specification below when updating or re-porting `platforms/codex/`.

---

```text
You are porting the "stablehand" toolkit to OpenAI Codex CLI. stablehand is a set of
skills and agents that help people create THEIR OWN project skills and agents. Write all
output in English. Work only inside platforms/codex/ unless a step says otherwise. Do not
commit.

Step 1. Read these files completely:
  a) README.md
  b) docs/architecture.md
  c) contracts/README.md, then every file in contracts/skills/ and contracts/agents/
  d) shared/references/codex.md (your platform card: the source of truth for fields,
     paths, sandbox modes, and CLI flags)
  e) shared/references/writing-for-agents.md, coexistence.md, eval-protocol.md,
     decision-guide.md

KEY REQUIREMENT: users open the stablehand repo in Codex and ask for a skill or agent
for ANOTHER repository, for example "I need a skill for ../shop-api that ...". Every skill
must do these things first:
  - establish the target repo path and the target platform (shared/references/targets.md);
  - get access to it (--add-dir <target> or -C <target>);
  - never write artifacts into stablehand.

Step 2. For every contract in contracts/skills/, create
platforms/codex/skills/<id>/SKILL.md with these rules:
  - Frontmatter keys: only name and description (double-quoted strings).
  - name = the folder name.
  - description: double-quoted, third person, starts with what it does and when to use
    it, ends with "Not for ...". At most 500 characters.
  - To load another stablehand skill, write: invoke `$<id>` (or read its SKILL.md).
  - To delegate to a stablehand subagent, write: spawn `<id>` (defined in .codex/agents/<id>.toml).
  - Reference files: link them as references/<file>.md. List every file named in the
    contract's "references" field. They are copied in at Step 4.
  - The validator lives at skills/validating-artifacts/scripts/lint.py.
  - Headless test command:
    codex exec --ephemeral --json --sandbox read-only -C "<dir>" "<prompt>"
  - Do not use Claude tool names (Read, Grep, Agent, Skill tool, TodoWrite) or
    Antigravity tool names (view_file, invoke_subagent, etc.) anywhere.

Step 3. For every contract in contracts/agents/, create platforms/codex/agents/<id>.toml:
  - Format: standalone TOML with name, description, sandbox_mode,
    model_reasoning_effort, and developer_instructions.
  - artifact-reviewer: sandbox_mode = "read-only", model_reasoning_effort = "high".
  - platform-researcher: sandbox_mode = "read-only", model_reasoning_effort = "low".
  - scenario-runner: sandbox_mode = "workspace-write", model_reasoning_effort = "medium".
  - Copy the contract's inputs, procedure, output template, and constraints into
    developer_instructions.

Step 4. From the repo root run:  uv run tools/sync.py

Step 5. Run:  uv run tools/lint.py --platform codex platforms/codex --strict
  Fix every error and warning until clean.

Step 6. Run smoke/eval tests in a scratch target repo using:
  uv run tools/install.py codex --scope project --project <scratch>
  and codex exec --ephemeral --sandbox read-only --skip-git-repo-check -C <scratch> "..."

Step 7. Write platforms/codex/PORT-NOTES.md.

Step 8. Update the codex row in platforms/README.md.
```
