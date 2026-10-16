# JSON 콘텐츠 스키마 설계 — v1

> 콘텐츠 위치: `lab_app/content/` · 예시: [example_curriculum.json](example_curriculum.json), [example_lesson.json](example_lesson.json)
> 검증 구현: `lab_app/core/content.py` (`validate_curriculum`, `validate_lesson`) + `lab_app/tests/test_content.py`

## 1. 파일 구성

```
lab_app/content/
├── curriculum.json        전체 로드맵: 단계, 주차, 개념 태그 사전, 작성된 Day 목록
└── lessons/
    ├── day01.json         Day 하나 = 파일 하나 (15분 수업 + 문제)
    ├── ...
    └── day07.json         누적 복습 (review_every = 7)
```
새 Day를 추가할 때는 `lessons/dayNN.json`을 만들고 `curriculum.json`의 `days`에 한 줄을 넣는다. Python 코드는 고치지 않는다.

모든 텍스트 필드에서 `*_md`로 끝나는 필드는 Markdown이며 `st.markdown`으로 렌더링한다. 파일 인코딩은 UTF-8이다.

## 2. `curriculum.json`

| 필드 | 타입 | 설명 |
|---|---|---|
| `schema_version` | int | `1` |
| `title` | str | 앱 제목 |
| `minutes_per_day` | int | `15` |
| `review_every` | int | `7`. Day 번호가 7의 배수이면 누적 복습일 |
| `stages[]` | list | 4단계 로드맵 |
| `stages[].id` | str | `basics`, `advanced_data`, `ml`, `dl` |
| `stages[].order` | int | 1~4 |
| `stages[].title` / `description` | str | 한국어 |
| `stages[].weeks` | int | 5 / 5 / 7 / 7 |
| `stages[].day_range` | [int, int] | 시작·끝 Day (아래 표) |
| `weeks[]` | list | 주차별 주제 (`week`, `stage`, `title`) — 총 24주 |
| `concepts` | dict[str, str] | 개념 태그 → 한국어 라벨. 문제의 `concepts`는 여기 있는 키만 쓸 수 있다 |
| `days[]` | list | **작성된** Day만 나열 |
| `days[].day` | int | 1부터 |
| `days[].title` | str | 수업 제목 |
| `days[].file` | str | `content/` 기준 상대 경로 |
| `days[].is_review` | bool | 누적 복습 여부 (`day % review_every == 0`과 일치해야 함) |

| 단계 | 주 | Day 범위 |
|---|---|---|
| 1. Python 기초 (`basics`) | 5 | 1 ~ 35 |
| 2. Python 심화 및 데이터 분석 (`advanced_data`) | 5 | 36 ~ 70 |
| 3. 머신러닝 (`ml`) | 7 | 71 ~ 119 |
| 4. PyTorch 딥러닝 (`dl`) | 7 | 120 ~ 168 |

전체 168일이다. 커리큘럼 진행률의 분모는 `stages`의 마지막 `day_range` 끝값에서 계산한다.

## 3. `lessons/dayNN.json`

### 3.1 최상위 필드
| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `schema_version` | int | ✔ | `1` |
| `day` | int | ✔ | 파일 이름 번호와 일치 |
| `title` | str | ✔ | |
| `stage` | str | ✔ | `curriculum.stages[].id` |
| `week` | int | ✔ | |
| `is_review` | bool | ✔ | |
| `objectives` | list[str] | ✔ | 학습 목표 2~4개 |
| `concepts` | list[str] | ✔ | 이 Day의 개념 태그 |
| `sections` | list | ✔ | **정확히 5개, 아래 순서 고정** |
| `exercises` | list | ✔ | 이 Day의 실습 문제 (섹션에서 ID로 참조) |

### 3.2 섹션 (순서·분량 고정)
| # | `type` | `minutes` | 내용 필드 |
|---|---|---|---|
| 1 | `review` | 2 | `title`, `content_md`, `quiz[]` (Day 1은 오리엔테이션 내용) |
| 2 | `concept` | 4 | `title`, `blocks[]` |
| 3 | `fill_blank` | 3 | `title`, `intro_md`, `exercise_ids[]` (kind=`fill_blank`) |
| 4 | `coding` | 4 | `title`, `intro_md`, `exercise_ids[]` (kind=`coding`) |
| 5 | `summary` | 2 | `title`, `points[]`, `quiz[]` (1개 이상, 완료 조건) |

