#!/usr/bin/env python3
"""Cold-start experiment: times the first calls of `sort` in a fresh JVM (exp01.ColdWorker).

Usage: python3 scripts/run_cold.py --out results/ext_cold [--forks 30]
Every (algorithm, order, size, fork) job is one JVM; jobs are shuffled with a fixed seed.
"""
import argparse
import itertools
import random
import subprocess
import sys
import time
from pathlib import Path

ALGORITHMS = ["PassPerItem", "UntilNoChange", "WhileNeeded"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--forks", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--orders", nargs="*", default=["random", "sorted", "reversed"])
    ap.add_argument("--sizes", type=int, nargs="*", default=[10, 100, 1000, 10000])
    ap.add_argument("--max-calls", type=int, default=50)
    ap.add_argument("--budget-ms", type=int, default=3000, help="stop a JVM when the cumulated sort time exceeds this")
    ap.add_argument("--classes", default="bin_ext2")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.csv"
    done_file = out / "completed_jobs.txt"
    jobs = list(itertools.product(ALGORITHMS, args.orders, args.sizes, range(args.forks)))
    random.Random(args.seed).shuffle(jobs)
    done = set(done_file.read_text().split("\n")) if done_file.exists() else set()
    if not raw.exists():
        raw.write_text("seq,algorithm,order,size,fork,call,ns\n")
    t0 = time.time()
    with raw.open("a") as rf, done_file.open("a") as df:
        for seq, (alg, order, size, fork) in enumerate(jobs):
            key = f"{alg}|{order}|{size}|{fork}"
            if key in done:
                continue
            cmd = ["java", "-Xms2g", "-Xmx2g", "-XX:+UseSerialGC", "-cp", args.classes, "exp01.ColdWorker", alg, order,
                   str(size), str(fork), str(args.seed), str(args.max_calls), str(args.budget_ms)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print("FAILED", key, res.stderr, file=sys.stderr)
                return 1
            for line in res.stdout.splitlines():
                rf.write(f"{seq},{line}\n")
            rf.flush()
            df.write(key + "\n")
            df.flush()
            if seq % 50 == 0:
                print(f"[{time.ctime()}] job {seq + 1}/{len(jobs)} elapsed {(time.time() - t0) / 60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
