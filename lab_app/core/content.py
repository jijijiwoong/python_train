"""Load and validate curriculum/lesson JSON (01_design/content_schema.md).

Structural rules are enforced here; rules that need code execution (solutions pass,
starters fail, runnable blocks match) are verified by `grader.verify_lesson` and pytest.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from lab_app import config
from lab_app.core.checks import SUPPORTED_SYNTAX
from lab_app.core.models import (
    Block, Curriculum, DayInfo, Exercise, Lesson, QuizItem, Section, Stage, TestCase, Week,
)

SECTION_ORDER = ["review", "concept", "fill_blank", "coding", "summary"]
SCHEMA_VERSION = 1
COMPARE_MODES = {"normalized", "exact", "float", "unordered"}


class ContentError(Exception):
    """Raised when content files break the schema. `errors` lists every problem found."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("콘텐츠 오류:\n- " + "\n- ".join(errors))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ContentError([f"{path.name}: 파일이 없습니다"]) from None
    except json.JSONDecodeError as e:
        raise ContentError([f"{path.name}: JSON 형식 오류 (줄 {e.lineno}, 칸 {e.colno}): {e.msg}"]) from None


class _Collector:
    """Accumulates validation errors with a location prefix."""

    def __init__(self, source: str):
        self.source = source
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{self.source}: {where}: {msg}" if where else f"{self.source}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{self.source}: {where}: {msg}")

    def require(self, obj: dict, key: str, typ: type | tuple[type, ...], where: str) -> Any:
        if not isinstance(obj, dict) or key not in obj:
            self.error(where, f"'{key}' 필드가 필요합니다")
            return None
        value = obj[key]
        # bool is a subclass of int; reject it where an int is required
        if not isinstance(value, typ) or (typ is int and isinstance(value, bool)):
            self.error(where, f"'{key}'의 형식이 올바르지 않습니다")
            return None
        return value


# ---------------------------------------------------------------- curriculum

def load_curriculum(content_dir: Path) -> Curriculum:
    path = content_dir / "curriculum.json"
    raw = _read_json(path)
    c = _Collector(path.name)
    if raw.get("schema_version") != SCHEMA_VERSION:
        c.error("", f"schema_version은 {SCHEMA_VERSION}이어야 합니다")

    stages: list[Stage] = []
    for i, s in enumerate(c.require(raw, "stages", list, "") or []):
        w = f"stages[{i}]"
        dr = c.require(s, "day_range", list, w)
        if dr is None or len(dr) != 2:
            c.error(w, "day_range는 [시작, 끝] 형식이어야 합니다")
            continue
        stage = Stage(id=c.require(s, "id", str, w), order=c.require(s, "order", int, w),
                      title=c.require(s, "title", str, w), description=s.get("description", ""),
                      weeks=c.require(s, "weeks", int, w), day_range=(dr[0], dr[1]))
        if stage.weeks and dr[1] - dr[0] + 1 != stage.weeks * 7:
            c.error(w, "day_range 길이가 weeks × 7과 다릅니다")
        stages.append(stage)
    for prev, cur in zip(stages, stages[1:]):
        if cur.day_range[0] != prev.day_range[1] + 1:
            c.error("stages", f"{prev.id}와 {cur.id}의 Day 범위가 이어지지 않습니다")

    stage_ids = {s.id for s in stages}
    weeks = []
    for i, wk in enumerate(raw.get("weeks", [])):
        week = Week(week=c.require(wk, "week", int, f"weeks[{i}]"), stage=c.require(wk, "stage", str, f"weeks[{i}]"),
                    title=c.require(wk, "title", str, f"weeks[{i}]"))
        if week.stage not in stage_ids:
            c.error(f"weeks[{i}]", f"알 수 없는 stage '{week.stage}'")
        weeks.append(week)

    concepts = c.require(raw, "concepts", dict, "") or {}
    review_every = c.require(raw, "review_every", int, "") or 7

    days: list[DayInfo] = []
    seen_days: set[int] = set()
    for i, d in enumerate(c.require(raw, "days", list, "") or []):
        w = f"days[{i}]"
        info = DayInfo(day=c.require(d, "day", int, w), title=c.require(d, "title", str, w),
                       file=c.require(d, "file", str, w), is_review=c.require(d, "is_review", bool, w))
        if info.day in seen_days:
            c.error(w, f"Day {info.day}가 중복됩니다")
        seen_days.add(info.day)
        if isinstance(info.day, int) and info.is_review != (info.day % review_every == 0):
            c.error(w, f"is_review는 Day 번호가 {review_every}의 배수일 때만 true입니다")
        days.append(info)
    days.sort(key=lambda d: d.day)

    if c.errors:
        raise ContentError(c.errors)
    return Curriculum(title=raw.get("title", "Python Learning Lab"), minutes_per_day=raw.get("minutes_per_day", 15),
                      review_every=review_every, stages=stages, weeks=weeks, concepts=concepts, days=days)


