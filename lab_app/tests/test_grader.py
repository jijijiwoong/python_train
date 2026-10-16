"""Grading: comparison rules (no subprocess) and the full pipeline (real subprocess)."""
import pytest

from lab_app.core.checks import run_static_checks
from lab_app.core.errors import ErrorType, classify_exception
from lab_app.core.grader import grade, normalize_stdout, values_equal, verify_lesson
from lab_app.core.models import ExceptionInfo, ExecutionReport, TestOutcome


# ---------------------------------------------------------------- pure comparison

@pytest.mark.parametrize("expected, actual, ok", [
    ("a\nb\n", "a  \r\nb\n\n\n", True),
    ("a\nb", "a\n b", False),
    ("", "\n", True),
])
def test_normalize_stdout(expected, actual, ok):
    assert (normalize_stdout(expected) == normalize_stdout(actual)) is ok


@pytest.mark.parametrize("expected, actual, mode, ok", [
    (3, 3, "normalized", True),
    (5.0, 5, "normalized", True),            # int/float compare numerically
    (True, 1, "normalized", False),          # bool is not int
    (1, True, "normalized", False),
    ("1", 1, "normalized", False),
    (0.3, 0.1 + 0.2, "normalized", False),
    (0.3, 0.1 + 0.2, "float", True),
    ([1, 2, 3], [3, 1, 2], "normalized", False),
    ([1, 2, 3], [3, 1, 2], "unordered", True),
    ({"a": [1.0]}, {"a": [1.0000001]}, "float", True),
    ({"a": 1}, {"a": 1, "b": 2}, "normalized", False),
    (None, None, "normalized", True),
])
def test_values_equal(expected, actual, mode, ok):
    assert values_equal(expected, actual, mode, tol=1e-6) is ok


def test_classify_exception_prefers_subclass():
    assert classify_exception(["TabError", "IndentationError", "SyntaxError", "Exception"]) is ErrorType.INDENTATION_ERROR
    assert classify_exception(["UnboundLocalError", "NameError"]) is ErrorType.NAME_ERROR
    assert classify_exception(["RecursionError", "RuntimeError"]) is ErrorType.RUNTIME_ERROR


# ---------------------------------------------------------------- static checks

def test_static_checks_required_forbidden_and_style():
    code = "total = sum([1, 2])\nprint(f'{total}')\n" + "x = 1  # " + "가" * 100 + "\n"
    fb = run_static_checks(code, {"required_syntax": ["for"], "forbidden_calls": ["sum"], "max_lines": 1})
    errors = [f.message for f in fb if f.severity == "error"]
    warnings = [f.message for f in fb if f.severity == "warning"]
    assert any("for 반복문" in m for m in errors)
    assert any("sum()" in m for m in errors)
    assert any("3줄" in m for m in warnings) and any("100자" in m for m in warnings)


def test_static_checks_skip_syntax_errors():
    assert run_static_checks("def f(:\n", {"required_syntax": ["for"]}) == []


# ---------------------------------------------------------------- pipeline with a fake executor

def _report(**outcomes) -> ExecutionReport:
    return ExecutionReport(None, {k: v for k, v in outcomes.items()}, False, None, 1)


def test_hidden_test_details_are_not_exposed(content):
    ex = content.exercise("d02_fill_1")
    fake = lambda code, exercise: _report(
        t1=TestOutcome("t1", "ok", returned={"type": "int", "json": 3, "json_ok": True, "repr": "3"}),
        h1=TestOutcome("h1", "ok", returned={"type": "int", "json": 0, "json_ok": True, "repr": "0"}))
    r = grade(ex, "def add(a, b):\n    return 3\n", execute=fake)
    hidden = next(t for t in r.tests if t.hidden)
    assert not r.passed and r.error_type is ErrorType.WRONG_ANSWER
    assert (r.public_passed, r.hidden_passed) == (1, 0)
    assert hidden.expected is None and hidden.actual is None and hidden.description == ""


def test_precheck_blocks_without_running(content):
    def boom(code, exercise):
        raise AssertionError("must not execute")
    ex = content.exercise("d01_fill_1")
    assert grade(ex, ex.starter_code, execute=boom).error_type is ErrorType.UNFILLED_BLANK
    assert grade(ex, "   \n", execute=boom).error_type is ErrorType.EMPTY_CODE


