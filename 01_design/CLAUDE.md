# 01_design — 요구사항 분석 및 구조 설계

## Goal
Python Learning Lab MVP의 요구사항을 정리하고, 이후 단계가 그대로 따라 구현할 수 있도록 다음을 설계한다.
- 전체 아키텍처(UI / 코어 엔진 / 콘텐츠 / 저장소 / 향후 LLM 모듈 분리)
- SQLite 스키마(진도, 제출 코드, 테스트 결과, 오답)
- 커리큘럼·수업·문제 JSON 스키마
- 채점 방식(공개/숨김 테스트, 출력·반환값·예외 검사)과 실행 안전성 정책

## Process
1. (2026-10-16) 프로젝트 폴더 상태 확인: `python_train/`은 비어 있음. Python 3.14.6 설치 확인.
2. (2026-10-16) 폴더 구조 결정 및 사용자 확인 완료.
   - 단계 폴더(`01_`~`06_`)에는 **작업 기록**을 두고, 실행 코드는 **`lab_app/` 단일 패키지**에 모은다.
   - 이유: 숫자로 시작하는 폴더는 Python 패키지로 import할 수 없다.
3. (2026-10-16) 아키텍처 설계 → `architecture.md`. 주요 결정은 다음과 같다.
   - **채점도 자식 프로세스 안에서 한다.** harness가 실제 값만 보고하고 판정은 부모 grader가 한다. 그래서 판정 로직은 subprocess 없이 단위 테스트할 수 있다.
   - **작업 하나당 프로세스 하나**로 실행한다. 테스트마다 새 네임스페이스를 쓰고, 결과는 JSONL로 한 줄씩 기록한다. 테스트마다 프로세스를 띄우면 Windows에서 시작 비용이 크다. 그래서 시간 초과가 나면 결과가 없는 첫 테스트를 timeout으로 판정한다.
   - `python -I -X utf8`로 실행하고, stdout/stderr는 파이프 대신 파일로 받는다(deadlock 방지). 시간 초과 시 `taskkill /T /F`로 프로세스 트리를 종료한다.
   - 출력 상한 초과 예외를 `BaseException` 하위 클래스로 만든다. 사용자의 `except Exception`이 이 예외를 삼키지 못하게 하기 위해서다.
   - 채점 = 평가기 파이프라인(PreCheck → 정적 검사 → 테스트 → 향후 LLM 리뷰). 피드백 범주는 correctness/readability/logic이다.
   - 정답은 제출 1회 이후에만 공개한다. 정답을 본 뒤 통과해도 완료로 인정하되 표시를 남긴다.
   - 수업 완료 조건 = 필수 문제 전부 통과 + 정리 퀴즈 전부 제출. Day는 순서대로 잠금 해제한다.
   - 공통 UI 부품은 새 폴더 대신 `lab_app/components.py`에 둔다.
4. (2026-10-16) SQLite 스키마 설계 → `db_schema.md`, `schema.sql`.
   - 테이블 8개를 만들었다. 콘텐츠 ID(day, exercise_id)는 JSON에 있으므로 FK를 걸지 않고 검증 코드로 일관성을 확인한다.
   - 오답 노트는 문제당 1행(누적 횟수, 해결 여부)으로 하고, 반복 실수 통계는 `submissions.error_type`으로 집계한다.
   - 버전 관리는 `PRAGMA user_version`으로 한다.
5. (2026-10-16) JSON 콘텐츠 스키마 설계 → `content_schema.md`, `example_curriculum.json`, `example_lesson.json`.
   - 섹션은 5개로 고정했다(review 2 / concept 4 / fill_blank 3 / coding 4 / summary 2 = 15분).
   - 테스트 기대값은 `stdout` / `return` / `raises`이고, 비교 모드는 normalized / exact / float / unordered다.
   - Day 1~7 주제 초안: Day 6을 "함수 기초"로 정했다. 반환값·예외 채점을 실제 콘텐츠로 검증하기 위해서다. 리스트는 2주차로 미뤘다.
