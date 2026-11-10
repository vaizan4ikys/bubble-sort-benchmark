# Executed by build_report.py (shares its namespace): sections 3.7 and 3.8 (follow-up experiments).
ALG_ORDER = ["PassPerItem", "UntilNoChange", "WhileNeeded"]
F1 = ROOT / "analysis/out/followups"
F2 = ROOT / "analysis/out/followups2"
POOL = ROOT / "analysis/out/pooled"

doc.add_heading("E. Follow-up experiments", level=2)
p(f"The main experiment answers the question for one machine, one JDK, one garbage collector, one element type and a clean JVM. "
  f"To find out whether the recommendation depends on these choices, we ran the follow-up experiments of Table {TAB_NO[0] + 1}. Their first two queues were scripted while the main run was in progress, before any of its data were analysed "
  "(scripts/run_followups.sh, run_followups2.sh); the runs on other computers and the real JDK 25 run (Appendix E.9) were added after seeing the results. "
  "They use the same measuring procedure and the same fork-and-batch structure but fewer forks (5 per cell, unless stated), and they were run after the main experiment on the same machine (except Appendix E.9). "
  "They are descriptive checks of the *consistency* of the ranking; we did not pre-register thresholds for them.")
table(["Experiment", "Question", "Design"], [
    ["String elements", "Does the ranking change if comparisons are expensive?", "String instead of Integer, 6 orders × 5 sizes × 3 algorithms × 5 forks"],
    ["Garbage collector", "Is the result specific to SerialGC (JVM default is G1, whose array stores carry write barriers)?", "G1 and ParallelGC, 6 orders × 3 sizes × 5 forks"],
    ["JDK version", "Is it specific to JDK 26 (different JIT compilers)?", "JDK 8, 17, 21, 25.0.5, and a repeat on JDK 26.0.1 (a first JDK 25 run in fact used JDK 26, see Appendix E.2); 6 orders × 3 sizes × 5 forks"],
    ["Polluted JIT profile", "Real programs sort many element types; does the ranking survive megamorphic compareTo calls?", "900 ms of sorting Strings, Longs and custom objects before measuring Integers; 5 orders × 3 sizes × 5 forks"],
    ["Tiny arrays", "What is best for n = 2 … 50?", "8 input orders × 6 sizes × 5 forks"],
    ["Other input shapes", "Classic bubble-sort cases", "turtle, rabbit, sorted + random tail, organ pipe, sawtooth; 3 sizes × 5 forks"],
    ["JIT compiler level", "Are the anomalies caused by the optimising compiler (C2)?", "only C1 (-XX:TieredStopAtLevel=1) and interpreter only (-Xint); 6 orders × 100–2 000 (interpreter) / 10 000 (C1) × 5 forks"],
    ["Cold start", "What if the program sorts only a few times (no JIT warm-up)?", "first 50 calls of a fresh JVM, 30 JVMs per cell"],
    ["JMH", "Is our own harness biased?", "JMH 3 forks × 10 iterations, 3 orders × 2 sizes"],
    ["Scaling", "Exact growth exponent?", "random, sorted; 12 sizes from 200 to 40 000"],
    ["Other computers", "Does the result depend on this laptop or on ARM?", "x86 desktop and a second M3 Pro laptop; 6 orders × 3 sizes × 5 forks"],
    ["Replication, load, correctness", "Reproducible with other data? Sensitive to busy machine? Are the sorters correct?",
     "full design with a new seed; 6 busy processes; 20 139 functional checks"],
], widths=[1.3, 2.6, 2.6], size=8, caption="Follow-up experiments.")

# ---- element type
doc.add_heading("E.1 Element type: String instead of Integer", level=3)
sr = pd.read_csv(F1 / "string_vs_integer_ratios.csv")
def sv(setting, o, a, b, n=5000):
    r = sr[(sr.setting == setting) & (sr.order == o) & (sr["size"] == n) & (sr.numerator == a) & (sr.denominator == b)].iloc[0]
    return r