def test_internal_error_is_flagged(content):
    fake = lambda code, exercise: ExecutionReport(None, {}, False, "boom", 1)
    r = grade(content.exercise("d01_code_1"), "print(1)\n", execute=fake)
    assert r.error_type is ErrorType.INTERNAL_ERROR and not r.passed


def test_compile_error_fails_every_test(content):
    exc = ExceptionInfo("SyntaxError", ["SyntaxError", "Exception"], "invalid syntax", "", 1)
    fake = lambda code, exercise: ExecutionReport(exc, {}, False, None, 1)
    r = grade(content.exercise("d01_code_1"), "print(\n", execute=fake)
    assert r.error_type is ErrorType.SYNTAX_ERROR
    assert all(not t.passed for t in r.tests) and len(r.tests) == 2


# ---------------------------------------------------------------- pipeline with real execution

def test_static_failure_blocks_pass_even_if_tests_pass(content):
    ex = content.exercise("d02_code_1")
    code = "def safe_div(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        raise ValueError('0')\n"
    r = grade(ex, code)
    assert all(t.passed for t in r.tests)
    assert not r.passed and r.error_type is ErrorType.STATIC_CHECK_FAILED


def test_expected_exception_rules(content):
    ex = content.exercise("d02_code_1")
    no_raise = grade(ex, "def safe_div(a, b):\n    if b == 0:\n        return 0\n    return a / b\n")
    wrong_raise = grade(ex, "def safe_div(a, b):\n    if b == 0:\n        pass\n    return a / b\n")
    assert no_raise.error_type is ErrorType.WRONG_EXCEPTION
    t2 = next(t for t in wrong_raise.tests if t.test_id == "t2")
    assert t2.error_type is ErrorType.WRONG_EXCEPTION and "ZeroDivisionError" in t2.message


def test_stdin_program_grading(content):
    ex = content.exercise("d01_code_1")
    assert grade(ex, "n = int(input('수: '))\nprint(n * 2)\n").passed
    r = grade(ex, "n = input()\nprint(n * 2)\n")  # string repetition: "33"
    assert r.error_type is ErrorType.WRONG_ANSWER
    t1 = r.tests[0]
    assert t1.expected == "6\n" and t1.actual == "33\n"


def test_fixture_lessons_pass_self_check(content):
    for lesson in content.lessons():
        assert verify_lesson(lesson) == []


def test_verify_lesson_catches_broken_content(content):
    """The content self-check itself must fail loudly on bad solutions, free passes and wrong examples."""
    from dataclasses import replace
    lesson = content.lesson(1)
    fill, code = lesson.exercises
    concept = lesson.section("concept")
    bad_blocks = [replace(b, expected_output="틀린 출력\n") if b.runnable else b for b in concept.blocks]
    broken = replace(lesson, exercises=[replace(fill, solution='print("bye")\n'), replace(code, starter_code=code.solution)],
                     sections=[replace(concept, blocks=bad_blocks) if s.type == "concept" else s for s in lesson.sections])
    problems = "\n".join(verify_lesson(broken))
    assert "d01_fill_1: solution이 통과하지 못합니다" in problems
    assert "d01_code_1: starter_code가 채점을 통과합니다" in problems
    assert "코드 블록" in problems


def test_reviewer_hook_adds_feedback_without_changing_the_verdict(content):
    """Future LLM reviewers plug in here; their feedback is advisory only."""
    from lab_app.core.models import Feedback
    from lab_app.llm.base import NullReviewer, StaticHintProvider, get_reviewer

    class FakeReviewer:
        def review(self, exercise, code, result):
            return [Feedback("readability", "error", "변수 이름을 더 구체적으로", source="llm")]

    ex = content.exercise("d01_fill_1")
    result = grade(ex, 'print("hello")\n', reviewer=FakeReviewer())
    assert result.passed and result.feedback[-1].source == "llm"
    assert NullReviewer().review(ex, "", result) == []
    assert StaticHintProvider().hint(ex, "", None, 1) == ex.hints[0]
    assert StaticHintProvider().hint(ex, "", None, 9) is None
    assert get_reviewer("none") is None
    with pytest.raises(NotImplementedError):
        get_reviewer("openai")
