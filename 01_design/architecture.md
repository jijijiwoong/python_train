# 아키텍처 설계 — Python Learning Lab MVP

> 작성일: 2026-10-16 · 대상 버전: MVP (Day 1~7)
> 관련 문서: [db_schema.md](db_schema.md), [content_schema.md](content_schema.md)

## 1. 설계 원칙

| 원칙 | 구체적인 의미 |
|---|---|
| 콘텐츠와 코드 분리 | 수업·문제는 모두 `lab_app/content/*.json`에 있다. 새 Day를 추가할 때 Python 코드를 고치지 않는다. |
| UI와 로직 분리 | `views/`는 화면만 그린다. SQL, 채점, 진도 계산은 `core/`의 서비스 함수를 호출한다. 그래서 UI 없이 pytest로 전부 검증할 수 있다. |
| 사용자 코드는 항상 별도 프로세스 | 앱 프로세스는 사용자 코드를 `exec`/`eval`하지 않는다. 실행·채점은 모두 자식 프로세스(`harness.py`)에서 한다. |
| 완료는 증거 기반 | 필수 실습 문제를 통과한 기록(DB)이 있어야 수업이 완료된다. 버튼 클릭만으로는 완료되지 않는다. |
| 확장 지점은 인터페이스로 | 채점은 평가기(Evaluator) 파이프라인이다. LLM 리뷰·힌트는 `llm/` 인터페이스로 나중에 끼워 넣는다. |

## 2. 전체 구조

```
┌──────────────────────── Streamlit 프로세스 (앱) ─────────────────────────┐
│                                                                          │
│  app.py ── st.navigation ──► views/                                      │
│                              dashboard · lesson · practice ·             │
│                              wrong_notes · history                       │
│                                   │ (서비스 함수 호출만)                  │
│                                   ▼                                      │
│  core/                                                                   │
│   content.py ──► content/*.json 로드·검증 (ContentRepository)            │
│   grader.py  ──► 평가기 파이프라인 ─┬─ TestEvaluator ──► runner.py ──────┼──┐
│                                    └─ StaticCheckEvaluator (ast, checks.py)│ │
│   progress.py ─► 완료 규칙, 연속 학습, 정답률, 취약 개념                  │  │
│   repository.py ► SQL 쿼리 ──► db.py ──► data/learning.db (SQLite)       │  │
│   errors.py   ─► 오류 유형 분류·한국어 라벨                               │  │
│  llm/base.py  ─► (향후) CodeReviewer / HintProvider, 기본은 Null 구현     │  │
└──────────────────────────────────────────────────────────────────────────┘  │
                                                                              │ subprocess
┌──────────── 자식 프로세스: python -I -X utf8 harness.py <job_dir> ─────────┐ │
│  job.json + user_code.py 읽기 → 컴파일 → 테스트별 실행 → result.jsonl 기록 │◄┘
│  (stdlib만 사용, 출력량 제한, 테스트마다 새 네임스페이스)                   │
└────────────────────────────────────────────────────────────────────────────┘
```

## 3. 모듈 구성 (`lab_app/`)

