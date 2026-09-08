# RDP employee bundle — delivery report

Date: 2026-09-08. Candidate version: **1.0.1-rc.1**. Source/runtime commit tested: `c3261995bc8cf399971c49598a9139aeee879ac6` (the subsequent employee checkout commit changes documentation only).

## Delivered

- Private source repository: https://github.com/rdp-team/rdp-ai-skills
- Implementation PR: https://github.com/rdp-team/rdp-ai-skills/pull/2 — open for human review; main has only the repository bootstrap.
- Employee ZIP: `rdp-ai-skills-1.0.1-rc.1.zip`, with SHA-256 sidecar.
- CI ZIP artifact: https://github.com/rdp-team/rdp-ai-skills/actions/runs/34218046257 — `rdp-employee-zip-candidate` (authenticated download; 30-day retention).
- SHA-256: `9461f6067d28f17d4647d93dbd7b47c4bc02ac493af92e7b0b99dcce2ca11086`.
- Ten general skills: onboarding, project setup, task development, testing, security, PR delivery, review, handoff, knowledge sharing, updates.
- Optional unmodified Priority v1.0.0, pinned to upstream commit `014a35eca44c668081738eb19a8c7a2ad3bf9bb6`; 52 original files verified against its release manifest.

The employee extracts the ZIP, opens `rdp-ai` in their coding agent and writes **חבר אותי לפרויקט של RDP**. START_HERE.md provides the Hebrew fallback prompt and official login steps.

## Architecture and changed files

Canonical instructions are in `skills/*/SKILL.md` and WORKFLOW.md. The ZIP generates identical Codex `.agents/skills` and Claude `.claude/skills` discovery trees and root entrypoints. `rdp.py` handles build, doctor, onboarding, installation, updates, rollback, verification, Issue branches and PR creation. Templates live under `templates/project`, preserved on an existing project. Upstream Priority is stored unchanged under `vendor` with provenance.

Project versions are recorded in RDP_AI_MANIFEST.yaml, rdp-skills.lock.json and the installer ownership ledger. The manifest uses JSON syntax, a valid YAML 1.2 subset; arbitrary YAML syntax is not supported. General skill lock versions identify the bundle distribution; embedded skill metadata 1.0.0 identifies the unchanged authored workflow revision. Priority retains its independent upstream version. Existing Priority locks and unrelated lock fields are preserved.

Runtime dependencies: Python 3.11+ standard library, Git and GitHub CLI. No third-party Python runtime packages. Ruff/mypy are pinned development-only tools. CI and release workflows use SHA-pinned actions. Root README, employee guides, implementation plan, changelog, tests and the complete PR diff document the delivered files.

## Actual validation

| Check | Evidence / result |
| --- | --- |
| Test-first development | Bundle suite initially failed because rdp did not exist; pilot tests initially failed because task_export did not exist. Both failure runs were observed before implementation. |
| `python3 -m unittest discover -s tests -v` | Exit 0; 22 behavioral tests passed locally, including invitation validation, dry-run behavior and idempotent member/pending-invitation handling. |
| `python3 scripts/validate.py` | Exit 0; 10 skill contracts, internal links, 52 upstream file hashes, archive extraction, both discovery trees and bundled-secret scan passed. |
| Official `quick_validate.py` | Exit 0 for all 10 authored skills. |
| `.venv/bin/ruff check .` | Exit 0. |
| `.venv/bin/mypy rdp.py` | Exit 0. |
| `python3 -m compileall -q rdp.py scripts tests` | Exit 0. |
| `python3 rdp.py build --output dist` | Exit 0; deterministic ZIP and SHA-256 produced. |
| Cross-platform CI | All six combinations of Windows/macOS/Ubuntu and Python 3.11/3.13 passed; artifact job passed. Run: https://github.com/rdp-team/rdp-ai-skills/actions/runs/34218046257 |
| Independent CI artifact comparison | Downloaded CI-built candidate; byte-identical ZIP and identical entries compared to the local artifact. |
| GitHub authentication / authorization | Live doctor verified existing authenticated account, active rdp-team membership and private repository write access. The organization owner explicitly granted GitHub CLI `admin:org` for member invitations. No credentials collected or printed. |
| Negative authorization | Unit mocks verified pending membership, foreign organization and read-only project access are rejected. No unauthorized live account was used. |
| Codex CLI discovery | Live, tool-free smoke test returned all 10 rdp-* skill names. Evidence: docs/evidence/agent-discovery.json. |
| Claude Code discovery | Attempted but blocked: OAuth session expired and refresh failed. Structural discovery passed; live Claude discovery is **not verified**. |
| Secret checks | No configured-pattern findings in the delivered ZIP or pilot candidate files. These are pattern checks, not comprehensive DLP or penetration testing. |

