# Executed by build_report.py when REPORT_MODE=short (shares its namespace): the compact report that is submitted.
# The extended version (all follow-up experiments, all five-number tables) is built by the same script without
# REPORT_MODE and is kept as supplementary material in the repository.
import numpy as np


def th(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ")


def ci(lo, hi, d=2):
    while d < 5 and f"{lo:.{d}f}" == f"{hi:.{d}f}":
        d += 1
    return f"{lo:.{d}f}–{hi:.{d}f}"


SC = ROOT / "analysis" / "out" / "steady_check"
HC = pd.read_csv(SC / "hypothesis_comparison.csv")
RC = pd.read_csv(SC / "regret_comparison.csv")
HST = pd.read_csv(ROOT / "analysis/out/steady/hypothesis_cells.csv")
SS = "steady-state re-measurement"
MS = "main (all 30 batches)"
sm = pd.read_csv(SC / "level_shifts_main.csv")
n_shift, n_mild = int(sm["shift"].sum()), int(sm["mild"].sum())


def hcnt(h, a):
    r = HC[(HC.analysis == a) & (HC.hypothesis == h)].iloc[0]
    return f"{r.falsified}/{r.cells}" + (f" (+{r.inconclusive} inc.)" if r.inconclusive else "")


def rcc(alg, a):
    return RC[(RC.analysis == a) & (RC.algorithm == alg)].iloc[0]


def H(h, **kw):
    d = hyp[hyp.hypothesis == h]
    for k, v in kw.items():
        d = d[d[k] == v]
    return d


SUPP = "report/Supplementary material - extended report.docx"
p(f"Further results (all follow-up experiments, all five-number tables, other computers) are in the supplementary file “{SUPP.split('/')[-1]}”, which is in the repository (and can be submitted with this report); its appendices are cited as S-C, S-D, S-E, S-F.", italic=True, size=9)

# ------------------------------------------------------------------------------ abstract / intro
doc.add_heading("Abstract", level=1)
p((ROOT / "analysis" / "abstract.txt").read_text().strip())

doc.add_heading("1. Introduction", level=1)
p("Bubble Inc. wants to ship one of three correct Java bubble sorts, judged only by running time. They differ only in when they stop: "
  "**PassPerItem** always makes n passes, **UntilNoChange** stops after the first pass without a swap, and **WhileNeeded** also shortens every pass to the position of the last swap of the previous pass. "
  "Counting comparisons predicts WhileNeeded ≤ UntilNoChange ≤ PassPerItem, but on a real JVM running time also depends on branch prediction, memory access and the just-in-time (JIT) compiler that optimises hot code at run time, so we measured it. "
  "We ran a full-factorial experiment (3 algorithms × 6 input orders × 6 sizes) in fresh JVMs, with the hypotheses committed to git before the main data were collected. "
  "Follow-up experiments (other garbage collectors, JDKs, element types, tiny arrays, other computers) are in the supplement and only summarised here.")

doc.add_heading("Hypotheses", level=2)
p(f"The hypotheses were committed in HYPOTHESES.md (commit {PREREG[0]}, {PREREG[1][:19].replace('T', ' ')} local time) before the harness commit and the main run; "
  "a short pilot followed (Section 2.4). The file was committed once and not changed afterwards (see the git history). The independent variables are algorithm, input order and size n; the dependent variable is the running time of one call to sort. "
  "Each condition is evaluated from the 10 fork medians (a fork is one fresh JVM process; its median is taken over its 30 timed batches): a ratio between algorithms is the mean of the 10 paired per-fork ratios, a time is the mean of the 10 fork medians, and thresholds are compared with the 95 % confidence interval (Section 2.4). The null hypothesis of each is the negation of its statement.")
HYP_SHORT = [
    ("H1", "Sorted input, n ≥ 1 000: PassPerItem needs at least 100× the time of UntilNoChange and of WhileNeeded."),
    ("H2", "Random input, n ≥ 5 000: WhileNeeded is the fastest; UntilNoChange and PassPerItem differ by less than 15 %."),
    ("H3", "Reversed input, n ≥ 5 000: WhileNeeded is at least 10 % faster than both others."),
    ("H4", "Locally disturbed input, n ≥ 5 000: UntilNoChange and WhileNeeded are at least 10× faster than PassPerItem."),
    ("H5", "Doubling n from 10 000 to 20 000 multiplies the time by 3.3–4.7 on random input (all algorithms) and for PassPerItem on sorted input, and by less than 2.6 for the other two algorithms on sorted input."),
    ("H6", "For no input order and n ≥ 1 000 is WhileNeeded more than 5 % slower than another algorithm; if so, WhileNeeded is recommended."),
]
table(["", "Statement (alternative hypothesis)"], [list(x) for x in HYP_SHORT], widths=[0.5, 6.0],
      caption="Hypotheses (committed in advance). A condition counts as supporting a hypothesis if the whole 95 % confidence interval satisfies its threshold, as falsifying it if the whole interval lies on the wrong side, "
              "and as inconclusive otherwise; by the registered rule one falsified condition falsifies the hypothesis.")

# ------------------------------------------------------------------------------ method
doc.add_heading("2. Method", level=1)
doc.add_heading("2.1 Variables", level=2)
table(["Role", "Variable", "Levels / value"], [
    ["Independent", "Algorithm (3)", "PassPerItem · UntilNoChange · WhileNeeded (the provided classes, unmodified)"],
    ["Independent", "Input order (6)", "random · sorted · reversed · nearly sorted, local (also called \"locally disturbed\"; 5 % of the elements swapped with a neighbour at most 10 positions away) · nearly sorted, random (n/20 random pairs swapped) · few unique (10 different values)"],
    ["Independent", "Size n (6)", "100 · 1 000 · 2 000 · 5 000 · 10 000 · 20 000 Integer objects as elements"],
    ["Dependent", "Running time of one sort()", "System.nanoTime() over a batch of sorts (~2 ms), divided by the batch size; ratio scale, ns"],
    ["Control", "Input data", "identical arrays for the three algorithms (seed depends on order, n and fork, not on the algorithm); copying and the sortedness check are outside the timed region"],
    ["Control", "Machine, JVM", "one Apple M3 Pro laptop on AC power, OpenJDK 26.0.1, -Xms2g -Xmx2g -XX:+UseSerialGC (no collection during timed batches); one algorithm per JVM process; fresh JVM per measurement"],
    ["Control", "Run order", "all 1 080 JVM runs in random order (seed 20261104) in one session"],
], widths=[0.85, 1.35, 4.3], size=8.5)

doc.add_heading("2.2 Design", level=2)
p("Type of study:   ☐ Observational    ☐ Quasi-Experiment    ☒ Experiment          Number of factors:   ☐ Single-Factor    ☒ Multi-Factor    ☐ Other", size=10)
p("A **multi-factor, full-factorial, repeated-measures experiment**: algorithm × input order × size = 108 cells, each measured in 10 independent JVMs (forks) with 30 timed batches per JVM "
  "(32 400 observations). The \"participants\" are the data sets: fork *k* of every algorithm sorts the same data, so comparisons between algorithms are paired. "
  "Order effects are controlled because every measurement runs in a fresh JVM and the order of the runs is randomised; a drift check follows in Section 3.1. "
  "Batches within a JVM are not independent, so the unit of analysis is the median of a fork.")
figure(MAIN / "fig_design.png", "Design: three crossed factors (3 × 6 × 6 cells), 10 forks per cell, 30 timed batches per fork; the three algorithms are measured on the same inputs.", width=5.4)

doc.add_heading("2.3 Apparatus and Materials", level=2)
p("MacBook Pro (Mac15,6) with Apple M3 Pro (5 performance + 6 efficiency cores, 18 GB), macOS 26.7.1, AC power, lid open, heavy applications closed, sleep prevented with caffeinate; clock frequency and temperature were not recorded. "
  "Main experiment: OpenJDK 26.0.1 (Homebrew build), which also compiled the code. Other JDKs used only in the follow-ups of the supplement: OpenJDK 17.0.19 and 21.0.11 (Homebrew), Amazon Corretto 8 (1.8.0_482), Eclipse Temurin 25.0.5, and on other computers JDK 25.0.1 (second M3 Pro), Temurin 17.0.21 and 26.0.2.1 (Ryzen PC). "
  "Analysis: Python 3.14 with pandas 3.1, NumPy 2.5, SciPy 1.18 and matplotlib 3.11 (exact versions in requirements.txt). Own code: InputGenerator, Worker (the measuring program), run_experiment.py (one JVM per job) and the analysis scripts; "
  f"the three sorting classes come from the assignment. All code and raw data: {REPO_URL}.")

doc.add_heading("2.4 Procedure", level=2)
bullets([
    "The orchestrator starts a fresh JVM for one (algorithm, order, size, fork); the worker generates the input and creates the sorter.",
    "**Warm-up:** sorts of fresh copies until at least 20 sorts and 1.5 s have passed and the last five medians are within 5 % of the five before (limit 40 s). **Calibration:** the batch size is chosen so that a batch lasts about 2 ms.",
    "**Measurement:** two untimed batches, then 30 timed batches (copies made before the clock starts; every result is checked to be sorted afterwards, and a garbage collection in the timed region is flagged).",
])
p(f"The main run (about 77 minutes, 01:25:20–02:42:47 on 4 November 2026) was started and supervised by an AI assistant on the first author's laptop; its few concurrent commits and smoke tests are logged in results/full/interference_log.txt, and the {N_OVER} overlapping jobs are indistinguishable from the others (median relative time {REL_OVER:.3f} against {REL_OTHER:.3f}).")
p("**Statistics.** Per cell we report the five-number summary of the 300 batch measurements. Inference uses the 10 fork medians. The 95 % confidence interval is the one of Lecture 7, mean ± critical value × s/√N, with s the standard deviation of the 10 values; because N is only 10 we use the critical value 2.26 of the t distribution (9 degrees of freedom) instead of z = 1.96, which makes the interval slightly wider. Ratios between algorithms: for each fork we divide the two times measured on the same data, and take the mean and this interval of the 10 ratios. "
  "Growth factors t(20 000)/t(10 000) as the ratio of the mean time at 20 000 to the mean time at 10 000; its interval runs from (lower limit at 20 000) ÷ (upper limit at 10 000) to (upper limit at 20 000) ÷ (lower limit at 10 000), this construction is ad hoc (not a formula of the lectures): it covers the true factor in at least about 90 % of repetitions and is usually wider than a 95 % interval. No p-values are used and there is no multiple-comparison correction. Most conclusions rest on effects that are large compared with the intervals; the borderline cells (H5, and one cell of H2) are not claimed as evidence either way. "
  "A rule committed before the analysis (REMEASURE_RULE.md) re-measured ten uncertain groups with 20 additional forks; the pooled data are a sensitivity analysis, not a replacement of the main analysis, so the verdicts in this report are those of the main data. Pooling would change three cells (H2 and H5: inconclusive → falsified; H6: falsified → inconclusive; S-F). "
  "Disclosure: our first analysis code used other interval methods (geometric means of ratios, a Welch interval); we replaced them afterwards by the lecture method above. This changed H5 (falsified → inconclusive) and one H6 cell (inconclusive → falsified), nothing else.")
p("**Pilot.** Between the commit of the hypotheses and the start of the main run we ran a pilot (108 jobs, n ∈ {100, 1 000, 5 000}, 2 forks) with a not yet committed version of the harness, to choose warm-up and batch parameters. "
  "It already suggested that UntilNoChange is slower than PassPerItem on random input and WhileNeeded slower than PassPerItem on reversed input. We did not change the hypotheses; no result below uses the pilot data.")
p("**Use of GenAI.** An AI assistant was used throughout; Appendix A documents how.")

# ------------------------------------------------------------------------------ results
doc.add_heading("3. Results", level=1)
p(f"**In brief.** On sorted input PassPerItem is at least {th(H('H1').estimate.min())}× slower than the two early-stopping algorithms (n ≥ 1 000), on locally disturbed input {H('H4').estimate.min():.0f}–{H('H4').estimate.max():.0f}× (n ≥ 5 000). "
  "On random input WhileNeeded needs 57–76 % of PassPerItem's time and UntilNoChange is 9–26 % slower than PassPerItem. On reversed input WhileNeeded is 7–12 % slower than PassPerItem (main setting only). "
  "H1 and H4 are supported; H2, H3 and H6 are falsified in 1 to 6 of their cells; H5 is inconclusive (1 cell; the pooled 30-fork re-measurement data would falsify it, Section 2.4). A measurement problem (a \"level shift\": for very short sorts the speed changes part-way through a run, Section 3.6) does not change these verdicts.")

doc.add_heading("3.1 Visual Overview", level=2)
dl = drift.strip().splitlines()
_first, _last = re.findall(r": ([\d.]+)", dl[0])
_lo, _hi = dl[1].split(":")[1].strip().split("..")
_lo, _hi = _lo.strip(), _hi.strip()
p("All 1 080 jobs completed, every result was verified to be sorted, no timed batch contained a garbage collection and no warm-up hit its limit. The individual batch measurements range from 25 ns per sort (sorted, n = 100) to 0.52 s (n = 20 000). "
  f"Drift over the session: the median relative time (job time ÷ cell median) is {_first} in the first third of the session and {_last} in the last third; the rolling median stays within {_lo}–{_hi} of the cell median, far smaller than the 5–10 % and larger effects discussed below.")
figure(MAIN / "fig_scaling.png",
       "Median time of one sort against input size (log–log), one panel per input order; shaded band = 95 % CI over forks (mostly narrower than the markers); dotted lines show n and n² growth.", width=5.6)
figure(MAIN / "fig_boxplots.png",
       "Distribution of the time per sort (all 300 batch measurements per box, logarithmic axis) for each size, input order and algorithm. Box = interquartile range, line = median, whiskers = 1.5 × IQR, points = outliers. The wide boxes (sorted, n = 1 000 and 20 000) are level shifts (Section 3.6).", width=5.6)

doc.add_heading("3.2 Descriptive Statistics", level=2)
p("The five-number summary of the 300 measurements per cell gives the minimum (fastest batch), first quartile Q1, median, third quartile Q3 and maximum; Q3 − Q1 shows how repeatable the timing is. Table 2 shows n = 10 000; the other sizes are in S-C and in analysis/out/main/five_number_tables.md of the repository.")
rows = []
for o in ORDERS:
    for a in ALG_ORDER:
        r = summ[(summ.algorithm == a) & (summ.order == o) & (summ["size"] == 10000)].iloc[0]
        rows.append([ORDER_LABEL[o], a, fmt_time(r["min"]), fmt_time(r.q1), fmt_time(r["median"]), fmt_time(r.q3), fmt_time(r["max"])])
table(["Input order", "Algorithm", "Min", "Q1", "Median", "Q3", "Max"], rows, widths=[1.6, 1.25, 0.75, 0.75, 0.75, 0.75, 0.75], align_right_from=2, size=8,
      caption="Five-number summary of the time per sort, n = 10 000. Summary of all 300 batches per row.")

doc.add_heading("3.3 Comparing the algorithms", level=2)
rows = []
for o in ORDERS:
    for n in (5000, 20000):
        def f(r):
            if r.ratio_mean < 0.01:
                return tiny_ratio(r.ratio_mean, r.ci_lo, r.ci_hi)
            if r.ratio_mean < 0.1:
                return f"{r.ratio_mean:.3f} [{r.ci_lo:.3f}, {r.ci_hi:.3f}]"
            return f"{fmt_ratio(r.ratio_mean)} [{fmt_ratio(r.ci_lo)}, {fmt_ratio(r.ci_hi)}]"
        rows.append([ORDER_LABEL[o], th(n), f(ratio(o, n, "UntilNoChange", "PassPerItem")), f(ratio(o, n, "WhileNeeded", "PassPerItem")), f(ratio(o, n, "WhileNeeded", "UntilNoChange"))])
table(["Input order", "n", "UntilNoChange ÷ PassPerItem", "WhileNeeded ÷ PassPerItem", "WhileNeeded ÷ UntilNoChange"], rows,
      widths=[1.55, 0.6, 1.5, 1.5, 1.5], size=8,
      caption="Paired time ratios (mean over 10 forks, 95 % CI in brackets); values below 1 mean the first-named algorithm is faster; 1/970 means 970× faster. Ratios on sorted input are distorted by level shifts (Section 3.6); other sizes: S-Table 3.")

doc.add_heading("3.4 Hypothesis checks", level=2)
rows = []
for r in hyp_all.itertuples():
    rows.append([r.hypothesis, (f"Inconclusive ({r.inconclusive} of {r.cells} cells)" if r.falsified == 0 and r.inconclusive > 0 else verdict_label(r)), hcnt(r.hypothesis, SS).replace('inc.', 'inconclusive')])
table(["Hypothesis", "Verdict, main data (registered rule)", "Cells falsified, steady-state re-measurement"], rows, widths=[1.0, 3.3, 2.2], size=8.5,
      caption="Hypothesis verdicts. The steady-state column (cells falsified, inconclusive in brackets) comes from the re-measurement of Section 3.6, in which a warm-up of the timed loop was added (3 forks per cell). H1 and H4 are supported in both analyses.")

doc.add_heading("3.5 Decision metric: worst-case slowdown", level=2)
p("For the recommendation we compare each algorithm with the fastest one in every cell with n ≥ 1 000 (30 cells): the slowdown is its median time divided by the smallest median of the three (1.00 = fastest).")
rows = []
for a in ALG_ORDER:
    m, s = rcc(a, MS), rcc(a, SS)
    rows.append([a, f"{int(m.fastest)} / 30", sig3(m.worst_slowdown), pretty_where(m.worst_where), f"{int(s.fastest)} / 30", sig3(s.worst_slowdown), pretty_where(s.worst_where)])
table(["Algorithm", "Fastest in (main)", "Worst slowdown (main)", "Where", "Fastest in (steady)", "Worst slowdown (steady)", "Where"], rows,
      widths=[1.05, 0.75, 0.8, 1.2, 0.75, 0.8, 1.2], size=8,
      caption="Slowdown relative to the fastest algorithm per cell, n ≥ 1 000. WhileNeeded's main-data worst case (sorted, n = 20 000) is the level-shift artefact of Section 3.6; in the steady state it is 1.16.")

doc.add_heading("3.6 Level shifts inside a JVM and a steady-state check", level=2)
p(f"A review of the raw data after the main analysis showed that for very short sorts the time per sort changes inside a fork. Comparing the first and last 10 of the 30 timed batches, {n_shift} of 1 080 forks differ by more than 20 % ({n_mild} more by 5–20 %); "
  "all large shifts are speed-ups and all flagged cells have very short sorts (sorted n = 100, 1 000, 20 000 and locally disturbed n = 100, 1 000). In sorted input with n = 1 000 all 20 forks of both early-stopping algorithms get about twice as fast "
  "(for example 570 ns → 250 ns), and in sorted input with n = 20 000 all ten forks of UntilNoChange go from 11.4 µs to 5.7 µs. The most likely cause is that the JIT compiler finishes compiling the loop that runs the batches while it is being timed; "
  "the main harness warmed up with single sorts and only two untimed batches. We did not record compilation events, so this explanation is untested.")
figure(SC / "fig_level_shifts.png",
       "Time per sort of each timed batch, sorted input, n = 1 000 and 20 000. Top: main data (10 forks, thin lines; thick = median). Bottom: steady-state re-measurement (3 forks).", width=5.2)
_svm = pd.read_csv(SC / "steady_vs_main_cells.csv")
_big = _svm[_svm["size"] >= 1000]
p("We therefore re-measured all 108 cells with a variant of the harness (SteadyWorker) that, after the warm-up, runs whole batches until the batch time is stable (window of 50 batches, tolerance 3 %, at least 8 s for short sorts) before the 30 timed batches; "
  "same JDK, flags and data, 3 forks per cell. Compared with the same forks of the main data, "
  f"{int(_big.differs_10pct.sum())} of {len(_big)} cells with n ≥ 1 000 differ by more than 10 %: main-data times of the early-stopping algorithms on sorted and nearly sorted input are up to a factor of about 2 too high. "
  "The verdicts of H1–H6 do not change (Table 4), two cell verdicts of H6 do, and the recommendation is the same (Table 5). Main-data times for these cells (Tables 2–3 and S-C) should be read as upper bounds.")

# ------------------------------------------------------------------------------ discussion
doc.add_heading("4. Discussion", level=1)
doc.add_heading("4.1 Compare Hypothesis to Results", level=2)
h1 = H("H1")
r5 = ratio("random", 5000, "UntilNoChange", "PassPerItem")
b = ratio("reversed", 5000, "WhileNeeded", "PassPerItem")
a2 = ratio("reversed", 20000, "WhileNeeded", "UntilNoChange")
g = H("H5", claim="PassPerItem: t(20000)/t(10000) within 3.3-4.7", order="random").iloc[0]
f6 = H("H6", verdict="falsified")
bullets([
    f"**H1 supported.** PassPerItem is {th(h1.estimate.min())}–{th(h1.estimate.max())}× slower on sorted input (lowest CI bound {th(h1.ci_lo.min())}×; steady state {th(HST[HST.hypothesis == 'H1'].estimate.min())}–{th(HST[HST.hypothesis == 'H1'].estimate.max())}×), "
    "far above 100×: PassPerItem makes n(n−1) comparisons whatever the input, the others one pass.",
    f"**H2 falsified (1 of 9 cells; 1 inconclusive).** WhileNeeded is the fastest in every random cell with n ≥ 5 000, but UntilNoChange is {(r5.ratio_mean-1)*100:.0f} % slower than PassPerItem at n = 5 000 (CI {ci(r5.ci_lo, r5.ci_hi)}), more than the 15 % allowed. "
    "Both make about n² comparisons, so the gap is a cost per iteration. Our conjecture is that the flag UntilNoChange sets inside the swap branch slows the compiled loop; the gap disappears with only the C1 compiler or the interpreter (S-E.8), but we did not inspect machine code.",
    f"**H3 falsified (5 of 6 cells).** WhileNeeded is faster than UntilNoChange at n = 5 000 but {(b.ratio_mean-1)*100:.0f} % *slower* than PassPerItem (CI {ci(b.ci_lo, b.ci_hi)}), and at n ≥ 10 000 no faster than UntilNoChange ({fmt_ratio(a2.ratio_mean)}× at 20 000). "
    "The disadvantage (7–12 %, up to 16 % in the steady state) is not a robust property of the algorithms: it occurs only in the main setting (this OpenJDK 26.0.1 build on this laptop, Serial or Parallel collector) and not with G1, JDK 8/17/21/25, a second M3 Pro, an x86 PC, String elements or a polluted JIT profile (S-E, S-D). Its cause is unknown.",
    f"**H4 supported.** Both early-stopping algorithms are {H('H4').estimate.min():.0f}–{H('H4').estimate.max():.0f}× faster than PassPerItem (lowest CI bound {H('H4').ci_lo.min():.0f}×).",
    f"**H5 inconclusive (1 of 6 cells).** Only PassPerItem on random input is at issue: it grows by {g.estimate:.2f}× (CI {ci(g.ci_lo, g.ci_hi)}) when n doubles, against the limit 4.7. The interval reaches just below the limit; with the 30 forks of the pooled data the cell is falsified (S-F).",
    f"**H6 falsified ({len(f6)} of 60 comparisons).** WhileNeeded is more than 5 % slower than another algorithm on reversed input, against PassPerItem (see H3), and in one cell whose ratio is distorted by a level shift (sorted, n = 20 000, against UntilNoChange; Section 3.6). The registered rule therefore does not fire, and our recommendation rests on a post-hoc criterion.",
])
p("The qualitative predictions were right (early stopping helps enormously on sorted and nearly sorted input; growth is quadratic or linear as expected). Wrong were thresholds that assumed fewer comparisons always mean less time. The hypotheses were not changed afterwards.")

doc.add_heading("4.2 Limitations and Threats to Validity", level=2)
bullets([
    "**Measurement validity.** The main harness did not warm up the batch loop, so main-data times of very short sorts are up to 2× too high in some cells (Section 3.6). The steady-state re-measurement has only 3 forks and no analysis recorded JIT compilations.",
    "**One machine, one JDK build.** The complete data come from one M3 Pro laptop and one OpenJDK build. A reduced design on a second M3 Pro and an x86 PC, and several other JDKs, kept the ranking but not the reversed-input anomaly (S-D, S-E); clock frequency and temperature were not recorded.",
    "**Inputs and use.** Six synthetic input orders (five more shapes in S-E.4) with boxed Integers allocated in order and a warmed-up JVM. A real application with a polluted JIT profile is about 3× slower (S-E.2); absolute times should not be quoted, only the ranking. Expensive comparators and real customer data were not measured.",
    "**Statistics.** Ten forks per cell; the t intervals are approximate where the JIT is unstable (sorted n = 20 000; locally disturbed inputs). No correction for multiple comparisons.",
    "**Post-hoc analysis.** The worst-case-slowdown criterion, the late-batch and steady-state analyses and all follow-ups were chosen after seeing the main results and are exploratory. The pilot had already hinted at some falsifications. Timestamps are local git times; the first push to GitHub came after the main run.",
])

doc.add_heading("4.3 Conclusions", level=2)
_pp = pair[(pair.denominator == "PassPerItem") & (pair["size"] >= 1000)]
_pmin_s = 1 / _pp[_pp.order == "sorted"].ratio_mean.max()
_pmin_l = 1 / _pp[_pp.order == "nearly_local"].ratio_mean.max()
rg = regret.set_index("algorithm")
w5, u5, pp5 = rcc("WhileNeeded", SS), rcc("UntilNoChange", SS), rcc("PassPerItem", SS)
p(f"**Recommendation: ship BubbleSortWhileNeeded.** In the 30 conditions with n ≥ 1 000 it is the fastest in {int(rg.loc['WhileNeeded'].cells_fastest)} (main data) and {int(w5.fastest)} (steady state) and at most {w5.worst_slowdown:.2f}× slower than the best in the steady state (reversed input, n = 20 000; a point estimate from 3 forks without interval; the main data give {rcc('WhileNeeded', MS).worst_slowdown:.2f}, an artefact of level shifts, Section 3.6). "
  f"UntilNoChange is up to {u5.worst_slowdown:.1f}× slower than the best; PassPerItem is up to about {sig3(pp5.worst_slowdown)}× slower (sorted input) and at least {_pmin_s:.0f}× slower on sorted and {_pmin_l:.0f}× on locally disturbed input (n ≥ 1 000, main data). "
  "The criterion is post hoc because the H6 criterion fixed in advance was not met.")
p("**Where WhileNeeded is not the best:** on reversed input with cheap Integer comparisons it is 7–16 % slower than PassPerItem in our main setting; for arrays of 20 elements or fewer another algorithm wins some cases by at most about 1–2 µs (S-E.3). "
  "Running time was not predictable from comparison counts alone, and a benchmark must warm up the code path it times and check for level shifts inside each run. Open: the mechanism of the JIT effects and whether the reversed-input anomaly is a property of this JDK build.")

doc.add_heading("Appendix A: Use of GenAI tools", level=1)
p("**Tools.** Claude (Anthropic) through Claude Code, a command-line coding agent with access to the first author's laptop, including to its files and shell commands, and, as sub-agents without our context, additional Claude sessions for reviews. The second author used his own Claude session on his computers.")
bullets([
    "**What the assistant did:** proposed the design and hypotheses (the authors decided on the design questions); wrote the Java measuring code, the Python orchestration and analysis scripts and the script that builds this document; started and monitored the experiments; drafted the text of this report from the generated tables.",
    "**What the authors did:** defined the assignment and the design decisions (for example the choice of what to compare and which follow-ups to run), prepared the machine (power, closed applications), installed additional JDKs, ran the experiments on the second author's computers, and read and checked the report, the numbers and the code.",
    "**Review by independent AI sessions:** two sub-agents without prior context audited the data and the report. They flagged the level shifts of Section 3.6, which we then verified in the raw data (Figure 3), and several wrong or overstated claims in earlier drafts (for example an unsupported \"bimodal JIT\" explanation, a wrong direction of an effect, a wrong battery statement); these were corrected, and the corrections are in the git history.",
    "**Limits of this documentation:** the full chat transcript is not part of the repository, and the model versions of the early sessions were not recorded; later git commits carry the trailer \"Co-Authored-By: Claude Sonnet 5.5\". Tables and most numbers in the text are generated by scripts from the raw data; the ranges in \"In brief\" and in Section 4.1 (for example 7–12 %, 57–76 %, up to 16 %) were typed from those outputs.",
])
p("The authors take responsibility for the report and are prepared to explain every method in it, including the confidence interval mean ± t · s/√N over fork medians, the mean of paired ratios, the conservative interval of the growth factor, and the steady-state re-measurement.")

doc.add_heading("Appendix B: reproduction", level=1)
p(f"Everything needed to recreate every number, table and figure is in {REPO_URL} (branch main at the time of submission): raw measurements (results/full/raw.csv, one line per timed batch), environment records, harness, orchestration and analysis scripts, HYPOTHESES.md and REMEASURE_RULE.md; the order of the steps is in README.md. "
  "The three sorting classes were used unmodified; no human participants were involved. The supplementary file contains the five-number tables of all conditions (S-C), the measurements on the other computers (S-D), the follow-up experiments (S-E) and the re-measurement of uncertain groups (S-F).")
