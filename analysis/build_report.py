#!/usr/bin/env python3
"""Builds the report (Word document) in the structure of the course template.

Usage:  python analysis/build_report.py [OUTPUT.docx]

Every number that appears in a table or in a result sentence is read from the CSV files that
analyze_main.py / decision_metrics.py (and the follow-up analyses, if present) produced from the
raw data, so the report can be regenerated after any re-measurement.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from common import ORDER_LABEL, ORDERS, ROOT, fmt_ratio, fmt_time

SHORT = os.environ.get("REPORT_MODE", "full") == "short"   # short = the submitted report; full = supplementary material
OUT_DOCX = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "report" / ("Experiment 01 - Report.docx" if SHORT else "Supplementary material - extended report.docx")
OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
MAIN = ROOT / "analysis/out/main"
FOLLOW = ROOT / "analysis/out/followups"
REPO_URL = "https://github.com/vaizan4ikys/bubble-sort-benchmark"
ALG_ORDER = ["PassPerItem", "UntilNoChange", "WhileNeeded"]
AUTHORS = "Pavlo Harabadzhiiev and Vladyslav Nechaiev"
TITLE = "Which Bubble Sort Should Bubble Inc. Ship? A Running-Time Experiment"


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout.strip()


PREREG = git("log", "--format=%h|%aI", "--diff-filter=A", "--", "HYPOTHESES.md").splitlines()[-1].split("|")
HEAD = git("rev-parse", "--short", "HEAD")

# ------------------------------------------------------------------------------------ data
summ = pd.read_csv(MAIN / "summary_cells.csv")
pair = pd.read_csv(MAIN / "pairwise_ratios.csv")
hyp = pd.read_csv(MAIN / "hypothesis_cells.csv")
hyp_all = pd.read_csv(MAIN / "hypothesis_overall.csv")
regret = pd.read_csv(MAIN / "regret_summary.csv")
regcell = pd.read_csv(MAIN / "regret_cells.csv")
cost = pd.read_csv(MAIN / "cost_model.csv")
dq = (MAIN / "data_quality.txt").read_text()
drift = (MAIN / "drift.txt").read_text()
five_md = (MAIN / "five_number_tables.md").read_text()


def ratio(order, size, num, den):
    r = pair[(pair.order == order) & (pair["size"] == size) & (pair.numerator == num) & (pair.denominator == den)]
    return r.iloc[0]


def rr(order, size, num, den):
    r = ratio(order, size, num, den)
    return f"{fmt_ratio(r.ratio_mean)}× (95 % CI {fmt_ratio(r.ci_lo)}–{fmt_ratio(r.ci_hi)})"


def med(alg, order, size):
    r = summ[(summ.algorithm == alg) & (summ.order == order) & (summ["size"] == size)].iloc[0]
    return r.median_of_fork_medians


def sig3(x):
    """3 significant digits with thin-space thousands separators (for human readers)."""
    if x >= 1000:
        return f"{round(x, -(len(str(int(x))) - 3)):,.0f}".replace(",", " ")
    return f"{x:.2f}" if x < 100 else f"{x:.0f}"


def pretty_where(w):
    """'nearly_random n=10000' -> 'nearly sorted (random swaps), n = 10 000'."""
    order, n = w.rsplit(" n=", 1)
    return f"{ORDER_LABEL.get(order, order)}, n = " + f"{int(n):,}".replace(",", " ")


_ic = (ROOT / "analysis/out/steady_check/interference_check.txt").read_text()
_m = re.search(r"overlapping.*?: (\d+); median relative time ([\d.]+) \(other jobs ([\d.]+)\)", _ic)
N_OVER, REL_OVER, REL_OTHER = int(_m.group(1)), float(_m.group(2)), float(_m.group(3))


def tiny_ratio(g, lo, hi):
    """Ratios far below 1 as 1/N so that they stay readable."""
    th = lambda v: f"{v:,.0f}".replace(",", " ")
    return f"1/{th(1 / g)} [1/{th(1 / lo)}, 1/{th(1 / hi)}]"


def verdict_label(r):
    """Verdict under the rule of HYPOTHESES.md: one clear violation falsifies the hypothesis."""
    if r.falsified > 0:
        return f"Falsified ({r.falsified} of {r.cells} cells)" + (f"; {r.inconclusive} inconclusive" if r.inconclusive else "")
    if r.inconclusive > 0:
        return f"Not falsified; {r.inconclusive} of {r.cells} cells inconclusive"
    return "Supported"


def verdict_counts(h):
    r = hyp_all[hyp_all.hypothesis == h].iloc[0]
    return r


# ------------------------------------------------------------------------------ docx helpers
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)  # A4
doc.core_properties.author = AUTHORS
doc.core_properties.last_modified_by = AUTHORS
doc.core_properties.title = TITLE
doc.core_properties.subject = "Experimentation & Evaluation 2026 - Experiment 1"
doc.core_properties.comments = ""
sec.left_margin = sec.right_margin = Inches(1.0)
sec.top_margin = sec.bottom_margin = Inches(0.9)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(5)
st.paragraph_format.line_spacing = 1.08
for name, size in (("Heading 1", 15), ("Heading 2", 12.5), ("Heading 3", 11)):
    h = doc.styles[name]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = RGBColor(0x1F, 0x1F, 0x1F)
    h.paragraph_format.space_before = Pt(12 if name == "Heading 1" else 8)
    h.paragraph_format.space_after = Pt(4)

# page numbers in the footer
_fp = sec.footer.paragraphs[0]
_fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for _kind, _txt in (("begin", None), (None, "PAGE"), ("end", None)):
    _r = _fp.add_run()
    if _kind:
        _e = OxmlElement("w:fldChar")
        _e.set(qn("w:fldCharType"), _kind)
    else:
        _e = OxmlElement("w:instrText")
        _e.set(qn("xml:space"), "preserve")
        _e.text = _txt
    _r._r.append(_e)

FIG_NO = [0]
FIGREF = {}
TAB_NO = [0]


def p(text="", bold=False, italic=False, size=None, align=None, style=None, keep=False):
    para = doc.add_paragraph(style=style)
    add_runs(para, text, bold, italic, size)
    if align:
        para.alignment = align
    if keep:
        para.paragraph_format.keep_with_next = True
    return para


def add_runs(para, text, bold=False, italic=False, size=None):
    """Supports **bold** and *italic* inline markup."""
    for tok in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not tok:
            continue
        if tok.startswith("**"):
            r = para.add_run(tok[2:-2])
            r.bold = True
        elif tok.startswith("*"):
            r = para.add_run(tok[1:-1])
            r.italic = True
        else:
            r = para.add_run(tok)
            r.bold = bold
        if italic:
            r.italic = True
        if size:
            r.font.size = Pt(size)


def bullets(items):
    for it in items:
        para = doc.add_paragraph(style="List Bullet")
        add_runs(para, it)
        para.paragraph_format.space_after = Pt(2)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def table(header, rows, widths=None, caption=None, size=8.5, align_right_from=None):
    if caption:
        TAB_NO[0] += 1
        cp = p(f"**Table {TAB_NO[0]}.** {caption}", size=9, keep=True)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        add_runs(c.paragraphs[0], f"**{h}**", size=size)
        shade(c, "E8E8E4")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            add_runs(cells[i].paragraphs[0], str(v), size=size)
            if align_right_from is not None and i >= align_right_from:
                cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in t.rows:
        for c in r.cells:
            for para in c.paragraphs:
                para.paragraph_format.space_after = Pt(0)
    if widths:
        for r in t.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Inches(w)
    # repeat the header row on every page
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figure(path, caption, width=6.4):
    path = Path(path)
    if not path.exists():
        p(f"[missing figure: {path.name}]", italic=True)
        return
    FIG_NO[0] += 1
    FIGREF[path.name] = FIG_NO[0]
    doc.add_picture(str(path), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    p(f"**Figure {FIG_NO[0]}.** {caption}", size=9, align=WD_ALIGN_PARAGRAPH.LEFT)


# =========================================================================== title + abstract
tp = p(TITLE if SHORT else "Supplementary material: " + TITLE, bold=True, size=19 if SHORT else 16, align=WD_ALIGN_PARAGRAPH.LEFT)
tp.paragraph_format.space_after = Pt(2)
p(AUTHORS, size=11.5)
p("Experiment 1, Experimentation & Evaluation 2026 · Università della Svizzera italiana", italic=True, size=9.5)
if SHORT:
    st.font.size = Pt(10)
    sec.left_margin = sec.right_margin = Inches(0.95)
    sec.top_margin = sec.bottom_margin = Inches(0.8)
    exec((ROOT / "analysis" / "report_short.py").read_text())
    doc.save(OUT_DOCX)
    print("written", OUT_DOCX)
    sys.exit(0)
p("This is the extended version of the report (all follow-up experiments, all five-number tables, the experiments on other computers). The submitted report is the shorter file “Experiment 01 - Report.docx”, which cites this file as S-… (S-C = Appendix C, and so on).", italic=True, size=9)

doc.add_heading("Abstract", level=1)
ABSTRACT = (ROOT / "analysis" / "abstract.txt").read_text().strip() if (ROOT / "analysis" / "abstract.txt").exists() else ""
p(ABSTRACT)
print("abstract words:", len(ABSTRACT.split()))

# ============================================================================== 1 Introduction
doc.add_heading("1. Introduction", level=1)
p("Bubble sort is the textbook example of a simple but slow sorting algorithm, yet it is still shipped "
  "in teaching libraries, embedded code and small utilities because it is short, stable and sorts in place. "
  "The company *Bubble Inc.* wants to ship one bubble-sort implementation in its Java library. Three "
  "candidates exist. They are all correct and differ only in when they stop: **PassPerItem** always makes "
  "n passes over the array, **UntilNoChange** stops after the first pass in which nothing was swapped, and "
  "**WhileNeeded** also stops early and, in addition, shortens every pass to the position of the last swap "
  "of the previous pass. Reading the code suggests an ordering (WhileNeeded ≤ UntilNoChange ≤ PassPerItem in the "
  "number of comparisons), but running time on a real JVM also depends on branch prediction, memory access and "
  "the just-in-time (JIT) compiler. The customer-facing question – *which implementation is fastest?* – "
  "therefore needs measurements, not only code reading. A wrong choice can be expensive: when the input is "
  "already sorted, an implementation that never stops early is thousands of times slower than one that does.")
p("The only decision criterion is running time. We designed a controlled, full-factorial experiment: the three algorithms sort identical data in six input orders and six sizes (100 to 20 000 elements), "
  "each condition in 10 fresh JVMs after a warm-up, with the hypotheses committed to git before any measurement. Follow-up experiments (appendices) test whether the recommendation survives other garbage collectors, "
  "Java versions, element types, tiny arrays, cold starts, another benchmark harness (JMH) and other computers.")

doc.add_heading("Hypotheses", level=2)
p(f"The hypotheses below were committed to the repository (file HYPOTHESES.md, commit {PREREG[0]}, "
  f"{PREREG[1][:19].replace('T', ' ')} local time) before the benchmark harness was committed and before any main-experiment data "
  "was collected; a first, uncommitted version of the harness was used for a short pilot a minute later (Section 2.4). The times are local git commit times; the repository was first pushed to GitHub, at about 02:44, after the main run. "
  "Table 1 restates them with the null hypothesis written out; the conditions and thresholds are exactly those of HYPOTHESES.md, "
  "which has only one commit and was never edited. In all of them the independent variables are *algorithm*, "
  "*input order* and *input size n* (as named per hypothesis), and the dependent variable is the *running "
  "time of one call to sort* (nanoseconds, ratio scale). \"Median time\" always means the median over the "
  "medians of the 10 JVM forks of a condition.")
HYP_TXT = [
    ("H1 (sorted input)", "For n ≥ 1 000, on sorted input the median time of PassPerItem is at least 100× that of "
     "UntilNoChange and at least 100× that of WhileNeeded.",
     "H0: the ratio is below 100 for at least one of the two comparisons. IV: algorithm; DV: running time."),
    ("H2 (random input)", "For n ≥ 5 000, on random input WhileNeeded has the lowest median running time of the three "
     "algorithms, while UntilNoChange and PassPerItem differ from each other by less than 15 %.",
     "H0: WhileNeeded is not the fastest, or UntilNoChange and PassPerItem differ by 15 % or more. IV: algorithm; DV: running time."),
    ("H3 (reversed input)", "For n ≥ 5 000, on reversed input WhileNeeded is at least 10 % faster than both "
     "UntilNoChange and PassPerItem.", "H0: WhileNeeded is less than 10 % faster than at least one of them. IV: algorithm; DV: running time."),
    ("H4 (locally disturbed input)", "For n ≥ 5 000, on nearly sorted input with local swaps, both UntilNoChange and "
     "WhileNeeded are at least 10× faster than PassPerItem.", "H0: at least one of the two is less than 10× faster. IV: algorithm; DV: running time."),
    ("H5 (growth with n)", "On random input, doubling n from 10 000 to 20 000 multiplies the median time of every "
     "algorithm by a factor between 3.3 and 4.7 (quadratic growth). On sorted input the factor is below 2.6 for "
     "UntilNoChange and WhileNeeded (linear growth) and between 3.3 and 4.7 for PassPerItem.",
     "H0: at least one factor lies outside the stated range. IV: input size and algorithm; DV: running time."),
    ("H6 (recommendation)", "In no combination of input order and size n ≥ 1 000 is WhileNeeded more than 5 % slower than "
     "UntilNoChange or PassPerItem. If this holds, WhileNeeded is recommended.",
     "H0: in at least one such combination WhileNeeded is more than 5 % slower than another algorithm. IV: algorithm, input order, input size; DV: running time."),
]
table(["Hypothesis", "Statement (alternative hypothesis)", "Null hypothesis / variables"],
      [[a, b, c] for a, b, c in HYP_TXT], widths=[1.15, 3.35, 2.0],
      caption="Pre-registered hypotheses. Each is falsifiable: it names a numeric threshold, and a condition whose "
              "95 % confidence interval lies entirely on the wrong side of that threshold counts as a falsification. "
              "Under the rule registered in HYPOTHESES.md a single clear violation falsifies a hypothesis.")

# ==================================================================================== 2 Method
doc.add_heading("2. Method", level=1)
doc.add_heading("2.1 Variables", level=2)
p("**Independent variables** (manipulated by us; each level was combined with every level of the other two):", keep=True)
table(["Independent variable", "Levels"], [
    ["Algorithm (3)", "PassPerItem · UntilNoChange · WhileNeeded (the three provided Java classes, unmodified)"],
    ["Input order (6)", "random · sorted · reversed · nearly sorted with local swaps (5 % of the elements swapped with a "
                        "neighbour at most 10 positions away) · nearly sorted with random swaps (n/20 random pairs "
                        "swapped) · few unique values (random draws from 10 values)"],
    ["Input size n (6)", "100 · 1 000 · 2 000 · 5 000 · 10 000 · 20 000 elements"],
], widths=[1.6, 4.9])
p("**Dependent variable** (what we measure):", keep=True)
table(["Dependent variable", "Measurement", "Scale"], [
    ["Running time of one call of sort()", "Wall-clock time from System.nanoTime(), measured for a batch of "
     "consecutive sorts on private copies of the input and divided by the batch size. Copying and the "
     "sortedness check are outside the timed region.", "Ratio scale, nanoseconds per sort"],
], widths=[1.6, 3.7, 1.2])
p("**Control variables** (kept constant):", keep=True)
table(["Control variable", "Fixed value"], [
    ["Input data", "Identical arrays for all three algorithms (same seed for a given order, n and fork; the "
                   "algorithm is not part of the seed). Elements are boxed Integer objects, allocated in array order (values from −128 to 127 are shared, cached Integer objects, which concerns the few-unique arrays and some of the n = 100 arrays)."],
    ["Machine and Java", "One laptop (Apple M3 Pro), OpenJDK 26.0.1, AC power, lid open, heavy applications closed by the user; "
                         "JVM flags -Xms2g -Xmx2g -XX:+UseSerialGC."],
    ["JIT / JVM state", "One algorithm per JVM process, so that the call to compareTo is not influenced by other "
                        "sorting code; every measurement starts in a fresh JVM, after a warm-up phase."],
    ["Garbage collection", "Heap pre-sized so that no collection happens during timed batches; each batch is checked "
                           "for collections and flagged if one occurs."],
    ["Run order", "All 1 080 JVM runs executed in one session in a random order (fixed seed 20261104), so that slow "
                  "drifts of the machine are not confounded with an algorithm or a size."],
], widths=[1.6, 4.9])

doc.add_heading("2.2 Design", level=2)
p("Type of study (check one):   ☐ Observational Study    ☐ Quasi-Experiment    ☒ Experiment", size=10.5)
p("Number of factors (check one):   ☐ Single-Factor Design    ☒ Multi-Factor Design    ☐ Other", size=10.5)
p("This is a true **experiment**: we manipulate the independent variables ourselves and assign the conditions "
  "without any pre-existing grouping. It is a **multi-factor, full-factorial design** with three factors "
  "(algorithm × input order × input size, 3 × 6 × 6 = 108 conditions, called cells). "
  "It is a **repeated-measures (within-subjects) design**: the \"participants\" are the random data sets, and the "
  "same data set (identified by its fork number) is sorted by all three algorithms, so that comparisons between "
  "algorithms are paired and differences between data sets cancel out. In the language of the lectures, the "
  "repeated-measures design raises the sensitivity of the comparison, but it brings the risk of order effects "
  "(a later measurement is influenced by an earlier one). We control order effects in three ways: every "
  "measurement runs in its own fresh JVM, so nothing carries over from one measurement to the next; the order "
  "of the 1 080 JVM runs is randomised; and we check for slow drift of the machine afterwards (Section 3.1). "
  "Each condition is replicated with 10 independent JVMs (forks) and 30 timed batches per JVM, i.e. 300 "
  "observations per cell and 32 400 in total. Because the JVM state is not stable from one fork to the next "
  "(JIT decisions can differ), the unit of analysis for inference is the median of one fork, not the individual "
  "batch (batches within a JVM are not independent).")
figure(ROOT / "analysis/out/main/fig_design.png",
       "Design of the experiment: three crossed factors (3 × 6 × 6 cells), 10 forks per cell, 30 timed batches per fork; "
       "the three algorithms are measured on the same inputs.", width=6.3)

doc.add_heading("2.3 Apparatus and Materials", level=2)
env = (ROOT / "results/full/environment.txt").read_text() if (ROOT / "results/full/environment.txt").exists() else ""
p("**Hardware and system.** Apple MacBook with an Apple M3 Pro (11 cores, 18 GB RAM), macOS 26.7.1 (MacBook Pro, model Mac15,6; "
  "the 11 cores are 5 performance and 6 efficiency cores, and macOS does not allow pinning a process to a core), connected to "
  "AC power (recorded at the start: battery at 67 % and charging; battery level is a time threat in laptop benchmarks), "
  "lid open, screen on, heavy applications closed. We prevented sleep with caffeinate. The full environment "
  "record is stored with the data (results/full/environment.txt). Clock frequency and temperature were not recorded.")
REQS = dict(l.split("==") for l in (ROOT / "requirements.txt").read_text().split() if "==" in l)
p("**Software.** Main experiment: OpenJDK 26.0.1, Homebrew build (https://formulae.brew.sh/formula/openjdk), with the code compiled by the same JDK. "
  "Follow-up runs: Homebrew openjdk@17 (17.0.19) and openjdk@21 (21.0.11), Amazon Corretto 8 (1.8.0_482, https://aws.amazon.com/corretto), "
  "Eclipse Temurin 25.0.5 and, on the desktop, Temurin 17.0.21 and 26.0.2.1 (https://adoptium.net); JMH 1.37 (https://github.com/openjdk/jmh) built with Maven. "
  f"Analysis: Python 3 with pandas {REQS['pandas']} (3.1.0 in the first author's environment, which gives the same outputs), NumPy {REQS['numpy']}, SciPy {REQS['scipy']}, matplotlib {REQS['matplotlib']} and python-docx {REQS['python-docx']} "
  "(pinned in requirements.txt). The three sorting classes and the interface Sorter come from the assignment and "
  "were not modified (byte-identical copies in src/exp01). Our own code: InputGenerator (deterministic data), Worker "
  "(the measuring program; SteadyWorker is a variant with a longer warm-up of the batch loop, used in Section 3.7), run_experiment.py (orchestrator, one JVM per job), and the analysis scripts. All code "
  f"and data are public: {REPO_URL}.")
p("**How time is measured.** Inside the JVM with System.nanoTime(). Sorting an array of 100 elements takes only "
  "microseconds, which is too short to time one call reliably. We therefore time a *batch* of sorts and divide: "
  "the batch size is calibrated so that a batch lasts about 2 ms (between 1 and 20 000 sorts per batch). The arrays "
  "of a batch are private copies created before the timer starts.")

doc.add_heading("2.4 Procedure", level=2)
p("One experimental run (a *job*) is one JVM process for one (algorithm, order, size, fork) combination:", keep=True)
bullets([
    "The orchestrator starts a fresh JVM (java -Xms2g -Xmx2g -XX:+UseSerialGC exp01.Worker …). The worker generates the input "
    "array from (order, n, seed, fork) and creates the one sorter under test.",
    "**Warm-up.** The worker sorts fresh copies of the input until at least 20 sorts and 1.5 s have passed and the median "
    "of the five most recent sorts is within 5 % of the five before (i.e. the JIT compiler has settled), with a limit of 40 s. "
    "For very short sorts (< 100 µs) the time criterion alone ends the warm-up.",
    "**Calibration.** From the warm-up speed, the batch size is chosen so that one batch lasts about 2 ms.",
    "**Measurement.** Two untimed batches, then 30 times: create the batch of array copies (not timed); start the clock; sort all arrays; stop the "
    "clock; check (not timed) that each array is sorted; note whether a garbage collection happened in the timed region. "
    "The job is aborted with an error if any result is not sorted.",
    "The worker prints one CSV line per batch. The orchestrator appends them to raw.csv, runs the 1 080 jobs in "
    "randomised order (seed 20261104) and can resume after an interruption.",
])
p(f"The whole main experiment took 77 minutes (01:25–02:43 on 4 November 2026). It was started and supervised by the AI assistant (Claude Code) on the first author's laptop, "
  "at the first author's request, after the first author had closed other heavy applications. "
  "While it ran, the assistant made four short git commits (01:30–01:42, among them the follow-up scripts and the re-measurement rule) and a few low-priority smoke tests, "
  f"all listed in results/full/interference_log.txt; the {N_OVER} jobs that overlapped with them (approximate windows) have a median relative time of {REL_OVER:.3f}, the other jobs {REL_OTHER:.3f} (Section 3.1). "
  "Because the same ten fork numbers (0–9) are used for all three algorithms, each fork index defines one data set shared by the three algorithms.")
p("**Pilot.** Between the commit of the hypotheses (01:16:35) and the start of the main run (01:25:20) we ran a short pilot (01:17–01:20, results/pilot/: 108 jobs = 3 algorithms × 6 input orders × n ∈ {100, 1 000, 5 000} × 2 forks, 10 timed batches each), "
  "using an early, not yet committed version of the harness (committed at 01:20:59), to test the harness and to choose the warm-up and batch parameters. The pilot already suggested that "
  "UntilNoChange is slower than PassPerItem on random input and that WhileNeeded is slower than PassPerItem on reversed input, i.e. that some of our hypotheses might fail. "
  "We did not change the hypotheses (HYPOTHESES.md has a single commit), and no result in this report is based on the pilot data.")
p("**Statistics.** Per cell, we compute the five-number summary of all 300 batch measurements. For inference we "
  "use the 10 fork medians: 95 % confidence intervals from the t distribution (N = 10 is small, so t rather than z), "
  "ratios between algorithms as the mean of the 10 paired per-fork ratios with the same kind of interval, "
  "and growth factors t(20 000)/t(10 000) as the ratio of the two means, with the conservative interval lower limit at 20 000 ÷ upper limit at 10 000 (and vice versa). A hypothesis cell is *supported* when the "
  "whole confidence interval satisfies the threshold, *falsified* when the whole interval lies on the wrong side, "
  "and *inconclusive* otherwise; by the rule of HYPOTHESES.md a hypothesis is falsified as soon as one of its cells is, so we report \"falsified (k of m cells)\". "
  "The code that computes these intervals and verdicts (analysis/common.py and analyze_main.py) was committed at 01:34 (c7b3506), before the main data were analysed; that code used geometric means of the ratios (t interval on the log scale) and a Welch interval for growth factors. Because these methods were not taught in the course, we replaced them afterwards by the interval of lecture 7 (mean ± t · standard error); "
  "this changed the verdicts of H5 (falsified → inconclusive in the main data), H6 (one inconclusive cell → falsified) and none of the others. "
  "**Re-measurement rule (pre-registered at 01:36, during the main run and before any of its data were analysed):** a group (order, size ≥ 1 000) is "
  "re-measured with 20 additional forks per algorithm if the between-fork variation is above 5 %, the CI half-width is above "
  "3 %, a garbage collection occurred, the warm-up timed out, or any hypothesis cell is inconclusive.")
p("**Use of AI.** The course allows the use of AI assistants. We used an AI assistant (Claude, via Claude Code) to help design the experiment, write the "
  "measuring and analysis code, run the main experiment and draft this report; the second author used his own assistant session for the runs on his computers and parts of the text. "
  "The authors reviewed the design, the code, the numbers and the text.")

# ==================================================================================== 3 Results
doc.add_heading("3. Results", level=1)
p("**Results in brief** (details and caveats in the sections named):", keep=True)
bullets([
    "*Sorted input:* PassPerItem is at least 970× slower than the two early-stopping algorithms (about 2 200× or more in the steady state); *locally disturbed input:* 199–794× slower (n ≥ 5 000). Section 3.3.",
    "*Random input:* WhileNeeded needs 57–76 % of PassPerItem's time; UntilNoChange is 9–26 % *slower* than PassPerItem (n ≥ 5 000). Section 3.3.",
    "*Reversed input:* WhileNeeded is 7–12 % slower than PassPerItem (up to 16 % in the steady state), but only in the main setting (JDK 26.0.1 on the main laptop); other JDKs and computers do not show it (Appendix E). Section 3.3.",
    "*Over the 30 conditions with n ≥ 1 000* WhileNeeded is the fastest algorithm in 24 (25 in the steady state); its worst slowdown against the best is 1.16× in the steady state. Section 3.5.",
    "*Hypotheses:* H1 and H4 supported; H2, H3 and H6 falsified (in 1 to 6 of their cells); H5 inconclusive (1 cell). Section 3.6.",
    "*Quality problem:* for very short sorts the speed changed inside some JVM runs. A steady-state re-measurement leaves all verdicts unchanged, but main-data times in some cells are up to 2× too high. Section 3.7.",
])
doc.add_heading("3.1 Visual Overview", level=2)
p("**Data quality.** All 1 080 jobs completed without errors and every sorted result was verified. "
  "The data set contains 32 400 batch measurements (108 cells × 10 forks × 30 batches). No timed batch contained a garbage "
  "collection and no warm-up hit its time limit. Time per sort ranges from 25 ns (sorting a sorted array of 100 elements) to "
  "0.52 s (20 000 elements). One quality problem was found afterwards: for some very short sorts the speed changed inside a JVM during the 30 timed batches (Section 3.7).")
figure(MAIN / "fig_scaling.png",
       "Median running time of one sort (µs, log–log axes) against input size, one panel per input order. Markers are "
       "the measured sizes; the shaded band is the 95 % CI over forks (mostly narrower than the markers); dotted grey lines "
       "show n and n² growth for reference. Log scales are used because sizes and times span several orders of magnitude.")
figure(MAIN / "fig_boxplots.png",
       "Distribution of the measured time per sort (all 300 batch measurements per box; logarithmic axis) for every input size, by input order "
       "and algorithm. Box = interquartile range, line = median, whiskers = 1.5 × IQR, points = outliers. Most boxes are very narrow because repeated measurements agree closely; "
       "the wide boxes (sorted, n = 1 000 and 20 000) are level shifts inside a JVM (Section 3.7).")
figure(MAIN / "fig_ratio_heatmaps.png",
       "Time of one algorithm relative to another (mean over forks of the paired per-fork ratios). Values below 1 mean "
       "the first-named algorithm is faster. Cells with n < 1 000 are descriptive only.")
figure(MAIN / "fig_ecdf.png",
       "Empirical cumulative distribution functions of the time per sort for n = 10 000 on random, reversed and nearly sorted (random swaps) input. "
       "A curve further to the left is faster; a steep curve means repeatable timings.")

figure(MAIN / "fig_drift.png", "Check for slow drift of the machine during the 77-minute session: relative time of each job (to its cell median) in execution order, with rolling median.")
dl = drift.strip().splitlines()
p("Drift check: " + dl[0].replace("rho", "ρ") + ". The rolling median of the relative time stays within "
  + dl[1].split(":")[1].strip().replace("..", "to") + f" of the cell median (Figure {FIG_NO[0]}), so the drift is statistically detectable but tiny (later jobs were about 0.1–0.3 % faster): far smaller than "
  f"the differences between algorithms. The {N_OVER} jobs that overlapped with logged activity of the assistant (smoke tests, git commits; results/full/interference_log.txt) "
  f"have a median relative time of {REL_OVER:.3f}, the other jobs {REL_OTHER:.3f}, so these short checks did not leave a visible trace.")

doc.add_heading("3.2 Descriptive Statistics", level=2)
p("For each of the 108 conditions we summarise the 300 measurements with the **five-number summary**: the *minimum* is the "
  "fastest batch observed; the *first quartile (Q1)* is the value below which the fastest quarter of the batches lies; the "
  "*median* is the middle value – half of the batches were faster, half slower; the *third quartile (Q3)* is the value below "
  "which three quarters of the batches lie; the *maximum* is the slowest batch. The distance Q3 − Q1 (the interquartile range) "
  "shows how much the measurements vary: a narrow range means the timing is repeatable. Table 2 gives the summary for n = 10 000; the "
  "tables for all sizes are in Appendix C. Times are per call of sort(), in the unit shown.")
rows = []
for o in ORDERS:
    for a in ("PassPerItem", "UntilNoChange", "WhileNeeded"):
        r = summ[(summ.algorithm == a) & (summ.order == o) & (summ["size"] == 10000)].iloc[0]
        rows.append([ORDER_LABEL[o], a, fmt_time(r["min"]), fmt_time(r.q1), fmt_time(r["median"]), fmt_time(r.q3), fmt_time(r["max"])])
table(["Input order", "Algorithm", "Min", "Q1", "Median", "Q3", "Max"], rows,
      widths=[1.6, 1.25, 0.75, 0.75, 0.75, 0.75, 0.75], align_right_from=2,
      caption="Five-number summary of the time per sort, n = 10 000 (300 measurements per row). For sorted input the rows of the two early-stopping algorithms are about twice the steady-state values (Section 3.7).")
p("The median over forks, the 95 % confidence intervals and the between-fork variation per condition are in the file "
  "analysis/out/main/summary_cells.csv.")

doc.add_heading("3.3 Comparing the algorithms", level=2)
p("Table 3 gives the paired ratio of the running times for the most informative sizes. Values below 1 mean that the "
  "first-named algorithm needs less time.")
rows = []
for o in ORDERS:
    for n in (1000, 5000, 20000):
        a = ratio(o, n, "UntilNoChange", "PassPerItem")
        b = ratio(o, n, "WhileNeeded", "PassPerItem")
        c = ratio(o, n, "WhileNeeded", "UntilNoChange")
        def f(r):
            if r.ratio_mean < 0.01:
                return tiny_ratio(r.ratio_mean, r.ci_lo, r.ci_hi)
            if r.ratio_mean < 0.1:
                return f"{r.ratio_mean:.3f} [{r.ci_lo:.3f}, {r.ci_hi:.3f}]"
            return f"{fmt_ratio(r.ratio_mean)} [{fmt_ratio(r.ci_lo)}, {fmt_ratio(r.ci_hi)}]"
        rows.append([ORDER_LABEL[o], f"{n:,}".replace(",", " "), f(a), f(b), f(c)])
table(["Input order", "n", "UntilNoChange ÷ PassPerItem", "WhileNeeded ÷ PassPerItem", "WhileNeeded ÷ UntilNoChange"],
      rows, widths=[1.55, 0.6, 1.5, 1.5, 1.5], size=8,
      caption="Time ratios (mean over the 10 paired forks) with 95 % confidence interval in brackets; ratios below 0.01 are written as 1/N, e.g. 1/970 means 970 times faster. For sorted input, the ratio WhileNeeded ÷ UntilNoChange is affected by level shifts and is about 0.98 in the steady state (Section 3.7).")

doc.add_heading("3.4 Operation counts", level=2)
p("To relate time to the work performed, an instrumented copy of the algorithms counted the comparisons (calls to compareTo) and the inversions "
  "(= swaps, identical for all three algorithms) for every cell (results/operation_counts.csv; Figure 7 shows n = 10 000).")
figure(MAIN / "fig_operations.png", "Number of comparisons (bars, as a fraction of n²) and of swaps (diamonds) per algorithm and input order for n = 10 000.")

doc.add_heading("3.5 Decision metric: worst-case slowdown", level=2)
p("For the recommendation, we compare every algorithm with the fastest one in each condition. The *slowdown* of an algorithm in "
  "a cell is its median time divided by the smallest median time of the three algorithms in that cell (1.00 = fastest). Table 4 "
  "summarises the 30 cells with n ≥ 1 000.")
rows = []
for r in regret.itertuples():
    rows.append([r.algorithm, f"{r.cells_fastest} / {r.cells}", f"{r.cells_within_5pct_of_best} / {r.cells}",
                 f"{r.geomean_regret:.2f}", sig3(r.max_regret), pretty_where(r.max_regret_where)])
table(["Algorithm", "Fastest in", "Within 5 % of best", "Geometric-mean slowdown", "Worst slowdown", "Where"], rows,
      widths=[1.3, 0.85, 1.0, 1.1, 0.9, 1.35], size=8.5, caption="Slowdown relative to the fastest algorithm per cell (n ≥ 1 000), from the medians of all 30 batches. Section 3.7 repeats this analysis for the steady state.")
figure(MAIN / "fig_regret.png", "Worst slowdown relative to the best algorithm per input order (n ≥ 1 000; logarithmic axis, 1 = best).", width=6.0)

# Hypothesis table
doc.add_heading("3.6 Hypothesis checks", level=2)
rows = []
for r in hyp_all.itertuples():
    rows.append([r.hypothesis, verdict_label(r), r.supported, r.falsified, r.inconclusive])
table(["Hypothesis", "Verdict under the registered rule", "Cells supported", "Cells falsified", "Cells inconclusive"], rows,
      widths=[1.0, 2.2, 1.0, 1.0, 1.1], caption="Verdicts of the pre-registered hypotheses based on the main data (before re-measurement; Section 3.7 and Appendix F give the sensitivity analyses).")

# 3.7 level shifts / steady-state check and 3.8 summary of the follow-ups
exec((ROOT / "analysis" / "report_steady.py").read_text())

# ================================================================================ 4 Discussion
doc.add_heading("4. Discussion", level=1)
disc = ROOT / "analysis" / "report_discussion.py"
if disc.exists():
    exec(disc.read_text())
else:
    p("[Discussion not yet written]")

# ================================================================================== Appendix
doc.add_heading("Appendix", level=1)
doc.add_heading("A. Materials", level=2)
p("The three algorithms under test are the classes provided with the assignment, used unmodified (src/exp01/BubbleSortPassPerItem.java, "
  "BubbleSortUntilNoChange.java, BubbleSortWhileNeeded.java, interface Sorter.java). No informed-consent documents were needed because there "
  "were no human participants.")
doc.add_heading("B. Reproduction Package", level=2)
p(f"Everything needed to recreate every number, table and figure of this report is in the public repository **{REPO_URL}** "
  f"(data, analysis and report scripts as of commit {HEAD}): the raw measurements (results/full/raw.csv: one line per timed batch, 32 400 lines), the "
  "environment records, the operation counts, the code of the harness, the orchestration and analysis scripts, the pre-registered hypotheses "
  "(HYPOTHESES.md) and the pre-registered re-measurement rule (REMEASURE_RULE.md). To reproduce: build with javac, run "
  "scripts/run_experiment.py and the follow-up scripts, then the analysis scripts in the order given in README.md.")
bullets([
    "results/full/ – main experiment (raw.csv, run.log, environment.txt, interference_log.txt)",
    "results/remeasure/ – the 20 additional forks of the 10 uncertain groups (Appendix F)",
    "results/steady/ – the steady-state re-measurement of the full design (Section 3.7)",
    "results/ext_*/ – follow-up experiments, each with its own raw.csv and environment.txt",
    "results/portable_*/ – the reduced design on two other computers (run by the second author)",
    "results/pilot/ – pilot run made before the main experiment with a not yet committed version of the harness, used only to choose the parameters; results/pilot_ext/ – short smoke test of ExtendedWorker made during the main run (see results/full/interference_log.txt)",
    "analysis/out/ – all derived tables and figures of this report",
])
doc.add_heading("C. Five-number summaries of all conditions", level=2)
p("Minimum, first quartile, median, third quartile and maximum of the 300 measurements per condition (per call of sort()).", size=9.5)
for block in five_md.split("### ")[1:]:
    title, *lines = block.strip().splitlines()
    doc.add_heading(ORDER_LABEL.get(title.strip(), title), level=3)
    tab = [ln for ln in lines if ln.startswith("|")]
    header = [c.strip() for c in tab[0].strip("|").split("|")]
    body = [[c.strip() for c in ln.strip("|").split("|")] for ln in tab[2:]]
    table(header, body, widths=[0.6, 1.4, 0.9, 0.9, 0.9, 0.9, 0.9], size=8, align_right_from=2)

exec((ROOT / "analysis" / "report_appendix_devices.py").read_text())

# Appendix E (follow-up experiments) and F (re-measurement)
exec((ROOT / "analysis" / "report_followups.py").read_text())

doc.save(OUT_DOCX)
print("written", OUT_DOCX)
