#!/usr/bin/env python3
"""Applies the rule in REMEASURE_RULE.md and re-measures the uncertain (order, size) groups.

Usage:  python3 scripts/remeasure.py [--dry-run]

1. reads results/full/raw.csv (+ analysis/out/main/hypothesis_cells.csv, if present),
2. writes results/remeasure/plan.csv (which groups are uncertain and WHY),
3. runs scripts/run_experiment.py for every uncertain group with fork ids 10..29.
"""
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "results" / "full" / "raw.csv"
HYP = ROOT / "analysis" / "out" / "main" / "hypothesis_cells.csv"
OUT = ROOT / "results" / "remeasure"
EXTRA_FORKS, FORK_START, ITERS = 20, 10, 30
CV_LIMIT, CI_LIMIT = 0.05, 0.03


def main() -> int:
    dry = "--dry-run" in sys.argv
    df = pd.read_csv(FULL)
    fm = df.groupby(["algorithm", "order", "size", "fork"], as_index=False).ns_per_sort.median()
    hyp = pd.read_csv(HYP) if HYP.exists() else None
    plan = []
    for (o, n), g in df[df["size"] >= 1000].groupby(["order", "size"]):
        why = []
        for a, ga in fm[(fm.order == o) & (fm["size"] == n)].groupby("algorithm"):
            x = ga.ns_per_sort.values
            cv = x.std(ddof=1) / x.mean()
            half = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / math.sqrt(len(x)) / x.mean()
            if cv > CV_LIMIT:
                why.append(f"{a}: CV {cv * 100:.1f} % > 5 %")
            if half > CI_LIMIT:
                why.append(f"{a}: CI half-width {half * 100:.1f} % > 3 %")
        if g.gc_during.sum() > 0:
            why.append(f"{int(g.gc_during.sum())} timed batches with GC")
        if g.warmup_timeout.sum() > 0:
            why.append("warm-up timeout")
        if hyp is not None:
            h = hyp[(hyp.order == o) & (hyp["size"] == n) & (hyp.verdict == "inconclusive")]
            for _, r in h.iterrows():
                why.append(f"{r.hypothesis} inconclusive ({r.claim})")
        plan.append(dict(order=o, size=n, uncertain=bool(why), reasons="; ".join(why)))
    plan = pd.DataFrame(plan)
    OUT.mkdir(parents=True, exist_ok=True)
    plan.to_csv(OUT / "plan.csv", index=False)
    todo = plan[plan.uncertain]
    print(f"{len(todo)} of {len(plan)} groups are uncertain")
    print(todo.to_string(index=False))
    if dry:
        return 0
    for _, r in todo.iterrows():
        out = OUT / f"{r.order}_{r['size']}"
        cmd = [sys.executable, str(ROOT / "scripts" / "run_experiment.py"), "--out", str(out), "--classes", str(ROOT / "bin"),
               "--orders", r.order, "--sizes", str(r["size"]), "--forks", str(EXTRA_FORKS), "--fork-start", str(FORK_START),
               "--iters", str(ITERS)]
        print(" ".join(cmd), flush=True)
        if subprocess.run(cmd, cwd=ROOT).returncode != 0:
            print("FAILED", r.order, r["size"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
