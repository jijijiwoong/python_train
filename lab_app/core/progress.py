"""Service layer used by the UI: lesson flow, submissions, completion rules, statistics.

Rules: 01_design/architecture.md §6. Pages call only this module (plus content models);
SQL stays in repository.py, execution in runner.py, judgement in grader.py.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from lab_app import config
from lab_app.core import repository as repo
from lab_app.core.content import ContentRepository
from lab_app.core.db import init_db, transaction
from lab_app.core.errors import ErrorType
from lab_app.core.grader import Executor, grade
from lab_app.core.models import Exercise, GradeResult, RunResult
from lab_app.core.runner import run_program, run_tests
from lab_app.llm.base import CodeReviewer


class LockedError(Exception):
    """The lesson or solution is not available yet."""


@dataclass
class SubmitOutcome:
    result: GradeResult
    submission_id: int | None      # None when not stored (internal grader error)
    lesson_completed: bool         # True only on the submission that completed the lesson


@dataclass
class LessonChecklist:
    required_ids: list[str]
    passed_ids: list[str]
    quiz_ids: list[str]
    answered_quiz_ids: list[str]
    completed: bool

    @property
    def remaining_exercises(self) -> list[str]:
        return [e for e in self.required_ids if e not in self.passed_ids]

    @property
    def remaining_quizzes(self) -> list[str]:
        return [q for q in self.quiz_ids if q not in self.answered_quiz_ids]


@dataclass
class WeakConcept:
    tag: str
    label: str
    submissions: int
    failed: int
    unresolved_notes: int

    @property
    def fail_rate(self) -> float:
        return self.failed / self.submissions if self.submissions else 0.0


@dataclass
class Recommendation:
    kind: str                      # wrong_note | lesson
    day: int
    title: str
    reason: str
    exercise_id: str | None = None


@dataclass
class DashboardStats:
    today_day: int | None
    study_days: int
    streak: int
    completed_days: int
    total_days: int
    authored_days: int
    submissions: int
    passed_submissions: int
    quiz_answers: int
    quiz_correct: int
    weak_concepts: list[WeakConcept] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)

    @property
    def curriculum_progress(self) -> float:
        return self.completed_days / self.total_days if self.total_days else 0.0

    @property
    def accuracy(self) -> float | None:
        return self.passed_submissions / self.submissions if self.submissions else None

    @property
    def quiz_accuracy(self) -> float | None:
        return self.quiz_correct / self.quiz_answers if self.quiz_answers else None


def compute_streak(dates: set[date], today: date) -> int:
    """Consecutive study days ending today, or yesterday if today has no activity yet."""
    day = today if today in dates else today - timedelta(days=1)
    streak = 0
    while day in dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _local_now() -> datetime:
    return datetime.now().astimezone()


class LearningService:
    def __init__(self, content: ContentRepository, db_path: Path | None = None, *,
                 clock: Callable[[], datetime] = _local_now, executor: Executor = run_tests,
                 reviewer: CodeReviewer | None = None):
        self.content = content
        self.db_path = Path(db_path or config.DB_PATH)
        self.clock = clock
        self.executor = executor
        self.reviewer = reviewer
        init_db(self.db_path)

    def _tx(self):
        return transaction(self.db_path)

    # ------------------------------------------------------------ lesson flow

    def lesson_status(self, day: int) -> str:
        """locked | not_started | in_progress | completed"""
        if not self.is_unlocked(day):
            return "locked"
        with self._tx() as conn:
            row = repo.get_lesson_progress(conn, day)
        return row["status"] if row else "not_started"

    def is_unlocked(self, day: int) -> bool:
        days = self.content.available_days
        if day not in days:
            return False
        index = days.index(day)
        if index == 0:
            return True
        with self._tx() as conn:
            prev = repo.get_lesson_progress(conn, days[index - 1])
        return prev is not None and prev["status"] == "completed"

    def all_statuses(self) -> dict[int, str]:
        with self._tx() as conn:
            rows = repo.all_lesson_progress(conn)
        out: dict[int, str] = {}
        prev_completed = True
        for day in self.content.available_days:
            status = rows[day]["status"] if day in rows else "not_started"
            out[day] = status if prev_completed else "locked"
            prev_completed = status == "completed"
        return out

    def today_day(self) -> int | None:
        """The lowest unlocked, not-yet-completed lesson; None when every written lesson is done."""
        return next((d for d, s in self.all_statuses().items() if s in ("not_started", "in_progress")), None)

    def _require_unlocked(self, day: int) -> None:
        if not self.is_unlocked(day):
            raise LockedError(f"Day {day}는 아직 잠겨 있습니다. 이전 수업을 먼저 완료하세요.")

    def start_lesson(self, day: int) -> None:
        self._require_unlocked(day)
        now = self.clock()
        with self._tx() as conn:
            if repo.mark_lesson_started(conn, day, now):
                repo.log_activity(conn, "lesson_started", now, day=day)

    def view_section(self, day: int, index: int) -> None:
        """Remember the section for "이어하기". The UI should call this only when the section changes."""
        self._require_unlocked(day)
        now = self.clock()
        with self._tx() as conn:
            repo.mark_lesson_started(conn, day, now)
            repo.set_current_section(conn, day, index, now)
            repo.log_activity(conn, "section_viewed", now, day=day, detail={"section": index})

    def checklist(self, day: int) -> LessonChecklist:
        lesson = self.content.lesson(day)
        with self._tx() as conn:
            states = repo.all_exercise_states(conn)
            answered = repo.answered_quiz_ids(conn, day, "summary")
            row = repo.get_lesson_progress(conn, day)
        passed = [e for e in lesson.required_exercise_ids if e in states and states[e]["status"] == "passed"]
        return LessonChecklist(lesson.required_exercise_ids, passed, lesson.summary_quiz_ids,
                               [q for q in lesson.summary_quiz_ids if q in answered],
                               completed=bool(row and row["status"] == "completed"))

    def try_complete_lesson(self, day: int) -> bool:
        """Complete the lesson iff every required exercise passed and every summary quiz was answered.
        Returns True only when this call changed the status to completed."""
        check = self.checklist(day)
        if check.completed or check.remaining_exercises or check.remaining_quizzes:
            return False
        now = self.clock()
        with self._tx() as conn:
            repo.mark_lesson_started(conn, day, now)
            repo.mark_lesson_completed(conn, day, now)
            repo.log_activity(conn, "lesson_completed", now, day=day)
        return True

    # ------------------------------------------------------------ exercises

    def exercise_state(self, exercise_id: str) -> dict[str, Any]:
        with self._tx() as conn:
            row = repo.get_exercise_state(conn, exercise_id)
        if row is None:
            return {"status": "unsolved", "attempts": 0, "hints_revealed": 0, "solution_viewed": False, "draft_code": None}
        return {"status": row["status"], "attempts": row["attempts"], "hints_revealed": row["hints_revealed"],
                "solution_viewed": bool(row["solution_viewed"]), "draft_code": row["draft_code"]}

    def current_code(self, exercise_id: str) -> str:
        """Draft code if any, otherwise the starter code."""
        draft = self.exercise_state(exercise_id)["draft_code"]
        return draft if draft is not None else self.content.exercise(exercise_id).starter_code

    def save_draft(self, exercise_id: str, code: str) -> None:
        ex = self.content.exercise(exercise_id)
        with self._tx() as conn:
            repo.save_draft(conn, exercise_id, ex.day, code, self.clock())

    def run(self, code: str, stdin: str = "", exercise_id: str | None = None) -> RunResult:
        """Free run: not graded, not a submission. Saves the draft when tied to an exercise."""
        result = run_program(code, stdin)
        now = self.clock()
        with self._tx() as conn:
            day = None
            if exercise_id is not None:
                day = self.content.exercise(exercise_id).day
                repo.save_draft(conn, exercise_id, day, code, now)
            repo.log_activity(conn, "code_run", now, day=day, exercise_id=exercise_id,
                              detail={"status": result.status})
        return result

    def submit(self, exercise_id: str, code: str) -> SubmitOutcome:
        ex = self.content.exercise(exercise_id)
        self._require_unlocked(ex.day)
        result = grade(ex, code, execute=self.executor, reviewer=self.reviewer)
        if result.error_type is ErrorType.INTERNAL_ERROR:
            return SubmitOutcome(result, None, False)  # the grader's fault; do not count it

        now = self.clock()
        with self._tx() as conn:
            state = repo.get_exercise_state(conn, exercise_id)
            if repo.mark_lesson_started(conn, ex.day, now):
                repo.log_activity(conn, "lesson_started", now, day=ex.day)
            sid = repo.insert_submission(
                conn, exercise_id=exercise_id, day=ex.day, kind=ex.kind, code=code, result=result,
                hints_used=state["hints_revealed"] if state else 0,
                solution_viewed=bool(state and state["solution_viewed"]), now=now)
            repo.record_attempt(conn, exercise_id, ex.day, code, result.passed, now)
            if result.passed:
                repo.resolve_wrong(conn, exercise_id, now)
            else:
                repo.record_wrong(conn, exercise_id, ex.day, str(result.error_type), sid, now)
            repo.log_activity(conn, "submission", now, day=ex.day, exercise_id=exercise_id,
                              detail={"passed": result.passed, "error_type": str(result.error_type)})
        completed = self.try_complete_lesson(ex.day) if result.passed else False
        return SubmitOutcome(result, sid, completed)

    def revealed_hints(self, exercise_id: str) -> list[str]:
        ex = self.content.exercise(exercise_id)
        return ex.hints[: self.exercise_state(exercise_id)["hints_revealed"]]

    def reveal_next_hint(self, exercise_id: str) -> str | None:
        """Open one more hint (staged, never the full solution). None when all are open."""
        ex = self.content.exercise(exercise_id)
        opened = self.exercise_state(exercise_id)["hints_revealed"]
        if opened >= len(ex.hints):
            return None
        now = self.clock()
        with self._tx() as conn:
            repo.set_hints_revealed(conn, exercise_id, ex.day, opened + 1, now)
            repo.log_activity(conn, "hint_revealed", now, day=ex.day, exercise_id=exercise_id,
                              detail={"level": opened + 1})
        return ex.hints[opened]

    def can_view_solution(self, exercise_id: str) -> bool:
        return self.exercise_state(exercise_id)["attempts"] >= config.SOLUTION_UNLOCK_ATTEMPTS

    def view_solution(self, exercise_id: str) -> str:
        if not self.can_view_solution(exercise_id):
            raise LockedError("정답은 한 번 이상 제출한 뒤에 볼 수 있습니다.")
        ex = self.content.exercise(exercise_id)
        now = self.clock()
        with self._tx() as conn:
            already = repo.get_exercise_state(conn, exercise_id)["solution_viewed"]
            repo.mark_solution_viewed(conn, exercise_id, ex.day, now)
            if not already:
                repo.log_activity(conn, "solution_viewed", now, day=ex.day, exercise_id=exercise_id)
        return ex.solution

    # ------------------------------------------------------------ quizzes

    def answer_quiz(self, day: int, quiz_id: str, selected_index: int) -> bool:
        self._require_unlocked(day)
        lesson = self.content.lesson(day)
        section, quiz = next(((s.type, q) for s in lesson.sections for q in s.quiz if q.id == quiz_id), (None, None))
        if quiz is None:
            raise KeyError(f"Day {day}에 퀴즈 '{quiz_id}'가 없습니다")
        correct = selected_index == quiz.answer_index
        now = self.clock()
        with self._tx() as conn:
            if repo.mark_lesson_started(conn, day, now):
                repo.log_activity(conn, "lesson_started", now, day=day)
            repo.insert_quiz_answer(conn, day, quiz_id, section, selected_index, correct, now)
            repo.log_activity(conn, "quiz_answered", now, day=day, detail={"quiz_id": quiz_id, "correct": correct})
        if section == "summary":
            self.try_complete_lesson(day)
        return correct

    def quiz_answers(self, day: int) -> dict[str, dict[str, Any]]:
        """Latest answer per quiz: {quiz_id: {"selected": int, "correct": bool}}."""
        with self._tx() as conn:
            rows = repo.latest_quiz_answers(conn, day)
        return {qid: {"selected": r["selected_index"], "correct": bool(r["correct"])} for qid, r in rows.items()}

    # ------------------------------------------------------------ wrong notes & stats

    def wrong_notes(self, resolved: bool | None = False) -> list[dict[str, Any]]:
        with self._tx() as conn:
            rows = repo.list_wrong_notes(conn, resolved)
        notes = []
        for r in rows:
            ex = self.content.exercise(r["exercise_id"]) if self.content.has_exercise(r["exercise_id"]) else None
            notes.append({
                "exercise_id": r["exercise_id"], "day": r["day"], "title": ex.title if ex else r["exercise_id"],
                "concepts": ex.concepts if ex else [], "wrong_count": r["wrong_count"],
                "error_type": ErrorType(r["last_error_type"]), "last_wrong_code": r["last_wrong_code"],
                "last_wrong_at": r["last_wrong_at"], "resolved": bool(r["resolved"]), "memo": r["memo"] or "",
            })
        return notes

    def set_memo(self, exercise_id: str, memo: str) -> None:
        with self._tx() as conn:
            repo.set_wrong_note_memo(conn, exercise_id, memo)

    def error_stats(self) -> list[tuple[ErrorType, int]]:
        """Failed submissions per error type (repeated-mistake statistics)."""
        with self._tx() as conn:
            counts = repo.error_type_counts(conn)
        return [(ErrorType(et), n) for et, n in counts if ErrorType(et).is_user_mistake]

    def submission_history(self, exercise_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with self._tx() as conn:
            rows = repo.submissions_for(conn, exercise_id, limit)
        return [dict(r) for r in rows]

    def daily_history(self, limit: int = 60) -> list[dict[str, Any]]:
        with self._tx() as conn:
            return repo.daily_history(conn, limit)

    def concept_mastery(self) -> list[dict[str, Any]]:
        """Per concept tag in written lessons: exercises solved and submission accuracy."""
        with self._tx() as conn:
            states = repo.all_exercise_states(conn)
            stats = repo.per_exercise_stats(conn)
        agg: dict[str, dict[str, Any]] = {}
        for ex in self.content.exercises():
            for tag in ex.concepts:
                a = agg.setdefault(tag, {"tag": tag, "label": self.content.curriculum.concept_label(tag),
                                         "exercises": 0, "solved": 0, "submissions": 0, "failed": 0})
                a["exercises"] += 1
                a["solved"] += int(ex.id in states and states[ex.id]["status"] == "passed")
                n, failed = stats.get(ex.id, (0, 0))
                a["submissions"] += n
                a["failed"] += failed
        for a in agg.values():
            a["accuracy"] = (a["submissions"] - a["failed"]) / a["submissions"] if a["submissions"] else None
        return sorted(agg.values(), key=lambda a: a["label"])

    def weak_concepts(self, limit: int = 5) -> list[WeakConcept]:
        with self._tx() as conn:
            stats = repo.per_exercise_stats(conn)
            unresolved = repo.list_wrong_notes(conn, resolved=False)
        per: dict[str, WeakConcept] = {}

        def get(tag: str) -> WeakConcept:
            return per.setdefault(tag, WeakConcept(tag, self.content.curriculum.concept_label(tag), 0, 0, 0))

        for ex_id, (n, failed) in stats.items():
            if self.content.has_exercise(ex_id):
                for tag in self.content.exercise(ex_id).concepts:
                    w = get(tag)
                    w.submissions += n
                    w.failed += failed
        for note in unresolved:
            if self.content.has_exercise(note["exercise_id"]):
                for tag in self.content.exercise(note["exercise_id"]).concepts:
                    get(tag).unresolved_notes += 1
        weak = [w for w in per.values()
                if w.unresolved_notes > 0
                or (w.submissions >= config.WEAK_MIN_SUBMISSIONS and w.fail_rate >= config.WEAK_FAIL_RATE)]
        weak.sort(key=lambda w: (-w.fail_rate, -w.unresolved_notes, -w.submissions, w.tag))
        return weak[:limit]

    def recommendations(self, weak: list[WeakConcept] | None = None) -> list[Recommendation]:
        recs = [Recommendation("wrong_note", n["day"], n["title"], f"{n['error_type'].label} · {n['wrong_count']}회 틀림",
                               exercise_id=n["exercise_id"])
                for n in self.wrong_notes(resolved=False)[:3]]
        weak = self.weak_concepts() if weak is None else weak
        if weak:
            tag = weak[0].tag
            lesson = next((l for l in self.content.lessons() if tag in l.concepts), None)
            if lesson is not None:
                recs.append(Recommendation("lesson", lesson.day, lesson.title, f"취약 개념 '{weak[0].label}' 복습"))
        return recs

    def dashboard_stats(self) -> DashboardStats:
        today = self.clock().date()
        with self._tx() as conn:
            dates = {date.fromisoformat(d) for d in repo.study_dates(conn)}
            passed, total = repo.submission_totals(conn)
            q_correct, q_total = repo.quiz_totals(conn)
        statuses = self.all_statuses()
        weak = self.weak_concepts()
        return DashboardStats(
            today_day=next((d for d, s in statuses.items() if s in ("not_started", "in_progress")), None),
            study_days=len(dates), streak=compute_streak(dates, today),
            completed_days=sum(s == "completed" for s in statuses.values()),
            total_days=self.content.curriculum.total_days, authored_days=len(statuses),
            submissions=total, passed_submissions=passed, quiz_answers=q_total, quiz_correct=q_correct,
            weak_concepts=weak, recommendations=self.recommendations(weak))

    def resume_point(self) -> tuple[int, int] | None:
        """(day, section index) to continue from: the last lesson touched if unfinished, else today's lesson."""
        with self._tx() as conn:
            last = repo.last_activity(conn)
            progress = repo.all_lesson_progress(conn)
        if last is not None:
            day = last["day"]
            row = progress.get(day)
            if row is not None and row["status"] == "in_progress" and self.content.has_lesson(day):
                return day, row["current_section"]
        day = self.today_day()
        if day is None:
            return None
        row = progress.get(day)
        return day, row["current_section"] if row else 0


def exercise_label(ex: Exercise) -> str:
    kind = "빈칸 채우기" if ex.kind == "fill_blank" else "코드 작성"
    return f"Day {ex.day} · {kind} · {ex.title}"
