# Architecture

GitHub organization `rdp-team` is the operational source of truth.

- `rdp-priority-ai-skill`: canonical workflow knowledge, immutable releases and `rdp-ai` CLI.
- `rdp-priority-project-template`: project bootstrap, CI, local adapters and exact Skill lock.
- `rdp-priority-shared-components`: separately versioned reusable production code.

Projects install a released Skill snapshot under `.rdp/skills/rdp-priority/<version>`, generate thin agent adapters and record source commit/manifest checksum in `rdp-skills.lock.json`. Knowledge proposals travel back through separate reviewed PRs. Backups contain Git history, tracked source, manifests and checksums; optional Azure upload is outside normal project execution.
