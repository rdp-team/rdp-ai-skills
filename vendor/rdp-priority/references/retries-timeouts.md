# Retries and Timeouts

Every network call has a finite timeout. Retry only transient, safely repeatable operations; use bounded attempts, exponential backoff and jitter. Respect server rate-limit guidance when available.

Never retry validation, authorization or permanent failures automatically. For writes, prove idempotency or route ambiguous outcomes to reconciliation. Expose attempt count and final category without leaking payloads.