`minutes`의 합은 15여야 한다.

**`blocks[]`** (개념 설명):
| `kind` | 필드 | 설명 |
|---|---|---|
| `text` | `md` | 설명 문단 |
| `code` | `code`, `runnable`(bool), `expected_output`(str, runnable이면 필수) | 예제 코드. 화면에서 "실행" 버튼으로 바로 돌려 볼 수 있다. pytest가 실제로 실행해 `expected_output`과 비교한다 |
| `tip` | `md` | 주의점·팁 강조 상자 |

**`quiz[]`** (복습·정리):
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | str | 전역 고유. `d06_review_q1`, `d06_summary_q1` |
| `question_md` | str | |
| `choices` | list[str] | 2~5개 |
| `answer_index` | int | 0부터 |
| `explanation_md` | str | 답을 낸 뒤에 보여 줌 |

### 3.3 문제 (`exercises[]`)
| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `id` | str | ✔ | 전역 고유. `d06_fill_1`, `d06_code_1` |
| `kind` | str | ✔ | `fill_blank` / `coding` |
| `title` | str | ✔ | |
| `prompt_md` | str | ✔ | 문제 설명. 입출력 예시 포함 |
| `concepts` | list[str] | ✔ | 개념 태그 (취약 개념 계산) |
| `difficulty` | int | ✔ | 1~3 |
| `required` | bool | ✔ | `true`면 수업 완료 조건에 포함 |
| `starter_code` | str | ✔ | 에디터 초기값. `fill_blank`는 빈칸 `____`(밑줄 4개)를 1개 이상 포함 |
| `entry` | object | ✔ | `{"mode": "program"}` 또는 `{"mode": "function", "name": "함수명"}` |
| `tests` | list | ✔ | 공개 1개 이상 + 숨김 1개 이상 (권장). 입력이 없는 고정 출력 program 문제는 숨김 테스트가 의미 없으므로 경고하지 않음 (03단계에서 결정) |
| `hints` | list[str] | ✔ | 2~3단계. 앞 단계일수록 추상적으로. **정답 코드를 그대로 쓰지 않는다** |
| `solution` | str | ✔ | 모범 답안. 모든 테스트와 정적 검사를 통과해야 한다 (pytest 검증) |
| `checks` | object | | 정적 검사 (아래) |
| `time_limit_sec` | number | | 기본 5 |

**`tests[]`**:
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | str | 문제 안에서 고유 (`t1`, `h1` …) |
| `hidden` | bool | `true`면 화면에 입력·기대값을 숨기고 통과 여부만 보여 줌 |
| `description` | str | 예: "음수 입력" (숨김이면 표시하지 않음) |
| `stdin` | str | 표준 입력. 기본 `""` |
| `call` | object | 함수 모드 전용: `{"args": [...], "kwargs": {...}}` |
| `expect` | object | `stdout`, `return`, `raises` 중 1개 이상. `return`과 `raises`는 함께 쓸 수 없다 |
| `compare` | object | 선택: `{"mode": "normalized"(기본) / "exact" / "float" / "unordered", "tol": 1e-6}` |

- `program` 모드에서는 `call`을 쓰지 않고 `expect.stdout`만 쓴다.
- 채점할 때는 `input("안내 문구")`의 안내 문구가 출력에 포함되지 않는다. 그래서 `expect.stdout`에 안내 문구를 쓰지 않는다. 자유 실행(Run)에서는 터미널처럼 안내 문구와 입력값을 함께 보여 준다. (02단계에서 결정)
- `function` 모드에서는 `return`, `raises`, `stdout`(함수 안에서 print한 내용)을 검사할 수 있다.
- JSON으로 표현할 수 있는 값(int, float, str, bool, null, list, dict)만 인자·기대값으로 쓴다. tuple 반환값은 list로 바꿔 비교한다.

**`checks`** (정적 검사, `ast` 기반 — 가독성·논리 평가의 확장 지점):
| 필드 | 예 | 위반 시 |
|---|---|---|
| `required_syntax` | `["for", "if", "def", "fstring", "while", "return"]` | error: "for 문을 사용해 보세요" |
| `forbidden_syntax` | `["while", "import"]` | error |
| `forbidden_calls` | `["eval", "exec", "sum"]` | error (예: 직접 누적 연습 문제에서 sum 금지) |
| `max_lines` | `15` | warning |

