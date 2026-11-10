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


def max_loss(df, alg):
    """Largest absolute loss (median time minus best median time of the cell, n >= 1000) of an algorithm, in ns."""
    d = df[df["size"] >= 1000].pivot_table(index=["order", "size"], columns="algorithm", values="median_of_fork_medians")
    loss = d[alg] - d.min(axis=1)
    return loss.max(), loss.idxmax()


SUMM_ST = pd.read_csv(ROOT / "analysis/out/steady/summary_cells.csv") if (ROOT / "analysis/out/steady/summary_cells.csv").exists() else summ
HST = pd.read_csv(ROOT / "analysis/out/steady/hypothesis_cells.csv") if (ROOT / "analysis/out/steady/hypothesis_cells.csv").exists() else hyp


def local_exponents(alg, order="random"):
    sc = pd.read_csv(ROOT / "results" / "ext_scaling" / "raw.csv")
    t = sc[(sc.algorithm == alg) & (sc.order == order)].groupby(["size", "fork"]).ns_per_sort.median().groupby("size").median()
    return dict(zip(zip(t.index[:-1], t.index[1:]), np.diff(np.log(t.values)) / np.diff(np.log(t.index.values))))


h1 = H("H1")
doc.add_heading("4.1 Compare Hypothesis to Results", level=2)
p(f"Under the rule registered in HYPOTHESES.md (one clear violation falsifies), **H1 and H4 were supported, H2, H3 and H6 were falsified, and H5 is inconclusive (not falsified)** in the main data "
  f"({counts('H2')} for H2, {counts('H3')} for H3, {counts('H5')} for H5, {counts('H6')} for H6). "
  f"The steady-state re-measurement of Section 3.7 gives the same verdicts (cells falsified: H2 {hc('H2').falsified}, H3 {hc('H3').falsified}, H5 {hc('H5').falsified}, H6 {hc('H6').falsified}); H5 is the fragile one (below). "
  "The qualitative predictions were right (early stopping helps enormously on sorted and nearly sorted input, WhileNeeded needs the fewest comparisons, growth is quadratic or linear as expected). "
  "Wrong were our thresholds and the assumption that fewer comparisons always mean less time. The hypotheses were not changed afterwards.")
p(f"**H1 – sorted input: supported.** PassPerItem is between {th(h1.estimate.min())}× and {th(h1.estimate.max())}× slower than the early-stopping algorithms (lowest CI bound "
  f"{th(h1.ci_lo.min())}×; steady state: {th(HST[HST.hypothesis == 'H1'].estimate.min())}×–{th(HST[HST.hypothesis == 'H1'].estimate.max())}×, see Section 3.7), far beyond the predicted 100×: "
  "PassPerItem makes n(n−1) comparisons whatever the input, the others a single pass of n−1 comparisons.")
r5 = ratio("random", 5000, "UntilNoChange", "PassPerItem"); r10 = ratio("random", 10000, "UntilNoChange", "PassPerItem")
r20 = ratio("random", 20000, "UntilNoChange", "PassPerItem")
p("**H2 – random input: falsified in one cell, inconclusive in one.** WhileNeeded is the fastest algorithm in every random cell "
  f"with n ≥ 5 000 (it needs {fmt_ratio(ratio('random',20000,'WhileNeeded','PassPerItem').ratio_mean)}–"
  f"{fmt_ratio(ratio('random',5000,'WhileNeeded','PassPerItem').ratio_mean)} of PassPerItem's time). UntilNoChange and "
  f"PassPerItem are not within 15 % of each other at n = 5 000 ({fmt_ratio(r5.ratio_mean)}×, CI {ci(r5.ci_lo, r5.ci_hi)}), inconclusive at 10 000 ({fmt_ratio(r10.ratio_mean)}×; falsified after re-measurement, Appendix F) and within 15 % at 20 000 "
  f"({fmt_ratio(r20.ratio_mean)}×). Both make about n² comparisons on random data, so the gap must come from the cost per loop iteration; our conjecture is that "
  "the flag UntilNoChange sets inside the swap branch slows the compiled loop. This is supported only indirectly: with only the C1 compiler or the interpreter the gap "
  "disappears (Appendix E.8), so the C2 compiler is necessary for it. We did not inspect the generated machine code.")
