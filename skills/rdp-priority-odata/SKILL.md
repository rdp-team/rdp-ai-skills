---
name: rdp-priority-odata
description: Query Priority ERP over OData correctly — supported filter subset, subform access, throttling and caching. Use when reading Priority data from any RDP service; it does not authorize writes.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# קריאה מ-Priority דרך OData

1. Read the base URL, token and token password from environment only. The base URL includes the tabula `.ini` file and the company, with a trailing slash. Refuse a non-HTTPS base URL. Never log, echo or embed the token, and never place it in a query string.
2. Priority implements a narrow OData subset. Only `eq/ne/gt/ge/lt/le` with `and/or` are reliable; `contains()` and `startswith()` are not available, so filter server-side on what it supports and do substring matching client-side. Dates need a full ISO timestamp, not a bare date. Always send `$select` and `$top` — a bare entity read can return megabytes, and base64 file columns will dominate the response.
3. Subform-only entities (`PROJCUSTNOTES_SUBFORM`, `CUSTEXTFILE`, `ORDERITEMS_SUBFORM`) return 404 when addressed directly. Reach them through the parent, either with `$expand` or through a keyed navigation path such as `DOCUMENTS_p(DOCNO='<docno>',TYPE='p')/PROJCUSTNOTES_SUBFORM(<key>)`. A nested path that omits the child key may silently answer with the parent's first child rather than the row you asked for, so verify that a read is actually scoped before you trust it.
4. The cloud tenant throttles at roughly 100 requests per minute with limited concurrency. Cap concurrency, pace the queue, and sample sequentially with pauses rather than firing parallel `$expand` bursts. A background warm-up that bursts while a user request is in flight is enough to cross the limit and surface a throttling error in the user's face.
5. Cache reference data (customers, users, contact index, choose values) and refresh with stale-while-revalidate. Never clear a cache before its replacement is built — the gap is exactly when a user request falls through and pays the full cost, or pushes the tenant over its limit.
6. Many screens return `form_not_api_enabled` — commonly the dictionary tables you most want, such as status lists and allowed-file-type lists. That is an administrator flag on the form, not a defect in your code and not something to work around. Record which screens you need, request them in one batch, and design a configurable fallback so the feature degrades instead of failing while you wait.
