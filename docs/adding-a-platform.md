# Adding a platform

Nothing in stablehand assumes a fixed number of platforms: a new harness is a folder, a card and a port.

1. **Write the platform card.** Create `shared/references/<platform>.md` with the same sections as the existing cards:
   - instructions;
   - skills;
   - agents;
   - tools and model tiers;
   - plugins/hooks/MCP;
   - testing;
   - gotchas.

   Use official sources only, add "Last verified: <date>", and give a source URL for every non-obvious claim. The `platform-researcher` agent can draft it.
2. **Extend the coexistence matrix.** Add the platform's read paths to `shared/references/coexistence.md`. Check whether it reads `.claude/` or `.agents/` folders, which is where collisions come from.
3. **Teach the linter.** In `tools/lint.py`:
   - add the platform to `PLATFORMS`;
   - add its skill and agent key sets, tool names, enums, and a `lint_<platform>_agent` function;
   - add project-mode discovery.

   Add tests in `tools/tests/test_lint.py`.
4. **Register the platform for sync.** Add it to `tools/sync.json`. Use `"per-skill"` unless the platform has a plugin-root variable, like Claude's `${CLAUDE_PLUGIN_ROOT}`.
5. **Write the bootstrap.** Create `platforms/<platform>/README.md` and `BOOTSTRAP.md`, using the Antigravity or OpenCode bootstrap as a template, and replace the mechanics with the new platform's.
6. **Port.** Run the bootstrap inside the new platform. Then:
   - run `uv run tools/sync.py`;
   - lint until clean;
   - translate and run the shared evals;
   - write `PORT-NOTES.md`.
7. **Install support.** In `tools/install.py`, add an `install_<platform>` function and the platform's entries in the `wire_workspace` tables (links, target root, hint) and in the `all` list. Then add the platform to `PLATFORMS` in `.agents/skills/auditing-stablehand/scripts/self_check.py` (which CI runs on Linux, macOS and Windows) and to the platform lists in `AGENTS.md`.
8. **List the platform.** Add a row to `platforms/README.md` and to the root README table.
9. **Cross-review.** Have another platform's `artifact-reviewer` check the port against `contracts/`.
