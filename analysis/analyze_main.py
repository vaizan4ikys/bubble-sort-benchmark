#!/usr/bin/env python3
"""Analysis of the main experiment: tables, hypothesis checks and figures.

Usage:  python analysis/analyze_main.py [RAW_DIR] [OUT_DIR]
        (defaults: results/full  analysis/out/main)

Everything in the report (tables, numbers, plots) is regenerated from raw.csv by this script.
"""
import sys

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Rectangle

from common import *  # noqa: F401,F403

style()
RAW = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "results/full")
OUT = ROOT / (sys.argv[2] if len(sys.argv) > 2 else "analysis/out/main")
OUT.mkdir(parents=True, exist_ok=True)

df = load_raw(RAW / "raw.csv")
fm = fork_medians(df)
wide = fm.pivot_table(index=["order", "size", "fork"], columns="algorithm", values="med")
SIZES = sorted(df["size"].unique())
N_FORKS = df.fork.nunique()
ORD = [o for o in ORDERS if o in set(df.order)]

# ------------------------------------------------------------------ data quality
lines = [
    f"rows (batch measurements): {len(df)}",
    f"cells (algorithm x order x size): {df.groupby(['algorithm', 'order', 'size']).ngroups}",
    f"forks per cell: {sorted(df.groupby(['algorithm', 'order', 'size']).fork.nunique().unique())}",
    f"measured batches per fork: {sorted(df.groupby(['algorithm', 'order', 'size', 'fork']).size().unique())}",
    f"batches with a GC during the timed region: {int(df.gc_during.sum())} ({df.gc_during.mean() * 100:.2f} %)",
    f"forks whose warm-up hit the time limit: {int(df.groupby(['algorithm', 'order', 'size', 'fork']).warmup_timeout.max().sum())}",
    f"smallest batch size: {int(df.batch.min())}, largest: {int(df.batch.max())}",
    f"shortest measured time per sort: {df.ns_per_sort.min():.1f} ns; longest: {fmt_time(df.ns_per_sort.max())}",
]
(OUT / "data_quality.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))

# --------------------------------------------------------- per-cell summary table
rows = []
for (a, o, n), g in df.groupby(["algorithm", "order", "size"]):
    q = five_number(g.ns_per_sort)
    f = fm[(fm.algorithm == a) & (fm.order == o) & (fm["size"] == n)]
    m, lo, hi = t_ci(f.med)
    rows.append(dict(algorithm=a, order=o, size=n, n_obs=len(g), n_forks=len(f), min=q[0], q1=q[1], median=q[2],
                     q3=q[3], max=q[4], mean=g.ns_per_sort.mean(), sd=g.ns_per_sort.std(ddof=1),
                     median_of_fork_medians=f.med.median(), mean_fork_median=m, ci95_lo=lo, ci95_hi=hi,
                     cv_between_forks=f.med.std(ddof=1) / f.med.mean() if len(f) > 1 else math.nan))
summ = pd.DataFrame(rows)
summ["algorithm"] = pd.Categorical(summ.algorithm, ALGS)
summ["order"] = pd.Categorical(summ.order, ORD)
summ = summ.sort_values(["order", "size", "algorithm"]).reset_index(drop=True)
summ.to_csv(OUT / "summary_cells.csv", index=False, float_format="%.3f")

# Human-readable five-number tables (one markdown block per order) for the report appendix.
with open(OUT / "five_number_tables.md", "w") as fh:
    for o in ORD:
        fh.write(f"### {ORDER_LABEL[o]}\n\n| n | algorithm | min | Q1 | median | Q3 | max |\n|---|---|---|---|---|---|---|\n")
        for _, r in summ[summ.order == o].iterrows():
            fh.write(f"| {r['size']} | {r.algorithm} | " + " | ".join(fmt_time(r[c]) for c in ["min", "q1", "median", "q3", "max"]) + " |\n")
        fh.write("\n")

# ------------------------------------------------------------- hypothesis checks
hyp_rows = []


def add(h, desc, order, size, est, lo, hi, thr, verdict):
    hyp_rows.append(dict(hypothesis=h, claim=desc, order=order, size=size, estimate=est, ci_lo=lo, ci_hi=hi,
                         threshold=thr, verdict=verdict))


def judge_ge(lo, hi, thr):  # claim: value >= thr
    return "supported" if lo >= thr else ("falsified" if hi < thr else "inconclusive")


def judge_le(lo, hi, thr):  # claim: value <= thr
    return "supported" if hi <= thr else ("falsified" if lo > thr else "inconclusive")


def judge_in(lo, hi, a, b):  # claim: a <= value <= b
    return "supported" if (lo >= a and hi <= b) else ("falsified" if (hi < a or lo > b) else "inconclusive")


def ratio(o, n, a, b):
    p, g, lo, hi = paired_ratio(wide, o, n, a, b)
    return g, lo, hi


if "sorted" in ORD:
    for n in [s for s in SIZES if s >= 1000]:
        for other in ["UntilNoChange", "WhileNeeded"]:
            g, lo, hi = ratio("sorted", n, "PassPerItem", other)
            add("H1", f"PassPerItem / {other} >= 100", "sorted", n, g, lo, hi, 100, judge_ge(lo, hi, 100))
for n in [s for s in SIZES if s >= 5000]:
    if "random" in ORD:
        for other in ["UntilNoChange", "PassPerItem"]:
            g, lo, hi = ratio("random", n, "WhileNeeded", other)
            add("H2", f"WhileNeeded / {other} < 1", "random", n, g, lo, hi, 1, judge_le(lo, hi, 1.0))
        g, lo, hi = ratio("random", n, "UntilNoChange", "PassPerItem")
        add("H2", "UntilNoChange / PassPerItem within 0.85-1.15", "random", n, g, lo, hi, "0.85-1.15", judge_in(lo, hi, 0.85, 1.15))
    if "reversed" in ORD:
        for other in ["UntilNoChange", "PassPerItem"]:
            g, lo, hi = ratio("reversed", n, "WhileNeeded", other)
            add("H3", f"WhileNeeded / {other} <= 0.90", "reversed", n, g, lo, hi, 0.9, judge_le(lo, hi, 0.9))
    if "nearly_local" in ORD:
        for other in ["UntilNoChange", "WhileNeeded"]:
            g, lo, hi = ratio("nearly_local", n, "PassPerItem", other)
            add("H4", f"PassPerItem / {other} >= 10", "nearly_local", n, g, lo, hi, 10, judge_ge(lo, hi, 10))
if {10000, 20000} <= set(SIZES):
    for alg in ALGS:
        if "random" in ORD:
            g, lo, hi = growth_factor(fm, "random", alg, 10000, 20000)
            add("H5", f"{alg}: t(20000)/t(10000) within 3.3-4.7", "random", 20000, g, lo, hi, "3.3-4.7", judge_in(lo, hi, 3.3, 4.7))
        if "sorted" in ORD:
            g, lo, hi = growth_factor(fm, "sorted", alg, 10000, 20000)
            if alg == "PassPerItem":
                add("H5", f"{alg}: t(20000)/t(10000) within 3.3-4.7", "sorted", 20000, g, lo, hi, "3.3-4.7", judge_in(lo, hi, 3.3, 4.7))
            else:
                add("H5", f"{alg}: t(20000)/t(10000) < 2.6", "sorted", 20000, g, lo, hi, 2.6, judge_le(lo, hi, 2.6))
for o in ORD:
    for n in [s for s in SIZES if s >= 1000]:
        for other in ["UntilNoChange", "PassPerItem"]:
            g, lo, hi = ratio(o, n, "WhileNeeded", other)
            add("H6", f"WhileNeeded / {other} <= 1.05", o, n, g, lo, hi, 1.05, judge_le(lo, hi, 1.05))
hyp = pd.DataFrame(hyp_rows)
hyp.to_csv(OUT / "hypothesis_cells.csv", index=False, float_format="%.4f")

overall = []
for h, g in hyp.groupby("hypothesis"):
    c = g.verdict.value_counts().to_dict()
    if c.get("falsified", 0) == 0 and c.get("inconclusive", 0) == 0:
        v = "SUPPORTED"
    elif c.get("falsified", 0) == len(g):
        v = "FALSIFIED"
    elif c.get("falsified", 0) > 0:
        v = "PARTLY FALSIFIED"
    else:
        v = "INCONCLUSIVE"
    overall.append(dict(hypothesis=h, verdict=v, supported=c.get("supported", 0), falsified=c.get("falsified", 0),
                        inconclusive=c.get("inconclusive", 0), cells=len(g)))
overall = pd.DataFrame(overall)
overall.to_csv(OUT / "hypothesis_overall.csv", index=False)
print(overall.to_string(index=False))

# ------------------------------------------------------ pairwise ratio matrix
ratio_rows = []
for o in ORD:
    for n in SIZES:
        for a, b in [("UntilNoChange", "PassPerItem"), ("WhileNeeded", "PassPerItem"), ("WhileNeeded", "UntilNoChange")]:
            p, g, lo, hi = paired_ratio(wide, o, n, a, b)
            ratio_rows.append(dict(order=o, size=n, numerator=a, denominator=b, ratio_mean=g, ci_lo=lo, ci_hi=hi,
                                   ratio_of_medians=p))
ratios = pd.DataFrame(ratio_rows)
ratios.to_csv(OUT / "pairwise_ratios.csv", index=False, float_format="%.6g")

# winner table: fastest algorithm per cell and by how much it beats the second-fastest
win_rows = []
for o in ORD:
    for n in SIZES:
        s = summ[(summ.order == o) & (summ["size"] == n)].set_index("algorithm").median_of_fork_medians.sort_values()
        win_rows.append(dict(order=o, size=n, fastest=s.index[0], second=s.index[1], advantage_vs_second=s.iloc[1] / s.iloc[0],
                             slowest=s.index[2], advantage_vs_slowest=s.iloc[2] / s.iloc[0]))
pd.DataFrame(win_rows).to_csv(OUT / "winners.csv", index=False, float_format="%.3f")

# ------------------------------------------------------ mechanism: operation counts
opc_path = ROOT / "results" / "operation_counts.csv"
if opc_path.exists():
    opc = pd.read_csv(opc_path)
    opc = opc.groupby(["algorithm", "order", "size"], as_index=False)[["comparisons", "inversions"]].mean()
    m = summ.merge(opc, on=["algorithm", "order", "size"])
    m["ns_per_comparison"] = m.median_of_fork_medians / m.comparisons
    m.to_csv(OUT / "cells_with_operation_counts.csv", index=False, float_format="%.4f")
    reg = []
    for a in ALGS:
        d = m[(m.algorithm == a) & (m["size"] >= 1000)]
        X = d[["comparisons", "inversions"]].values
        y = d.median_of_fork_medians.values
        w = 1.0 / y  # relative-error weighting
        coef, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)
        pred = X @ coef
        r2 = 1 - ((y - pred) ** 2 * w ** 2).sum() / (((y - np.average(y, weights=w ** 2)) ** 2) * w ** 2).sum()
        reg.append(dict(algorithm=a, ns_per_comparison=coef[0], ns_per_swap=coef[1], weighted_r2=r2, cells=len(d)))
    pd.DataFrame(reg).to_csv(OUT / "cost_model.csv", index=False, float_format="%.4f")
    print(pd.DataFrame(reg).to_string(index=False))

