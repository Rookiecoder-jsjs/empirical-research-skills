#!/usr/bin/env python3
"""Report interpreter ownership and installed package metadata without installing software."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys


def inspect(project: Path, version: str | None, required: list[str]) -> dict:
    root = project.resolve()
    expected = (root / ".venv").resolve()
    issues = []
    if not root.is_dir():
        issues.append("Project directory does not exist")
    if Path(sys.prefix).resolve() != expected or sys.prefix == sys.base_prefix:
        issues.append("This process is not using the project's .venv; use its Python executable")
    if version:
        try:
            wanted = tuple(int(part) for part in version.split("."))
        except ValueError as exc:
            raise ValueError("Python version must be numeric, e.g. 3.11 or 3.11.9") from exc
        if not 1 <= len(wanted) <= 3:
            raise ValueError("Python version must have one to three components")
        if tuple(sys.version_info[:len(wanted)]) != wanted:
            issues.append(f"Python does not match requested version {version}")
    packages = {}
    for name in required:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
            issues.append(f"Missing distribution: {name}")
    uv_path = shutil.which("uv")
    uv_version = None
    if uv_path:
        try:
            check = subprocess.run([uv_path, "--version"], capture_output=True, text=True,
                                   timeout=10, check=True)
            uv_version = check.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            issues.append("uv exists but its version check failed")
    else:
        issues.append("uv is not on PATH")
    slope, intercept = statistics.linear_regression([0, 1, 2, 3], [1, 3, 5, 7])
    smoke_ok = abs(slope - 2) < 1e-12 and abs(intercept - 1) < 1e-12
    if not smoke_ok:
        issues.append("Standard-library synthetic regression check failed")
    return {"ok": not issues, "project": str(root), "python": platform.python_version(),
            "executable": sys.executable, "prefix": sys.prefix, "expected_prefix": str(expected),
            "uv": uv_version, "packages": packages, "stdlib_smoke_ok": smoke_ok,
            "issues": issues, "limits": "Package metadata only; run uv pip check and task-specific imports/computations separately. No scientific or document pipeline was run."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--python-version")
    parser.add_argument("--require", action="append", default=[])
    args = parser.parse_args()
    try:
        report = inspect(args.project, args.python_version, args.require)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Environment check stopped: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