| 경로 | 역할 | 주요 함수/클래스 (예정) |
|---|---|---|
| `app.py` | Streamlit 진입점. 프로젝트 루트를 `sys.path`에 추가(실행 방식에 상관없이 `import lab_app` 가능), DB 초기화, 사이드바 내비게이션 구성 | `main()` |
| `config.py` | 경로·제한값 상수. 환경변수로 덮어쓰기 가능 | `DB_PATH`, `CONTENT_DIR`, `RUN_TIMEOUT_SEC` 등 |
| `components.py` | 화면 공통 부품: 코드 에디터 래퍼, 채점 결과 표, 힌트 패널 | `code_editor()`, `render_grade_result()` |
| `views/dashboard.py` | 대시보드 | — |
| `views/lesson.py` | 오늘의 수업(5개 섹션 진행) | — |
| `views/practice.py` | 코드 실습(Day/문제 선택 → 실행·채점) | — |
| `views/wrong_notes.py` | 오답 노트, 재도전, 반복 실수 통계 | — |
| `views/history.py` | 일자별 이력, 주제별 성취도, 이어하기 | — |
| `core/models.py` | 데이터 클래스(콘텐츠·실행 결과·채점 결과) | `Lesson`, `Exercise`, `TestCase`, `RunResult`, `GradeResult`, `Feedback` |
| `core/content.py` | JSON 로드, 스키마 검증, 캐시 | `ContentRepository.load()`, `.lesson(day)`, `.exercise(id)`, `validate_lesson()` |
| `core/runner.py` | 작업 디렉터리 생성 → 자식 프로세스 실행 → 시간 초과 시 프로세스 트리 종료 → 결과 수집 | `run_program(code, stdin)`, `run_tests(code, exercise)` |
| `core/harness.py` | **자식 프로세스 전용 스크립트.** stdlib만 import. 앱 코드에서 import하지 않음 | (스크립트) |
| `core/grader.py` | 평가기 파이프라인, 결과 비교(출력 정규화·실수 허용 오차·예외 타입) | `grade(exercise, code) -> GradeResult` |
| `core/checks.py` | `ast` 기반 정적 검사(필수/금지 구문, 줄 수, 가독성 경고) | `run_static_checks(code, checks)` |
| `core/errors.py` | 오류 유형 열거형, 한국어 라벨, 예외 → 오류 유형 매핑 | `ErrorType`, `classify()` |
| `core/db.py` | 연결 생성(`foreign_keys=ON`), `PRAGMA user_version` 기반 마이그레이션 | `connect()`, `init_db()` |
| `core/repository.py` | 테이블별 CRUD. SQL은 이 파일에만 둔다 | `save_submission()`, `get_exercise_state()` … |
| `core/progress.py` | 서비스 계층: 수업 시작/진행/완료 판정, 통계 계산 | `submit()`, `try_complete_lesson()`, `dashboard_stats()` |
| `llm/base.py` | LLM 연동 인터페이스와 Null 구현 | `CodeReviewer`, `HintProvider`, `NullReviewer` |
| `content/` | `curriculum.json`, `lessons/dayNN.json` | — |
| `data/` | `learning.db` (git 제외) | — |
| `tests/` | pytest | — |

> 화면 폴더는 04단계에서 `pages/` → `views/`로 이름을 바꿨다(Streamlit이 `pages/`를 자동 인식해 `app.py`를 건너뛰는 문제). 폴더는 이미 만든 구조를 그대로 쓰고, 공통 UI 부품은 새 폴더 대신 `lab_app/components.py` 파일 하나에 둔다.
> Streamlit 테마 설정(`.streamlit/config.toml`)이 필요하면 04단계에서 폴더 생성 전에 확인을 요청한다.

## 4. 코드 실행 설계 (runner + harness)

### 4.1 실행 흐름
1. `runner`가 임시 작업 디렉터리를 만든다 (`tempfile.TemporaryDirectory(prefix="pylab_", ignore_cleanup_errors=True)`).
2. `user_code.py`(사용자 코드)와 `job.json`(모드, 테스트, 제한값)을 쓴다.
3. 자식 프로세스를 실행한다.
   ```
   [sys.executable, "-I", "-X", "utf8", "<lab_app/core/harness.py>", "<job_dir>"]
   cwd=<job_dir>, stdin=DEVNULL, stdout/stderr → job_dir 안의 파일
   env: 최소 환경(SYSTEMROOT, PATH, TEMP 등) + PYTHONIOENCODING=utf-8
   creationflags=CREATE_NEW_PROCESS_GROUP (Windows)
   ```
   - `-I`(격리 모드): 사용자 site-packages·`PYTHON*` 환경변수·스크립트 폴더를 `sys.path`에서 뺀다. 그래서 harness는 **stdlib만** 쓴다.
   - stdout/stderr를 파이프가 아니라 파일로 받는다. 출력이 많아도 파이프가 막히는(deadlock) 일이 없다.
4. `proc.wait(timeout=...)`. 시간을 넘기면 `taskkill /PID <pid> /T /F`로 **프로세스 트리 전체**를 종료한다. 사용자 코드가 만든 하위 프로세스까지 정리하기 위해서다.
5. harness가 테스트 하나를 끝낼 때마다 `result.jsonl`에 한 줄씩 쓰고 `flush`한다. 시간 초과가 나면 결과가 없는 **첫 테스트를 `timeout`**, 나머지는 `not_run`으로 처리한다.
6. 작업 디렉터리를 삭제한다(실패해도 무시).

