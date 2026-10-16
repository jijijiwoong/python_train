"""Service layer: completion rules, persistence, wrong notes, hints/solution policy, statistics."""
from datetime import date

import pytest

from lab_app.core import repository as repo
from lab_app.core.db import SCHEMA_VERSION, init_db, transaction
from lab_app.core.errors import ErrorType
from lab_app.core.progress import LearningService, LockedError, compute_streak

D1_FILL = 'print("hello")\n'
D1_CODE = "n = int(input())\nprint(n * 2)\n"


def _finish_day1(service: LearningService) -> None:
    assert service.submit("d01_fill_1", D1_FILL).result.passed
    assert service.submit("d01_code_1", D1_CODE).result.passed
    service.answer_quiz(1, "d01_summary_q1", 0)  # any answer counts, even a wrong one


# ---------------------------------------------------------------- db

def test_init_db_is_idempotent(db_path):
    assert init_db(db_path) == SCHEMA_VERSION
    assert init_db(db_path) == SCHEMA_VERSION
    with transaction(db_path) as conn:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert {"lesson_progress", "submissions", "test_results", "exercise_state", "wrong_notes",
            "quiz_answers", "activity_log", "settings"} <= tables


def test_settings_roundtrip(db_path):
    init_db(db_path)
    with transaction(db_path) as conn:
        repo.set_setting(conn, "theme", "dark")
        repo.set_setting(conn, "theme", "light")
    with transaction(db_path) as conn:
        assert repo.get_setting(conn, "theme") == "light"


# ---------------------------------------------------------------- unlock & completion

def test_only_first_day_is_unlocked_initially(service):
    assert service.all_statuses() == {1: "not_started", 2: "locked"}
    assert service.today_day() == 1
    with pytest.raises(LockedError):
        service.submit("d02_fill_1", "def add(a, b):\n    return a + b\n")
    with pytest.raises(LockedError):
        service.start_lesson(2)


def test_lesson_is_not_completed_without_solving(service):
    service.start_lesson(1)
    service.answer_quiz(1, "d01_review_q1", 1)
    service.answer_quiz(1, "d01_summary_q1", 1)
    assert service.lesson_status(1) == "in_progress"
    assert service.try_complete_lesson(1) is False
    check = service.checklist(1)
    assert check.remaining_exercises == ["d01_fill_1", "d01_code_1"] and check.remaining_quizzes == []


def test_failed_and_starter_submissions_do_not_complete(service):
    service.answer_quiz(1, "d01_summary_q1", 1)
    service.submit("d01_fill_1", service.content.exercise("d01_fill_1").starter_code)
    service.submit("d01_code_1", "print(6)\n")  # passes the public test only
    assert service.lesson_status(1) == "in_progress"


def test_lesson_completes_when_all_required_pass_and_quiz_answered(service):
    assert service.submit("d01_fill_1", D1_FILL).lesson_completed is False
    assert service.submit("d01_code_1", D1_CODE).lesson_completed is False  # summary quiz still missing
    service.answer_quiz(1, "d01_summary_q1", 0)
    assert service.lesson_status(1) == "completed"
    assert service.all_statuses() == {1: "completed", 2: "not_started"}
    assert service.today_day() == 2


def test_completion_by_last_submission_is_reported(service):
    service.answer_quiz(1, "d01_summary_q1", 1)
    service.submit("d01_fill_1", D1_FILL)
    assert service.submit("d01_code_1", D1_CODE).lesson_completed is True


def test_completed_stays_completed_after_later_failures(service):
    _finish_day1(service)
    service.submit("d01_code_1", "print('oops')\n")
    assert service.lesson_status(1) == "completed"
    assert service.exercise_state("d01_code_1")["status"] == "passed"


def test_progress_survives_restart(content, db_path, clock):
    first = LearningService(content, db_path, clock=clock)
    _finish_day1(first)
    first.save_draft("d02_fill_1", "def add(a, b):\n    return a")
    restarted = LearningService(content, db_path, clock=clock)
    assert restarted.lesson_status(1) == "completed"
    assert restarted.current_code("d02_fill_1") == "def add(a, b):\n    return a"
    assert restarted.dashboard_stats().submissions == 2


# ---------------------------------------------------------------- submissions, wrong notes

def test_submission_and_test_results_are_stored(service, db_path):
    out = service.submit("d01_code_1", "n = input()\nprint(n * 2)\n")
    assert out.result.error_type is ErrorType.WRONG_ANSWER
    with transaction(db_path) as conn:
        sub = repo.get_submission(conn, out.submission_id)
        rows = repo.test_results_for(conn, out.submission_id)
    assert sub["code"].startswith("n = input()") and sub["passed"] == 0 and sub["error_type"] == "wrong_answer"
    hidden = next(r for r in rows if r["hidden"])
    assert hidden["expected"] is None and hidden["actual"] is None


