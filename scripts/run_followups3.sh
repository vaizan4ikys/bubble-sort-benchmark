#!/bin/bash
# Re-run of the two steps of the first queue that failed because argparse took "-Xint" and
# "-XX:TieredStopAtLevel=1" for options (fixed with --jvm-extra=VALUE). Starts after queue 2.
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
LOG=results/followups3.log
log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
step() {
  local name="$1"; shift
  log "START $name"
  rm -rf "results/$name"; mkdir -p "results/$name"
  scripts/capture_environment.sh "results/$name/environment.txt"
  $PY scripts/run_experiment.py --out "results/$name" "$@" >> "results/$name/stdout.log" 2>&1 \
    || log "WARNING: $name ended with an error (see results/$name/stdout.log)"
  log "END   $name ($(grep -c . "results/$name/completed_jobs.txt" 2>/dev/null) jobs done)"
}
log "waiting for the second queue"
until grep -q "ALL SECOND-QUEUE EXPERIMENTS FINISHED" results/followups2.log 2>/dev/null; do sleep 60; done
step ext_c1     --classes bin_ext --types Integer --jvm-extra=-XX:TieredStopAtLevel=1 \
                --sizes 100 1000 2000 5000 10000 --forks 5 --iters 20
step ext_interp --classes bin_ext --types Integer --jvm-extra=-Xint --sizes 100 1000 2000 --forks 5 --iters 10
log "ALL THIRD-QUEUE EXPERIMENTS FINISHED"
