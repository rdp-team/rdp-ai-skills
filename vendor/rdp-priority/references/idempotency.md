# Idempotency

Treat a timeout after a write as an unknown outcome. Do not blindly retry a create operation. Use a stable business key/idempotency key, query-before-create or a transactional uniqueness constraint when the verified interface supports it.

Test duplicate delivery, concurrent attempts and timeout-after-success. Record how long idempotency state is retained and how operators reconcile ambiguous outcomes.
