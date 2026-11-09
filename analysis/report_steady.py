# Executed by build_report.py (shares its namespace): sections 3.7 and 3.8 of the report.
SCD = ROOT / "analysis" / "out" / "steady_check"
sm = pd.read_csv(SCD / "level_shifts_main.csv")
lcells = pd.read_csv(SCD / "level_shift_cells_main.csv")
HCc = pd.read_csv(SCD / "hypothesis_comparison.csv")
RCc = pd.read_csv(SCD / "regret_comparison.csv")
KCc = pd.read_csv(SCD / "key_cells.csv")
has_steady = (RCc.analysis == "steady-state re-measurement").any()
n_shift, n_mild, n_forks = int(sm["shift"].sum()), int(sm["mild"].sum()), len(sm)

doc.add_heading("3.7 Level shifts inside a JVM and a steady-state check", level=2)
p(f"After the main analysis, an independent audit of the raw data found that in some cells the time per sort changes inside a fork. For every fork we compared the median of the first 10 "
  f"with the median of the last 10 of the 30 timed batches. In {n_shift} of the 1 080 forks the two differ by more than 20 %, and in {n_mild} more by 5–20 %. " +
  "All large shifts go in the same direction (the later batches are faster) and they are confined to cells with very short sorts (Table "
  f"{TAB_NO[0] + 1}). In sorted input with n = 1 000, all 20 forks of both early-stopping algorithms speed up by a factor of about 2 (UntilNoChange from about 570 ns to about 250 ns, WhileNeeded from about 490 ns to about 270 ns); "
  "in sorted input with n = 20 000, all ten forks of UntilNoChange go from about 11.4 µs to about 5.7 µs. Figure "
  f"{FIG_NO[0] + 1} shows the trajectories. The five-number summaries of Appendix C and the medians of Section 3.2 contain both levels for these cells.")
rows = []
for r in lcells.itertuples():
    rows.append([ORDER_LABEL[r.order], f"{r.size:,}".replace(",", " "), r.algorithm, f"{r.forks_with_shift} of 10", f"{r.median_last_over_first:.2f}", f"{r.median_switch_batch:.0f}"])
table(["Input order", "n", "Algorithm", "Forks with a shift > 20 %", "Time of last 10 ÷ first 10 batches (median)", "Batch at which the shift happens (median)"], rows,
      widths=[1.5, 0.6, 1.2, 1.0, 1.2, 1.0], size=8, caption="Cells of the main data with level shifts inside the forks (the other 99 cells have none above 20 %).")
figure(SCD / "fig_level_shifts.png",
       "Time per sort of every timed batch for sorted input, n = 1 000 and 20 000. Top: main data (10 forks, thin lines; thick line = median over forks). "
       "Bottom: steady-state re-measurement (3 forks) with a long stabilisation of the batch loop before the timed batches. Logarithmic y axis.", width=6.4)
p("We therefore report three analyses of the same design. (1) *All batches*: the pre-planned analysis of Sections 3.2–3.6. (2) *Late batches*: the same analysis of the main data using only batches 21–30 of every fork, "
  "when the shifts are complete. (3) *Steady-state re-measurement*: all 108 cells measured again with exp01.SteadyWorker, a variant of the measuring program that, after the single-sort warm-up, runs whole batches "
  "through the same method that is later timed, until the batch time has been stable for 5 consecutive checks (at least 400 rounds and at least 8 s of wall-clock time for short sorts, at most 15 s of batch time), "
  "before the 30 timed batches. It uses the same JDK, flags, data (forks 0–2 of the main data, same seed) and procedure otherwise; 3 forks per cell instead of 10 because of the time available (about one hour). "
  "SteadyWorker was written after the audit; Worker, which produced the main data, was not changed.")
if has_steady:
    ss = pd.read_csv(SCD / "level_shifts_steady.csv")
    st_dq = (ROOT / "analysis/out/steady/data_quality.txt").read_text()
    st_gc = int(re.search(r"GC during the timed region: (\d+)", st_dq).group(1))
    p(f"In the steady-state run the stabilisation criterion was met in all {len(ss)} forks; {int(ss['shift'].sum())} fork has a level shift above 20 % between the first and the last 10 timed batches "
      f"({int(ss['mild'].sum())} more between 5 and 20 %); {st_gc} timed batch contained a garbage collection (flagged, 0.01 %). "
      "The run lasted 56 minutes (20:13–21:09 on 9 November 2026). It started on battery power (87 %) and the charger was connected a few minutes later, which is not the condition of the main run (AC throughout); "
      "no other program was started during the run except one test run of the analysis script at the lowest priority (results/full/interference_log.txt). "
      "In the steady state, WhileNeeded on sorted input with n = 20 000 also reaches about 5.8 µs: its switch comes much later than that of UntilNoChange (in the main data it was still at about 9.8 µs during all 30 batches).")
def _cnt(a, h):
    r = HCc[(HCc.analysis == a) & (HCc.hypothesis == h)].iloc[0]
    return f"{r.falsified}/{r.cells}" + (f" (+{r.inconclusive} inconclusive)" if r.inconclusive else "")
