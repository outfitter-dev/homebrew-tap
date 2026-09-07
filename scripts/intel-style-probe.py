"""Diagnostic proposal only: observe the owned brew-style process tree."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def snapshot(root_pid):
    output = subprocess.check_output(
        ["ps", "-axo", "pid=,ppid=,state=,etime=,%cpu=,%mem=,comm="],
        text=True,
        timeout=5,
    )
    rows = []
    for line in output.splitlines():
        fields = line.split(maxsplit=6)
        if len(fields) == 7:
            rows.append(dict(zip(
                ["pid", "ppid", "state", "elapsed", "cpu", "memory", "executable"],
                fields,
            )))
    owned = {str(root_pid)}
    while True:
        children = {row["pid"] for row in rows if row["ppid"] in owned}
        if children <= owned:
            break
        owned |= children
    return [row for row in rows if row["pid"] in owned]


def main():
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    deadline = started + 240
    sampled = False
    deadline_reached = False
    with (destination / "style.log").open("w") as log:
        process = subprocess.Popen(
            ["brew", "style", "--debug", "outfitter-dev/tap"],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            while process.poll() is None:
                elapsed = int(time.monotonic() - started)
                rows = snapshot(process.pid)
                record = {"elapsedSeconds": elapsed, "processes": rows}
                print(json.dumps(record), flush=True)
                (destination / f"processes-{elapsed}.json").write_text(
                    json.dumps(record, indent=2) + "\n"
                )
                if elapsed >= 180 and not sampled:
                    sampled = True
                    candidates = sorted(
                        rows,
                        key=lambda row: (
                            row["pid"] != str(process.pid),
                            not Path(row["executable"]).name.startswith("ruby"),
                            int(row["pid"]),
                        ),
                    )
                    for row in candidates:
                        remaining = deadline - time.monotonic()
                        if remaining < 10:
                            print(f"Sampling budget exhausted before PID {row['pid']}", flush=True)
                            break
                        try:
                            result = subprocess.run(
                                ["sample", row["pid"], "5", "-file",
                                 str(destination / f"sample-{row['pid']}.txt")],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                timeout=min(10, remaining),
                            )
                            status = f"exit={result.returncode}\n{result.stdout}"
                        except subprocess.TimeoutExpired:
                            status = "sample timed out\n"
                        (destination / f"sample-{row['pid']}-status.txt").write_text(status)
                if time.monotonic() >= deadline:
                    deadline_reached = True
                    break
                time.sleep(min(30, max(0, deadline - time.monotonic())))
        finally:
            terminated_for_diagnostics = process.poll() is None
            if terminated_for_diagnostics:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            result = {
                "pid": process.pid,
                "exitCode": process.returncode,
                "timedOut": deadline_reached,
                "terminatedForDiagnostics": terminated_for_diagnostics,
                "elapsedSeconds": round(time.monotonic() - started, 1),
            }
            (destination / "result.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result), flush=True)
    return 124 if deadline_reached else process.returncode


if __name__ == "__main__":
    def terminate(signum, _frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, terminate)
    sys.exit(main())
