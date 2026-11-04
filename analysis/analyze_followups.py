#!/usr/bin/env python3
"""Analysis of the follow-up experiments (see scripts/run_followups.sh).

Usage:  python analysis/analyze_followups.py
Reads results/<experiment>/raw.csv, writes tables and figures to analysis/out/followups/.
Experiments that do not exist (yet) are skipped.
"""
from common import *  # noqa: F401,F403

style()
RES = ROOT / "results"
OUT = ROOT / "analysis" / "out" / "followups"
OUT.mkdir(parents=True, exist_ok=True)
NOTES = []


def note(s):
    print(s)
    NOTES.append(s)


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def have(name):
    return (RES / name / "raw.csv").exists() and (RES / name / "raw.csv").stat().st_size > 200


def wide_of(df, extra=()):
    fm = fork_medians(df, extra)
    return fm, fm.pivot_table(index=list(extra) + ["order", "size", "fork"], columns="algorithm", values="med")


main = load_raw(RES / "full" / "raw.csv") if have("full") else None
opc = pd.read_csv(RES / "operation_counts.csv").groupby(["algorithm", "order", "size"], as_index=False)[
    ["comparisons", "inversions"]].mean() if (RES / "operation_counts.csv").exists() else None
PAIRS = [("UntilNoChange", "PassPerItem"), ("WhileNeeded", "PassPerItem"), ("WhileNeeded", "UntilNoChange")]