The initial Windows CI failure correctly detected Git newline conversion in the upstream files. Repository attributes now preserve exact upstream bytes; installed managed files also receive scoped attributes. The new regression test additionally clones with Windows-style conversion and verifies every managed checksum. A runner-dependent local-clone failure was eliminated by using Git transport instead of local hardlink optimization. The final six-environment matrix passed.

## Live GitHub pilot

Private project: https://github.com/rdp-team/rdp-ai-workflow-pilot

Issue: https://github.com/rdp-team/rdp-ai-workflow-pilot/issues/1

PR: https://github.com/rdp-team/rdp-ai-workflow-pilot/pull/2

The actual extracted ZIP created and cloned the private project, made an onboarding branch, installed project skills and produced an onboarding report. The implementing Codex session read the installed task skill, wrote a test-first synthetic Hebrew CSV feature and used the installed helper to verify, push and open the PR. Five pilot behavior tests and compileall passed. Both GitHub CI runs passed, including https://github.com/rdp-team/rdp-ai-workflow-pilot/actions/runs/34217798174 .

Actual commands included:

```text
python3 rdp.py doctor --repo rdp-team/rdp-ai-skills
python3 rdp.py onboard --repo rdp-team/rdp-ai-workflow-pilot --destination PATH --create
python3 rdp.py update --project PATH --bundle NEW_BUNDLE_PATH
python3 .rdp/rdp.py rollback --project . --version 1.0.0
python3 rdp.py update --project PATH --bundle NEW_BUNDLE_PATH
python3 .rdp/rdp.py verify --project .
python3 .rdp/rdp.py pr --project . --issue 1 --title TITLE
```

All completed with exit 0. Upgrade 1.0.0 → 1.0.1-rc.1, rollback and re-upgrade were executed locally in the real pilot checkout, and its checks passed after each transition. The PR remains unmerged. No production/client integration was used.

## Employee invitation rollout

The administrator invitation helper was executed against the approved employee roster on 2026-09-08. It found six existing organization members and created 11 `direct_member` invitations. A live follow-up query returned exactly 11 pending invitations, all with `failed_at=null`. The source roster remained in a temporary local file; employee addresses are ignored by Git and are not stored in the repository or this report.

One BCC onboarding email was sent from the connected administrator mailbox to all 17 employees. It links to the Hebrew account/setup guide, covers both new and existing GitHub accounts, and asks recipients to choose Tuesday 2026-09-15 or Wednesday 2026-09-16 with a preferred time for the onboarding meeting. Gmail returned a sent message ID and a follow-up search found the message in `SENT` with all 17 BCC recipients.

## Remaining human actions and limits

1. Review and merge the implementation and pilot PRs if approved. A stable release has **not** been published. The release workflow, which creates a draft after a tag on main, is implemented but has not been triggered end to end.
2. Renew the employee's Claude Code login and repeat discovery before declaring live Claude onboarding validated. Codex discovery is already verified.
3. Eleven invited employees must accept their GitHub invitations before they expire; the six existing members can proceed immediately. Organization-wide repository policy still requires an administrator to configure approved branch protection/review ownership. Live inspection found `main.protected=false` on the two newly created repositories. No protection settings were changed by this task.
4. An existing Priority lock is preserved rather than upgraded; its own project verification is still required. Neither Priority client operations nor any production access were tested.
5. Skill instructions are not an enforcement sandbox. Check commands execute with employee permissions; an interrupted disk write/power loss is not a full filesystem transaction. Source hashes prove integrity, while approved GitHub provenance establishes trust.

Recommended next step: collect employee availability, review the two concrete PRs and renew Claude authentication, then tag and approve the first employee release before the scheduled onboarding meeting.

**Ready with conditions**
