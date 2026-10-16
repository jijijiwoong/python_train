"""Shared fixtures: a tiny two-day course written to a temp folder, a fixed clock, a fresh DB."""
from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from lab_app.core.content import ContentRepository
from lab_app.core.progress import LearningService

KST = timezone(timedelta(hours=9))

CURRICULUM = {
    "schema_version": 1,
    "title": "Test Lab",
    "minutes_per_day": 15,
    "review_every": 7,
    "stages": [{"id": "basics", "order": 1, "title": "기초", "description": "", "weeks": 1, "day_range": [1, 7]}],
    "weeks": [{"week": 1, "stage": "basics", "title": "1주"}],
    "concepts": {"print": "출력", "input": "입력", "function": "함수", "return": "반환값",
                 "condition": "조건문", "exception": "예외"},
    "days": [
        {"day": 1, "title": "출력과 입력", "file": "lessons/day01.json", "is_review": False},
        {"day": 2, "title": "함수", "file": "lessons/day02.json", "is_review": False},
    ],
}


def _quiz(qid: str) -> dict:
    return {"id": qid, "question_md": "1 + 1 = ?", "choices": ["1", "2"], "answer_index": 1, "explanation_md": "2"}


def _lesson(day: int, title: str, concepts: list[str], fill: dict, code: dict) -> dict:
    return {
        "schema_version": 1, "day": day, "title": title, "stage": "basics", "week": 1, "is_review": False,
        "objectives": ["목표"], "concepts": concepts,
        "sections": [
            {"type": "review", "minutes": 2, "title": "복습", "content_md": "복습", "quiz": [_quiz(f"d{day:02d}_review_q1")]},
            {"type": "concept", "minutes": 4, "title": "개념", "blocks": [
                {"kind": "text", "md": "설명"},
                {"kind": "code", "code": "print('예제')\n", "runnable": True, "expected_output": "예제\n"}]},
            {"type": "fill_blank", "minutes": 3, "title": "빈칸", "intro_md": "", "exercise_ids": [fill["id"]]},
            {"type": "coding", "minutes": 4, "title": "작성", "intro_md": "", "exercise_ids": [code["id"]]},
            {"type": "summary", "minutes": 2, "title": "정리", "points": ["요점"], "quiz": [_quiz(f"d{day:02d}_summary_q1")]},
        ],
        "exercises": [fill, code],
    }


DAY1 = _lesson(1, "출력과 입력", ["print", "input"], {
    "id": "d01_fill_1", "kind": "fill_blank", "title": "인사", "prompt_md": "hello를 출력", "concepts": ["print"],
    "difficulty": 1, "required": True, "starter_code": "print(____)\n", "entry": {"mode": "program"},
    "tests": [{"id": "t1", "hidden": False, "description": "출력", "expect": {"stdout": "hello\n"}},
              {"id": "h1", "hidden": True, "description": "숨김", "expect": {"stdout": "hello"}}],
    "hints": ["따옴표를 쓰세요", "문자열 hello"], "solution": "print(\"hello\")\n",
}, {
    "id": "d01_code_1", "kind": "coding", "title": "두 배", "prompt_md": "정수를 입력받아 두 배 출력", "concepts": ["input"],
    "difficulty": 1, "required": True, "starter_code": "# 코드를 작성하세요\n", "entry": {"mode": "program"},
    "tests": [{"id": "t1", "hidden": False, "description": "3", "stdin": "3\n", "expect": {"stdout": "6\n"}},
              {"id": "h1", "hidden": True, "description": "0", "stdin": "0\n", "expect": {"stdout": "0\n"}}],
    "hints": ["input()은 문자열을 돌려줍니다", "int()로 바꾸세요"], "solution": "n = int(input())\nprint(n * 2)\n",
})

DAY2 = _lesson(2, "함수", ["function", "return", "condition", "exception"], {
    "id": "d02_fill_1", "kind": "fill_blank", "title": "더하기", "prompt_md": "합 반환", "concepts": ["function", "return"],
    "difficulty": 1, "required": True, "starter_code": "def add(a, b):\n    return ____\n",
    "entry": {"mode": "function", "name": "add"},
    "tests": [{"id": "t1", "hidden": False, "description": "1+2", "call": {"args": [1, 2]}, "expect": {"return": 3}},
              {"id": "h1", "hidden": True, "description": "실수", "call": {"args": [0.1, 0.2]}, "expect": {"return": 0.3},
               "compare": {"mode": "float", "tol": 1e-9}}],
    "hints": ["두 값을 더하세요", "+ 연산자"], "solution": "def add(a, b):\n    return a + b\n",
}, {
    "id": "d02_code_1", "kind": "coding", "title": "안전한 나누기", "prompt_md": "b가 0이면 ValueError",
    "concepts": ["function", "condition", "exception"], "difficulty": 2, "required": True,
    "starter_code": "def safe_div(a, b):\n    pass\n", "entry": {"mode": "function", "name": "safe_div"},
    "tests": [{"id": "t1", "hidden": False, "description": "6/3", "call": {"args": [6, 3]}, "expect": {"return": 2.0}},
              {"id": "t2", "hidden": False, "description": "0으로", "call": {"args": [1, 0]}, "expect": {"raises": "ValueError"}},
              {"id": "h1", "hidden": True, "description": "음수", "call": {"args": [-4, 2]}, "expect": {"return": -2.0}}],
    "hints": ["b가 0인지 먼저 검사", "raise ValueError(...)"],
    "solution": "def safe_div(a, b):\n    if b == 0:\n        raise ValueError(\"0으로 나눌 수 없습니다\")\n    return a / b\n",
    "checks": {"required_syntax": ["if"]},
})


def write_content(root: Path, curriculum: dict | None = None, lessons: dict[int, dict] | None = None) -> Path:
    curriculum = curriculum or CURRICULUM
    lessons = lessons if lessons is not None else {1: DAY1, 2: DAY2}
    (root / "lessons").mkdir(parents=True, exist_ok=True)
    (root / "curriculum.json").write_text(json.dumps(curriculum, ensure_ascii=False), encoding="utf-8")
    for day, lesson in lessons.items():
        (root / "lessons" / f"day{day:02d}.json").write_text(json.dumps(lesson, ensure_ascii=False), encoding="utf-8")
    return root


@pytest.fixture
def lesson_dicts() -> dict[int, dict]:
    """Deep copies that a test may mutate to build invalid content."""
    return {1: copy.deepcopy(DAY1), 2: copy.deepcopy(DAY2)}


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    return write_content(tmp_path / "content")


@pytest.fixture
def content(content_dir: Path) -> ContentRepository:
    return ContentRepository(content_dir)


class FakeClock:
    def __init__(self, start: datetime):
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 10, 16, 21, 0, tzinfo=KST))


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "data" / "learning.db"


@pytest.fixture
def service(content: ContentRepository, db_path: Path, clock: FakeClock) -> LearningService:
    return LearningService(content, db_path, clock=clock)
