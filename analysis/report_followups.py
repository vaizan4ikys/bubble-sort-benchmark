# Executed by build_report.py (shares its namespace): sections 3.7 and 3.8 (follow-up experiments).
ALG_ORDER = ["PassPerItem", "UntilNoChange", "WhileNeeded"]
F1 = ROOT / "analysis/out/followups"
F2 = ROOT / "analysis/out/followups2"
POOL = ROOT / "analysis/out/pooled"

doc.add_heading("3.7 Robustness experiments", level=2)
p("The main experiment answers the question for one machine, one JDK, one garbage collector, one element type and a clean JVM. "
  "To find out whether the recommendation depends on these choices, we ran the follow-up experiments of Table 7. They were planned and "
  "scripted together with the main experiment (scripts/run_followups*.sh), they use the same measuring procedure and the same "
  "fork-and-batch structure but fewer forks (5 per cell, unless stated), and they were run after the main experiment on the same machine. "
  "They are descriptive checks of the *consistency* of the ranking; we did not pre-register thresholds for them.")
table(["Experiment", "Question", "Design"], [
    ["String elements", "Does the ranking change if comparisons are expensive?", "String instead of Integer, 6 orders × 5 sizes × 3 algorithms × 5 forks"],
    ["Garbage collector", "Is the result specific to SerialGC (JVM default is G1, whose array stores carry write barriers)?", "G1 and ParallelGC, 6 orders × 3 sizes × 5 forks"],
    ["JDK version", "Is it specific to JDK 26 (different JIT compilers)?", "JDK 8, 17, 21, 25; 6 orders × 3 sizes × 5 forks"],
    ["Polluted JIT profile", "Real programs sort many element types; does the ranking survive megamorphic compareTo calls?", "900 ms of sorting Strings, Longs and custom objects before measuring Integers; 5 orders × 3 sizes × 5 forks"],
    ["Tiny arrays", "What is best for n = 2 … 50?", "8 input orders × 6 sizes × 5 forks"],
    ["Other input shapes", "Classic bubble-sort cases", "turtle, rabbit, sorted + random tail, organ pipe, sawtooth; 3 sizes × 5 forks"],
    ["Cold start", "What if the program sorts only a few times (no JIT warm-up)?", "first 50 calls of a fresh JVM, 30 JVMs per cell"],
    ["JMH", "Is our own harness biased?", "JMH 3 forks × 10 iterations, 3 orders × 2 sizes"],
    ["Scaling", "Exact growth exponent?", "random, sorted; 12 sizes from 200 to 40 000"],
    ["Replication, load, correctness", "Reproducible with other data? Sensitive to busy machine? Are the sorters correct?",
     "full design with a new seed; 6 busy processes; 20 139 functional checks"],
], widths=[1.3, 2.6, 2.6], size=8, caption="Follow-up experiments.")

# ---- element type
doc.add_heading("3.7.1 Element type: String instead of Integer", level=3)
sr = pd.read_csv(F1 / "string_vs_integer_ratios.csv")
def sv(setting, o, a, b, n=5000):
    r = sr[(sr.setting == setting) & (sr.order == o) & (sr["size"] == n) & (sr.numerator == a) & (sr.denominator == b)].iloc[0]
    return r
rs, ri = sv("String", "reversed", "WhileNeeded", "PassPerItem"), sv("Integer", "reversed", "WhileNeeded", "PassPerItem")
us, ui = sv("String", "random", "UntilNoChange", "PassPerItem"), sv("Integer", "random", "UntilNoChange", "PassPerItem")
p("When the elements are Strings, comparing two elements costs much more than swapping two references, so the number of comparisons "
  f"matters more. The ranking then follows the comparison counts: on reversed input (n = 5 000) WhileNeeded needs {rs.ratio:.2f}× the time of "
  f"PassPerItem (CI {rs.ci_lo:.2f}–{rs.ci_hi:.2f}) instead of {ri.ratio:.2f}× with Integers, and the gap between UntilNoChange and PassPerItem on random "
  f"input disappears ({us.ratio:.2f}× instead of {ui.ratio:.2f}×). WhileNeeded is the fastest algorithm in every String condition with n ≥ 1 000, except that it ties with UntilNoChange on sorted input.")
