---
name: rdp-priority-tasks
description: Create Priority project tasks with their description text and file attachments, including the ownership columns and the paths that silently misfile data. Use when an RDP service opens tasks in Priority.
metadata:
  version: "1.0.0"
  owner: "rdp-team"
---

# פתיחת משימות פרויקט ונספחים

1. Project tasks live in `PROJCUSTNOTES_SUBFORM` under `DOCUMENTS_p(DOCNO='<docno>',TYPE='p')` and are addressed through it using the numeric `CUSTNOTE` key returned by the create call. Confirm the mandatory create columns against the live dictionary for this installation instead of copying them from another environment.
2. Ownership is spread across several distinct columns: `USERLOGIN` (assigned to), `USERLOGIN2`-`USERLOGIN8` (participant slots) and `OUSERLOGIN` (opened by). They are separate fields with different labels on different screens, so confirm which one the employees actually read in their day-to-day screen before deciding which to populate.
3. `OUSERLOGIN` is marked `READONLY='R'` on the project-task form and is stamped by Priority with the user the API token belongs to. No payload can change it. If it must show a specific identity, the token has to be issued from that Priority user — prefer a dedicated service user, which also gives you meaningful permissions and an honest audit trail.
4. Task description text lives in `CUSTNOTESTEXT_SUBFORM` and is written with `APPEND: true` rather than replaced. Reading it back through a direct nested path returns the first task's text regardless of the key you supplied, which looks exactly like data corruption; read it through `$expand=CUSTNOTESTEXT_SUBFORM($select=TEXT)` on the keyed task and you will see the true content.
5. Attach files through the task-level `CUSTNOTEEXTFILE_SUBFORM`. The project-level attachment path accepts the same request, answers 200, and files the document under the project instead of the task. `SUFFIX` is read-only: Priority derives it from the data-URI media type and validates it against `EXTFILETYPES`, so `message/rfc822` and `application/octet-stream` are refused while `text/html` is accepted; deleting a row requires the composite key `(CUST=<n>,EXTFILENUM=<n>)`, not the single row id.
6. Content assembled from an email needs preparation before it is stored. Images referenced by content-id resolve only inside the mailbox and render as broken boxes once saved, so inline them as data URIs, restrict them to a closed list of safe image types, and cap the total size. Never build an anchor from an unvalidated URL: HTML escaping protects text, not the value of an href.