rs, ri = sv("String", "reversed", "WhileNeeded", "PassPerItem"), sv("Integer", "reversed", "WhileNeeded", "PassPerItem")
us, ui = sv("String", "random", "UntilNoChange", "PassPerItem"), sv("Integer", "random", "UntilNoChange", "PassPerItem")
p("When the elements are Strings, comparing two elements costs much more than swapping two references, so the number of comparisons "
  f"matters more. The ranking then follows the comparison counts: on reversed input (n = 5 000) WhileNeeded needs {rs.ratio:.2f}× the time of "
  f"PassPerItem (CI {ci(rs.ci_lo, rs.ci_hi)}) instead of {ri.ratio:.2f}× with Integers, and the gap between UntilNoChange and PassPerItem on random "
  f"input disappears ({us.ratio:.2f}× instead of {ui.ratio:.2f}×). WhileNeeded is the fastest algorithm in every String condition with n ≥ 1 000, except that it ties with UntilNoChange on sorted input.")
figure(F1 / "fig_string_vs_integer.png", "Time ratios at n = 5 000 for Integer and String elements (log axis; below 1 means the numerator is faster; bars are 95 % CIs).", width=6.4)

# ---- GC / JDK / polluted
doc.add_heading("E.2 Garbage collector, JDK version and JIT profile", level=3)
vr = pd.read_csv(F2 / "variant_regret.csv")
vs = pd.read_csv(F2 / "variant_absolute_speed.csv")
p(f"Figure {FIG_NO[0] + 1} compares the three pairwise ratios at n = 5 000 across all settings, and Table {TAB_NO[0] + 1} the slowdown relative to the best algorithm in each cell. "
  "Two observations stand out. First, the ranking for random, sorted, nearly sorted and few-unique inputs is similar in all settings: WhileNeeded "
  "fastest, UntilNoChange slowest on random-like data, PassPerItem catastrophically slow on sorted and locally disturbed data (exceptions: with the polluted JIT profile UntilNoChange is as fast as PassPerItem on random input and 7 % faster than WhileNeeded on sorted input). Second, the single "
  "anomaly of the main experiment – WhileNeeded about 10 % slower than PassPerItem on reversed input – occurs in the main setting (JDK 26.0.1 on this Mac), in its repeat run "
  "and with the Parallel collector. With G1 (the JVM default), on JDK 8, 17, 21 and 25.0.5, and on the two other machines of Appendix E.9, WhileNeeded is as fast as or faster than PassPerItem on reversed input. "
  "(The row \"JDK 26 (repeat run)\" was planned as JDK 25, but the Homebrew package openjdk@25 on this Mac turned out to contain JDK 26.0.1, as the environment file of that run shows; it is therefore a repeat of the main setting, and it reproduces the main result. A real JDK 25 was measured afterwards, row \"JDK 25 (this Mac)\", see Appendix E.9.)")
rows = []
for lab in vr.setting.unique():
    g = vr[vr.setting == lab].set_index("algorithm")
    rows.append([lab] + [f"{int(g.loc[a].fastest)}/{int(g.loc[a].cells)}" for a in ALG_ORDER] + [f"{g.loc['WhileNeeded'].max_regret:.2f}", f"{g.loc['UntilNoChange'].max_regret:.2f}", f"{g.loc['PassPerItem'].max_regret:,.0f}".replace(",", " ")])
table(["Setting", "PassPerItem fastest", "UntilNoChange fastest", "WhileNeeded fastest", "WhileNeeded worst slowdown", "UntilNoChange worst slowdown", "PassPerItem worst slowdown"],
      rows, widths=[1.7, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8], size=7.5,
      caption="Per setting (n ∈ {1 000, 5 000, 10 000}; polluted: {1 000, 5 000}): in how many (order, size) cells each algorithm is fastest, and the worst slowdown relative to the best algorithm in a cell. The row \"main\" uses only forks 0–4 of the main data, as the other rows have 5 forks (the main-laptop row of the table in E.9 uses all 10 forks).")
