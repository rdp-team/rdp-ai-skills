"""Cross-platform CLI for the RDP Priority development workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

SKILL_REPO = "rdp-team/rdp-priority-ai-skill"
SKILL_URL = f"https://github.com/{SKILL_REPO}"
LOCK_NAME = "rdp-skills.lock.json"
DOCS = ["DISCOVERY.md", "PLAN.md", "AI-HANDOFF.md", "SKILL-LEARNING.md"]
SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
]


class WorkflowError(RuntimeError):
    """Expected user-correctable workflow failure."""


def run(command: list[str], cwd: Path | None = None, check: bool = True, capture: bool = True, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture,
        timeout=timeout,
    )


def output(command: list[str], cwd: Path | None = None, timeout: int = 60) -> str:
    return run(command, cwd=cwd, timeout=timeout).stdout.strip()


def git_root(path: Path | None = None) -> Path:
    location = (path or Path.cwd()).resolve()
    try:
        return Path(output(["git", "rev-parse", "--show-toplevel"], cwd=location)).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise WorkflowError("Run this command inside a Git repository.") from exc


def current_branch(root: Path) -> str:
    return output(["git", "branch", "--show-current"], cwd=root)


def is_dirty(root: Path) -> bool:
    return bool(output(["git", "status", "--porcelain"], cwd=root))


def require_clean(root: Path) -> None:
    if is_dirty(root):
        raise WorkflowError("Working tree is not clean. Commit or safely stash changes before this operation.")


def ask_yes(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        return False
    return input(f"{prompt} [y/N] ").strip().lower() in {"y", "yes"}


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_lock(root: Path) -> dict[str, Any] | None:
    path = root / LOCK_NAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"{LOCK_NAME} is invalid JSON: {exc}") from exc


def locked_skill(root: Path) -> dict[str, Any] | None:
    lock = load_lock(root)
    if not lock:
        return None
    return lock.get("skills", {}).get("rdp-priority")


def latest_release() -> tuple[str, str]:
    try:
        raw = output([
            "gh", "api", f"repos/{SKILL_REPO}/releases/latest",
            "--jq", "[.tag_name,.target_commitish]|@tsv",
        ])
        tag, target = raw.split("\t", 1)
        return tag, target
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as exc:
        raise WorkflowError(f"Cannot discover the latest stable Skill release at {SKILL_URL}.") from exc


def verify_source(source: Path) -> tuple[str, str, str]:
    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    validator = source / "scripts/validate_skill.py"
    result = run([sys.executable, str(validator)], cwd=source, check=False)
    if result.returncode != 0:
        raise WorkflowError(f"Skill validation failed:\n{result.stdout}{result.stderr}")
    manifest_path = source / "release-manifest.json"
    if not manifest_path.is_file():
        raise WorkflowError("Stable Skill source has no release-manifest.json.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("version") != version:
        raise WorkflowError("Skill manifest version does not match VERSION.")
    for item in manifest.get("files", []):
        path = source / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise WorkflowError(f"Skill checksum validation failed for {item['path']}.")
    try:
        commit = output(["git", "rev-parse", "HEAD"], cwd=source)
    except subprocess.CalledProcessError:
        commit = "local-uncommitted-source"
    return version, commit, sha256(manifest_path)


def copy_release(source: Path, destination: Path) -> None:
    manifest_path = source / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if destination.exists():
        shutil.rmtree(destination)
    for item in manifest["files"]:
        src = source / item["path"]
        dst = destination / item["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copy2(manifest_path, destination / "release-manifest.json")


def install_templates(source: Path, root: Path) -> None:
    docs_dir = root / "docs/ai"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        destination = docs_dir / name
        if not destination.exists():
            shutil.copy2(source / "templates" / name, destination)

    issue = root / ".github/ISSUE_TEMPLATE/priority-development.md"
    issue.parent.mkdir(parents=True, exist_ok=True)
    if not issue.exists():
        shutil.copy2(source / "templates/ISSUE_TEMPLATE.md", issue)
    pr = root / ".github/pull_request_template.md"
    if not pr.exists():
        shutil.copy2(source / "templates/PULL_REQUEST_TEMPLATE.md", pr)


def generate_adapters(source: Path, root: Path) -> None:
    result = run([
        sys.executable, str(source / "scripts/generate_adapters.py"),
        "--source", str(source), "--target", str(root),
    ], cwd=root, check=False)
    if result.returncode != 0:
        raise WorkflowError(f"Adapter generation failed:\n{result.stdout}{result.stderr}")
    print(result.stdout.strip())


def write_lock(root: Path, version: str, commit: str, checksum: str) -> None:
    lock = {
        "schemaVersion": 1,
        "skills": {
            "rdp-priority": {
                "version": version,
                "channel": "stable",
                "commit": commit,
                "checksum": f"sha256:{checksum}",
                "source": SKILL_URL,
            }
        },
        "sharedComponents": {},
        "updatedAt": iso_now(),
    }
    (root / LOCK_NAME).write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sync_from_source(root: Path, source: Path, assume_yes: bool) -> None:
    version, commit, checksum = verify_source(source)
    existing = locked_skill(root)
    if existing and existing.get("version") == version and existing.get("commit") == commit:
        installed = root / ".rdp/skills/rdp-priority" / version
        if installed.exists() and sha256(installed / "release-manifest.json") == checksum:
            print(f"Skill v{version} is already locked and verified.")
            return
    if existing and existing.get("version") == version and existing.get("commit") != commit:
        raise WorkflowError(
            f"Immutability violation: stable version {version} resolves to a different commit. "
            "The existing lock was preserved."
        )
    if existing:
        before = existing.get("version", "unknown")
        if not ask_yes(f"Upgrade locked Skill from {before} to {version}?", assume_yes):
            raise WorkflowError("Skill upgrade was not approved; lock file was not changed.")
    elif not ask_yes(f"Install stable Skill v{version}?", assume_yes):
        raise WorkflowError("Skill installation was not approved.")

    destination = root / ".rdp/skills/rdp-priority" / version
    copy_release(source, destination)
    generate_adapters(source, root)
    install_templates(source, root)
    write_lock(root, version, commit, checksum)
    print(f"Installed and locked RDP Priority Skill v{version} ({commit[:12]}).")


def sync_project(root: Path, assume_yes: bool, source_override: str | None = None) -> None:
    require_clean(root)
    source_env = source_override or os.environ.get("RDP_AI_SKILL_SOURCE")
    if source_env:
        source = Path(source_env).expanduser().resolve()
        if not source.is_dir():
            raise WorkflowError(f"Local Skill source does not exist: {source}")
        sync_from_source(root, source, assume_yes)
        return

    tag, _ = latest_release()
    with tempfile.TemporaryDirectory(prefix="rdp-ai-skill-") as temporary:
        source = Path(temporary) / "skill"
        clone = run([
            "git", "clone", "--quiet", "--depth", "1", "--branch", tag,
            SKILL_URL + ".git", str(source),
        ], check=False, timeout=180)
        if clone.returncode != 0:
            raise WorkflowError("Could not fetch the stable Skill. Existing locked files were not changed.")
        sync_from_source(root, source, assume_yes)


def command_doctor(_: argparse.Namespace) -> int:
    checks: list[tuple[str, bool, str]] = []
    for binary in ["git", "gh", "claude"]:
        path = shutil.which(binary)
        checks.append((binary, bool(path), path or "not found"))
    gh_ok = False
    try:
        auth = run(["gh", "auth", "status"], check=False)
        gh_ok = auth.returncode == 0
    except FileNotFoundError:
        pass
    checks.append(("GitHub authentication", gh_ok, "interactive gh auth" if gh_ok else "run gh auth login"))
    access = False
    if gh_ok:
        access = run(["gh", "repo", "view", SKILL_REPO, "--json", "name"], check=False).returncode == 0
    checks.append(("Skill repository access", access, SKILL_URL))
    try:
        root = git_root()
        checks.append(("Git repository", True, str(root)))
        checks.append(("Working tree", not is_dirty(root), "clean" if not is_dirty(root) else "has uncommitted changes"))
    except WorkflowError:
        checks.append(("Git repository", False, "current directory is not a repository"))
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'WARN'}  {name}: {detail}")
    blocking = [name for name, ok, _ in checks if not ok and name in {"git", "gh", "GitHub authentication", "Skill repository access"}]
    return 1 if blocking else 0


def command_init(args: argparse.Namespace) -> int:
    root = git_root()
    require_clean(root)
    try:
        head = output(["git", "rev-parse", "HEAD"], cwd=root)
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        checkpoint = f"rdp-ai/pre-init-{stamp}"
        run(["git", "tag", checkpoint, head], cwd=root)
        print(f"Created local recovery tag {checkpoint}.")
    except subprocess.CalledProcessError:
        print("Repository has no commit yet; create an initial commit for a durable recovery point.")
    sync_project(root, args.yes, args.source)
    return 0


def issue_title(root: Path, issue: int) -> str:
    result = run(["gh", "issue", "view", str(issue), "--json", "title,state", "--jq", "[.title,.state]|@tsv"], cwd=root, check=False)
    if result.returncode != 0:
        raise WorkflowError(f"Cannot read Issue #{issue} from this repository.")
    title, state = result.stdout.strip().split("\t", 1)
    if state.upper() != "OPEN":
        raise WorkflowError(f"Issue #{issue} is not open.")
    return title


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "work"


def command_start(args: argparse.Namespace) -> int:
    root = git_root()
    require_clean(root)
    branch = current_branch(root)
    if branch not in {"main", "master"}:
        raise WorkflowError(f"Start from the default branch, not {branch!r}.")
    title = issue_title(root, args.issue)
    new_branch = f"{args.kind}/{args.issue}-{slugify(title)}"
    run(["git", "switch", "-c", new_branch], cwd=root)
    print(f"Created branch {new_branch} for Issue #{args.issue}: {title}")
    sync_project(root, args.yes, args.source)
    issue_marker = root / ".rdp/current-issue.json"
    issue_marker.parent.mkdir(parents=True, exist_ok=True)
    issue_marker.write_text(json.dumps({"issue": args.issue, "title": title, "branch": new_branch}, indent=2) + "\n", encoding="utf-8")
    print("Next: complete docs/ai/DISCOVERY.md and docs/ai/PLAN.md, then obtain human approval.")
    return 0


def command_sync(args: argparse.Namespace) -> int:
    root = git_root()
    sync_project(root, args.yes, args.source)
    return 0


def command_status(_: argparse.Namespace) -> int:
    root = git_root()
    skill = locked_skill(root)
    installed = skill.get("version") if skill else "not installed"
    latest = "unavailable"
    try:
        latest = latest_release()[0].removeprefix("v")
    except WorkflowError:
        pass
    issue = "none"
    issue_path = root / ".rdp/current-issue.json"
    if issue_path.exists():
        issue = str(json.loads(issue_path.read_text(encoding="utf-8")).get("issue", "unknown"))
    print(f"Repository: {root.name}")
    print(f"Branch: {current_branch(root)}")
    print(f"Issue: {issue}")
    print(f"Installed Skill: {installed}")
    print(f"Latest stable Skill: {latest}")
    print(f"Skill drift: {'unknown' if latest == 'unavailable' else ('none' if installed == latest else 'update available')}")
    print(f"Shared components: {len((load_lock(root) or {}).get('sharedComponents', {}))}")
    report = root / ".rdp/reports/verification.json"
    print(f"Verification: {'not run' if not report.exists() else json.loads(report.read_text()).get('status', 'unknown')}")
    print(f"Uncommitted changes: {'yes' if is_dirty(root) else 'no'}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    root = git_root()
    discovery = root / "docs/ai/DISCOVERY.md"
    plan = root / "docs/ai/PLAN.md"
    if not discovery.exists() or not plan.exists():
        raise WorkflowError("Run rdp-ai init/start first; discovery or plan template is missing.")
    if args.approve:
        if not ask_yes("Record your human approval for this plan?", args.yes):
            raise WorkflowError("Plan approval was not recorded.")
        name = output(["git", "config", "user.name"], cwd=root) or "authorized developer"
        content = plan.read_text(encoding="utf-8")
        content = re.sub(r"(?m)^Approval Status:.*$", "Approval Status: APPROVED", content, count=1)
        content = re.sub(r"(?m)^Approved By:.*$", f"Approved By: {name}", content, count=1)
        content = re.sub(r"(?m)^Approved At:.*$", f"Approved At: {iso_now()}", content, count=1)
        plan.write_text(content, encoding="utf-8")
        print(f"Recorded plan approval by {name}.")
    else:
        approved = "Approval Status: APPROVED" in plan.read_text(encoding="utf-8")
        print(f"Discovery: present\nPlan: present\nApproval: {'APPROVED' if approved else 'PENDING'}")
    return 0


def verify_lock(root: Path) -> list[str]:
    errors: list[str] = []
    skill = locked_skill(root)
    if not skill:
        return [f"{LOCK_NAME} has no rdp-priority Skill"]
    version = skill.get("version")
    installed = root / ".rdp/skills/rdp-priority" / str(version)
    manifest = installed / "release-manifest.json"
    if not manifest.is_file():
        return [f"installed Skill v{version} manifest is missing"]
    expected = str(skill.get("checksum", "")).removeprefix("sha256:")
    if sha256(manifest) != expected:
        errors.append("installed Skill manifest does not match lock checksum")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for item in data.get("files", []):
        path = installed / item["path"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            errors.append(f"installed Skill file checksum mismatch: {item['path']}")
    return errors


def tracked_files(root: Path) -> list[Path]:
    raw = output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    return [root / item for item in raw.split("\0") if item]


def secret_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for path in tracked_files(root):
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(f"potential secret in {path.relative_to(root)} (value suppressed)")
    return findings


def verification_commands(root: Path) -> tuple[list[str], int]:
    config = root / "rdp-ai.toml"
    if not config.exists():
        return [], 600
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    verify = data.get("verify", {})
    return list(verify.get("commands", [])), int(verify.get("timeout_seconds", 600))


def command_verify(_: argparse.Namespace) -> int:
    root = git_root()
    errors = verify_lock(root)
    for name in DOCS:
        if not (root / "docs/ai" / name).is_file():
            errors.append(f"required document missing: docs/ai/{name}")
    branch = current_branch(root)
    if branch not in {"main", "master"}:
        plan = root / "docs/ai/PLAN.md"
        if plan.exists() and "Approval Status: APPROVED" not in plan.read_text(encoding="utf-8"):
            errors.append("human plan approval is not recorded")
    errors.extend(secret_findings(root))
    results: list[dict[str, Any]] = []
    commands, timeout = verification_commands(root)
    for command in commands:
        command = command.replace("{python}", shlex.quote(sys.executable))
        started = iso_now()
        completed = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True, timeout=timeout)
        results.append({
            "command": command,
            "status": "pass" if completed.returncode == 0 else "fail",
            "exitCode": completed.returncode,
            "startedAt": started,
            "stdoutTail": completed.stdout[-4000:],
            "stderrTail": completed.stderr[-4000:],
        })
        if completed.returncode != 0:
            errors.append(f"verification command failed: {command}")
    report = {
        "schemaVersion": 1,
        "status": "pass" if not errors else "fail",
        "generatedAt": iso_now(),
        "repository": root.name,
        "branch": branch,
        "skill": locked_skill(root),
        "commands": results,
        "errors": errors,
    }
    report_path = root / ".rdp/reports/verification.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Verification: {report['status'].upper()}")
    print(f"Configured commands: {len(commands)}")
    for error in errors:
        print(f"- {error}")
    print(f"Machine report: {report_path}")
    return 0 if not errors else 1


def command_finish(_: argparse.Namespace) -> int:
    root = git_root()
    if current_branch(root) in {"main", "master"}:
        raise WorkflowError("Finish work on an issue branch, not the default branch.")
    result = command_verify(argparse.Namespace())
    if result:
        raise WorkflowError("Verification failed; finish is blocked.")
    handoff = root / "docs/ai/AI-HANDOFF.md"
    learning = root / "docs/ai/SKILL-LEARNING.md"
    if "Learning review completed: YES" not in learning.read_text(encoding="utf-8"):
        raise WorkflowError("Complete the Skill learning review and set 'Learning review completed: YES'.")
    changed = output(["git", "status", "--short"], cwd=root)
    print("Work is ready for PR review after the handoff contents are confirmed.")
    print("Changed files:\n" + (changed or "(none)"))
    print(f"Handoff: {handoff}\nLearning: {learning}")
    return 0


def command_learn(_: argparse.Namespace) -> int:
    root = git_root()
    source = root / "docs/ai/SKILL-LEARNING.md"
    if not source.exists() or "Learning review completed: YES" not in source.read_text(encoding="utf-8"):
        raise WorkflowError("Complete the Skill learning review first.")
    if secret_findings(root):
        raise WorkflowError("Potential secret detected; sanitized learning proposal was not created.")
    text = source.read_text(encoding="utf-8")
    if "GENERAL VS CUSTOMER-SPECIFIC\n\nGENERAL" not in text.upper():
        raise WorkflowError("Mark the lesson as GENERAL after sanitization, or keep it project-specific.")
    target = root / ".rdp/skill-proposals" / f"learning-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    print(f"Created sanitized candidate proposal: {target}")
    print("It still requires a separate Skill PR, validation and authorized release approval.")
    return 0


def command_pr(args: argparse.Namespace) -> int:
    root = git_root()
    if command_verify(argparse.Namespace()):
        raise WorkflowError("PR is blocked because verification failed.")
    if not ask_yes("Create a GitHub pull request now?", args.yes):
        raise WorkflowError("PR creation was not confirmed.")
    template = root / ".github/pull_request_template.md"
    command = ["gh", "pr", "create", "--fill"]
    if template.exists():
        command.extend(["--template", str(template)])
    completed = run(command, cwd=root, check=False, capture=False)
    return completed.returncode


def command_backup_status(_: argparse.Namespace) -> int:
    root = git_root()
    result = run([
        "gh", "run", "list", "--workflow", "backup.yml", "--limit", "1",
        "--json", "status,conclusion,createdAt,url",
    ], cwd=root, check=False)
    if result.returncode != 0:
        raise WorkflowError("Backup workflow status is unavailable for this repository.")
    rows = json.loads(result.stdout or "[]")
    if not rows:
        print("No backup workflow run is recorded.")
        return 1
    row = rows[0]
    print(f"Backup workflow: {row.get('status')} / {row.get('conclusion')}\nCreated: {row.get('createdAt')}\n{row.get('url')}")
    return 0 if row.get("conclusion") == "success" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rdp-ai", description="RDP Priority development workflow")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor").set_defaults(func=command_doctor)

    init = sub.add_parser("init")
    init.add_argument("--yes", action="store_true")
    init.add_argument("--source", help="validated local Skill source (development/testing only)")
    init.set_defaults(func=command_init)

    start = sub.add_parser("start")
    start.add_argument("issue", type=int)
    start.add_argument("--kind", choices=["feature", "fix", "refactor"], default="feature")
    start.add_argument("--yes", action="store_true")
    start.add_argument("--source")
    start.set_defaults(func=command_start)

    sync = sub.add_parser("sync")
    sync.add_argument("--yes", action="store_true")
    sync.add_argument("--source")
    sync.set_defaults(func=command_sync)

    sub.add_parser("status").set_defaults(func=command_status)
    plan = sub.add_parser("plan")
    plan.add_argument("--approve", action="store_true")
    plan.add_argument("--yes", action="store_true")
    plan.set_defaults(func=command_plan)
    sub.add_parser("verify").set_defaults(func=command_verify)
    sub.add_parser("finish").set_defaults(func=command_finish)
    sub.add_parser("learn").set_defaults(func=command_learn)
    pr = sub.add_parser("pr")
    pr.add_argument("--yes", action="store_true")
    pr.set_defaults(func=command_pr)
    sub.add_parser("backup-status").set_defaults(func=command_backup_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except WorkflowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as exc:
        print(f"ERROR: command timed out after {exc.timeout} seconds", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        print(f"ERROR: command failed ({exc.returncode}): {detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