# ======================================================================= FIGURES
US = 1e3  # ns -> µs


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---- Figure 1: design diagram -------------------------------------------------------
def design_figure():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.set_xlim(-1.6, 13.2)
    ax.set_ylim(-1.7, 8.9)
    ax.axis("off")
    ax.grid(False)
    sizes = [100, 1000, 2000, 5000, 10000, 20000]
    ax.text(5.6, 8.35, "Input size n (6 levels)", ha="center", fontsize=9.5, fontweight="bold")
    ax.text(-1.3, 3.9, "Input order (6 levels)", ha="center", va="center", fontsize=9.5, fontweight="bold", rotation=90)
    for j, n in enumerate(sizes):
        ax.text(1.6 + j * 1.75 + 0.8, 7.7, f"{n:,}", ha="center", fontsize=8.5)
    short = {"random": "random", "sorted": "sorted", "reversed": "reversed", "nearly_local": "nearly sorted,\nlocal",
             "nearly_random": "nearly sorted,\nrandom", "few_unique": "few unique"}
    for i, o in enumerate(ORDERS):
        y = 6.6 - i * 1.15
        ax.text(1.35, y + 0.4, short[o], ha="right", va="center", fontsize=7.8)
        for j in range(6):
            x = 1.6 + j * 1.75
            ax.add_patch(FancyBboxPatch((x, y), 1.6, 0.8, boxstyle="round,pad=0.02,rounding_size=0.08",
                                        fc="#f4f3ef", ec=INK2, lw=0.6))
            for k, a in enumerate(ALGS):
                ax.add_patch(Rectangle((x + 0.14 + k * 0.5, y + 0.2), 0.4, 0.4, fc=COLOR[a], ec="white", lw=0.8))
    # legend for the repeated-measures factor
    for k, a in enumerate(ALGS):
        ax.add_patch(Rectangle((1.6 + k * 3.7, -0.35), 0.4, 0.4, fc=COLOR[a], ec="white"))
        ax.text(2.15 + k * 3.7, -0.15, a, va="center", fontsize=8.5)
    ax.text(5.6, -1.0, "Algorithm (3 levels): every cell is measured with all three algorithms on the SAME input data",
            ha="center", fontsize=8.3, color=INK2)
    ax.text(5.6, -1.5, "Each of the 3 x 6 x 6 = 108 cells: 10 forks (fresh JVM, own input data) x 30 timed batches",
            ha="center", fontsize=8.3, color=INK2)
    ax.set_title("Full-factorial, repeated-measures design", fontsize=10, loc="center", pad=2)
    save(fig, "fig_design")


