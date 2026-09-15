# Restore Runbook

1. Download one backup artifact from GitHub Actions or the approved Azure container into a new empty local directory.
2. Run `python scripts/restore_backup.py <backup-directory>` to verify every SHA-256 and `git bundle verify`.
3. Restore into a new path: `python scripts/restore_backup.py <backup-directory> --restore-to <new-directory>`.
4. Confirm restored `HEAD` equals the manifest commit, inspect all refs, run Skill/project verification and compare the release manifest.
5. Restore to GitHub only after an RDP administrator confirms the target repository and access controls. Never force-push over an existing repository as part of a drill.

Record date, operator, manifest commit, restored location and verification result. Delete drill copies only after the evidence is retained and the target is confirmed non-authoritative.
