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
import json
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
    ap.add_argument("--forks", type=int, default=10, help="number of forks (JVMs) per cell")
    ap.add_argument("--fork-start", type=int, default=0, help="id of the first fork (used for additional forks)")
    ap.add_argument("--iters", type=int, default=30, help="measured iterations per fork")
    ap.add_argument("--seed", type=int, default=20261104, help="base seed for data AND job order")
    ap.add_argument("--sizes", type=int, nargs="*", default=SIZES)
    ap.add_argument("--orders", nargs="*", default=ORDERS)
    ap.add_argument("--algorithms", nargs="*", default=ALGORITHMS)
    ap.add_argument("--classes", default="bin", help="directory with the compiled classes")
    ap.add_argument("--types", nargs="*", default=None,
                    help="element types (Integer/String). If given, exp01.ExtendedWorker is used "
                         "instead of exp01.Worker and a 'type' column is written")
    ap.add_argument("--jvm-extra", default="", help='extra JVM flags appended to the defaults, e.g. "-Xint"')
    ap.add_argument("--jvm-flags", default=None,
                    help="REPLACES the default flags (-Xms2g -Xmx2g -XX:+UseSerialGC), e.g. '' for JVM defaults (G1)")
    ap.add_argument("--java", default="java", help="java executable (to compare JDK versions)")
    ap.add_argument("--worker", default=None, choices=["steady"],
                    help="'steady' uses exp01.SteadyWorker (adaptive warm-up of the batch loop; adds the columns "
                         "stab_rounds,stab_converged)")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "raw.csv"
    done_file = out / "completed_jobs.txt"
    log = out / "run.log"

    typed = args.types is not None
    header = HEADER.replace("seq,", "seq,type,", 1) if typed else HEADER
    if args.worker == "steady":
        header = header.rstrip("\n") + ",stab_rounds,stab_converged\n"
    jvm_flags = (JVM_FLAGS if args.jvm_flags is None else args.jvm_flags.split()) + args.jvm_extra.split()
    types = args.types if typed else [None]
    jobs = list(itertools.product(types, args.algorithms, args.orders, args.sizes, range(args.fork_start, args.fork_start + args.forks)))
    random.Random(args.seed).shuffle(jobs)
    (out / "config.json").write_text(json.dumps({**vars(args), "jvm_flags": jvm_flags, "n_jobs": len(jobs)}, indent=2))

    done = set(done_file.read_text().split("\n")) if done_file.exists() else set()
    if not raw.exists():
        raw.write_text(header)

    t_start = time.time()
    with raw.open("a") as raw_f, done_file.open("a") as done_f, log.open("a") as log_f:
        for seq, (typ, alg, order, size, fork) in enumerate(jobs):
            key = f"{typ + '|' if typed else ''}{alg}|{order}|{size}|{fork}"
            if key in done:
                continue
            worker = ["exp01.ExtendedWorker", typ] if typed else ["exp01.SteadyWorker" if args.worker == "steady" else "exp01.Worker"]
            cmd = [args.java, *jvm_flags, "-cp", args.classes, *worker,
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
