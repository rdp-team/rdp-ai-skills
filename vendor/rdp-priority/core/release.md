# Release and Deployment

Record project commit, Skill version, shared-component versions, checksums, deploy instructions and rollback. Back up the release before protected deployment. Use staged environments when available.

Production deployment is a distinct human-authorized action after green verification, owner approval, backup confirmation and rollback readiness. Record the smoke-test result. A failed backup or CI run must remain visible and prevents a protected-success claim.
