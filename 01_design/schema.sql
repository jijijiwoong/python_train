-- Python Learning Lab — SQLite schema v1
-- 02_core_engine 단계에서 lab_app/core/db.py의 마이그레이션 v1로 그대로 사용한다.
-- 시간 컬럼(*_at): 로컬 시간대 포함 ISO 8601 문자열 (예: 2026-10-16T21:05:12+09:00)
-- local_date: 로컬 날짜 'YYYY-MM-DD' (학습일·연속 학습 계산용)
-- 불리언 컬럼: INTEGER 0/1

PRAGMA foreign_keys = ON;

-- 수업(Day)별 진행 상태
CREATE TABLE IF NOT EXISTS lesson_progress (
    day             INTEGER PRIMARY KEY,
    status          TEXT    NOT NULL DEFAULT 'not_started'
                    CHECK (status IN ('not_started', 'in_progress', 'completed')),
    current_section INTEGER NOT NULL DEFAULT 0,   -- 이어하기용 섹션 인덱스 (0~4)
    started_at      TEXT,
    completed_at    TEXT,
    updated_at      TEXT    NOT NULL
);

-- 채점 제출 1건 = 1행 (실행(Run)은 저장하지 않음)
CREATE TABLE IF NOT EXISTS submissions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id     TEXT    NOT NULL,
    day             INTEGER NOT NULL,
    kind            TEXT    NOT NULL CHECK (kind IN ('fill_blank', 'coding')),
    code            TEXT    NOT NULL,
    passed          INTEGER NOT NULL CHECK (passed IN (0, 1)),
    error_type      TEXT    NOT NULL,             -- 통과 시 'none'
    public_passed   INTEGER NOT NULL,
    public_total    INTEGER NOT NULL,
    hidden_passed   INTEGER NOT NULL,
    hidden_total    INTEGER NOT NULL,
    hints_used      INTEGER NOT NULL DEFAULT 0,   -- 제출 시점까지 연 힌트 수
    solution_viewed INTEGER NOT NULL DEFAULT 0 CHECK (solution_viewed IN (0, 1)),
    duration_ms     INTEGER,
    feedback_json   TEXT,                         -- Feedback 목록(JSON): 정적 검사, 향후 LLM 리뷰
    submitted_at    TEXT    NOT NULL,
    local_date      TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_submissions_exercise ON submissions (exercise_id, submitted_at);
CREATE INDEX IF NOT EXISTS idx_submissions_date     ON submissions (local_date);
CREATE INDEX IF NOT EXISTS idx_submissions_error    ON submissions (error_type);

-- 제출별 테스트 케이스 결과
CREATE TABLE IF NOT EXISTS test_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id   INTEGER NOT NULL REFERENCES submissions (id) ON DELETE CASCADE,
    test_id         TEXT    NOT NULL,
    hidden          INTEGER NOT NULL CHECK (hidden IN (0, 1)),
    passed          INTEGER NOT NULL CHECK (passed IN (0, 1)),
    error_type      TEXT    NOT NULL,
    message         TEXT,                         -- 사용자에게 보여 줄 한국어 메시지
    expected        TEXT,                         -- 숨김 테스트는 NULL
    actual          TEXT,                         -- 숨김 테스트는 NULL
    duration_ms     INTEGER
);
CREATE INDEX IF NOT EXISTS idx_test_results_submission ON test_results (submission_id);

-- 문제별 현재 상태 (초안 코드, 힌트·정답 열람)
CREATE TABLE IF NOT EXISTS exercise_state (
    exercise_id     TEXT    PRIMARY KEY,
    day             INTEGER NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'unsolved'
                    CHECK (status IN ('unsolved', 'attempted', 'passed')),
    attempts        INTEGER NOT NULL DEFAULT 0,   -- 제출 횟수
    hints_revealed  INTEGER NOT NULL DEFAULT 0,
    solution_viewed INTEGER NOT NULL DEFAULT 0 CHECK (solution_viewed IN (0, 1)),
    draft_code      TEXT,                         -- 마지막 실행/제출 코드 (이어하기)
    first_passed_at TEXT,
    updated_at      TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_exercise_state_day ON exercise_state (day);

-- 오답 노트: 문제당 1행, 통과하면 resolved=1
CREATE TABLE IF NOT EXISTS wrong_notes (
    exercise_id              TEXT    PRIMARY KEY,
    day                      INTEGER NOT NULL,
    wrong_count              INTEGER NOT NULL DEFAULT 1,
    last_error_type          TEXT    NOT NULL,
    last_wrong_submission_id INTEGER NOT NULL REFERENCES submissions (id),
    first_wrong_at           TEXT    NOT NULL,
    last_wrong_at            TEXT    NOT NULL,
    resolved                 INTEGER NOT NULL DEFAULT 0 CHECK (resolved IN (0, 1)),
    resolved_at              TEXT,
    memo                     TEXT
);
CREATE INDEX IF NOT EXISTS idx_wrong_notes_resolved ON wrong_notes (resolved, last_wrong_at);

-- 복습/정리 퀴즈 응답 (같은 퀴즈를 여러 번 풀면 여러 행)
CREATE TABLE IF NOT EXISTS quiz_answers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    day             INTEGER NOT NULL,
    quiz_id         TEXT    NOT NULL,
    section         TEXT    NOT NULL CHECK (section IN ('review', 'summary')),
    selected_index  INTEGER NOT NULL,
    correct         INTEGER NOT NULL CHECK (correct IN (0, 1)),
    answered_at     TEXT    NOT NULL,
    local_date      TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_quiz_answers_day ON quiz_answers (day, quiz_id);

-- 활동 로그: 학습일·연속 학습·일자별 이력 계산
CREATE TABLE IF NOT EXISTS activity_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT    NOT NULL CHECK (event_type IN (
                        'lesson_started', 'section_viewed', 'code_run', 'submission',
                        'quiz_answered', 'hint_revealed', 'solution_viewed', 'lesson_completed')),
    day             INTEGER,
    exercise_id     TEXT,
    detail          TEXT,                         -- 선택적 JSON
    occurred_at     TEXT    NOT NULL,
    local_date      TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_activity_date ON activity_log (local_date, event_type);

-- 앱 설정 키-값 (예: 마지막으로 연 화면, 에디터 테마)
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

PRAGMA user_version = 1;