figure(F1 / "fig_string_vs_integer.png", "Time ratios at n = 5 000 for Integer and String elements (log axis; below 1 means the numerator is faster; bars are 95 % CIs).", width=6.4)

# ---- GC / JDK / polluted
doc.add_heading("3.7.2 Garbage collector, JDK version and JIT profile", level=3)
vr = pd.read_csv(F2 / "variant_regret.csv")
vs = pd.read_csv(F2 / "variant_absolute_speed.csv")
p(f"Figure {FIG_NO[0] + 1} compares the three pairwise ratios at n = 5 000 across all settings, and Table 8 the slowdown relative to the best algorithm in each cell. "
  "Two observations stand out. First, the ranking for random, sorted, nearly sorted and few-unique inputs is the same in every setting: WhileNeeded "
  "fastest, UntilNoChange slowest on random-like data, PassPerItem catastrophically slow on sorted and locally disturbed data. Second, the single "
  "anomaly of the main experiment – WhileNeeded about 10 % slower than PassPerItem on reversed input – occurs only on JDK 25/26 with the "
  "Serial and Parallel collectors. With G1 (the JVM default), and on JDK 8, 17 and 21, WhileNeeded is as fast as or faster than PassPerItem on reversed input.")
rows = []
for lab in vr.setting.unique():
    g = vr[vr.setting == lab].set_index("algorithm")
    rows.append([lab] + [f"{int(g.loc[a].fastest)}/{int(g.loc[a].cells)}" for a in ALG_ORDER] + [f"{g.loc['WhileNeeded'].max_regret:.2f}", f"{g.loc['UntilNoChange'].max_regret:.2f}", f"{g.loc['PassPerItem'].max_regret:,.0f}".replace(",", " ")])
table(["Setting", "PassPerItem fastest", "UntilNoChange fastest", "WhileNeeded fastest", "WhileNeeded worst slowdown", "UntilNoChange worst slowdown", "PassPerItem worst slowdown"],
      rows, widths=[1.7, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8], size=7.5,
      caption="Per setting (n ∈ {1 000, 5 000, 10 000}; polluted: {1 000, 5 000}): in how many (order, size) cells each algorithm is fastest, and the worst slowdown relative to the best algorithm in a cell.")
figure(F2 / "fig_variants_ratio_n5000.png", "Time ratios at n = 5 000 for different garbage collectors, JDK versions and a polluted JIT profile (same data in every setting).", width=6.5)
pv = vs[vs.setting.str.contains("polluted")].set_index("algorithm")
pol = vr[vr.setting.str.contains("polluted")].set_index("algorithm")
p("The absolute speed does depend on the setting, but only little for GC and JDK version (geometric mean within about ±10 % of the main setting, "
  "the extremes being cells with a few percent of timing noise). The polluted JIT profile is different: when the JIT compiler has already seen other element "
  f"types, every algorithm becomes slower by a factor of {pv.geomean_time_vs_main.min():.1f}–{pv.geomean_time_vs_main.max():.1f} (geometric mean over cells), "
  "because the call to compareTo can no longer be inlined. The ranking nevertheless survives: " + 
  f"WhileNeeded is fastest in {int(pol.loc['WhileNeeded'].fastest)} of {int(pol.loc['WhileNeeded'].cells)} polluted cells and never more than {(pol.loc['WhileNeeded'].max_regret - 1) * 100:.0f} % behind the best; "
  "it needs about 40 % less time than PassPerItem on random and reversed input – so with a polluted profile the reversed-input disadvantage of the main experiment is gone. "
  "The absolute times in Section 3 are therefore a best case for a clean JVM, not a prediction for a real application.")