rows = []
for a in RCc.analysis.unique():
    w = RCc[(RCc.analysis == a) & (RCc.algorithm == "WhileNeeded")].iloc[0]
    u = RCc[(RCc.analysis == a) & (RCc.algorithm == "UntilNoChange")].iloc[0]
    pp = RCc[(RCc.analysis == a) & (RCc.algorithm == "PassPerItem")].iloc[0]
    rows.append([a, " · ".join(f"H{k}: {_cnt(a, 'H' + str(k))}" for k in (2, 3, 5, 6)), f"{int(w.fastest)} / {int(w.cells)}", f"{w.worst_slowdown:.2f}",
                 f"{int(u.fastest)} / {int(u.cells)}", f"{u.worst_slowdown:.2f}", sig3(pp.worst_slowdown)])
table(["Analysis", "Cells falsified (H1 and H4: supported in all)", "WhileNeeded fastest", "WhileNeeded worst slowdown", "UntilNoChange fastest", "UntilNoChange worst slowdown", "PassPerItem worst slowdown"], rows,
      widths=[1.3, 2.0, 0.7, 0.7, 0.7, 0.7, 0.7], size=7.5,
      caption="The three analyses compared (n ≥ 1 000; 'fastest' counts the cells in which the algorithm has the smallest median time).")
rows = []
for a in KCc.analysis.unique():
    for o, n in (("sorted", 100), ("sorted", 1000), ("sorted", 20000), ("nearly_local", 100)):
        r = KCc[(KCc.analysis == a) & (KCc.order == o) & (KCc["size"] == n)].iloc[0]
        rows.append([a, ORDER_LABEL[o], f"{n:,}".replace(",", " "), fmt_time(r.PassPerItem), fmt_time(r.UntilNoChange), fmt_time(r.WhileNeeded), f"{r.W_over_U:.2f}"])
table(["Analysis", "Input order", "n", "PassPerItem", "UntilNoChange", "WhileNeeded", "WhileNeeded ÷ UntilNoChange"], rows,
      widths=[1.7, 1.2, 0.6, 0.9, 0.9, 0.9, 0.9], size=8, align_right_from=3,
      caption="Median time per sort in the cells most affected by level shifts, in the three analyses.")

doc.add_heading("3.8 Further experiments and re-measurement (summary)", level=2)
vr_ = pd.read_csv(ROOT / "analysis/out/followups2/variant_regret.csv")
_w = vr_[(vr_.algorithm == "WhileNeeded") & (vr_.cells == 18)]
sr_ = pd.read_csv(ROOT / "analysis/out/followups/string_vs_integer_ratios.csv")
_s = sr_[(sr_.setting == "String") & (sr_.order == "reversed") & (sr_["size"] == 5000) & (sr_.numerator == "WhileNeeded") & (sr_.denominator == "PassPerItem")].iloc[0].ratio
p("Besides the main experiment we ran the follow-up experiments of Appendix E and the pre-registered re-measurement of Appendix F. They are descriptive checks "
  "of the consistency of the ranking and are not used for the hypothesis verdicts. Table "
  f"{TAB_NO[0] + 1} gives the main numbers; the details, figures and the discussion of the differences are in the appendices.")
table(["Experiment", "Main number", "Details"], [
    ["Garbage collectors, JDK versions, polluted JIT profile, other computers (n ∈ {1 000, 5 000, 10 000})",
     f"WhileNeeded is the fastest algorithm in {int(_w.fastest.min())}–{int(_w.fastest.max())} of 18 cells in every setting; its worst slowdown against the best is {_w.max_regret.min():.2f}–{_w.max_regret.max():.2f}×", "Appendix E.2, E.9, D"],
    ["String instead of Integer elements", f"WhileNeeded ÷ PassPerItem on reversed input, n = 5 000: {_s:.2f} (main data with Integer: 1.10)", "Appendix E.1"],
    ["Tiny arrays (n = 2 … 50)", "WhileNeeded fastest in 77 % of 48 cells; differences at most about 1 µs on non-sorted input", "Appendix E.3"],
    ["Other input shapes", "WhileNeeded fastest in 13 of 15 cells, never more than 0.8 % slower than the best", "Appendix E.4"],
    ["Cold start, JMH", "first call of PassPerItem (random, n = 100) 8.6× the time of calls 30–50; JMH ratios agree with ours within 1.2 % (random, reversed)", "Appendix E.5, E.6"],
    ["Scaling, replication, load, correctness", "exponents 2.0–2.1 (random) and 1.0 (sorted, early-stopping); 94 % of cells within 5 % in the replication; 20 139 correctness checks passed", "Appendix E.7"],
    ["JIT compiler level", "UntilNoChange ÷ PassPerItem on random input, n = 2 000: 1.22 (default), 1.05 (C1 only), 0.98 (interpreter)", "Appendix E.8"],
    ["Re-measurement of 10 uncertain groups (20 more forks)", "one hypothesis cell changes (H2, random, n = 10 000: inconclusive → falsified)", "Appendix F"],
], widths=[2.3, 3.3, 0.9], size=8, caption="Summary of the further experiments.")