figure(F2 / "fig_variants_ratio_n5000.png", "Time ratios at n = 5 000 for different garbage collectors, JDK versions and a polluted JIT profile (same data in every setting).", width=6.5)
pv = vs[vs.setting.str.contains("polluted")].set_index("algorithm")
pol = vr[vr.setting.str.contains("polluted")].set_index("algorithm")
p("The absolute speed does depend on the setting, but only little for GC and JDK version (geometric mean within about ±10 % of the main setting, "
  "the extremes are the reversed-input cells, where WhileNeeded needs only 0.64–0.67 of its main-setting time on JDK 21 and 25.0.5, i.e. the anomaly itself). The polluted JIT profile is different: when the JIT compiler has already seen other element "
  f"types, every algorithm becomes slower by a factor of {pv.geomean_time_vs_main.min():.1f}–{pv.geomean_time_vs_main.max():.1f} (geometric mean over cells), "
  "because the call to compareTo can no longer be inlined. The ranking nevertheless survives: " + 
  f"WhileNeeded is fastest in {int(pol.loc['WhileNeeded'].fastest)} of {int(pol.loc['WhileNeeded'].cells)} polluted cells and never more than {(pol.loc['WhileNeeded'].max_regret - 1) * 100:.0f} % behind the best; "
  "it needs about 40 % less time than PassPerItem on random and reversed input – so with a polluted profile the reversed-input disadvantage of the main experiment is gone. "
  "The absolute times in Section 3 are therefore a best case for a clean JVM, not a prediction for a real application.")
figure(F2 / "fig_variants_regret.png", "Worst slowdown relative to the best algorithm in a cell, per setting (log axis).", width=5.8)

# ---- small
doc.add_heading("E.3 Tiny arrays (n = 2 … 50)", level=3)
sw = pd.read_csv(F2 / "small_winners.csv")
ws = (sw.fastest == "WhileNeeded").mean()
_sm = pd.read_csv(F2 / "small_ratios.csv")
_sw50 = _sm[(_sm.order == "sorted") & (_sm["size"] == 50) & (_sm.numerator == "WhileNeeded") & (_sm.denominator == "PassPerItem")].iloc[0].ratio
_sw10 = _sm[(_sm.order == "sorted") & (_sm["size"] == 10) & (_sm.numerator == "WhileNeeded") & (_sm.denominator == "PassPerItem")].iloc[0].ratio
p(f"For arrays of 50 or fewer elements one sort takes between a few nanoseconds (sorted input) and about 3 µs. On sorted input the early-stopping algorithms are clearly faster "
  f"(WhileNeeded needs {_sw10:.2f}× the time of PassPerItem at n = 10 and {_sw50:.3f}× at n = 50). On the other input orders the differences are small in absolute terms "
  f"(best-to-worst spread up to about 1–2 µs): WhileNeeded is the fastest algorithm in {ws * 100:.0f} % of all {len(sw)} (order, size) combinations, UntilNoChange and PassPerItem win the rest, "
  f"all of them at n ≤ 20 (at n = 50 WhileNeeded wins all 8 input orders). The fastest algorithm is on median {sw.advantage_vs_second.median():.2f}× faster than the second fastest "
  f"(range {sw.advantage_vs_second.min():.2f}–{sw.advantage_vs_second.max():.2f}×), and the confidence intervals in Figure {FIG_NO[0] + 1} overlap for many of these cells.")
figure(F2 / "fig_small.png", "Time of UntilNoChange and WhileNeeded relative to PassPerItem for very small arrays (bands: 95 % CI).", width=6.4)

# ---- shapes
doc.add_heading("E.4 Other classic input shapes", level=3)
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
doc.add_heading("E.5 Cold start", level=3)
cr = pd.read_csv(F2 / "cold_ratios.csv")
_cc = pd.read_csv(F2 / "cold_cumulative.csv")
_craw = pd.read_csv(ROOT / "results" / "ext_cold" / "raw.csv")
_cg = _craw[(_craw.algorithm == "PassPerItem") & (_craw.order == "random")]
cold1, coldpl = {}, {}
for n in (100, 1000, 10000):
    _x = _cg[_cg["size"] == n]
    coldpl[n] = _x[_x.call >= 20].groupby("call").ns.median().median()
    cold1[n] = _x[_x.call == 0].ns.median() / coldpl[n]
