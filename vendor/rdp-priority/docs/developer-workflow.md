# Developer Workflow

Create an Issue, enter the project, then run:

```bash
rdp-ai doctor
rdp-ai start <issue-number>
```

Complete `docs/ai/DISCOVERY.md` and `docs/ai/PLAN.md`. An authorized developer reviews the plan and records approval with `rdp-ai plan --approve`. Implement only on the issue branch, then:

```bash
rdp-ai verify
rdp-ai finish
rdp-ai pr
```

`sync` never upgrades a dirty worktree and requires explicit acceptance. Production deployment is not performed by this CLI.

Create a new private project from the approved template with:

```bash
gh repo create rdp-team/<approved-project-name> --private --template rdp-team/rdp-priority-project-template --clone
```

Repository creation/naming must be approved by the relevant RDP owner.
