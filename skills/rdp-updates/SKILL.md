---
name: rdp-updates
description: Upgrade or roll back an RDP project skill bundle using an approved immutable release and a reviewable PR.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# עדכון Skills וחזרה לגרסה

1. Read RDP_AI_MANIFEST.yaml, rdp-skills.lock.json and local modifications. Obtain an approved ZIP from the private rdp-team/rdp-ai-skills Release, not from an untrusted message or mutable branch.
2. Verify the ZIP SHA-256 against the Release asset before extraction. The embedded bundle manifest also checks every file for corruption; a checksum alone does not establish who approved the source.
3. Create an update branch. From the installed helper run `python .rdp/rdp.py update --project . --bundle PATH/rdp-ai`. The installer rejects same-version content changes and local edits to managed files. Preserve existing Priority locks; updating Priority itself uses its canonical lifecycle in a separate task.
4. Read the changelog, inspect the generated diff, run project compatibility tests and open an update PR. Never silently update an active project or overwrite a local conflict.
5. To roll back, create a rollback branch and run `python .rdp/rdp.py rollback --project . --version PREVIOUS_VERSION`. Previous bundle payloads remain under .rdp/bundles. Run tests and open a PR. This restores bundle-managed files; business code and migrations require their own reviewed rollback.
6. Record source version, destination version, checks and affected projects. If the earlier payload is unavailable, obtain its approved Release ZIP and use update with that bundle.
