---
name: skill-authoring
description: Create, update, review, or publish team Agent Skills in this repository. Use when asked to manage AI skills, write SKILL.md, add skill resources, validate skills, package skills into the team-skills plugin, or improve reusable workflows for team members.
---

# Skill Authoring

## Workflow

1. Confirm the target skill name, users, trigger examples, expected outputs, and whether it is personal, project-specific, or team-wide.
2. Read `../../../../docs/skill-management.md` when repository conventions, lifecycle, or review criteria are needed.
3. For a new team skill, copy `../../../../templates/skill/` into `../<skill-name>/`.
4. Keep `SKILL.md` concise. Put long schemas, examples, policies, and runbooks under `references/`.
5. Put deterministic repeated operations under `scripts/`, and static templates or media under `assets/`.
6. Update `agents/openai.yaml` so the display name, short description, and default prompt match `SKILL.md`.
7. Run `python3 ../../../../scripts/validate-skills.py --repo-root ../../../../` before reporting completion.

## Review Rules

- Ensure the folder name and frontmatter `name` match exactly.
- Ensure `description` says what the skill does and when to use it.
- Remove placeholder files that are not needed.
- Do not hard-code secrets, personal paths, customer data, or production credentials.
- Ask for explicit confirmation before adding workflows that modify production systems or perform irreversible operations.

## Output

Report changed files, validation result, and any remaining assumptions or missing examples.
