# Bootstrap: port stablehand to OpenCode

Open the stablehand repository root in OpenCode, use the strongest model you have (for example `deepseek/deepseek-v4-pro`), and paste the prompt below. The agent builds `platforms/opencode/` itself, so the result fits OpenCode and the model that will run it.

---

```text
You are porting the "stablehand" toolkit to OpenCode. stablehand is a set of skills and
agents that help people create THEIR OWN project skills and agents. Write all output in
English. Work only inside platforms/opencode/ unless a step says otherwise. Do not commit.
Do the steps in order. After each step, write one line: "Step N done: <what you did>".

Step 1. Read these files completely:
  a) README.md
  b) docs/architecture.md
  c) contracts/README.md, then every file in contracts/skills/ and contracts/agents/
  d) shared/references/opencode.md  (your platform card: the source of truth for
     fields, paths, permission keys and model IDs)
  e) shared/references/writing-for-agents.md, coexistence.md, eval-protocol.md,
     decision-guide.md
  f) platforms/claude-code/skills/*/SKILL.md and platforms/claude-code/agents/*.md
     (one example of meeting each contract; copy the behaviour, not the Claude mechanics)

KEY REQUIREMENT: users open the stablehand repo in OpenCode and ask for a skill or agent
for ANOTHER repository, for example "I need a skill for ../shop-api that ...". Every skill
must do these things first:
  - establish the target repo path and the target platform (shared/references/targets.md);
  - get access to it (the external_directory permission);
  - never write artifacts into stablehand.
Run commands for the target with --dir "<target>".

Step 2. For every contract in contracts/skills/, create
platforms/opencode/skills/<id>/SKILL.md with these rules:
  - Frontmatter keys: only name, description, license, compatibility, metadata.
  - name = the folder name.
  - description: double-quoted, third person, starts with what it does and when to use
    it, ends with "Not for …". At most 500 characters.
  - metadata: set opencode/slash: "true" for every skill (strings, quoted).
  - To load another stablehand skill, write: call the skill tool with name "<id>".
  - To delegate to a stablehand agent, write: use the task tool with the agent "<id>".
  - Reference files: link them as references/<file>.md. List exactly the files named in
    the contract's "references" field. They are copied in at Step 4.
  - The validator lives at skills/validating-artifacts/scripts/lint.py. Other skills
    must name that path explicitly or tell the agent to load validating-artifacts.
  - Real-loader test commands: opencode run "<prompt>" --format json --dir <project>
  - Do not use Claude tool names (Read, Grep, Agent, Skill tool, TodoWrite) or
    ${CLAUDE_...} variables anywhere.
  - Use numbered steps with one action each, exact commands, and exact output templates.

Step 3. For every contract in contracts/agents/, create platforms/opencode/agents/<id>.md:
  - Frontmatter: description, mode: subagent, and permission. No name key and no tools
    key.
  - artifact-reviewer: permission edit: deny, shell: deny, webfetch: deny.
  - platform-researcher: permission edit: deny, shell: deny, webfetch: allow,
    websearch: allow. Set model: deepseek/deepseek-flash.
  - scenario-runner: default permissions. Omit model.
  - The body: copy the contract's inputs, procedure, output template and constraints.

Step 4. From the repo root run:  uv run tools/sync.py

Step 5. Run:  uv run tools/lint.py --platform opencode platforms/opencode
  Fix every error and run it again until there are no errors.
  For each warning, fix it or write the reason into PORT-NOTES.md.

Step 6. Translate evals/scenarios/*.md into platforms/opencode/evals/ (one file per
  scenario, same Expected and Must not, OpenCode run commands). Wire the workspace:
  uv run tools/install.py opencode --scope workspace
  Restart OpenCode in the stablehand folder. Run persona-agents-pushback,
  unrelated-request-no-trigger and external-target-repo (with a scratch target repo
  outside stablehand). Write the results to platforms/opencode/evals/RESULTS.md.

Step 7. Write platforms/opencode/PORT-NOTES.md. Include: the date, the OpenCode version,
  the model used, and for each contract: the mapping decisions, the lossy items, the
  untested behaviour, and every place where the platform card was wrong (with evidence).

Step 8. Update the opencode row in platforms/README.md.

Finish with a short report: files created, lint result, eval results, open problems.
```
