# Priority API

This release intentionally contains no asserted endpoint, authentication, field or payload facts. Before implementation, use the project's approved documentation and exact Priority version, and record the source in `DISCOVERY.md`.

Every external call needs an explicit timeout, safe authentication handling, response validation and observable failure. Writes require scoped authorization, an idempotency decision and a non-production validation plan. Do not call EFORM or any Priority API merely to discover behavior.
