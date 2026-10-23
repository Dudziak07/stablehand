---
id: external-target-repo
kind: behavior
runs: 3
targets: [authoring-skills]
---

## Prompt
I need a skill named `adding-endpoints` for the repository in `./shop-api` that adds a new REST endpoint the way that repo does it. Work non-interactively: don't ask me questions, skip baseline runs, and write the files directly.

## Setup
A folder `shop-api/`, a scratch copy outside the stablehand checkout. It is a small Express + Vitest repo. Its README states the conventions:
- routers in `src/routes/<resource>.ts`, registered in `src/server.ts`;
- zod schemas in `src/schemas/<resource>.ts`;
- tests in `tests/<resource>.test.ts`;
- a single test file runs with `pnpm vitest run tests/<resource>.test.ts`.

Create it under the OS temp directory and pass its **absolute** path in the prompt. The run uses `--dir "<stablehand-checkout>"`, so the stablehand skills are on the discovery path, and the target is reached through the `external_directory` permission.

## Expected (all must hold)
- `authoring-skills` is loaded.
- The skill is created **inside the target**, at `shop-api/.opencode/skills/adding-endpoints/SKILL.md`. Nothing is written to the stablehand checkout or to the working directory's own skill folders.
- The skill encodes the target's real conventions: the routes, schemas and tests paths, and the single-test command. It contains no generic Express advice.
- The final message names the created path and says the skill is untested, because baseline runs were skipped on request.

## Must not
- Write the skill outside `shop-api/`.
- Invent conventions that are not in the target repo.

## OpenCode run
```
opencode run "I need a skill named adding-endpoints for the repository at <absolute scratch target path> that adds a new REST endpoint the way that repo does it. Work non-interactively: don't ask me questions, skip baseline runs, and write the files directly." \
  --format json --dir "<stablehand-checkout>" --model deepseek/deepseek-flash --auto
```
`--auto` approves the `external_directory` prompt; the target is a scratch copy, and the clean-status check below proves nothing landed in stablehand.

## Checks
- deterministic:
  - a file was created matching `shop-api/.opencode/skills/*/SKILL.md`;
  - none matching `.opencode/skills/*/SKILL.md` at the stablehand checkout root;
  - `git -C "<stablehand-checkout>" status --porcelain` is empty after the run.
- judge: PASS if the skill uses `src/routes/`, `src/schemas/`, `tests/<resource>.test.ts` and the single-test command, and the final message gives the path and says it is untested. FAIL otherwise.