design_figure()

# ---- Figure 2: box plots per input order ----------------------------------------------
def boxplots():
    ncol = 3
    nrow = math.ceil(len(ORD) / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(7.0, 2.6 * nrow), sharey=True)
    axes = np.atleast_1d(axes).ravel()
    for ax, o in zip(axes, ORD):
        for k, a in enumerate(ALGS):
            data = [df[(df.algorithm == a) & (df.order == o) & (df["size"] == n)].ns_per_sort.values / US for n in SIZES]
            pos = np.arange(len(SIZES)) + (k - 1) * 0.27
            bp = ax.boxplot(data, positions=pos, widths=0.23, patch_artist=True, showfliers=True,
                            flierprops=dict(marker=".", markersize=2, markeredgecolor=COLOR[a], alpha=0.5),
                            medianprops=dict(color="white", lw=1.2), whiskerprops=dict(color=COLOR[a], lw=0.8),
                            capprops=dict(color=COLOR[a], lw=0.8), boxprops=dict(edgecolor=COLOR[a], lw=0.8))
            for b in bp["boxes"]:
                b.set_facecolor(COLOR[a])
        ax.set_yscale("log")
        ax.set_xticks(range(len(SIZES)))
        ax.set_xticklabels([f"{n // 1000}k" if n >= 1000 else str(n) for n in SIZES])
        ax.set_title(ORDER_LABEL[o], fontsize=8.8)
        ax.set_xlabel("input size n")
    for ax in axes[::ncol]:
        ax.set_ylabel("time per sort [µs, log scale]")
    for ax in axes[len(ORD):]:
        ax.axis("off")
    handles = [Rectangle((0, 0), 1, 1, fc=COLOR[a]) for a in ALGS]
    fig.legend(handles, ALGS, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "fig_boxplots")


