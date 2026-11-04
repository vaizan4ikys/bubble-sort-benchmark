#!/usr/bin/env python3
"""Second-machine check: runs a reduced design on another computer (Windows, Linux or macOS).

Design: 3 algorithms x 6 input orders x sizes 1000/5000/10000 x 5 forks = 270 JVM runs.
Needs a JDK (>= 8) and Python 3.7+; no Python packages.

    python scripts/run_portable.py windows-x86            run everything (resumes if interrupted)
    python scripts/run_portable.py windows-x86 --check    only check that this computer is ready

Result: results/portable_<name>/  (raw.csv, environment.txt, config.json, run.log, ...)
"""
import argparse
import csv
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLASSES = "bin_portable"
ALGORITHMS = ["PassPerItem", "UntilNoChange", "WhileNeeded"]
ORDERS = ["random", "sorted", "reversed", "nearly_local", "nearly_random", "few_unique"]
SIZES = [1000, 5000, 10000]
FORKS = 5
ITERS = 20
JVM_FLAGS = ["-Xms2g", "-Xmx2g", "-XX:+UseSerialGC"]
FIELDS = 11  # columns of raw.csv

WINDOWS_ENVIRONMENT = r"""
$ErrorActionPreference = 'SilentlyContinue'
Get-CimInstance Win32_Processor | Format-List Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, LoadPercentage
Get-CimInstance Win32_ComputerSystem | Format-List Manufacturer, Model, TotalPhysicalMemory
Get-CimInstance Win32_OperatingSystem | Format-List Caption, Version, BuildNumber, FreePhysicalMemory
Get-CimInstance Win32_Battery | Format-List BatteryStatus, EstimatedChargeRemaining
powercfg /getactivescheme
"""
ENVIRONMENT_COMMANDS = {
    "win32": [["powershell", "-NoProfile", "-NonInteractive", "-Command", WINDOWS_ENVIRONMENT]],
    "darwin": [["sysctl", "-n", "machdep.cpu.brand_string", "hw.physicalcpu", "hw.logicalcpu", "hw.memsize"],
               ["sw_vers"], ["pmset", "-g", "batt"], ["uptime"]],
    "linux": [["lscpu"], ["free", "-b"], ["uptime"]],
}


def die(message):
    print(f"\nERROR: {message}", file=sys.stderr)
    sys.exit(1)


def output_of(cmd):
    """Output of a diagnostic command; a missing tool must never stop the experiment."""
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             errors="replace", timeout=60)
        return res.stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return f"(could not run {cmd[0]}: {exc})"


def find_jdk():
    """javac and the java next to it, so that compiler and runtime are always the same JDK."""
    candidates = []
    if os.environ.get("JAVA_HOME"):
        candidates.append(shutil.which("javac", path=str(Path(os.environ["JAVA_HOME"]) / "bin")))
    candidates.append(shutil.which("javac"))
    for javac in candidates:
        if javac:
            java = shutil.which("java", path=str(Path(javac).parent))
            if java:
                return javac, java
    die("javac was not found. Install a JDK (not only a JRE), for example https://adoptium.net, "
        "enable 'Add to PATH' / 'Set JAVA_HOME' in the installer and open a new window.")


def compile_sources(javac):
    sources = [str(p.relative_to(ROOT)) for p in sorted((ROOT / "src" / "exp01").glob("*.java"))]
    res = subprocess.run([javac, "-d", CLASSES, *sources], cwd=ROOT, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, errors="replace")
    if res.returncode != 0:
        die(f"compilation failed:\n{res.stdout}")


def check_row(row):
    """Reason why a raw.csv row is invalid, or None. row: everything after the seq column."""
    if len(row) != FIELDS - 1:
        return f"expected {FIELDS - 1} fields, got {len(row)}"
    try:
        return None if float(row[6]) > 0 else f"non-positive time {row[6]}"
    except ValueError:
        return f"ns_per_sort is not a number: {row[6]!r}"


