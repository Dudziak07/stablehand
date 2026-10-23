---
type: llm
weight: 2
focus:
  source: file
  path: shop-api/.claude/skills/adding-endpoints/SKILL.md
---

The target repo's real conventions are:
- routers in `src/routes/<resource>.ts`, registered in `src/server.ts`;
- zod schemas in `src/schemas/<resource>.ts`;
- tests in `tests/<resource>.test.ts` with vitest and supertest;
- one test file runs with `pnpm vitest run tests/<resource>.test.ts`.

PASS if the skill is a short procedure built on these conventions, with a description that says when to use it.

FAIL if it adds generic Express or REST advice, invents conventions or tools the repo does not have (for example a different validation library, folder layout or test runner), or summarizes the workflow in its description.
