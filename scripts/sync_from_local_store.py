#!/usr/bin/env python3
"""
sync_from_local_store.py — Refresh `.agents/skills/` in this repository from
`~/.skills-manager/store/`, keeping excluded host-only/legacy entries out and
stripping `__pycache__` or `.pyc` artifacts.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8")
        except Exception:
            pass

REPO_ROOT = Path(__file__).resolve().parent.parent
DEST_SKILLS = REPO_ROOT / ".agents" / "skills"
LOCAL_STORE = Path.home() / ".skills-manager" / "store"

EXCLUDED_SKILLS = {
    "deepapi",
    "cmux",
    "herdr",
    "corral-launch-agents",
    "macbook-metrics-setup",
    "nuke-cursor-app",
    "anti-sleep",
}


def ignore_junk(_dir: str, names: list[str]) -> set[str]:
    return {
        n for n in names
        if n in {"__pycache__", ".git", ".pytest_cache", "node_modules", ".env"}
        or n.endswith((".pyc", ".pyo", ".pyd"))
    }


def main() -> int:
    if not LOCAL_STORE.exists():
        print(f"Local store not found: {LOCAL_STORE}", file=sys.stderr)
        return 1

    DEST_SKILLS.mkdir(parents=True, exist_ok=True)
    # Remove skills no longer present or now excluded
    for existing in list(DEST_SKILLS.iterdir()):
        if existing.is_dir():
            if existing.name in EXCLUDED_SKILLS or not (LOCAL_STORE / existing.name).is_dir():
                shutil.rmtree(existing)

    copied = 0
    for src in sorted(LOCAL_STORE.iterdir(), key=lambda p: p.name.lower()):
        if not src.is_dir() or src.name.startswith(".") or src.name in EXCLUDED_SKILLS:
            continue
        if not (src / "SKILL.md").is_file():
            continue
        dst = DEST_SKILLS / src.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=ignore_junk)
        copied += 1

    print(f"Synced {copied} skills into {DEST_SKILLS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
