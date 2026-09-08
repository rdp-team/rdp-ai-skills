# Security boundaries and verification limits

- Trust the approved private RDP release origin before executing any ZIP code. Embedded hashes detect corruption, not a malicious distributor who can replace code and hashes together.
- GitHub CLI uses the employee's existing official authentication. No tokens are stored or logged by the bundle. Access checks require active RDP membership and private-project write access.
- Local install is intentionally offline and proves no GitHub membership. Use doctor/onboard for live access verification.
- Installer rejects path traversal and symlink targets, preflights collisions, preserves unrelated content, and records owned file checksums. Generated instructions complement existing project instructions.
- Verification command arrays avoid shell-string interpretation but execute project code with local permissions; review them before running. Stdout/stderr are omitted from saved reports to reduce disclosure.
- Common-secret pattern checks have false negatives and do not classify customer data. Review diffs and handoff content before publishing. Never include customer data in shared skill contributions.
- No production deployment, permission mutation, destructive cleanup, automated merge or stable publication is implemented.
- Unit tests, source scans, live GitHub pilot and live agent discovery are separate evidence categories; record untested categories explicitly in DELIVERY_REPORT.md.
