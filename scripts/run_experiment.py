#!/usr/bin/env python3
"""Orchestrates the whole benchmark.

Every (algorithm, input order, size, fork) combination is one *job*; a job is one
fresh JVM running ``exp01.Worker``. All jobs are shuffled with a fixed seed so that
the three algorithms are interleaved over the whole run (this spreads slow drifts such
as thermal throttling or background activity evenly over all conditions instead of
penalising whichever algorithm happens to run last).

The script is resumable: finished jobs are listed in ``<out>/completed_jobs.txt`` and
skipped when the script is started again.

Usage:  python3 scripts/run_experiment.py --out results/full --forks 10
"""
import argparse
import itertools
import random
import subprocess
import sys
import time
from pathlib import Path

ALGORITHMS = ["PassPerItem", "UntilNoChange", "WhileNeeded"]
ORDERS = ["random", "sorted", "reversed", "nearly_local", "nearly_random", "few_unique"]
SIZES = [100, 1000, 2000, 5000, 10000, 20000]

JVM_FLAGS = ["-Xms2g", "-Xmx2g", "-XX:+UseSerialGC"]
HEADER = "seq,algorithm,order,size,fork,iter,batch,ns_per_sort,gc_during,warmup_sorts,warmup_timeout\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--forks", type=int, default=10)
    ap.add_argument("--iters", type=int, default=30, help="measured iterations per fork")
    ap.add_argument("--seed", type=int, default=20261104, help="base seed for data AND job order")
    ap.add_argument("--sizes", type=int, nargs="*", default=SIZES)
    ap.add_argument("--orders", nargs="*", default=ORDERS)
    ap.add_argument("--algorithms", nargs="*", default=ALGORITHMS)
    ap.add_argument("--classes", default="bin", help="directory with the compiled classes")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.csv"
    done_file = out / "completed_jobs.txt"
    log = out / "run.log"

    jobs = list(itertools.product(args.algorithms, args.orders, args.sizes, range(args.forks)))
    random.Random(args.seed).shuffle(jobs)

    done = set(done_file.read_text().split("\n")) if done_file.exists() else set()
    if not raw.exists():
        raw.write_text(HEADER)

    t_start = time.time()
    with raw.open("a") as raw_f, done_file.open("a") as done_f, log.open("a") as log_f:
        for seq, (alg, order, size, fork) in enumerate(jobs):
            key = f"{alg}|{order}|{size}|{fork}"
            if key in done:
                continue
            cmd = ["java", *JVM_FLAGS, "-cp", args.classes, "exp01.Worker",
                   alg, order, str(size), str(fork), str(args.seed), str(args.iters)]
            t0 = time.time()
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                log_f.write(f"[{time.ctime()}] FAILED {key}: {res.stderr.strip()}\n")
                log_f.flush()
                print(f"FAILED {key}: {res.stderr.strip()}", file=sys.stderr)
                return 1
            for line in res.stdout.splitlines():
                raw_f.write(f"{seq},{line}\n")
            raw_f.flush()
            done_f.write(key + "\n")
            done_f.flush()
            msg = (f"[{time.ctime()}] job {seq + 1}/{len(jobs)} {key} took {time.time() - t0:.1f}s "
                   f"(elapsed {(time.time() - t_start) / 60:.1f} min)")
            log_f.write(msg + "\n")
            log_f.flush()
            print(msg, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
