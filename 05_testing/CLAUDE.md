# 05_testing — 자동 테스트

## Goal
`lab_app/tests/`의 pytest를 점검하고 빈 곳을 채운다.
- Streamlit **AppTest** 기반 화면 스모크 테스트를 추가한다(04단계에서 화면은 수동 검증만 했음).
- 요구사항별로 어떤 테스트가 확인하는지 대응표를 만들고, 빠진 부분을 보완한다.
- 커버리지를 측정하고, 반복 실행으로 결과가 흔들리지 않는지 확인한다.

## Process
1. (2026-10-16) Streamlit 1.66의 `AppTest` API를 확인했다(`from_file`, `switch_page`, 위젯 조회·조작).
   - 탐색 스크립트로 `st.navigation`과 `switch_page`가 동작하는지 확인했다. 커스텀 컴포넌트(코드 에디터)도 오류 없이 넘어간다.
2. **`test_ui.py`** 작성 (16개)
   - 격리: `config.DB_PATH`를 테스트별 임시 DB로 바꾸고, 서비스 캐시(`st.cache_resource`)를 테스트 전후에 비우고, `server.address`를 localhost로 설정했다가 원래 값으로 되돌린다.
   - AppTest는 커스텀 에디터에 글자를 입력할 수 없다. 그래서 서비스로 **초안 코드**를 넣어 에디터 시작 코드로 만든 뒤 실제 버튼을 누르는 방식으로 화면과 서비스의 연결을 검증했다.
   - 첫 실행 결과 15/16 통과. 실패 1건은 `st.code`가 끝 줄바꿈을 지워서 생긴 비교 차이였고, 테스트 기대값을 수정했다(앱 결함 아님).
3. `pytest-cov`를 설치하고 `requirements.txt`에 추가했다. 커버리지를 측정했다(아래 Results).
4. 요구사항 대응 점검에서 빈 곳을 찾아 테스트를 추가했다.
   - **`test_architecture.py`** (17개): 소스를 읽어 구조 규칙을 강제한다.
     - 앱 프로세스 코드에 `exec`/`eval` 호출이 없다(harness 제외).
     - harness는 표준 라이브러리만 import하고, 앱은 harness를 import하지 않는다.
     - 화면 코드는 `sqlite3`·repository·db·runner를 직접 쓰지 않는다.
     - `sqlite3`는 `db.py`·`repository.py`에서만 쓴다.
   - `test_grader.py` +2:
     - `verify_lesson`이 깨진 콘텐츠를 실제로 잡아내는지 확인한다: 틀린 모범 답안, 시작 코드로 통과, 예제 출력 불일치.
     - LLM reviewer 확장 지점을 확인한다: 피드백은 추가되지만 합격 판정은 바뀌지 않는다. Null/Static 구현, `get_reviewer` 동작도 함께 본다.
5. 전체 스위트를 2회 실행했다. 두 번 모두 156 passed였고, 시간 의존 테스트(시간 초과·종료)가 흔들리지 않았다. 실제 `lab_app/data/`에는 DB가 생기지 않았다.

## Files
| 파일 | 테스트 수 | 내용 |
|---|---|---|
| `../lab_app/tests/conftest.py` | — | 임시 2일 강의, 고정 시계, 임시 DB 픽스처 |
| `../lab_app/tests/test_runner.py` | 24 | 자식 프로세스 실행: 시간 초과·출력 제한·격리·오류 보고·부분 출력 |
| `../lab_app/tests/test_grader.py` | 28 | 비교 규칙, 정적 검사, 채점 파이프라인, 콘텐츠 자기 검증, reviewer 확장 |
| `../lab_app/tests/test_content.py` | 18 | 콘텐츠 스키마 검증과 오류 메시지 |
| `../lab_app/tests/test_real_content.py` | 19 | 실제 Day 1~7: 자기 검증, 흔한 실수 10가지 |
| `../lab_app/tests/test_progress.py` | 20 | DB, 완료 규칙, 재시작 후 유지, 오답 노트, 힌트·정답 정책, 통계 |
| `../lab_app/tests/test_ui.py` | **16 (신규)** | AppTest 화면 스모크 테스트 |
| `../lab_app/tests/test_architecture.py` | **17 (신규)** | 구조 규칙(실행 안전성, UI/로직 분리) |
| `../requirements.txt` | — | `pytest-cov>=6` 추가 |
| `CLAUDE.md`, `summary.html` | — | 이 단계 기록, 요약 보고서 |

