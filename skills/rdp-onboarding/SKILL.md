---
name: rdp-onboarding
description: Connect an RDP employee to an authorized GitHub project when they say חבר אותי לפרויקט של RDP or open the employee starter ZIP.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# חיבור עובד ל־RDP

1. Read START_HERE.md in the extracted bundle. Locate its `rdp.py`; never put customer code in the starter directory.
2. Check Git, GitHub CLI, Python 3.11+ and the chosen coding agent. Run `python rdp.py doctor --offline`. If Python is exposed as `python3` or `py -3`, use that executable consistently.
3. Run `python rdp.py doctor`. If authentication is missing, guide the employee through `gh auth login --hostname github.com --web` and `gh auth setup-git` in their terminal. Never request, print, store or paste a token. Do not change an already-correct account.
4. Ask only which authorized project they want, or the name of a new project. List accessible repositories with `gh repo list rdp-team --json name,description,isPrivate`; do not assume membership grants access to all repositories.
5. Existing project: `python rdp.py onboard --repo rdp-team/NAME --destination PATH`. New project explicitly requested by the employee: add `--create`. Add `--priority` only for Priority work. The destination must be new; for an existing local checkout create a work branch and use `install --project PATH` after checking its origin and access.
6. Read the installation report under `.rdp/reports/onboarding.json`. Have the employee open the target project in the chosen agent; a new session may be needed for skill discovery. Explain that this installs instructions, not the agent application or a model subscription.
7. Onboarding edits need review, commit and a PR. Report repository, branch, installed version and next action in Hebrew. Do not claim the agent loaded the skills until it demonstrates reading one.
