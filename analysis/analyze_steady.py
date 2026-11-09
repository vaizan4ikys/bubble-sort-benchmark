#!/usr/bin/env python3
"""Level shifts inside a JVM and the steady-state check.

The audit of the main data set found that, for very short sorts, the time per sort changed by up to a factor 2
INSIDE one fork (after ~20 of the 30 timed batches), because the JIT compiler finished compiling the batch loop
while it was being timed. This script
  1. quantifies the level shifts in the main data (last 10 batches vs first 10 batches of every fork),
  2. re-analyses the main data with only the last 10 of the 30 batches per fork ("late-batch sensitivity analysis"),
  3. analyses the steady-state re-measurement (results/steady, exp01.SteadyWorker with a long adaptive stabilisation
     of the batch loop; same data, same JDK, forks 0-2) with the same pipeline as the main data,
  4. compares the three analyses (cells, ratios, hypothesis verdicts, slowdown metric) and draws the trajectories.

Usage:  python analysis/analyze_steady.py            (run from the analysis directory or the repository root)
Output: analysis/out/steady_check/ and the analyses analysis/out/main_last10/ and analysis/out/steady/.
"""
import subprocess
import sys

from common import *  # noqa: F401,F403

style()
OUT = ROOT / "analysis" / "out" / "steady_check"
OUT.mkdir(parents=True, exist_ok=True)
PY = sys.executable
SHIFT = 0.20     # |last10 / first10 - 1| above this = level shift
MILD = 0.05

main = pd.read_csv(ROOT / "results" / "full" / "raw.csv")
steady_path = ROOT / "results" / "steady" / "raw.csv"
steady = pd.read_csv(steady_path) if steady_path.exists() else None


def shifts(df, label):
    rows = []
    for (a, o, n, f), g in df.sort_values("iter").groupby(["algorithm", "order", "size", "fork"]):
        v = g.ns_per_sort.values
        f10, l10 = np.median(v[:10]), np.median(v[-10:])
        mid = (f10 + l10) / 2
        crossed = np.where(v <= mid)[0] if l10 < f10 else np.where(v >= mid)[0]
        rows.append(dict(dataset=label, algorithm=a, order=o, size=n, fork=f, first10=f10, last10=l10, ratio=l10 / f10,
                         switch_batch=int(crossed[0]) + 1 if len(crossed) else np.nan))
    r = pd.DataFrame(rows)
    r["shift"] = (r.ratio < 1 / (1 + SHIFT)) | (r.ratio > 1 + SHIFT)
    r["mild"] = ((r.ratio < 1 / (1 + MILD)) | (r.ratio > 1 + MILD)) & ~r["shift"]
    return r


sm = shifts(main, "main")
sm.to_csv(OUT / "level_shifts_main.csv", index=False, float_format="%.4f")
cells = (sm[sm["shift"]].groupby(["order", "size", "algorithm"]).agg(forks_with_shift=("fork", "size"),
         median_last_over_first=("ratio", "median"), median_switch_batch=("switch_batch", "median")).reset_index())
cells.to_csv(OUT / "level_shift_cells_main.csv", index=False, float_format="%.3f")
txt = [f"main data: {int(sm['shift'].sum())} of {len(sm)} forks have a level shift of more than {SHIFT:.0%} between the first and the last 10 batches; "
       f"{int(sm['mild'].sum())} more between {MILD:.0%} and {SHIFT:.0%}.",
       "cells with level shifts (forks with shift of 10 per cell):", cells.round(2).to_string(index=False)]

# ---------------------------------------------- 2. late-batch sensitivity analysis of the main data
derived = ROOT / "analysis" / "out" / "derived_inputs" / "main_last10"
derived.mkdir(parents=True, exist_ok=True)
main[main["iter"] >= 20].to_csv(derived / "raw.csv", index=False)
env = dict(**{"PYTHONWARNINGS": "ignore"})
subprocess.run([PY, "analyze_main.py", "analysis/out/derived_inputs/main_last10", "analysis/out/main_last10"], cwd=ROOT / "analysis",
               check=True, capture_output=True)
subprocess.run([PY, "decision_metrics.py", str(ROOT / "analysis/out/main_last10/summary_cells.csv")], cwd=ROOT / "analysis",
               check=True, capture_output=True)

# ---------------------------------------------- 3. steady-state re-measurement
variants = {"main (all 30 batches)": ROOT / "analysis/out/main",
            "main, last 10 batches": ROOT / "analysis/out/main_last10"}