_sst = pd.read_csv(ROOT / "analysis/out/steady/summary_cells.csv")
_ss100 = _sst[(_sst.algorithm == "PassPerItem") & (_sst.order == "random") & (_sst["size"] == 100)].median_of_fork_medians.iloc[0]
cold_main_ratio = coldpl[100] / _ss100
_srt = cr[cr.order == "sorted"]
_lo, _hi = min(_srt.U_vs_P.min(), _srt.W_vs_P.min()) * 100, max(_srt.U_vs_P.max(), _srt.W_vs_P.max()) * 100
p("A program that sorts only a handful of times never reaches the optimised code that the main experiment measures. We timed the first 50 calls in "
  "30 fresh JVMs per condition. " + f"Figure {FIG_NO[0] + 1} shows that the very first call of PassPerItem on random input takes {cold1[100]:.1f}× the time of calls 20 and later for n = 100, "
  f"{cold1[1000]:.0f}× for n = 1 000 and {cold1[10000]:.1f}× for n = 10 000 (the code is interpreted at first and then compiled in stages), "
  f"and that for n = 100 and 1 000 the time stops falling after 10–20 calls. For n = 100 this plateau ({coldpl[100] / 1e3:.0f} µs) is still {cold_main_ratio:.1f}× the steady-state time of the main experiment "
  f"({_ss100 / 1e3:.1f} µs in the steady-state re-measurement): a fresh JVM does not reach the steady state within 50 calls. In the cold phase the ranking is similar: for random "
  f"input WhileNeeded is fastest in all {int((cr[cr.order == 'random'].fastest == 'WhileNeeded').sum())} of {len(cr[cr.order == 'random'])} checkpoints (first call, first 5 calls, first 20 calls). On reversed input, "
  "PassPerItem becomes slightly faster for n ≥ 1 000 after about 5 calls, as in the main experiment; on sorted input the early-stopping algorithms need "
  f"only {_lo:.1f}–{_hi:.0f} % of PassPerItem's time, depending on n and the number of calls.")
figure(F2 / "fig_cold.png", "Median time of the k-th call in a fresh JVM (random input), n = 100, 1 000 and 10 000 (log axis; 30 JVMs per curve).", width=6.5)

# ---- JMH
doc.add_heading("E.6 Cross-check with JMH", level=3)
ja = pd.read_csv(F2 / "jmh_ratio_agreement.csv")
core = ja[ja.order != "nearly_local"]
p("JMH is the standard Java micro-benchmark harness. We ran it on a subset (random, reversed and nearly-local input; n = 5 000 and 20 000; 3 JVMs, "
  "10 iterations of 1 s, one sort per invocation) and compared the ratios between the algorithms with ours. For random and reversed input the ratios "
  f"agree to within {max(abs(core.agreement - 1).max(), 0) * 100:.1f} % (ratio of ratios {core.agreement.min():.3f}–{core.agreement.max():.3f}), "
  "so our hand-written harness does not bias the comparison. On nearly-local input the ratios are very small (≈0.003) and "
  "differ by up to a factor 1.8, probably because JMH sorts a single fixed random input whereas we draw a new one per fork (we did not test this); the conclusion (hundreds of times faster than PassPerItem) is the same.")

# ---- scaling, replication, load, correctness
doc.add_heading("E.7 Scaling, replication, load and correctness", level=3)
se = pd.read_csv(F1 / "scaling_exponents.csv")
def ex(o, a):
    r = se[(se.order == o) & (se.algorithm == a)].iloc[0]
    return f"{r.exponent:.2f} ({r.ci_lo:.2f}–{r.ci_hi:.2f})"
