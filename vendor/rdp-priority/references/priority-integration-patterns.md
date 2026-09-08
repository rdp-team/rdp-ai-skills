# Integration Patterns

Model boundaries explicitly: source, transformation, destination, identity, authorization and audit trail. Separate transport failures from business validation failures. For batches, define per-item results, partial-failure behavior and safe retry rules.

For create/write flows, choose and persist an idempotency key or document why duplicate prevention is handled elsewhere. Validate unknown Priority-specific details against approved project evidence rather than generalizing from one customer.
