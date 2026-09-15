from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import invite_members


class InvitationTests(unittest.TestCase):
    def csv_file(self, rows: list[dict[str, str]]) -> Path:
        temporary = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        with temporary:
            writer = csv.DictWriter(temporary, fieldnames=["name", "email", "github_username"])
            writer.writeheader()
            writer.writerows(rows)
        return Path(temporary.name)

    def test_load_rejects_non_rdp_and_duplicate_addresses(self):
        with self.assertRaises(invite_members.InviteError):
            invite_members.load_employees(self.csv_file([{"name": "A", "email": "a@example.com", "github_username": ""}]))
        duplicate = [
            {"name": "A", "email": "a@rdp.co.il", "github_username": ""},
            {"name": "B", "email": "A@RDP.CO.IL", "github_username": ""},
        ]
        with self.assertRaises(invite_members.InviteError):
            invite_members.load_employees(self.csv_file(duplicate))

    def test_plan_skips_members_and_pending_invitations(self):
        employees = [
            invite_members.Employee("Existing", "existing@rdp.co.il", "ExistingUser"),
            invite_members.Employee("Pending", "pending@rdp.co.il", ""),
            invite_members.Employee("New", "new@rdp.co.il", ""),
        ]
        plan = invite_members.invitation_plan(employees, {"existinguser"}, {"pending@rdp.co.il"})
        self.assertEqual([item["status"] for item in plan], ["already_member", "already_invited", "invite"])
        self.assertNotIn("existing@rdp.co.il", str(plan))

    def test_dry_run_has_no_post(self):
        path = self.csv_file([{"name": "New", "email": "new@rdp.co.il", "github_username": ""}])
        with patch("scripts.invite_members.run_gh", side_effect=[[], []]) as mocked:
            report = invite_members.invite(path, execute=False)
        self.assertEqual(report["counts"], {"invite": 1})
        self.assertEqual(mocked.call_count, 2)

    def test_execute_uses_direct_member_role(self):
        path = self.csv_file([{"name": "New", "email": "new@rdp.co.il", "github_username": ""}])
        with patch("scripts.invite_members.run_gh", side_effect=[[], [], {"id": 1}]) as mocked:
            report = invite_members.invite(path, execute=True)
        self.assertEqual(report["counts"], {"invited": 1})
        self.assertIn("role=direct_member", mocked.call_args_list[2].args[0])


if __name__ == "__main__":
    unittest.main()
