---
name: rdp-pull-request
description: Deliver completed RDP branch work as a GitHub Pull Request with test evidence and handoff, without merging.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# הכנת Pull Request

1. Inspect the branch and `git diff`; the target must be an authorized rdp-team project and a work branch. Include only changes for the current Issue.
2. Complete docs/ai/HANDOFF.md, removing its incomplete marker only after writing outcome, tests, limitations and rollback. Update docs/STATUS.md and DECISIONS when relevant.
3. Run `python .rdp/rdp.py verify --project .`. Review and commit the exact intended files with a clear message. Never stage unrelated employee changes merely to satisfy the clean-tree check.
4. Run `python .rdp/rdp.py pr --project . --issue N --title "Concrete outcome"`. It rechecks access, branch, Issue, checks and handoff, pushes the branch and opens a PR or returns the existing one. It does not commit or merge for you.
5. Inspect actual GitHub Actions and review status. Fix in-scope failures and refresh handoff evidence. Existing PR descriptions must be refreshed when scope/results change; the CLI's existing-PR path only returns its URL.
6. Return the PR link and outstanding review. Merge and stable skill release await authorized review; do not bypass rules or self-approve.