figure(F2 / "fig_variants_regret.png", "Worst slowdown relative to the best algorithm in a cell, per setting (log axis).", width=5.8)

# ---- small
doc.add_heading("3.7.3 Tiny arrays (n = 2 … 50)", level=3)
sw = pd.read_csv(F2 / "small_winners.csv")
ws = (sw.fastest == "WhileNeeded").mean()
p(f"For arrays of 50 or fewer elements one sort takes between tens of nanoseconds and a few microseconds, and the differences between the algorithms are "
  f"small (a few nanoseconds) and noisy. WhileNeeded is the fastest algorithm in {ws * 100:.0f} % of the {len(sw)} (order, size) combinations; "
  f"UntilNoChange and PassPerItem win the rest. The fastest algorithm is on median {sw.advantage_vs_second.median():.2f}× faster than the second fastest "
  f"(range {sw.advantage_vs_second.min():.2f}–{sw.advantage_vs_second.max():.2f}×), and the confidence intervals in Figure {FIG_NO[0] + 1} overlap. At this scale the "
  "choice of algorithm has no practical consequence compared with, e.g., the cost of calling the method, and no algorithm is reliably best.")
figure(F2 / "fig_small.png", "Time of UntilNoChange and WhileNeeded relative to PassPerItem for very small arrays (bands: 95 % CI).", width=6.4)

# ---- shapes
doc.add_heading("3.7.4 Other classic input shapes", level=3)
shp = pd.read_csv(F2 / "shapes_regret.csv").set_index("algorithm")
shr = pd.read_csv(F2 / "shapes_ratios.csv")
def shv(o, a, b, n=5000):
    return shr[(shr.order == o) & (shr["size"] == n) & (shr.numerator == a) & (shr.denominator == b)].iloc[0].ratio
p("The five additional shapes are turtle (a small element at the very end, which bubble sort moves left only one position per pass), rabbit (a large "
  "element at the start, which moves to the end in one pass), a sorted array with a random 10 % tail, an organ pipe and a sawtooth. For n = 5 000: "
  f"WhileNeeded needs {shv('turtle','WhileNeeded','PassPerItem'):.2f}× the time of PassPerItem on the turtle, {shv('sorted_tail','WhileNeeded','PassPerItem'):.2f}× on sorted + tail, "
  f"{shv('organ_pipe','WhileNeeded','PassPerItem'):.2f}× on the organ pipe and {shv('sawtooth','WhileNeeded','PassPerItem'):.2f}× on the sawtooth, and is about as fast as UntilNoChange on the rabbit "
  f"(both ≈ {1 / shv('rabbit','WhileNeeded','PassPerItem'):.0f}× faster than PassPerItem). UntilNoChange is up to {shv('turtle','UntilNoChange','PassPerItem'):.2f}× *slower* than PassPerItem on the turtle. "
  f"WhileNeeded is the fastest algorithm in {int(shp.loc['WhileNeeded'].fastest)} of {int(shp.loc['WhileNeeded'].cells)} shape/size cells and never more than {(shp.loc['WhileNeeded'].max_regret - 1) * 100:.1f} % slower than the best.")
figure(F2 / "fig_shapes.png", "Time ratios for the additional input shapes.", width=6.4)

# ---- cold start
doc.add_heading("3.7.5 Cold start", level=3)
cr = pd.read_csv(F2 / "cold_ratios.csv")
_cc = pd.read_csv(F2 / "cold_cumulative.csv")
cold1 = {n: _cc[(_cc.algorithm == "PassPerItem") & (_cc.order == "random") & (_cc["size"] == n) & (_cc.calls == 1)].median_total_ns.iloc[0] / med("PassPerItem", "random", n)
         for n in (100, 1000, 10000)}
