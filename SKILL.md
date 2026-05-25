---
name: dynamic-skill-mcp-router
description: Dynamically discover the currently installed skills and configured MCP servers on the local machine, then choose the best fit for a user task and provide an exact trigger phrase. Use when the user asks which skill or MCP to use, wants a recommendation based on the current environment instead of a static note, or does not want to remember trigger prompts.
metadata:
  short-description: Dynamically route tasks to installed skills and MCPs
---

# Dynamic Skill MCP Router

This skill routes a task to the best available skill or MCP based on what is actually installed on the current machine.

## Use This Skill When

- The user asks which skill should be used for a task
- The user asks which MCP should be used for a task
- The user wants a recommendation based on the current environment
- The user does not want to maintain or read a static trigger-template note
- The user wants a copy-paste trigger phrase for the next turn

## Discovery Workflow

1. Run `scripts/discover.py --json` to discover installed skills and configured MCP servers.
2. Use discovered skill names and descriptions as the primary signal for what each skill does.
3. Use the current session's MCP tool definitions as the primary signal for what each MCP can do.
4. If MCP tool definitions are not available in the current session, fall back to the MCP server name plus local config and clearly state that capability inference is limited.
5. Recommend only tools that were actually discovered.

## Routing Workflow

1. Decide whether the task benefits from a specialized skill or MCP at all.
2. If yes, choose one primary recommendation.
3. If there is a reasonable alternative, provide one fallback.
4. Return one exact trigger phrase the user can copy next time.
5. If the user wants to continue immediately, proceed with the chosen skill or MCP.

## Output Format

Use this compact structure:

- `Best fit:` the single best discovered skill or MCP
- `Why:` one short reason tied to the task
- `Trigger:` one sentence the user can copy next time
- `Fallback:` only when there is a reasonable second choice

If no specialized tool is clearly beneficial, say:

- `Best fit: none`
- `Why:` normal Codex behavior is enough for this task

## Trigger Construction Rules

- For skills, prefer: `Use <skill-name> ...`
- For MCP tools, prefer: `Prefer <mcp-name> ...` or `Use <mcp-name> ...`
- If the best fit is `codegraph` and the project does not have `.codegraph/`, tell the user to initialize it with `codegraph init -i`.
- If the recommendation depends on assumptions because MCP capability data is incomplete, state that explicitly.

## Important Constraints

- Do not invent skills or MCPs that were not discovered.
- Do not dump the entire inventory unless the user asks for a list.
- Do not rely on a static local note as the source of truth.
- Treat the current machine's environment as the source of truth.
