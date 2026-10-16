# 02_core_engine — 코드 실행기 · 채점기 · 저장소

## Goal
UI와 독립적으로 동작하는 핵심 엔진을 `lab_app/core/`에 구현한다.
- `runner` + `harness`: 사용자 코드를 **별도 프로세스**로 실행한다. 시간 초과, 출력량 제한, 오류 처리를 맡고, 메인 앱에서는 exec/eval을 쓰지 않는다.
- `grader`: 공개/숨김 테스트로 채점하고 stdout·반환값·예외를 검사한다. 가독성·논리 평가를 붙일 수 있는 확장 구조로 만든다.
- `db` / `repository`: SQLite 스키마와 CRUD
- `progress`: 학습 일수, 연속 학습, 진행률, 정답률, 취약 개념. 문제를 풀지 않으면 완료 처리하지 않는다.
- 의존성 설치

## Process
1. (2026-10-16) 환경 확인: Python 3.14.6, pip 26. Streamlit 최신(1.66.0)이 3.14용으로 배포되어 있음을 확인했다.
2. (2026-10-16) 사용자 확인 후 프로젝트 루트에 가상환경 `.venv/`를 만들었다.
3. 루트 파일을 만들었다.
   - `requirements.txt`: streamlit, pytest
   - `pyproject.toml`: pytest 설정(`pythonpath=["."]`, `testpaths`)
   - `.gitignore`: `.venv`, DB 파일, 캐시
4. `.venv`에 설치했다: **streamlit 1.66.0, pytest 9.1.1**, pip 26.2.1.
5. 모듈 구현 (`lab_app/`):
   - `config.py`: 경로(환경변수 `LAB_DB_PATH`, `LAB_CONTENT_DIR`로 덮어쓰기 가능)와 제한값
   - `core/errors.py`: `ErrorType` 21종, 한국어 라벨, 예외 MRO → 오류 유형 분류, 오류 유형별 일반 팁
   - `core/models.py`: 콘텐츠·실행·채점 데이터 클래스
   - `core/content.py`: JSON 로드와 구조 검증. 설계 문서 §5 규칙 1~5, 9, 10과 Day 간 ID 중복 검사를 한다. 오류는 모두 모아서 한 번에 보고한다.
   - `core/harness.py`: 자식 프로세스 전용이며 stdlib만 쓴다. 테스트마다 새 네임스페이스로 실행하고, 결과는 테스트마다 JSONL 한 줄로 즉시 기록한다.
   - `core/runner.py`: 실행 명령은 `python -I -X utf8 harness.py <임시 폴더>`이다. stdout/stderr는 파일로 받고, 시간 초과 시 `taskkill /T /F`로 프로세스 트리를 종료한다.
   - `core/checks.py`: `ast` 기반 정적 검사(필수/금지 구문, 금지 함수, 줄 수, 긴 줄, 탭 들여쓰기)
   - `core/grader.py`: PreCheck → 정적 검사 → 테스트 → (선택) reviewer 순서의 파이프라인. 비교 규칙은 부모 프로세스에서 판정한다. `verify_lesson()`은 콘텐츠 실행 검증(규칙 6~8)을 한다.
   - `core/db.py`: `PRAGMA user_version` 기반 마이그레이션. v1은 `core/schema_v1.sql`이다.
   - `core/repository.py`: 모든 SQL
   - `core/progress.py`: `LearningService` 서비스 계층. 잠금/완료 규칙, 제출, 힌트·정답 정책, 퀴즈, 오답 노트, 통계, 이어하기를 맡는다.
   - `llm/base.py`: `CodeReviewer`/`HintProvider` 프로토콜, `NullReviewer`, `StaticHintProvider`, `get_reviewer()`
6. 수동 스모크 테스트로 실행기를 확인했다: 정상 실행, 무한 루프(2초 후 종료), 0 나누기, 문법 오류, 출력 폭주, `os._exit`.
7. 테스트 작성 및 실행 (`lab_app/tests/`, 87개, 아래 Results)

### 구현 중 결정·설계 변경 사항
- **`ExceptionInfo.mro` → `mro_names`**: 데이터클래스 필드 이름이 `mro`이면 모든 클래스에 있는 `type.mro` 메서드가 기본값으로 잡혀 오류가 난다(Python 3.14에서 확인).
- **비정상 종료 처리**: 사용자 코드가 `os._exit()` 등으로 결과 없이 프로세스를 끝내면 그 테스트를 `crashed` → `runtime_error`로 처리한다. 사용자 코드가 원인이므로 `internal_error`가 아니다. `internal_error`는 harness 자체 오류에만 쓴다.
- **`input()` 안내 문구**: 채점에서는 안내 문구를 출력에 포함하지 않는다. 그래서 `input("숫자: ")`를 써도 채점에 영향이 없다. 자유 실행에서는 안내 문구와 입력값을 터미널처럼 표시한다. `01_design/content_schema.md`에 반영했다.
- **함수 모드의 `__name__`**: `"user_module"`로 둔다. 사용자가 `if __name__ == "__main__":` 아래에 쓴 테스트 코드는 채점 때 실행되지 않는다.
- **bool ≠ int 비교**: `True`와 `1`은 다르게 판정한다. int와 float는 수치로 비교한다(5 == 5.0).
- **채점 도구 내부 오류는 저장하지 않는다**: 제출 기록·시도 횟수·오답 노트에 반영하지 않는다.
- **빈 코드·빈칸 미완성 제출**: 저장하고 오답으로 기록한다. 실행하지 않고 즉시 반환한다.
- **`schema_v1.sql`**: `01_design/schema.sql`을 복사하고 `user_version` 줄만 뺐다. 이후 버전 관리는 `db.py`가 한다. 앞으로는 이 파일이 기준이다.
- 힌트 누설 검사(규칙 10)는 경고로 처리한다. 콘텐츠를 막지는 않는다.

