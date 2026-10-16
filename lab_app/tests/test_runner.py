"""Child-process execution: limits, isolation and error reporting (real subprocesses)."""
import time

import pytest

from lab_app import config
from lab_app.core.errors import ErrorType
from lab_app.core.models import Exercise, TestCase
from lab_app.core.runner import run_program, run_tests


def _exercise(mode: str, tests: list[TestCase], name: str | None = None, time_limit: float | None = None) -> Exercise:
    return Exercise(id="x", day=1, kind="coding", title="t", prompt_md="", concepts=[], difficulty=1, required=True,
                    starter_code="", entry_mode=mode, function_name=name, tests=tests, hints=["a", "b"], solution="",
                    time_limit_sec=time_limit)


def _t(tid: str, **kw) -> TestCase:
    return TestCase(id=tid, hidden=False, description="", expect={"stdout": ""}, **kw)


class TestRunProgram:
    def test_prints_unicode_and_reads_stdin_with_echo(self):
        r = run_program('print("안녕")\nname = input("이름: ")\nprint(name * 2)\n', stdin="ab\n")
        assert r.status == "ok" and r.error_type is ErrorType.NONE
        assert r.stdout == "안녕\n이름: ab\nabab\n"

    def test_runtime_error_has_user_only_traceback(self):
        r = run_program("x = 1\nprint(x / 0)\n")
        assert r.status == "error" and r.error_type is ErrorType.ZERO_DIVISION
        assert 'File "main.py", line 2' in r.stderr
        assert "harness" not in r.stderr

    def test_syntax_error(self):
        r = run_program("def f(:\n    pass\n")
        assert r.error_type is ErrorType.SYNTAX_ERROR
        assert r.exception.lineno == 1

    def test_indentation_error(self):
        r = run_program("if True:\nprint(1)\n")
        assert r.error_type is ErrorType.INDENTATION_ERROR

    def test_missing_input_is_eof_error(self):
        r = run_program("a = input()\nb = input()\n", stdin="1\n")
        assert r.error_type is ErrorType.EOF_ERROR

    def test_infinite_loop_times_out_and_app_survives(self):
        start = time.perf_counter()
        r = run_program("while True:\n    pass\n", timeout=1.0)
        assert r.status == "timeout" and r.error_type is ErrorType.TIMEOUT
        assert time.perf_counter() - start < 8  # killed promptly, caller not blocked

    def test_timeout_keeps_output_printed_before_the_hang(self):
        code = 'name = input()\nprint(f"안녕, {name}!")\nwhile True:\n    pass\n'
        r = run_program(code, stdin="파이썬\n", timeout=1.0)
        assert r.status == "timeout"
        assert r.stdout == "파이썬\n안녕, 파이썬!\n"

    def test_output_flood_is_cut(self):
        r = run_program("while True:\n    print('x' * 100)\n")
        assert r.status == "output_limit"
        assert len(r.stdout) <= config.MAX_STDOUT_CHARS

    def test_except_exception_cannot_swallow_output_limit(self):
        code = "try:\n    while True:\n        print('y' * 1000)\nexcept Exception:\n    print('caught')\n"
        assert run_program(code).status == "output_limit"

    def test_hard_exit_is_reported_as_runtime_error(self):
        r = run_program("import os\nos._exit(3)\n")
        assert r.error_type is ErrorType.RUNTIME_ERROR

    def test_sys_exit_zero_is_normal(self):
        r = run_program("import sys\nprint('bye')\nsys.exit(0)\n")
        assert r.status == "ok" and r.stdout == "bye\n"

    def test_child_cannot_import_app_package(self):
        r = run_program("import lab_app\n")
        assert r.error_type is ErrorType.RUNTIME_ERROR  # ModuleNotFoundError: isolated mode

    def test_runs_in_temporary_working_directory(self, tmp_path):
        r = run_program("open('note.txt', 'w').write('x')\nimport os\nprint(os.path.basename(os.getcwd())[:6])\n")
        assert r.stdout.strip() == "pylab_"


class TestRunTests:
    def test_program_mode_ignores_input_prompt(self):
        ex = _exercise("program", [_t("t1", stdin="5\n")])
        rep = run_tests('n = int(input("숫자: "))\nprint(n + 1)\n', ex)
        assert rep.outcomes["t1"].stdout == "6\n"

    def test_each_test_gets_fresh_namespace(self):
        code = "counter = []\ndef f():\n    counter.append(1)\n    return len(counter)\n"
        ex = _exercise("function", [_t("a"), _t("b")], name="f")
        rep = run_tests(code, ex)
        assert [rep.outcomes[k].returned["json"] for k in ("a", "b")] == [1, 1]

    def test_function_mode_return_encoding(self):
        code = "def f(kind):\n    return {'t': (1, 2), 's': {3, 1}, 'o': object}[kind]\n"
        ex = _exercise("function", [_t("t", args=["t"]), _t("s", args=["s"]), _t("o", args=["o"])], name="f")
        out = run_tests(code, ex).outcomes
        assert out["t"].returned == {"type": "tuple", "json": [1, 2], "json_ok": True, "repr": "(1, 2)"}
        assert out["s"].returned["json"] == [1, 3]
        assert out["o"].returned["json_ok"] is False

    def test_function_mode_separates_module_and_call_output(self):
        code = "print('module level')\ndef f():\n    print('inside')\n"
        rep = run_tests(code, _exercise("function", [_t("a")], name="f"))
        assert rep.outcomes["a"].stdout == "inside\n"

    def test_main_guard_does_not_run_in_function_mode(self):
        code = "def f():\n    return 1\nif __name__ == '__main__':\n    print(f())\n    raise SystemExit(1)\n"
        rep = run_tests(code, _exercise("function", [_t("a")], name="f"))
        assert rep.outcomes["a"].status == "ok"

    def test_missing_function_is_name_error(self):
        rep = run_tests("def g():\n    pass\n", _exercise("function", [_t("a")], name="f"))
        assert rep.outcomes["a"].exception.error_type is ErrorType.NAME_ERROR

    def test_exception_mro_is_reported(self):
        rep = run_tests("def f():\n    return {}['k']\n", _exercise("function", [_t("a")], name="f"))
        assert "LookupError" in rep.outcomes["a"].exception.mro_names

    def test_timeout_marks_hanging_test_and_skips_rest(self):
        code = "def f(n):\n    while n == 2:\n        pass\n    return n\n"
        ex = _exercise("function", [_t("a", args=[1]), _t("b", args=[2]), _t("c", args=[3])], name="f", time_limit=1.5)
        out = run_tests(code, ex).outcomes
        assert [out[k].status for k in "abc"] == ["ok", "timeout", "not_run"]

    def test_compile_error_reported_once(self):
        rep = run_tests("print(\n", _exercise("program", [_t("a"), _t("b")]))
        assert rep.compile_error is not None and rep.outcomes == {}


@pytest.mark.parametrize("code", ["import time\ntime.sleep(30)\n", "x = [0] * 10\nwhile True:\n    x.append(1)\n    x.pop()\n"])
def test_long_running_code_is_killed(code):
    assert run_program(code, timeout=1.0).status == "timeout"
