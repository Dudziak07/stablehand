---
id: writing-project-instructions
kind: skill
version: 2026.10.0
references: [targets.md, coexistence.md, writing-for-agents.md, "@all-platforms"]
---
# writing-project-instructions

## Purpose
Write, trim or audit a project's always-loaded instructions (AGENTS.md, CLAUDE.md, rule files) so that they hold only what the agent cannot infer from the repository.

## Triggers
- **Should:**
  - "write/update/shorten our AGENTS.md / CLAUDE.md";
  - "add a rule for the migrations folder";
  - "/init made a huge file, clean it up";
  - "set up instructions shared by Claude and OpenCode".
- **Should not:**
  - procedures needed only for some tasks (they belong in `authoring-skills`);
  - README or end-user documentation.

## Inputs
- The target repository path.
- The platforms that open the repo.
- Facts the user wants enforced.

## Procedure
0. **Target.** Establish the target repo and access to it, following `targets.md`. Never write into stablehand.
1. **Inventory:**
   - existing instruction and rule files on all platforms;
   - README;
   - manifests and scripts;
   - CI configuration.
2. **Collect candidate facts.** Look for these categories:
   - commands (build, test, a single test, lint, format);
   - non-obvious conventions;
   - boundaries (never edit X, always use Y);
   - gotchas from real incidents;
   - pointers to where things live.
3. **Filter.** Remove anything inferable from the code, general good practice, and procedures (those become skills, at most with a one-line pointer). Verify each command against the repository; run it when safe.
4. **Choose files** with `coexistence.md`:
   - AGENTS.md as the shared canonical file when more than one platform is used;
   - a platform file only for platform-only facts, with the bridge (Claude: CLAUDE.md starting with `@AGENTS.md`);
   - path-scoped rules for path-specific facts.
5. **Write.** Use short imperative lines grouped under a few headings. Target ≤ 150 lines in total; the always-on budget is shared with every task.
6. **Test.** In a fresh session, ask 3 questions the file should answer. Examples: "what command runs one test?", "may I edit generated files?". Check the answers.

## Outputs
- The instruction and rule files.
- A short list of what was removed, and why.

## Done when
- Every line is a non-inferable fact or a pointer.
- The commands have been verified.
- The size is within budget.
- The bridges between platforms are correct.
- The fresh-session questions are answered correctly.

## Must not
- Paste procedures, style guides or README content into always-loaded files.
- Create CLAUDE.md beside AGENTS.md without the `@AGENTS.md` bridge.
- Add YAML frontmatter to AGENTS.md.
- Leave unverified commands.

## Platform adaptation
- **Files and rule formats:**
  - Claude: `.claude/rules/*.md` with `paths:`.
  - Antigravity: `.agents/rules/*.md` with `trigger:`, under a 20k-token always-on budget.
  - OpenCode: AGENTS.md, plus `instructions` in `opencode.json`.
- **The fresh-session test command**, using each platform's headless runner.

## Evals
`agents-md-minimal`