# ---------------------------------------------------------------- lesson

def _parse_quiz(c: _Collector, items: Any, where: str) -> list[QuizItem]:
    out = []
    for i, q in enumerate(items or []):
        w = f"{where}.quiz[{i}]"
        choices = c.require(q, "choices", list, w) or []
        answer = c.require(q, "answer_index", int, w)
        if not 2 <= len(choices) <= 5:
            c.error(w, "선택지는 2~5개여야 합니다")
        if answer is not None and not 0 <= answer < len(choices):
            c.error(w, "answer_index가 선택지 범위를 벗어났습니다")
        out.append(QuizItem(id=c.require(q, "id", str, w), question_md=c.require(q, "question_md", str, w),
                            choices=choices, answer_index=answer if answer is not None else 0,
                            explanation_md=q.get("explanation_md", "")))
    return out


def _parse_test(c: _Collector, t: dict, where: str, mode: str) -> TestCase:
    expect = c.require(t, "expect", dict, where) or {}
    keys = set(expect) & {"stdout", "return", "raises"}
    if not keys:
        c.error(where, "expect에 stdout/return/raises 중 하나 이상이 필요합니다")
    if {"return", "raises"} <= keys:
        c.error(where, "return과 raises는 함께 쓸 수 없습니다")
    if mode == "program" and keys - {"stdout"}:
        c.error(where, "program 모드에서는 expect.stdout만 쓸 수 있습니다")
    if "stdout" in expect and not isinstance(expect["stdout"], str):
        c.error(where, "expect.stdout은 문자열이어야 합니다")
    if "raises" in expect and not isinstance(expect["raises"], str):
        c.error(where, "expect.raises는 예외 이름 문자열이어야 합니다")
    call = t.get("call") or {}
    if mode == "program" and "call" in t:
        c.error(where, "program 모드에서는 call을 쓰지 않습니다")
    compare = t.get("compare") or {}
    cmode = compare.get("mode", "normalized")
    if cmode not in COMPARE_MODES:
        c.error(where, f"알 수 없는 compare.mode '{cmode}'")
    return TestCase(id=c.require(t, "id", str, where), hidden=bool(t.get("hidden", False)),
                    description=t.get("description", ""), expect=expect, stdin=t.get("stdin", ""),
                    args=list(call.get("args", [])), kwargs=dict(call.get("kwargs", {})),
                    compare_mode=cmode, tol=float(compare.get("tol", 1e-6)))


