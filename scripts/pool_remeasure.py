#!/usr/bin/env python3
"""Pools the main data (results/full) with the re-measured groups (results/remeasure/*) into
results/pooled/raw.csv, for the sensitivity analysis required by REMEASURE_RULE.md.
Fork ids of re-measured groups are 10..29; `seq` of the extra jobs is offset by 10000 so that
the execution-order columns stay unique."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
parts = [pd.read_csv(ROOT / "results/full/raw.csv")]
for d in sorted((ROOT / "results/remeasure").iterdir()):
    f = d / "raw.csv"
    if f.exists():
        x = pd.read_csv(f)
        x["seq"] = x["seq"] + 10000
        parts.append(x)
out = pd.concat(parts, ignore_index=True)
(ROOT / "results/pooled").mkdir(exist_ok=True)
out.to_csv(ROOT / "results/pooled/raw.csv", index=False)
print(len(out), "rows;", out.groupby(["order", "size"]).fork.nunique().value_counts().to_dict())
