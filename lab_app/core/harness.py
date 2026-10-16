"""Child-process harness: runs user code and reports raw results. NEVER imported by the app.

Usage: python -I -X utf8 harness.py <job_dir>

<job_dir>/job.json      {"mode": "run" | "program" | "function", "function_name": str | null,
                         "tests": [{"id", "stdin", "args", "kwargs"}], "max_stdout": int, "max_stderr": int}
<job_dir>/user_code.py  the user's code
<job_dir>/result.jsonl  one JSON object per line, flushed as soon as it is known:
                        {"event": "compile", "ok": bool, "exception"?: {...}}
                        {"event": "test", "id", "status", "stdout", "stderr", "returned"?, "exception"?, "duration_ms"}
                        {"event": "done"}  |  {"event": "internal_error", "message"}

Only the standard library may be used here: with -I neither the app package nor the user's
site-packages are importable. Judging (expected vs actual) is done by the parent's grader.
"""
import builtins
import io
import json
import linecache
import math
import os
import sys
import time
import traceback

USER_FILENAME = "main.py"  # name shown in tracebacks


class OutputLimitExceeded(BaseException):
    """BaseException so that a user's `except Exception:` cannot swallow it."""


class LimitedWriter(io.TextIOBase):
    def __init__(self, limit: int, tee=None):
        self._tee = tee  # optional line-buffered file so output survives a timeout kill
        self._parts: list[str] = []
        self._size = 0
        self._limit = limit
        self.exceeded = False

    @property
    def encoding(self):
        return "utf-8"

    def writable(self):
        return True

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError(f"write() argument must be str, not {type(s).__name__}")
        remaining = self._limit - self._size
        if len(s) > remaining:
            self._parts.append(s[:max(remaining, 0)])
            if self._tee:
                self._tee.write(s[:max(remaining, 0)])
            self._size = self._limit
            self.exceeded = True
            raise OutputLimitExceeded()
        self._parts.append(s)
        self._size += len(s)
        if self._tee:
            self._tee.write(s)
        return len(s)

    def getvalue(self) -> str:
        return "".join(self._parts)


def _make_input(stdin_text: str, echo: bool):
    """input() reading from the test's stdin. Prompts are echoed only in free-run mode,
    so graded output never depends on prompt text."""
    stream = io.StringIO(stdin_text)

    def _input(prompt=""):
        if echo and prompt:
            sys.stdout.write(str(prompt))
        line = stream.readline()
        if not line:
            raise EOFError("EOF when reading a line")
        value = line[:-1] if line.endswith("\n") else line
        if echo:
            sys.stdout.write(value + "\n")
        return value

    return stream, _input


def _encode_value(value):
    def norm(x, depth=0):
        if depth > 50:
            raise ValueError("too deep")
        if x is None or isinstance(x, (bool, int, str)):
            return x
        if isinstance(x, float):
            if math.isnan(x) or math.isinf(x):
                raise ValueError("non-finite float")
            return x
        if isinstance(x, (list, tuple)):
            return [norm(i, depth + 1) for i in x]
        if isinstance(x, (set, frozenset)):
            return sorted((norm(i, depth + 1) for i in x), key=lambda v: json.dumps(v, sort_keys=True))
        if isinstance(x, dict):
            if not all(isinstance(k, str) for k in x):
                raise ValueError("non-str key")
            return {k: norm(v, depth + 1) for k, v in x.items()}
        # numpy arrays/scalars, pandas Series, torch tensors: compare their plain-Python form
        tolist = getattr(x, "tolist", None)
        if callable(tolist):
            return norm(tolist(), depth + 1)
        raise TypeError("not JSON-like")

    try:
        encoded, ok = norm(value), True
    except Exception:
        encoded, ok = None, False
    try:
        text = repr(value)
    except Exception:
        text = f"<{type(value).__name__}>"
    return {"type": type(value).__name__, "json": encoded, "json_ok": ok, "repr": text[:2000]}


def _exception_info(exc: BaseException) -> dict:
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == USER_FILENAME]
    lines = []
    if frames:
        lines.append("Traceback (most recent call last):\n")
        lines.extend(traceback.format_list(frames))
    lines.extend(traceback.format_exception_only(type(exc), exc))
    lineno = frames[-1].lineno if frames else getattr(exc, "lineno", None)
    return {
        "type": type(exc).__name__,
        "mro": [c.__name__ for c in type(exc).__mro__],
        "message": str(exc)[:1000],
        "traceback": "".join(lines)[-4000:],
        "lineno": lineno,
    }


