# Bubble Sort Benchmark

Reproduction package for *Experiment 1* of **Experimentation & Evaluation 2026** (Prof. G. Bavota, G. Crupi):
which of three Java bubble-sort implementations should *Bubble Inc.* ship in its library?
The only criterion is running time.

Authors: Pavlo Harabadzhiiev, Vladyslav Nechaiev.
The work was done with the help of an AI assistant (Claude Code), which is allowed by the course.

| Candidate | Idea |
|---|---|
| `BubbleSortPassPerItem` | always `n` passes of `n-1` comparisons |
| `BubbleSortUntilNoChange` | stops after the first pass without a swap |
| `BubbleSortWhileNeeded` | stops early *and* shrinks every pass to the position of the last swap |

The three sorters in `src/exp01/` are the files provided with the assignment, **unchanged**.

## Experiment in one paragraph

A full-factorial, repeated-measures design: **3 algorithms x 6 input orders x 6 input sizes** (108 cells).
Every cell is measured in 10 *forks* (a fork is a fresh JVM); each fork warms up the JIT compiler, then times
30 batches of sorts (batching makes sub-microsecond sorts measurable) and verifies, outside the timed region,
that every result is sorted. All three algorithms receive exactly the same input data within a fork index, and the
order of the 1 080 jobs is shuffled with a fixed seed. The pre-registered hypotheses are in
[`HYPOTHESES.md`](HYPOTHESES.md) (committed before any code or data existed).

## Layout

```
HYPOTHESES.md             hypotheses, committed before the experiment
src/exp01/                the three sorters + Sorter (given), and our code:
  InputGenerator.java       deterministic input generation (6 orders)
  Worker.java               one fork of the main experiment (Integer elements)
  ExtendedWorker.java       same procedure for the follow-ups (String elements)
  OperationCounter.java     counts comparisons / inversions (not timed)
scripts/
  run_experiment.py         orchestrator (shuffled, resumable, one JVM per job)
  run_followups.sh          queue of all follow-up experiments
  capture_environment.sh    records hardware / software / power state
analysis/
  analyze_main.py           tables, hypothesis checks, figures for the main data
  analyze_followups.py      same for the follow-up experiments
  build_report.py           assembles the Word report from the analysis outputs
results/
  full/                     MAIN experiment: raw.csv, run.log, environment.txt, ...
  ext_string/ ext_c1/ ext_interp/ ext_scaling/ replication/ ext_noload/ ext_load/
  operation_counts.csv      comparisons and inversions per algorithm / order / size
analysis/out/               all generated tables and figures
```

## Reproduce

Requirements: a JDK (we used OpenJDK 26.0.1), Python 3 with `numpy pandas scipy matplotlib python-docx`.

```sh
javac -d bin src/exp01/*.java
cp -r bin bin_ext                                   # (follow-ups use a separate copy of the classes)
java -cp bin exp01.OperationCounter results/operation_counts.csv

# main experiment (about 2 hours; close other applications, keep the laptop on AC power)
scripts/capture_environment.sh results/full/environment.txt
python3 scripts/run_experiment.py --out results/full --forks 10 --iters 30

# follow-ups (several hours)
scripts/run_followups.sh

# analysis
python3 analysis/analyze_main.py
python3 analysis/analyze_followups.py
python3 analysis/build_report.py
```

`results/*/raw.csv` columns: `seq` (position in the shuffled job order), `algorithm`, `order`, `size`, `fork`,
`iter` (timed batch), `batch` (number of sorts in the batch), `ns_per_sort` (batch time / batch size),
`gc_during` (a garbage collection happened inside the timed region), `warmup_sorts`, `warmup_timeout`.
Follow-ups that use `ExtendedWorker` have an additional `type` column.

## Measurement procedure (per fork)

1. Generate the input from `(base seed, order, size, fork)`.
2. Warm-up: sort fresh copies one at a time until at least 20 sorts and 1.5 s have passed and the median time has
   stabilised (<5 % change) - tiny sorts only need the minimum time.
3. Calibrate a batch size B so that one timed batch takes about 2 ms.
4. Two untimed batches, then 30 timed batches. Per batch: copy B arrays (untimed), time `sort` on all of them,
   verify they are sorted (untimed). Recorded value: batch time / B.
5. JVM flags: `-Xms2g -Xmx2g -XX:+UseSerialGC` (no concurrent GC threads, fixed heap).
