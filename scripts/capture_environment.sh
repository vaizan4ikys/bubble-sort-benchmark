#!/bin/sh
# Records the hardware / software / power state in which an experiment was run.
# Usage: scripts/capture_environment.sh OUTPUT_FILE
out="$1"
{
  echo "date: $(date)"
  echo "--- hardware"
  sysctl -n machdep.cpu.brand_string
  echo "cores (physical/logical): $(sysctl -n hw.physicalcpu)/$(sysctl -n hw.logicalcpu)"
  echo "memory bytes: $(sysctl -n hw.memsize)"
  sw_vers
  echo "--- java"
  java -version 2>&1
  echo "--- power"
  pmset -g batt | head -2
  pmset -g therm 2>&1 | head -5
  echo "--- load before start"
  uptime
} > "$out"
