"""Data classes shared by the engine and the UI. Field meanings: 01_design/content_schema.md."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from lab_app.core.errors import ErrorType, classify_exception


# ---------------------------------------------------------------- content

@dataclass(frozen=True)
class Stage:
    id: str
    order: int
    title: str
    description: str
    weeks: int
    day_range: tuple[int, int]


@dataclass(frozen=True)
class Week:
    week: int
    stage: str
    title: str


@dataclass(frozen=True)
class DayInfo:
    day: int
    title: str
    file: str
    is_review: bool


@dataclass(frozen=True)
class Curriculum:
    title: str
    minutes_per_day: int
    review_every: int
    stages: list[Stage]
    weeks: list[Week]
    concepts: dict[str, str]
    days: list[DayInfo]

    @property
    def total_days(self) -> int:
        return max(s.day_range[1] for s in self.stages)

    def stage_of(self, day: int) -> Stage | None:
        return next((s for s in self.stages if s.day_range[0] <= day <= s.day_range[1]), None)

    def concept_label(self, tag: str) -> str:
        return self.concepts.get(tag, tag)


@dataclass(frozen=True)
class QuizItem:
    id: str
    question_md: str
    choices: list[str]
    answer_index: int
    explanation_md: str


@dataclass(frozen=True)
class Block:
    kind: str                      # text | code | tip
    md: str = ""
    code: str = ""
    runnable: bool = False
    expected_output: str | None = None


@dataclass(frozen=True)
class Section:
    type: str                      # review | concept | fill_blank | coding | summary
    minutes: int
    title: str
    content_md: str = ""
    intro_md: str = ""
    blocks: list[Block] = field(default_factory=list)
    exercise_ids: list[str] = field(default_factory=list)
    points: list[str] = field(default_factory=list)
    quiz: list[QuizItem] = field(default_factory=list)


@dataclass(frozen=True)
class TestCase:
    __test__ = False  # not a pytest test class

    id: str
    hidden: bool
    description: str
    expect: dict[str, Any]         # keys: stdout / return / raises
    stdin: str = ""
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    compare_mode: str = "normalized"
    tol: float = 1e-6


@dataclass(frozen=True)
class Exercise:
    id: str
    day: int
    kind: str                      # fill_blank | coding
    title: str
    prompt_md: str
    concepts: list[str]
    difficulty: int
    required: bool
    starter_code: str
    entry_mode: str                # program | function
    function_name: str | None
    tests: list[TestCase]
    hints: list[str]
    solution: str
    checks: dict[str, Any] = field(default_factory=dict)
    time_limit_sec: float | None = None

    @property
    def public_tests(self) -> list[TestCase]:
        return [t for t in self.tests if not t.hidden]

    @property
    def hidden_tests(self) -> list[TestCase]:
        return [t for t in self.tests if t.hidden]


@dataclass(frozen=True)
class Lesson:
    day: int
    title: str
    stage: str
    week: int
    is_review: bool
    objectives: list[str]
    concepts: list[str]
    sections: list[Section]
    exercises: list[Exercise]

    def section(self, type_: str) -> Section:
        return next(s for s in self.sections if s.type == type_)

    def exercise(self, exercise_id: str) -> Exercise:
        return next(e for e in self.exercises if e.id == exercise_id)

    @property
    def required_exercise_ids(self) -> list[str]:
        return [e.id for e in self.exercises if e.required]

    @property
    def summary_quiz_ids(self) -> list[str]:
        return [q.id for q in self.section("summary").quiz]


# ---------------------------------------------------------------- execution

@dataclass
class ExceptionInfo:
    type: str
    mro_names: list[str]
    message: str
    traceback: str = ""
    lineno: int | None = None

    @property
    def error_type(self) -> ErrorType:
        return classify_exception(self.mro_names)

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> ExceptionInfo | None:
        if not d:
            return None
        return cls(type=d.get("type", "Exception"), mro_names=list(d.get("mro") or [d.get("type", "Exception")]),
                   message=d.get("message", ""), traceback=d.get("traceback", ""), lineno=d.get("lineno"))


@dataclass
class TestOutcome:
    """Raw result of one test from the child process (no pass/fail judgement yet)."""
    __test__ = False  # not a pytest test class

    test_id: str
    status: str                    # ok | exception | output_limit | timeout | crashed | not_run
    stdout: str = ""
    stderr: str = ""
    returned: dict[str, Any] | None = None   # {"type", "json", "json_ok", "repr"}
    exception: ExceptionInfo | None = None
    duration_ms: int | None = None


@dataclass
class ExecutionReport:
    compile_error: ExceptionInfo | None
    outcomes: dict[str, TestOutcome]
    timed_out: bool
    internal_error: str | None
    duration_ms: int


@dataclass
class RunResult:
    """Result of a free "실행" (run) — not graded, not stored as a submission."""
    status: str                    # ok | error | timeout | output_limit | internal_error
    stdout: str
    stderr: str
    error_type: ErrorType
    exception: ExceptionInfo | None
    duration_ms: int


# ---------------------------------------------------------------- grading

@dataclass
class Feedback:
    category: str                  # correctness | readability | logic
    severity: str                  # error | warning | info
    message: str
    line: int | None = None
    source: str = "static"         # static | tests | llm

    def to_dict(self) -> dict[str, Any]:
        return {"category": self.category, "severity": self.severity, "message": self.message,
                "line": self.line, "source": self.source}


@dataclass
class TestResult:
    __test__ = False  # not a pytest test class

    test_id: str
    hidden: bool
    description: str
    passed: bool
    error_type: ErrorType
    message: str
    expected: str | None = None    # None for hidden tests
    actual: str | None = None      # None for hidden tests
    stdout: str | None = None      # public tests only
    traceback: str | None = None   # public tests only
    duration_ms: int | None = None


@dataclass
class GradeResult:
    passed: bool
    error_type: ErrorType
    tests: list[TestResult]
    feedback: list[Feedback]
    public_passed: int
    public_total: int
    hidden_passed: int
    hidden_total: int
    duration_ms: int
    compile_error: ExceptionInfo | None = None

    @property
    def summary(self) -> str:
        if self.passed:
            return "모든 테스트를 통과했습니다."
        return f"{self.error_type.label}: 공개 {self.public_passed}/{self.public_total}, 숨김 {self.hidden_passed}/{self.hidden_total} 통과"