boxplots()

# ---- Figure 3: scaling (log-log) ---------------------------------------------------------
def scaling():
    ncol = 3
    nrow = math.ceil(len(ORD) / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(7.0, 2.6 * nrow), sharex=True, sharey=True)
    axes = np.atleast_1d(axes).ravel()
    for ax, o in zip(axes, ORD):
        for a in ALGS:
            xs, ys, lo, hi = [], [], [], []
            for n in SIZES:
                f = fm[(fm.algorithm == a) & (fm.order == o) & (fm["size"] == n)].med.values / US
                m, l, h = t_ci(f)
                xs.append(n); ys.append(np.median(f)); lo.append(max(l, 1e-4)); hi.append(h)
            ax.plot(xs, ys, color=COLOR[a], ls=LINESTYLE[a], marker=MARKER[a], ms=4, lw=1.4, label=a)
            ax.fill_between(xs, lo, hi, color=COLOR[a], alpha=0.18, lw=0)
        # reference slopes anchored at the left of the PassPerItem line
        x0 = SIZES[0]
        y0 = fm[(fm.algorithm == "PassPerItem") & (fm.order == o) & (fm["size"] == x0)].med.median() / US * 0.25
        xs = np.array([x0, SIZES[-1]], dtype=float)
        ax.plot(xs, y0 * (xs / x0) ** 2, color=INK2, lw=0.7, ls=(0, (1, 3)))
        ax.plot(xs, y0 * (xs / x0) ** 1, color=INK2, lw=0.7, ls=(0, (1, 3)))
        ax.text(xs[-1], y0 * (xs[-1] / x0) ** 2 * 0.55, "n²", color=INK2, fontsize=7, ha="right")
        ax.text(xs[-1], y0 * (xs[-1] / x0) * 1.35, "n", color=INK2, fontsize=7, ha="right")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(ORDER_LABEL[o], fontsize=8.8)
        ax.set_xlabel("input size n")
        ax.tick_params(axis="x", labelbottom=True)  # tick labels on every panel, not only on the bottom row
    for ax in axes[::ncol]:
        ax.set_ylabel("median time per sort [µs]")
    for ax in axes[len(ORD):]:
        ax.axis("off")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "fig_scaling")


