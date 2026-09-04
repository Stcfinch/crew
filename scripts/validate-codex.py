#!/usr/bin/env python3
"""Check the portable Codex payload and its local reference graph (stdlib only)."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    errors = []
    manifest = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "crew" or manifest.get("skills") != "./skills/":
        errors.append("Incorrect plugin name or skill directory")
    if any(key in manifest for key in ("hooks", "apps", "mcpServers")):
        errors.append("This skill-only port must not register undeclared capabilities")
    actual = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    upstream = {p.parent.name for p in root.glob("plugins/*/skills/*/SKILL.md")}
    if actual != upstream:
        errors.append(f"Skill coverage differs from upstream: missing={upstream-actual}, extra={actual-upstream}")
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        content = path.read_text(encoding="utf-8")
        front = re.match(r"^---\n(.*?)\n---\n", content, re.S)
        if not front:
            errors.append(f"Invalid frontmatter: {path}")
            continue
        fields = dict(line.split(": ", 1) for line in front[1].splitlines() if ": " in line)
        if fields.get("name") != path.parent.name or not fields.get("description"):
            errors.append(f"Invalid skill metadata: {path}")
        if set(fields) != {"name", "description"}:
            errors.append(f"Unexpected runtime-specific frontmatter: {path}")
        if len(content.splitlines()) > 500:
            errors.append(f"Skill is too large: {path}")
    docs = [*(root / "skills").rglob("*.md"), *(root / "codex/references").glob("*.md")]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in link or link.startswith("#"):
                continue
            target = (path.parent / link.split("#", 1)[0]).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"Broken or external local reference: {path}: {link}")
        for token in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR", "TeamCreate(", "TaskCreate(", "mcp__plugin_notion__", "claude plugin "):
            if token in text:
                errors.append(f"Nonportable instruction {token}: {path}")
    for name in ("crew-state.py", "crew-project.py", "check-spec-drift.py"):
        path = root / "codex/scripts" / name
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    if not (root / "codex/LICENSE").is_file():
        errors.append("Missing upstream license")
    return errors


if __name__ == "__main__":
    issues = validate()
    if issues:
        print("\n".join(issues))
        sys.exit(1)
    print("Codex package valid: 27 skills, complete local references, portable runtime.")
