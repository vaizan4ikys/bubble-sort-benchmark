#!/bin/bash
# PORTABLE VERSION: run a reduced design on ANOTHER machine to check that the conclusions are not
# specific to our Apple M3 Pro. Takes about 30-40 minutes. Requirements: a JDK (any version >= 8),
# Python 3. Close other applications, plug the laptop in, do not use it while this runs.
#
#   scripts/run_portable.sh <name-of-the-machine>      e.g.  scripts/run_portable.sh vlad-laptop
#
# Result: results/portable_<name>/  (send this folder back / push it to the repository)
cd "$(dirname "$0")/.." || exit 1
NAME="${1:?usage: scripts/run_portable.sh <name-of-the-machine>}"
OUT="results/portable_$NAME"
mkdir -p "$OUT" bin_portable
javac -d bin_portable src/exp01/*.java || exit 1
scripts/capture_environment.sh "$OUT/environment.txt" 2>/dev/null
{ uname -a; (lscpu 2>/dev/null | head -20); (wmic cpu get name 2>/dev/null); } >> "$OUT/environment.txt"
python3 scripts/run_experiment.py --out "$OUT" --classes bin_portable --forks 5 --iters 20 \
  --orders random sorted reversed nearly_local nearly_random few_unique --sizes 1000 5000 10000
