"""Descriptive calculation on intentionally artificial demo observations."""
import csv
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "data" / "synthetic.csv").open(encoding="utf-8", newline="") as stream:
    values = [float(row["outcome"]) for row in csv.DictReader(stream)]
output = ROOT / "processed" / "results" / "summary.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"synthetic": True, "n": len(values),
                              "mean": statistics.mean(values)}, indent=2) + "\n", encoding="utf-8")
