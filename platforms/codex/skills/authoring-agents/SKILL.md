---
name: "authoring-agents"
description: "Creates or improves one custom subagent for a target repository and platform (Codex TOML agents under .codex/agents/ by default, or Claude Code, Antigravity, OpenCode), only when justified by the five reasons. Use when asked to create or fix a subagent. Not for orchestration, skills, or porting."
---

Create a custom subagent only after proving that built-ins and skills are not enough. Write all output in English.

Reference material (in this skill's folder):
- `references/targets.md`: target repo, access, and non-host platforms.
- `references/decision-guide.md`: the five reasons for a subagent and persona anti-patterns.
- `references/writing-for-agents.md`: concise instruction style.
- `references/eval-protocol.md`: benchmark tasks and decision rule.
- `references/coexistence.md`: safe agent paths across platforms.
- `references/codex.md`, `references/claude-code.md`, `references/antigravity.md`, `references/opencode.md`: platform cards.

## Process

0. **Target** (`references/targets.md`). Confirm target repo, access, and platform. Never write into `stablehand`. If target != Codex, draft and validate for the target, skip step 5, and hand off the benchmark prompt.
1. **Justify.** Confirm at least one of the five reasons (`references/decision-guide.md`) and check built-ins (`default`, `worker`, `explorer`) first. If none apply, switch to `$authoring-skills`.
2. **Contract.** Specify responsibility, delegation trigger (`description`), caller inputs, exact output template, least-privilege `sandbox_mode`, `model_reasoning_effort` / `model`, preloaded skills, and 3-5 benchmark tasks.
3. **Draft** `.codex/agents/<name>.toml` (or `~/.codex/agents/<name>.toml` for user scope) per `references/codex.md`:
   - Required TOML keys: `name`, `description`, `developer_instructions`.
   - Optional TOML keys: `sandbox_mode` (`"read-only"` for reviewers/researchers, `"workspace-write"` for implementers), `model_reasoning_effort`, `model`, `nickname_candidates`.
   - Keep `developer_instructions` concise (<= 150 lines); put domain procedures in skills.
4. **Validate.** Invoke `$validating-artifacts` on the agent file with `--platform <target>` and fix all errors.
5. **Test.** Run each benchmark in a scratch worktree via explicit delegation (`"Spawn <name> to ..."`), plus 2 natural prompts via `codex exec --ephemeral --json --sandbox read-only -C "<scratch>" "<prompt>"` to verify automatic delegation. Record results in `<target>/.stablehand/evals/agents/<name>/`.
6. **Review.** Spawn `artifact-reviewer` with the agent path, contract, target card path, and `references/writing-for-agents.md`. Fix blocking findings and re-run reviewer once more.
7. **Hand over.** Update `<target>/.stablehand/manifest.json` (`stablehand_version`, `kind`, `platform`, `card_verified`, `target_model`, `updated_at`) and report path, invocation, and benchmark results.

## Done when
- [ ] Justification is stated and least-privilege `sandbox_mode` is enforced
- [ ] Validator reports zero errors and benchmarks pass
- [ ] `artifact-reviewer` has no open blocking findings