if steady is not None and steady.groupby(["algorithm", "order", "size", "fork"]).ngroups >= 324:
    subprocess.run([PY, "analyze_main.py", "results/steady", "analysis/out/steady"], cwd=ROOT / "analysis", check=True, capture_output=True)
    subprocess.run([PY, "decision_metrics.py", str(ROOT / "analysis/out/steady/summary_cells.csv")], cwd=ROOT / "analysis",
                   check=True, capture_output=True)
    variants["steady-state re-measurement"] = ROOT / "analysis/out/steady"
    ss = shifts(steady, "steady")
    ss.to_csv(OUT / "level_shifts_steady.csv", index=False, float_format="%.4f")
    conv = steady.groupby(["algorithm", "order", "size", "fork"]).stab_converged.first()
    txt.append(f"steady run: {int(ss['shift'].sum())} of {len(ss)} forks with a level shift > {SHIFT:.0%}; {int(ss['mild'].sum())} with {MILD:.0%}-{SHIFT:.0%}; "
               f"stabilisation criterion met in {int(conv.sum())} of {len(conv)} forks.")
    late = ss[ss["shift"] | ss["mild"]].groupby(["order", "size", "algorithm"]).fork.size()
    txt.append("residual shifts in the steady run (forks per cell):\n" + late.to_string())

# comparison of the analyses
rows, hrows = [], []
for lab, d in variants.items():
    h = pd.read_csv(d / "hypothesis_overall.csv").set_index("hypothesis")
    r = pd.read_csv(d / "regret_summary.csv").set_index("algorithm")
    for hh in h.index:
        hrows.append(dict(analysis=lab, hypothesis=hh, supported=h.loc[hh, "supported"], falsified=h.loc[hh, "falsified"],
                          inconclusive=h.loc[hh, "inconclusive"], cells=h.loc[hh, "cells"]))
    for a in ALGS:
        rows.append(dict(analysis=lab, algorithm=a, fastest=r.loc[a, "cells_fastest"], cells=r.loc[a, "cells"],
                         within5=r.loc[a, "cells_within_5pct_of_best"], geomean_slowdown=r.loc[a, "geomean_regret"],
                         worst_slowdown=r.loc[a, "max_regret"], worst_where=r.loc[a, "max_regret_where"]))
pd.DataFrame(rows).to_csv(OUT / "regret_comparison.csv", index=False, float_format="%.4f")
pd.DataFrame(hrows).to_csv(OUT / "hypothesis_comparison.csv", index=False)
txt.append("slowdown metric (n >= 1000):\n" + pd.DataFrame(rows).round(3).to_string(index=False))
txt.append("hypothesis verdict counts:\n" + pd.DataFrame(hrows).to_string(index=False))

# key cells side by side
key = [("sorted", 100), ("sorted", 1000), ("sorted", 20000), ("nearly_local", 100), ("nearly_local", 1000), ("nearly_local", 20000),
       ("random", 5000), ("reversed", 5000), ("reversed", 20000)]
krow = []
for lab, d in variants.items():
    s = pd.read_csv(d / "summary_cells.csv")
    for o, n in key:
        x = s[(s.order == o) & (s["size"] == n)].set_index("algorithm").median_of_fork_medians
        krow.append(dict(analysis=lab, order=o, size=n, PassPerItem=x["PassPerItem"], UntilNoChange=x["UntilNoChange"],
                         WhileNeeded=x["WhileNeeded"], W_over_U=x["WhileNeeded"] / x["UntilNoChange"],
                         W_over_P=x["WhileNeeded"] / x["PassPerItem"]))
pd.DataFrame(krow).to_csv(OUT / "key_cells.csv", index=False, float_format="%.5g")
txt.append("key cells:\n" + pd.DataFrame(krow).round(4).to_string(index=False))

# ---------------------------------------------- 3b. main data versus steady state, cell by cell
if steady is not None and "steady-state re-measurement" in variants:
    fm_main = main[main.fork < 3].groupby(["algorithm", "order", "size", "fork"]).ns_per_sort.median().groupby(["algorithm", "order", "size"]).median()
    fm_st = steady.groupby(["algorithm", "order", "size", "fork"]).ns_per_sort.median().groupby(["algorithm", "order", "size"]).median()
    cmpc = pd.concat([fm_main.rename("main_forks012"), fm_st.rename("steady")], axis=1).reset_index()
    cmpc["steady_over_main"] = cmpc.steady / cmpc.main_forks012
    cmpc["differs_10pct"] = (cmpc.steady_over_main < 1 / 1.1) | (cmpc.steady_over_main > 1.1)
    cmpc.to_csv(OUT / "steady_vs_main_cells.csv", index=False, float_format="%.5g")
    big = cmpc[cmpc["size"] >= 1000]
    sm100 = cmpc[cmpc["size"] == 100]
    by = big[big.differs_10pct].groupby(["order"]).size()
    txt.append(f"steady vs main (forks 0-2): {int(big.differs_10pct.sum())} of {len(big)} cells with n >= 1000 differ by more than 10 %; "
               f"{int(sm100.differs_10pct.sum())} of {len(sm100)} cells with n = 100.\n" + by.to_string())
    pd.DataFrame([dict(n_ge_1000_cells=len(big), n_ge_1000_differ=int(big.differs_10pct.sum()), n100_cells=len(sm100), n100_differ=int(sm100.differs_10pct.sum()))]).to_csv(
        OUT / "steady_vs_main_summary.csv", index=False)

