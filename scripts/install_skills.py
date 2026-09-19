#!/usr/bin/env python3
"""Install the bundled skills without overwriting existing destinations."""
import argparse
from pathlib import Path
import shutil


def install(source: Path, destination: Path) -> list[str]:
    source, destination = source.resolve(), destination.resolve()
    skills = sorted(p for p in source.iterdir() if (p / "SKILL.md").is_file())
    if not skills:
        raise ValueError("No skills found in source")
    conflicts = [p.name for p in skills if (destination / p.name).exists()
                 or (destination / p.name).is_symlink()]
    if conflicts:
        raise ValueError("Refusing to overwrite: " + ", ".join(conflicts))
    if any(p.is_symlink() for skill in skills for p in skill.rglob("*")):
        raise ValueError("Source skill resources must not be symlinks")
    destination.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(skill, destination / skill.name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return [p.name for p in skills]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", type=Path)
    group.add_argument("--destination", type=Path)
    args = parser.parse_args()
    destination = args.destination if args.destination else args.project / ".agents" / "skills"
    try:
        names = install(Path(__file__).resolve().parents[1] / "skills", destination)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Installation stopped: {exc}\n")
    print(f"Installed {len(names)} skills to {destination.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
