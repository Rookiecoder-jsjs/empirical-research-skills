#!/usr/bin/env python3
"""Dependency-free structure, link and syntax checks for this skill bundle."""
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"empirical-" + suffix for suffix in (
    "workflow", "setup", "project", "data", "analysis", "explore", "writing", "audit")}


def validate(root: Path) -> list[str]:
    problems = []
    skills = {p.name: p for p in (root / "skills").iterdir() if p.is_dir()}
    if set(skills) != NAMES:
        problems.append("Expected exactly the eight documented skill folders")
    for name, folder in skills.items():
        path = folder / "SKILL.md"
        if not path.exists():
            problems.append(f"Missing SKILL.md: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        front = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: (\"[^\n]*\")\n---\n", text)
        if not front or front[1] != name:
            problems.append(f"Invalid frontmatter: {name}")
        else:
            try:
                description = json.loads(front[2])
                if not description or len(description) > 1024:
                    problems.append(f"Invalid description length: {name}")
            except ValueError:
                problems.append(f"Invalid quoted description: {name}")
        metadata = folder / "agents" / "openai.yaml"
        if not metadata.exists() or f"${name}" not in metadata.read_text(encoding="utf-8"):
            problems.append(f"Missing UI metadata or invocation: {name}")
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "[TODO:" in text:
            problems.append(f"Unfinished scaffold: {path.relative_to(root)}")
        if sum(line.startswith("```") for line in text.splitlines()) % 2:
            problems.append(f"Unbalanced code fences: {path.relative_to(root)}")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            link = target.split("#", 1)[0]
            if not (path.parent / link).exists():
                problems.append(f"Broken resource link in {path.relative_to(root)}: {target}")
    for path in root.rglob("*.py"):
        if ".git" not in path.parts:
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                problems.append(str(exc))
    return problems


if __name__ == "__main__":
    errors = validate(ROOT)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("Eight skills: metadata, resource links, fences and Python syntax checked.")
