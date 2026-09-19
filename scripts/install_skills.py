#!/usr/bin/env python3
"""Copy skills for Codex or Claude Code; preview and refuse existing names."""
import argparse
from pathlib import Path
import shutil
import sys


CLIENT_DIRS = {"codex": ".agents", "claude": ".claude"}


def destinations(client: str, project: Path | None = None,
                 user: bool = False, home: Path | None = None) -> list[Path]:
    if user == (project is not None):
        raise ValueError("Choose either a project or user-wide installation")
    base = (home or Path.home()) if user else project.expanduser()
    if not user and not base.is_dir():
        raise ValueError(f"Project folder does not exist: {base}")
    clients = list(CLIENT_DIRS) if client == "both" else [client]
    return [base / CLIENT_DIRS[name] / "skills" for name in clients]


def install_many(source: Path, targets: list[Path], dry_run: bool = False) -> list[str]:
    source = source.resolve()
    targets = [p.expanduser().resolve() for p in targets]
    skills = sorted(p for p in source.iterdir() if (p / "SKILL.md").is_file())
    if not skills:
        raise ValueError("No skills found in source")
    if any(skill.is_symlink() or any(p.is_symlink() for p in skill.rglob("*"))
           for skill in skills):
        raise ValueError("Source skill resources must not be symlinks")
    if not targets or len(set(targets)) != len(targets):
        raise ValueError("Installation destinations must be nonempty and distinct")
    # Preflight every client before copying any skills.
    for target in targets:
        for parent in [target, *target.parents]:
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"Not a directory: {parent}")
    conflicts = [str(target / skill.name) for target in targets for skill in skills
                 if (target / skill.name).exists() or (target / skill.name).is_symlink()]
    if conflicts:
        raise ValueError("Refusing to overwrite: " + ", ".join(conflicts))
    if not dry_run:
        for target in targets:
            target.mkdir(parents=True, exist_ok=True)
            for skill in skills:
                shutil.copytree(skill, target / skill.name,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return [p.name for p in skills]


def install(source: Path, destination: Path) -> list[str]:
    """Backward-compatible single destination API."""
    return install_many(source, [destination])


def main() -> int:
    # Keep the terminal encoding; escape unsupported path characters in legacy pipes.
    sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", type=Path, help="Existing research project folder")
    group.add_argument("--global", dest="user", action="store_true",
                       help="Install for all projects of the current OS user")
    group.add_argument("--destination", type=Path, help="Explicit skill directory")
    parser.add_argument("--client", choices=["codex", "claude", "both"], default=None)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()
    if args.destination and args.client:
        parser.error("--destination cannot be combined with --client")
    try:
        targets = ([args.destination] if args.destination else
                   destinations(args.client or "codex", args.project, args.user))
        names = install_many(Path(__file__).resolve().parents[1] / "skills", targets,
                             args.dry_run)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Installation stopped: {exc}\n")
    for target in targets:
        print(f"{'Would install' if args.dry_run else 'Installed'} {len(names)} skills to "
              f"{target.expanduser().resolve()}")
    if not args.dry_run:
        print("Open your research project and check the skill selector; "
              "start a new session if the skills have not appeared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
