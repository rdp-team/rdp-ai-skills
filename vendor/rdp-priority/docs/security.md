# Security

Authentication uses `gh auth login` and the OS credential store; no prompt or file should contain a token. Secret/customer-data scans suppress matched values. Repository Actions use read-only contents by default; release and Azure jobs receive only their required permissions.

Production writes/deploys, destructive changes, organization security changes and stable publication require explicit authorized approval. This platform never calls Priority or EFORM during setup, sync, validation, backup or onboarding.
