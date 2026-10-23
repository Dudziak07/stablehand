# Bootstrap: port stablehand to Antigravity

Open the stablehand repository root in Antigravity (App or CLI `agy`, with a `pro` model if you can) and paste the prompt below. The agent builds `platforms/antigravity/` itself: it knows Antigravity's dialect and can test the result there.

---

```text
You are porting the "stablehand" toolkit to Google Antigravity. stablehand is a set of
skills and agents that help people create THEIR OWN project skills and agents. Work only
inside platforms/antigravity/ unless a step says otherwise. Do not commit.

1. Read, in this order:
   - README.md and docs/architecture.md
   - contracts/README.md, then every file in contracts/skills/ and contracts/agents/
   - shared/references/antigravity.md (your platform card — the source of truth for fields,
     paths, tool names), shared/references/writing-for-agents.md, coexistence.md,
     eval-protocol.md, decision-guide.md
   - the reference implementation in platforms/claude-code/ (skills/*/SKILL.md, agents/*.md)
     to see one way of meeting each contract. Port the BEHAVIOUR, not the Claude mechanics.

   KEY REQUIREMENT: users open the stablehand repo in Antigravity and ask for a skill or agent
   for ANOTHER repository ("I need a skill for ../shop-api that ..."). Every skill must first
   establish the target repo path, access to it (shared/references/targets.md) and the target
   platform, and must never write artifacts into stablehand. Find out how Antigravity reads
   and writes a folder outside the workspace on this version, and record it in PORT-NOTES.md.

2. For every contract in contracts/skills/, create platforms/antigravity/skills/<id>/SKILL.md:
   - frontmatter: name (= folder), description (double-quoted, third person, triggers first,
     "Not for …" clause, <= 500 chars). Use disable-slash-command only where the Claude
     version uses user-invocable: false. Nothing else unless the card supports it.
   - Loading another stablehand skill: tell the agent to invoke /stablehand:<id>, or to read
     that skill's SKILL.md by path. Never just mention its name.
   - Delegating to a stablehand agent: use invoke_subagent with the agent name.
   - Reference files: link them as references/<file>.md (they are copied in by step 4).
     List exactly the files named in the contract's "references" field.
   - The validator: the skill validating-artifacts runs `uv run scripts/lint.py ...` from its
     own folder; other skills tell the agent to run that script by its path in the
     validating-artifacts skill folder, or to invoke /stablehand:validating-artifacts.
   - Real-loader test commands: use `agy -p "<prompt>" --output-format json` (see the card).
   - Explicit stop conditions and output formats (Gemini benefits from them).

3. For every contract in contracts/agents/, create platforms/antigravity/agents/<id>.md:
   - name, description, tools (ONLY exact names from the card's section 5 — an unknown tool
     name can hang the agent), model (inherit|flash|pro), subagent: true, mainAgent: false.
   - artifact-reviewer and platform-researcher must be read-only (no write/replace/run tools;
     researcher gets search_web and read_url_content).
   - scenario-runner gets the default working tool set.

4. From the repo root run:  uv run tools/sync.py
   This copies the references into each skill and the linter into validating-artifacts.

5. Lint until clean:  uv run tools/lint.py --platform antigravity platforms/antigravity
   Fix every error. Fix or justify every warning in PORT-NOTES.md.

6. Translate evals/scenarios/*.md into platforms/antigravity/evals/ (one file per scenario,
   same Expected/Must-not, Antigravity-specific run instructions). Wire the workspace
   (uv run tools/install.py antigravity --scope workspace), reload, and actually run at least
   persona-agents-pushback, unrelated-request-no-trigger and external-target-repo (with a
   scratch target repo outside stablehand). Record the results in
   platforms/antigravity/evals/RESULTS.md.

7. Write platforms/antigravity/PORT-NOTES.md: date, Antigravity versions (App/IDE/CLI),
   per contract: mapping decisions, lossy items, untested behaviour, and any place where
   the platform card turned out to be wrong (quote the evidence).

8. Update the antigravity row in platforms/README.md (status, contract version).

Finish with a short report: files created, lint result, eval results, open problems.
```
