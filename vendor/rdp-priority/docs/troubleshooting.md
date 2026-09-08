# Troubleshooting

- **GitHub unavailable:** keep local commits; do not claim sync, PR or backup completion.
- **Skill unavailable:** use only an already-locked local snapshot whose manifest checksum passes. Latest-stable status remains unknown.
- **Dirty worktree:** commit or safely stash before `init`, `start` or `sync`; the CLI will not overwrite it.
- **Adapter conflict:** existing root instructions are preserved. Merge them deliberately with the generated project-local Skill reference.
- **Secret/customer data found:** remove/sanitize it without echoing the value; rotate a committed credential through an authorized owner.
- **CI/backup failure:** inspect the recorded run. Do not declare protected release success.
- **Claude unavailable:** use Codex/Cursor/Copilot adapter while GitHub, lock, docs and checks remain authoritative.
