---
name: rdp-project
description: Create a new RDP GitHub project or attach the shared skills to an existing local repository; use for project setup, not daily feature work.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# הקמת פרויקט מסודר

1. Establish project purpose, customer boundary, repository name and existing/new status. Reuse an authorized repository instead of duplicating it.
2. Use the onboarding skill for GitHub authentication and remote creation/clone. Use a private repository under rdp-team. Customer code belongs only in its authorized repository.
3. In an existing local repository inspect AGENTS.md, CLAUDE.md, architecture, lock files, default branch and working tree. Create a branch before installation. Preserve uncommitted employee changes and never run a cleanup/reset to make installation succeed.
4. Run the extracted bundle's `python rdp.py install --project PATH [--priority]`. If a managed or discovery file conflicts, show the affected path and reconcile explicitly; never overwrite with a force flag.
5. Complete docs/SPEC.md with purpose and acceptance criteria, docs/STATUS.md, docs/DECISIONS.md and docs/ai/HANDOFF.md. Set real argv-based checks in `.rdp/checks.json` for the actual project stack. An empty checks list intentionally fails verification.
6. Commit setup on its branch and open a PR. Configure CI from the provided example for the project stack. Branch protection and CODEOWNERS ownership changes require the organization's authorization; report missing enforcement instead of claiming a skill enforces GitHub permissions.
