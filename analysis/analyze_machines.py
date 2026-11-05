#!/usr/bin/env python3
"""Compares the three algorithms across machines and JDKs (reduced design: 6 orders x n = 1000, 5000, 10000).

Usage:  python analysis/analyze_machines.py
Output: analysis/out/machines/ (datasets.csv, ratios.csv, slowdown.csv, reversed_fork_ratios.csv, fig_machines.png)

The JDK of every dataset is read from its environment.txt and must match the expected major version:
the "JDK 25" follow-up (results/ext_jdk25) recorded JDK 26.0.1, so it is not used here as JDK 25.
Datasets that do not exist yet are skipped.
"""
import json
import math
import re
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import ALGS, COLOR, GRID, INK2, ORDERS, ROOT, fork_medians, style, t_ci

OUT = ROOT / "analysis" / "out" / "machines"
SIZES = [1000, 5000, 10000]
# folder, label, machine, expected JDK major version
DATASETS = [
    ("full", "M3 Pro laptop 1, JDK 26 (main)", "Apple M3 Pro, laptop 1, macOS 26.7", 26),
    ("ext_jdk17", "M3 Pro laptop 1, JDK 17", "Apple M3 Pro, laptop 1, macOS 26.7", 17),
    ("ext_jdk25_real", "M3 Pro laptop 1, JDK 25", "Apple M3 Pro, laptop 1, macOS 26.7", 25),
    ("portable_vlad-laptop", "M3 Pro laptop 2, JDK 25", "Apple M3 Pro, laptop 2, macOS 27", 25),
    ("portable_at3eus-pc-jdk26-2", "Ryzen 5 5600, JDK 26", "AMD Ryzen 5 5600, Windows 11", 26),
    ("portable_at3eus-pc", "Ryzen 5 5600, JDK 17", "AMD Ryzen 5 5600, Windows 11", 17),
]


def read_raw(path):
    """Reads raw.csv. A decimal comma (old code on a non-English locale) is repaired in memory, never on disk."""
    lines = path.read_text().splitlines()
    n = lines[0].count(",") + 1
    repaired = 0
    fixed = [lines[0]]
    for line in lines[1:]:
        fields = line.split(",")
        if len(fields) == n + 1 and fields[7].isdigit() and re.fullmatch(r"\d{3}", fields[8]):
            fields[7:9] = [f"{fields[7]}.{fields[8]}"]
            repaired += 1
        elif len(fields) != n:
            raise ValueError(f"{path}: bad row: {line}")
        fixed.append(",".join(fields))
    df = pd.read_csv(StringIO("\n".join(fixed)))
    if repaired not in (0, len(df)):
        raise ValueError(f"{path}: only {repaired} of {len(df)} rows have a decimal comma")
    if "type" in df:
        df = df[df.type == "Integer"]
    return df[df["size"].isin(SIZES)], repaired


def spread(df):
    """Median relative range (max - min) / median: of the batches within a fork, and of the fork medians in a cell."""
    keys = ["algorithm", "order", "size"]
    within = df.groupby(keys + ["fork"]).ns_per_sort.agg(lambda x: (x.max() - x.min()) / x.median())
    between = df.groupby(keys + ["fork"]).ns_per_sort.median().groupby(keys).agg(lambda x: (x.max() - x.min()) / x.median())
    return within.median(), between.median()


