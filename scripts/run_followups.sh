#!/bin/bash
# Runs all follow-up experiments one after the other, AFTER the main experiment
# (results/full) has finished, so that they never compete for the CPU.
#
# Usage:  caffeinate -dims scripts/run_followups.sh
#
# Experiments (all use the same worker procedure as the main experiment):
#   ext_string       element type String instead of Integer (same permutations as the main run)
#   ext_c1           JIT restricted to the C1 compiler       (-XX:TieredStopAtLevel=1)
#   ext_interp       JIT disabled, bytecode interpreter only (-Xint)
#   ext_scaling      fine sweep of the input size (random and sorted input)
#   replication      complete repetition of the main design with new seeds
#   ext_noload/load  the same cells with and without 6 busy background processes
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
LOG=results/followups.log
mkdir -p results

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

step() { # step NAME ARGS...   (all remaining args are passed to run_experiment.py)
  local name="$1"; shift
  log "START $name"
  mkdir -p "results/$name"
  scripts/capture_environment.sh "results/$name/environment.txt"
  $PY scripts/run_experiment.py --out "results/$name" "$@" >> "results/$name/stdout.log" 2>&1 \
    || log "WARNING: $name ended with an error (see results/$name/stdout.log)"
  log "END   $name ($(grep -c . "results/$name/completed_jobs.txt" 2>/dev/null) jobs done)"
}

log "waiting for the main experiment to finish"
while pgrep -f "run_experiment.py --out results/full" > /dev/null; do sleep 30; done
log "main experiment process ended; resuming it once to make sure it is complete"
$PY scripts/run_experiment.py --out results/full --forks 10 --iters 30 >> results/full/stdout.log 2>&1
log "main experiment: $(grep -c . results/full/completed_jobs.txt) / 1080 jobs done"

step ext_string  --classes bin_ext --types String --sizes 100 1000 2000 5000 10000 --forks 5 --iters 20
step ext_c1      --classes bin_ext --types Integer --jvm-extra "-XX:TieredStopAtLevel=1" \
                 --sizes 100 1000 2000 5000 10000 --forks 5 --iters 20
step ext_interp  --classes bin_ext --types Integer --jvm-extra "-Xint" --sizes 100 1000 2000 --forks 5 --iters 10
step ext_scaling --classes bin --orders random sorted \
                 --sizes 200 500 1000 2000 3000 5000 7500 10000 15000 20000 30000 40000 --forks 5 --iters 20
step replication --classes bin --seed 20261105 --forks 10 --iters 30

step ext_noload  --classes bin --orders random reversed nearly_local --sizes 2000 5000 --forks 10 --iters 20
log "starting 6 busy background processes"
LOADPIDS=""
for i in 1 2 3 4 5 6; do yes > /dev/null & LOADPIDS="$LOADPIDS $!"; done
trap 'kill $LOADPIDS 2>/dev/null' EXIT
step ext_load    --classes bin --orders random reversed nearly_local --sizes 2000 5000 --forks 10 --iters 20
kill $LOADPIDS 2>/dev/null
log "ALL FOLLOW-UP EXPERIMENTS FINISHED"