p("**Scaling.** Fitting time = c · n^k to the 10 sizes between 1 000 and 40 000 (10 sizes × 5 forks = 50 points, treated as independent, so the intervals are optimistic) gives exponents k (95 % CI) on random input of "
  f"{ex('random','PassPerItem')} for PassPerItem, {ex('random','UntilNoChange')} for UntilNoChange and {ex('random','WhileNeeded')} for WhileNeeded; "
  f"on sorted input {ex('sorted','PassPerItem')} for PassPerItem and {ex('sorted','UntilNoChange')} and {ex('sorted','WhileNeeded')} for the two others. "
  f"The growth is quadratic (PassPerItem steeper than 2 on average; the local exponents of Table {TAB_NO[0] + 1} show that this is a localised steepening between n ≈ 5 000 and 15 000, not a constant excess) and linear, respectively.")
_le = {a: local_exponents(a) for a in ["PassPerItem", "UntilNoChange", "WhileNeeded"]}
_segs = list(_le["PassPerItem"].keys())
table(["From n", "To n"] + ["PassPerItem", "UntilNoChange", "WhileNeeded"],
      [[f"{x:,}".replace(",", " "), f"{y:,}".replace(",", " ")] + [f"{_le[a][(x, y)]:.2f}" for a in ["PassPerItem", "UntilNoChange", "WhileNeeded"]] for x, y in _segs],
      widths=[1.0, 1.0, 1.2, 1.2, 1.2], size=8, align_right_from=2,
      caption="Local scaling exponents on random input (slope of log time against log n between consecutive sizes; medians over 5 forks).")
p("**Replication.** The complete main design was repeated with a different random seed (new data, new JVMs). Of the 108 cell medians, 94 % differ from the main data by less than 5 % "
  "and 98 % by less than 10 %. For n ≥ 1 000 the median absolute difference is 0.1 % and the largest 18.9 %. "
  "The only larger deviations are the two nearly-sorted cells with local swaps at n = 5 000 (−16 % and −19 %), which have the highest between-data variation (see Appendix F).")
p("**Load.** Under load the median slowdown is 1.057× (range 1.048–1.364). From idle to load, the median CV between forks rises from 1.3 % to 1.7 %, "
  "and the median relative IQR of the batches from 1.6 % to 25.7 %. Six busy background processes thus slow the sorts by about 6 % on average but make "
  "single batches far more variable, which confirms that benchmarks must be run on an otherwise idle machine – as ours was, apart from the logged short tests (Section 2.4).")
p("**Correctness.** The three sorters passed all 20 139 checks: every permutation of up to 7 elements, 600 random arrays against Arrays.sort, all 11 input shapes, stability, and in-place behaviour (results/correctness/correctness.txt). "
  "All timed results in every experiment were also verified to be sorted. The timing comparison therefore compares correct, equivalent sorters.")
# ---- JIT level
doc.add_heading("E.8 JIT compiler level", level=3)
jm = pd.read_csv(F1 / "jit_mode_ratios.csv")
def jr(mode, o, a, b, n=2000):
    return jm[(jm.setting == mode) & (jm.order == o) & (jm["size"] == n) & (jm.numerator == a) & (jm.denominator == b)].iloc[0].ratio
