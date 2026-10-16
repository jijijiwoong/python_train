"""Run user code in a separate Python process via harness.py (01_design/architecture.md §4).

The app process never exec/evals user code. This is NOT a security sandbox: it protects the
app from hangs, crashes and output floods, and assumes the code is the local user's own.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from lab_app import config
from lab_app.core.errors import ErrorType
from lab_app.core.models import ExceptionInfo, ExecutionReport, Exercise, RunResult, TestOutcome

HARNESS_PATH = Path(__file__).with_name("harness.py")
MATPLOTLIBRC_PATH = Path(__file__).with_name("matplotlibrc")
IS_WINDOWS = os.name == "nt"


def _child_env() -> dict[str, str]:
    # -I already ignores PYTHON* variables; drop them anyway, plus Streamlit's own settings.
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("PYTHON", "STREAMLIT"))}
    env["MPLBACKEND"] = "Agg"  # matplotlib must never open a window from the child process
    env["MATPLOTLIBRC"] = str(MATPLOTLIBRC_PATH)  # Korean font for plots
    return env


def _kill_tree(proc: subprocess.Popen) -> None:
    """Kill the child and anything it spawned."""
    try:
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            os.killpg(proc.pid, 9)
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        proc.kill()
    except OSError:
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def _read_text(path: Path, limit: int) -> str:
    try:
        with open(path, "rb") as f:
            data = f.read(limit)
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def _execute(code: str, job: dict, timeout: float) -> tuple[list[dict], bool, str, int, str, list[bytes]]:
    """Run one harness job. Returns (events, timed_out, raw_stderr, duration_ms, partial_stdout, figure_pngs)."""
    job = {"max_stdout": config.MAX_STDOUT_CHARS, "max_stderr": config.MAX_STDERR_CHARS, **job}
    with tempfile.TemporaryDirectory(prefix="pylab_", ignore_cleanup_errors=True) as tmp:
        job_dir = Path(tmp)
        (job_dir / "user_code.py").write_text(code, encoding="utf-8")
        (job_dir / "job.json").write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
        out_path, err_path = job_dir / "_stdout.txt", job_dir / "_stderr.txt"
        cmd = [sys.executable, "-I", "-X", "utf8", str(HARNESS_PATH), str(job_dir)]
        kwargs: dict = {}
        if IS_WINDOWS:
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        else:
            kwargs["start_new_session"] = True

        start = time.perf_counter()
        timed_out = False
        with open(out_path, "wb") as f_out, open(err_path, "wb") as f_err:
            proc = subprocess.Popen(cmd, cwd=job_dir, stdin=subprocess.DEVNULL, stdout=f_out, stderr=f_err,
                                    env=_child_env(), **kwargs)
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                _kill_tree(proc)
        duration_ms = int((time.perf_counter() - start) * 1000)

        events = []
        raw = _read_text(job_dir / "result.jsonl", config.MAX_RESULT_BYTES)
        for line in raw.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                break  # a line cut off by the kill; everything after it is unreliable
        raw_stderr = _read_text(err_path, config.MAX_READ_BYTES)
        partial = _read_text(job_dir / "partial_stdout.txt", config.MAX_READ_BYTES) if timed_out else ""
        images = []
        for ev in events:
            if ev.get("event") == "figures":
                for name in ev.get("files", []):
                    path = job_dir / Path(name).name
                    if path.is_file() and path.stat().st_size <= config.MAX_FIGURE_BYTES:
                        images.append(path.read_bytes())
    return events, timed_out, raw_stderr, duration_ms, partial, images


def _to_report(events: list[dict], test_ids: list[str], timed_out: bool, raw_stderr: str,
               duration_ms: int) -> ExecutionReport:
    compile_error = None
    internal_error = None
    outcomes: dict[str, TestOutcome] = {}
    finished = False
    for ev in events:
        kind = ev.get("event")
        if kind == "compile" and not ev.get("ok"):
            compile_error = ExceptionInfo.from_dict(ev.get("exception"))
        elif kind == "test":
            outcomes[ev["id"]] = TestOutcome(
                test_id=ev["id"], status=ev.get("status", "ok"), stdout=ev.get("stdout", ""),
                stderr=ev.get("stderr", ""), returned=ev.get("returned"),
                exception=ExceptionInfo.from_dict(ev.get("exception")), duration_ms=ev.get("duration_ms"))
        elif kind == "internal_error":
            internal_error = ev.get("message", "")
        elif kind == "done":
            finished = True

    if compile_error is None and internal_error is None:
        # The first test without a result is the one that hung (timeout) or killed the
        # process (crashed: os._exit, native crash); the rest never ran.
        first_status = "timeout" if timed_out else ("crashed" if not finished else "not_run")
        missing = [tid for tid in test_ids if tid not in outcomes]
        for i, tid in enumerate(missing):
            outcomes[tid] = TestOutcome(test_id=tid, status=first_status if i == 0 else "not_run",
                                        stderr=raw_stderr[-2000:] if first_status == "crashed" and i == 0 else "")
    return ExecutionReport(compile_error=compile_error, outcomes=outcomes, timed_out=timed_out,
                           internal_error=internal_error, duration_ms=duration_ms)


def run_tests(code: str, exercise: Exercise, timeout: float | None = None) -> ExecutionReport:
    """Run every test of an exercise (public and hidden) in one child process."""
    tests = [{"id": t.id, "stdin": t.stdin, "args": t.args, "kwargs": t.kwargs} for t in exercise.tests]
    job = {"mode": exercise.entry_mode, "function_name": exercise.function_name, "tests": tests}
    limit = timeout or exercise.time_limit_sec or config.RUN_TIMEOUT_SEC
    events, timed_out, raw_stderr, duration_ms, _, _ = _execute(code, job, limit)
    return _to_report(events, [t["id"] for t in tests], timed_out, raw_stderr, duration_ms)


def run_program(code: str, stdin: str = "", timeout: float | None = None) -> RunResult:
    """Free run ("실행" button): execute the code once with the given stdin. Open figures come back as PNGs."""
    result, images = _run_program(code, stdin, timeout)
    result.images = images
    return result


def _run_program(code: str, stdin: str, timeout: float | None) -> tuple[RunResult, list[bytes]]:
    job = {"mode": "run", "function_name": None, "tests": [{"id": "run", "stdin": stdin}]}
    events, timed_out, raw_stderr, duration_ms, partial, images = _execute(code, job, timeout or config.RUN_TIMEOUT_SEC)
    report = _to_report(events, ["run"], timed_out, raw_stderr, duration_ms)

    if report.compile_error:
        exc = report.compile_error
        return RunResult("error", "", exc.traceback, exc.error_type, exc, duration_ms), images
    if report.internal_error:
        return RunResult("internal_error", "", report.internal_error, ErrorType.INTERNAL_ERROR, None, duration_ms), images
    out = report.outcomes["run"]
    if out.status == "timeout":
        return RunResult("timeout", partial, f"시간 제한({timeout or config.RUN_TIMEOUT_SEC:g}초)을 넘어 실행을 중단했습니다.",
                         ErrorType.TIMEOUT, None, duration_ms), images
    if out.status == "output_limit":
        return RunResult("output_limit", out.stdout, out.stderr + f"\n출력이 {config.MAX_STDOUT_CHARS:,}자를 넘어 실행을 중단했습니다.",
                         ErrorType.OUTPUT_LIMIT, None, duration_ms), images
    if out.status == "crashed":
        return RunResult("error", out.stdout, (out.stderr + "\n").lstrip() + "프로그램이 비정상적으로 종료되었습니다.",
                         ErrorType.RUNTIME_ERROR, None, duration_ms), images
    if out.status == "exception" and out.exception:
        stderr = (out.stderr + "\n" if out.stderr else "") + out.exception.traceback
        return RunResult("error", out.stdout, stderr, out.exception.error_type, out.exception, duration_ms), images
    return RunResult("ok", out.stdout, out.stderr, ErrorType.NONE, None, duration_ms), images