_srt = cr[cr.order == "sorted"]
_lo, _hi = min(_srt.U_vs_P.min(), _srt.W_vs_P.min()) * 100, max(_srt.U_vs_P.max(), _srt.W_vs_P.max()) * 100
p("A program that sorts only a handful of times never reaches the optimised code that the main experiment measures. We timed the first 50 calls in "
  "30 fresh JVMs per condition. " + f"Figure {FIG_NO[0] + 1} shows that the very first call of PassPerItem on random input takes {cold1[100]:.0f}× the steady-state time for n = 100, "
  f"{cold1[1000]:.0f}× for n = 1 000 and {cold1[10000]:.1f}× for n = 10 000 (the code is interpreted, then compiled in stages; a long-running loop is compiled while it runs), "
  "and that the steady state is reached after 10–20 calls for n = 100 and 1 000. In the cold phase the ranking is similar: for random "
  f"input WhileNeeded is fastest in all {int((cr[cr.order == 'random'].fastest == 'WhileNeeded').sum())} of {len(cr[cr.order == 'random'])} checkpoints (first call, first 5 calls, first 20 calls). On reversed input, "
  "PassPerItem becomes slightly faster for n ≥ 1 000 after about 5 calls, as in the main experiment; on sorted input the early-stopping algorithms need "
  f"only {_lo:.1f}–{_hi:.0f} % of PassPerItem's time, depending on n and the number of calls.")
figure(F2 / "fig_cold.png", "Median time of the k-th call in a fresh JVM (random input), n = 100, 1 000 and 10 000 (log axis; 30 JVMs per curve).", width=6.5)

# ---- JMH
doc.add_heading("3.7.6 Cross-check with JMH", level=3)
ja = pd.read_csv(F2 / "jmh_ratio_agreement.csv")
core = ja[ja.order != "nearly_local"]
p("JMH is the standard Java micro-benchmark harness. We ran it on a subset (random, reversed and nearly-local input; n = 5 000 and 20 000; 3 JVMs, "
  "10 iterations of 1 s, one sort per invocation) and compared the ratios between the algorithms with ours. For random and reversed input the ratios "
  f"agree to within {max(abs(core.agreement - 1).max(), 0) * 100:.1f} % (ratio of ratios {core.agreement.min():.3f}–{core.agreement.max():.3f}), "
  "so our hand-written harness does not bias the comparison. On nearly-local input the ratios are very small (≈0.003) and "
  "differ by up to a factor 1.8 because JMH sorts a single fixed random input whereas we draw a new one per fork; the conclusion (hundreds of times faster than PassPerItem) is the same.")

# ---- scaling, replication, load, correctness
doc.add_heading("3.7.7 Scaling, replication, load and correctness", level=3)
se = pd.read_csv(F1 / "scaling_exponents.csv")
def ex(o, a):
    r = se[(se.order == o) & (se.algorithm == a)].iloc[0]
    return f"{r.exponent:.2f} ({r.ci_lo:.2f}–{r.ci_hi:.2f})"
p("**Scaling.** Fitting time = c · n^k on 12 sizes between 1 000 and 40 000 gives exponents k (95 % CI) on random input of "
  f"{ex('random','PassPerItem')} for PassPerItem, {ex('random','UntilNoChange')} for UntilNoChange and {ex('random','WhileNeeded')} for WhileNeeded; "
  f"on sorted input {ex('sorted','PassPerItem')} for PassPerItem and {ex('sorted','UntilNoChange')} and {ex('sorted','WhileNeeded')} for the two others. "
  "The growth is quadratic (PassPerItem a bit steeper than 2, consistent with the H5 result) and linear, respectively.")
p("**Replication.** The complete main design was repeated with a different random seed (new data, new JVMs). " + (F1 / "replication_summary.txt").read_text().strip().replace("Spearman rho", "Spearman ρ") + ". "
  "The only larger deviations are the two nearly-sorted cells with local swaps at n = 5 000 (−16 % and −19 %), which have the highest between-data variation (see Section 3.8).")
p("**Load.** " + (F1 / "load_summary.txt").read_text().strip() + ". Six busy background processes thus slow the sorts by about 6 % on average but make "
  "single batches far more variable, which confirms that benchmarks must be run on an otherwise idle machine – as ours were.")
