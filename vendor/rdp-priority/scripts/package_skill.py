#!/usr/bin/env python3
"""Create a deterministic release manifest and ZIP artifact."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_ROOTS = [
    "SKILL.md", "VERSION", "catalog.yaml", "CHANGELOG.md", "README.md",
    "agents", "core", "references", "templates", "scripts", "adapters",
    "docs", "src", "pyproject.toml",
]
EXCLUDED = {"release-manifest.json"}


def release_files() -> list[Path]:
    files: list[Path] = []
    for name in INCLUDE_ROOTS:
        path = ROOT / name
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return sorted({p for p in files if p.name not in EXCLUDED}, key=lambda p: p.relative_to(ROOT).as_posix())


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    items = [
        {"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in release_files()
    ]
    tree_hash = hashlib.sha256("".join(f"{i['path']}:{i['sha256']}\n" for i in items).encode()).hexdigest()
    manifest = {"schemaVersion": 1, "name": "rdp-priority", "version": version, "treeSha256": tree_hash, "files": items}
    manifest_path = ROOT / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    artifact = dist / f"rdp-priority-ai-skill-{version}.zip"
    with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in [*release_files(), manifest_path]:
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 9, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    checksum = artifact.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {artifact.name}\n", encoding="utf-8")
    print(f"Created {artifact}")
    print(f"SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
