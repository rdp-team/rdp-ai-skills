# Operations / תפעול

## Installation and discovery

Run commands with Python 3.11+. No pip install is needed by employees. Extracted distributions contain AGENTS.md, CLAUDE.md and identical generated `.agents/skills` / `.claude/skills` trees. The source `skills/` directory is canonical. Project installation creates discovery copies and versioned payloads under `.rdp/bundles/VERSION`. Reopen the agent on the project after installation; discovery layout validation alone is not a live agent test.

Official references consulted 2026-09-08:
- https://developers.openai.com/codex/skills/
- https://code.claude.com/docs/en/skills

## Existing local checkout

Check repository origin and `python PATH/rdp.py doctor --repo rdp-team/NAME`, inspect local changes, then create a work branch. Run `python PATH/rdp.py install --project PROJECT_PATH`. The installer blocks default branches, symlinks, conflicting skill files and locally edited managed content. It appends a delimited block to existing agent instructions, preserves project templates already present, and preserves unrelated lock entries. File writes roll back on an ordinary write failure; power-loss recovery is not guaranteed. Keep Git history as the recovery record.

For a new checkout use `onboard --repo rdp-team/NAME --destination PATH`; add `--create` only when creating a new private repository is intended. A README bootstrap initializes its default branch; generated project code and instructions are on the onboarding branch. A failed onboarding may leave a newly created private repository/clone; it is reported as a failure and never automatically deletes them.

## Manifest and lock

`RDP_AI_MANIFEST.yaml` is serialized as JSON, a YAML 1.2 subset, so employee installation has no YAML dependency. The supported editable format is JSON syntax in this `.yaml` file; arbitrary YAML syntax is rejected explicitly. Schema 1 requires bundle_version, skills and production_deploy=approval_required. Unknown fields are preserved. `rdp-skills.lock.json` retains its existing schemaVersion=1 shape and unrelated skills/sharedComponents. It adds rdpBundle and namespaced shared skill entries with bundle checksums. Priority locks stay untouched; installing Priority into a fresh project includes its full original references and legacy `.rdp/skills` payload.

An existing Priority lock does not prove its payload is installed. Existing project's own Priority doctor/verification remains necessary. Do not use the legacy Priority CLI sync to update this general bundle; it is an independent upstream lifecycle.

## Checks

Edit `.rdp/checks.json` with reviewed command arrays, for example:

```json
{"commands": [["{python}", "-m", "unittest", "discover", "-s", "tests", "-v"]], "timeout_seconds": 300}
```

Use actual project build/lint/typecheck/security commands where applicable. Empty commands intentionally fail. `verify` executes code with the employee's permissions; it is not a sandbox. Reports omit stdout/stderr entirely. Git candidate files are scanned by common credential patterns; ignored files are not included in the source scan. `.rdp/reports/` is ignored, and PR bodies embed a summary of actual checks.

## Updates and rollback

Download an approved release through authenticated GitHub access, verify its published SHA-256 and extract it. On a work branch run:

```text
python .rdp/rdp.py update --project . --bundle PATH/rdp-ai
python .rdp/rdp.py rollback --project . --version 1.0.0
```

Both produce a diff to review and test before a PR. The same version cannot silently change content. Historical bundle directories are kept so rollback works offline. Rollback restores managed skills/tooling, not business code, project-edited templates or customer data. A local edit conflict requires reconciliation; no force overwrite exists.

## Administration

Use team-scoped repository access. Before organizational rollout, an authorized administrator should enforce required CI/review on default branches and designate CODEOWNERS. This bundle does not change permissions or pretend that instruction text enforces them. Private Actions runners and client-data policies must match organizational approval. The pilot contains synthetic data only.

CI tests Python 3.11 and 3.13 on Ubuntu, macOS and Windows. Build produces a deterministic ZIP and checksum. The release workflow creates a draft only when an approved tag points to a commit reachable from main and VERSION matches the tag. An administrator reviews the draft before publishing. Existing releases are not overwritten.