def ratio_table(wide, label, extra_levels=()):
    rows = []
    sel = wide.reset_index()[["order", "size"]].drop_duplicates().values.tolist()
    for o, n in sel:
        for a, b in PAIRS:
            p, g, lo, hi = paired_ratio(wide, o, n, a, b)
            rows.append(dict(setting=label, order=o, size=n, numerator=a, denominator=b, ratio=g, ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- 1. element type
if have("ext_string") and main is not None:
    s = load_raw(RES / "ext_string" / "raw.csv")
    _, w_str = wide_of(s.drop(columns="type"))
    sizes = sorted(s["size"].unique())
    forks = sorted(s.fork.unique())
    _, w_int = wide_of(main[main.fork.isin(forks) & main["size"].isin(sizes)])
    t = pd.concat([ratio_table(w_int, "Integer"), ratio_table(w_str, "String")])
    t.to_csv(OUT / "string_vs_integer_ratios.csv", index=False, float_format="%.4f")
    n_show = 5000 if 5000 in sizes else sizes[-1]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=False)
    for ax, (a, b) in zip(axes, PAIRS):
        for k, (lab, mk) in enumerate([("Integer", "o"), ("String", "D")]):
            d = t[(t.setting == lab) & (t["size"] == n_show) & (t.numerator == a) & (t.denominator == b)].set_index("order").loc[ORDERS]
            x = np.arange(len(ORDERS)) + (k - 0.5) * 0.25
            ax.errorbar(x, d.ratio, yerr=[d.ratio - d.ci_lo, d.ci_hi - d.ratio], fmt=mk, ms=4.5, lw=0.8,
                        color=[INK2, "#6250d6"][k], label=lab)
        ax.axhline(1, color=INK2, lw=0.7)
        ax.set_yscale("log")
        ax.set_xticks(range(len(ORDERS)))
        ax.set_xticklabels(["random", "sorted", "reversed", "near-local", "near-random", "few-uniq"], rotation=45, ha="right", fontsize=7)
        ax.set_title(f"{a}\n÷ {b}", fontsize=8.5)
    axes[0].set_ylabel(f"time ratio (n = {n_show:,}; < 1: numerator faster)")
    axes[0].legend(loc="lower left")
    fig.tight_layout()
    save(fig, "fig_string_vs_integer")
    note(f"string_vs_integer: n={n_show}, forks={forks}")

# ---------------------------------------------------------------- 2. JIT modes
modes = {}
if main is not None:
    m = main[main.fork < 5]
    modes["C2 (default JIT)"] = m
for name, lab in [("ext_c1", "C1 only"), ("ext_interp", "interpreter only")]:
    if have(name):
        d = load_raw(RES / name / "raw.csv").drop(columns="type")
        modes[lab] = d
if len(modes) > 1 and opc is not None:
    common_sizes = sorted(set.intersection(*[set(d["size"].unique()) for d in modes.values()]))
    rows = []
    for lab, d in modes.items():
        fm_, w = wide_of(d[d["size"].isin(common_sizes)])
        rows.append(ratio_table(w, lab))
        c = fm_.groupby(["algorithm", "order", "size"], as_index=False).med.median().merge(opc, on=["algorithm", "order", "size"])
        c["ns_per_comparison"] = c.med / c.comparisons
        c["mode"] = lab
        c.to_csv(OUT / f"cost_per_comparison_{lab.split()[0]}.csv", index=False, float_format="%.4f")
        modes[lab] = (d, c)
    jr = pd.concat(rows)
    jr.to_csv(OUT / "jit_mode_ratios.csv", index=False, float_format="%.4f")
    n_show = 2000 if 2000 in common_sizes else common_sizes[-1]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    # left: ns per comparison, random input
    ax = axes[0]
    labs = list(modes)
    for k, a in enumerate(ALGS):
        v = [modes[l][1][(modes[l][1].algorithm == a) & (modes[l][1].order == "random") & (modes[l][1]["size"] == n_show)].ns_per_comparison.iloc[0] for l in labs]
        ax.bar(np.arange(len(labs)) + (k - 1) * 0.26, v, 0.24, color=COLOR[a], label=a)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels(labs, fontsize=7.5)
    ax.set_ylabel(f"time per comparison [ns]\n(random input, n = {n_show:,})")
    ax.set_yscale("log")
    ax.legend(fontsize=7, loc="upper left")
    # right: ratio U/P and W/P per mode for random + reversed
    ax = axes[1]
    xs = 0
    ticks, tl = [], []
    for o in ["random", "reversed", "nearly_random"]:
        for l in labs:
            for k, (a, b) in enumerate(PAIRS[:2]):
                r = jr[(jr.setting == l) & (jr.order == o) & (jr["size"] == n_show) & (jr.numerator == a) & (jr.denominator == b)].iloc[0]
                ax.errorbar(xs + (k - 0.5) * 0.25, r.ratio, yerr=[[r.ratio - r.ci_lo], [r.ci_hi - r.ratio]],
                            fmt=["s", "^"][k], color=COLOR[a], ms=4.5, lw=0.8)
            ticks.append(xs); tl.append(f"{o.split('_')[0]}\n{l.split()[0]}")
            xs += 1
        xs += 0.6
    ax.axhline(1, color=INK2, lw=0.7)
    ax.set_xticks(ticks)
    ax.set_xticklabels(tl, fontsize=6, rotation=90)
    ax.set_ylabel("time ÷ PassPerItem time")
    ax.set_title("▪ UntilNoChange   ▴ WhileNeeded", fontsize=8)
    fig.tight_layout()
    save(fig, "fig_jit_modes")
    note(f"jit modes: {list(modes)} at common sizes {common_sizes}")

# ---------------------------------------------------------------- 3. scaling exponents
if have("ext_scaling"):
    sc = load_raw(RES / "ext_scaling" / "raw.csv")
    fm_ = fork_medians(sc)
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), sharey=False)
    for ax, o in zip(axes, ["random", "sorted"]):
        for a in ALGS:
            d = fm_[(fm_.algorithm == a) & (fm_.order == o) & (fm_["size"] >= 1000)]
            x, y = np.log(d["size"].values), np.log(d.med.values)
            res = stats.linregress(x, y)
            h = stats.t.ppf(0.975, len(x) - 2) * res.stderr
            rows.append(dict(order=o, algorithm=a, exponent=res.slope, ci_lo=res.slope - h, ci_hi=res.slope + h, r2=res.rvalue ** 2,
                             n_points=len(x)))
            g = fm_[(fm_.algorithm == a) & (fm_.order == o)].groupby("size").med.median() / 1e3
            ax.plot(g.index, g.values, color=COLOR[a], ls=LINESTYLE[a], marker=MARKER[a], ms=4, lw=1.4,
                    label=f"{a} (slope {res.slope:.2f})")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(ORDER_LABEL[o], fontsize=9)
        ax.set_xlabel("input size n")
        ax.legend(fontsize=7)
    axes[0].set_ylabel("median time per sort [µs]")
    fig.tight_layout()
    save(fig, "fig_scaling_fine")
    pd.DataFrame(rows).to_csv(OUT / "scaling_exponents.csv", index=False, float_format="%.4f")
    note("scaling exponents:\n" + pd.DataFrame(rows).round(3).to_string(index=False))

