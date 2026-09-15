# Common Error Investigation

Classify failures before changing code: authentication/authorization, validation, transport/timeout, rate limiting, duplicate/conflict, partial batch, encoding, compatibility or unknown. Preserve a sanitized correlation identifier and reproducible steps.

Do not log raw credentials, request bodies containing personal/customer data, or private URLs. An observed error becomes reusable guidance only after sanitization and validation.
