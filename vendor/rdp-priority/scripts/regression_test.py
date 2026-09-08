#!/usr/bin/env python3
"""Deterministic coverage checks for the documented Skill scenarios."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "new-priority-integration", "existing-integration-bug", "timeout-after-write",
    "duplicate-prevention", "hebrew-encoding", "api-authentication-failure",
    "partial-batch-failure", "customer-rule-isolation", "secret-in-learning",
    "breaking-skill-update",
}


def main() -> int:
    scenarios = json.loads((ROOT / "tests/scenarios/catalog.json").read_text(encoding="utf-8"))
    names = {item["id"] for item in scenarios}
    errors = [f"missing scenario: {name}" for name in sorted(EXPECTED - names)]
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [ROOT / "SKILL.md", *sorted((ROOT / "core").glob("*.md")), *sorted((ROOT / "references").glob("*.md"))]
    ).lower()
    required_concepts = ["human approval", "idempoten", "bounded", "secret", "customer", "handoff", "rollback"]
    for concept in required_concepts:
        if concept not in combined:
            errors.append(f"required behavior not represented: {concept}")
    if errors:
        print("Regression suite: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Regression suite: PASS ({len(names)} scenarios, {len(required_concepts)} behavior checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