def analyse():
    meta, ratios, slowdown, forks = [], [], [], []
    for folder, label, machine, major in DATASETS:
        path = ROOT / "results" / folder
        if not (path / "raw.csv").exists():
            print(f"skipped (no data yet): {folder}")
            continue
        versions = re.findall(r'openjdk version "([^"]+)"', (path / "environment.txt").read_text(errors="replace"))
        java = versions[-1]
        if int(java.split(".")[0]) != major:
            raise ValueError(f"{folder}: expected JDK {major}, environment.txt says {java}")
        df, repaired = read_raw(path / "raw.csv")
        within, between = spread(df)
        config = json.loads((path / "config.json").read_text())
        meta.append(dict(dataset=folder, label=label, machine=machine, java=java,
                         harness="ExtendedWorker" if config.get("types") else "Worker",
                         forks=df.fork.nunique(), batches_per_fork=df.iter.nunique(), rows=len(df),
                         rows_repaired=repaired, gc_batches=int(df.gc_during.sum()),
                         warmup_timeouts=int(df.warmup_timeout.sum()),
                         spread_within_fork=within, spread_between_forks=between))
        wide = fork_medians(df).pivot_table(index=["order", "size", "fork"], columns="algorithm", values="med")
        for order in ORDERS:
            for size in SIZES:
                sel = wide.xs((order, size), level=("order", "size"))
                med = sel.median()
                best = med.min()
                for alg in ALGS:
                    slowdown.append(dict(label=label, order=order, size=size, algorithm=alg, slowdown=med[alg] / best))
                for num, den in (("PassPerItem", "WhileNeeded"), ("UntilNoChange", "WhileNeeded")):
                    r = sel[num] / sel[den]
                    _, lo, hi = t_ci(np.log(r.values))
                    ratios.append(dict(label=label, order=order, size=size, numerator=num, denominator=den,
                                       ratio_geomean=math.exp(np.log(r.values).mean()), ci_lo=math.exp(lo),
                                       ci_hi=math.exp(hi), ratio_median=r.median()))
                    if order == "reversed" and num == "PassPerItem":
                        forks += [dict(label=label, size=size, fork=f, ratio=v) for f, v in r.items()]
    return map(pd.DataFrame, (meta, ratios, slowdown, forks))


def figure(ratios, labels):
    """Small multiples, one panel per n; one series, so no colour legend is needed."""
    rev = ratios[(ratios.order == "reversed") & (ratios.numerator == "PassPerItem")]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 0.42 * len(labels) + 1.0), sharey=True, sharex=True)
    y = {label: i for i, label in enumerate(reversed(labels))}
    for ax, size in zip(axes, SIZES):
        d = rev[rev["size"] == size]
        ys = d.label.map(y)
        ax.axvline(1, color=INK2, linewidth=0.8)
        ax.hlines(ys, d.ci_lo, d.ci_hi, color=COLOR["WhileNeeded"], linewidth=2)
        ax.scatter(d.ratio_geomean, ys, s=30, color=COLOR["WhileNeeded"], edgecolor="white", linewidth=1, zorder=3,
                   label="Geometric mean, 95 % CI")
        ax.scatter(d.ratio_median, ys, s=70, marker="|", color="#0b0b0b", linewidth=1.2, zorder=4,
                   label="Median of the forks")
        ax.set_xscale("log")
        ax.set_xlim(0.75, 3.2)
        ax.set_xticks([0.8, 1, 1.5, 2, 3])
        ax.set_xticklabels(["0.8", "1", "1.5", "2", "3"])
        ax.minorticks_off()
        ax.set_title(f"n = {size:,}".replace(",", " "))
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color=GRID, linewidth=0.5)
    axes[0].set_yticks(list(y.values()))
    axes[0].set_yticklabels(list(y.keys()))
    axes[1].set_xlabel("PassPerItem ÷ WhileNeeded on reversed input (log axis; above 1: WhileNeeded is faster)")
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, loc="upper center", ncol=2, bbox_to_anchor=(0.6, 1.07))
    fig.savefig(OUT / "fig_machines.png", bbox_inches="tight", facecolor="white")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    style()
    meta, ratios, slowdown, forks = analyse()
    meta.to_csv(OUT / "datasets.csv", index=False, float_format="%.4f")
    ratios.to_csv(OUT / "ratios.csv", index=False, float_format="%.4f")
    slowdown.to_csv(OUT / "slowdown.csv", index=False, float_format="%.4f")
    forks.to_csv(OUT / "reversed_fork_ratios.csv", index=False, float_format="%.4f")
    figure(ratios, list(meta.label))
    print(meta[["label", "java", "harness", "forks", "rows", "rows_repaired", "gc_batches", "warmup_timeouts",
                "spread_within_fork", "spread_between_forks"]].to_string(index=False))


if __name__ == "__main__":
    main()