a = ratio("reversed", 5000, "WhileNeeded", "UntilNoChange"); b = ratio("reversed", 5000, "WhileNeeded", "PassPerItem")
a2 = ratio("reversed", 20000, "WhileNeeded", "UntilNoChange")
p("**H3 – reversed input: falsified in 5 of 6 cells.** WhileNeeded is clearly faster than UntilNoChange at n = 5 000 "
  f"({fmt_ratio(a.ratio_mean)}×) but {(b.ratio_mean-1)*100:.0f} % *slower* than PassPerItem (CI {ci(b.ci_lo, b.ci_hi)}), and at n ≥ 10 000 no faster than UntilNoChange ({fmt_ratio(a2.ratio_mean)}× at 20 000). "
  "This disadvantage (7–12 % in the main data, up to 16 % at n = 20 000 in the steady state) is not a robust property of the algorithms: it occurs only in the main setting "
  "(Homebrew OpenJDK 26.0.1 on the first M3 Pro, Serial or Parallel collector) and is absent in every other setting we tried (G1, other JDKs, two other computers, String elements, a polluted JIT profile, C2 switched off; Appendix E). "
  "Its cause is unknown; vendor build, patch level and power state are confounded with the Java version (Appendix E.9).")
p("**H4 – locally disturbed input: supported.** Both early-stopping algorithms are between "
  f"{H('H4').estimate.min():.0f}× and {H('H4').estimate.max():.0f}× faster than PassPerItem (lowest CI bound {H('H4').ci_lo.min():.0f}×; steady state: {HST[HST.hypothesis == 'H4'].estimate.min():.0f}×–{HST[HST.hypothesis == 'H4'].estimate.max():.0f}×).")
g = H("H5", claim="PassPerItem: t(20000)/t(10000) within 3.3-4.7", order="random").iloc[0]
le = local_exponents("PassPerItem")
lo_e = [v for (x, y), v in le.items() if y <= 5000]
hi_e = [v for (x, y), v in le.items() if x >= 20000]
mid_e = [v for (x, y), v in le.items() if 5000 <= x and y <= 15000]
p("**H5 – growth with n: not falsified; 1 of 6 cells inconclusive.** Only PassPerItem on random input is at issue: when n doubles from 10 000 to 20 000 it grows by "
  f"{g.estimate:.2f}× (CI {ci(g.ci_lo, g.ci_hi)}) against 4.7. The local scaling exponents (Appendix E.7) are about {np.mean(lo_e):.2f} for n ≤ 5 000 and {np.mean(hi_e):.2f} for n ≥ 20 000 but {min(mid_e):.2f}–{max(mid_e):.2f} between 5 000 and 15 000, "
  "a localised steepening that a cache effect might explain (not tested). The interval reaches just below the limit 4.7; with the 30 forks of the pooled data (Appendix F) the cell is falsified.")
f6 = H("H6", verdict="falsified")
w5, u5, p5 = rc("WhileNeeded"), rc("UntilNoChange"), rc("PassPerItem")
sk = kc("sorted", 1000); sb = kc("sorted", 20000)
sbm = kc("sorted", 20000, "main (all 30 batches)"); skm = kc("sorted", 1000, "main (all 30 batches)")
p(f"**H6 – recommendation criterion: falsified in {len(f6)} of 60 comparisons.** WhileNeeded is more than 5 % slower than another algorithm only on reversed input, against PassPerItem "
  f"({(f6[f6.order == 'reversed'].estimate.min()-1)*100:.0f}–{(f6[f6.order == 'reversed'].estimate.max()-1)*100:.0f} % in the main data, up to 16 % in the steady state; see H3), plus one cell whose ratio is distorted by a level shift (sorted, n = 20 000, against UntilNoChange; Section 3.7) and which is supported in the steady state. "
  "The registered rule \"if this holds, WhileNeeded is recommended\" therefore does not fire; the recommendation in Section 4.3 rests on a post-hoc criterion, the worst-case slowdown of Section 3.5.")
