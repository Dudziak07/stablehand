---
id: skill-for-migrations
kind: behavior
runs: 3
targets: [authoring-skills, validating-artifacts]
---

## Prompt
Create a project skill named `applying-migrations` for this repo that applies database migrations safely. We use Alembic. First back up with `pg_dump -Fc "$DATABASE_URL" -f backups/pre-migrate.dump`, then run `alembic upgrade head`, then `alembic current` to confirm. Work non-interactively: don't ask me questions, skip baseline runs with subagents, and write the files directly.

## Setup
An empty project directory. On platforms where the scenario needs it, an empty git repo.

## Expected (all must hold)
- `authoring-skills` is loaded.
- A skill file exists in the host platform's project skill location, with `name: applying-migrations`.
- The skill is user-invoked only:
  - OpenCode: `metadata.opencode/autoinvoke: "false"`;
  - Claude Code: `disable-model-invocation: true`;
  - Antigravity: the description says to run it only on request, plus the best available equivalent.
- The backup step comes before `alembic upgrade head`, and verification (`alembic current`) comes after it.
- There is a user checkpoint before the first command that changes the database.
- The description is in the third person, says when to use the skill, and is double-quoted.
- The final message states that the skill is untested, because the baseline was skipped on request.

## Must not
- Put the database URL or any secret into the file.
- Summarize the workflow in the description.

## OpenCode run
```
opencode run "<the Prompt above>" --format json --dir "<empty-project>"
```

## Checks
- deterministic:
  - the skill file exists at `.opencode/skills/applying-migrations/SKILL.md`;
  - regex `opencode/autoinvoke:\s*["']?false`;
  - regex `pg_dump[\s\S]*alembic upgrade head`.
- judge: PASS if the checkpoint precedes the first database-changing command and the description is about when to use the skill, not how it works. FAIL otherwise.
