"""All SQL lives here. Functions take an open connection and an explicit `now` (aware datetime)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from lab_app.core.models import GradeResult


def iso(now: datetime) -> str:
    return now.isoformat(timespec="seconds")


def local_date(now: datetime) -> str:
    return now.date().isoformat()


# ---------------------------------------------------------------- lesson_progress

def get_lesson_progress(conn: sqlite3.Connection, day: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM lesson_progress WHERE day = ?", (day,)).fetchone()


def all_lesson_progress(conn: sqlite3.Connection) -> dict[int, sqlite3.Row]:
    return {r["day"]: r for r in conn.execute("SELECT * FROM lesson_progress")}


def mark_lesson_started(conn: sqlite3.Connection, day: int, now: datetime) -> bool:
    """Create or move a lesson to in_progress. Returns True if it was not started before."""
    row = get_lesson_progress(conn, day)
    if row is None:
        conn.execute("INSERT INTO lesson_progress (day, status, started_at, updated_at) VALUES (?, 'in_progress', ?, ?)",
                     (day, iso(now), iso(now)))
        return True
    if row["status"] == "not_started":
        conn.execute("UPDATE lesson_progress SET status = 'in_progress', started_at = ?, updated_at = ? WHERE day = ?",
                     (iso(now), iso(now), day))
        return True
    return False


def set_current_section(conn: sqlite3.Connection, day: int, section: int, now: datetime) -> None:
    conn.execute("UPDATE lesson_progress SET current_section = ?, updated_at = ? WHERE day = ?", (section, iso(now), day))


def mark_lesson_completed(conn: sqlite3.Connection, day: int, now: datetime) -> None:
    conn.execute("UPDATE lesson_progress SET status = 'completed', completed_at = ?, updated_at = ? WHERE day = ?",
                 (iso(now), iso(now), day))


# ---------------------------------------------------------------- submissions / test_results

def insert_submission(conn: sqlite3.Connection, *, exercise_id: str, day: int, kind: str, code: str,
                      result: GradeResult, hints_used: int, solution_viewed: bool, now: datetime) -> int:
    cur = conn.execute(
        """INSERT INTO submissions (exercise_id, day, kind, code, passed, error_type, public_passed, public_total,
                                    hidden_passed, hidden_total, hints_used, solution_viewed, duration_ms,
                                    feedback_json, submitted_at, local_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (exercise_id, day, kind, code, int(result.passed), str(result.error_type), result.public_passed,
         result.public_total, result.hidden_passed, result.hidden_total, hints_used, int(solution_viewed),
         result.duration_ms, json.dumps([f.to_dict() for f in result.feedback], ensure_ascii=False),
         iso(now), local_date(now)))
    submission_id = cur.lastrowid
    conn.executemany(
        """INSERT INTO test_results (submission_id, test_id, hidden, passed, error_type, message, expected, actual, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(submission_id, t.test_id, int(t.hidden), int(t.passed), str(t.error_type), t.message,
          None if t.hidden else t.expected, None if t.hidden else t.actual, t.duration_ms) for t in result.tests])
    return submission_id


def get_submission(conn: sqlite3.Connection, submission_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()


def submissions_for(conn: sqlite3.Connection, exercise_id: str, limit: int = 20) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM submissions WHERE exercise_id = ? ORDER BY id DESC LIMIT ?",
                        (exercise_id, limit)).fetchall()


def test_results_for(conn: sqlite3.Connection, submission_id: int) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM test_results WHERE submission_id = ? ORDER BY id", (submission_id,)).fetchall()


# ---------------------------------------------------------------- exercise_state

def get_exercise_state(conn: sqlite3.Connection, exercise_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM exercise_state WHERE exercise_id = ?", (exercise_id,)).fetchone()


def all_exercise_states(conn: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    return {r["exercise_id"]: r for r in conn.execute("SELECT * FROM exercise_state")}


def ensure_exercise_state(conn: sqlite3.Connection, exercise_id: str, day: int, now: datetime) -> None:
    conn.execute("INSERT OR IGNORE INTO exercise_state (exercise_id, day, updated_at) VALUES (?, ?, ?)",
                 (exercise_id, day, iso(now)))


def save_draft(conn: sqlite3.Connection, exercise_id: str, day: int, code: str, now: datetime) -> None:
    ensure_exercise_state(conn, exercise_id, day, now)
    conn.execute("UPDATE exercise_state SET draft_code = ?, updated_at = ? WHERE exercise_id = ?",
                 (code, iso(now), exercise_id))


def record_attempt(conn: sqlite3.Connection, exercise_id: str, day: int, code: str, passed: bool, now: datetime) -> None:
    """attempts += 1; status becomes 'passed' on success and never goes back."""
    ensure_exercise_state(conn, exercise_id, day, now)
    conn.execute(
        """UPDATE exercise_state
              SET attempts = attempts + 1,
                  status = CASE WHEN ? THEN 'passed' WHEN status = 'passed' THEN 'passed' ELSE 'attempted' END,
                  first_passed_at = CASE WHEN ? AND first_passed_at IS NULL THEN ? ELSE first_passed_at END,
                  draft_code = ?, updated_at = ?
            WHERE exercise_id = ?""",
        (int(passed), int(passed), iso(now), code, iso(now), exercise_id))


def set_hints_revealed(conn: sqlite3.Connection, exercise_id: str, day: int, count: int, now: datetime) -> None:
    ensure_exercise_state(conn, exercise_id, day, now)
    conn.execute("UPDATE exercise_state SET hints_revealed = MAX(hints_revealed, ?), updated_at = ? WHERE exercise_id = ?",
                 (count, iso(now), exercise_id))


def mark_solution_viewed(conn: sqlite3.Connection, exercise_id: str, day: int, now: datetime) -> None:
    ensure_exercise_state(conn, exercise_id, day, now)
    conn.execute("UPDATE exercise_state SET solution_viewed = 1, updated_at = ? WHERE exercise_id = ?",
                 (iso(now), exercise_id))


# ---------------------------------------------------------------- wrong_notes

def record_wrong(conn: sqlite3.Connection, exercise_id: str, day: int, error_type: str, submission_id: int,
                 now: datetime) -> None:
    conn.execute(
        """INSERT INTO wrong_notes (exercise_id, day, wrong_count, last_error_type, last_wrong_submission_id,
                                    first_wrong_at, last_wrong_at, resolved)
           VALUES (?, ?, 1, ?, ?, ?, ?, 0)
           ON CONFLICT (exercise_id) DO UPDATE SET
               wrong_count = wrong_count + 1, last_error_type = excluded.last_error_type,
               last_wrong_submission_id = excluded.last_wrong_submission_id,
               last_wrong_at = excluded.last_wrong_at, resolved = 0, resolved_at = NULL""",
        (exercise_id, day, error_type, submission_id, iso(now), iso(now)))


def resolve_wrong(conn: sqlite3.Connection, exercise_id: str, now: datetime) -> None:
    conn.execute("UPDATE wrong_notes SET resolved = 1, resolved_at = ? WHERE exercise_id = ? AND resolved = 0",
                 (iso(now), exercise_id))


def list_wrong_notes(conn: sqlite3.Connection, resolved: bool | None = None) -> list[sqlite3.Row]:
    sql = """SELECT w.*, s.code AS last_wrong_code
               FROM wrong_notes w JOIN submissions s ON s.id = w.last_wrong_submission_id"""
    params: tuple = ()
    if resolved is not None:
        sql += " WHERE w.resolved = ?"
        params = (int(resolved),)
    sql += " ORDER BY w.resolved, w.last_wrong_at"
    return conn.execute(sql, params).fetchall()


def set_wrong_note_memo(conn: sqlite3.Connection, exercise_id: str, memo: str) -> None:
    conn.execute("UPDATE wrong_notes SET memo = ? WHERE exercise_id = ?", (memo, exercise_id))


# ---------------------------------------------------------------- quiz_answers

def insert_quiz_answer(conn: sqlite3.Connection, day: int, quiz_id: str, section: str, selected: int,
                       correct: bool, now: datetime) -> None:
    conn.execute("""INSERT INTO quiz_answers (day, quiz_id, section, selected_index, correct, answered_at, local_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                 (day, quiz_id, section, selected, int(correct), iso(now), local_date(now)))


def latest_quiz_answers(conn: sqlite3.Connection, day: int) -> dict[str, sqlite3.Row]:
    rows = conn.execute("""SELECT * FROM quiz_answers WHERE id IN
                             (SELECT MAX(id) FROM quiz_answers WHERE day = ? GROUP BY quiz_id)""", (day,))
    return {r["quiz_id"]: r for r in rows}


def answered_quiz_ids(conn: sqlite3.Connection, day: int, section: str) -> set[str]:
    rows = conn.execute("SELECT DISTINCT quiz_id FROM quiz_answers WHERE day = ? AND section = ?", (day, section))
    return {r[0] for r in rows}


# ---------------------------------------------------------------- activity_log

STUDY_EVENTS = ("submission", "quiz_answered", "lesson_completed")


def log_activity(conn: sqlite3.Connection, event_type: str, now: datetime, *, day: int | None = None,
                 exercise_id: str | None = None, detail: dict[str, Any] | None = None) -> None:
    conn.execute("""INSERT INTO activity_log (event_type, day, exercise_id, detail, occurred_at, local_date)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                 (event_type, day, exercise_id, json.dumps(detail, ensure_ascii=False) if detail else None,
                  iso(now), local_date(now)))


def study_dates(conn: sqlite3.Connection) -> list[str]:
    """Local dates with real study activity (opening a page does not count), newest first."""
    q = f"SELECT DISTINCT local_date FROM activity_log WHERE event_type IN ({','.join('?' * len(STUDY_EVENTS))}) ORDER BY local_date DESC"
    return [r[0] for r in conn.execute(q, STUDY_EVENTS)]


def last_activity(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM activity_log WHERE day IS NOT NULL ORDER BY id DESC LIMIT 1").fetchone()


# ---------------------------------------------------------------- statistics

def submission_totals(conn: sqlite3.Connection) -> tuple[int, int]:
    passed, total = conn.execute("SELECT COALESCE(SUM(passed), 0), COUNT(*) FROM submissions").fetchone()
    return passed, total


def quiz_totals(conn: sqlite3.Connection) -> tuple[int, int]:
    correct, total = conn.execute("SELECT COALESCE(SUM(correct), 0), COUNT(*) FROM quiz_answers").fetchone()
    return correct, total


def error_type_counts(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    rows = conn.execute("""SELECT error_type, COUNT(*) AS n FROM submissions
                            WHERE passed = 0 GROUP BY error_type ORDER BY n DESC, error_type""")
    return [(r["error_type"], r["n"]) for r in rows]


def per_exercise_stats(conn: sqlite3.Connection) -> dict[str, tuple[int, int]]:
    """exercise_id → (submissions, failed submissions)."""
    rows = conn.execute("SELECT exercise_id, COUNT(*) AS n, SUM(1 - passed) AS failed FROM submissions GROUP BY exercise_id")
    return {r["exercise_id"]: (r["n"], r["failed"]) for r in rows}


def daily_history(conn: sqlite3.Connection, limit: int = 60) -> list[dict[str, Any]]:
    rows = conn.execute(
        """SELECT local_date,
                  SUM(event_type = 'submission')       AS submissions,
                  SUM(event_type = 'code_run')         AS runs,
                  SUM(event_type = 'quiz_answered')    AS quizzes,
                  SUM(event_type = 'lesson_completed') AS lessons_completed,
                  GROUP_CONCAT(DISTINCT day)           AS days
             FROM activity_log GROUP BY local_date ORDER BY local_date DESC LIMIT ?""", (limit,)).fetchall()
    passed = dict(conn.execute("SELECT local_date, SUM(passed) FROM submissions GROUP BY local_date").fetchall())
    out = []
    for r in rows:
        days = sorted({int(d) for d in r["days"].split(",")}) if r["days"] else []
        out.append({"date": r["local_date"], "submissions": r["submissions"], "passed": passed.get(r["local_date"], 0),
                    "runs": r["runs"], "quizzes": r["quizzes"], "lessons_completed": r["lessons_completed"], "days": days})
    return out


# ---------------------------------------------------------------- settings

def get_setting(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value",
                 (key, value))