### 4.2 harness 동작 (자식 프로세스)
- `compile(code, "user_code.py", "exec")` → `SyntaxError`/`IndentationError`면 줄 번호와 메시지만 보고하고 끝낸다.
- 테스트마다 **새 네임스페이스**로 모듈 코드를 다시 실행한다. 전역 변수 상태가 다음 테스트로 넘어가지 않게 하기 위해서다.
- `sys.stdin` ← 테스트의 `stdin` 문자열(`io.StringIO`). 입력이 부족하면 `EOFError` → `eof_error`.
- `sys.stdout`/`sys.stderr` ← 상한이 있는 `LimitedWriter`. 상한을 넘으면 `OutputLimitExceeded`(`BaseException` 하위 클래스라 사용자의 `except Exception`에 잡히지 않음)를 던진다.
- 함수 모드: 모듈 실행 → `namespace[name](*args, **kwargs)` 호출 → 반환값 직렬화.
- 반환값 직렬화: `{"type": "list", "json": [...] 또는 null, "repr": "..."}`. tuple은 list로, set은 정렬된 list로 바꾸고, JSON으로 못 바꾸면 `repr`만 보낸다.
- 예외: 예외 타입 이름, MRO 이름 목록, 메시지, **사용자 코드 프레임만 남긴 traceback**을 보낸다.
- **비교·판정은 하지 않는다.** 실제 값만 보고하고, 판정은 부모의 `grader`가 한다. 그래서 판정 로직은 subprocess 없이 단위 테스트할 수 있다.

### 4.3 제한값 (`config.py`, 문제별 덮어쓰기 가능)

| 항목 | 기본값 | 비고 |
|---|---|---|
| 작업 전체 시간 제한 | 5초 | 문제 JSON의 `time_limit_sec`로 변경 |
| 테스트당 stdout 상한 | 20,000자 | 초과 시 `output_limit` |
| stderr 상한 | 10,000자 | |
| 부모가 읽는 파일 상한 | 256 KB | 이중 안전장치 |
| 메모리 제한 | 없음 (MVP) | Windows에는 `resource` 모듈이 없다. 나중에 Job Object로 검토 |

### 4.4 보안 범위 (명시적 한계)
- subprocess + 격리 모드는 **보안 샌드박스가 아니다.** 사용자 코드는 파일 읽기/쓰기, 네트워크 등을 할 수 있다.
- 이 앱은 **본인 PC에서 본인이 쓴 코드만** 실행한다는 전제다. 외부 사용자 코드 실행 기능(업로드, 공유 실행 등)은 만들지 않는다.
- 숨김 테스트는 JSON 파일 안에 있으므로 파일을 열면 볼 수 있다. 개인 학습용이라 이를 허용한다.

## 5. 채점 설계 (grader)

### 5.1 평가기 파이프라인
```
code ─► [PreCheck] 빈칸(____) 남음? 빈 코드? ──실패──► unfilled_blank / empty_code
         │
         ▼
       [StaticCheckEvaluator] ast 파싱 + 필수/금지 구문 + 줄 수 ──► Feedback(readability/logic)
         │   (severity=error면 실패, warning이면 통과에 영향 없음)
         ▼
       [TestEvaluator] runner로 공개+숨김 테스트 실행 → 비교 ──► 테스트별 결과(correctness)
         │
         ▼
       [ReviewEvaluator] (향후) llm.CodeReviewer, 기본 Null → 빈 목록
         │
         ▼
       GradeResult(passed, error_type, test_results[], feedback[], 공개/숨김 통과 수)
```
- 각 평가기는 `evaluate(exercise, code, context) -> list[Feedback]` 형태의 같은 인터페이스를 가진다. 피드백 범주는 `correctness` / `readability` / `logic`이다.
- 통과 조건은 **모든 테스트 통과 + severity=error인 정적 검사 위반 없음**이다.
- 대표 오류 유형(`error_type`)은 실패한 첫 테스트의 오류 유형으로 정한다(정적 검사 실패는 `static_check_failed`).

### 5.2 비교 규칙
| 기대값 | 비교 방법 |
|---|---|
| `stdout` | `\r\n`→`\n`, 각 줄 오른쪽 공백 제거, 끝 빈 줄 제거 후 일치 (`compare.mode="exact"`면 그대로 비교) |
| `return` | JSON 값으로 일치. `compare.mode="float"`면 숫자마다 `tol` 허용 오차, `"unordered"`면 리스트를 정렬해서 비교 |
| `raises` | 예외 타입 이름이 MRO 목록에 있으면 통과 (예: `"LookupError"`를 기대하면 `KeyError`도 통과) |

### 5.3 실행(Run)과 채점(Submit)의 차이
| | 실행 (Run) | 채점 (Submit) |
|---|---|---|
| 목적 | 시험 삼아 돌려 보기 | 정답 판정 |
| 입력 | 사용자가 입력한 stdin | 문제의 공개+숨김 테스트 |
| 기록 | `activity_log`(`code_run`)만 남김, 초안 코드 저장 | `submissions`, `test_results`, 오답 노트 갱신 |
| 결과 표시 | stdout, stderr/traceback | 테스트별 통과/실패, 숨김 테스트는 통과 개수만 |

