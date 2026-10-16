"""Grading pipeline (01_design/architecture.md §5):

PreCheck → static checks (ast) → tests in a child process → optional reviewer (future LLM).
The child only reports actual values; every pass/fail judgement happens here.
"""
from __future__ import annotations

import json
import math
from typing import Any, Callable

from lab_app import config
from lab_app.core.checks import run_static_checks
from lab_app.core.errors import ErrorType, hint_for
from lab_app.core.models import (
    ExecutionReport, Exercise, Feedback, GradeResult, Lesson, TestCase, TestOutcome, TestResult,
)
from lab_app.core.runner import run_program, run_tests
from lab_app.llm.base import CodeReviewer

Executor = Callable[[str, Exercise], ExecutionReport]


# ---------------------------------------------------------------- comparison

def normalize_stdout(text: str) -> str:
    """CRLF → LF, strip trailing spaces on each line, drop trailing blank lines."""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def stdout_matches(expected: str, actual: str, mode: str) -> bool:
    if mode == "exact":
        return expected == actual
    return normalize_stdout(expected) == normalize_stdout(actual)


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def values_equal(expected: Any, actual: Any, mode: str = "normalized", tol: float = 1e-6) -> bool:
    """Compare JSON-like values. bool and int are distinct (True != 1); int and float compare numerically."""
    if isinstance(expected, bool) or isinstance(actual, bool):
        return type(expected) is type(actual) and expected == actual
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if mode == "float":
            return math.isclose(expected, actual, rel_tol=0.0, abs_tol=tol)
        return expected == actual
    if isinstance(expected, list) and isinstance(actual, list):
        if mode == "unordered":
            expected, actual = sorted(expected, key=_canon), sorted(actual, key=_canon)
        return len(expected) == len(actual) and all(values_equal(e, a, mode, tol) for e, a in zip(expected, actual))
    if isinstance(expected, dict) and isinstance(actual, dict):
        return expected.keys() == actual.keys() and all(values_equal(expected[k], actual[k], mode, tol) for k in expected)
    return type(expected) is type(actual) and expected == actual


# ---------------------------------------------------------------- per-test judgement

def _judge(test: TestCase, out: TestOutcome, time_limit: float) -> tuple[bool, ErrorType, str, str | None, str | None]:
    """Returns (passed, error_type, message, expected_text, actual_text)."""
    exp = test.expect
    if out.status == "timeout":
        return False, ErrorType.TIMEOUT, f"시간 제한({time_limit:g}초)을 넘었습니다. 무한 루프가 없는지 확인하세요.", None, None
    if out.status == "not_run":
        return False, ErrorType.NOT_RUN, "앞선 테스트가 끝나지 않아 실행되지 않았습니다.", None, None
    if out.status == "crashed":
        return False, ErrorType.RUNTIME_ERROR, "프로그램이 비정상적으로 종료되었습니다.", None, None
    if out.status == "output_limit":
        return False, ErrorType.OUTPUT_LIMIT, f"출력이 {config.MAX_STDOUT_CHARS:,}자를 넘었습니다.", None, None

    if "raises" in exp:
        want = exp["raises"]
        if out.exception is None:
            actual = out.returned["repr"] if out.returned else "예외 없음"
            return False, ErrorType.WRONG_EXCEPTION, f"{want} 예외가 발생해야 하는데 발생하지 않았습니다.", f"{want} 발생", actual
        if want not in out.exception.mro_names:
            return (False, ErrorType.WRONG_EXCEPTION, f"{want} 예외가 발생해야 하는데 {out.exception.type}이(가) 발생했습니다.",
                    f"{want} 발생", f"{out.exception.type}: {out.exception.message}")
        return True, ErrorType.NONE, "통과", f"{want} 발생", f"{out.exception.type} 발생"

    if out.exception is not None:
        et = out.exception.error_type
        return False, et, f"{out.exception.type}: {out.exception.message}", None, None

    problems = []
    expected_parts, actual_parts = [], []
    if "return" in exp:
        returned = out.returned or {"json": None, "json_ok": True, "repr": "None"}
        ok = returned.get("json_ok", False) and values_equal(exp["return"], returned["json"], test.compare_mode, test.tol)
        expected_parts.append(repr(exp["return"]))
        actual_parts.append(returned["repr"])
        if not ok:
            problems.append("반환값이 기대값과 다릅니다.")
    if "stdout" in exp:
        mode = "exact" if test.compare_mode == "exact" else "normalized"
        expected_parts.append(exp["stdout"])
        actual_parts.append(out.stdout)
        if not stdout_matches(exp["stdout"], out.stdout, mode):
            problems.append("출력이 기대값과 다릅니다.")
    expected_text = "\n---\n".join(expected_parts)
    actual_text = "\n---\n".join(actual_parts)
    if problems:
        return False, ErrorType.WRONG_ANSWER, " ".join(problems), expected_text, actual_text
    return True, ErrorType.NONE, "통과", expected_text, actual_text


