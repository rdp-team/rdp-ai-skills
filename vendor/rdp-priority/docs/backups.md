# Backups

The `backup.yml` workflow creates a complete Git bundle, tracked-source ZIP, manifest and SHA-256 checksums and retains the GitHub artifact. When repository variable `AZURE_BACKUP_ENABLED=true` is set, a second least-privilege OIDC job uploads the verified set to the approved Azure Blob container.

Required Azure repository settings are documented in `admin-setup.md`. Suggested lifecycle policy is daily 30 days, weekly 12 weeks, monthly 12 months and major releases long-term; an RDP/Azure owner must confirm policy. A GitHub artifact alone is not the required external backup layer.
