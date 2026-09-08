# RDP Priority AI Skill

Canonical, versioned workflow and organizational knowledge for RDP Priority development. GitHub is the source of truth; project repositories install an immutable released version and record it in `rdp-skills.lock.json`.

## Safe lifecycle

1. Create a GitHub Issue.
2. Run `rdp-ai start <issue-number>` in the project repository.
3. Complete read-only discovery and a plan, then record human approval.
4. Implement and run `rdp-ai verify`.
5. Run `rdp-ai finish`, open a PR, review, merge and release.
6. Deploy only with explicit human authorization.
7. Propose sanitized reusable learning in a separate Skill PR.

Published tags are immutable. `stable` currently maps to `v1.0.0`. This repository contains workflow knowledge, not customer data or reusable production code.

## Install the CLI

Authenticate with the official GitHub CLI flow, configure Git credential access, then install the released package:

```bash
gh auth login
gh auth setup-git
python -m pip install --user "git+https://github.com/rdp-team/rdp-priority-ai-skill.git@v1.0.0"
rdp-ai doctor
```

`pipx install "git+https://github.com/rdp-team/rdp-priority-ai-skill.git@v1.0.0"` is preferred when `pipx` is available.

## Develop and validate

```bash
python scripts/validate_skill.py
python scripts/regression_test.py
python -m unittest discover -s tests -p 'test_*.py'
python scripts/package_skill.py
```

See [`docs/developer-workflow.md`](docs/developer-workflow.md), [`docs/admin-setup.md`](docs/admin-setup.md), and [`docs/restore-runbook.md`](docs/restore-runbook.md).