class _Recorder:
    def __init__(self, path: str):
        self._f = open(path, "a", encoding="utf-8")

    def emit(self, obj: dict) -> None:
        self._f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self._f.flush()


def _save_figures(job_dir: str, limit: int = 6) -> list[str]:
    """Free runs: save figures the user's code left open so the app can show them as images."""
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None:
        return []
    saved = []
    for i, num in enumerate(plt.get_fignums()[:limit], start=1):
        name = f"figure_{i}.png"
        plt.figure(num).savefig(os.path.join(job_dir, name), dpi=90, bbox_inches="tight")
        saved.append(name)
    return saved


def _run_one(code_obj, job: dict, test: dict, tee=None) -> dict:
    mode = job["mode"]
    stdin_stream, fake_input = _make_input(test.get("stdin", ""), echo=(mode == "run"))
    module_out = LimitedWriter(job["max_stdout"], tee=tee)
    err = LimitedWriter(job["max_stderr"])
    call_out = LimitedWriter(job["max_stdout"])
    namespace = {
        "__name__": "__main__" if mode != "function" else "user_module",
        "__builtins__": builtins,
        "input": fake_input,
    }
    result = {"event": "test", "id": test["id"], "status": "ok"}
    saved = sys.stdin, sys.stdout, sys.stderr
    start = time.perf_counter()
    try:
        sys.stdin, sys.stdout, sys.stderr = stdin_stream, module_out, err
        try:
            exec(code_obj, namespace)
            if mode == "function":
                func = namespace.get(job["function_name"])
                if not callable(func):
                    raise NameError(f"함수 '{job['function_name']}'를 찾을 수 없습니다 (이름을 확인하세요)")
                sys.stdout = call_out
                value = func(*test.get("args", []), **test.get("kwargs", {}))
                result["returned"] = _encode_value(value)
        except SystemExit as e:
            if e.code not in (None, 0):
                result["status"] = "exception"
                result["exception"] = _exception_info(e)
        except OutputLimitExceeded:
            result["status"] = "output_limit"
        except BaseException as e:  # noqa: BLE001 - user code may raise anything
            result["status"] = "exception"
            result["exception"] = _exception_info(e)
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved
    result["duration_ms"] = int((time.perf_counter() - start) * 1000)
    result["stdout"] = (call_out if mode == "function" else module_out).getvalue()
    result["stderr"] = err.getvalue()
    return result


def main(job_dir: str) -> None:
    rec = _Recorder(os.path.join(job_dir, "result.jsonl"))
    try:
        with open(os.path.join(job_dir, "job.json"), encoding="utf-8") as f:
            job = json.load(f)
        with open(os.path.join(job_dir, "user_code.py"), encoding="utf-8") as f:
            source = f.read()
        # Register the source so tracebacks can show the offending line.
        linecache.cache[USER_FILENAME] = (len(source), None, source.splitlines(True), USER_FILENAME)
        try:
            code_obj = compile(source, USER_FILENAME, "exec")
        except (SyntaxError, ValueError) as e:  # ValueError: source contains null bytes
            rec.emit({"event": "compile", "ok": False, "exception": _exception_info(e)})
            rec.emit({"event": "done"})
            return
        rec.emit({"event": "compile", "ok": True})
        # Free runs stream stdout to a file so the runner can show it even after a timeout kill.
        tee = None
        if job["mode"] == "run":
            tee = open(os.path.join(job_dir, "partial_stdout.txt"), "w", encoding="utf-8", newline="", buffering=1)
        for test in job["tests"]:
            rec.emit(_run_one(code_obj, job, test, tee))
        if job["mode"] == "run":
            try:
                rec.emit({"event": "figures", "files": _save_figures(job_dir)})
            except Exception:  # noqa: BLE001 - a broken figure must not hide the program's output
                pass
        rec.emit({"event": "done"})
    except BaseException:  # noqa: BLE001
        rec.emit({"event": "internal_error", "message": traceback.format_exc()[-4000:]})


if __name__ == "__main__":
    main(sys.argv[1])
    sys.stdout.flush()
    # Skip interpreter shutdown: non-daemon threads started by user code must not keep us alive.
    os._exit(0)
