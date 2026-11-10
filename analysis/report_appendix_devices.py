# Executed by build_report.py (shares its namespace): Appendix D, measurements from the additional computers.
import numpy as np

from analyze_machines import SIZES as DEV_SIZES, read_raw

DEVICES = [  # folder, label in ratios.csv, short column name, heading, description
    ("portable_vlad-laptop", "M3 Pro laptop 2, JDK 25", "M3 laptop 2, JDK 25",
     "Apple M3 Pro laptop 2, JDK 25.0.1",
     "macOS 27, on AC power, 10.6 minutes. The load average at the start was 5.28 over 1 minute and 24.9 over 5 minutes, "
     "so the machine had been busy shortly before the run."),
    ("portable_at3eus-pc-jdk26-2", "Ryzen 5 5600, JDK 26", "Ryzen, JDK 26",
     "AMD Ryzen 5 5600 desktop, JDK 26.0.2.1",
     "Windows 11, Temurin, High performance power plan, 15.7 minutes."),
    ("portable_at3eus-pc", "Ryzen 5 5600, JDK 17", "Ryzen, JDK 17",
     "AMD Ryzen 5 5600 desktop, JDK 17.0.21",
     "Windows 11, Temurin, 17.4 minutes. Power state not recorded and the noisiest run (Appendix E.9). The raw file has decimal "
     "commas, which the analysis repairs in memory; the tables below use the repaired values."),
]
dev_ratios = pd.read_csv(ROOT / "analysis/out/machines/ratios.csv")

doc.add_heading("D. Measurements from the additional computers", level=2)
p("These runs were made by the second author on his own devices with the reduced design of Appendix E.9: 270 JVM runs "
  "(18 conditions × 3 algorithms × 5 forks) and 20 timed batches per fork, i.e. 100 measurements per row of the five-number tables. "
  "No timed batch contained a garbage collection and no warm-up hit its time limit. The raw data are in results/portable_*/.", size=9.5)
bullets([f"**{head}:** {desc}" for _, _, _, head, desc in DEVICES])

doc.add_heading("Time ratios", level=3)
p("Mean over the 5 paired forks; above 1 means WhileNeeded is faster. Confidence intervals are in "
  "analysis/out/machines/ratios.csv. Reversed input at n = 1 000 and 10 000 on the JDK 26 desktop includes the outlier JVMs of Appendix E.9.", size=9.5)
rows = []
for o in ORDERS:
    for n in DEV_SIZES:
        row = [ORDER_LABEL[o], f"{n:,}".replace(",", " ")]
        for num in ("PassPerItem", "UntilNoChange"):
            for _, label, *_ in DEVICES:
                r = dev_ratios[(dev_ratios.label == label) & (dev_ratios.order == o) & (dev_ratios["size"] == n)
                               & (dev_ratios.numerator == num) & (dev_ratios.denominator == "WhileNeeded")]
                assert len(r) == 1, (label, o, n, num)
                row.append(fmt_ratio(r.iloc[0].ratio_mean))
        rows.append(row)
cols = [d[2] for d in DEVICES]
table(["Input order", "n", f"PassPerItem ÷ WhileNeeded: {cols[0]}", cols[1], cols[2],
       f"UntilNoChange ÷ WhileNeeded: {cols[0]}", cols[1], cols[2]],
      rows, widths=[1.5, 0.5, 0.9, 0.65, 0.65, 0.95, 0.65, 0.65], size=8, align_right_from=2)

for folder, _, _, head, _ in DEVICES:
    df, _ = read_raw(ROOT / "results" / folder / "raw.csv")
    doc.add_heading(head, level=3)
    rows = []
    for o in ORDERS:
        for n in DEV_SIZES:
            for a in ALG_ORDER:
                x = df[(df.order == o) & (df["size"] == n) & (df.algorithm == a)].ns_per_sort.to_numpy()
                assert len(x) == 100, (folder, o, n, a, len(x))
                rows.append([ORDER_LABEL[o], f"{n:,}".replace(",", " "), a]
                            + [fmt_time(v) for v in np.percentile(x, [0, 25, 50, 75, 100])])
    table(["Input order", "n", "Algorithm", "Min", "Q1", "Median", "Q3", "Max"], rows,
          widths=[1.5, 0.5, 1.0, 0.7, 0.7, 0.7, 0.7, 0.7], size=8, align_right_from=3)
