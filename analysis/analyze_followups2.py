#!/usr/bin/env python3
"""Analysis of the second queue of follow-up experiments (see scripts/run_followups2.sh):
other garbage collectors and JDK versions, tiny arrays, other input shapes, polluted JIT profile,
cold start, JMH cross-check and correctness tests.

Usage:  python analysis/analyze_followups2.py
Reads results/<experiment>/raw.csv; writes tables/figures to analysis/out/followups2/.
Experiments that do not exist (yet) are skipped.
"""
import json
import os
import re

from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from common import *  # noqa: F401,F403

style()
RES = Path(os.environ.get("EXP_RESULTS", ROOT / "results"))
OUT = Path(os.environ.get("EXP_OUT", ROOT / "analysis" / "out" / "followups2"))
OUT.mkdir(parents=True, exist_ok=True)
NOTES = []
PAIRS = [("UntilNoChange", "PassPerItem"), ("WhileNeeded", "PassPerItem"), ("WhileNeeded", "UntilNoChange")]
SHORT = {"random": "random", "sorted": "sorted", "reversed": "reversed", "nearly_local": "near-local",
         "nearly_random": "near-random", "few_unique": "few-unique", "turtle": "turtle", "rabbit": "rabbit",
         "sorted_tail": "sorted+tail", "organ_pipe": "organ pipe", "sawtooth": "sawtooth"}
CMAP = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f1f0ec", "#eb6834"])


def note(s):
    print(s)
    NOTES.append(s)


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def have(name):
    f = RES / name / "raw.csv"
    return f.exists() and f.stat().st_size > 200


def load(name):
    d = pd.read_csv(RES / name / "raw.csv")
    return d.drop(columns=[c for c in ("type",) if c in d.columns])


def wide_of(df):
    fm = fork_medians(df)
    return fm, fm.pivot_table(index=["order", "size", "fork"], columns="algorithm", values="med")


