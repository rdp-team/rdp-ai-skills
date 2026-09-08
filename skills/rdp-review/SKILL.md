---
name: rdp-review
description: Review an RDP Pull Request or address review feedback; assess correctness, tests and alignment with the Issue.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# סקירת שינוי

1. Read Issue acceptance criteria, current diff, relevant context and executed CI. Do not infer test success from the author's summary.
2. Trace behavior and failure cases. Prioritize actionable correctness, data isolation, security and maintainability issues with file/line evidence. Avoid cosmetic churn outside the request.
3. If asked to fix feedback, change only verified in-scope issues on the PR branch, run affected tests and update handoff. Keep unrelated reviewer proposals separate.
4. A review by the coding agent is an additional check, not the organization's independent human approval. Report CI failures and missing human approval accurately.
5. Never merge, override protection or dismiss a human review just because all local tests pass.
