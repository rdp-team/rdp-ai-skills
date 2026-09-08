# RDP AI Skills — חבילת העבודה הארגונית

ZIP אחד לעובד, תהליך משותף ל־Claude Code ול־Codex, ומקור גרסאות פרטי ב־GitHub.

**לעובד:** חלצו את החבילה, פתחו את תיקיית `rdp-ai` בסוכן וכתבו ״חבר אותי לפרויקט של RDP״. התחילו ב־[START_HERE.md](START_HERE.md).

החבילה מכילה 10 Skills כלליים ו־Priority 1.0.0 כאפשרות, תבניות, הוראות משותפות ומתקין Python 3.11+ ללא תלויות צד שלישי בזמן שימוש. Git ו־GitHub CLI נדרשים לעבודה מרחוק. Windows/macOS/Linux נבדקים ב־CI.

## פיתוח ובדיקות

```text
python -m unittest discover -s tests -v
python scripts/validate.py
python rdp.py build --output dist
python -m compileall -q rdp.py scripts tests
```

לבדיקות lint/typecheck: התקינו את requirements-dev.txt בסביבה וירטואלית והריצו `ruff check .` ו־`mypy rdp.py`. אלה תלויות פיתוח בלבד.

## גרסאות והפצה

מקור: https://github.com/rdp-team/rdp-ai-skills

עד אישור ה־PR, ה־ZIP הוא מועמד לבדיקה ולא Release ארגוני מאושר. אחרי Review ו־Merge אנושי, תג מאושר `vVERSION` מפעיל בדיקות ומפיק ZIP ו־SHA-256 ב־Release טיוטה. מנהל מורשה מפרסם את הטיוטה. אף סקריפט בחבילה לא עושה Merge או מפרסם גרסה יציבה בעצמו.

לעובדים חדשים: [מדריך GitHub ו־Claude Code בעברית](docs/employee/GITHUB_AND_CLAUDE_SETUP_HE.md). למנהלים: [הזמנת עובדים](docs/admin/INVITE_EMPLOYEES_HE.md) ו[נוסח המייל](docs/employee/EMAIL_INVITATION_HE.md).

לפרטי גרסאות, תאימות והתקנה: [המדריך הטכני](docs/employee/OPERATIONS.md). להנחות האבטחה: [גבולות וראיות](docs/employee/SECURITY.md). ההרחבה המקורית נשמרת תחת vendor ללא שינוי, ומקורה מתועד ב־vendor/priority-source.json.
