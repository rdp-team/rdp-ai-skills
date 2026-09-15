---
name: rdp-priority-writes
description: Write to Priority ERP safely — guarded execution, honest verification and time-bounded steps so a slow tenant never hangs the caller. Use when any RDP service creates or updates Priority records.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# כתיבה בטוחה ל-Priority

1. Keep writes off by default. Require an explicit write mode, a narrow entity allowlist rather than a wildcard, and per-call confirmation. Audit every write to an append-only log with customer identifiers masked, and persist that log outside the container so a rebuild cannot erase the evidence you will need.
2. Validate the payload against the live dictionary before sending, so a rejected field is caught locally with a readable message instead of surfacing as a generic Priority error.
3. A 200 response does not mean the data landed where you intended. Priority will accept a write addressed to a plausible-but-wrong navigation path and file it somewhere else; posting an attachment to a project's `EXTFILES_SUBFORM` instead of the task's `CUSTNOTEEXTFILE_SUBFORM` returns 200 and stores it on the project. Read the record back and assert the value is on the row you targeted, using a marker you can search for.
4. Priority keeps writing after it answers. An immediate read against the subform you just wrote can block for minutes, and a blocked read that hits the client's retry and backoff policy multiplies that delay several times over. Put a deadline on every verification **and on every write**, not only on the reads.
5. When a deadline expires, release the caller and let the operation finish in the background, logging how it settled. Attach an error handler to any promise you stop awaiting — a rejection that arrives after you have returned is an unhandled rejection that takes the process down. Size the deadlines so their sum stays below the caller's own timeout.
6. Report the two states separately: what was written and what was verified. If a step timed out, say the record may exist and must be checked before retrying. Telling a user an action failed when it may have succeeded is what produces duplicate records in the ERP.
