"""Decision metrics: "regret" of every algorithm = its median time divided by the best median time
of the same (order, size) cell. 1.00 = fastest. Used for the final recommendation.

usage: python decision_metrics.py [SUMMARY_CELLS_CSV] [OUT_DIR]
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import ALGS, COLOR, MARKER, ORDER_LABEL, ORDERS, ROOT, style

src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "analysis/out/main/summary_cells.csv"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent
s = pd.read_csv(src)
s = s[s["size"] >= 1000]
p = s.pivot_table(index=["order", "size"], columns="algorithm", values="median_of_fork_medians")
reg = p.div(p.min(axis=1), axis=0)
reg.to_csv(out / "regret_cells.csv")

rows = []
for a in ALGS:
    r = reg[a]
    rows.append({
        "algorithm": a,
        "cells": len(r),
        "cells_fastest": int((r <= 1.0 + 1e-12).sum()),
        "geomean_regret": float(np.exp(np.log(r).mean())),
        "median_regret": float(r.median()),
        "max_regret": float(r.max()),
        "max_regret_where": "{} n={}".format(*r.idxmax()),
        "cells_within_5pct_of_best": int((r <= 1.05).sum()),
        "cells_over_2x_best": int((r > 2).sum()),
    })
summ = pd.DataFrame(rows)
summ.to_csv(out / "regret_summary.csv", index=False)
print(summ.to_string(index=False))

# per-order maximum regret (n >= 1000), as a dot plot on a log axis
style()
fig, ax = plt.subplots(figsize=(7.2, 3.4))
x = np.arange(len(ORDERS))
for k, a in enumerate(ALGS):
    mx = [reg.loc[o][a].max() for o in ORDERS]
    ax.plot(x + (k - 1) * 0.18, mx, MARKER[a], color=COLOR[a], label=a, markersize=7,
            markeredgecolor="white", markeredgewidth=1.2)
ax.axhline(1.0, color="#52514e", lw=0.8)
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels([ORDER_LABEL[o].replace(" (", "\n(") for o in ORDERS], fontsize=7.5)
ax.set_ylabel("worst-case slowdown vs. fastest\n(n ≥ 1000; 1 = best)")
ax.set_xlabel("input order")
ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, 1.13))
fig.tight_layout()
fig.savefig(out / "fig_regret.png")
