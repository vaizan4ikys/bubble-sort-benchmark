# Executed by build_report.py (shares its namespace): section 4 of the report.
def H(h, **kw):
    d = hyp[hyp.hypothesis == h]
    for k, v in kw.items():
        d = d[d[k] == v]
    return d

def th(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ")


h1 = H("H1")
doc.add_heading("4.1 Compare Hypothesis to Results", level=2)
p("**H1 – sorted input: supported.** PassPerItem is between "
  f"{th(h1.estimate.min())}× and {th(h1.estimate.max())}× slower than the early-stopping algorithms (lowest CI bound "
  f"{th(h1.ci_lo.min())}×), far beyond the predicted 100×. The reason is mechanical: PassPerItem makes n(n−1) comparisons "
  "whatever the input, while the others make a single pass of n−1 comparisons.")
r5 = ratio("random", 5000, "UntilNoChange", "PassPerItem"); r10 = ratio("random", 10000, "UntilNoChange", "PassPerItem")
r20 = ratio("random", 20000, "UntilNoChange", "PassPerItem")
p("**H2 – random input: partly falsified.** The first part holds: WhileNeeded is the fastest algorithm in every random cell "
  f"with n ≥ 5 000 (it needs {fmt_ratio(ratio('random',20000,'WhileNeeded','PassPerItem').ratio_geomean)}–"
  f"{fmt_ratio(ratio('random',5000,'WhileNeeded','PassPerItem').ratio_geomean)} of PassPerItem's time). The second part (UntilNoChange and "
  f"PassPerItem within 15 % of each other) is falsified at n = 5 000 (UntilNoChange is {fmt_ratio(r5.ratio_geomean)}× PassPerItem, "
  f"CI {fmt_ratio(r5.ci_lo)}–{fmt_ratio(r5.ci_hi)}), inconclusive at 10 000 ({fmt_ratio(r10.ratio_geomean)}×) and supported at 20 000 "
  f"({fmt_ratio(r20.ratio_geomean)}×). We expected identical work for the two algorithms (about n² comparisons on random data), so the "
  "gap must come from the cost per comparison: UntilNoChange additionally updates a flag inside the swap branch, and the JIT-compiled "
  "inner loop and the branch predictor evidently handle that code less well. The JIT-level follow-up (Section 3.7.8) supports this: with only the C1 compiler or the interpreter the gap "
  "disappears (UntilNoChange ≈ PassPerItem), so it is created by the optimising C2 compiler. We did not inspect the generated machine code, so the exact mechanism remains a hypothesis.")
a = ratio("reversed", 5000, "WhileNeeded", "UntilNoChange"); b = ratio("reversed", 5000, "WhileNeeded", "PassPerItem")
a2 = ratio("reversed", 20000, "WhileNeeded", "UntilNoChange")
p("**H3 – reversed input: falsified.** WhileNeeded is clearly faster than UntilNoChange at n = 5 000 "
  f"({fmt_ratio(a.ratio_geomean)}×), but it is not 10 % faster than PassPerItem anywhere – it is in fact "
  f"{(b.ratio_geomean-1)*100:.0f} % *slower* at n = 5 000 (CI {fmt_ratio(b.ci_lo)}–{fmt_ratio(b.ci_hi)}) – and at n ≥ 10 000 "
  f"it is no faster than UntilNoChange either ({fmt_ratio(a2.ratio_geomean)}× at 20 000). On reversed input every pair of neighbours is "
  "out of order, so all three algorithms perform the same n(n−1)/2 swaps, and the number of comparisons is what differs: PassPerItem compares every pair "
  "n times, WhileNeeded about half as often. With cheap Integer comparisons the run time is dominated by the memory stores and the branch behaviour of the swaps, and the simple loop of PassPerItem "
  "is apparently compiled into slightly faster code than WhileNeeded's loop, which also tracks the last swap position. The follow-up experiments support this reading: the 7–12 % disadvantage occurs only in the main setting (JDK 26.0.1 on the first M3 Pro, Serial or Parallel collector). "
  "With the G1 collector, on JDK 8, 17 and 21, on a second M3 Pro with JDK 25.0.1 and on an x86 PC with JDK 26.0.2.1, with String elements (expensive comparisons) and with a polluted JIT profile, WhileNeeded is as fast as or up to "
  "40 % faster than PassPerItem on reversed input (Section 3.7). The JIT-level follow-up (Section 3.7.8) points the same way: with only C1 or in the interpreter, WhileNeeded is about 35–45 % faster than PassPerItem on reversed input, in line with its halved number of comparisons. We did not inspect the generated machine code, so the exact mechanism remains a hypothesis.")
p("**H4 – locally disturbed input: supported.** Both early-stopping algorithms are between "
  f"{H('H4').estimate.min():.0f}× and {H('H4').estimate.max():.0f}× faster than PassPerItem (lowest CI bound {H('H4').ci_lo.min():.0f}×).")
g = H("H5", claim="PassPerItem: t(20000)/t(10000) within 3.3-4.7", order="random").iloc[0]
p("**H5 – growth with n: partly falsified.** Five of six growth factors lie in the predicted range. PassPerItem on random input grows by "
  f"{g.estimate:.2f}× (CI {g.ci_lo:.2f}–{g.ci_hi:.2f}), slightly more than the 4.7 allowed – i.e. a little worse than quadratic. "
  "The doubling of n quadruples the number of operations, and the extra 20 % is probably a memory effect (two arrays of boxed Integer objects "
  "no longer fit into the fastest cache level, so the inner loop waits for memory more often). The scaling follow-up (Section 3.7.7) shows that the effect is "
  "not a jump between 10 000 and 20 000 but a persistent slope: over n = 1 000 … 40 000 the fitted exponent of PassPerItem on random input is above 2, while UntilNoChange and "
  "WhileNeeded are closer to 2. "
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

p("**Overall.** Two of six hypotheses (H1, H4) were supported, four were partly falsified (H2, H3, H5, H6). The falsifications are all of the same kind: our "
  "predictions were based on counting comparisons, but with Integer elements the measured time depends also on how the JIT compiler turns each loop into machine code. "
  "The qualitative predictions (early stopping helps enormously on sorted and nearly sorted data; WhileNeeded needs fewer comparisons on random data; "
  "quadratic versus linear growth) were all confirmed. What we got wrong were the thresholds (e.g. \"within 15 %\") and the assumption that fewer comparisons always "
  "mean less time. We report them as they are and did not change the hypotheses after the fact.")

doc.add_heading("4.2 Limitations and Threats to Validity", level=2)
bullets([
    "**Few machines (internal and external validity).** The complete data come from one Apple M3 Pro laptop (ARM). A reduced design was repeated on a second M3 Pro and on one x86 PC "
    "(Section 3.7.9); the ranking and the main conclusions hold there, but one anomaly of the main data (reversed input) does not appear, so JIT-related effects clearly depend on hardware and JDK build. "
    "Server-class CPUs, other operating systems with a quieter background and other JVM vendors were not tested. The second-machine runs have a higher noise level (6–10 % within a fork) than the main run (4.2 %).",
    "**Only HotSpot-based JVMs.** We varied the JDK version (8, 17, 21, 25.0.1 on another machine, 26) and the GC (Serial, Parallel, G1), but not the JVM implementation "
    "(OpenJ9, GraalVM). The JDK 8 data come from a different vendor build (Amazon Corretto).",
    "**Synthetic inputs.** The six input orders and five extra shapes are classical but synthetic. Real data are somewhere in between; the recommendation "
    "rests on the fact that WhileNeeded is never far from the best on any of them. Arrays are filled with boxed Integers allocated in array order, which gives better memory locality than "
    "in a long-running application with a fragmented heap.",
    "**Element type and comparator.** The main experiment uses Integer; a String check and a polluted-JIT check were added. Expensive user-defined comparators "
    "would favour fewer comparisons, i.e. WhileNeeded, even more (as the String result shows), so this threat works in favour of the recommendation, but we have not measured it.",
    "**Steady-state vs. real use.** The main design measures optimised, warmed-up code in a clean JVM. A real application is slower by a factor of about 3 when the JIT profile is polluted "
    "and much slower in the first calls (Sections 3.7.2, 3.7.5). The absolute numbers should therefore not be quoted as customer-facing performance, only the relative ranking, which "
    "was stable in these settings.",
    "**Statistical limits.** Ten JVM forks per cell give confidence intervals of about ±1 % where the JIT is stable, but wide intervals where it is not (the bimodal "
    "sorted/n = 20 000 cell; nearly-local inputs). The distribution of fork medians is then not normal and the t intervals are approximate. Several hundred intervals were computed, "
    "without correction for multiple comparisons; the conclusions rest on effects that are large compared with the intervals. The follow-up experiments use 5 forks per cell and no pre-registered thresholds.",
    "**Post-hoc analysis.** The hypotheses and the re-measurement rule were fixed before the data; the worst-case slowdown metric used for the recommendation (Section 3.5), the "
    "choice of follow-up experiments and their analysis were defined later, after seeing the main results. They should be read as exploratory.",
    "**Time and interference.** The experiment ran overnight on AC power, with the machine otherwise idle. We checked for drift (tiny) and logged our own short test runs "
    "(results/full/interference_log.txt). The follow-up experiments ran after the main one, so the main data cannot have been disturbed by them.",
    "**Scope of the criterion.** Only running time was considered (as requested). Memory use is identical (in place), and all three are stable sorts, so nothing else would "
    "change the decision, but code size, readability and maintenance were out of scope.",
])

doc.add_heading("4.3 Conclusions", level=2)
rg = regret.set_index("algorithm")
p(f"**Recommendation: ship BubbleSortWhileNeeded.** In the 30 conditions with n ≥ 1 000 of the main experiment it is the fastest algorithm in {int(rg.loc['WhileNeeded'].cells_fastest)}, "
  f"within 5 % of the fastest in {int(rg.loc['WhileNeeded'].cells_within_5pct_of_best)}, and its geometric-mean slowdown against the best algorithm is only {rg.loc['WhileNeeded'].geomean_regret:.2f}. "
  f"For comparison, UntilNoChange is never within 5 % of the best except once and is up to {rg.loc['UntilNoChange'].max_regret:.1f}× slower than the best, and PassPerItem is up to "
  f"{th(rg.loc['PassPerItem'].max_regret)}× slower on sorted data (at least 50 times slower on sorted or locally disturbed input with n ≥ 1 000).")
p("**Where WhileNeeded is not the best.** (1) On reversed input and cheap Integer comparisons, PassPerItem is 7–12 % faster in the main setting (JDK 26.0.1 on the first M3 Pro, Serial or Parallel collector); this disappears "
  "with G1, with older JDKs, on a second M3 Pro with JDK 25.0.1, on an x86 PC, with String elements and with a polluted JIT profile. (2) On sorted input with 20 000 elements the order of WhileNeeded and UntilNoChange depends on the JIT's luck "
  "in a given JVM (UntilNoChange is either 1.7× faster or about 1.2× slower than WhileNeeded); for n ≤ 10 000 WhileNeeded is about 15 % faster. (3) For arrays of 50 elements or fewer no algorithm is reliably best, and "
  "the differences are nanoseconds. In absolute terms the losses of WhileNeeded are microseconds to milliseconds, while the alternatives can lose seconds.")
p("**What we learned beyond the decision.** Predicting running time from comparison counts alone is not enough: four of our six hypotheses were at least partly falsified because "
  "their thresholds were derived from counting comparisons. And a single JVM run can give a wrong ordering for algorithms that are close, so repeated fresh-JVM runs "
  "are the minimum for credible Java benchmarks.")
p("**Open items.** The mechanism behind the C2 effects (Section 3.7.8) "
  "was not examined at machine-code level.")
