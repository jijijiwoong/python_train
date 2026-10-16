# SQLite 스키마 설계 — v1

> DDL 원본: [schema.sql](schema.sql) · DB 파일: `lab_app/data/learning.db` (환경변수 `LAB_DB_PATH`로 변경 가능, 테스트에서는 임시 경로 사용)

## 1. 테이블 관계

```
lesson_progress (day) ─┐
                       │ day로 느슨하게 연결 (콘텐츠는 JSON이라 FK 없음)
exercise_state (exercise_id) ──┐
                               │ exercise_id
submissions (id) ◄── test_results.submission_id   (ON DELETE CASCADE)
      ▲
      └──────────── wrong_notes.last_wrong_submission_id

quiz_answers, activity_log, settings — 독립 테이블
```

`exercise_id`와 `day`는 JSON 콘텐츠의 ID다. 콘텐츠가 DB 밖에 있으므로 FK를 걸지 않는다. 대신 앱 시작 시 `content.py` 검증과 pytest로 ID 일관성을 확인한다.

## 2. 테이블 요약

| 테이블 | 한 행의 의미 | 쓰는 시점 | 요구사항 |
|---|---|---|---|
| `lesson_progress` | Day 하나의 진행 상태 | 수업 시작, 섹션 이동, 완료 판정 | 진도 저장, 이어하기 |
| `submissions` | 채점 제출 1회 | 채점 버튼 | 제출 코드·결과 저장, 정답률 |
| `test_results` | 제출 1회 안의 테스트 1개 결과 | 채점 직후 | 테스트 결과 저장 |
| `exercise_state` | 문제 하나의 현재 상태 | 실행/제출/힌트/정답 열람 | 초안 유지, 힌트 단계, 정답 공개 정책 |
| `wrong_notes` | 틀린 적 있는 문제 하나 | 실패 제출 시 생성·갱신, 통과 시 해결 | 오답 노트, 재도전 |
| `quiz_answers` | 퀴즈 응답 1회 | 복습·정리 퀴즈 제출 | 복습/점검, 완료 조건 ② |
| `activity_log` | 학습 활동 1건 | 대부분의 사용자 행동 | 학습일, 연속 학습, 일자별 이력 |
| `settings` | 설정 키-값 | 설정 변경 | 확장용 |

## 3. 주요 동작별 쓰기 순서 (트랜잭션 단위)

### 3.1 채점 제출 — `progress.submit(exercise_id, code)`
하나의 트랜잭션 안에서:
1. `submissions` INSERT (요약 + `feedback_json`)
2. `test_results` INSERT × 테스트 수 (숨김 테스트는 `expected`/`actual`을 NULL로)
3. `exercise_state` UPSERT: `attempts += 1`, `status` = `passed`(통과 시, 이후 되돌리지 않음) 또는 `attempted`, `draft_code` 갱신, 처음 통과했으면 `first_passed_at`
4. 실패 시 `wrong_notes` UPSERT: `wrong_count += 1`, `last_error_type`, `last_wrong_submission_id`, `last_wrong_at`, `resolved = 0`
   통과 시 해당 행이 있으면 `resolved = 1`, `resolved_at`
5. `activity_log` INSERT (`submission`)
6. 커밋 후 `try_complete_lesson(day)` 호출

### 3.2 수업 완료 판정 — `progress.try_complete_lesson(day)`
```sql
-- ① 필수 문제가 모두 passed인가 (필수 문제 ID 목록은 JSON에서 가져온다)
SELECT COUNT(*) FROM exercise_state
 WHERE exercise_id IN (:required_ids) AND status = 'passed';      -- = len(required_ids) 이어야 함
-- ② 정리 퀴즈를 모두 제출했는가
SELECT COUNT(DISTINCT quiz_id) FROM quiz_answers
 WHERE day = :day AND section = 'summary';                          -- = 정리 퀴즈 개수 이어야 함
```
두 조건을 모두 만족할 때만 `lesson_progress.status = 'completed'`, `completed_at`을 기록하고 `activity_log`(`lesson_completed`)를 남긴다. 이미 완료된 Day는 되돌리지 않는다.