def preflight(java):
    """One short real fork: proves that the JVM flags, the classes and the CSV format all work."""
    res = subprocess.run([java, *JVM_FLAGS, "-cp", CLASSES, "exp01.Worker", "WhileNeeded", "random", "1000", "0", "1", "3"],
                         cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    if res.returncode != 0:
        die(f"the test run failed (too little free memory for -Xms2g?):\n{res.stderr.strip()}")
    rows = list(csv.reader(res.stdout.splitlines()))
    problems = [p for p in map(check_row, rows) if p]
    if len(rows) != 3 or problems:
        die(f"the test run produced bad output: {problems or res.stdout!r}")


def warn_if_on_battery():
    if sys.platform == "win32":
        status = output_of(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                            "(Get-CimInstance Win32_Battery).BatteryStatus"])
        if status.splitlines()[:1] == ["1"]:
            print("WARNING: running on battery. Plug the computer in; it changes the measurements.")


def keep_awake():
    """Windows only: no sleep while this process runs. Ends with the process; settings are untouched."""
    if sys.platform == "win32":
        import ctypes
        es_continuous, es_system_required = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(es_continuous | es_system_required)


def capture_environment(path, java):
    parts = [f"date: {time.ctime()}", f"host: {platform.node()}", f"os: {platform.platform()}",
             f"machine: {platform.machine()}", f"processor: {platform.processor()}",
             f"logical cpus: {os.cpu_count()}", f"python: {platform.python_version()}",
             "--- java", output_of([java, "-version"]), "--- system"]
    parts += [output_of(cmd) for cmd in ENVIRONMENT_COMMANDS.get(sys.platform, [])]
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def refuse_other_machines_folder(env_file):
    """Otherwise a reused name would count this computer's run as already finished by another one."""
    if env_file.exists():
        text = env_file.read_text(encoding="utf-8", errors="replace").lower()
        if platform.node().lower() not in text:
            die(f"{env_file.parent} was created on another computer. Choose a different name.")


def validate(raw):
    expected_jobs = len(ALGORITHMS) * len(ORDERS) * len(SIZES) * FORKS
    with raw.open(newline="") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)
    problems = [(i + 2, p) for i, p in enumerate(check_row(r[1:]) for r in rows) if p]
    if problems:
        die(f"{raw}: {len(problems)} bad rows, first: line {problems[0][0]}: {problems[0][1]}")
    if len(rows) != expected_jobs * ITERS:
        die(f"{raw}: {len(rows)} rows, expected {expected_jobs * ITERS}.")
    gc_rows = sum(r[8] == "1" for r in rows)
    timeouts = len({tuple(r[1:5]) for r in rows if r[10] == "1"})
    print(f"\nOK: {expected_jobs} jobs, {len(rows)} rows, every value valid.")
    print(f"Batches with GC: {gc_rows}. Forks whose warm-up timed out: {timeouts}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", help="name of this machine, e.g. windows-x86")
    ap.add_argument("--check", action="store_true", help="only check that this computer is ready")
    args = ap.parse_args()

    if sys.version_info < (3, 7):
        die("Python 3.7 or newer is needed.")
    name = args.name or input("Name for this machine (e.g. windows-x86): ").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
        die("The name may only contain Latin letters, digits, '.', '_' and '-'.")
    out = ROOT / "results" / f"portable_{name}"
    env_file = out / "environment.txt"
    refuse_other_machines_folder(env_file)

    javac, java = find_jdk()
    print(f"JDK: {javac}\n{output_of([java, '-version'])}")
    compile_sources(javac)
    preflight(java)
    warn_if_on_battery()
    print("Check passed: compiled, and a test fork produced valid data.")

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            capture_environment(Path(tmp) / "environment.txt", java)
            print("\n" + (Path(tmp) / "environment.txt").read_text(encoding="utf-8"))
        print(f"Ready. Now run the same command without --check. Results will go to {out}")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    if not env_file.exists():
        capture_environment(env_file, java)
    keep_awake()
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_experiment.py"), "--out", str(out.relative_to(ROOT)),
                          "--classes", CLASSES, "--java", java, "--forks", str(FORKS), "--iters", str(ITERS),
                          "--orders", *ORDERS, "--sizes", *map(str, SIZES)], cwd=ROOT)
    if res.returncode != 0:
        die("the run stopped. Run the same command again to continue where it stopped.")
    validate(out / "raw.csv")
    print(f"Done. Results: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