# ---------------------------------------------- 3c. did the logged activity of the assistant disturb the main run?
import re as _re
from datetime import datetime as _dt, timedelta as _td
rows_ = []
for ln in (ROOT / "results" / "full" / "run.log").read_text().splitlines():
    m_ = _re.match(r"\[(.*?)\] job (\d+)/1080 \S+ took ([\d.]+)s", ln)
    if m_:
        end = _dt.strptime(m_.group(1), "%a %b %d %H:%M:%S %Y")
        rows_.append((int(m_.group(2)) - 1, end - _td(seconds=float(m_.group(3))), end))
WINDOWS = [("01:29:50", "01:30:40"), ("01:32:50", "01:33:20"), ("01:34:00", "01:34:20"), ("01:36:30", "01:36:50"), ("01:42:30", "01:43:05")]  # approximate, from interference_log.txt
day = rows_[0][1].date()
win = [(_dt.combine(day, _dt.strptime(a, "%H:%M:%S").time()), _dt.combine(day, _dt.strptime(b, "%H:%M:%S").time())) for a, b in WINDOWS]
over = {q for q, st_, en_ in rows_ if any(st_ <= w1 and en_ >= w0 for w0, w1 in win)}
fmain = main.groupby(["algorithm", "order", "size", "fork"], as_index=False).agg(med=("ns_per_sort", "median"), seq=("seq", "first"))
fmain["rel"] = fmain.med / fmain.groupby(["algorithm", "order", "size"]).med.transform("median")
fmain["overlap"] = fmain.seq.isin(over)
ov_txt = (f"jobs overlapping the logged activity windows: {int(fmain.overlap.sum())}; median relative time {fmain[fmain.overlap].rel.median():.4f} "
          f"(other jobs {fmain[~fmain.overlap].rel.median():.4f}); windows (approximate): {WINDOWS}")
(OUT / "interference_check.txt").write_text(ov_txt + "\n")
txt.append(ov_txt)

# ---------------------------------------------- 4. trajectories
panels = [("UntilNoChange", "sorted", 1000), ("WhileNeeded", "sorted", 1000), ("UntilNoChange", "sorted", 20000), ("WhileNeeded", "sorted", 20000)]
rowsets = [("main data (10 forks)", main)] + ([("steady-state re-measurement (3 forks)", steady)] if steady is not None else [])
fig, axes = plt.subplots(len(rowsets), 4, figsize=(7.4, 2.6 * len(rowsets)), sharex=True, squeeze=False)
for r_i, (rl, df) in enumerate(rowsets):
    for c_i, (a, o, n) in enumerate(panels):
        ax = axes[r_i, c_i]
        g = df[(df.algorithm == a) & (df.order == o) & (df["size"] == n)]
        for f, gg in g.groupby("fork"):
            gg = gg.sort_values("iter")
            ax.plot(gg["iter"] + 1, gg.ns_per_sort, color=COLOR[a], alpha=0.35, lw=0.8)
        m = g.groupby("iter").ns_per_sort.median()
        ax.plot(m.index + 1, m.values, color=COLOR[a], lw=2, ls=LINESTYLE[a])
        ax.set_yscale("log")
        ax.set_ylim(150 if n == 1000 else 4000, 800 if n == 1000 else 16000)
        if r_i == 0:
            ax.set_title(f"{a}\n{o}, n = {n:,}".replace(",", " "), fontsize=7.5)
        if c_i == 0:
            ax.set_ylabel(f"{rl}\nns per sort", fontsize=7)
        if r_i == len(rowsets) - 1:
            ax.set_xlabel("timed batch number")
fig.tight_layout()
fig.savefig(OUT / "fig_level_shifts.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

(OUT / "notes.txt").write_text("\n\n".join(txt) + "\n")
print("\n\n".join(txt))
