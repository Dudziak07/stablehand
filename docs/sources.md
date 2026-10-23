# Sources and credits

stablehand's text is original. The ideas below come from public work, credited here with links. Platform facts were checked against the official sources on 2026-10-21.

## Platform documentation (facts)
- Claude Code: https://code.claude.com/docs/en/skills, /sub-agents, /memory, /plugins/manifest-reference, /plugins/marketplace-reference, /plugin-evals; changelog: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- Anthropic, Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agent Skills open standard: https://agentskills.io/specification
- AGENTS.md: https://agents.md
- Antigravity: https://antigravity.google/docs (skills, rules, subagents, plugins, hooks, cli/gcli-migration, migration/workflows-to-skills); CLI changelog: https://github.com/google-antigravity/antigravity-cli
- OpenCode: https://opencode.ai/docs (skills, agents, permissions, rules, commands, providers, cli)
- DeepSeek API: https://api-docs.deepseek.com (models, Anthropic API compatibility, Claude Code integration); model IDs via https://models.dev

## Ideas and techniques (credited, not copied)
- **Evaluation-driven skill development** with with/without baselines, trigger sets and description optimization. Sources: Anthropic's `skill-creator` (https://github.com/anthropics/skills) and `claude plugin eval`.
- **"No skill without a failing test first"**, pressure scenarios, and matching the form of guidance to the failure. Source: obra/superpowers `writing-skills` (https://github.com/obra/superpowers, MIT).
- **Evidence-driven skill creation** with RED/GREEN gates, per-skill regression evals and an ecosystem doctor. Source: tripleyak/SkillForge (https://github.com/tripleyak/SkillForge, MIT).
- **Descriptions as routing signals**, and context load vs cognitive load. Source: mattpocock/skills `writing-for-agents` (https://github.com/mattpocock/skills, MIT).
- **One source, many harnesses**, capability matrices. Sources: wshobson/agents (https://github.com/wshobson/agents, MIT) and dyoshikawa/rulesync (https://github.com/dyoshikawa/rulesync, MIT).
- **The agent generation prompt structure** (identifier, whenToUse, systemPrompt) and the reviewer-agent pattern. Source: Anthropic `plugin-dev` (https://github.com/anthropics/claude-plugins-official, Apache-2.0).
- **Evidence on context files:** "Evaluating AGENTS.md", arXiv:2602.11988 (ETH Zurich / LogicStar). Context files rarely improve task success and add cost; hence the ≤ 150-line budget.

If you contribute material derived from any of these, keep its license notice next to it and add it here.
