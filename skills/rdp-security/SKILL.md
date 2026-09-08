---
name: rdp-security
description: Review RDP changes for credentials, customer isolation, dangerous operations and dependencies before sharing or a PR.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# אבטחה וגבולות גישה

1. Identify repository, customer and authorized environments. Skills are instructions, not credential storage, sandbox enforcement or a substitute for GitHub permissions.
2. Check the diff and staged/untracked candidate files for secrets, .env data, customer records and sensitive logs. Use the bundled verification scan and inspect contextual risks it cannot detect. Its pattern scan is not a complete DLP solution.
3. Review authentication/authorization, input boundaries, path traversal, shell injection, network destinations and dependency changes where the change touches them. Prefer the existing stack; justify each new dependency and review the lockfile.
4. Production deployment, destructive operations, permission changes, financial actions and customer-system writes require explicit human scope. User authorization already granted for the same action remains valid. Do not turn ordinary development into repeated approval prompts.
5. Keep discovered sensitive data out of comments, issues and the shared skill repository. Report the affected location without the value. Credential rotation remains an explicitly approved action.
6. Record verified findings, fixes, executed tests and untested areas. Never label a regex scan as a penetration test or a security certification.