def test_wrong_note_lifecycle(service):
    service.submit("d01_code_1", "print(n)\n")                 # name_error
    service.submit("d01_code_1", "n = input()\nprint(n * 2)\n")  # wrong_answer
    [note] = service.wrong_notes(resolved=False)
    assert note["wrong_count"] == 2 and note["error_type"] is ErrorType.WRONG_ANSWER
    assert note["last_wrong_code"].startswith("n = input()")
    service.set_memo("d01_code_1", "int() 변환 잊지 말기")
    service.submit("d01_code_1", D1_CODE)
    assert service.wrong_notes(resolved=False) == []
    [resolved] = service.wrong_notes(resolved=True)
    assert resolved["memo"] == "int() 변환 잊지 말기"
    assert dict(service.error_stats()) == {ErrorType.NAME_ERROR: 1, ErrorType.WRONG_ANSWER: 1}


def test_internal_errors_are_not_stored(content, db_path, clock):
    from lab_app.core.models import ExecutionReport
    broken = LearningService(content, db_path, clock=clock,
                             executor=lambda code, ex: ExecutionReport(None, {}, False, "boom", 1))
    out = broken.submit("d01_code_1", D1_CODE)
    assert out.submission_id is None and out.result.error_type is ErrorType.INTERNAL_ERROR
    assert broken.exercise_state("d01_code_1")["attempts"] == 0


# ---------------------------------------------------------------- hints & solution

def test_hints_open_one_at_a_time(service):
    ex = service.content.exercise("d01_code_1")
    assert service.revealed_hints(ex.id) == []
    assert service.reveal_next_hint(ex.id) == ex.hints[0]
    assert service.reveal_next_hint(ex.id) == ex.hints[1]
    assert service.reveal_next_hint(ex.id) is None
    assert service.revealed_hints(ex.id) == ex.hints


def test_solution_requires_a_submission(service):
    with pytest.raises(LockedError):
        service.view_solution("d01_code_1")
    service.reveal_next_hint("d01_code_1")
    service.submit("d01_code_1", "print(0)\n")
    assert service.view_solution("d01_code_1") == D1_CODE
    out = service.submit("d01_code_1", D1_CODE)
    sub = service.submission_history("d01_code_1")[0]
    assert out.result.passed and sub["solution_viewed"] == 1 and sub["hints_used"] == 1


# ---------------------------------------------------------------- statistics

def test_streak_rules():
    d = date(2026, 10, 16)
    days = lambda *offsets: {date.fromordinal(d.toordinal() - o) for o in offsets}
    assert compute_streak(set(), d) == 0
    assert compute_streak(days(0, 1, 2), d) == 3
    assert compute_streak(days(1, 2), d) == 2       # today not studied yet: streak still alive
    assert compute_streak(days(0, 2, 3), d) == 1
    assert compute_streak(days(2, 3), d) == 0


def test_dashboard_counts_study_days_and_accuracy(service, clock):
    service.run("print(1)\n")                       # running code alone is not a study day
    assert service.dashboard_stats().study_days == 0
    service.submit("d01_fill_1", "print('hi')\n")   # fail
    clock.advance(days=1)
    service.submit("d01_fill_1", D1_FILL)           # pass
    clock.advance(days=1)
    service.answer_quiz(1, "d01_review_q1", 1)
    stats = service.dashboard_stats()
    assert (stats.study_days, stats.streak) == (3, 3)
    assert (stats.submissions, stats.passed_submissions, stats.accuracy) == (2, 1, 0.5)
    assert stats.quiz_accuracy == 1.0
    assert stats.total_days == 7 and stats.authored_days == 2 and stats.today_day == 1


def test_weak_concepts_and_recommendations(service):
    service.submit("d01_code_1", "print(n)\n")
    service.submit("d01_code_1", "print(m)\n")
    service.submit("d01_fill_1", D1_FILL)
    weak = service.weak_concepts()
    assert [w.tag for w in weak] == ["input"]
    assert weak[0].fail_rate == 1.0 and weak[0].unresolved_notes == 1
    recs = service.recommendations()
    assert recs[0].kind == "wrong_note" and recs[0].exercise_id == "d01_code_1"
    assert recs[-1].kind == "lesson" and recs[-1].day == 1


def test_concept_mastery(service):
    service.submit("d01_fill_1", D1_FILL)
    by_tag = {c["tag"]: c for c in service.concept_mastery()}
    assert by_tag["print"]["solved"] == 1 and by_tag["print"]["accuracy"] == 1.0
    assert by_tag["function"]["solved"] == 0 and by_tag["function"]["accuracy"] is None


def test_resume_point_and_history(service, clock):
    assert service.resume_point() == (1, 0)
    service.view_section(1, 3)
    assert service.resume_point() == (1, 3)
    _finish_day1(service)
    assert service.resume_point() == (2, 0)
    history = service.daily_history()
    assert history[0]["date"] == "2026-10-16" and history[0]["submissions"] == 2
    assert history[0]["passed"] == 2 and history[0]["lessons_completed"] == 1 and history[0]["days"] == [1]


def test_quiz_answers_keep_latest(service):
    assert service.answer_quiz(1, "d01_review_q1", 0) is False
    assert service.answer_quiz(1, "d01_review_q1", 1) is True
    assert service.quiz_answers(1) == {"d01_review_q1": {"selected": 1, "correct": True}}
    with pytest.raises(KeyError):
        service.answer_quiz(1, "missing", 0)
