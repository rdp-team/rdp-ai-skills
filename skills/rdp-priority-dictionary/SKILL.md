---
name: rdp-priority-dictionary
description: Establish which Priority fields are mandatory, read-only and where a labelled field actually stores its value, from the live dictionary rather than assumption. Use before writing to any Priority form.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# בירור שדות מול המילון החי

1. Never trust a hand-maintained field catalog, documentation or a previous project's mapping. Query `FORMCLMNSTITLE` filtered by the form's `ENAME` for the form you are about to write to, and treat its answer as the contract for this installation.
2. In `FORMCLMNSTITLE`, `READONLY='M'` marks a column mandatory on create and `READONLY='R'` marks it read-only — either derived by Priority or stamped by the server. Sending a read-only column fails the whole request; omitting a mandatory one passes local validation and is then rejected by Priority, which is the harder failure to diagnose.
3. Labels are per-form, not per-column. The same storage column can appear with different Hebrew titles on different screens — a participant slot on one form is the task owner on another — so a field an employee calls by one name may already be one you populate under another. When someone reports a field is empty, query `FORMCLMNSTITLE` by `TITLE` across all forms before concluding the field is missing.
4. The dictionary's `CNAME` often names the lookup target (for example `USERLOGIN` in the users table) rather than the storage column on this form. Confirm storage empirically: read one complete record that has the value and one that does not, and diff them. The single differing column is the one to write.
5. Choose values and status lists are installation-specific and must never be hardcoded. Read them from their own table; if that table is API-blocked (status lists frequently are), expose the list as configuration, accumulate observed values across refreshes so the list only grows, and state clearly that a sampled list is not a complete one.
6. Numeric scales are also installation-specific. Confirm the real range and direction from live rows before mapping a UI control onto them — a task priority column may run 0-99 with higher meaning more urgent, which inverts and rescales any 1-5 control built on assumption — a value that is valid in one scale can be silently meaningless in another, which produces records that look correct and rank wrongly.
