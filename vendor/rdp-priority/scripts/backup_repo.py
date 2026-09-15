#!/usr/bin/env python3
"""Create a complete Git bundle, source archive, manifest and checksums."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    name = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--show-toplevel"], text=True).strip()
    repo_name = Path(name).name
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    bundle = output / f"{repo_name}.bundle"
    subprocess.run(["git", "-C", str(repo), "bundle", "create", str(bundle), "--all"], check=True)
    archive = output / f"{repo_name}-{commit[:12]}.zip"
    files = subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z"]).split(b"\0")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
        for raw in sorted(item for item in files if item):
            relative = raw.decode()
            handle.write(repo / relative, relative)
    manifest = {
        "schemaVersion": 1,
        "repository": repo_name,
        "commit": commit,
        "createdAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "artifacts": [
            {"name": bundle.name, "sha256": digest(bundle)},
            {"name": archive.name, "sha256": digest(archive)},
        ],
    }
    manifest_path = output / "backup-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "SHA256SUMS").write_text(
        "".join(f"{item['sha256']}  {item['name']}\n" for item in manifest["artifacts"]), encoding="utf-8"
    )
    print(f"Backup created for {repo_name}@{commit[:12]} in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
