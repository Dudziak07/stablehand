---
description: A skill requested for another repository lands in that repository and encodes its real conventions (evals/scenarios/external-target-repo.md). Needs --scaffold.
tags: [authoring-skills, target-repo]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

I need a skill named `adding-endpoints` for the repository in `./shop-api` that adds a new REST endpoint the way that repo does it. Work non-interactively: don't ask me questions, skip baseline runs, and write the files directly.