def _parse_exercise(c: _Collector, e: dict, where: str, day: int) -> Exercise:
    entry = c.require(e, "entry", dict, where) or {}
    mode = entry.get("mode")
    if mode not in ("program", "function"):
        c.error(where, "entry.mode는 program 또는 function이어야 합니다")
    if mode == "function" and not isinstance(entry.get("name"), str):
        c.error(where, "function 모드에는 entry.name이 필요합니다")
    kind = c.require(e, "kind", str, where)
    if kind not in ("fill_blank", "coding"):
        c.error(where, "kind는 fill_blank 또는 coding이어야 합니다")

    tests = [_parse_test(c, t, f"{where}.tests[{i}]", mode) for i, t in enumerate(c.require(e, "tests", list, where) or [])]
    test_ids = [t.id for t in tests]
    if len(set(test_ids)) != len(test_ids):
        c.error(where, "테스트 id가 중복됩니다")
    if not any(not t.hidden for t in tests):
        c.error(where, "공개 테스트가 1개 이상 필요합니다")
    # Hidden tests only add value when inputs vary; a fixed-output program has nothing to hide.
    if not any(t.hidden for t in tests) and (mode == "function" or any(t.stdin for t in tests)):
        c.warn(where, "숨김 테스트가 없습니다 (권장: 1개 이상)")

    hints = c.require(e, "hints", list, where) or []
    if not 2 <= len(hints) <= 3:
        c.error(where, "힌트는 2~3개여야 합니다")
    starter = c.require(e, "starter_code", str, where) or ""
    solution = c.require(e, "solution", str, where) or ""
    if kind == "fill_blank":
        if config.BLANK_TOKEN not in starter:
            c.error(where, f"fill_blank의 starter_code에 빈칸 {config.BLANK_TOKEN}이 필요합니다")
        if config.BLANK_TOKEN in solution:
            c.error(where, f"solution에 빈칸 {config.BLANK_TOKEN}이 남아 있습니다")
    _warn_hint_leaks(c, where, hints, solution)

    checks = e.get("checks") or {}
    for key in ("required_syntax", "forbidden_syntax"):
        for name in checks.get(key, []):
            if name not in SUPPORTED_SYNTAX:
                c.error(where, f"checks.{key}: 지원하지 않는 구문 이름 '{name}'")
    unknown = set(checks) - {"required_syntax", "forbidden_syntax", "forbidden_calls", "max_lines"}
    if unknown:
        c.error(where, f"checks에 알 수 없는 키 {sorted(unknown)}")

    difficulty = c.require(e, "difficulty", int, where)
    if difficulty is not None and not 1 <= difficulty <= 3:
        c.error(where, "difficulty는 1~3이어야 합니다")

    return Exercise(id=c.require(e, "id", str, where), day=day, kind=kind, title=c.require(e, "title", str, where),
                    prompt_md=c.require(e, "prompt_md", str, where), concepts=c.require(e, "concepts", list, where) or [],
                    difficulty=difficulty or 1, required=bool(e.get("required", True)), starter_code=starter,
                    entry_mode=mode or "program", function_name=entry.get("name"), tests=tests, hints=hints,
                    solution=solution, checks=checks, time_limit_sec=e.get("time_limit_sec"))


def _warn_hint_leaks(c: _Collector, where: str, hints: list[str], solution: str) -> None:
    """Rule 10: a hint must not contain a solution line verbatim (≥20 chars, whitespace ignored)."""
    squash = lambda s: re.sub(r"\s+", "", s)
    lines = [squash(line) for line in solution.splitlines() if len(squash(line)) >= 20]
    for i, hint in enumerate(hints):
        h = squash(hint)
        if any(line in h for line in lines):
            c.warn(where, f"hints[{i}]에 정답 코드 줄이 그대로 들어 있습니다")


def _is_punct(ch: str) -> bool:
    return unicodedata.category(ch)[0] in "PS"


def markdown_emphasis_issues(text: str) -> list[str]:
    """Find `**bold**` that CommonMark will not render.

    A closing `**` right after punctuation and directly followed by a letter is not
    "right-flanking", so it stays literal. This is common in Korean: `**문자열(str)**입니다`.
    """
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "`C`", text)  # code spans count as punctuation at their edges
    issues = []
    for i, m in enumerate(re.finditer(r"\*\*", text)):
        pos = m.start()
        prev = text[pos - 1] if pos > 0 else " "
        nxt = text[pos + 2] if pos + 2 < len(text) else " "
        if i % 2 == 0:  # opener must be left-flanking
            ok = not nxt.isspace() and (not _is_punct(nxt) or prev.isspace() or _is_punct(prev))
        else:           # closer must be right-flanking
            ok = not prev.isspace() and (not _is_punct(prev) or nxt.isspace() or _is_punct(nxt))
        if not ok:
            issues.append(text[max(0, pos - 12): pos + 14].replace("\n", " "))
    return issues