p("**Level shifts inside a JVM.** A review of the raw data by a second AI assistant session found that for very short sorts the speed changed inside the 30 timed batches of a fork, "
  "most likely because the JIT compiler finished compiling the loop that runs the batches while it was being timed (Section 3.7; compilation events were not recorded). "
  "Our first explanation, a \"bimodal\" JIT state that depends on the JVM, was wrong: almost all forks go through the same switch, only at different batches, and WhileNeeded's switch on sorted input with n = 20 000 comes much later than UntilNoChange's "
  f"(main data: {fmt_time(sbm.WhileNeeded)} against {fmt_time(sbm.UntilNoChange)}; steady state: {fmt_time(sb.WhileNeeded)} against {fmt_time(sb.UntilNoChange)}). "
  "The steady-state analysis changes two cell verdicts (both in H6) and no overall verdict, but it changes magnitudes: main-data times of the early-stopping algorithms on sorted and nearly sorted input (and of all n = 100 cells) are up to a factor 2 too high, "
  f"WhileNeeded's worst slowdown is {w5.worst_slowdown:.2f} instead of {rc('WhileNeeded', 'main (all 30 batches)').worst_slowdown:.2f}, and UntilNoChange's {u5.worst_slowdown:.2f} instead of {rc('UntilNoChange', 'main (all 30 batches)').worst_slowdown:.2f}. The recommendation is the same in all analyses.")

doc.add_heading("4.2 Limitations and Threats to Validity", level=2)
bullets([
    "**Measurement validity: JIT state during the timed batches.** The harness warmed up with single sorts and only two untimed batches of the loop that runs the timed batches. "
    "In 46 of 1 080 forks (very short sorts) the speed changed by more than 20 % inside the fork, and 19 of 90 cells with n ≥ 1 000 and 16 of 18 cells with n = 100 are more than 10 % off the steady state even where no shift is visible (Section 3.7). "
    "We report all-batches, late-batch and steady-state analyses, but the steady-state run has only 3 forks, could itself miss shifts later than its stabilisation (at least 8 s), and no analysis monitored JIT compilations. "
    "A harness that records compilation events (a compilation MXBean or -XX:+PrintCompilation) would close this gap.",
    "**Machines and JVMs.** The complete data come from one Apple M3 Pro laptop (ARM, performance and efficiency cores, no core pinning; clock frequency and temperature not recorded). "
    "A reduced design was repeated on a second M3 Pro and on one x86 PC (Appendix E.9); the ranking holds there, the reversed-input anomaly does not appear, and since it also disappears under JDK 25.0.5 on the main laptop, JIT effects depend on the JDK build; a dependence on the hardware cannot be excluded. "
    "The second-machine runs are noisier (about 6–10 % within a fork, 28 % for the JDK 17 desktop run) than the main run (4.9 %). We varied JDK versions (8, 17, 21, 25, 26) and collectors (Serial, Parallel, G1) but only HotSpot-based JVMs from several vendors, not OpenJ9 or GraalVM. "
    "Future work: the full design on more machines (including an x86 server), the two missing runs (JDK 26.0.1 on x86, JDK 26.0.2.1 on the M3 Pro), and an inspection of the C2 machine code.",
    "**Inputs, element types, real use.** The six input orders and five extra shapes are classical but synthetic, and the arrays hold boxed Integers allocated in array order, which has better memory locality than in a long-running application. "
    "Only Integer (and, as a check, String and a polluted-JIT variant) was measured; expensive comparators should favour fewer comparisons, i.e. WhileNeeded, but we did not measure them. "
    "The design measures optimised code in a clean JVM; a real application is about 3× slower with a polluted JIT profile and much slower in the first calls (Appendices E.2, E.5), so the absolute numbers should not be quoted as customer-facing performance, only the ranking. "
    "Samples of Bubble Inc.'s real data and comparators, and measurements inside a representative application, would close these gaps.",
    "**Statistical limits.** Ten JVM forks per cell give confidence intervals of about ±1 % where the JIT is stable and wide ones where it is not (sorted n = 20 000; nearly-local inputs, whose data differ between forks); the t intervals are then approximate. "
    "Batches within a JVM are not independent, which is why the unit of inference is the fork median. Several hundred intervals were computed without correction for multiple comparisons; the conclusions rest on effects that are large compared with the intervals. "
    "The follow-ups use 3–5 forks per cell and no pre-registered thresholds. The run order was randomised but not counterbalanced (e.g. a Latin square). The ranking of the algorithms depends on the input order (an interaction), which is why every order is analysed separately. "
    "More forks, bootstrap intervals and a Holm correction would make the intervals more reliable.",
    "**Pre-registration and post-hoc analysis.** The hypotheses (01:16) and the analysis code (01:34) were committed before the main data were analysed, and the re-measurement rule (01:36) while the main run was in progress; "
    "the timestamps are local git times and the first push to GitHub came after the main run. A pilot (01:17–01:20) had already hinted at some of the later falsifications. "
    "The worst-case slowdown metric behind the recommendation (Section 3.5), the late-batch and steady-state analyses, the follow-ups and the runs on other computers came after seeing the main results and are exploratory; "
    "a new pre-registered experiment with the slowdown criterion fixed in advance would make them confirmatory.",
    f"**Time and interference.** The experiment ran overnight with the laptop connected to AC power (recorded at the start) and heavy applications closed. Four short git commits and a few low-priority tests ran at the same time; "
    f"they are logged (results/full/interference_log.txt), and the {N_OVER} overlapping jobs are indistinguishable from the others (Section 3.1). The follow-ups ran afterwards, one after the other, with a few logged analysis scripts at the lowest priority.",
    "**Scope.** Only running time was considered (as requested). Memory use is identical (in place) and all three are stable sorts; code size and readability were out of scope.",
])

