# Deployment

Record artifact/release identity, environment, prerequisites, configuration names (never secret values), database/data impact, smoke tests and rollback. Prefer Development → Test → Staging → Production when available.

Production deployment and post-deploy writes require explicit authorized approval. Confirm backup and rollback before deployment, and record actual smoke-test evidence afterward.
