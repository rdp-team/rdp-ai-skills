# RDP bundle implementation plan

1. Add failing behavioral tests for packaging, installation, Git boundaries, access checks, compatibility, update and rollback.
2. Build a Python 3.11+ standard-library CLI and independently loadable skills. Preserve existing project instructions and Priority locks.
3. Vendor the exact Priority v1.0.0 release from its canonical repository, verifying its manifest without executing downloaded scripts.
4. Produce a deterministic, checksummed ZIP with discoverable Claude/Codex entrypoints and Hebrew onboarding.
5. Validate on Windows/macOS/Linux CI, exercise a dedicated GitHub pilot through Issue and PR, and provide evidence. No merge, production operations, permission changes or stable publication without approval.

Source repository: rdp-team/rdp-ai-skills. Work branch: codex/rdp-employee-skills.
