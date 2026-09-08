# Administrator Setup

## GitHub

For each of the three platform repositories:

1. Require pull requests on `main`, at least one approving review and resolved conversations.
2. Require the actual CI check names after their first successful run.
3. Block force pushes/deletions and require CODEOWNERS where the plan supports it.
4. Keep Actions default token read-only; allow only reviewed actions.
5. Enable secret scanning, push protection and dependency alerts if the organization plan permits them.
6. Restrict stable Skill release approval to `rdp-team/priority-ai-platform-owners`.

## Azure Blob backup

1. Approve or create a dedicated storage account/container and retention/lifecycle policy.
2. Create a GitHub OIDC federated identity scoped to the repository/environment.
3. Grant only `Storage Blob Data Contributor` on the backup container.
4. Add secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
5. Add variables `AZURE_STORAGE_ACCOUNT`, `AZURE_BACKUP_CONTAINER`, then `AZURE_BACKUP_ENABLED=true`.
6. Run `backup.yml`, download/verify the artifact, perform the restore drill and record evidence.

Never add Azure keys or connection strings to GitHub.