scaling()

# ---- Figure 4: ratio heat maps ---------------------------------------------------------------
def heatmaps():
    cmap = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#e9e8e4", "#eb6834"])
    pairs = [("UntilNoChange", "PassPerItem"), ("WhileNeeded", "PassPerItem"), ("WhileNeeded", "UntilNoChange")]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.9), sharey=True)
    for ax, (a, b) in zip(axes, pairs):
        M = np.array([[ratios[(ratios.order == o) & (ratios["size"] == n) & (ratios.numerator == a) &
                              (ratios.denominator == b)].ratio_mean.iloc[0] for n in SIZES] for o in ORD])
        lim = max(np.log10(M.max()), -np.log10(M.min()), 0.3)
        ax.imshow(np.log10(M), cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax.text(j, i, fmt_ratio(M[i, j]), ha="center", va="center", fontsize=6.5, color=INK)
        ax.set_xticks(range(len(SIZES)))
        ax.set_xticklabels([f"{n // 1000}k" if n >= 1000 else str(n) for n in SIZES])
        ax.set_yticks(range(len(ORD)))
        ax.set_yticklabels([ORDER_LABEL[o].replace(" (", "\n(") if False else ORDER_LABEL[o] for o in ORD], fontsize=7)
        ax.set_title(f"{a}\n÷ {b}", fontsize=8.5)
        ax.set_xlabel("input size n")
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.tight_layout()
    save(fig, "fig_ratio_heatmaps")


heatmaps()

# ---- Figure 5: ECDF of the timed batches for three representative cells ---------------------------
def ecdfs():
    cells = [(o, 10000) for o in ["random", "reversed", "nearly_random"] if o in ORD and 10000 in SIZES]
    if not cells:
        cells = [(ORD[0], SIZES[-1])]
    fig, axes = plt.subplots(1, len(cells), figsize=(7.0, 2.5), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, (o, n) in zip(axes, cells):
        for a in ALGS:
            v = np.sort(df[(df.algorithm == a) & (df.order == o) & (df["size"] == n)].ns_per_sort.values / 1e6)
            ax.step(v, np.arange(1, len(v) + 1) / len(v), where="post", color=COLOR[a], ls=LINESTYLE[a], lw=1.5, label=a)
        ax.set_title(f"{ORDER_LABEL[o]}, n = {n:,}", fontsize=8.8)
        ax.set_xlabel("time per sort [ms]")
    axes[0].set_ylabel("cumulative proportion of batches")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.07))
    fig.tight_layout()
    save(fig, "fig_ecdf")


