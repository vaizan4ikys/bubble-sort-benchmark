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

## To do: Pavlo (temporary, delete this section before submitting)

Report deadline: **10 November 2026, 18:00**. Please do this on `main`, and tell Vlad when it is done.

**Why:** `results/ext_jdk25/environment.txt` shows that the "JDK 25" run actually used **JDK 26.0.1**, because
`/opt/homebrew/opt/openjdk@25` pointed to JDK 26 on your Mac. Its reversed-input ratio (PassPerItem / WhileNeeded) is
0.91-0.94, the same as the main data. A real JDK 25.0.1 on Vlad's Mac gives 1.42-1.47, with WhileNeeded fastest. So the
report's claim that the anomaly is "specific to JDK 25/26" is not supported yet.

1. **[OPEN] Measure a real JDK 25 on your Mac (about 10 minutes).** Your Mac matters here: only the Java version should change
   compared with the main data. Install JDK 25 (for example the Temurin package from https://adoptium.net), plug in the
   laptop and close other applications. Then run the commands below. The first one must print version 25; otherwise stop.
   Change the path in `J=` if your JDK is elsewhere.

   ```sh
   git switch main && git pull
   J=/Library/Java/JavaVirtualMachines/temurin-25.jdk/Contents/Home/bin/java
   "$J" -version
   "$(dirname "$J")/javac" -d bin_jdk25 src/exp01/*.java
   mkdir -p results/ext_jdk25_real
   scripts/capture_environment.sh results/ext_jdk25_real/environment.txt
   { echo "--- java used by this experiment ($J)"; "$J" -version 2>&1; } >> results/ext_jdk25_real/environment.txt
   caffeinate -dims python3 scripts/run_experiment.py --out results/ext_jdk25_real --classes bin_jdk25 --types Integer \
     --java "$J" --orders random sorted reversed nearly_local nearly_random few_unique \
     --sizes 1000 5000 10000 --forks 5 --iters 20
   git add results/ext_jdk25_real
   git commit -m "Follow-up: JDK 25 re-measured with a real JDK 25"
   git pull --rebase && git push
   ```

   Do not delete or overwrite `results/ext_jdk25/`: it stays as a repeat of JDK 26 and will be relabelled.
2. **[DONE 5 Nov] Pilot data.** If you still have `results/pilot/`, add it to the repository: it is in `.gitignore`, and the template
   asks to keep all raw data, including data collected before the experiment. Tell Vlad if it no longer exists.
3. **[DONE 5 Nov: in report section 2.4 and results/full/interference_log.txt] Tell Vlad what ran during the main experiment (01:25-02:43).** The report says no other user programs were running,
   but commits were made at 01:30-01:42. Also confirm that you started that run: section 2.4 has to say who did.
4. **[DONE 5 Nov, report updated; the JDK 25 sentence is added automatically once item 1 is done] Review the planned change of conclusion.** The abstract and sections 3.7.2, 4.1 (H3), 4.2 and 4.3 will no longer say
   "JDK 25/26". Please do not edit the report in the meantime, to avoid conflicting versions.

## Guide for an AI assistant on the Windows PC (temporary, delete before submitting)

Read this if you are an AI assistant (such as Claude Code) working on Vlad's Windows PC (AMD Ryzen 5 5600).
Your job is **one measurement run, then push the data**. The analysis and the report are done on the Mac.

**Why this run is needed.** The earlier run, `results/portable_at3eus-pc/`, cannot be compared cleanly with the main data:
- It used JDK 17, while the main data use JDK 26.0.1. This new run asks whether, on x86 with JDK 26, PassPerItem also beats
  WhileNeeded on reversed input, as it does on the main M3 Pro.
- It was noisy: the median spread within a fork was 28 %, against 2.7 % on the M3 Pro with JDK 17.
- It used the old code, so the Windows decimal comma split `ns_per_sort` into two columns in all 5 400 rows of `raw.csv`.
- Its `environment.txt` was not produced by the committed script, and its power state is missing.

**Do not:** edit or delete `results/portable_at3eus-pc/` or any other existing results; edit a `raw.csv` or
`environment.txt` by hand; change the sorters or the design (`FORKS`, `ITERS`, `SIZES`, `ORDERS`, `JVM_FLAGS`); edit the report;
use WSL or `scripts/run_portable.sh`. If something fails, report the exact output and ask Vlad before working around it.

### Steps

Commands are for Git Bash, the shell Claude Code normally uses on Windows. If `py` is missing, use `python`.

1. **Check the clone.** Run `git status`. Earlier local edits may exist, because the old `environment.txt` came from a changed
   script. If anything is modified, show it to Vlad and do not discard it. Otherwise run `git switch main && git pull`.
2. **Find JDK 26.** The main data used OpenJDK 26.0.1, so ask Vlad before using another 26.x. If it is not installed, ask Vlad
   to install it (Temurin from https://adoptium.net) or to allow you to do so. Then set `JAVA_HOME` with a Windows-style path,
   which `scripts/run_portable.py` prefers over `PATH`, and check it:

   ```sh
   ls "/c/Program Files/Eclipse Adoptium/"
   export JAVA_HOME='C:\Program Files\Eclipse Adoptium\<jdk-26-folder>'
   "$JAVA_HOME/bin/java" -version
   ```
3. **Check the setup (about 10 seconds; it saves no results):**

   ```sh
   py -3 scripts/run_portable.py at3eus-pc-jdk26 --check
   ```

   Expect `Ready`, JDK 26 in the output, and the Ryzen CPU under `--- system`. This is the first real use of this script's
   Windows code, so show Vlad any empty or odd fields.
4. **Ask Vlad to prepare the PC.** Close all other programs and other AI sessions, use the High or Balanced power plan, and leave
   the PC alone until the run ends. Wait for his confirmation.
5. **Start the run in the background (about 20 minutes)**, with `nohup` or your tool's background option, because a normal
   command timeout would kill it:

   ```sh
   py -3 scripts/run_portable.py at3eus-pc-jdk26
   ```

   While it runs, **do no other work on this PC**: no builds, searches or frequent polling, because they add noise to the
   measurements. Wait for the exit notification. If it stops, the same command resumes it; `JAVA_HOME` must be the same.
   Do not use `run_windows.bat` here: it ends with `pause`, which would block a non-interactive shell. Vlad can use it by hand,
   as `run_windows.bat <name>` in cmd or `.\run_windows.bat <name>` in PowerShell.
6. **Check the result:**

   ```sh
   py -3 scripts/check_quality.py results/portable_at3eus-pc-jdk26/raw.csv
   ```

   The run must have printed `OK: 270 jobs, 5400 rows, every value valid`, and `environment.txt` must show JDK 26. **If the
   spread within a fork is above 10 %, tell Vlad before pushing.** A rerun then needs a new name, such as `at3eus-pc-jdk26-2`;
   keep the first folder.
7. **Push only the new folder:**

   ```sh
   git add results/portable_at3eus-pc-jdk26
   git commit -m "Second-machine run: Ryzen 5 5600, Windows 11, JDK 26"
   git pull --rebase && git push
   ```

   Say in the commit message only what you verified, and mention any problem.
8. **Report to Vlad:** the exact Java version, the run time, the spread, the three reversed-input ratios, and anything unusual.
   Compare the ratios with the main data (PassPerItem / WhileNeeded = 0.92, 0.91, 0.94 for n = 1 000, 5 000, 10 000), but leave
   the conclusions for the report to the Mac session.

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
  run_portable.py           second-machine check, any OS (run_windows.bat in the root starts it on Windows)
  check_quality.py          noise and reversed-input ratios of one run
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

## Task: check on a second machine

The main data come from one Apple M3 Pro laptop (ARM). To show that the conclusions are not specific
to it, the same experiment is repeated in a reduced form (6 input orders × sizes 1 000 / 5 000 / 10 000
× 3 algorithms × 5 forks = 270 JVM runs, about 35 minutes) on **another computer, ideally x86**.
`results/portable_vlad-laptop/` is this design on a second M3 Pro (another laptop, macOS 27, JDK 25.0.1), so it is not an x86 check.

1. Install a JDK (any version ≥ 8), Python 3.7+ and Git. On Windows, tick "Add to PATH" in the installers.
2. `git clone https://github.com/vaizan4ikys/bubble-sort-benchmark` and enter the folder.
3. Check that the computer is ready (about 10 seconds, nothing is saved):
   - Windows, native and not WSL (WSL adds a virtualisation layer): `run_windows.bat windows-x86 --check`
     (in PowerShell: `.\run_windows.bat windows-x86 --check`)
   - macOS / Linux: `scripts/run_portable.sh linux-x86 --check`
4. Plug the computer in, close other programs, and start the same command without `--check`.
   Do not use the computer or close the lid until it finishes. If it is interrupted, the same command resumes it.
5. Commit and push (or send) the folder `results/portable_<name-of-the-machine>/`. It contains the raw
   measurements and an `environment.txt` with the hardware and Java version.

The results are then compared with the main data (ratios between the algorithms) and added to the report.