## Files
| 파일 | 내용 |
|---|---|
| `../requirements.txt`, `../pyproject.toml`, `../.gitignore` | 의존성, pytest 설정, git 제외 목록 |
| `../lab_app/config.py` | 경로·제한값 |
| `../lab_app/core/errors.py` | 오류 유형 |
| `../lab_app/core/models.py` | 데이터 클래스 |
| `../lab_app/core/content.py` | 콘텐츠 로드·검증, `ContentRepository` |
| `../lab_app/core/harness.py` | 자식 프로세스 스크립트 |
| `../lab_app/core/runner.py` | `run_program()`, `run_tests()` |
| `../lab_app/core/checks.py` | 정적 검사 |
| `../lab_app/core/grader.py` | `grade()`, `verify_lesson()` |
| `../lab_app/core/db.py`, `schema_v1.sql` | 연결, 마이그레이션 |
| `../lab_app/core/repository.py` | SQL |
| `../lab_app/core/progress.py` | `LearningService` |
| `../lab_app/llm/base.py` | LLM 확장 인터페이스 |
| `../lab_app/tests/conftest.py` | 임시 2일짜리 강의, 고정 시계, 임시 DB 픽스처 |
| `../lab_app/tests/test_runner.py` | 실행기 23개 |
| `../lab_app/tests/test_grader.py` | 비교·정적 검사·채점 파이프라인 26개 |
| `../lab_app/tests/test_content.py` | 콘텐츠 검증 18개 (01_design 예시 Day 6 검증 포함) |
| `../lab_app/tests/test_progress.py` | DB·완료 규칙·오답 노트·통계 20개 |
| `CLAUDE.md`, `summary.html` | 이 단계 기록, 요약 보고서 |

## Results
- `.venv\Scripts\python -m pytest` → **87 passed** (약 15초). 경고 0개. 테스트가 실제 `lab_app/data/`에 DB를 만들지 않음을 확인했다.
- 검증한 주요 동작:
  - 무한 루프·`sleep(30)`은 제한 시간 뒤 강제 종료되고 앱은 계속 동작한다. 여러 테스트 중 멈춘 테스트만 `timeout`, 나머지는 `not_run`이 된다.
  - 출력 폭주는 2만 자에서 끊긴다. `except Exception:`으로도 이 제한을 피할 수 없다.
  - 자식 프로세스는 앱 패키지를 import할 수 없고(격리 모드), 임시 폴더에서 실행된다.
  - traceback에는 사용자 코드(`main.py`)의 줄만 남는다.
  - 숨김 테스트는 입력·기대값·실제값이 화면 데이터와 DB 어디에도 저장·노출되지 않는다.
  - 문제를 풀지 않거나(시작 코드, 공개 테스트만 맞춤) 정리 퀴즈를 내지 않으면 수업은 완료되지 않는다. 완료된 수업은 이후 오답으로 되돌아가지 않는다.
  - 앱을 다시 시작해도(새 `LearningService`) 진도·초안·제출 기록이 유지된다.
  - 정답은 제출 1회 전에는 잠겨 있다. 정답 열람·힌트 사용 횟수는 제출 기록에 남는다.
  - 연속 학습 계산: 오늘 아직 학습하지 않았으면 어제까지의 연속 기록을 유지한다. 코드 실행만 한 날은 학습일이 아니다.
  - `01_design/example_lesson.json`이 실제 검증기와 채점기를 통과한다.

## Issues & open questions
- **실행 속도**: 제출 한 번에 자식 프로세스 1개를 띄우며 약 130~150 ms 걸린다. 개인 사용에는 충분하다.
- **메모리 제한 없음**(Windows). 거대한 리스트를 만들면 PC 메모리를 쓴다. 시간 제한으로 대부분 끊긴다.
- 자식 프로세스에 앱의 환경변수를 넘긴다(`PYTHON*`, `STREAMLIT*` 제외). 3·4단계에서 numpy/torch를 쓸 때 필요하기 때문이다. 개인 로컬 사용 전제를 유지한다.
- 콘텐츠(`lab_app/content/`)가 아직 없어서 앱 전체는 아직 실행할 수 없다(03단계).
- 코드 에디터 컴포넌트(문법 하이라이팅)는 04단계에서 선택하고 requirements에 추가한다.
- git 저장소 루트 문제(홈 폴더)는 그대로다.

## Status
Done — 엔진 구현, 의존성 설치, 테스트 87개 통과 (last updated: 2026-10-16)
