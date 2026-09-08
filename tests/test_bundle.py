from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import rdp

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_VERSION = (ROOT / 'VERSION').read_text().strip()


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'פרויקט test'
        self.project.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Local Test')
        self.git('config', 'user.email', 'local@example.invalid')
        (self.project / 'README.md').write_text('Existing project\n')
        self.git('add', '.')
        self.git('commit', '-m', 'Initial fixture')
        self.git('switch', '-c', 'codex/test-install')
        self.bundle = self.root / 'bundle'
        rdp.stage_bundle(ROOT, self.bundle)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.project, check=True, capture_output=True, text=True).stdout.strip()

    def install(self, **kwargs):
        return rdp.install(self.bundle, self.project, **kwargs)

    def test_install_discovery_and_repeat_preserves_project(self):
        (self.project / 'AGENTS.md').write_text('Keep existing instructions.\n')
        first = self.install()
        snapshot = {p.relative_to(self.project).as_posix(): p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts}
        self.install()
        self.assertEqual(snapshot, {p.relative_to(self.project).as_posix(): p.read_bytes() for p in self.project.rglob('*') if p.is_file() and '.git' not in p.parts})
        self.assertTrue((self.project / 'AGENTS.md').read_text().startswith('Keep existing instructions.'))
        for name in first['skills']:
            a = self.project / '.agents/skills' / name / 'SKILL.md'
            b = self.project / '.claude/skills' / name / 'SKILL.md'
            self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(rdp.load_manifest(self.project)['schema_version'], 1)

    def test_default_branch_blocked(self):
        self.git('switch', 'main')
        with self.assertRaises(rdp.Error):
            self.install()
        self.assertFalse((self.project / '.rdp').exists())

    def test_tampered_source_rejected_before_writes(self):
        (self.bundle / 'WORKFLOW.md').write_text('tampered')
        with self.assertRaises(rdp.Error):
            self.install()
        self.assertFalse((self.project / '.rdp').exists())

    def test_conflicting_discovery_file_is_not_overwritten(self):
        p = self.project / '.claude/skills/rdp-onboarding/SKILL.md'
        p.parent.mkdir(parents=True)
        p.write_text('User owned')
        with self.assertRaises(rdp.Error):
            self.install()
        self.assertEqual(p.read_text(), 'User owned')
        self.assertFalse((self.project / 'RDP_AI_MANIFEST.yaml').exists())

    def test_priority_lock_preserved(self):
        legacy = {'schemaVersion': 1, 'skills': {'rdp-priority': {'version': '1.0.0', 'source': 'legacy', 'extra': True}}, 'sharedComponents': {'x': '1'}, 'custom': 'retain'}
        (self.project / 'rdp-skills.lock.json').write_text(json.dumps(legacy))
        self.install(priority=True)
        lock = json.loads((self.project / 'rdp-skills.lock.json').read_text())
        self.assertEqual(lock['skills']['rdp-priority'], legacy['skills']['rdp-priority'])
        self.assertEqual(lock['custom'], 'retain')
        self.assertFalse((self.project / '.agents/skills/rdp-priority').exists())

    def test_priority_fresh_install_full_references(self):
        self.install(priority=True)
        p = self.project / '.agents/skills/rdp-priority'
        self.assertTrue((p / 'core/security.md').is_file())
        self.assertEqual((p / 'SKILL.md').read_bytes(), (self.bundle / 'vendor/rdp-priority/SKILL.md').read_bytes())

    def test_update_and_rollback_preserve_unrelated_lock_entries(self):
        self.install()
        newer = self.root / 'newer'
        shutil.copytree(self.bundle, newer)
        (newer / 'VERSION').write_text('1.1.0\n')
        (newer / 'WORKFLOW.md').write_text('New workflow\n')
        rdp.seal(newer)
        with self.assertRaises(rdp.Error):
            rdp.install(newer, self.project)
        rdp.install(newer, self.project, change_version=True)
        self.assertEqual(rdp.load_manifest(self.project)['bundle_version'], '1.1.0')
        self.install(change_version=True)
        self.assertEqual(rdp.load_manifest(self.project)['bundle_version'], BUNDLE_VERSION)
        self.assertTrue((self.project / '.rdp/bundles/1.1.0').is_dir())

    def test_locally_edited_managed_file_blocks_update(self):
        self.install()
        p = self.project / '.agents/skills/rdp-onboarding/SKILL.md'
        p.write_text('Local changes')
        with self.assertRaises(rdp.Error):
            self.install()
        self.assertEqual(p.read_text(), 'Local changes')

    def test_manifest_invalid_and_unknown_schema(self):
        path = self.project / 'RDP_AI_MANIFEST.yaml'
        for content in ['invalid yaml', '{"schema_version":99}', '{"schema_version":1}']:
            path.write_text(content)
            with self.assertRaises(rdp.Error):
                rdp.load_manifest(self.project)

    def test_permission_denied(self):
        with patch('rdp.api', return_value={'state': 'pending'}):
            with self.assertRaises(rdp.Error):
                rdp.check_access('rdp-team/demo')
        with patch('rdp.api', side_effect=[{'state': 'active'}, {'private': True, 'permissions': {'pull': True, 'push': False}}]):
            with self.assertRaises(rdp.Error):
                rdp.check_access('rdp-team/demo')
        with self.assertRaises(rdp.Error):
            rdp.check_access('another-org/demo')

    def test_bundle_zip_deterministic(self):
        a = rdp.package(self.bundle, self.root / 'a')
        b = rdp.package(self.bundle, self.root / 'b')
        self.assertEqual(a.read_bytes(), b.read_bytes())
        import zipfile
        with zipfile.ZipFile(a) as z:
            self.assertIn('rdp-ai/START_HERE.md', z.namelist())
            self.assertIn('rdp-ai/.agents/skills/rdp-onboarding/SKILL.md', z.namelist())
            self.assertFalse(any('/.git/' in p or p.endswith('/.env') for p in z.namelist()))

    def test_path_traversal_rejected(self):
        m = json.loads((self.bundle / 'bundle.json').read_text())
        m['files']['../escape'] = '0' * 64
        (self.bundle / 'bundle.json').write_text(json.dumps(m))
        with self.assertRaises(rdp.Error):
            self.install()

    def test_symlink_destination_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        try:
            (self.project / '.agents').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('symlink privilege unavailable')
        with self.assertRaises(rdp.Error):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_verify_does_not_pass_without_test_commands(self):
        self.install()
        result = rdp.verify_project(self.project)
        self.assertEqual(result['status'], 'fail')
        self.assertIn('No verification commands configured', result['errors'])

    def test_verification_redacts_command_output(self):
        self.install()
        config = {'commands': [[__import__('sys').executable, '-c', "print('gh' + 'p_' + 'a'*36)"]]}
        (self.project / '.rdp/checks.json').write_text(json.dumps(config))
        result = rdp.verify_project(self.project)
        self.assertNotIn('a' * 36, json.dumps(result))
        self.assertEqual(result['status'], 'fail')

    def test_write_failure_restores_existing_files(self):
        import os
        original = os.replace
        calls = 0

        def fail_once(src, dst):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError('simulated disk failure')
            return original(src, dst)

        (self.project / 'AGENTS.md').write_text('Original instructions')
        with patch('rdp.os.replace', side_effect=fail_once):
            with self.assertRaises(rdp.Error):
                self.install()
        self.assertEqual((self.project / 'AGENTS.md').read_text(), 'Original instructions')
        self.assertFalse((self.project / '.rdp/bundle-state.json').exists())

    def test_changed_lock_fails_verification(self):
        self.install()
        path = self.project / 'rdp-skills.lock.json'
        lock = json.loads(path.read_text())
        lock['skills']['rdp-task']['version'] = '9.0.0'
        path.write_text(json.dumps(lock))
        result = rdp.verify_project(self.project)
        self.assertTrue(any('lock differs' in item for item in result['errors']))


if __name__ == '__main__':
    unittest.main()