def ratios(wide, label):
    rows = []
    for o, n in wide.reset_index()[["order", "size"]].drop_duplicates().values.tolist():
        for a, b in PAIRS:
            _, g, lo, hi = paired_ratio(wide, o, n, a, b)
            rows.append(dict(setting=label, order=o, size=int(n), numerator=a, denominator=b, ratio=g, ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(rows)


def cell_medians(fm):
    return fm.groupby(["algorithm", "order", "size"]).med.median().unstack("algorithm")


def regret_stats(fm, label):
    m = cell_medians(fm)
    m = m[m.index.get_level_values("size") >= 1000]
    reg = m.div(m.min(axis=1), axis=0)
    rows = []
    for a in ALGS:
        rows.append(dict(setting=label, algorithm=a, cells=len(reg), fastest=int((reg[a] <= 1 + 1e-12).sum()),
                         within5=int((reg[a] <= 1.05).sum()), geomean_regret=float(np.exp(np.log(reg[a]).mean())),
                         max_regret=float(reg[a].max()), max_where="{} n={}".format(*reg[a].idxmax())))
    return pd.DataFrame(rows)


def heat(ax, mat, rows, cols, title, fmt_cols=None):
    arr = mat.loc[rows, cols].values.astype(float)
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    norm = TwoSlopeNorm(vcenter=1.0, vmin=min(lo, 0.95) if lo < 1 else 0.5, vmax=max(hi, 1.05) if hi > 1 else 2.0)
    ax.imshow(np.clip(arr, norm.vmin, norm.vmax), cmap=CMAP, norm=norm, aspect="auto")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            ax.text(j, i, "-" if np.isnan(v) else fmt_ratio(v), ha="center", va="center", fontsize=6.5, color=INK)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([SHORT.get(c, c) for c in cols], rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=7)
    ax.set_title(title, fontsize=8.5)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)


# ================================================================== 1. other GC / JDK / polluted JIT
main = load("full") if have("full") else None
variants = {}
if main is not None:
    sel = main[(main.fork < 5) & main["size"].isin([1000, 5000, 10000])]
    variants["main: JDK 26, SerialGC"] = sel
for name, label in [("ext_g1", "JDK 26, G1 GC"), ("ext_parallel", "JDK 26, ParallelGC"),
                    ("ext_jdk25", "JDK 26 (repeat run)"), ("ext_jdk25_real", "JDK 25 (this Mac)"),
                    ("ext_jdk21", "JDK 21"), ("ext_jdk17", "JDK 17"), ("ext_jdk8", "JDK 8"),
                    ("ext_polluted", "JDK 26, polluted JIT profile"),
                    ("portable_vlad-laptop", "2nd M3 Pro, JDK 25.0.1"),
                    ("portable_at3eus-pc-jdk26-2", "Ryzen 5 5600 (x86), JDK 26")]:
    if have(name):
        d = load(name)
        if name == "ext_polluted":
            d = d[d["size"].isin([1000, 5000])]
        variants[label] = d

if len(variants) > 1:
    all_ratios, all_regret, fms = [], [], {}
    for label, d in variants.items():
        fm, w = wide_of(d)
        fms[label] = fm
        all_ratios.append(ratios(w, label))
        all_regret.append(regret_stats(fm, label))
    R = pd.concat(all_ratios)
    R.to_csv(OUT / "variant_ratios.csv", index=False, float_format="%.4f")
    G = pd.concat(all_regret)
    G.to_csv(OUT / "variant_regret.csv", index=False, float_format="%.4f")
    note("variant regret summary:\n" + G.round(3).to_string(index=False))

    # absolute speed relative to the main setting (same fork ids, same data)
    base = fms["main: JDK 26, SerialGC"]
    rows = []
    for label, fm in fms.items():
        if label.startswith("main") or "2nd M3" in label or "Ryzen" in label:
            continue  # other machines: absolute speed is not comparable
        m1 = cell_medians(base)
        m2 = cell_medians(fm)
        idx = m1.index.intersection(m2.index)
        rel = (m2.loc[idx] / m1.loc[idx])
        for a in ALGS:
            r = rel[a]
            rows.append(dict(setting=label, algorithm=a, geomean_time_vs_main=float(np.exp(np.log(r).mean())),
                             min=float(r.min()), max=float(r.max())))
    A = pd.DataFrame(rows)
    A.to_csv(OUT / "variant_absolute_speed.csv", index=False, float_format="%.4f")
    note("absolute speed vs main setting:\n" + A.round(3).to_string(index=False))

    # figure: heat maps (variant x order) at n = 5000, one panel per pair
    labels = list(variants)
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 3.0), sharey=True)
    for ax, (a, b) in zip(axes, PAIRS):
        mat = R[(R["size"] == 5000) & (R.numerator == a) & (R.denominator == b)].pivot(index="setting", columns="order", values="ratio")
        heat(ax, mat, labels, [o for o in ORDERS if o in mat.columns], f"{a}\n÷ {b}")
    fig.tight_layout()
    save(fig, "fig_variants_ratio_n5000")

    # figure: WhileNeeded slowdown vs best, per variant (n >= 1000)
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    for k, a in enumerate(ALGS):
        y = [G[(G.setting == l) & (G.algorithm == a)].max_regret.iloc[0] for l in labels]
        ax.plot(np.arange(len(labels)) + (k - 1) * 0.18, y, MARKER[a], color=COLOR[a], label=a, ms=6,
                markeredgecolor="white", markeredgewidth=1)
    ax.set_yscale("log")
    ax.axhline(1, color=INK2, lw=0.7)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([l.replace(", ", ",\n").replace("main: ", "main:\n") for l in labels], fontsize=6.5)
    ax.set_ylabel("worst slowdown vs best\n(over orders and sizes)")
    ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, 1.15))
    fig.tight_layout()
    save(fig, "fig_variants_regret")

