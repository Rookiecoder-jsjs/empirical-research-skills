#!/usr/bin/env python3
"""Read-only CSV contract checks; report counts and row numbers, never raw records."""
import argparse
import csv
import json
import math
from pathlib import Path


def check_csv(path: Path, keys=(), required=(), numeric=(), lower=None, upper=None,
              missing=("", "NA", "N/A", "NaN", "null"), delimiter=",") -> dict:
    lower, upper = lower or {}, upper or {}
    numeric = set(numeric) | set(lower) | set(upper)
    required, keys = set(required), list(keys)
    missing = set(missing)
    errors, missing_counts, seen, rows = [], {}, set(), 0
    for name in set(lower) & set(upper):
        if lower[name] > upper[name]:
            raise ValueError(f"Minimum exceeds maximum for {name}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        columns = reader.fieldnames or []
        if not columns or len(columns) != len(set(columns)) or any(not x.strip() for x in columns):
            raise ValueError("CSV requires nonempty unique column names")
        absent = (set(keys) | required | numeric) - set(columns)
        if absent:
            raise ValueError("Missing columns: " + ", ".join(sorted(absent)))
        missing_counts = dict.fromkeys(columns, 0)
        counts = {"malformed_rows": 0, "empty_keys": 0, "duplicate_keys": 0,
                  "required_missing": 0, "invalid_numeric": 0, "out_of_range": 0}

        def issue(kind, line, column=None):
            counts[kind] += 1
            if len(errors) < 30:
                errors.append({"kind": kind, "line": line, "column": column})

        for record in reader:
            rows += 1
            line = reader.line_num
            if None in record or any(v is None for v in record.values()):
                issue("malformed_rows", line)
                continue
            values = {name: value.strip() for name, value in record.items()}
            for name, value in values.items():
                if value in missing:
                    missing_counts[name] += 1
                    if name in required:
                        issue("required_missing", line, name)
            if keys:
                key = tuple(values[k] for k in keys)
                if any(v in missing for v in key):
                    issue("empty_keys", line)
                elif key in seen:
                    issue("duplicate_keys", line)
                else:
                    seen.add(key)
            for name in sorted(numeric):
                value = values[name]
                if value in missing:
                    continue
                try:
                    number = float(value)
                    if not math.isfinite(number):
                        raise ValueError()
                except ValueError:
                    issue("invalid_numeric", line, name)
                    continue
                if (name in lower and number < lower[name]) or (name in upper and number > upper[name]):
                    issue("out_of_range", line, name)
    return {"ok": rows > 0 and not any(counts.values()), "rows": rows, "columns": columns,
            "counts": counts, "missing": missing_counts, "issues_first_30": errors,
            "empty_data": rows == 0}


def bounds(values: list[str]) -> dict:
    result = {}
    for item in values:
        name, sep, raw = item.partition("=")
        if not sep or not name:
            raise ValueError("Bounds must use column=number")
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError("Bounds must be finite")
        result[name] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    for flag in ("key", "required", "numeric", "min", "max", "missing"):
        parser.add_argument("--" + flag, action="append", default=[])
    parser.add_argument("--delimiter", default=",")
    args = parser.parse_args()
    try:
        report = check_csv(args.csv, args.key, args.required, args.numeric,
                           bounds(args.min), bounds(args.max),
                           ["", "NA", "N/A", "NaN", "null"] + args.missing, args.delimiter)
    except (OSError, ValueError, csv.Error, TypeError) as exc:
        parser.exit(1, f"CSV check stopped: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
