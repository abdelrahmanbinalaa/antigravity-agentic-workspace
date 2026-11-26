#!/usr/bin/env python3
"""
Antigravity SessionStart hook: silently ensures quantitative/OR dependencies and
output directories exist on first run in a fresh container or workstation, then
emits valid hook JSON on stdout.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = AGENTS_DIR.parent
MARKER = AGENTS_DIR / ".bootstrap_done"


def main() -> int:
    try:
        _stdin_raw = sys.stdin.read()
    except Exception:
        _stdin_raw = ""

    for d in ("research_runs", "swarm_runs"):
        (REPO_ROOT / d).mkdir(parents=True, exist_ok=True)

    missing = [p for p in ("numpy", "scipy", "pandas", "networkx", "pydantic") if importlib.util.find_spec(p) is None]
    if missing and not MARKER.exists():
        req = REPO_ROOT / "requirements.txt"
        cmd = [sys.executable, "-m", "pip", "install", "-q"]
        if req.exists():
            cmd.extend(["-r", str(req)])
        else:
            cmd.extend(missing)
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            MARKER.write_text("ok\n", encoding="utf-8")
    elif not missing and not MARKER.exists():
        MARKER.write_text("ok\n", encoding="utf-8")

    # Never bloat session context; return clean empty hook response
    sys.stdout.write("{}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
