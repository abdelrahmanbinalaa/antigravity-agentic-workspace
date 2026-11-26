# Workspace Rules & Skill Routing

All skills in `.agents/skills/` follow the open `SKILL.md` standard and load automatically when working in this repository (Local or Antigravity Remote).

- Read `AGENTS.md` at the repository root for full operational guidance.
- Never commit API keys, `.env` files, or raw credentials; store secrets in environment variables or local user configs only (`configs/mcp_config.template.json` holds sanitized templates).
- Place temporary investigation runs inside `research_runs/` and swarm runs inside `swarm_runs/` (both gitignored).
