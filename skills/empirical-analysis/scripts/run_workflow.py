#!/usr/bin/env python3
"""Plan or execute a declared, serial research workflow. This is not a sandbox."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import uuid


def safe_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("Declared paths must be nonempty project-relative strings")
    # Reject both path syntaxes even when validating on another OS.
    if "\\" in value or re.match(r"^[A-Za-z]:", value):
        raise ValueError("Use portable forward-slash project-relative paths")
    path = (root / value).resolve()
    if path == root or not path.is_relative_to(root):
        raise ValueError(f"Path leaves project or names its root: {value}")
    return path


def strings(value, label):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise ValueError(f"{label} must be an array of nonempty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"Duplicate entries in {label}")
    return value


def load_manifest(root: Path, manifest: str) -> dict:
    raw = json.loads(safe_path(root, manifest).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise ValueError("Expected workflow schema_version 1")
    raw_paths = strings(raw.get("raw_paths", ["data"]), "raw_paths")
    if not raw_paths:
        raise ValueError("Declare at least one protected raw input directory")
    protected = [safe_path(root, p) for p in raw_paths]
    state_dir = safe_path(root, raw.get("state_dir", "processed/results"))
    if any(state_dir == p or state_dir.is_relative_to(p) for p in protected):
        raise ValueError("State directory overlaps raw inputs")
    steps = raw.get("steps")
    if not isinstance(steps, list):
        raise ValueError("steps must be an array")
    by_id, outputs = {}, {}
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError("Each step must be an object")
        key = step.get("id")
        if not isinstance(key, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", key):
            raise ValueError("Step IDs must contain letters, digits, dots, hyphens or underscores")
        if key in by_id:
            raise ValueError(f"Duplicate step ID: {key}")
        command = step.get("command")
        if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command) or not command[0]:
            raise ValueError(f"Invalid command array: {key}")
        for field in ("inputs", "code", "outputs", "depends_on"):
            strings(step.get(field, []), f"{key}.{field}")
            step.setdefault(field, [])
        if not step["code"] or not step["outputs"]:
            raise ValueError(f"Declare code and outputs for step {key}")
        for value in step["inputs"] + step["code"]:
            safe_path(root, value)
        for value in step["outputs"]:
            path = safe_path(root, value)
            if any(path == p or path.is_relative_to(p) for p in protected):
                raise ValueError(f"Output overlaps protected raw inputs: {value}")
            if path == state_dir or state_dir.is_relative_to(path):
                raise ValueError("Output cannot contain the state directory")
            if path.parent == state_dir and (path.name == "workflow_state.json" or path.name.startswith("run_")):
                raise ValueError("Output uses a reserved run-record filename")
            if path in outputs or any(path.is_relative_to(p) or p.is_relative_to(path) for p in outputs):
                raise ValueError(f"Overlapping output: {value}")
            outputs[path] = key
        by_id[key] = step
    raw["_steps"] = by_id
    order = plan(raw, [])  # Also validates cycles and unknown dependencies globally.
    ancestors = {}
    for key in order:
        step = by_id[key]
        ancestors[key] = set(step["depends_on"])
        for parent in step["depends_on"]:
            ancestors[key].update(ancestors[parent])
        for value in step["inputs"] + step["code"]:
            producer = outputs.get(safe_path(root, value))
            if producer is not None and producer not in ancestors[key]:
                raise ValueError(f"{key} reads an output without its producer dependency: {producer}")
    return raw


def plan(manifest: dict, targets: list[str]) -> list[str]:
    steps, active, done, order = manifest["_steps"], set(), set(), []

    def visit(key):
        if key not in steps:
            raise ValueError(f"Unknown step: {key}")
        if key in active:
            raise ValueError(f"Dependency cycle at {key}")
        if key in done:
            return
        active.add(key)
        for parent in steps[key]["depends_on"]:
            visit(parent)
        active.remove(key)
        done.add(key)
        order.append(key)

    for key in targets or steps:
        visit(key)
    return order


def digest_file(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"Declared file missing or not a file: {path.name}")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def environment() -> dict:
    packages = sorted((d.metadata.get("Name", "unknown"), d.version)
                      for d in importlib.metadata.distributions())
    return {"python": platform.python_version(), "platform": platform.platform(),
            "executable": sys.executable, "packages": packages,
            "runner_sha256": digest_file(Path(__file__))}


def output_snapshot(root: Path, paths: list[str]) -> dict:
    result = {}
    for value in paths:
        path = safe_path(root, value)
        if path.is_file():
            stat = path.stat()
            result[value] = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size,
                             stat.st_ino, digest_file(path))
    return result


def save(path: Path, value) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def execute(root: Path, manifest: dict, targets: list[str], resume=False) -> dict:
    order = plan(manifest, targets)
    state_dir = safe_path(root, manifest.get("state_dir", "processed/results"))
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "workflow_state.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {"steps": {}}
    if not isinstance(state, dict) or not isinstance(state.get("steps"), dict):
        raise ValueError("Invalid workflow state; preserve and inspect it before rerunning")
    env = environment()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
    report = {"run_id": run_id, "ok": True, "environment": env, "steps": []}
    report_file = state_dir / f"run_{run_id}.json"
    fingerprints = {}
    for key in order:
        step = manifest["_steps"][key]
        record = {"id": key, "status": "running"}
        old = state["steps"].get(key, {})
        try:
            files = {p: digest_file(safe_path(root, p)) for p in step["inputs"] + step["code"]}
            signature = digest({"step": step, "files": files, "environment": env,
                                "dependencies": {p: fingerprints[p] for p in step["depends_on"]}})
            fingerprints[key] = signature
            current_outputs = None
            try:
                current_outputs = {p: digest_file(safe_path(root, p)) for p in step["outputs"]}
            except ValueError:
                pass
            if resume and old.get("status") == "success" and old.get("fingerprint") == signature and old.get("outputs") == current_outputs and current_outputs is not None:
                record.update(status="skipped", fingerprint=signature)
                report["steps"].append(record)
                continue
            record.update(fingerprint=signature, input_hashes=files, started_at=datetime.now(timezone.utc).isoformat())
            state["steps"][key] = dict(record)  # Invalidate previous success before running.
            save(state_file, state)
            before_outputs = output_snapshot(root, step["outputs"])
            command = [sys.executable if x == "{python}" else x for x in step["command"]]
            logfile = state_dir / f"run_{run_id}_{key}.log"
            record["command"] = command
            record["log"] = str(logfile.relative_to(root))
            with logfile.open("wb") as stream:
                result = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT, check=False)
            record["returncode"] = result.returncode
            if result.returncode != 0:
                raise ValueError(f"Step exited with code {result.returncode}; inspect its log")
            record["outputs"] = {p: digest_file(safe_path(root, p)) for p in step["outputs"]}
            after_outputs = output_snapshot(root, step["outputs"])
            unchanged = [p for p in before_outputs if before_outputs[p] == after_outputs.get(p)]
            if unchanged:
                raise ValueError("Declared outputs were not refreshed: " + ", ".join(unchanged))
            # Declared inputs/code must remain unchanged during execution.
            if files != {p: digest_file(safe_path(root, p)) for p in files}:
                raise ValueError("A declared input or code file changed during execution")
            record["status"] = "success"
        except (OSError, ValueError, KeyboardInterrupt) as exc:
            record.update(status="failed", error=str(exc) or "Interrupted")
            report["ok"] = False
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        state["steps"][key] = dict(record)
        report["steps"].append(record)
        save(state_file, state)
        save(report_file, report)
        if not report["ok"]:
            break
    save(report_file, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--manifest", default="workflow.json")
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.resume and not args.execute:
        parser.error("--resume requires --execute")
    root = args.project.resolve()
    try:
        manifest = load_manifest(root, args.manifest)
        if args.execute:
            report = execute(root, manifest, args.target, args.resume)
        else:
            report = {"mode": "plan", "ok": True, "writes": False,
                      "steps": [manifest["_steps"][k] for k in plan(manifest, args.target)]}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Workflow stopped: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