6. (2026-10-16) 설계 산출물 검증(스크래치 스크립트, 프로젝트 밖에서 실행)
   - `schema.sql`을 인메모리 SQLite에 적용했다: 테이블 8개, user_version=1, FK·CHECK 제약 동작 확인.
   - 예시 JSON 규칙을 확인했다: 섹션 순서·15분·ID 참조·개념 태그·빈칸 규칙, 단계별 Day 범위(=주×7), 7의 배수 = 복습일.
   - 예시 문제를 자식 프로세스에서 실행했다: **solution은 모든 테스트 통과, starter_code는 통과하지 않음**. 실행 가능한 코드 블록 2개는 출력이 expected_output과 같았다.

## Files
- `CLAUDE.md` — 이 단계의 기록 (현재 파일)
- `architecture.md` — 모듈 구성, 실행·채점 설계, 진도 규칙, 화면별 데이터 흐름, LLM 확장 지점
- `db_schema.md` — 테이블 관계, 동작별 쓰기 순서, 통계 쿼리, 오류 유형 목록, 마이그레이션
- `schema.sql` — SQLite DDL v1 (02단계에서 그대로 사용)
- `content_schema.md` — curriculum/lesson/exercise/test JSON 필드 정의, ID 규칙, 검증 규칙, Day 1~7 주제
- `example_curriculum.json` — 4단계·24주·168일 로드맵, 개념 태그 사전, Day 1~7 목록 (03단계 `curriculum.json`의 초안)
- `example_lesson.json` — Day 6(함수 기초) 예시. 모든 섹션 유형과 return/raises/float 비교, 숨김 테스트, 정적 검사 포함
- `summary.html` — 비전문가용 요약 보고서

## Results
- 확정 구조:
```
python_train/
├── index.html · README.md(06) · requirements.txt(02) · pyproject.toml(02, pytest 설정)
├── 01_design/ … 06_release/   단계별 작업 기록
└── lab_app/
    ├── app.py · config.py · components.py
    ├── views/      dashboard · lesson · practice · wrong_notes · history
    ├── core/       models · content · runner · harness · grader · checks · errors · db · repository · progress
    ├── llm/        base.py (CodeReviewer / HintProvider 인터페이스 + Null 구현)
    ├── content/    curriculum.json · lessons/day01~07.json
    ├── data/       learning.db
    └── tests/
```
- DB: 테이블 8개 (lesson_progress, submissions, test_results, exercise_state, wrong_notes, quiz_answers, activity_log, settings)
- 오류 유형 21종 정의 (`db_schema.md` §5)
- 검증 결과: 모든 검사 통과

## Issues & open questions
- 설치된 Python이 3.14.6이다. Streamlit 및 에디터 컴포넌트가 3.14를 지원하는지 02/04단계에서 확인해야 한다. 지원하지 않으면 3.12 가상환경을 검토한다.
- git 저장소 루트가 `C:/Users/jiwoo`(홈 폴더)다. 이 프로젝트용 별도 저장소를 만들지는 아직 정하지 않았다.
- 메모리 사용량 제한은 MVP에서 구현하지 않는다(Windows에 `resource` 모듈 없음). 필요하면 Job Object를 검토한다.
- 숨김 테스트가 JSON에 그대로 있어 파일을 열면 보인다. 개인 학습용이라 허용했다.
- 학습일·연속 학습은 PC 로컬 시간대 기준이다. 자정 전후로 학습하면 날짜가 나뉜다.
- `.streamlit/config.toml`(테마)이 필요하면 04단계에서 폴더 생성 전에 확인을 요청한다.
- `lab_app/` 하위 `.gitkeep`은 실제 파일이 생기면 삭제한다.

## Status
Done — 아키텍처·DB·콘텐츠 스키마 설계 및 검증 완료 (last updated: 2026-10-16)
