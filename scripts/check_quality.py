#!/usr/bin/env python3
"""Noise and reversed-input ratios of one run. Usage: python scripts/check_quality.py results/<run>/raw.csv"""
import csv, statistics as st, sys
d = {}
with open(sys.argv[1], newline="") as f:
    for r in csv.DictReader(f):
        d.setdefault((r["algorithm"], r["order"], int(r["size"])), {}).setdefault(r["fork"], []).append(float(r["ns_per_sort"]))
med = lambda k: st.median(st.median(x) for x in d[k].values())
within = st.median((max(x) - min(x)) / st.median(x) for v in d.values() for x in v.values())
between = st.median((max(m) - min(m)) / st.median(m) for m in ([st.median(x) for x in v.values()] for v in d.values()))
print(f"spread within a fork {within:.1%}, between forks {between:.1%}")
for n in (1000, 5000, 10000):
    print(n, "reversed PassPerItem/WhileNeeded", round(med(("PassPerItem", "reversed", n)) / med(("WhileNeeded", "reversed", n)), 2))
