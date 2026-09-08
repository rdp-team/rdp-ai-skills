# Testing and Verification

Run the repository's configured build, unit, integration, lint, dependency and security checks. Where applicable, cover authorization, required fields, validation, duplicate prevention, partial failure, precision, date/time, Hebrew encoding, timeouts, retries and version compatibility.

`rdp-ai verify` must exit non-zero on a blocking failure and write `.rdp/reports/verification.json`. Never claim unrun checks passed. Test-environment writes also require project authorization; production writes are outside verification.
