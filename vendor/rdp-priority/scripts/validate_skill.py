#!/usr/bin/env python3
"""Deterministic structural validation for the canonical RDP Skill."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "CHANGELOG.md", "VERSION", "catalog.yaml", "SKILL.md",
    "agents/openai.yaml", "core/mandatory-rules.md", "core/git-workflow.md",
    "core/security.md", "core/testing.md", "core/release.md",
    "core/learning-policy.md", "references/priority-development.md",
    "references/priority-api.md", "references/priority-integration-patterns.md",
    "references/common-errors.md", "references/logging.md",
    "references/idempotency.md", "references/retries-timeouts.md",
    "references/encoding-hebrew.md", "references/deployment.md",
    "templates/ISSUE_TEMPLATE.md", "templates/DISCOVERY.md", "templates/PLAN.md",
    "templates/AI-HANDOFF.md", "templates/SKILL-LEARNING.md",
    "templates/ADR.md", "templates/PULL_REQUEST_TEMPLATE.md",
]
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
HIGH_CONFIDENCE_SECRETS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        errors.append(f"VERSION is not semantic: {version!r}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "\nname: rdp-priority\n" not in skill:
        errors.append("SKILL.md frontmatter is missing or invalid")
    if "description:" not in skill.split("---", 2)[1]:
        errors.append("SKILL.md description is missing")

    catalog = (ROOT / "catalog.yaml").read_text(encoding="utf-8")
    if f"version: {version}" not in catalog or "channel: stable" not in catalog:
        errors.append("catalog version/channel does not match VERSION")

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if f'version = "{version}"' not in pyproject:
        errors.append("pyproject version does not match VERSION")

    scan_paths = [ROOT / "SKILL.md", ROOT / "core", ROOT / "references", ROOT / "templates"]
    for base in scan_paths:
        files = [base] if base.is_file() else sorted(base.rglob("*"))
        for path in files:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(pattern.search(text) for pattern in HIGH_CONFIDENCE_SECRETS):
                errors.append(f"potential secret in {path.relative_to(ROOT)}")

    manifest = ROOT / "release-manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if data.get("version") != version:
                errors.append("release manifest version mismatch")
            for item in data.get("files", []):
                path = ROOT / item["path"]
                if not path.is_file():
                    errors.append(f"manifest file missing: {item['path']}")
                    continue
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != item["sha256"]:
                    errors.append(f"manifest checksum mismatch: {item['path']}")
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            errors.append(f"invalid release manifest: {exc}")

    if errors:
        print("Skill validation: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Skill validation: PASS (v{version}, {len(REQUIRED)} required files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
