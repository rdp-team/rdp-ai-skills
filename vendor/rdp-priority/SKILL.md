---
name: rdp-priority
description: Develop or review RDP Priority ERP projects using the approved GitHub, planning, security, verification, handoff, and learning workflow. Use for Priority-related repository work; do not use it to authorize production writes or deployments.
---

# RDP Priority Development

Use GitHub as the source of truth and the exact Skill version recorded in `rdp-skills.lock.json`. Never silently upgrade an active project.

## Required workflow

1. Confirm a GitHub Issue exists and work on an issue-linked branch, never protected `main`.
2. Before material edits, inspect the repository, tests, project instructions, ADRs, lock file, and only the relevant references below.
3. Write `docs/ai/DISCOVERY.md` and `docs/ai/PLAN.md`. Do not begin material implementation until an authorized human records approval.
4. Keep customer data and secrets project-specific. Never promote them into this Skill.
5. Use explicit timeouts, bounded retries and idempotency for external create/write operations where applicable.
6. Run `rdp-ai verify`; record untested areas, rollback and remaining risks in `docs/ai/AI-HANDOFF.md`.
7. Complete `docs/ai/SKILL-LEARNING.md`. Reusable knowledge is a separate, sanitized proposal and never becomes stable automatically.

## Hard boundaries

- Never deploy to production, perform destructive schema/data changes, rotate organization secrets, bypass protection, merge sensitive changes, or publish a stable Skill without explicit human authorization.
- Do not call Priority/EFORM or write to any Priority environment unless the project scope and an authorized human explicitly allow the exact action. Default discovery and validation to read-only.
- Do not expose credentials, personal data, customer documents, commercial data, private URLs, or proprietary customer rules.
- Treat existing project instructions as additive constraints. Preserve and surface conflicts instead of overwriting them.

## Load only what applies

- Always read [`core/mandatory-rules.md`](core/mandatory-rules.md), [`core/git-workflow.md`](core/git-workflow.md), and [`core/security.md`](core/security.md).
- For verification and release work, read [`core/testing.md`](core/testing.md) and [`core/release.md`](core/release.md).
- For lessons or Skill changes, read [`core/learning-policy.md`](core/learning-policy.md).
- For an integration, read [`references/priority-integration-patterns.md`](references/priority-integration-patterns.md), [`references/idempotency.md`](references/idempotency.md), and [`references/retries-timeouts.md`](references/retries-timeouts.md).
- For Hebrew/files/logging, read the matching file under `references/`.
- Priority API facts are intentionally not asserted without validated RDP sources; see [`references/priority-api.md`](references/priority-api.md).

Use the templates under `templates/` and the project-local `rdp-ai` commands. Reusable code belongs in `rdp-priority-shared-components`, not in this Skill.