doc.add_heading("4.3 Conclusions", level=2)
rg = regret.set_index("algorithm")
p(f"**Recommendation: ship BubbleSortWhileNeeded.** In the 30 conditions with n ≥ 1 000 it is the fastest algorithm in {int(rg.loc['WhileNeeded'].cells_fastest)} in the main data "
  f"and in {int(w5.fastest)} in the steady-state re-measurement; its geometric-mean slowdown against the best algorithm is {rg.loc['WhileNeeded'].geomean_regret:.2f} ({w5.geomean_slowdown:.2f}) and its worst slowdown is {w5.worst_slowdown:.2f}× "
  f"(steady state; reversed input, n = 20 000, an absolute loss of {max_loss(SUMM_ST, 'WhileNeeded')[0] / 1e6:.0f} ms per sort). "
  f"UntilNoChange is the fastest in {int(rg.loc['UntilNoChange'].cells_fastest)} cell ({int(u5.fastest)} in the steady state) and up to {rg.loc['UntilNoChange'].max_regret:.1f}× ({u5.worst_slowdown:.1f}× in the steady state, in a single 3-fork cell) slower than the best "
  f"(up to {max_loss(SUMM_ST, 'UntilNoChange')[0] / 1e6:.0f} ms per sort); PassPerItem is up to about {sig3(rg.loc['PassPerItem'].max_regret)}× slower on sorted data (at least 50× on sorted or locally disturbed input with n ≥ 1 000; up to {max_loss(SUMM_ST, 'PassPerItem')[0] / 1e6:.0f} ms per sort). "
  "The criterion is post hoc (smallest worst-case slowdown) because the pre-registered criterion H6 is not met.")
p("**Where WhileNeeded is not the best.** (1) On reversed input and cheap Integer comparisons it is 7–16 % slower than PassPerItem in the main setting only (see H3). "
  "(2) For arrays of 20 elements or fewer, UntilNoChange or PassPerItem win some cases (WhileNeeded wins all 8 input orders at n = 50), by at most about 1–2 µs (Appendix E.3). "
  "(3) On sorted input the two early-stopping algorithms are equally fast in the steady state; the differing all-batches medians of the main data are an artefact of level shifts (Section 3.7).")
p("**Beyond the decision.** Running time is not predictable from comparison counts alone: H2, H3 and H6 failed because their thresholds were derived from counting comparisons. "
  "A benchmark must warm up the code path it measures, and fresh-JVM repetitions with a check for level shifts inside each run are the minimum for credible Java benchmarks; our main harness missed this for very short sorts until a review found it. "
  "Open: the mechanism of the C2 effects (not examined at machine-code level) and whether the reversed-input anomaly is a property of JDK 26.0.1 or of the Homebrew build.")