# ================================================================== 2. tiny arrays
if have("ext_small"):
    d = load("ext_small")
    fm, w = wide_of(d)
    S = ratios(w, "small")
    S.to_csv(OUT / "small_ratios.csv", index=False, float_format="%.4f")
    meds = cell_medians(fm)
    meds.to_csv(OUT / "small_medians_ns.csv", float_format="%.2f")
    orders = [o for o in ORDERS + ["turtle", "rabbit"] if o in set(d.order)]
    fig, axes = plt.subplots(2, 4, figsize=(7.4, 3.8), sharex=True)
    for ax, o in zip(axes.flat, orders):
        for (a, b), ls in zip(PAIRS[:2], ["--", ":"]):
            x = S[(S.order == o) & (S.numerator == a) & (S.denominator == b)].sort_values("size")
            ax.plot(x["size"], x.ratio, marker=MARKER[a], ms=3.5, lw=1.2, color=COLOR[a], ls=LINESTYLE[a], label=f"{a} ÷ PassPerItem")
            ax.fill_between(x["size"], x.ci_lo, x.ci_hi, color=COLOR[a], alpha=0.15, lw=0)
        ax.axhline(1, color=INK2, lw=0.6)
        ax.set_xscale("log")
        ax.set_xticks([2, 5, 10, 20, 50])
        ax.set_xticklabels(["2", "5", "10", "20", "50"])
        ax.minorticks_off()
        ax.set_title(SHORT[o], fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("input size n")
    for ax in axes[:, 0]:
        ax.set_ylabel("time ratio")
    axes[0, 0].legend(fontsize=6, loc="upper left")
    fig.tight_layout()
    save(fig, "fig_small")
    win = []
    for (o, n), g in meds.iterrows():
        win.append(dict(order=o, size=n, fastest=g.idxmin(), advantage_vs_second=sorted(g)[1] / g.min()))
    pd.DataFrame(win).to_csv(OUT / "small_winners.csv", index=False, float_format="%.3f")
    note("small arrays: wrote small_ratios.csv, small_winners.csv, fig_small")

# ================================================================== 3. other input shapes
if have("ext_shapes"):
    d = load("ext_shapes")
    fm, w = wide_of(d)
    Sh = ratios(w, "shapes")
    Sh.to_csv(OUT / "shapes_ratios.csv", index=False, float_format="%.4f")
    meds = cell_medians(fm)
    meds.to_csv(OUT / "shapes_medians_ns.csv", float_format="%.1f")
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6), sharey=True)
    cols = [o for o in ["turtle", "rabbit", "sorted_tail", "organ_pipe", "sawtooth"] if o in set(d.order)]
    for ax, (a, b) in zip(axes, PAIRS):
        mat = Sh[(Sh.numerator == a) & (Sh.denominator == b)].assign(sz=lambda x: x["size"].map(lambda v: f"n = {v:,}")).pivot(
            index="sz", columns="order", values="ratio")
        heat(ax, mat, sorted(mat.index, key=lambda s: int(s[4:].replace(",", ""))), cols, f"{a}\n÷ {b}")
    fig.tight_layout()
    save(fig, "fig_shapes")
    rg = regret_stats(fm, "shapes")
    rg.to_csv(OUT / "shapes_regret.csv", index=False, float_format="%.4f")
    note("shapes: " + rg.round(3).to_string(index=False))