def _test_result(test: TestCase, out: TestOutcome, time_limit: float) -> TestResult:
    passed, et, message, expected, actual = _judge(test, out, time_limit)
    if test.hidden:
        # Hidden tests reveal only pass/fail and the error category.
        message = "통과" if passed else f"숨김 테스트를 통과하지 못했습니다 ({et.label})."
        return TestResult(test.id, True, "", passed, et, message, duration_ms=out.duration_ms)
    return TestResult(test.id, False, test.description, passed, et, message, expected=expected, actual=actual,
                      stdout=out.stdout, traceback=out.exception.traceback if out.exception else None,
                      duration_ms=out.duration_ms)


# ---------------------------------------------------------------- pipeline

def _blocked_result(exercise: Exercise, error_type: ErrorType, message: str) -> GradeResult:
    """Result when the code is rejected before running (nothing executed)."""
    tests = [TestResult(t.id, t.hidden, "" if t.hidden else t.description, False, ErrorType.NOT_RUN,
                        "실행되지 않았습니다.") for t in exercise.tests]
    return GradeResult(False, error_type, tests, [Feedback("correctness", "error", message, source="tests")],
                       0, len(exercise.public_tests), 0, len(exercise.hidden_tests), 0)


def grade(exercise: Exercise, code: str, *, execute: Executor = run_tests,
          reviewer: CodeReviewer | None = None) -> GradeResult:
    # 1. PreCheck
    if not code.strip():
        return _blocked_result(exercise, ErrorType.EMPTY_CODE, "코드를 입력하세요.")
    if config.BLANK_TOKEN in code:
        return _blocked_result(exercise, ErrorType.UNFILLED_BLANK,
                               f"아직 채우지 않은 빈칸({config.BLANK_TOKEN})이 있습니다.")

    # 2. Static checks (parse only)
    feedback = run_static_checks(code, exercise.checks)
    static_failed = any(f.severity == "error" for f in feedback)

    # 3. Tests in a child process
    report = execute(code, exercise)
    time_limit = exercise.time_limit_sec or config.RUN_TIMEOUT_SEC
    n_pub, n_hid = len(exercise.public_tests), len(exercise.hidden_tests)

    if report.internal_error:
        feedback.append(Feedback("correctness", "error", "채점 도구에 문제가 생겼습니다. 다시 시도해 주세요.", source="tests"))
        return GradeResult(False, ErrorType.INTERNAL_ERROR, [], feedback, 0, n_pub, 0, n_hid, report.duration_ms)

    if report.compile_error:
        exc = report.compile_error
        et = exc.error_type
        tests = [TestResult(t.id, t.hidden, "" if t.hidden else t.description, False, et,
                            "코드에 문법 오류가 있어 실행하지 못했습니다.") for t in exercise.tests]
        feedback.insert(0, Feedback("correctness", "error", f"{et.label} ({exc.lineno}번째 줄): {exc.message}",
                                    line=exc.lineno, source="tests"))
        if tip := hint_for(et):
            feedback.append(Feedback("correctness", "info", tip, source="tests"))
        return GradeResult(False, et, tests, feedback, 0, n_pub, 0, n_hid, report.duration_ms, compile_error=exc)

    results = [_test_result(t, report.outcomes[t.id], time_limit) for t in exercise.tests]
    first_fail = next((r for r in results if not r.passed), None)
    if first_fail is not None:
        error_type = first_fail.error_type
        if tip := hint_for(error_type):
            feedback.append(Feedback("correctness", "info", tip, source="tests"))
    elif static_failed:
        error_type = ErrorType.STATIC_CHECK_FAILED
    else:
        error_type = ErrorType.NONE

    result = GradeResult(
        passed=error_type is ErrorType.NONE, error_type=error_type, tests=results, feedback=feedback,
        public_passed=sum(r.passed for r in results if not r.hidden), public_total=n_pub,
        hidden_passed=sum(r.passed for r in results if r.hidden), hidden_total=n_hid,
        duration_ms=report.duration_ms,
    )
    # 4. Optional reviewer (future LLM); its feedback never changes pass/fail.
    if reviewer is not None:
        result.feedback.extend(reviewer.review(exercise, code, result))
    return result


# ---------------------------------------------------------------- content self-check

def verify_lesson(lesson: Lesson) -> list[str]:
    """Execution-based content rules (content_schema.md §5, rules 6-8). Returns problems found."""
    problems = []
    for ex in lesson.exercises:
        sol = grade(ex, ex.solution)
        if not sol.passed:
            failed = [r.test_id for r in sol.tests if not r.passed]
            problems.append(f"Day {lesson.day} {ex.id}: solution이 통과하지 못합니다 ({sol.error_type}, 실패: {failed})")
        if any(f.severity == "warning" for f in sol.feedback):
            problems.append(f"Day {lesson.day} {ex.id}: solution에 가독성 경고가 있습니다")
        if grade(ex, ex.starter_code).passed:
            problems.append(f"Day {lesson.day} {ex.id}: starter_code가 채점을 통과합니다 (풀지 않고 완료 가능)")
    for section in lesson.sections:
        for block in section.blocks:
            if block.kind == "code" and block.runnable:
                run = run_program(block.code, timeout=block.time_limit_sec)
                if run.status != "ok" or run.stdout != block.expected_output:
                    problems.append(f"Day {lesson.day} '{section.title}' 코드 블록: 출력 {run.stdout!r} ≠ 기대 {block.expected_output!r}")
    return problems
