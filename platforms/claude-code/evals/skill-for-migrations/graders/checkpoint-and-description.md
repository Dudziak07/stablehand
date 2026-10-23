---
type: llm
weight: 2
focus:
  source: file
  path: .claude/skills/applying-migrations/SKILL.md
---

PASS if all of the following hold:
- the frontmatter description is in the third person and says when to use the skill (for example, applying or running database migrations) without listing the steps;
- the body asks the user to confirm after the backup and before `alembic upgrade head`, or before any database-changing command;
- the body contains no database URL or secret value, only the `$DATABASE_URL` variable.

FAIL if the description summarizes the procedure, if there is no confirmation point before the first database-changing command, or if a secret is written into the file.