def _markdown_fields(raw: dict[str, Any]) -> list[tuple[str, str]]:
    """(location, text) for every string the UI renders as Markdown."""
    out: list[tuple[str, str]] = [(f"objectives[{i}]", o) for i, o in enumerate(raw.get("objectives", []))]
    for i, s in enumerate(raw.get("sections", [])):
        w = f"sections[{i}]"
        out += [(w, s.get(k, "")) for k in ("content_md", "intro_md")]
        out += [(f"{w}.blocks[{j}]", b.get("md", "")) for j, b in enumerate(s.get("blocks", []))]
        out += [(f"{w}.points[{j}]", p) for j, p in enumerate(s.get("points", []))]
        for j, q in enumerate(s.get("quiz", []) or []):
            out += [(f"{w}.quiz[{j}]", t) for t in [q.get("question_md", ""), q.get("explanation_md", ""), *q.get("choices", [])]]
    for i, e in enumerate(raw.get("exercises", [])):
        out += [(f"exercises[{i}]", t) for t in [e.get("prompt_md", ""), *e.get("hints", [])]]
    return [(w, t) for w, t in out if isinstance(t, str) and t]


def parse_lesson(raw: dict[str, Any], source: str, curriculum: Curriculum) -> tuple[Lesson, list[str]]:
    """Validate a lesson dict. Returns (lesson, warnings); raises ContentError on errors."""
    c = _Collector(source)
    if raw.get("schema_version") != SCHEMA_VERSION:
        c.error("", f"schema_version은 {SCHEMA_VERSION}이어야 합니다")
    day = c.require(raw, "day", int, "") or 0
    stage = c.require(raw, "stage", str, "")
    if stage and stage not in {s.id for s in curriculum.stages}:
        c.error("", f"알 수 없는 stage '{stage}'")
    concepts = c.require(raw, "concepts", list, "") or []

    exercises = [_parse_exercise(c, e, f"exercises[{i}]", day) for i, e in enumerate(c.require(raw, "exercises", list, "") or [])]
    by_id = {e.id: e for e in exercises}
    if len(by_id) != len(exercises):
        c.error("exercises", "문제 id가 중복됩니다")

    sections: list[Section] = []
    raw_sections = c.require(raw, "sections", list, "") or []
    types = [s.get("type") for s in raw_sections if isinstance(s, dict)]
    if types != SECTION_ORDER:
        c.error("sections", f"섹션 순서는 {' → '.join(SECTION_ORDER)}이어야 합니다 (현재: {types})")
    for i, s in enumerate(raw_sections):
        w = f"sections[{i}]"
        stype = s.get("type")
        blocks = []
        for j, b in enumerate(s.get("blocks", [])):
            kind = b.get("kind")
            if kind not in ("text", "code", "tip"):
                c.error(f"{w}.blocks[{j}]", f"알 수 없는 kind '{kind}'")
            if kind == "code" and b.get("runnable") and not isinstance(b.get("expected_output"), str):
                c.error(f"{w}.blocks[{j}]", "runnable 코드 블록에는 expected_output이 필요합니다")
            blocks.append(Block(kind=kind, md=b.get("md", ""), code=b.get("code", ""), runnable=bool(b.get("runnable")),
                                expected_output=b.get("expected_output")))
        ex_ids = s.get("exercise_ids", [])
        for ex_id in ex_ids:
            if ex_id not in by_id:
                c.error(w, f"없는 문제 id '{ex_id}'를 참조합니다")
            elif by_id[ex_id].kind != stype:
                c.error(w, f"문제 '{ex_id}'의 kind가 섹션 type '{stype}'과 다릅니다")
        if stype in ("fill_blank", "coding") and not ex_ids:
            c.error(w, "exercise_ids가 비어 있습니다")
        quiz = _parse_quiz(c, s.get("quiz"), w)
        if stype == "summary" and not quiz:
            c.error(w, "summary 섹션에는 퀴즈가 1개 이상 필요합니다")
        sections.append(Section(type=stype, minutes=c.require(s, "minutes", int, w) or 0, title=s.get("title", ""),
                                content_md=s.get("content_md", ""), intro_md=s.get("intro_md", ""), blocks=blocks,
                                exercise_ids=ex_ids, points=s.get("points", []), quiz=quiz))
    if sum(s.minutes for s in sections) != curriculum.minutes_per_day:
        c.error("sections", f"minutes 합계는 {curriculum.minutes_per_day}분이어야 합니다")
    referenced = {ex_id for s in sections for ex_id in s.exercise_ids}
    for e in exercises:
        if e.id not in referenced:
            c.warn("exercises", f"'{e.id}'는 어느 섹션에서도 참조되지 않습니다")

    for tag in set(concepts) | {t for e in exercises for t in e.concepts}:
        if tag not in curriculum.concepts:
            c.error("concepts", f"curriculum.concepts에 없는 개념 태그 '{tag}'")

    for where, text in _markdown_fields(raw):
        for snippet in markdown_emphasis_issues(text):
            c.warn(where, f"굵게(**) 표시가 적용되지 않습니다: '…{snippet}…' (닫는 ** 앞뒤 문자를 확인하세요)")

    if c.errors:
        raise ContentError(c.errors)
    lesson = Lesson(day=day, title=c.require(raw, "title", str, ""), stage=stage, week=raw.get("week", 1),
                    is_review=bool(raw.get("is_review", False)), objectives=raw.get("objectives", []),
                    concepts=concepts, sections=sections, exercises=exercises)
    return lesson, c.warnings


