# מדריך הצטרפות ל־RDP ב־GitHub וחיבור ל־Claude Code

המדריך מיועד גם למי שאין לו ניסיון ב־GitHub. אין לשלוח לאף אחד סיסמה, קוד אימות או Token.

## 1. קבלת ההזמנה ל־GitHub

GitHub שולח מייל הזמנה מטעמו. ההזמנה תקפה לשבעה ימים.

### אם כבר יש חשבון GitHub

1. יש לוודא שהכתובת שאליה נשלחה ההזמנה מופיעה בחשבון ומאומתת: GitHub → תמונת הפרופיל → Settings → Emails.
2. יש לפתוח את הודעת ההזמנה מ־GitHub וללחוץ על **Join RDP team** או **Accept invitation**.
3. אם הקישור פג, יש להשיב למייל של RDP ולבקש הזמנה חדשה.
4. לאחר האישור יש לפתוח את [ארגון RDP](https://github.com/rdp-team) ולוודא שהוא מופיע.

### אם אין חשבון GitHub

1. יש לפתוח את [עמוד ההרשמה ל־GitHub](https://github.com/signup).
2. יש ליצור חשבון עם אותה כתובת `@rdp.co.il` שאליה נשלחה ההזמנה.
3. יש לפתוח את הודעת האימות של GitHub ולאמת את הכתובת.
4. חוזרים למייל ההזמנה ולוחצים על **Accept invitation**.
5. מומלץ להפעיל אימות דו־שלבי בהגדרות Password and authentication.

GitHub מאפשר קבלת הזמנה לפי כתובת רק כאשר הכתובת מאומתת בחשבון. אם קיים חשבון עם כתובת אחרת, ניתן להוסיף אליו את כתובת RDP ולאמת אותה במקום לפתוח חשבון נוסף.

## 2. הכנת המחשב

נדרשים Git, ‏GitHub CLI, ‏Python 3.11 ומעלה ו־Claude Code. ניתן לבצע את ההתקנה יחד במפגש ההדרכה.

### Windows

1. מתקינים [Git for Windows](https://git-scm.com/download/win).
2. מתקינים [GitHub CLI](https://cli.github.com/).
3. מתקינים [Python](https://www.python.org/downloads/windows/) ומסמנים בזמן ההתקנה **Add Python to PATH**.
4. פותחים PowerShell ומתקינים Claude Code:

```powershell
winget install Anthropic.ClaudeCode
```

### macOS

1. מתקינים [GitHub CLI](https://cli.github.com/) ו־Python 3.11 ומעלה. אם Homebrew מותקן:

```bash
brew install gh python
brew install --cask claude-code
```

2. Git קיים בדרך כלל. אם macOS מבקש להתקין Command Line Tools, מאשרים.

הוראות Claude Code העדכניות נמצאות ב[מדריך הרשמי](https://code.claude.com/docs/en/quickstart).

## 3. התחברות ל־GitHub במחשב

פותחים PowerShell ב־Windows או Terminal ב־macOS ומריצים:

```text
gh auth login --hostname github.com --web
gh auth setup-git
```

בוחרים GitHub.com ו־HTTPS, ומאשרים בחלון הדפדפן. אין להעתיק Token לצ'אט. לבדיקת החיבור:

```text
gh auth status
gh repo view rdp-team/rdp-ai-skills
```

## 4. הורדת מאגר החבילה

יוצרים תיקייה לפרויקטים ומריצים:

```text
gh repo clone rdp-team/rdp-ai-skills
cd rdp-ai-skills
git switch codex/rdp-employee-skills
```

פקודת `git switch` נדרשת כל עוד גרסת ההפצה נמצאת בבדיקת Pull Request. לאחר אישור ומיזוג הגרסה, המאגר ייפתח ישירות בגרסה המאושרת ללא הפקודה הנוספת.

אם מתקבלת הודעת `not found` או `permission denied`, יש לוודא שההזמנה לארגון אושרה ושהחשבון הפעיל ב־`gh auth status` הוא החשבון הנכון.

## 5. פתיחת המאגר ב־Claude Code

מתוך תיקיית `rdp-ai-skills` מריצים:

```text
claude
```

בהפעלה הראשונה הדפדפן ייפתח להתחברות לחשבון Claude. נדרש חשבון Claude מתאים או גישה ארגונית. זהו חיבור נפרד מחשבון GitHub.

לאחר הכניסה כותבים ל־Claude:

> קרא את START_HERE.md ואת skills/rdp-onboarding/SKILL.md. חבר אותי לפרויקט של RDP ופעל לפי ההוראות.

Claude יבדוק את סביבת העבודה, יבקש לבחור פרויקט מורשה ויכין אותו עם ההוראות וה־Skills של RDP. אין צורך להעתיק ידנית קובצי Skill לתוך כל פרויקט.

## 6. התחלת עבודה בפרויקט

לאחר שהסוכן מסיים את ההכנה:

1. סוגרים את Claude Code בתיקיית החבילה.
2. עוברים לתיקיית הפרויקט שהסוכן הוריד או הכין.
3. מריצים שוב `claude` מתוך תיקיית הפרויקט.
4. כותבים בשפה פשוטה את התוצאה הרצויה, לדוגמה: “טפל ב־Issue מספר 12”.

העבודה נשמרת בענף וב־Pull Request. אין לעבוד ישירות על `main`, ואין להכניס סודות או מידע לקוח לצ'אט.

## פתרון תקלות קצר

- **הזמנת GitHub לא נפתחת:** יש לוודא שהכתובת `@rdp.co.il` מאומתת ושנכנסו לחשבון הנכון. הזמנה פגה לאחר שבעה ימים.
- **`gh` לא מזוהה:** יש לסגור ולפתוח מחדש את PowerShell/Terminal לאחר ההתקנה.
- **`claude` לא מזוהה:** יש לפתוח חלון טרמינל חדש ולבדוק שוב את התקנת Claude Code.
- **Claude מבקש התחברות מחדש:** מריצים `claude auth login` ופועלים לפי הקישור בדפדפן.
- **המאגר אינו מופיע ב־Claude Web:** חיבור Claude Web ל־GitHub דורש הרשאה נפרדת ל־GitHub App. בעבודה המקומית המתוארת כאן די ב־GitHub CLI.

מקורות רשמיים: [הצטרפות לארגון GitHub](https://docs.github.com/en/organizations/managing-membership-in-your-organization/inviting-users-to-join-your-organization), [התחברות באמצעות GitHub CLI](https://docs.github.com/en/get-started/learning-to-code/getting-started-with-git), [התקנה והתחברות ל־Claude Code](https://code.claude.com/docs/en/quickstart).
