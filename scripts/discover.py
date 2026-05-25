#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


ENV_CODEX_CONFIG = "DYNAMIC_SKILL_MCP_ROUTER_CODEX_CONFIG"
ENV_SKILL_ROOTS = "DYNAMIC_SKILL_MCP_ROUTER_SKILL_ROOTS"


def expand_path(raw: str) -> Path:
    return Path(raw).expanduser()


def resolve_codex_home(raw: str | None) -> Path:
    if raw:
        return expand_path(raw)
    return expand_path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))


def default_skill_roots(base_codex_home: Path) -> list[Path]:
    home = Path.home()
    return [
        base_codex_home / "skills",
        home / ".agents" / "skills",
        home / ".understand-anything" / "repo" / "understand-anything-plugin" / "skills",
    ]


def resolve_skill_roots(base_codex_home: Path, roots: list[str] | None) -> list[Path]:
    if roots:
        return [expand_path(root) for root in roots]

    env_value = os.environ.get(ENV_SKILL_ROOTS, "")
    if env_value:
        return [expand_path(root) for root in env_value.split(os.pathsep) if root.strip()]

    return default_skill_roots(base_codex_home)


def resolve_codex_config(base_codex_home: Path, raw: str | None) -> Path:
    if raw:
        return expand_path(raw)

    env_value = os.environ.get(ENV_CODEX_CONFIG)
    if env_value:
        return expand_path(env_value)

    return base_codex_home / "config.toml"


def extract_frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return match.group(1) if match else ""


def parse_frontmatter(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in {"name", "description"}:
            result[key] = value
    return result


def discover_skills(skill_roots: list[Path]) -> list[dict[str, str]]:
    discovered: list[dict[str, str]] = []
    seen_paths: set[str] = set()

    for root in skill_roots:
        if not root.exists():
            continue
        for skill_md in sorted(root.glob("*/SKILL.md")):
            skill_dir = skill_md.parent
            if str(skill_dir) in seen_paths:
                continue
            seen_paths.add(str(skill_dir))

            text = skill_md.read_text(encoding="utf-8")
            frontmatter = parse_frontmatter(extract_frontmatter(text))
            discovered.append(
                {
                    "name": frontmatter.get("name", skill_dir.name),
                    "description": frontmatter.get("description", ""),
                    "path": str(skill_dir),
                    "source": str(root),
                }
            )

    return discovered


def discover_mcps(config_path: Path) -> list[dict[str, str]]:
    if not config_path.exists():
        return []

    text = config_path.read_text(encoding="utf-8")
    pattern = re.compile(r"^\[mcp_servers\.([^\]]+)\]$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    discovered: list[dict[str, str]] = []

    for index, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]

        command_match = re.search(r'^command\s*=\s*"([^"]+)"', block, re.MULTILINE)
        args_match = re.search(r"^args\s*=\s*\[(.*?)\]", block, re.MULTILINE | re.DOTALL)

        command = command_match.group(1) if command_match else ""
        args = ""
        if args_match:
            args = " ".join(re.findall(r'"([^"]+)"', args_match.group(1)))

        discovered.append(
            {
                "name": name,
                "command": command,
                "args": args,
                "config_path": str(config_path),
            }
        )

    return discovered


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover installed skills and MCP servers.")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--codex-home",
        help="Override CODEX_HOME for discovery. Defaults to $CODEX_HOME or ~/.codex.",
    )
    parser.add_argument(
        "--config",
        help="Override the Codex config.toml path used for MCP discovery.",
    )
    parser.add_argument(
        "--skill-root",
        action="append",
        default=[],
        help="Additional or replacement skill root. Repeat to pass multiple roots.",
    )
    args = parser.parse_args()

    base_codex_home = resolve_codex_home(args.codex_home)
    skill_roots = resolve_skill_roots(base_codex_home, args.skill_root or None)
    config_path = resolve_codex_config(base_codex_home, args.config)

    payload = {
        "meta": {
            "codex_home": str(base_codex_home),
            "skill_roots": [str(root) for root in skill_roots],
            "config_path": str(config_path),
        },
        "skills": discover_skills(skill_roots),
        "mcps": discover_mcps(config_path),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("Skills:")
    for skill in payload["skills"]:
        print(f"- {skill['name']}: {skill['description']}")

    print("\nMCPs:")
    for mcp in payload["mcps"]:
        suffix = f" ({mcp['command']} {mcp['args']})".rstrip()
        print(f"- {mcp['name']}{suffix}")


if __name__ == "__main__":
    main()