ecdfs()

# ---- Figure 6: drift check (time vs. position in the randomized job order) -----------------------------
def drift():
    f = fm.copy()
    cellmed = f.groupby(["algorithm", "order", "size"]).med.transform("median")
    f["rel"] = f.med / cellmed
    f = f[f["size"] >= 1000].sort_values("seq")
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    ax.scatter(f.seq, f.rel, s=3, color=INK2, alpha=0.25, lw=0)
    roll = f.set_index("seq").rel.rolling(60, min_periods=20).median()
    ax.plot(roll.index, roll.values, color=COLOR["UntilNoChange"], lw=1.6)
    ax.axhline(1, color=INK2, lw=0.6)
    ax.set_ylim(0.8, 1.25)
    ax.set_xlabel("position of the fork in the randomized job order")
    ax.set_ylabel("fork median ÷ cell median")
    ax.set_title("Drift check: relative time of every fork (dots) and rolling median of 60 forks (line)", fontsize=8.5)
    save(fig, "fig_drift")
    ordered = f.sort_values("seq").rel.values
    third = len(ordered) // 3
    (OUT / "drift.txt").write_text(f"median relative time in the first third of the session: {np.median(ordered[:third]):.4f}, in the last third: {np.median(ordered[-third:]):.4f}\n"
                                   f"rolling-median range: {roll.min():.3f} .. {roll.max():.3f}\n")


drift()

# ---- Figure 7: comparisons per n^2 (mechanism) --------------------------------------------------------
if opc_path.exists():
    def counts_fig():
        d = m[m["size"] == 10000] if 10000 in SIZES else m[m["size"] == SIZES[-1]]
        nn = d["size"].iloc[0]
        fig, ax = plt.subplots(figsize=(6.8, 2.8))
        w = 0.26
        for k, a in enumerate(ALGS):
            v = [d[(d.algorithm == a) & (d.order == o)].comparisons.iloc[0] / nn ** 2 for o in ORD]
            ax.bar(np.arange(len(ORD)) + (k - 1) * w, v, w * 0.9, color=COLOR[a], label=a)
        inv = [d[(d.algorithm == "PassPerItem") & (d.order == o)].inversions.iloc[0] / nn ** 2 for o in ORD]
        ax.plot(np.arange(len(ORD)), inv, color=INK, marker="D", ms=4, lw=0, label="swaps (= inversions)")
        ax.set_xticks(range(len(ORD)))
        ax.set_xticklabels([ORDER_LABEL[o].replace(" (", "\n(") for o in ORD], fontsize=7)
        ax.set_ylabel(f"operations ÷ n²  (n = {nn:,})")
        ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.2))
        save(fig, "fig_operations")

    counts_fig()

print("analysis finished ->", OUT)