p("**Correctness.** The three sorters passed all 20 139 checks: every permutation of up to 7 elements, 600 random arrays against Arrays.sort, all 11 input shapes, stability, and in-place behaviour (results/correctness/correctness.txt). "
  "All timed results in every experiment were also verified to be sorted. The timing comparison therefore compares correct, equivalent sorters.")
if (F1 / "fig_jit_modes.png").exists():
    figure(F1 / "fig_jit_modes.png", "Effect of the JIT compiler level: time per comparison and time ratios with only the C1 compiler or the bytecode interpreter.", width=6.2)

# ---- re-measurement
doc.add_heading("3.8 Re-measurement of uncertain conditions", level=2)
plan = pd.read_csv(ROOT / "results/remeasure/plan.csv")
unc = plan[plan.uncertain]
p("The pre-registered rule (Section 2.4) flagged "
  f"{len(unc)} of the 30 (order, size ≥ 1 000) groups as uncertain. These were measured again with 20 additional forks per algorithm (fork ids 10–29), so that they now "
  "have 30 forks (900 batches per cell), and we report the pooled data next to the main data. Table 9 lists the groups and why they were flagged.")
rows = []
for r in unc.itertuples():
    rows.append([ORDER_LABEL[r.order], f"{r.size:,}".replace(",", " "), r.reasons.replace(" > 5 %", "").replace(" > 3 %", "")])
table(["Input order", "n", "Reason(s) for re-measuring (rule in REMEASURE_RULE.md)"], rows, widths=[1.6, 0.6, 4.3], size=8,
      caption="Groups re-measured with 20 additional forks.")
pooled_h = pd.read_csv(POOL / "hypothesis_cells.csv")
chg = hyp.merge(pooled_h, on=["hypothesis", "claim", "order", "size"], suffixes=("_main", "_pool"))
chg = chg[chg.verdict_main != chg.verdict_pool]
p("**Effect on the hypothesis verdicts.** After pooling, one hypothesis cell changes: " + "; ".join(
    f"{r.hypothesis}, {r.claim}, {r.order} n = {r.size}: {r.verdict_main} → {r.verdict_pool} ({r.estimate_pool:.3f}, CI {r.ci_lo_pool:.3f}–{r.ci_hi_pool:.3f})"
    for r in chg.itertuples()) + ". All other cells keep their verdict, so the main conclusions do not depend on the re-measurement. "
  "The overall verdicts remain: H1 and H4 supported; H2, H3, H5 and H6 partly falsified. The cost-model coefficients are stable (R² ≥ 0.96).")
p("**Why were the groups uncertain?** There are two different reasons. (1) *Nearly sorted with local swaps* (all five sizes): here the between-fork variation (CV 10–23 %) is "
  "not measurement noise. Each fork uses a different random input (5 % of the elements displaced), and the running time of the early-stopping algorithms "
  "depends strongly on how far the most displaced element has to travel, i.e. on the data. The 30 forks give a better estimate of the *distribution* of running times over such inputs, "
  "but the spread remains. The pairwise ratios are paired by data set and stay tight. (2) *Sorted input, n = 20 000, UntilNoChange*: the JIT compiler ends in one of two states. "
  "In the pooled data 40 % of the JVMs ran the sort in about 5.7 µs and 60 % in about 11.4 µs, with no values in between, while WhileNeeded was stable at 9.8 µs. "
  "A single JVM therefore can give either ordering of the two early-stopping algorithms on this input, and we cannot state which of them is faster there; "
  "the hypothesis cell stays inconclusive. This is a property of the JVM, not a flaw of the measurement, and a practical reminder that single JVM runs can mislead.")
figure(POOL / "fig_boxplots.png", f"Pooled data (main + re-measurement): distribution of the time per sort at n = 5 000 and 20 000 (compare Figure {FIGREF.get('fig_boxplots.png', '?')}).", width=6.2)
