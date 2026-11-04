# Executed by build_report.py (shares its namespace): section 4 of the report.
def H(h, **kw):
    d = hyp[hyp.hypothesis == h]
    for k, v in kw.items():
        d = d[d[k] == v]
    return d

h1 = H("H1")
doc.add_heading("4.1 Compare Hypothesis to Results", level=2)
p("**H1 – sorted input: supported.** PassPerItem is between "
  f"{h1.estimate.min():,.0f}× and {h1.estimate.max():,.0f}× slower than the early-stopping algorithms (lowest CI bound "
  f"{h1.ci_lo.min():,.0f}×), far beyond the predicted 100×. The reason is mechanical: PassPerItem makes n(n−1) comparisons "
  "whatever the input, while the others make a single pass of n−1 comparisons.".replace(",", " "))
r5 = ratio("random", 5000, "UntilNoChange", "PassPerItem"); r10 = ratio("random", 10000, "UntilNoChange", "PassPerItem")
r20 = ratio("random", 20000, "UntilNoChange", "PassPerItem")
p("**H2 – random input: partly falsified.** The first part holds: WhileNeeded is the fastest algorithm in every random cell "
  f"with n ≥ 5 000 (it needs {fmt_ratio(ratio('random',20000,'WhileNeeded','PassPerItem').ratio_geomean)}–"
  f"{fmt_ratio(ratio('random',5000,'WhileNeeded','PassPerItem').ratio_geomean)} of PassPerItem's time). The second part (UntilNoChange and "
  f"PassPerItem within 15 % of each other) is falsified at n = 5 000 (UntilNoChange is {fmt_ratio(r5.ratio_geomean)}× PassPerItem, "
  f"CI {fmt_ratio(r5.ci_lo)}–{fmt_ratio(r5.ci_hi)}), inconclusive at 10 000 ({fmt_ratio(r10.ratio_geomean)}×) and supported at 20 000 "
  f"({fmt_ratio(r20.ratio_geomean)}×). We expected identical work for the two algorithms (about n² comparisons on random data), so the "
  "gap must come from the cost per comparison: UntilNoChange additionally updates a flag inside the swap branch, and the JIT-compiled "
  "inner loop and the branch predictor evidently handle that code less well. We did not verify this explanation (e.g. by inspecting the "
  "generated machine code); it is a hypothesis.")
a = ratio("reversed", 5000, "WhileNeeded", "UntilNoChange"); b = ratio("reversed", 5000, "WhileNeeded", "PassPerItem")
a2 = ratio("reversed", 20000, "WhileNeeded", "UntilNoChange")
p("**H3 – reversed input: falsified.** WhileNeeded is clearly faster than UntilNoChange at n = 5 000 "
  f"({fmt_ratio(a.ratio_geomean)}×), but it is not 10 % faster than PassPerItem anywhere – it is in fact "
  f"{(b.ratio_geomean-1)*100:.0f} % *slower* at n = 5 000 (CI {fmt_ratio(b.ci_lo)}–{fmt_ratio(b.ci_hi)}) – and at n ≥ 10 000 "
  f"it is no faster than UntilNoChange either ({fmt_ratio(a2.ratio_geomean)}× at 20 000). On reversed input every pair of neighbours is "
  "out of order, so all three algorithms perform the same n(n−1)/2 swaps and WhileNeeded cannot skip anything. What remains is the "
  "cost of the shorter pass bookkeeping, which here yields no benefit. That PassPerItem's simple loop is the fastest, "
  "although it makes twice the comparisons, shows that for swap-dominated inputs the memory writes, not the comparisons, determine the running time.")
p("**H4 – locally disturbed input: supported.** Both early-stopping algorithms are between "
  f"{H('H4').estimate.min():.0f}× and {H('H4').estimate.max():.0f}× faster than PassPerItem (lowest CI bound {H('H4').ci_lo.min():.0f}×).")
g = H("H5", claim="PassPerItem: t(20000)/t(10000) within 3.3-4.7", order="random").iloc[0]
p("**H5 – growth with n: partly falsified.** Five of six growth factors lie in the predicted range. PassPerItem on random input grows by "
  f"{g.estimate:.2f}× (CI {g.ci_lo:.2f}–{g.ci_hi:.2f}), slightly more than the 4.7 allowed – i.e. a little worse than quadratic. "
  "The doubling of n quadruples the number of operations, and the extra 20 % is probably a memory effect (two arrays of boxed Integer objects "
  "no longer fit into the fastest cache level, so the inner loop waits for memory more often); the scaling follow-up (Section 3.7) examines this. "
  "The linear growth on sorted input holds for UntilNoChange and WhileNeeded; however, UntilNoChange's value at n = 20 000 "
  "has a very wide interval, which we explain below.")
inc = H("H6", verdict="inconclusive")
f6 = H("H6", verdict="falsified")
p("**H6 – recommendation criterion: partly falsified.** WhileNeeded is never more than 5 % slower than the other algorithms in 54 of "
  f"the 60 comparisons. It violates the criterion in {len(f6)} cells, all on *reversed* input against PassPerItem, where it is "
  f"{(f6.estimate.min()-1)*100:.0f}–{(f6.estimate.max()-1)*100:.0f} % slower, and one cell is inconclusive (sorted, n = 20 000 against "
  "UntilNoChange). Strictly, H6 is therefore falsified, and the stated recommendation rule does not fire. The practical question is how much "
  "WhileNeeded can lose compared with how much the alternatives can lose (Section 3.5): WhileNeeded's worst slowdown relative to the best "
  "algorithm in a cell is about 12 % on reversed input, while PassPerItem is up to four to five orders of magnitude slower on sorted input and "
  "UntilNoChange is up to 2× slower than the best on random-like input.")
p("**An unexpected finding: bimodal JIT behaviour.** For UntilNoChange on sorted input with n = 20 000, the fork medians fall into two clusters, "
  "about 5.7 µs and about 11.4 µs (Section 3.8), although all forks ran the same code on the same data. The JIT compiler evidently reaches two different "
  "compilations of the same loop depending on the run, and one of them is twice as fast. This is the reason why the confidence interval for this cell is wide and "
  "why the corresponding hypothesis cells are inconclusive; it is also the reason why the ten forks per cell are essential: a single JVM run could have "
  "given either answer.")
