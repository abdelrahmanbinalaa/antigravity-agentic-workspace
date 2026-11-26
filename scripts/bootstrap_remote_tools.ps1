$ErrorActionPreference = "Stop"

Write-Host "[bootstrap] Checking Python environment..."
python --version

New-Item -ItemType Directory -Force -Path "research_runs", "swarm_runs" | Out-Null

Write-Host "[bootstrap] Installing Python packages from requirements.txt..."
python -m pip install -q -r requirements.txt

Write-Host "[bootstrap] Verifying deterministic skill engines..."
python .agents/skills/deep-research/scripts/dr_engine.py --help | Out-Null
python .agents/skills/agent-swarm/scripts/swarm_coordinator.py --help | Out-Null

Write-Host "[bootstrap] Complete."
