"""The shipped lessons in lab_app/content: schema, self-check, and typical beginner mistakes."""
import pytest

from lab_app.core.content import ContentRepository
from lab_app.core.errors import ErrorType
from lab_app.core.grader import grade, verify_lesson

REPO = ContentRepository()


def test_week_one_is_complete_and_clean():
    assert REPO.available_days == [1, 2, 3, 4, 5, 6, 7]
    assert REPO.warnings == []
    assert REPO.curriculum.total_days == 168
    assert [d.day for d in REPO.curriculum.days if d.is_review] == [7]
    for lesson in REPO.lessons():
        assert lesson.required_exercise_ids, f"Day {lesson.day} has no required exercise"


@pytest.mark.parametrize("day", REPO.available_days)
def test_lesson_self_check(day):
    """Solutions pass, starters fail, runnable examples print what the text claims."""
    assert verify_lesson(REPO.lesson(day)) == []


@pytest.mark.parametrize("exercise_id, code, error_type", [
    ("d01_code_1", 'print("총액: 13500")\nprint("<class \'int\'>")\n', ErrorType.NONE),  # fixed output: accepted
    ("d02_fill_1", "a = input()\nb = int(input())\nprint(a + b)\n", ErrorType.TYPE_ERROR),
    ("d02_code_1", "m = int(input())\nprint(m / 60)\nprint(m % 60)\n", ErrorType.WRONG_ANSWER),
    ("d03_code_1", 'name = input()\nage = int(input())\nprint(f"{name}님, 내년에 {age + 1}살이 됩니다")\n',
     ErrorType.WRONG_ANSWER),                                                     # forgot strip()
    ("d03_code_1", 'name = input().strip()\nage = int(input())\nprint(name + "님, 내년에 " + str(age + 1) + "살이 됩니다")\n',
     ErrorType.STATIC_CHECK_FAILED),                                              # correct output, no f-string
    ("d04_code_1", 'age = int(input())\nif age < 8 or age > 65:\n    print("무료")\nelif age < 18:\n    print("5000원")\n'
                   'else:\n    print("10000원")\n', ErrorType.WRONG_ANSWER),       # boundary mistakes
    ("d05_code_1", "n = int(input())\nprint(sum(range(2, n + 1, 2)))\n", ErrorType.STATIC_CHECK_FAILED),
    ("d05_code_1", "n = int(input())\ntotal = 0\ni = 0\nwhile i <= n:\n    total += i\n", ErrorType.TIMEOUT),
    ("d06_code_1", 'def grade(score):\n    if score >= 90:\n        return "A"\n    elif score >= 80:\n        return "B"\n'
                   '    elif score >= 70:\n        return "C"\n    return "F"\n', ErrorType.WRONG_EXCEPTION),
    ("d07_code_1", 'n = int(input())\ntotal = 0\nbest = 0\nfor _ in range(n):\n    s = int(input())\n    total += s\n'
                   '    best = s\nprint(f"평균: {total / n:.1f}")\nprint(f"최고: {best}")\nprint("합격" if total / n >= 60 else "불합격")\n',
     ErrorType.WRONG_ANSWER),                                                     # best = last, not max
])
def test_typical_mistakes(exercise_id, code, error_type):
    result = grade(REPO.exercise(exercise_id), code)
    assert result.error_type is error_type, [(t.test_id, t.error_type, t.message) for t in result.tests]


def test_optional_challenge_is_not_required():
    lesson = REPO.lesson(7)
    assert "d07_code_2" not in lesson.required_exercise_ids
    assert lesson.exercise("d07_code_2").kind == "coding"
