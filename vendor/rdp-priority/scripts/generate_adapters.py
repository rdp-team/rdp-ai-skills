#!/usr/bin/env python3
"""Generate thin project adapters from the canonical Skill."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path


def write_if_safe(path: Path, content: str, force_generated: bool = False) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force_generated:
        return f"preserved existing {path}"
    path.write_text(content, encoding="utf-8")
    return f"generated {path}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--generated-at")
    args = parser.parse_args()

    source = args.source.resolve()
    target = args.target.resolve()
    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    generated_at = args.generated_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    origin = "https://github.com/rdp-team/rdp-priority-ai-skill"
    metadata = f"Canonical source: {origin}\nSkill version: {version}\nGenerated at: {generated_at}\n"
    skill_text = (source / "SKILL.md").read_text(encoding="utf-8")
    messages: list[str] = []

    for relative in [
        ".claude/skills/rdp-priority/SKILL.md",
        ".agents/skills/rdp-priority/SKILL.md",
    ]:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(skill_text, encoding="utf-8")
        messages.append(f"generated {destination}")

    claude = f"# RDP Priority project instructions\n\n{metadata}\nRead `.claude/skills/rdp-priority/SKILL.md` and the exact version in `rdp-skills.lock.json` before Priority-related work. Preserve stricter project instructions.\n"
    codex = f"# RDP Priority project instructions\n\n{metadata}\nRead `.agents/skills/rdp-priority/SKILL.md` and the exact version in `rdp-skills.lock.json` before Priority-related work. Preserve stricter project instructions.\n"
    cursor = f"---\ndescription: RDP Priority project workflow\nalwaysApply: true\n---\n\n{metadata}\nFollow `.agents/skills/rdp-priority/SKILL.md` and `rdp-skills.lock.json`.\n"
    copilot = f"# RDP Priority project instructions\n\n{metadata}\nFollow `.agents/skills/rdp-priority/SKILL.md` and the locked Skill version. Require discovery, approved plan, verification and handoff. Never infer production authorization.\n"

    messages.append(write_if_safe(target / "CLAUDE.md", claude))
    messages.append(write_if_safe(target / "AGENTS.md", codex))
    messages.append(write_if_safe(target / ".cursor/rules/rdp-priority.mdc", cursor, True))
    messages.append(write_if_safe(target / ".github/copilot-instructions.md", copilot, True))

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
