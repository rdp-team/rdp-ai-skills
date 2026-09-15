#!/usr/bin/env python3
"""Validate source skill contracts, upstream integrity, links and ZIP discovery."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import rdp  # noqa: E402


def main() -> int:
    errors: list[str] = []
    skill_count = 0
    for skill in sorted((ROOT / 'skills').glob('*/SKILL.md')):
        text = skill.read_text(encoding='utf-8')
        parts = text.split('---', 2)
        if len(parts) != 3 or parts[0].strip():
            errors.append(f'{skill.parent.name}: invalid frontmatter')
            continue
        for key in ['name', 'description']:
            match = re.search(rf'^{key}: (.+)$', parts[1], re.M)
            if not match or (key == 'name' and match[1] != skill.parent.name):
                errors.append(f'{skill.parent.name}: invalid {key}')
        if len(parts[2].strip()) < 300 or 'TODO' in text:
            errors.append(f'{skill.parent.name}: unfinished workflow')
        skill_count += 1
    if skill_count < 10:
        errors.append('Shared skill catalog is incomplete')
    vendor = ROOT / 'vendor/rdp-priority'
    manifest = rdp.read_json(vendor / 'release-manifest.json')
    for item in manifest['files']:
        path = rdp.safe_path(vendor, item['path'])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            errors.append(f'Priority source changed: {item["path"]}')
    source = rdp.read_json(ROOT / 'vendor/priority-source.json')
    if source['lockEntry']['checksum'] != 'sha256:' + rdp.digest((vendor / 'release-manifest.json').read_bytes()):
        errors.append('Priority provenance checksum mismatch')
    for folder in ['skills', 'docs/employee']:
        for path in (ROOT / folder).rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if not link.startswith(('https://', 'http://', '#')) and not (path.parent / link.split('#')[0]).is_file():
                    errors.append(f'Broken link: {path.relative_to(ROOT)} -> {link}')
    with tempfile.TemporaryDirectory(prefix='rdp-validation-') as temp:
        stage = Path(temp) / 'bundle'
        rdp.stage_bundle(ROOT, stage)
        archive = rdp.package(stage, Path(temp) / 'dist')
        for path in stage.rglob('*'):
            if path.is_file() and rdp.SECRET_RE.search(path.read_text(encoding='utf-8', errors='replace')):
                errors.append(f'Potential secret in bundle: {path.relative_to(stage)} (value suppressed)')
        unpacked = Path(temp) / 'unpacked'
        with zipfile.ZipFile(archive) as z:
            z.extractall(unpacked)
        extracted = unpacked / 'rdp-ai'
        rdp.validate_bundle(extracted)
        for skill in (stage / 'skills').glob('*/SKILL.md'):
            for agent in ['.agents', '.claude']:
                if skill.read_bytes() != (extracted / agent / 'skills' / skill.parent.name / 'SKILL.md').read_bytes():
                    errors.append(f'Discovery differs for {agent}/{skill.parent.name}')
    print(json.dumps({'status': 'fail' if errors else 'pass', 'sharedSkills': skill_count, 'priorityVersion': manifest['version'], 'priorityFilesVerified': len(manifest['files']), 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