p("HotSpot first interprets the bytecode, then compiles hot loops with the fast C1 compiler and finally with the optimising C2 compiler. We repeated the experiment "
  "with C2 switched off (C1 only) and with the compiler switched off entirely (interpreter only), at n = 2 000 (the interpreter is too slow for larger sizes). "
  f"With the default JIT, UntilNoChange needs {jr('C2 (default JIT)', 'random', 'UntilNoChange', 'PassPerItem'):.2f}× the time of PassPerItem on random input and WhileNeeded "
  f"{jr('C2 (default JIT)', 'reversed', 'WhileNeeded', 'PassPerItem'):.2f}× on reversed input. With only C1 these ratios are {jr('C1 only', 'random', 'UntilNoChange', 'PassPerItem'):.2f} and "
  f"{jr('C1 only', 'reversed', 'WhileNeeded', 'PassPerItem'):.2f}, and in the interpreter {jr('interpreter only', 'random', 'UntilNoChange', 'PassPerItem'):.2f} and "
  f"{jr('interpreter only', 'reversed', 'WhileNeeded', 'PassPerItem'):.2f}. Without C2 the running time simply follows the number of comparisons: WhileNeeded needs "
  f"{min(jr('C1 only', 'random', 'WhileNeeded', 'PassPerItem'), jr('interpreter only', 'random', 'WhileNeeded', 'PassPerItem')):.2f}–{max(jr('C1 only', 'random', 'WhileNeeded', 'PassPerItem'), jr('interpreter only', 'random', 'WhileNeeded', 'PassPerItem')):.2f}× the time of PassPerItem on random and reversed input, UntilNoChange equals PassPerItem. "
  "The two main surprises of the main experiment (UntilNoChange slower than PassPerItem on random input; WhileNeeded slower than PassPerItem on reversed input) need the C2 compiler: without it the ranking simply follows the comparison counts. "
  "We did not inspect the code that C2 generates, so why it produces these two effects remains open.")
figure(F1 / "fig_jit_modes.png", "Effect of the JIT compiler level at n = 2 000: time per comparison on random input (left) and time ratios to PassPerItem (right) with the default JIT, with C1 only and in the interpreter.", width=6.2)

# ---- other computers
doc.add_heading("E.9 Other computers", level=3)
M = ROOT / "analysis/out/machines"
md = pd.read_csv(M / "datasets.csv")
mr = pd.read_csv(M / "ratios.csv")
ms = pd.read_csv(M / "slowdown.csv")
mf = pd.read_csv(M / "reversed_fork_ratios.csv")
RYZEN26, RYZEN17, MAIN26 = "Ryzen 5 5600, JDK 26", "Ryzen 5 5600, JDK 17", "M3 Pro laptop 1, JDK 26 (main)"
def mrev(label, n=5000):
    return mr[(mr.label == label) & (mr.order == "reversed") & (mr.numerator == "PassPerItem") & (mr["size"] == n)].iloc[0]
def mworst(label, alg):
    return ms[(ms.label == label) & (ms.algorithm == alg)].slowdown.max()
def mwins(label):
    d = ms[(ms.label == label) & (ms.algorithm == "WhileNeeded")]
    return f"{(d.slowdown == 1).sum()}/{len(d)}"
def mspread(label):
    return md[md.label == label].spread_within_fork.iloc[0] * 100
r26, m26 = mrev(RYZEN26), mrev(MAIN26)
f26 = mf[mf.label == RYZEN26]
p("All measurements so far come from one laptop. To test whether the conclusions depend on it, we repeated the reduced design "
  "(6 input orders × n = 1 000, 5 000, 10 000 × 3 algorithms × 5 forks × 20 batches; same code, seed and JVM flags) on an x86 desktop "
  "(AMD Ryzen 5 5600, 6 cores, 16 GB RAM, Windows 11) and on a second Apple M3 Pro laptop (macOS 27). Table "
  f"{TAB_NO[0] + 1} lists the runs next to the matching data from the main laptop. The JDK of each run is taken from its environment record. "
  "The main-laptop JDK 17 row comes from the JDK follow-up, which uses ExtendedWorker with the same procedure. "
  "Machine and JDK are not fully crossed, and the JDK builds differ slightly, so this is a descriptive check.")
table(["Run", "JDK", "Forks", "WhileNeeded fastest", "Worst slowdown: WhileNeeded", "Worst slowdown: UntilNoChange", "Worst slowdown: PassPerItem",
       "PassPerItem ÷ WhileNeeded, reversed, n = 5 000", "Spread within a fork"],
      [[r.label, r.java, r.forks, mwins(r.label), f"{mworst(r.label, 'WhileNeeded'):.2f}", f"{mworst(r.label, 'UntilNoChange'):.2f}",
        f"{mworst(r.label, 'PassPerItem'):,.0f}".replace(",", " "),
        f"{mrev(r.label).ratio_mean:.2f} [{mrev(r.label).ci_lo:.2f}, {mrev(r.label).ci_hi:.2f}]", f"{r.spread_within_fork * 100:.1f} %"]
       for r in md.itertuples()],
      widths=[1.3, 0.6, 0.4, 0.6, 0.7, 0.7, 0.6, 0.9, 0.6], size=8,
      caption="The same design on different computers and JDKs (n ∈ {1 000, 5 000, 10 000}, 18 cells). Slowdown is relative to the fastest algorithm per cell. Spread: median of (max − min) / median of the batches of one fork.")
