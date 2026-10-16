"""Content loading and schema validation."""
import json
import shutil
from pathlib import Path

import pytest

from lab_app.config import PROJECT_ROOT
from lab_app.core.content import ContentError, ContentRepository, load_curriculum, parse_lesson
from lab_app.core.grader import verify_lesson
from lab_app.tests.conftest import CURRICULUM, write_content


def test_loads_fixture_course(content):
    assert content.available_days == [1, 2]
    assert content.curriculum.total_days == 7
    lesson = content.lesson(2)
    assert lesson.required_exercise_ids == ["d02_fill_1", "d02_code_1"]
    assert lesson.summary_quiz_ids == ["d02_summary_q1"]
    ex = content.exercise("d02_code_1")
    assert ex.entry_mode == "function" and ex.function_name == "safe_div"
    assert [t.id for t in ex.hidden_tests] == ["h1"]
    assert content.warnings == []


def _errors(tmp_path: Path, lessons: dict) -> list[str]:
    with pytest.raises(ContentError) as info:
        ContentRepository(write_content(tmp_path / "c", lessons=lessons))
    return info.value.errors


@pytest.mark.parametrize("mutate, fragment", [
    (lambda d: d["sections"].reverse(), "섹션 순서"),
    (lambda d: d["sections"][0].update(minutes=5), "minutes 합계"),
    (lambda d: d["sections"][2].update(exercise_ids=["nope"]), "없는 문제 id"),
    (lambda d: d["exercises"][0].update(starter_code="print('x')\n"), "빈칸"),
    (lambda d: d["exercises"][0].update(concepts=["unknown_tag"]), "개념 태그"),
    (lambda d: d["exercises"][0]["tests"][0].update(expect={}), "stdout/return/raises"),
    (lambda d: d["exercises"][0]["tests"][0].update(expect={"return": 1}), "program 모드"),
    (lambda d: d["exercises"][0].update(hints=["하나"]), "힌트는 2~3개"),
    (lambda d: d["exercises"][0].update(checks={"required_syntax": ["goto"]}), "지원하지 않는 구문"),
    (lambda d: d["sections"][4].update(quiz=[]), "summary 섹션에는 퀴즈"),
    (lambda d: d["sections"][4]["quiz"][0].update(answer_index=9), "answer_index"),
    (lambda d: [t.update(hidden=True) for t in d["exercises"][1]["tests"]], "공개 테스트"),
])
def test_invalid_lessons_are_rejected(tmp_path, lesson_dicts, mutate, fragment):
    mutate(lesson_dicts[1])
    errors = _errors(tmp_path, lesson_dicts)
    assert any(fragment in e for e in errors), errors


def test_duplicate_exercise_ids_across_days(tmp_path, lesson_dicts):
    lesson_dicts[2]["exercises"][0]["id"] = "d01_fill_1"
    lesson_dicts[2]["sections"][2]["exercise_ids"] = ["d01_fill_1"]
    assert any("중복" in e for e in _errors(tmp_path, lesson_dicts))


def test_broken_json_reports_position(tmp_path):
    root = write_content(tmp_path / "c")
    (root / "lessons" / "day01.json").write_text("{ broken", encoding="utf-8")
    with pytest.raises(ContentError) as info:
        ContentRepository(root)
    assert "JSON 형식 오류" in info.value.errors[0]


def test_curriculum_review_day_rule(tmp_path):
    bad = json.loads(json.dumps(CURRICULUM))
    bad["days"][0]["is_review"] = True
    with pytest.raises(ContentError, match="is_review"):
        load_curriculum(write_content(tmp_path / "c", curriculum=bad, lessons={}))


def test_hint_leak_warning(tmp_path, lesson_dicts):
    lesson_dicts[1]["exercises"][1]["solution"] = "number_value = int(input())\nprint(number_value * 2)\n"
    lesson_dicts[1]["exercises"][1]["hints"][1] = "number_value = int(input()) 를 쓰세요"
    repo = ContentRepository(write_content(tmp_path / "c", lessons=lesson_dicts))
    assert any("정답 코드" in w for w in repo.warnings)


def test_design_example_lesson_is_valid(tmp_path):
    """The Day 6 example in 01_design must stay valid against the implemented schema."""
    design = PROJECT_ROOT / "01_design"
    root = tmp_path / "c"
    root.mkdir()
    shutil.copy(design / "example_curriculum.json", root / "curriculum.json")
    curriculum = load_curriculum(root)
    raw = json.loads((design / "example_lesson.json").read_text(encoding="utf-8"))
    lesson, warnings = parse_lesson(raw, "example_lesson.json", curriculum)
    assert warnings == []
    assert verify_lesson(lesson) == []
