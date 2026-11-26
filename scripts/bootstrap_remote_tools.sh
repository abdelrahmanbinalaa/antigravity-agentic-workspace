#!/usr/bin/env bash
set -euo pipefail

echo "[bootstrap] Checking Python environment..."
PYTHON_BIN="$(command -v python3 || command -v python)"
echo "[bootstrap] Using: $PYTHON_BIN ($($PYTHON_BIN --version))"

mkdir -p research_runs swarm_runs

echo "[bootstrap] Installing core OR & research packages..."
$PYTHON_BIN -m pip install --upgrade pip >/dev/null 2>&1 || true
$PYTHON_BIN -m pip install -q -r requirements.txt

echo "[bootstrap] Verifying deterministic skill engines..."
$PYTHON_BIN .agents/skills/deep-research/scripts/dr_engine.py --help >/dev/null
$PYTHON_BIN .agents/skills/agent-swarm/scripts/swarm_coordinator.py --help >/dev/null

echo "[bootstrap] Ready. Optional tools check:"
command -v agent-reach >/dev/null 2>&1 && echo "  - agent-reach: OK" || echo "  - agent-reach: not on PATH"
command -v scrapling >/dev/null 2>&1 && echo "  - scrapling: OK" || echo "  - scrapling: not on PATH"
echo "[bootstrap] Complete."