# ================================================================== 4. cold start
if have("ext_cold"):
    c = pd.read_csv(RES / "ext_cold" / "raw.csv")
    rows = []
    for (a, o, n), g in c.groupby(["algorithm", "order", "size"]):
        pivot = g.pivot_table(index="fork", columns="call", values="ns")
        full = pivot.dropna(axis=1, thresh=int(0.9 * len(pivot)))
        for k in (1, 5, 20):
            if full.shape[1] >= k:
                tot = full.iloc[:, :k].sum(axis=1)
                rows.append(dict(algorithm=a, order=o, size=n, calls=k, median_total_ns=float(tot.median()),
                                 q1=float(tot.quantile(.25)), q3=float(tot.quantile(.75))))
    C = pd.DataFrame(rows)
    C.to_csv(OUT / "cold_cumulative.csv", index=False, float_format="%.1f")
    rr = []
    for (o, n, k), g in C.groupby(["order", "size", "calls"]):
        t = g.set_index("algorithm").median_total_ns
        rr.append(dict(order=o, size=n, calls=k, **{f"{a[:1]}_vs_P": t[a] / t["PassPerItem"] for a in ("UntilNoChange", "WhileNeeded")},
                       fastest=t.idxmin()))
    pd.DataFrame(rr).to_csv(OUT / "cold_ratios.csv", index=False, float_format="%.3f")
    # time per call index (median over forks), random input
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.7), sharey=False)
    for ax, n in zip(axes, [100, 1000, 10000]):
        for a in ALGS:
            g = c[(c.algorithm == a) & (c.order == "random") & (c["size"] == n)]
            m = g.groupby("call").ns.median() / 1e3
            cnt = g.groupby("call").fork.nunique()
            m = m[cnt >= 0.5 * g.fork.nunique()]
            ax.plot(m.index + 1, m.values, color=COLOR[a], ls=LINESTYLE[a], marker=MARKER[a], ms=2.8, lw=1.1, label=a)
        ax.set_yscale("log")
        ax.set_xlabel("call number in a fresh JVM")
        ax.set_title(f"random, n = {n:,}", fontsize=8.5)
    axes[0].set_ylabel("median time of that call [µs]")
    axes[0].legend(fontsize=6.5)
    fig.tight_layout()
    save(fig, "fig_cold")
    note("cold start: wrote cold_cumulative.csv, cold_ratios.csv, fig_cold")

# ================================================================== 5. JMH cross-check
jf = RES / "ext_jmh" / "jmh.json"
if jf.exists() and main is not None:
    j = json.loads(jf.read_text())
    rows = []
    for b in j:
        rows.append(dict(algorithm=b["params"]["algorithm"], order=b["params"]["order"], size=int(b["params"]["size"]),
                         score=b["primaryMetric"]["score"], error=b["primaryMetric"]["scoreError"], unit=b["primaryMetric"]["scoreUnit"]))
    J = pd.DataFrame(rows)
    J.to_csv(OUT / "jmh_scores.csv", index=False, float_format="%.4f")
    fm = fork_medians(main)
    ours = fm.groupby(["algorithm", "order", "size"]).med.median()
    to_ns = {"ns/op": 1.0, "us/op": 1e3, "ms/op": 1e6, "s/op": 1e9}
    J["jmh_ns"] = J.score * J.unit.map(to_ns)
    J["our_ns"] = [ours[(a, o, n)] for a, o, n in zip(J.algorithm, J.order, J["size"])]
    J["jmh_over_ours"] = J.jmh_ns / J.our_ns
    rr = []
    for (o, n), g in J.groupby(["order", "size"]):
        t, u = g.set_index("algorithm").jmh_ns, g.set_index("algorithm").our_ns
        for a, b in PAIRS:
            rr.append(dict(order=o, size=n, pair=f"{a} / {b}", jmh_ratio=t[a] / t[b], our_ratio=u[a] / u[b]))
    RR = pd.DataFrame(rr)
    RR["agreement"] = RR.jmh_ratio / RR.our_ratio
    J.to_csv(OUT / "jmh_vs_ours.csv", index=False, float_format="%.4f")
    RR.to_csv(OUT / "jmh_ratio_agreement.csv", index=False, float_format="%.4f")
    note(f"JMH: ratio of ratios (JMH/ours) median {RR.agreement.median():.3f}, range {RR.agreement.min():.3f}-{RR.agreement.max():.3f}")

# ================================================================== 6. correctness
cf = RES / "correctness" / "correctness.txt"
if cf.exists():
    note("correctness: " + cf.read_text().strip().splitlines()[-1])

(OUT / "notes.txt").write_text("\n\n".join(NOTES) + "\n")
print("follow-up 2 analysis finished ->", OUT)
