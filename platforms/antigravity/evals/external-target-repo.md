---
id: external-target-repo
kind: behavior
runs: 3
targets: [authoring-skills]
---
## Prompt
I need a skill named `adding-endpoints` for the repository in `./shop-api` that adds a new REST endpoint the way that repo does it. Work non-interactively: don't ask me questions, skip baseline runs, and write the files directly.

## Setup
A folder `shop-api/`, separate from the working directory in real use. It is a small Express + Vitest repo. Its README states the conventions:
- routers in `src/routes/<resource>.ts`, registered in `src/server.ts`;
- zod schemas in `src/schemas/<resource>.ts`;
- tests in `tests/<resource>.test.ts`;
- a single test file runs with `pnpm vitest run tests/<resource>.test.ts`.

## Antigravity Run Instructions
Execute with `agy` or in an Antigravity session with stablehand enabled:
```bash
agy -p "I need a skill named \`adding-endpoints\` for the repository in \`./shop-api\` that adds a new REST endpoint the way that repo does it. Work non-interactively: don't ask me questions, skip baseline runs, and write the files directly." --output-format json
```

## Expected (all must hold)
- `authoring-skills` is loaded (e.g. `/stablehand:authoring-skills`). *(mechanism: with-artifact arm only)*
- The skill is created **inside the target**, at `shop-api/.agents/skills/adding-endpoints/SKILL.md` (or `shop-api/.agents/plugins/stablehand/skills/...`). Nothing is written to the working directory's own skill folders.
- The skill encodes the target's real conventions: the routes, schemas and tests paths, and the single-test command. It contains no generic Express advice.
- The final message names the created path and says the skill is untested, because baseline runs were skipped on request.

## Must not
- Write the skill outside `shop-api/`.
- Invent conventions that are not in the target repo.

## Checks
- deterministic:
  - a file was created matching `shop-api/.agents/skills/*/SKILL.md` (or plugin equivalent);
  - no file matching `.agents/skills/*/SKILL.md` was created at the working directory root.
- judge: PASS if the skill uses `src/routes/`, `src/schemas/`, `tests/<resource>.test.ts` and the single-test command, and the final message gives the path and says it is untested. FAIL otherwise.
