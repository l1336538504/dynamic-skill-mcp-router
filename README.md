# Dynamic Skill MCP Router

`dynamic-skill-mcp-router` is a Codex skill that inspects the local environment, discovers the skills and MCP servers that are actually available, and recommends the best fit for a given task.

Instead of relying on a static cheat sheet, it routes based on what is installed right now.

## Features

- Discovers installed skills from common local skill directories
- Discovers configured MCP servers from the active Codex config
- Uses discovered skill metadata as the primary signal for skill intent
- Helps choose the best fit for a user task
- Returns an exact trigger phrase the user can copy into the next turn

## Installation

Install either by copying the skill into your Codex skills directory, or from GitHub using the Skills CLI.

### From a local checkout

Copy the directory into your Codex skills folder:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /path/to/dynamic-skill-mcp-router "${CODEX_HOME:-$HOME/.codex}/skills/dynamic-skill-mcp-router"
```

### From GitHub

If this repository contains only this single skill at the repo root:

```bash
npx skills add <owner>/<repo> -g -y
```

If this skill lives in a larger repository and needs to be installed by explicit skill name:

```bash
npx skills add https://github.com/<owner>/<repo> --skill dynamic-skill-mcp-router -g -y
```

If you are not using the Skills CLI, copy the directory into:

```text
$CODEX_HOME/skills/dynamic-skill-mcp-router
```

If `CODEX_HOME` is unset, the default is usually:

```text
~/.codex/skills/dynamic-skill-mcp-router
```

Restart Codex after installation so the new skill is discovered reliably.

## Usage

Prompt example:

```text
Use dynamic-skill-mcp-router to decide which installed skill or MCP is best for this task: explain how authentication flows through this codebase.
```

Prompt example:

```text
Use dynamic-skill-mcp-router to recommend the best tool for this task and give me the exact trigger phrase: review this .pcap file for suspicious traffic.
```

Prompt example:

```text
Use dynamic-skill-mcp-router to inspect my current environment and tell me whether I should use a skill or an MCP for this job: update the OpenAPI definition in Apifox.
```

## How Discovery Works

The bundled `scripts/discover.py` script checks:

- `$CODEX_HOME/skills`
- `~/.agents/skills`
- `~/.understand-anything/repo/understand-anything-plugin/skills`
- `$CODEX_HOME/config.toml` for configured MCP servers

It does not assume that every machine has the same setup.

You can override the defaults:

```bash
python3 scripts/discover.py --json \
  --codex-home /custom/codex-home \
  --config /custom/codex-home/config.toml \
  --skill-root /custom/skills \
  --skill-root /another/skills
```

You can also use environment variables:

```bash
export DYNAMIC_SKILL_MCP_ROUTER_CODEX_CONFIG=/custom/codex/config.toml
export DYNAMIC_SKILL_MCP_ROUTER_SKILL_ROOTS=/custom/skills:/another/skills
python3 scripts/discover.py --json
```

## Repository Structure

```text
dynamic-skill-mcp-router/
├── .gitignore
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── discover.py
```

## Notes

- Skill discovery is based on each skill's `SKILL.md` frontmatter and description.
- MCP discovery is based on the active Codex config. Understanding what an MCP can do still depends on the MCP tool definitions available in the running session.
- The default discovery locations are conventions, not requirements. The script supports overrides for other setups.
- This skill is intentionally small. It is a router, not a replacement for the underlying skill or MCP documentation.