# ---------------------------------------------------------------- 4. replication
if have("replication") and main is not None:
    rep = load_raw(RES / "replication" / "raw.csv")
    a_ = fork_medians(main).groupby(["algorithm", "order", "size"]).med.median().rename("main")
    b_ = fork_medians(rep).groupby(["algorithm", "order", "size"]).med.median().rename("replication")
    c = pd.concat([a_, b_], axis=1).dropna()
    c["rel_diff"] = c.replication / c.main - 1
    c.to_csv(OUT / "replication_cells.csv", float_format="%.5f")
    big = c[c.index.get_level_values("size") >= 1000]
    txt = (f"cells compared: {len(c)}; |difference| < 5 %: {(c.rel_diff.abs() < .05).mean() * 100:.0f} %, < 10 %: "
           f"{(c.rel_diff.abs() < .10).mean() * 100:.0f} %; for n >= 1000: median |diff| {big.rel_diff.abs().median() * 100:.1f} %, "
           f"max |diff| {big.rel_diff.abs().max() * 100:.1f} %; Spearman rho of the cell medians "
           f"{stats.spearmanr(c.main, c.replication).statistic:.4f}")
    note("replication: " + txt)
    (OUT / "replication_summary.txt").write_text(txt + "\n")
    fig, ax = plt.subplots(figsize=(3.6, 3.4))
    for a in ALGS:
        d = c.xs(a, level="algorithm")
        ax.scatter(d.main / 1e3, d.replication / 1e3, s=14, color=COLOR[a], marker=MARKER[a], label=a, lw=0)
    lim = [c.min().min() / 1e3 * 0.7, c.max().max() / 1e3 * 1.4]
    ax.plot(lim, lim, color=INK2, lw=0.7)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("main run: median time [µs]"); ax.set_ylabel("replication: median time [µs]")
    ax.legend(loc="upper left", fontsize=7)
    save(fig, "fig_replication")

# ---------------------------------------------------------------- 5. background load
if have("ext_noload") and have("ext_load"):
    nl, ld = load_raw(RES / "ext_noload" / "raw.csv"), load_raw(RES / "ext_load" / "raw.csv")
    f0, f1 = fork_medians(nl), fork_medians(ld)
    keys = ["algorithm", "order", "size"]
    g0 = f0.groupby(keys).med.agg(["median", lambda x: x.std(ddof=1) / x.mean()]).set_axis(["median_idle", "cv_idle"], axis=1)
    g1 = f1.groupby(keys).med.agg(["median", lambda x: x.std(ddof=1) / x.mean()]).set_axis(["median_load", "cv_load"], axis=1)
    c = g0.join(g1)
    c["slowdown"] = c.median_load / c.median_idle
    c.to_csv(OUT / "load_effect.csv", float_format="%.5f")
    # also the spread of single batches (not only of fork medians)
    sp = []
    for lab, d in [("idle", nl), ("load", ld)]:
        q = d.groupby(keys).ns_per_sort.agg(lambda x: np.percentile(x, 75) - np.percentile(x, 25))
        med = d.groupby(keys).ns_per_sort.median()
        sp.append((q / med).rename(f"rel_iqr_{lab}"))
    c = c.join(pd.concat(sp, axis=1))
    c.to_csv(OUT / "load_effect.csv", float_format="%.5f")
    txt = (f"median slowdown under load: {c.slowdown.median():.3f} (range {c.slowdown.min():.3f}-{c.slowdown.max():.3f}); "
           f"median CV between forks idle {c.cv_idle.median() * 100:.1f} % vs load {c.cv_load.median() * 100:.1f} %; "
           f"median relative IQR of batches idle {c.rel_iqr_idle.median() * 100:.1f} % vs load {c.rel_iqr_load.median() * 100:.1f} %")
    note("load: " + txt)
    (OUT / "load_summary.txt").write_text(txt + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))
    d = c.reset_index()
    d = d[d["size"] == 5000]
    for ax, col_i, col_l, yl in [(axes[0], "median_idle", "median_load", "median time per sort [ms]"),
                                 (axes[1], "cv_idle", "cv_load", "variation between forks (CV) [%]")]:
        sc_ = 1e6 if col_i.startswith("median") else 1 / 100
        xs = np.arange(len(d))
        ax.bar(xs - 0.2, d[col_i] / sc_, 0.38, color="#9a9992", label="idle machine")
        ax.bar(xs + 0.2, d[col_l] / sc_, 0.38, color="#6250d6", label="6 busy background processes")
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{a[:4]}.\n{o.split('_')[0]}" for a, o in zip(d.algorithm, d.order)], fontsize=6)
        ax.set_ylabel(yl)
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig_load")

(OUT / "notes.txt").write_text("\n\n".join(NOTES) + "\n")
print("follow-up analysis finished ->", OUT)
