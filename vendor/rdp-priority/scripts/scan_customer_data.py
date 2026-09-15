#!/usr/bin/env python3
"""Conservative pre-promotion scanner for secrets and obvious customer data."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = {
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "cloud access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "email address": re.compile(r"(?<![\w.-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "Israeli phone-like value": re.compile(r"(?<!\d)(?:\+972|0)[2-9][ -]?\d{3}[ -]?\d{4}(?!\d)"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    findings: list[tuple[str, int, str]] = []
    paths = sorted(args.path.rglob("*")) if args.path.is_dir() else [args.path]
    for path in paths:
        if not path.is_file() or ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), 1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append((str(path), line_number, label))
    if findings:
        print("Customer-data scan: BLOCKED")
        for path, line, label in findings:
            print(f"- {path}:{line}: {label} (value suppressed)")
        return 1
    print("Customer-data scan: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
