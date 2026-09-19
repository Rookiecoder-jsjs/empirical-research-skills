#!/usr/bin/env python3
"""Preview or create a new research workspace; never overwrite an existing project."""
import argparse
import json
from pathlib import Path

PATHS = {
    "raw": "data", "analysis_data": "processed/panels",
    "intermediate": "processed/intermediate", "results": "processed/results",
    "scripts": "scripts", "literature": "literature",
    "manuscript": "manuscript", "experiments": "experiments",
}
DIRECTORIES = list(PATHS.values()) + ["scripts/clean", "scripts/analysis",
                                      "scripts/figures", "scripts/utils"]


def initialize(root: Path, create: bool = False) -> dict:
    root = root.resolve()
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ValueError("Target must be absent or empty; existing projects require explicit mapping")
    config = {
        "schema_version": 1, "project_title": "", "python_version": "3.11",
        "paths": PATHS,
        "data_contract": {"unit": None, "time": None, "keys": [], "required": [],
                          "missing_values": ["", "NA"]},
        "research_design": {"question": None, "estimand": None,
                            "method": None, "assumptions": []},
    }
    files = {
        "research-project.json": json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        "workflow.json": json.dumps({"schema_version": 1, "raw_paths": ["data"],
                                     "state_dir": "processed/results", "steps": []}, indent=2) + "\n",
        "requirements.txt": "# Declare only the packages needed by this study.\n# Record versions after compatibility is verified. No analysis packages are installed by this template.\n",
        ".gitignore": ".venv/\n__pycache__/\n*.py[cod]\n.env\n.env.*\ndata/\nprocessed/\nexperiments/\n",
        "AGENTS.md": "# Research project\n\nRead research-project.json and workflow.json before running analysis.\n"
        "Respect existing user instructions. Base inputs in data/ are read-only during analysis.\n"
        "Keep processing reproducible in scripts/ and generated outputs in processed/.\n"
        "Keep exploratory scripts and all generated artifacts in experiments/<topic>/.\n"
        "Do not adopt a candidate specification without the user's stated scope.\n"
        "Record actual input versions, parameters, seeds, methods, and inference.\n"
        "Do not choose models to obtain significance or reproduce a preferred number.\n"
        "Check evidence before writing claims. Generate document exports only when requested.\n"
        "Do not commit, push, publish, or send research artifacts without authorization.\n",
    }
    if create:
        root.mkdir(parents=True, exist_ok=True)
        for directory in DIRECTORIES:
            (root / directory).mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            with (root / name).open("x", encoding="utf-8") as out:
                out.write(content)
    return {"project": str(root), "created": create, "directories": DIRECTORIES,
            "files": list(files), "note": "Configure the research question, data contract and dependencies before analysis."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--create", action="store_true")
    args = parser.parse_args()
    try:
        result = initialize(args.project, args.create)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Initialization stopped: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