## 4. 통계 쿼리 (대시보드·기록)

```sql
-- 학습일 목록 (연속 학습은 Python에서 날짜를 거꾸로 세어 계산)
SELECT DISTINCT local_date FROM activity_log
 WHERE event_type IN ('submission', 'quiz_answered', 'lesson_completed')
 ORDER BY local_date DESC;

-- 누적 정답률
SELECT COALESCE(SUM(passed), 0), COUNT(*) FROM submissions;

-- 반복 실수 통계 (오류 유형별)
SELECT error_type, COUNT(*) AS n FROM submissions
 WHERE passed = 0 GROUP BY error_type ORDER BY n DESC;

-- 일자별 이력
SELECT local_date,
       COUNT(*)                     AS submissions,
       SUM(passed)                  AS passed,
       COUNT(DISTINCT exercise_id)  AS exercises
  FROM submissions GROUP BY local_date ORDER BY local_date DESC;

-- 문제별 제출·실패 수 → Python에서 JSON의 개념 태그와 합쳐 개념별 성취도·취약 개념 계산
SELECT exercise_id, COUNT(*) AS n, SUM(1 - passed) AS failed
  FROM submissions GROUP BY exercise_id;
```

## 5. 오류 유형 (`error_type` 값)

`core/errors.py`의 `ErrorType`과 똑같이 맞춘다. 한국어 라벨은 UI 표시용이다.

| 값 | 라벨 | 발생 조건 |
|---|---|---|
| `none` | 통과 | — |
| `syntax_error` | 문법 오류 | `SyntaxError` (아래 두 가지 제외) |
| `indentation_error` | 들여쓰기 오류 | `IndentationError`, `TabError` |
| `name_error` | 이름 오류 | `NameError`, `UnboundLocalError` |
| `type_error` | 자료형 오류 | `TypeError` |
| `value_error` | 값 오류 | `ValueError` |
| `index_error` | 인덱스 범위 오류 | `IndexError` |
| `key_error` | 키 오류 | `KeyError` |
| `attribute_error` | 속성 오류 | `AttributeError` |
| `zero_division` | 0으로 나누기 | `ZeroDivisionError` |
| `eof_error` | 입력 부족 | `EOFError` (`input()` 호출이 입력보다 많음) |
| `runtime_error` | 기타 실행 오류 | 위에 없는 예외 |
| `wrong_answer` | 오답 | 실행은 됐지만 출력/반환값이 다름 |
| `wrong_exception` | 예외 불일치 | 예외를 기대했는데 발생하지 않았거나 종류가 다름 |
| `timeout` | 시간 초과 | 제한 시간 초과 (무한 루프 등) |
| `output_limit` | 출력 초과 | 출력 상한 초과 |
| `unfilled_blank` | 빈칸 미완성 | 빈칸 표시 `____`가 남아 있음 |
| `empty_code` | 코드 없음 | 공백만 있는 코드 |
| `static_check_failed` | 조건 미충족 | 필수 구문 누락, 금지 구문 사용 등 |
| `not_run` | 실행 안 됨 | 앞선 시간 초과로 실행되지 못한 테스트 (test_results에서만 사용) |
| `internal_error` | 내부 오류 | harness 자체 오류. 사용자 실수로 집계하지 않음 |

## 6. 마이그레이션
- `PRAGMA user_version`으로 스키마 버전을 관리한다. `db.init_db()`는 현재 버전보다 높은 마이그레이션만 순서대로 적용한다.
- v1 = `schema.sql`. 이후 컬럼을 추가할 때는 `ALTER TABLE` 마이그레이션 v2, v3…을 추가한다. 기존 학습 기록은 지우지 않는다.
- 연결마다 `PRAGMA foreign_keys = ON`을 실행한다. 이 설정은 연결 단위라 매번 켜야 한다.
