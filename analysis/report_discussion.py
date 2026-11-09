# Executed by build_report.py (shares its namespace): section 4 of the report.
import numpy as np


def H(h, **kw):
    d = hyp[hyp.hypothesis == h]
    for k, v in kw.items():
        d = d[d[k] == v]
    return d


def th(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ")


def ci(lo, hi, d=2):
    """Interval text that never collapses to 'x–x'."""
    while d < 5 and f"{lo:.{d}f}" == f"{hi:.{d}f}":
        d += 1
    return f"{lo:.{d}f}–{hi:.{d}f}"


SC = ROOT / "analysis" / "out" / "steady_check"
HC = pd.read_csv(SC / "hypothesis_comparison.csv")
RC = pd.read_csv(SC / "regret_comparison.csv")
KC = pd.read_csv(SC / "key_cells.csv")
SS = "steady-state re-measurement" if (HC.analysis == "steady-state re-measurement").any() else "main, last 10 batches"


def hc(h, a=None):
    return HC[(HC.analysis == (a or SS)) & (HC.hypothesis == h)].iloc[0]


def rc(alg, a=None):
    return RC[(RC.analysis == (a or SS)) & (RC.algorithm == alg)].iloc[0]


def kc(o, n, a=None):
    return KC[(KC.analysis == (a or SS)) & (KC.order == o) & (KC["size"] == n)].iloc[0]


def counts(h):
    r = hyp_all[hyp_all.hypothesis == h].iloc[0]
    return f"{r.falsified} of {r.cells} cells falsified" + (f", {r.inconclusive} inconclusive" if r.inconclusive else "")


def local_exponents(alg, order="random"):
    sc = pd.read_csv(ROOT / "results" / "ext_scaling" / "raw.csv")
    t = sc[(sc.algorithm == alg) & (sc.order == order)].groupby(["size", "fork"]).ns_per_sort.median().groupby("size").median()
    return dict(zip(zip(t.index[:-1], t.index[1:]), np.diff(np.log(t.values)) / np.diff(np.log(t.index.values))))


h1 = H("H1")
doc.add_heading("4.1 Compare Hypothesis to Results", level=2)
p(f"Under the rule registered in HYPOTHESES.md (one clear violation falsifies), **two hypotheses (H1, H4) were supported and four (H2, H3, H5, H6) were falsified** in the main data "
  f"({counts('H2')} for H2, {counts('H3')} for H3, {counts('H5')} for H5, {counts('H6')} for H6). "
  f"The same verdict pattern results from the steady-state re-measurement of Section 3.7 (cells falsified: H2 {hc('H2').falsified}, H3 {hc('H3').falsified}, H5 {hc('H5').falsified}, H6 {hc('H6').falsified}). "
  "The qualitative predictions were right: early stopping helps enormously on sorted and nearly sorted input, WhileNeeded needs the fewest comparisons, and growth is quadratic or linear as expected. "
  "What we got wrong were thresholds and the assumption that fewer comparisons always mean less time. The hypotheses were not changed after the fact.")
p("**H1 – sorted input: supported.** PassPerItem is between "
  f"{th(h1.estimate.min())}× and {th(h1.estimate.max())}× slower than the early-stopping algorithms (lowest CI bound "
  f"{th(h1.ci_lo.min())}×), far beyond the predicted 100×. PassPerItem makes n(n−1) comparisons whatever the input, the others a single pass of n−1 comparisons.")
r5 = ratio("random", 5000, "UntilNoChange", "PassPerItem"); r10 = ratio("random", 10000, "UntilNoChange", "PassPerItem")
r20 = ratio("random", 20000, "UntilNoChange", "PassPerItem")
p("**H2 – random input: falsified in one cell, inconclusive in one.** WhileNeeded is the fastest algorithm in every random cell "
  f"with n ≥ 5 000 (it needs {fmt_ratio(ratio('random',20000,'WhileNeeded','PassPerItem').ratio_geomean)}–"
  f"{fmt_ratio(ratio('random',5000,'WhileNeeded','PassPerItem').ratio_geomean)} of PassPerItem's time). The second part (UntilNoChange and "
  f"PassPerItem within 15 % of each other) is falsified at n = 5 000 (UntilNoChange is {fmt_ratio(r5.ratio_geomean)}× PassPerItem, "
  f"CI {ci(r5.ci_lo, r5.ci_hi)}), inconclusive at 10 000 ({fmt_ratio(r10.ratio_geomean)}×; falsified after re-measurement, Appendix F) and supported at 20 000 "
  f"({fmt_ratio(r20.ratio_geomean)}×). Both algorithms make about n² comparisons on random data, so the gap must come from the cost per comparison. Our conjecture is that "
  "the flag that UntilNoChange sets inside the swap branch makes the compiled loop slower; this is supported only indirectly: with only the C1 compiler or the interpreter the gap "
  "disappears (UntilNoChange ≈ PassPerItem, Appendix E.8), so the optimising C2 compiler is necessary for it. We did not inspect the generated machine code.")
a = ratio("reversed", 5000, "WhileNeeded", "UntilNoChange"); b = ratio("reversed", 5000, "WhileNeeded", "PassPerItem")
a2 = ratio("reversed", 20000, "WhileNeeded", "UntilNoChange")
p("**H3 – reversed input: falsified in 5 of 6 cells.** WhileNeeded is clearly faster than UntilNoChange at n = 5 000 "
  f"({fmt_ratio(a.ratio_geomean)}×), but it is not 10 % faster than PassPerItem anywhere – it is {(b.ratio_geomean-1)*100:.0f} % *slower* at n = 5 000 "
  f"(CI {ci(b.ci_lo, b.ci_hi)}) – and at n ≥ 10 000 it is no faster than UntilNoChange either ({fmt_ratio(a2.ratio_geomean)}× at 20 000). "
  "WhileNeeded makes about half as many comparisons as PassPerItem on reversed input, but both perform the same n(n−1)/2 swaps, and with cheap Integer comparisons the run time is dominated by the swaps. "
  "The 7–12 % disadvantage in the main data (up to 16 % at n = 20 000 in the steady state) is, however, not a robust property of the algorithms: it occurs only in the main setting (Homebrew OpenJDK 26.0.1 on the first M3 Pro with the Serial or Parallel collector). "
  "It is absent with G1, on JDK 8, 17, 21 and 25.0.5 (same laptop), on a second M3 Pro with JDK 25.0.1, on an x86 PC with JDK 26.0.2.1, with String elements, with a polluted JIT profile, "
  "and when the C2 compiler is switched off (Appendix E). Which feature of the main setting causes it we cannot say: vendor build, patch level and power state are confounded with the Java version in the JDK 25 comparison (Appendix E.9).")
p("**H4 – locally disturbed input: supported.** Both early-stopping algorithms are between "
  f"{H('H4').estimate.min():.0f}× and {H('H4').estimate.max():.0f}× faster than PassPerItem (lowest CI bound {H('H4').ci_lo.min():.0f}×).")
g = H("H5", claim="PassPerItem: t(20000)/t(10000) within 3.3-4.7", order="random").iloc[0]
le = local_exponents("PassPerItem")
lo_e = [v for (x, y), v in le.items() if y <= 5000]
hi_e = [v for (x, y), v in le.items() if x >= 20000]
mid_e = [v for (x, y), v in le.items() if 5000 <= x and y <= 15000]
p("**H5 – growth with n: falsified in 1 of 6 cells.** The growth factors lie in the predicted range except for PassPerItem on random input, which grows by "
  f"{g.estimate:.2f}× (CI {ci(g.ci_lo, g.ci_hi)}) when n doubles from 10 000 to 20 000, slightly more than the 4.7 allowed. "
  f"The local scaling exponents of PassPerItem on random input (Appendix E.7) are about {np.mean(lo_e):.2f} for n ≤ 5 000 and {np.mean(hi_e):.2f} for n ≥ 20 000, but {min(mid_e):.2f}–{max(mid_e):.2f} between n = 5 000 and 15 000, "
  "so the excess is a localised steepening, not a constant one. A cache effect (the boxed Integer objects of the arrays no longer fit into a cache level) would fit this picture, but we did not test it. "
  "The linear growth on sorted input holds for UntilNoChange and WhileNeeded.")
f6 = H("H6", verdict="falsified")
w5, u5, p5 = rc("WhileNeeded"), rc("UntilNoChange"), rc("PassPerItem")
sk = kc("sorted", 1000); sb = kc("sorted", 20000)
sbm = kc("sorted", 20000, "main (all 30 batches)"); skm = kc("sorted", 1000, "main (all 30 batches)")
p(f"**H6 – recommendation criterion: falsified in {len(f6)} of 60 comparisons (one more inconclusive).** WhileNeeded is more than 5 % slower than another algorithm only on reversed input, against PassPerItem "
  f"({(f6.estimate.min()-1)*100:.0f}–{(f6.estimate.max()-1)*100:.0f} % slower in the main data, up to 16 % in the steady state; see H3); in addition, one cell is inconclusive in the all-batches analysis (sorted, n = 20 000, against UntilNoChange; supported in the steady state, see below). "
  "The registered rule \"if this holds, WhileNeeded is recommended\" therefore does not fire. "
  "The recommendation in Section 4.3 rests on a post-hoc criterion (the worst-case slowdown of Section 3.5), which we state explicitly.")
p("**Level shifts inside a JVM (found after the main analysis).** An independent audit showed that for very short sorts the time per sort changed inside the 30 timed batches of a fork, "
  "because the JIT compiler finished compiling the loop that runs the batches while it was being timed (Section 3.7). We first explained this wrongly as a "
  "\"bimodal\" JIT state that depends on the JVM; the trajectories show that almost all forks go through the same switch, only at different batches, and that the switch of WhileNeeded on sorted input with n = 20 000 comes much later than that of "
  f"UntilNoChange: in the main data WhileNeeded stayed at {fmt_time(sbm.WhileNeeded)} during all 30 batches, UntilNoChange dropped to {fmt_time(sbm.UntilNoChange)}. "
  f"In the steady state both early-stopping algorithms need practically the same time on sorted input (n = 1 000: {fmt_time(sk.UntilNoChange)} for UntilNoChange against {fmt_time(sk.WhileNeeded)} for WhileNeeded; "
  f"n = 20 000: {fmt_time(sb.UntilNoChange)} against {fmt_time(sb.WhileNeeded)}), whereas the all-batches medians of the main data suggested differences of {abs(skm.W_over_U - 1) * 100:.0f} % and a factor {sbm.W_over_U:.1f}. "
  "The steady-state analysis changes the verdict of two cells (H6, sorted n = 20 000 against UntilNoChange: inconclusive → supported; H6, reversed n = 10 000 against PassPerItem: falsified → inconclusive) "
  "and leaves all overall verdicts and the headline numbers practically unchanged (Section 3.7).")

doc.add_heading("4.2 Limitations and Threats to Validity", level=2)
bullets([
    "**Measurement validity: JIT state during the timed batches.** The harness warmed up with single sorts, but not with the loop that runs the timed batches; "
    "in 46 of 1 080 forks (very short sorts) the speed changed by more than 20 % inside the fork (Section 3.7). We report an all-batches analysis (as planned), a late-batches sensitivity analysis and a steady-state re-measurement, "
    "but the harness did not monitor JIT compilations, so other, smaller shifts cannot be excluded. A harness that records compilation events (e.g. with a compilation MXBean or -XX:+PrintCompilation) would close this gap.",
    "**Few machines (internal and external validity).** The complete data come from one Apple M3 Pro laptop (ARM). A reduced design was repeated on a second M3 Pro and on one x86 PC "
    "(Appendix E.9); the ranking and the main conclusions hold there, but one anomaly of the main data (reversed input) does not appear. Since it also disappears on the main laptop under JDK 25.0.5, JIT-related effects clearly depend on the JDK; a dependence on the hardware cannot be excluded. "
    "Server-class CPUs and other operating systems with a quieter background were not tested. The 11 cores of the M3 Pro are performance and efficiency cores and the operating system gives no way to pin a process, so scheduling can add noise; "
    "clock frequency and temperature were not recorded. The second-machine runs have a higher noise level (about 6–10 % within a fork) than the main run (4.9 %). "
    "Future work: the full design on more machines, including an x86 server under Linux, and the two missing runs (JDK 26.0.1 on x86, JDK 26.0.2.1 on the M3 Pro) that would locate the anomaly.",
    "**Only HotSpot-based JVMs.** We varied the JDK version (8, 17, 21, 25.0.5 and 26.0.1 on the main laptop; 25.0.1 and 26.0.2.1 on other computers) and the GC (Serial, Parallel, G1), but not the JVM implementation "
    "(OpenJ9, GraalVM). The JDK builds also come from different vendors (Homebrew, Amazon Corretto for JDK 8, Temurin for JDK 25.0.5 and the desktop). "
    "A repeat on OpenJ9 and GraalVM, and an inspection of the C2 machine code for reversed input, would test whether the ranking and our explanation hold beyond HotSpot.",
    "**Synthetic inputs.** The six input orders and five extra shapes are classical but synthetic. Real data are somewhere in between; the recommendation "
    "rests on the fact that WhileNeeded is never far from the best on any of them. Arrays are filled with boxed Integers allocated in array order, which gives better memory locality than "
    "in a long-running application with a fragmented heap. A benchmark on samples of the customers' real data, and on arrays whose elements are scattered in memory, would close this gap.",
    "**Element type and comparator.** The main experiment uses Integer; a String check and a polluted-JIT check were added. Expensive user-defined comparators "
    "would favour fewer comparisons, i.e. WhileNeeded, even more (as the String result suggests), but we have not measured them. The next step would be to measure the element types and comparators that Bubble Inc.'s customers actually use.",
    "**Steady-state vs. real use.** The main design measures optimised, warmed-up code in a clean JVM. A real application is slower by a factor of about 3 when the JIT profile is polluted "
    "and much slower in the first calls (Appendices E.2, E.5). The absolute numbers should therefore not be quoted as customer-facing performance, only the relative ranking, which "
    "was stable in these settings. Measuring the sorts inside a representative application, with its real mix of calls, would give absolute numbers that can be quoted.",
    "**Statistical limits.** Ten JVM forks per cell give confidence intervals of about ±1 % where the JIT is stable, but wide intervals where it is not (sorted n = 20 000; nearly-local inputs, whose data differ between forks). "
    "The distribution of fork medians is then not normal and the t intervals are approximate. Batches within a JVM are not independent, which is why the unit of inference is the fork median. "
    "Several hundred intervals were computed, without correction for multiple comparisons; the conclusions rest on effects that are large compared with the intervals. "
    "The follow-up experiments use 3–5 forks per cell and no pre-registered thresholds. More forks for the unstable cells, bootstrap intervals and a correction such as Holm's would make the intervals more reliable. "
    "The design has no counterbalancing (e.g. a Latin square) of the run order; we rely on randomisation and the drift check. An interaction between algorithm and input order is clearly present "
    "(the ranking of the algorithms changes with the input order) and is the reason why we analyse every order separately instead of averaging over them.",
    "**Pre-registration and post-hoc analysis.** The hypotheses (01:16) and the analysis code (01:34) were committed before the main data were analysed, and the re-measurement rule (01:36) while the main run was in progress; "
    "the timestamps are local git times, and the first push to GitHub was after the main run. A pilot run (01:17–01:20) had already hinted at some of the later falsifications. "
    "The worst-case slowdown metric used for the recommendation (Section 3.5), the late-batch and steady-state analyses, the interpretation of the follow-ups, and the runs on other computers and the real JDK 25 "
    "came after seeing the main results; all of these are exploratory. A new, pre-registered experiment with the slowdown criterion fixed in advance would turn them into confirmatory tests.",
    "**Time and interference.** The experiment ran overnight on AC power, with heavy applications closed. Four short git commits and a few low-priority tests ran at the same time; "
    "they are logged (results/full/interference_log.txt), and the 34 overlapping jobs are indistinguishable from the others (Section 3.1). The follow-up experiments ran afterwards, one after the other; "
    "a few short analysis scripts ran at the lowest priority during them and are logged in the same file. A dedicated machine with no other user activity would remove this threat.",
    "**Scope of the criterion.** Only running time was considered (as requested). Memory use is identical (in place), and all three are stable sorts, so nothing else would "
    "change the decision, but code size, readability and maintenance were out of scope. If they matter to Bubble Inc., a code review should complement this experiment.",
])

doc.add_heading("4.3 Conclusions", level=2)
rg = regret.set_index("algorithm")
p(f"**Recommendation: ship BubbleSortWhileNeeded.** In the 30 conditions with n ≥ 1 000 it is the fastest algorithm in {int(rg.loc['WhileNeeded'].cells_fastest)} in the main data "
  f"and in {int(w5.fastest)} in the steady-state re-measurement; its geometric-mean slowdown against the best algorithm is only {rg.loc['WhileNeeded'].geomean_regret:.2f} ({w5.geomean_slowdown:.2f} in the steady state), "
  f"and its worst slowdown is {w5.worst_slowdown:.2f}× (steady state; reversed input, n = 20 000, see below). "
  f"UntilNoChange is the fastest in {int(rg.loc['UntilNoChange'].cells_fastest)} cell ({int(u5.fastest)} in the steady state) and up to {rg.loc['UntilNoChange'].max_regret:.1f}× ({u5.worst_slowdown:.1f}× in the steady state) slower than the best; "
  f"PassPerItem is up to about {sig3(rg.loc['PassPerItem'].max_regret)}× slower on sorted data (at least 50 times slower on sorted or locally disturbed input with n ≥ 1 000). "
  "This follows a post-hoc criterion (smallest worst-case slowdown), because the pre-registered criterion H6 is not met.")
p("**Where WhileNeeded is not the best.** (1) On reversed input and cheap Integer comparisons PassPerItem is 7–16 % faster in the main setting (Homebrew OpenJDK 26.0.1 on the first M3 Pro, Serial or Parallel collector); this disappears "
  "with G1, with older JDKs (including 25.0.5 on the same laptop), on a second M3 Pro with JDK 25.0.1, on an x86 PC with JDK 26.0.2.1, with String elements and with a polluted JIT profile. "
  "(2) For arrays of 50 elements or fewer, WhileNeeded wins most cases, but by at most about 1 µs, and no algorithm wins reliably (Appendix E.3). "
  "(3) On sorted input the two early-stopping algorithms are equally fast in the steady state; the all-batches medians of the main data, which differ, are an artefact of level shifts (Section 3.7). "
  "In absolute terms the losses of WhileNeeded are microseconds to a few milliseconds, while the alternatives can lose seconds.")
p("**What we learned beyond the decision.** Running time is not predictable from comparison counts alone: four of our six hypotheses were falsified because "
  "their thresholds were derived from counting comparisons. A benchmark must warm up the code path it measures, and repeated fresh-JVM runs with a check for level shifts inside each run "
  "are the minimum for credible Java benchmarks; our own main harness missed this for very short sorts until an independent audit found it.")
p("**Open items.** The mechanism behind the C2 effects (Appendix E.8) was not examined at machine-code level, and whether the reversed-input anomaly is a property of JDK 26.0.1 or of the Homebrew build is open.")
