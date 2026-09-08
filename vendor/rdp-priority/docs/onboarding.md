# Employee Onboarding

Prerequisites are Git, GitHub CLI, Python 3.11+ and Claude Code for the primary workflow. Use official interactive GitHub authentication, then `gh auth setup-git`. Install the exact stable CLI tag with `pipx` or a user-scoped Python environment.

Clone or create an authorized RDP project, run `rdp-ai doctor`, then `rdp-ai init --yes`. Confirm `rdp-ai status` reports Skill 1.0.0 and that `CLAUDE.md` points to the project-local locked Skill. Never paste a PAT, password, API key or customer secret into Claude.
