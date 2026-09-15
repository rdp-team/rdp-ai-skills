#!/usr/bin/env python3
"""Invite RDP employees to GitHub from a local CSV, safely and repeatably."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ORG = "rdp-team"
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@rdp\.co\.il$", re.IGNORECASE)
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


class InviteError(RuntimeError):
    """A safe, user-correctable invitation error."""


@dataclass(frozen=True)
class Employee:
    name: str
    email: str
    github_username: str


def run_gh(arguments: list[str]) -> Any:
    completed = subprocess.run(
        ["gh", "api", *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    if completed.returncode:
        raise InviteError(f"GitHub operation failed with exit {completed.returncode}; raw output suppressed")
    try:
        return json.loads(completed.stdout or "null")
    except json.JSONDecodeError as exc:
        raise InviteError("GitHub returned an invalid response") from exc


def load_employees(path: Path) -> list[Employee]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise InviteError("Could not read the employee CSV") from exc
    if not rows or not {"name", "email", "github_username"}.issubset(rows[0]):
        raise InviteError("CSV headers must be name,email,github_username")
    employees: list[Employee] = []
    seen: set[str] = set()
    for row in rows:
        name = (row.get("name") or "").strip()
        email = (row.get("email") or "").strip().lower()
        login = (row.get("github_username") or "").strip()
        if not name or not EMAIL_RE.fullmatch(email):
            raise InviteError("Every row needs a name and a valid @rdp.co.il address")
        if login and not LOGIN_RE.fullmatch(login):
            raise InviteError("Invalid GitHub username in CSV")
        if email in seen:
            raise InviteError("Duplicate employee email in CSV")
        seen.add(email)
        employees.append(Employee(name, email, login))
    return employees


def mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    return f"{local[:2]}***@{domain}"


def invitation_plan(employees: list[Employee], members: set[str], pending: set[str]) -> list[dict[str, str]]:
    plan: list[dict[str, str]] = []
    for employee in employees:
        if employee.github_username and employee.github_username.lower() in members:
            status = "already_member"
        elif employee.email in pending:
            status = "already_invited"
        else:
            status = "invite"
        plan.append(
            {
                "name": employee.name,
                "email": mask_email(employee.email),
                "github_username": employee.github_username,
                "status": status,
            }
        )
    return plan


def invite(path: Path, execute: bool) -> dict[str, Any]:
    employees = load_employees(path)
    members_data = run_gh([f"orgs/{ORG}/members?per_page=100"])
    pending_data = run_gh([f"orgs/{ORG}/invitations?per_page=100"])
    members = {str(item.get("login", "")).lower() for item in members_data}
    pending = {str(item.get("email", "")).lower() for item in pending_data if item.get("email")}
    plan = invitation_plan(employees, members, pending)
    if execute:
        for employee, item in zip(employees, plan, strict=True):
            if item["status"] != "invite":
                continue
            try:
                run_gh(
                    [
                        f"orgs/{ORG}/invitations",
                        "--method",
                        "POST",
                        "-f",
                        f"email={employee.email}",
                        "-f",
                        "role=direct_member",
                    ]
                )
                item["status"] = "invited"
            except InviteError:
                # A verified address may already belong to an organization member even when
                # GitHub does not expose their email through the members endpoint.
                item["status"] = "not_sent_check_member_or_address"
    counts: dict[str, int] = {}
    for item in plan:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    return {"organization": ORG, "mode": "execute" if execute else "dry-run", "counts": counts, "employees": plan}


def main() -> int:
    parser = argparse.ArgumentParser(description="Invite RDP employees as regular GitHub organization members")
    parser.add_argument("csv", type=Path, help="Local CSV with name,email,github_username; never commit this file")
    parser.add_argument("--execute", action="store_true", help="Send invitations; omission performs a dry run")
    args = parser.parse_args()
    try:
        print(json.dumps(invite(args.csv, args.execute), ensure_ascii=False, indent=2))
        return 0
    except (InviteError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
