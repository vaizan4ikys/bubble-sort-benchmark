#!/bin/bash
# SECOND queue of follow-up experiments ("threats to the final decision"). Starts when the first
# queue (scripts/run_followups.sh) has finished, so nothing competes for the CPU.
#
# Usage:  caffeinate -dims scripts/run_followups2.sh
#
#   correctness      exhaustive / random / stability tests of the three sorters (not timed)
#   ext_g1, ext_parallel   other garbage collectors (G1 is the JVM default; array stores carry GC write barriers)
#   ext_jdk8/17/21/25      other JDK versions (different JIT compilers); the main data is JDK 26
#   ext_small        tiny arrays (n = 2..50)
#   ext_shapes       classic bubble-sort cases: turtle, rabbit, sorted+random tail, organ pipe, sawtooth
#   ext_polluted     JVM whose compareTo call sites have already seen other element types
#   ext_cold         the first sort calls of a fresh JVM (no warm-up)
#   ext_jmh          cross-check of our harness with JMH
#   remeasure        re-measure the uncertain groups (rule in REMEASURE_RULE.md)
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
LOG=results/followups2.log
ALL6="random sorted reversed nearly_local nearly_random few_unique"
mkdir -p results

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

step() { # step NAME [JAVA_BIN=path] ARGS...
  local name="$1"; shift
  local jbin=java
  if [[ "$1" == JAVA_BIN=* ]]; then jbin="${1#JAVA_BIN=}"; shift; fi
  log "START $name"
  mkdir -p "results/$name"
  scripts/capture_environment.sh "results/$name/environment.txt"
  { echo "--- java used by this experiment ($jbin)"; "$jbin" -version 2>&1; } >> "results/$name/environment.txt"
  $PY scripts/run_experiment.py --out "results/$name" "$@" >> "results/$name/stdout.log" 2>&1 \
    || log "WARNING: $name ended with an error (see results/$name/stdout.log)"
  log "END   $name ($(grep -c . "results/$name/completed_jobs.txt" 2>/dev/null) jobs done)"
}

log "waiting for the first follow-up queue to finish"
while pgrep -f "run_followups.sh" > /dev/null; do sleep 30; done
log "first queue finished"

# ---- correctness (not timed) ----------------------------------------------------------------
log "START correctness"
mkdir -p results/correctness
java -cp bin_ext2 exp01.CorrectnessTest > results/correctness/correctness.txt 2>&1
log "END   correctness: $(tail -1 results/correctness/correctness.txt)"
java -cp bin_ext2 exp01.OperationCounter results/operation_counts_extended.csv extended
log "operation counts (extended) written"

C="--classes bin_ext2 --types Integer"
# ---- garbage collectors ------------------------------------------------------------------------
step ext_g1       $C --jvm-flags ""                                  --orders $ALL6 --sizes 1000 5000 10000 --forks 5 --iters 20
step ext_parallel $C --jvm-flags "-Xms2g -Xmx2g -XX:+UseParallelGC"  --orders $ALL6 --sizes 1000 5000 10000 --forks 5 --iters 20
# ---- JDK versions --------------------------------------------------------------------------------
# JDK locations: override with JAVA8_BIN and JDK_PREFIX (the java of JDK v is $JDK_PREFIX$v/bin/java).
J8=${JAVA8_BIN:-$HOME/Library/Java/JavaVirtualMachines/corretto-1.8.0_482/Contents/Home/bin/java}
for v in 17 21 25; do
  J=${JDK_PREFIX:-/opt/homebrew/opt/openjdk@}$v/bin/java
  step ext_jdk$v JAVA_BIN=$J $C --java $J --orders $ALL6 --sizes 1000 5000 10000 --forks 5 --iters 20
done
step ext_jdk8 JAVA_BIN=$J8 $C --java $J8 --orders $ALL6 --sizes 1000 5000 10000 --forks 5 --iters 20
# ---- other inputs ------------------------------------------------------------------------------------
step ext_small    $C --orders $ALL6 turtle rabbit --sizes 2 3 5 10 20 50 --forks 5 --iters 30
step ext_shapes   $C --orders turtle rabbit sorted_tail organ_pipe sawtooth --sizes 1000 5000 10000 --forks 5 --iters 20
step ext_polluted --classes bin_ext2 --types PollutedInteger --orders random sorted reversed nearly_local nearly_random \
                  --sizes 1000 5000 20000 --forks 5 --iters 20
# ---- cold start -----------------------------------------------------------------------------------------
log "START ext_cold"
scripts/capture_environment.sh results/ext_cold_environment.txt
$PY scripts/run_cold.py --out results/ext_cold >> results/ext_cold.stdout 2>&1 || log "WARNING: ext_cold ended with an error"
log "END   ext_cold"
# ---- JMH cross-check -----------------------------------------------------------------------------------------
log "START ext_jmh"
scripts/run_jmh.sh >> results/ext_jmh.stdout 2>&1 || log "WARNING: ext_jmh failed (see results/ext_jmh.stdout)"
log "END   ext_jmh"
# ---- re-measure uncertain groups --------------------------------------------------------------------------------
log "START remeasure (analysis of the main data first)"
(cd analysis && ../$PY analyze_main.py results/full analysis/out/main >> ../results/followups2.analysis.log 2>&1)
$PY scripts/remeasure.py >> results/remeasure.stdout 2>&1 || log "WARNING: remeasure ended with an error"
log "END   remeasure"
log "ALL SECOND-QUEUE EXPERIMENTS FINISHED"
