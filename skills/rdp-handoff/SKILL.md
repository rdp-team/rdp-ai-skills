---
name: rdp-handoff
description: Hand an RDP project or task to another employee or agent and update shared project status.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# שיתוף והעברת עבודה

1. Read the current Issue, PR, branch and actual tests. Update docs/STATUS.md with current outcome, next action and blockers.
2. Write docs/ai/HANDOFF.md with Issue/PR links, branch, relevant files, setup/run/check commands, results, decisions, known limitations and rollback instructions. Never include credentials or customer exports.
3. Put durable decisions and their reasons in docs/DECISIONS.md and product changes in docs/SPEC.md. Link rather than copy long conversations.
4. Keep handoff inside the project repository under its existing permissions. The receiving employee continues from the named branch/PR and pinned skill version.
5. Offer reusable knowledge through rdp-knowledge; do not send messages to employees or customers unless sending was explicitly requested.
