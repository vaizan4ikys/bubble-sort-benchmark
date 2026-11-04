"""Shared helpers for the analysis scripts (loading, statistics, plotting style)."""
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ALGS = ["PassPerItem", "UntilNoChange", "WhileNeeded"]
ORDERS = ["random", "sorted", "reversed", "nearly_local", "nearly_random", "few_unique"]
ORDER_LABEL = {
    "random": "random",
    "sorted": "sorted",
    "reversed": "reversed",
    "nearly_local": "nearly sorted (local swaps)",
    "nearly_random": "nearly sorted (random swaps)",
    "few_unique": "few unique values",
}

# Validated categorical palette (slots 1-3, light surface); see dataviz skill / palette.md.
COLOR = {"PassPerItem": "#2a78d6", "UntilNoChange": "#eb6834", "WhileNeeded": "#1baf7a"}
MARKER = {"PassPerItem": "o", "UntilNoChange": "s", "WhileNeeded": "^"}
LINESTYLE = {"PassPerItem": "-", "UntilNoChange": "--", "WhileNeeded": ":"}
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#d9d8d3"


def style():
    """Apply the plotting style: thin recessive grid, no top/right spines, readable text."""
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 8.5, "axes.titlesize": 9.5,
        "axes.labelsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.axisbelow": True,
        "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
    })


def fmt_time(ns: float) -> str:
    """Human-readable duration with 3 significant digits (precision for people, not machines)."""
    if ns is None or (isinstance(ns, float) and math.isnan(ns)):
        return "-"
    for unit, scale in (("s", 1e9), ("ms", 1e6), ("µs", 1e3), ("ns", 1.0)):
        if ns >= scale or unit == "ns":
            v = ns / scale
            digits = 0 if v >= 100 else (1 if v >= 10 else 2)
            return f"{v:.{digits}f} {unit}"
    return str(ns)


def fmt_ratio(r: float) -> str:
    if r < 0.01:
        return "<0.01"
    if r >= 100:
        return f"{r:.0f}"
    if r >= 10:
        return f"{r:.1f}"
    return f"{r:.2f}"


def load_raw(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def fork_medians(df: pd.DataFrame, extra_keys=()) -> pd.DataFrame:
    """One row per (cell, fork): the median of the timed batches of that fork (JVM)."""
    keys = list(extra_keys) + ["algorithm", "order", "size", "fork"]
    return df.groupby(keys, as_index=False).agg(med=("ns_per_sort", "median"), seq=("seq", "first"))


def t_ci(x, conf=0.95):
    """Mean and t-based confidence interval of a sample (lecture 7; t instead of z because N is small)."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    m = x.mean()
    if n < 2:
        return m, m, m
    se = x.std(ddof=1) / math.sqrt(n)
    h = stats.t.ppf(0.5 + conf / 2, n - 1) * se
    return m, m - h, m + h


def paired_ratio(wide: pd.DataFrame, order: str, size: int, num: str, den: str, **extra):
    """Ratio num/den of the per-fork medians, paired by fork (same input data for both algorithms).

    Returns (point, geo_mean, lo, hi): point = median(num)/median(den) over forks,
    geo_mean/lo/hi = geometric mean of the paired ratios with its 95 % t-interval.
    """
    sel = wide.xs((order, size), level=("order", "size"))
    a, b = sel[num].dropna(), sel[den].dropna()
    idx = a.index.intersection(b.index)
    a, b = a.loc[idx], b.loc[idx]
    if len(idx) == 0:
        return (math.nan,) * 4
    logr = np.log(a.values / b.values)
    m, lo, hi = t_ci(logr)
    return float(a.median() / b.median()), math.exp(m), math.exp(lo), math.exp(hi)


def growth_factor(fm: pd.DataFrame, order: str, alg: str, n1: int, n2: int):
    """Factor by which the time grows from size n1 to n2 (Welch interval on log fork medians)."""
    def logs(n):
        return np.log(fm[(fm.order == order) & (fm.algorithm == alg) & (fm["size"] == n)].med.values)
    a, b = logs(n1), logs(n2)
    if len(a) < 2 or len(b) < 2:
        return (math.nan,) * 3
    d = b.mean() - a.mean()
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    h = stats.t.ppf(0.975, df) * se
    return math.exp(d), math.exp(d - h), math.exp(d + h)


def five_number(x):
    x = np.asarray(x, dtype=float)
    q = np.percentile(x, [0, 25, 50, 75, 100])
    return q
