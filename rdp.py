#!/usr/bin/env python3
"""RDP employee bundle: stdlib-only, project-scoped installation and GitHub workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ORG = 'rdp-team'
REPO = f'{ORG}/rdp-ai-skills'
VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?$')
SKILL_RE = re.compile(r'^rdp-[a-z0-9-]+$')
SECRET_RE = re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|sk-[A-Za-z0-9_-]{32,}')
ROOT_FILES = ['rdp.py', 'VERSION', 'README.md', 'START_HERE.md', 'WORKFLOW.md', 'CHANGELOG.md']
ROOT_DIRS = ['skills', 'templates', 'vendor', 'docs/employee']
STATE = '.rdp/bundle-state.json'
MANIFEST = 'RDP_AI_MANIFEST.yaml'
LOCK = 'rdp-skills.lock.json'
BEGIN = '<!-- RDP BUNDLE START -->'
END = '<!-- RDP BUNDLE END -->'


class Error(Exception):
    """User-facing failure. Never include raw subprocess output or credentials."""


def dumps(data: Any) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value, dict):
            raise ValueError('expected object')
        return value
    except (OSError, ValueError) as exc:
        raise Error(f'Invalid JSON document: {path.name}') from exc


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    parts = PurePosixPath(relative)
    if not relative or '\\' in relative or ':' in relative or parts.is_absolute() or any(p in {'..', '.'} for p in relative.split('/')):
        raise Error('Unsafe path in bundle or project state')
    path = root.joinpath(*parts.parts)
    current = root
    for part in parts.parts:
        current = current / part
        if current.is_symlink():
            raise Error('Symlink paths are not supported by the bundle installer')
    if not path.resolve().is_relative_to(root.resolve()):
        raise Error('Path escapes project')
    return path


def run(args: list[str], cwd: Path | None = None, timeout: int = 120) -> str:
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Error(f'{args[0]} unavailable or timed out') from exc
    if result.returncode:
        raise Error(f'{args[0]} operation failed (exit {result.returncode}); check access and local state. Raw output suppressed.')
    return result.stdout.strip()


def api(endpoint: str) -> Any:
    try:
        return json.loads(run(['gh', 'api', endpoint]))
    except ValueError as exc:
        raise Error('Invalid GitHub response') from exc


def check_access(repository: str | None = None) -> dict[str, Any]:
    if repository and not re.fullmatch(r'rdp-team/[A-Za-z0-9_.-]+', repository):
        raise Error('Select a repository in rdp-team')
    membership = api(f'user/memberships/orgs/{ORG}')
    if membership.get('state') != 'active':
        raise Error('Active RDP organization membership is required')
    if repository:
        info = api(f'repos/{repository}')
        if not info.get('private') or not info.get('permissions', {}).get('push'):
            raise Error('Private project with write access is required')
    return {'organization': ORG, 'membership': 'active', 'repository': repository, 'mode': 'live'}


def require_branch(project: Path) -> str:
    top = Path(run(['git', 'rev-parse', '--show-toplevel'], project)).resolve()
    if top != project.resolve():
        raise Error('Target must be the project Git root')
    branch = run(['git', 'branch', '--show-current'], project)
    defaults = {'main', 'master'}
    try:
        defaults.add(run(['git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'], project).removeprefix('origin/'))
    except Error:
        pass
    if not branch or branch in defaults:
        raise Error('Create a work branch first; default branches and detached HEAD are blocked')
    return branch


def file_map(root: Path) -> dict[str, str]:
    output: dict[str, str] = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise Error('Bundle contains a symlink')
        if p.is_file() and p != root / 'bundle.json' and '__pycache__' not in p.parts:
            output[p.relative_to(root).as_posix()] = digest(p.read_bytes())
    return output


def seal(root: Path) -> dict[str, Any]:
    version = (root / 'VERSION').read_text().strip()
    if not VERSION_RE.fullmatch(version):
        raise Error('Invalid bundle version')
    data = {'schemaVersion': 1, 'name': 'rdp-ai-skills', 'version': version, 'source': f'https://github.com/{REPO}', 'files': file_map(root)}
    (root / 'bundle.json').write_bytes(dumps(data))
    return data


def validate_bundle(root: Path) -> dict[str, Any]:
    info = read_json(root / 'bundle.json')
    if info.get('schemaVersion') != 1 or info.get('name') != 'rdp-ai-skills' or not VERSION_RE.fullmatch(str(info.get('version', ''))):
        raise Error('Unsupported bundle manifest')
    files = info.get('files')
    if not isinstance(files, dict) or not files:
        raise Error('Empty or invalid bundle file manifest')
    for name, checksum in files.items():
        p = safe_path(root, name)
        if not p.is_file() or digest(p.read_bytes()) != checksum:
            raise Error(f'Bundle integrity failure: {name}')
    if file_map(root) != files:
        raise Error('Bundle contains unlisted files')
    if (root / 'VERSION').read_text().strip() != info['version']:
        raise Error('Bundle version mismatch')
    return info


def stage_bundle(source: Path, target: Path) -> dict[str, Any]:
    if target.exists():
        raise Error('Staging directory already exists')
    for name in ROOT_FILES + ROOT_DIRS:
        entry = safe_path(source, name)
        if entry.is_dir() and any(p.is_symlink() for p in entry.rglob('*')):
            raise Error('Source contains a symlink')
    target.mkdir(parents=True)
    for name in ROOT_FILES:
        shutil.copy2(source / name, target / name)
    for name in ROOT_DIRS:
        shutil.copytree(source / name, target / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for agent in ['.agents', '.claude']:
        shutil.copytree(target / 'skills', target / agent / 'skills')
    instructions = '# RDP employee starter\n\nRead START_HERE.md and WORKFLOW.md. For “חבר אותי לפרויקט של RDP”, load skills/rdp-onboarding/SKILL.md. This directory is a distribution, not the customer project. Never create customer code here.\n'
    for name in ['AGENTS.md', 'CLAUDE.md', 'CODEX.md']:
        (target / name).write_text(instructions, encoding='utf-8', newline='\n')
    return seal(target)


def package(bundle: Path, destination: Path) -> Path:
    info = validate_bundle(bundle)
    destination.mkdir(parents=True, exist_ok=True)
    artifact = destination / f'rdp-ai-skills-{info["version"]}.zip'
    with zipfile.ZipFile(artifact, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted([*info['files'], 'bundle.json']):
            entry = zipfile.ZipInfo(f'rdp-ai/{name}', date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, safe_path(bundle, name).read_bytes())
    artifact.with_suffix('.zip.sha256').write_text(f'{digest(artifact.read_bytes())}  {artifact.name}\n', encoding='utf-8')
    return artifact


def load_manifest(project: Path) -> dict[str, Any]:
    data = read_json(project / MANIFEST)  # JSON is the portable YAML 1.2 subset we generate.
    if data.get('schema_version') != 1 or not VERSION_RE.fullmatch(str(data.get('bundle_version', ''))) or not isinstance(data.get('skills'), list) or data.get('production_deploy') != 'approval_required':
        raise Error('Unsupported or invalid RDP_AI_MANIFEST.yaml')
    return data


def merge_instructions(existing: bytes, version: str) -> bytes:
    text = existing.decode('utf-8')
    block = f'{BEGIN}\nRead `.rdp/bundles/{version}/WORKFLOW.md` and `RDP_AI_MANIFEST.yaml` for RDP work.\nSkills are in `.agents/skills/` (Codex) and `.claude/skills/` (Claude Code).\nUse `python .rdp/rdp.py --help` for local tools. Preserve existing project instructions.\n{END}'
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) > text.index(END):
            raise Error('Malformed RDP instruction block; resolve manually')
        return (text[:text.index(BEGIN)] + block + text[text.index(END) + len(END):]).encode('utf-8')
    return (text.rstrip('\n') + '\n\n' + block + '\n').encode('utf-8')


def apply_files(project: Path, changes: dict[str, bytes | None]) -> None:
    originals: dict[str, bytes | None] = {}
    for name in changes:
        p = safe_path(project, name)
        if p.exists() and not p.is_file():
            raise Error(f'Destination is not a file: {name}')
        originals[name] = p.read_bytes() if p.exists() else None
    completed: list[str] = []
    try:
        for name, content in changes.items():
            p = safe_path(project, name)
            if content == originals[name]:
                continue
            if content is None:
                p.unlink(missing_ok=True)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                fd, temporary = tempfile.mkstemp(prefix='.rdp-write-', dir=p.parent)
                try:
                    with os.fdopen(fd, 'wb') as f:
                        f.write(content)
                    os.replace(temporary, p)
                finally:
                    Path(temporary).unlink(missing_ok=True)
            completed.append(name)
    except OSError as exc:
        for name in reversed(completed):
            p = safe_path(project, name)
            old = originals[name]
            if old is None:
                p.unlink(missing_ok=True)
            else:
                p.write_bytes(old)
        raise Error('Installation write failed; completed file changes restored') from exc


def install(bundle: Path, project: Path, *, priority: bool = False, change_version: bool = False) -> dict[str, Any]:
    require_branch(project)
    info = validate_bundle(bundle)
    version = info['version']
    state_path = safe_path(project, STATE)
    state = read_json(state_path) if state_path.exists() else {}
    if state and state.get('schemaVersion') != 1:
        raise Error('Unsupported installation state')
    if state and state['version'] != version and not change_version:
        raise Error('Version change requires update/rollback on a work branch')
    if state and state['version'] == version and state['bundleSha256'] != digest((bundle / 'bundle.json').read_bytes()):
        raise Error('Immutable version changed; publish a new version')
    for name, checksum in state.get('managed', {}).items():
        p = safe_path(project, name)
        if not p.is_file() or digest(p.read_bytes()) != checksum:
            raise Error(f'Local edit or missing managed file: {name}; preserve and reconcile it first')
    lock_path = safe_path(project, LOCK)
    lock = read_json(lock_path) if lock_path.exists() else {'schemaVersion': 1, 'skills': {}, 'sharedComponents': {}}
    if lock.get('schemaVersion') != 1 or not isinstance(lock.get('skills'), dict):
        raise Error('Unsupported existing lock file')
    priority = priority or bool(state.get('priority'))
    names = sorted(p.name for p in (bundle / 'skills').iterdir() if p.is_dir())
    if any(not SKILL_RE.fullmatch(n) for n in names):
        raise Error('Invalid skill folder name')
    desired: dict[str, bytes] = {'.rdp/rdp.py': (bundle / 'rdp.py').read_bytes()}
    for name in [*info['files'], 'bundle.json']:
        desired[f'.rdp/bundles/{version}/{name}'] = safe_path(bundle, name).read_bytes()
    for name in names:
        existing_entry = lock['skills'].get(name)
        if existing_entry and existing_entry.get('source') != info['source']:
            raise Error(f'Existing skill has another owner: {name}')
        for file in (bundle / 'skills' / name).rglob('*'):
            if file.is_file():
                for adapter in ['.agents', '.claude']:
                    desired[f'{adapter}/skills/{name}/{file.relative_to(bundle / "skills" / name).as_posix()}'] = file.read_bytes()
        lock['skills'][name] = {'version': version, 'source': info['source'], 'checksum': f'sha256:{digest((bundle / "bundle.json").read_bytes())}'}
    if priority and 'rdp-priority' not in lock['skills']:
        provenance = read_json(bundle / 'vendor/priority-source.json')
        for file in (bundle / 'vendor/rdp-priority').rglob('*'):
            if file.is_file():
                relative = file.relative_to(bundle / 'vendor/rdp-priority').as_posix()
                for base in ['.agents/skills/rdp-priority', '.claude/skills/rdp-priority', '.rdp/skills/rdp-priority/1.0.0']:
                    desired[f'{base}/{relative}'] = file.read_bytes()
        lock['skills']['rdp-priority'] = provenance['lockEntry']
    # Reinstall/update maintains already-owned Priority files unchanged.
    for name in state.get('managed', {}):
        if '/rdp-priority/' in name and name not in desired and '/bundles/' not in name:
            desired[name] = safe_path(project, name).read_bytes()
    changes: dict[str, bytes | None] = {}
    for name, content in desired.items():
        p = safe_path(project, name)
        if p.exists() and (not p.is_file() or (name not in state.get('managed', {}) and p.read_bytes() != content)):
            raise Error(f'Existing file would be overwritten: {name}')
        changes[name] = content
    for name in state.get('managed', {}):
        if name not in desired and '/bundles/' not in name:
            changes[name] = None
    for name in ['AGENTS.md', 'CLAUDE.md', 'CODEX.md']:
        p = safe_path(project, name)
        changes[name] = merge_instructions(p.read_bytes() if p.exists() else b'', version)
    for p in (bundle / 'templates/project').rglob('*'):
        if p.is_file():
            name = p.relative_to(bundle / 'templates/project').as_posix()
            if not safe_path(project, name).exists():
                changes[name] = p.read_bytes()
    manifest_path = safe_path(project, MANIFEST)
    manifest = load_manifest(project) if manifest_path.exists() else {}
    if manifest and not state:
        raise Error('Existing manifest is not owned by this installer; migrate explicitly')
    manifest.update({'schema_version': 1, 'bundle_version': version, 'organization': ORG, 'source': info['source'], 'skills': [f'{n}@{lock["skills"][n]["version"]}' for n in sorted(lock['skills'])], 'agents': {'claude_code': 'enabled', 'codex': 'enabled'}, 'environments': ['development', 'test'], 'production_deploy': 'approval_required'})
    lock['rdpBundle'] = {'version': version, 'source': info['source'], 'checksum': digest((bundle / 'bundle.json').read_bytes())}
    changes[MANIFEST] = dumps(manifest)
    changes[LOCK] = dumps(lock)
    # Append only the needed ignores, retaining all existing entries.
    ignore_path = safe_path(project, '.gitignore')
    ignore = ignore_path.read_text(encoding='utf-8') if ignore_path.exists() else ''
    for pattern in ['.env', '.env.*', '!.env.example', '__pycache__/', '*.pyc', '.rdp/reports/']:
        if pattern not in ignore.splitlines():
            ignore = ignore.rstrip('\n') + '\n' + pattern + '\n'
    changes['.gitignore'] = ignore.encode('utf-8')
    attributes_path = safe_path(project, '.gitattributes')
    attributes = attributes_path.read_text(encoding='utf-8') if attributes_path.exists() else ''
    for rule in ['.rdp/** -text', '.agents/skills/rdp-*/** -text', '.claude/skills/rdp-*/** -text']:
        if rule not in attributes.splitlines():
            attributes = attributes.rstrip('\n') + '\n' + rule + '\n'
    changes['.gitattributes'] = attributes.encode('utf-8')
    new_state = {'schemaVersion': 1, 'version': version, 'priority': priority, 'bundleSha256': digest((bundle / 'bundle.json').read_bytes()), 'skills': names, 'managed': {n: digest(b) for n, b in desired.items()}}
    changes[STATE] = dumps(new_state)
    apply_files(project, changes)
    return new_state


def source_bundle() -> Path:
    here = Path(__file__).resolve().parent
    if (here / 'bundle.json').is_file():
        return here
    if (here / 'bundle-state.json').is_file():
        version = read_json(here / 'bundle-state.json').get('version', '')
        if not VERSION_RE.fullmatch(version):
            raise Error('Invalid installed version')
        return here / 'bundles' / version
    raise Error('Build a distribution first: python rdp.py build --output dist')


def redact(text: str) -> str:
    return SECRET_RE.sub('[REDACTED]', text)


def verify_project(project: Path) -> dict[str, Any]:
    errors: list[str] = []
    results: list[dict[str, Any]] = []
    try:
        state = read_json(safe_path(project, STATE))
        manifest = load_manifest(project)
        if manifest['bundle_version'] != state['version']:
            errors.append('Manifest version differs from installed state')
        lock = read_json(safe_path(project, LOCK))
        if lock.get('rdpBundle', {}).get('version') != state['version'] or lock.get('rdpBundle', {}).get('checksum') != state['bundleSha256']:
            errors.append('Lock differs from installed bundle')
        for skill in state['skills']:
            entry = lock.get('skills', {}).get(skill, {})
            if entry.get('version') != state['version'] or entry.get('checksum') != 'sha256:' + state['bundleSha256']:
                errors.append(f'Skill lock differs from installed bundle: {skill}')
        expected_skills = sorted(f'{name}@{entry["version"]}' for name, entry in lock.get('skills', {}).items())
        if sorted(manifest['skills']) != expected_skills:
            errors.append('Manifest skills differ from lock')
        for name, checksum in state['managed'].items():
            p = safe_path(project, name)
            if not p.is_file() or digest(p.read_bytes()) != checksum:
                errors.append(f'Managed file changed: {name}')
    except (Error, KeyError) as exc:
        errors.append(str(exc))
    files = run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], project).split('\0')
    for name in set(files):
        if not name:
            continue
        p = safe_path(project, name)
        if p.is_file() and (SECRET_RE.search(p.read_text(encoding='utf-8', errors='replace')) or (p.name.startswith('.env') and p.name != '.env.example')):
            errors.append(f'Potential secret: {name} (value suppressed)')
    config_path = safe_path(project, '.rdp/checks.json')
    config = read_json(config_path) if config_path.exists() else {}
    commands = config.get('commands', [])
    if not isinstance(commands, list) or not commands:
        errors.append('No verification commands configured')
        commands = []
    timeout = config.get('timeout_seconds', 300)
    if not isinstance(timeout, int) or timeout < 1 or timeout > 1800:
        raise Error('Check timeout must be 1–1800 seconds')
    for command in commands:
        if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command):
            raise Error('Each check must be an argv array, never a shell string')
        actual = [sys.executable if x == '{python}' else x for x in command]
        try:
            result = subprocess.run(actual, cwd=project, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, check=False)
            sensitive = bool(SECRET_RE.search(result.stdout + result.stderr))
            passed = result.returncode == 0 and not sensitive
            results.append({'command': redact(' '.join(command)), 'exitCode': result.returncode, 'status': 'pass' if passed else 'fail', 'output': 'suppressed (potential secret)' if sensitive else 'suppressed by default'})
            if not passed:
                errors.append('Verification command failed or produced a potential secret')
        except (OSError, subprocess.TimeoutExpired):
            results.append({'command': redact(' '.join(command)), 'status': 'fail', 'output': 'unavailable or timed out'})
            errors.append('Verification command unavailable or timed out')
    report = {'schemaVersion': 1, 'status': 'fail' if errors else 'pass', 'mode': 'local-executed', 'commands': results, 'errors': errors}
    apply_files(project, {'.rdp/reports/verification.json': dumps(report)})
    return report


def repository_for(project: Path) -> str:
    url = run(['git', 'remote', 'get-url', 'origin'], project)
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:)(rdp-team/[A-Za-z0-9_.-]+?)(?:\.git)?', url)
    if not match:
        raise Error('Origin must be a GitHub rdp-team repository')
    return match.group(1)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='RDP employee skills bundle (Python 3.11+)')
    sub = p.add_subparsers(dest='command', required=True)
    build = sub.add_parser('build')
    build.add_argument('--output', type=Path, default=Path('dist'))
    doctor = sub.add_parser('doctor')
    doctor.add_argument('--repo')
    doctor.add_argument('--offline', action='store_true', help='Tool checks only; never claims GitHub access')
    onboard = sub.add_parser('onboard')
    onboard.add_argument('--repo', required=True)
    onboard.add_argument('--destination', type=Path, required=True)
    onboard.add_argument('--create', action='store_true', help='Create a new private repository')
    onboard.add_argument('--priority', action='store_true')
    for command in ['install', 'update']:
        item = sub.add_parser(command)
        item.add_argument('--project', type=Path, required=True)
        item.add_argument('--bundle', type=Path)
        item.add_argument('--priority', action='store_true')
    rollback = sub.add_parser('rollback')
    rollback.add_argument('--project', type=Path, required=True)
    rollback.add_argument('--version', required=True)
    for command in ['verify', 'status', 'start', 'pr']:
        item = sub.add_parser(command)
        item.add_argument('--project', type=Path, default=Path.cwd())
        if command in ['start', 'pr']:
            item.add_argument('--issue', type=int, required=True)
        if command == 'pr':
            item.add_argument('--title', required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == 'build':
            with tempfile.TemporaryDirectory(prefix='rdp-build-') as temp:
                bundle = Path(temp) / 'bundle'
                stage_bundle(Path(__file__).resolve().parent, bundle)
                print(package(bundle, args.output.resolve()))
        elif args.command == 'doctor':
            tools = {name: bool(shutil.which(name)) for name in ['git', 'gh', 'claude', 'codex']}
            if not tools['git'] or not tools['gh']:
                raise Error('Install Git and GitHub CLI first; see START_HERE.md')
            report = {'tools': tools, 'mode': 'offline', 'github': 'not-tested'} if args.offline else {'tools': tools, **check_access(args.repo)}
            print(dumps(report).decode())
        elif args.command == 'onboard':
            check_access()
            if not re.fullmatch(r'rdp-team/[A-Za-z0-9_.-]+', args.repo):
                raise Error('Select a repository in rdp-team')
            if args.destination.exists():
                raise Error('Destination exists; use install on a project work branch')
            bundle = source_bundle()
            validate_bundle(bundle)
            if args.create:
                run(['gh', 'repo', 'create', args.repo, '--private', '--add-readme', '--description', 'RDP project with shared AI workflow'])
            access = check_access(args.repo)
            run(['gh', 'repo', 'clone', args.repo, str(args.destination.resolve())], timeout=180)
            run(['git', 'switch', '-c', 'codex/rdp-onboarding'], args.destination)
            state = install(bundle, args.destination.resolve(), priority=args.priority)
            apply_files(args.destination, {'.rdp/reports/onboarding.json': dumps({**access, 'version': state['version'], 'status': 'installed', 'agentRuntime': 'not-tested'})})
            print('Installed. Open the project in your agent; review and commit onboarding on its branch, then open a PR.')
        elif args.command in ['install', 'update', 'rollback']:
            if args.command == 'rollback':
                if not VERSION_RE.fullmatch(args.version):
                    raise Error('Invalid version')
                bundle = safe_path(args.project, f'.rdp/bundles/{args.version}')
            else:
                bundle = args.bundle or source_bundle()
            result = install(bundle.resolve(), args.project.resolve(), priority=getattr(args, 'priority', False), change_version=args.command != 'install')
            print(f'Installed RDP bundle {result["version"]}; commit and open a PR for review.')
        elif args.command == 'status':
            print(dumps(load_manifest(args.project)).decode())
        elif args.command == 'verify':
            report = verify_project(args.project)
            print(dumps(report).decode())
            return 0 if report['status'] == 'pass' else 1
        elif args.command == 'start':
            repo = repository_for(args.project)
            check_access(repo)
            issue = api(f'repos/{repo}/issues/{args.issue}')
            if issue.get('state') != 'open' or 'pull_request' in issue:
                raise Error('An open Issue is required')
            if run(['git', 'status', '--porcelain'], args.project):
                raise Error('Commit current work before starting another Issue')
            run(['git', 'fetch', 'origin'], args.project)
            default = api(f'repos/{repo}')['default_branch']
            run(['git', 'switch', '-c', f'codex/issue-{args.issue}', f'origin/{default}'], args.project)
            print(f'Issue #{args.issue}: branch created. Read the issue and project context, then plan and implement.')
        elif args.command == 'pr':
            branch = require_branch(args.project)
            repo = repository_for(args.project)
            check_access(repo)
            issue = api(f'repos/{repo}/issues/{args.issue}')
            if issue.get('state') != 'open' or 'pull_request' in issue:
                raise Error('An open Issue is required')
            report = verify_project(args.project)
            if report['status'] != 'pass':
                raise Error('Verification failed; PR blocked')
            if run(['git', 'status', '--porcelain'], args.project):
                raise Error('Review and commit changes before opening the PR')
            handoff = args.project / 'docs/ai/HANDOFF.md'
            body = handoff.read_text(encoding='utf-8') if handoff.is_file() else ''
            if not body.strip() or '<!-- COMPLETE BEFORE PR -->' in body:
                raise Error('Complete docs/ai/HANDOFF.md before opening a PR')
            if SECRET_RE.search(body):
                raise Error('Potential secret in handoff; PR blocked')
            body += f'\n\nCloses #{args.issue}\n\n## Executed checks\n```json\n{dumps(report).decode()}```\n'
            run(['git', 'push', '--set-upstream', 'origin', branch], args.project)
            with tempfile.TemporaryDirectory(prefix='rdp-pr-') as temp:
                path = Path(temp) / 'body.md'
                path.write_text(body, encoding='utf-8')
                existing = json.loads(run(['gh', 'pr', 'list', '--repo', repo, '--head', branch, '--json', 'url']))
                if existing:
                    print(existing[0]['url'])
                else:
                    print(run(['gh', 'pr', 'create', '--repo', repo, '--head', branch, '--title', args.title, '--body-file', str(path)], args.project))
        return 0
    except (Error, OSError, ValueError, KeyError) as exc:
        print(f'ERROR: {redact(str(exc))}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
