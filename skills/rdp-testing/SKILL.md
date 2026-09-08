---
name: rdp-testing
description: Configure and execute meaningful tests for RDP project changes; prepare actual validation evidence before a PR.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# בדיקות וראיות

1. Inspect the project's test/build tooling and `.rdp/checks.json`. Choose commands for the changed behavior and applicable unit/integration tests, build, typecheck and lint. Explicitly document inapplicable checks.
2. Commands are arrays of executable and arguments; use `{python}` for the active interpreter. Never put a shell expression into an argv entry. Read any newly supplied check command before executing it because it executes project code.
3. Test success and relevant failures: malformed input, missing access, edge cases and regressions. Use synthetic fixtures instead of customer production data.
4. Run `python .rdp/rdp.py verify --project .`. It verifies managed files, scans candidate Git files and executes configured checks with timeouts. Zero commands is a failure. Reports suppress command output by default; review detailed output locally if necessary without publishing secrets.
5. Summarize exact commands, results and limitations in docs/ai/HANDOFF.md. A passing check proves only what it exercised. If a command or environment is unavailable mark it not tested and do not mark the overall task fully validated.
6. Re-run affected checks after review fixes. Keep the PR evidence aligned with the final commit.