# ---------------------------------------------------------------- repository

class ContentRepository:
    """Read-only access to curriculum and lessons, with cross-file ID checks."""

    def __init__(self, content_dir: Path | None = None):
        self.content_dir = Path(content_dir or config.CONTENT_DIR)
        self.curriculum = load_curriculum(self.content_dir)
        self._lessons: dict[int, Lesson] = {}
        self._exercises: dict[str, Exercise] = {}
        self.warnings: list[str] = []
        self._load_all()

    def _load_all(self) -> None:
        errors: list[str] = []
        quiz_ids: set[str] = set()
        for info in self.curriculum.days:
            path = self.content_dir / info.file
            try:
                lesson, warnings = parse_lesson(_read_json(path), path.name, self.curriculum)
            except ContentError as e:
                errors.extend(e.errors)
                continue
            self.warnings.extend(warnings)
            if lesson.day != info.day:
                errors.append(f"{path.name}: day {lesson.day}가 curriculum의 Day {info.day}와 다릅니다")
            if lesson.is_review != info.is_review:
                errors.append(f"{path.name}: is_review가 curriculum과 다릅니다")
            for ex in lesson.exercises:
                if ex.id in self._exercises:
                    errors.append(f"{path.name}: 문제 id '{ex.id}'가 다른 Day와 중복됩니다")
                self._exercises[ex.id] = ex
            for q in (q for s in lesson.sections for q in s.quiz):
                if q.id in quiz_ids:
                    errors.append(f"{path.name}: 퀴즈 id '{q.id}'가 중복됩니다")
                quiz_ids.add(q.id)
            self._lessons[lesson.day] = lesson
        if errors:
            raise ContentError(errors)

    @property
    def available_days(self) -> list[int]:
        return sorted(self._lessons)

    def lesson(self, day: int) -> Lesson:
        try:
            return self._lessons[day]
        except KeyError:
            raise KeyError(f"Day {day} 수업이 아직 없습니다") from None

    def has_lesson(self, day: int) -> bool:
        return day in self._lessons

    def lessons(self) -> list[Lesson]:
        return [self._lessons[d] for d in self.available_days]

    def exercise(self, exercise_id: str) -> Exercise:
        return self._exercises[exercise_id]

    def has_exercise(self, exercise_id: str) -> bool:
        return exercise_id in self._exercises

    def exercises(self) -> list[Exercise]:
        return list(self._exercises.values())