p(f"**The recommendation holds.** On the x86 desktop with JDK 26, WhileNeeded is the fastest algorithm in {mwins(RYZEN26)} cells, while UntilNoChange is up to "
  f"{mworst(RYZEN26, 'UntilNoChange'):.2f}× and PassPerItem up to " + f"{mworst(RYZEN26, 'PassPerItem'):,.0f}".replace(",", " ") + "× slower than the best. Absolute times differ, but the "
  "largest effect (early stopping on sorted input) has the same order of magnitude in every run.")
p(f"**The reversed-input anomaly does not transfer.** With the same major JDK version, PassPerItem needs {r26.ratio_mean:.2f}× the time of WhileNeeded on the desktop "
  f"(n = 5 000, CI {ci(r26.ci_lo, r26.ci_hi)}), against {m26.ratio_mean:.2f}× (CI {ci(m26.ci_lo, m26.ci_hi)}) on the main laptop: the direction is reversed. "
  "So the anomaly does not follow from JDK 26 alone. With one computer per architecture and no inspection of the machine code, we cannot attribute it to the CPU architecture itself (Figure "
  f"{FIG_NO[0] + 1}).")
p(f"**Data quality.** The desktop is noisier than the main laptop: the spread within a fork is {mspread(RYZEN26):.1f} % against {mspread(MAIN26):.1f} %. "
  f"Reversed input has two outlier JVMs: at n = 1 000 one fork has a ratio of "
  f"{f26[f26['size'] == 1000].ratio.min():.2f}, and at n = 10 000 one has {f26[f26['size'] == 10000].ratio.max():.2f}, so the means of the ratios at these sizes have wide intervals "
  f"while the median fork ratios stay near {mrev(RYZEN26, 1000).ratio_median:.2f}–{mrev(RYZEN26, 10000).ratio_median:.2f}. "
  f"The JDK 17 desktop run is weaker still ({mspread(RYZEN17):.1f} % spread, power state not recorded); its decimal commas (old code on a non-English locale) were repaired during analysis, leaving the raw file as measured. The measurements of these runs are in Appendix D.")
figure(M / "fig_machines.png", "PassPerItem ÷ WhileNeeded on reversed input per computer and JDK: mean of the paired forks with 95 % CI, and the median of the per-fork ratios.", width=6.2)
# ---- real JDK 25 on the main machine (only if that run exists)
vrr = pd.read_csv(F2 / "variant_ratios.csv")
_j25 = vrr[(vrr.setting == "JDK 25 (this Mac)") & (vrr.order == "reversed") & (vrr["size"] == 5000) & (vrr.numerator == "WhileNeeded") & (vrr.denominator == "PassPerItem")]
if len(_j25):
    r1 = _j25.iloc[0]
    p("**JDK 25 on the main laptop.** To separate the Java version from the hardware we also measured a real JDK 25 on the main laptop, with the same macOS and JVM flags but with Temurin instead of Homebrew, ExtendedWorker and 5 forks × 20 batches "
      "(the ExtendedWorker repeat on JDK 26.0.1 reproduces the main result): "
      f"WhileNeeded ÷ PassPerItem on reversed input at n = 5 000 is {r1.ratio:.2f} (CI {ci(r1.ci_lo, r1.ci_hi)}) with Temurin 25.0.5, i.e. WhileNeeded is clearly faster and the anomaly is absent. "
      "On the same laptop the anomaly therefore disappears when the JDK changes from the Homebrew OpenJDK 26.0.1 of the main experiment to Temurin 25.0.5, "
      "so the laptop alone does not cause it; the desktop result (Temurin 26.0.2.1) shows that the major version 26 alone does not cause it either. "
      "Our data cannot tell whether it is a property of JDK 26.0.1, of this Homebrew build, or of JDK 26 combined with the M3 Pro: "
      "we have no run of JDK 26.0.1 on x86 or of JDK 26.0.2.1 on the M3 Pro. "
      "Vendor (Temurin instead of Homebrew) and power state are therefore confounded with the Java version. This JDK 25 run was made with the laptop on battery power (39 % at the start, 33 % at the end), unlike the main run; its spread within a fork (5.1 %) is similar to the main run (4.9 %). "
      "The Homebrew package openjdk@25 had also been used for the first attempt, which silently ran JDK 26.0.1 (Appendix E.2).")