## Results
- **156 passed** (04단계 107 → +49), 약 46~52초, 2회 연속 통과
- 커버리지 89% (2,656줄 중 281줄 미실행)
  - `harness.py` 0%: 자식 프로세스에서 실행되어 측정되지 않을 뿐이다. 실제로는 `test_runner.py` 24개가 모든 경로를 간접 검증한다.
  - 나머지 미실행 줄은 대부분 콘텐츠 오류 메시지 분기, 프로세스 강제 종료 실패 처리, 화면의 예외적 분기(콘텐츠 모두 완료, 빈 목록 등)다.
  - harness를 제외한 모듈은 84~100%다.
- 가장 느린 테스트: 무한 루프 채점(5.3초, 시간 제한 5초가 실제로 지나야 함)

### 요구사항 ↔ 테스트 대응표
| 요구사항 | 확인하는 테스트 |
|---|---|
| 별도 프로세스 실행, app에서 exec/eval 금지 | `test_architecture::test_app_process_never_execs_user_code`, `test_runner::test_child_cannot_import_app_package` |
| 시간 초과·출력량 제한·오류 처리, 앱이 멈추지 않음 | `test_runner`의 timeout / output_flood / hard_exit / long_running 테스트 |
| 출력·반환값·예외 검사, 공개/숨김 테스트 | `test_grader` 비교·예외 테스트, `test_hidden_test_details_are_not_exposed` |
| 정답 비공개, 단계별 힌트, 정답 확인 | `test_progress::test_solution_requires_a_submission`, `test_hints_open_one_at_a_time`, `test_ui::test_wrong_answer_hint_and_solution_flow` |
| 가독성·논리 평가 구조, LLM 확장 | `test_static_checks_*`, `test_reviewer_hook_adds_feedback_without_changing_the_verdict` |
| 문제를 안 풀면 완료되지 않음 | `test_progress::test_lesson_is_not_completed_without_solving` 외 3개, `test_real_content::test_lesson_self_check`(시작 코드 불통과) |
| 앱 재시작 후 기록 유지 | `test_progress::test_progress_survives_restart` |
| 오답 노트·재도전·반복 실수 통계 | `test_progress::test_wrong_note_lifecycle`, `test_ui::test_wrong_note_retry_opens_practice` |
| 학습 일수·연속 학습·정답률·취약 개념·이어하기 | `test_progress` 통계 테스트 5개, `test_ui::test_history_shows_records_and_resume` |
| 7일마다 누적 복습, Day 1~7 콘텐츠 | `test_real_content::test_week_one_is_complete_and_clean` |
| 콘텐츠와 UI 분리, 콘텐츠 오류 시 안내 | `test_content.py`, `test_ui::test_broken_content_shows_readable_error`, `test_architecture::test_ui_does_not_touch_storage_directly` |
| 화면 5개 동작, 사이드바 | `test_ui::test_every_page_renders_on_a_fresh_db` ×5 외 |
| 로컬 전용 실행 | `test_ui::test_guard_blocks_non_local_address` |

## Issues & open questions
- **자동화되지 않은 부분**: 코드 에디터 입력(커스텀 컴포넌트), 라이트/다크 테마의 시각적 확인, 브라우저 자동 열기(`run_app.cmd`). 모두 04단계에서 수동 확인했고, 06단계에서 실제 실행으로 다시 본다.
- AppTest 실행 시 "missing ScriptRunContext" 로그 경고가 나온다. Streamlit이 bare mode에서 내는 정상 메시지다.
- harness 커버리지를 수치로 보려면 coverage의 서브프로세스 측정 설정이 필요하다. 이득이 작아서 하지 않았다.
- 전체 실행 시간 약 50초 중 대부분은 실제 자식 프로세스와 시간 초과 대기다.

## Status
Done — 화면 스모크 테스트·구조 규칙 테스트 추가, 156개 통과, 커버리지 89% (last updated: 2026-10-16)
