# Security

Never commit credentials, tokens, private keys, connection strings, production secrets or customer records. Use approved credential stores and interactive login.

Use least privilege, safe input handling, parameterized queries, dependency checks and logs that exclude secrets and unnecessary personal data. High-risk or security-sensitive changes need the repository's required reviewers. A detected secret blocks PR/release until removed from the worktree and, if committed, remediated in history and rotated by an authorized owner.