### 5.4 힌트·정답 공개 정책
- 힌트는 문제마다 2~3단계이며 **한 단계씩** 연다. 연 개수는 `exercise_state.hints_revealed`에 저장한다.
- 정답 코드는 **제출을 1회 이상 한 뒤**에만 버튼이 열린다(`config.SOLUTION_UNLOCK_ATTEMPTS = 1`). 열기 전에 확인 단계를 둔다.
- 정답을 본 뒤 통과해도 수업 완료로 인정한다. 다만 `solution_viewed=1`로 표시하고 통계에서 구분한다.

## 6. 진도·완료 규칙 (progress)

| 규칙 | 정의 |
|---|---|
| 수업 잠금 | Day N은 N=1이거나 Day N-1이 `completed`일 때 열린다. 완료한 Day는 언제든 다시 볼 수 있다. |
| 오늘의 수업 | 열려 있고 완료되지 않은 가장 작은 Day. 모두 완료했으면 "다음 수업 준비 중"을 표시한다. |
| 수업 완료 | ① 그 Day의 `required=true` 문제(빈칸+코드 작성)를 **모두 통과** + ② 정리 섹션 퀴즈를 **모두 제출**(정답 여부 무관). 조건을 만족하는 순간에만 `completed`로 바뀐다. |
| 섹션 진행 | Day 안에서는 섹션을 자유롭게 오갈 수 있다. `current_section`은 이어하기 용도로만 쓴다. |
| 학습일 | `submission`, `quiz_answered`, `lesson_completed` 활동이 1건 이상 있는 로컬 날짜. 화면을 열기만 한 날은 제외한다. |
| 연속 학습 일수 | 오늘(오늘 활동이 아직 없으면 어제)부터 거꾸로 이어지는 학습일 수 |
| 누적 정답률 | 통과한 제출 수 ÷ 전체 제출 수 (실행은 제외). 퀴즈 정답률은 따로 표시 |
| 커리큘럼 진행률 | 완료한 Day 수 ÷ 전체 168일 (작성된 Day 기준 진행률도 함께 표시) |
| 취약 개념 | 개념 태그별로 (실패 제출 ÷ 제출)을 계산한다. 제출 2회 이상 + 실패율 50% 이상이거나, 미해결 오답 노트가 있으면 취약으로 본다. 실패율 순으로 정렬 |
| 복습 추천 | 미해결 오답 노트(오래된 순) 최대 3개 + 가장 취약한 개념이 나온 Day |

날짜와 시간은 PC 로컬 시간대 기준이다: `datetime.now().astimezone()`. 테스트에서는 `today`를 인자로 주입한다.

## 7. 화면별 데이터 흐름

| 화면 | 읽기 | 쓰기 |
|---|---|---|
| 대시보드 | `progress.dashboard_stats()` (학습일, 연속일, 진행률, 정답률, 취약 개념, 복습 추천) | — |
| 오늘의 수업 | `content.lesson(day)`, `lesson_progress`, `exercise_state` | 섹션 이동, 퀴즈 답, 실행/제출, 힌트, 완료 판정 |
| 코드 실습 | 선택한 Day·문제, `exercise_state.draft_code` | 실행/제출, 초안 저장 |
| 오답 노트 | `wrong_notes` + 최근 제출 코드, 오류 유형 통계 | 재도전(실습 화면으로 이동), 메모 |
| 학습 기록 | `activity_log`·`submissions` 일자별 집계, 개념별 성취도 | 이어하기(마지막 Day·섹션으로 이동) |

## 8. LLM 확장 지점 (MVP에서는 구현하지 않음)
```python
class CodeReviewer(Protocol):
    def review(self, exercise: Exercise, code: str, result: GradeResult) -> list[Feedback]: ...

class HintProvider(Protocol):
    def hint(self, exercise: Exercise, code: str, result: GradeResult, level: int) -> str: ...
```
- 기본 구현은 `NullReviewer`/`StaticHintProvider`(JSON 힌트 사용)이다.
- `config.LLM_PROVIDER = "none"`이면 UI에 AI 버튼을 표시하지 않는다.
- 정답 비공개 원칙은 LLM 힌트에도 똑같이 적용한다. 프롬프트에 "정답 코드 전체를 쓰지 말 것"을 넣는다.

## 9. 실행 방법 (예정)
- 프로젝트 루트에서 `python -m streamlit run lab_app/app.py`
- 테스트: 프로젝트 루트에서 `python -m pytest` (`pyproject.toml`의 `pythonpath = ["."]`)
- 의존성(02단계에서 확정): `streamlit`, 코드 에디터 컴포넌트(04단계에서 선택), `pytest`
