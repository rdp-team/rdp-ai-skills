#!/usr/bin/env python3
"""Verify a backup manifest and optionally restore its Git bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("backup", type=Path)
    parser.add_argument("--restore-to", type=Path)
    args = parser.parse_args()
    backup = args.backup.resolve()
    manifest = json.loads((backup / "backup-manifest.json").read_text(encoding="utf-8"))
    for item in manifest["artifacts"]:
        path = backup / item["name"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise SystemExit(f"Checksum validation failed: {item['name']}")
    bundle = next(backup / item["name"] for item in manifest["artifacts"] if item["name"].endswith(".bundle"))
    subprocess.run(["git", "bundle", "verify", str(bundle)], check=True)
    print(f"Backup verification PASS: {manifest['repository']}@{manifest['commit'][:12]}")
    if args.restore_to:
        destination = args.restore_to.resolve()
        if destination.exists():
            raise SystemExit(f"Restore destination already exists: {destination}")
        subprocess.run(["git", "clone", str(bundle), str(destination)], check=True)
        restored = subprocess.check_output(["git", "-C", str(destination), "rev-parse", "HEAD"], text=True).strip()
        if restored != manifest["commit"]:
            raise SystemExit("Restored HEAD does not match manifest commit")
        print(f"Restore PASS: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