# ---- re-measurement
doc.add_heading("F. Re-measurement of uncertain conditions", level=2)
plan = pd.read_csv(ROOT / "results/remeasure/plan.csv")
unc = plan[plan.uncertain]
p("The pre-registered rule (Section 2.4) flagged "
  f"{len(unc)} of the 30 (order, size ≥ 1 000) groups as uncertain. These were measured again with 20 additional forks per algorithm (fork ids 10–29), so that they now "
  f"have 30 forks (900 batches per cell), and we report the pooled data next to the main data. Table {TAB_NO[0] + 1} lists the groups and why they were flagged.")
rows = []
for r in unc.itertuples():
    rows.append([ORDER_LABEL[r.order], f"{r.size:,}".replace(",", " "), r.reasons.replace(" > 5 %", "").replace(" > 3 %", "")])
table(["Input order", "n", "Reason(s) for re-measuring (rule in REMEASURE_RULE.md)"], rows, widths=[1.6, 0.6, 4.3], size=8,
      caption="Groups re-measured with 20 additional forks.")
pooled_h = pd.read_csv(POOL / "hypothesis_cells.csv")
chg = hyp.merge(pooled_h, on=["hypothesis", "claim", "order", "size"], suffixes=("_main", "_pool"))
chg = chg[chg.verdict_main != chg.verdict_pool]
p(f"**Effect on the hypothesis verdicts.** After pooling, {len(chg)} hypothesis cells change: " + "; ".join(
    f"{r.hypothesis}, {r.claim}, {r.order} n = {r.size}: {r.verdict_main} → {r.verdict_pool} ({r.estimate_pool:.3f}, CI {r.ci_lo_pool:.3f}–{r.ci_hi_pool:.3f})"
    for r in chg.itertuples()) + ". All other cells keep their verdict, so the main conclusions do not depend on the re-measurement. "
  "The overall verdicts of H1–H4 remain; H5 changes from inconclusive to falsified, and H6 stays falsified.")
p("**Why were the groups uncertain?** There are two different reasons. (1) *Nearly sorted with local swaps* (all five sizes): here the between-fork variation (CV 10–23 %) is "
  "not measurement noise. Each fork uses a different random input (5 % of the elements displaced), and the running time of the early-stopping algorithms "
  "depends strongly on how far the most displaced element has to travel, i.e. on the data. The 30 forks give a better estimate of the *distribution* of running times over such inputs, "
  "but the spread remains. The pairwise ratios are paired by data set and stay tight. (2) *Sorted input, n = 20 000, UntilNoChange*: inside every JVM the time per sort changes from about 11.4 µs to about 5.7 µs after some of the timed batches "
  "(Section 3.7). The pooled split of 40 % of the forks at 5.7 µs and 60 % at 11.4 µs therefore only shows in which phase the median of 30 batches falls; it is not two kinds of JVMs. "
  "Because the switch happens at different batches, the confidence interval of this cell is wide and the hypothesis cell stays inconclusive in the all-batches analysis.")
figure(POOL / "fig_boxplots.png", f"Pooled data (main + re-measurement): distribution of the time per sort for every input size (compare Figure {FIGREF.get('fig_boxplots.png', '?')}).", width=6.2)
