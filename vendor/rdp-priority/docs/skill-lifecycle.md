# Skill Lifecycle

`learning` and `candidate` changes use branches/PRs. Stable releases are signed off by the platform owner, carry semantic version `vX.Y.Z`, a GitHub Release, `release-manifest.json` and checksummed archive. Published tags must not move. Deprecated/unsafe versions are recorded in release notes and `catalog.yaml`; projects upgrade explicitly.

PATCH corrects non-breaking guidance, MINOR adds a reusable capability, and MAJOR changes compatibility or workflow. Rollback means explicitly syncing a prior approved tag and re-running verification; never mutate that release.
