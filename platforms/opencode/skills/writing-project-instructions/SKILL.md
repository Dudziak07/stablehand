---
name: writing-project-instructions
description: "Writes, trims or audits the always-loaded instructions of a given repository (AGENTS.md, CLAUDE.md, rules) so they hold only facts the agent cannot infer from the code. Use when asked to create, update, shorten or clean up AGENTS.md or CLAUDE.md for this or another repo, add a path-specific rule, or share instructions between OpenCode and other agents. Not for task procedures (use authoring-skills) or human docs."
metadata:
  opencode/slash: "true"
---

Every line in an always-loaded file costs context on every task. Keep only facts the agent cannot infer from the repo, and verify every command you write down. Write all output in English.

Reference material:
- `references/targets.md`: the target repo and access to it.
- `references/opencode.md`, section 1: the instruction files OpenCode reads, the `instructions` array, and the Claude fallback.
- `references/coexistence.md`: which file each platform reads, and the CLAUDE.md to AGENTS.md bridge.
- `references/writing-for-agents.md`: what to leave out.
- `references/claude-code.md` and `references/antigravity.md`: read the matching one when the repo is also opened by that platform.

## Process

0. **Target.**
   - Target repo: take it from the request. If it is missing, ask. Use the current directory only if it is not the stablehand repo. Never write into stablehand.
   - Access: if the target is outside the workspace, approve the `external_directory` prompt.
   - Commands: for `opencode run`, pass `--dir "<target-or-scratch>"`. For every other command that runs the target's code, use `cd "<target>" && <command>`; do not pass `--project "<target>"` to `uv run` from the stablehand folder.
   - Confirm in one line: `Target: <path> · Platform: <platform> · Building: <what>`.

1. **Inventory the target.** Read the existing `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/`, `.agents/rules/`, the README, manifests and scripts, and CI. Ask which agent platforms open the repo, if that is not known.

2. **Collect candidate facts**:
   - Commands: build, test, a single test, lint, format, run locally.
   - Non-obvious conventions: naming, layering, error handling the code does not make evident.
   - Boundaries: never edit generated files or migrations by hand; secrets live in X.
   - Gotchas from real incidents, with the symptom.
   - Pointers: where docs, specs or fixtures live.

3. **Filter.** Remove:
   - anything inferable from the code or config;
   - general good practice ("write clean code");
   - tutorials;
   - procedures used only for some tasks. These become skills; leave at most a one-line pointer.

   Verify each command against the scripts; run it when it is safe and fast.

4. **Choose files** (see `references/coexistence.md`):
   - **OpenCode only:** `AGENTS.md`.
   - **Shared with Claude Code or Antigravity:** `AGENTS.md` is canonical. Claude Code reads AGENTS.md only when no CLAUDE.md is in that directory. If Claude-only facts are needed, create `CLAUDE.md` starting with `@AGENTS.md`, then the Claude-only lines.
   - **Facts for some paths only:** for OpenCode, list extra files in the `instructions` array in `opencode.json`. For Claude Code, use `.claude/rules/<topic>.md` with frontmatter `paths: ["migrations/**"]`. For Antigravity, use `.agents/rules/<topic>.md` with `trigger: glob` and `globs:`.
   - **Personal, not shared:** a gitignored file, or a local `instructions` entry.

5. **Write.** Use short imperative lines under a few headings (Commands, Conventions, Boundaries, Gotchas). Target at most 150 lines in total; long context files cost more than they help. No frontmatter in AGENTS.md.

6. **Validate.** Call the skill tool with name `validating-artifacts`, and tell it to check the file with `--platform opencode`. For a shared setup, add `--project <target>`.

7. **Test in a fresh session.** Probe a scratch copy of the target, never the target checkout itself.
   1. Create the scratch: if `git -C "<target>" status --porcelain` is empty, run `git -C "<target>" worktree add "<scratch>" HEAD`; otherwise copy the target to a scratch directory. Copy the rewritten instructions into the scratch if the target has uncommitted changes.
   2. Install the probe: create `<scratch>/.opencode/agents/` and copy `trigger-probe.md` into it. Take it from the `agents/` folder beside the installed `skills/` folder (for a workspace install: `<stablehand>/.opencode/agents/trigger-probe.md`; in the checkout: `platforms/opencode/agents/trigger-probe.md`). Without this copy OpenCode cannot find the agent from `--dir "<scratch>"`.
   3. Ask 3 questions the file must answer, for example:
      `opencode run "What command runs a single test file here? Answer with the command only." --format json --dir "<scratch>" --agent trigger-probe --model deepseek/deepseek-flash`
   4. Wrong or vague answers mean the fact is missing or buried; fix the target file, refresh the scratch, and ask again.
   5. Remove the scratch when done (`git -C "<target>" worktree remove "<scratch>"`, or delete the copy).

8. **Report:** the file(s) written, line counts, and what you removed and why.

## Done when
- [ ] Every line is a non-inferable fact, a verified command, a boundary, or a pointer
- [ ] The total is within about 150 lines; procedures have moved to skills
- [ ] The CLAUDE.md and AGENTS.md bridge is correct for the platforms in use
- [ ] The validator is clean and the fresh-session questions are answered correctly