검사 이름 ↔ ast 노드 매핑은 `core/checks.py`에 둔다. 처음 버전에서 지원하는 이름: `for`, `while`, `if`, `def`, `return`, `fstring`, `import`, `list_comp`, `try`.

## 4. ID 규칙 요약
| 대상 | 형식 | 예 |
|---|---|---|
| 문제 | `d{DD}_{fill|code}_{n}` | `d03_code_2` |
| 퀴즈 | `d{DD}_{review|summary}_q{n}` | `d01_summary_q1` |
| 테스트 | 공개 `t{n}`, 숨김 `h{n}` | `t1`, `h2` |

## 5. 검증 규칙 (content.py + pytest에서 강제)
1. `curriculum.days[].file`이 모두 존재하고, 파일 안의 `day`가 일치한다.
2. 섹션은 5개이며 순서는 `review → concept → fill_blank → coding → summary`, `minutes` 합은 15다.
3. 모든 ID(문제·퀴즈)가 전역에서 고유하고, 섹션이 참조하는 `exercise_ids`가 실제로 있으며 kind가 섹션과 맞는다.
4. `concepts` 태그는 모두 `curriculum.concepts`에 있다.
5. `fill_blank`의 `starter_code`에는 `____`가 있고, `solution`에는 없다.
6. 각 문제의 `solution`이 **실제 runner로 실행했을 때** 모든 테스트와 `checks`를 통과한다.
7. 각 문제의 `starter_code`는 채점에서 **통과하지 않는다**. 문제를 안 풀고도 완료되는 것을 막는다.
8. `runnable=true`인 코드 블록은 실행 결과가 `expected_output`과 같다.
9. `answer_index`가 `choices` 범위 안에 있다.
10. 힌트 문자열에 `solution`의 핵심 줄이 그대로 들어 있지 않다. 공백을 제거한 뒤 20자 이상 겹치면 경고로 처리한다.

## 6. Day 1~7 주제 (03단계에서 확정)
| Day | 주제 | 주요 채점 방식 |
|---|---|---|
| 1 | print, 변수, 기본 자료형(int/float/str/bool) | stdout |
| 2 | 산술·비교 연산자, `input()`, 형 변환 | stdin → stdout |
| 3 | 문자열: 인덱싱, 슬라이싱, 메서드, f-string | stdout |
| 4 | 조건문 `if/elif/else`, 논리 연산자 | stdin → stdout |
| 5 | 반복문 `for`/`range`, `while`, 누적 패턴 | stdout + 정적 검사(for 필수) |
| 6 | 함수 기초 `def`/`return`, `raise ValueError` 맛보기 | 반환값 + 예외 |
| 7 | **누적 복습** (Day 1~6) | 혼합 |

Day 6에서 함수를 배우므로 반환값·예외 검사를 실제 콘텐츠로 검증할 수 있다. 리스트는 2주차로 미룬다.

## 7. Day 8~14 주제 (2주차: 리스트와 튜플, 07단계에서 추가)
| Day | 주제 | 주요 채점 방식 |
|---|---|---|
| 8 | 리스트 만들기, 인덱싱·음수 인덱스·슬라이싱, `len`, `in` | 반환값(리스트) + 예외 |
| 9 | 원소 바꾸기, `append/insert/pop/remove` | 반환값(리스트) + 예외 |
| 10 | 리스트 순회, 골라 담기, `range(len())`, 최댓값 직접 찾기 | 반환값 + 정적 검사(`max/sorted/sort` 금지) |
| 11 | `sum/max/min`, `sorted` vs `.sort()`, `count/index`, `split()` | 반환값, 한 줄 입력 → 출력 |
| 12 | 튜플, 언패킹, 여러 값 반환 | 튜플 반환값(list로 비교) + 예외 |
| 13 | 2차원 리스트, `enumerate`, `zip` | 반환값(리스트) + 예외 (도전 1개) |
| 14 | **누적 복습** (Day 8~13) | 혼합 (도전 1개) |

추가된 개념 태그: `list`, `list_method`, `list_iteration`, `sorting`, `tuple`, `unpacking`, `nested_list`, `enumerate_zip`.
JSON 인자에는 튜플이 없으므로 `(이름, 점수)` 쌍은 `[이름, 점수]` 리스트로 넘기고, 튜플 반환값은 list로 바꿔 비교한다.
