# 03_content — 커리큘럼 및 Day 1~7 수업 콘텐츠

## Goal
`lab_app/content/`에 JSON 콘텐츠를 작성한다. UI 코드와 분리하여 이후 수업을 파일 추가만으로 늘릴 수 있게 한다.
- `curriculum.json`: 4단계 168일 로드맵, 24주 주제, 개념 태그 사전, 작성된 Day 목록
- `lessons/day01.json` ~ `day07.json`: 15분 구성(복습 2 / 개념 4 / 빈칸 3 / 작성 4 / 정리 2)
- 설명은 한국어로 쓰고, 코드 예제는 실제로 실행 가능해야 한다.

## Process
1. (2026-10-16) 콘텐츠를 작성했다. 스크래치 빌더 스크립트(프로젝트 밖, 세션 임시 폴더)로 JSON을 생성했다.
   - 이유: 코드 문자열의 `\n`·따옴표 이스케이프 실수를 피하기 위해서다. 테스트 기대 출력은 **모범 답안을 실행하지 않고** 별도의 Python 식으로 계산했다. 답안으로 답안을 검증하는 순환을 막기 위해서다.
   - **이후 기준 원본은 JSON 파일이다.** 빌더는 저장소에 남기지 않았다. 수업을 수정하거나 추가할 때는 JSON을 직접 편집한다.
2. `curriculum.json`은 `01_design/example_curriculum.json`을 그대로 썼다(검증 완료본).
3. Day 6은 `01_design/example_lesson.json`(검증 완료본)을 그대로 썼다.
4. Day 7(누적 복습)에는 필수 문제 2개와 **선택 도전 문제 1개**(`d07_code_2`, `required: false`)를 넣었다. 4분 안에 코딩 문제 2개는 많기 때문이다.
5. 엔진 수정 1건(`core/content.py`): 입력이 없는 고정 출력 program 문제(Day 1)는 숨김 테스트가 의미 없으므로 "숨김 테스트 없음" 경고를 내지 않도록 했다. `01_design/content_schema.md`에 반영했다.
6. 검증 1차: Day 4 코딩 문제의 공개 테스트 id가 중복(`t1` ×3)되어 검증기가 거부했다. 수정 후 재생성했다.
7. 검증 2차: `ContentRepository()` 로드 경고 0건, 7개 Day 모두 `verify_lesson()` 통과
   - 모든 모범 답안이 공개·숨김 테스트와 정적 검사를 통과한다.
   - 모든 시작 코드는 채점을 통과하지 못한다.
   - 실행 가능 예제 20개의 실제 출력이 `expected_output`과 같다.
8. `lab_app/tests/test_real_content.py`를 추가했다(19개).
   - 실제 콘텐츠의 구조와 Day별 자기 검증
   - **초보자가 흔히 하는 실수 10가지**가 의도한 오류 유형으로 채점되는지 확인한다. 예: `int()` 변환을 빠뜨림, `/` 대신 `//`, `strip()` 누락, f-string 대신 `+` 연결, 경계값 실수, `sum()` 사용, 무한 루프, 예외 미발생, 최댓값 대신 마지막 값.

## Files
| 파일 | 내용 |
|---|---|
| `../lab_app/content/curriculum.json` | 4단계(기초 35일 / 심화·데이터 35일 / ML 49일 / DL 49일), 24주 주제, 개념 태그 18개, Day 1~7 목록 |
| `../lab_app/content/lessons/day01.json` | print, 변수, 기본 자료형 |
| `../lab_app/content/lessons/day02.json` | 산술·비교 연산자, `input()`, 형 변환 |
| `../lab_app/content/lessons/day03.json` | 인덱싱·슬라이싱, 문자열 메서드, f-string |
| `../lab_app/content/lessons/day04.json` | `if/elif/else`, `and/or/not` |
| `../lab_app/content/lessons/day05.json` | `for`/`range`, `while`, 누적 패턴 |
| `../lab_app/content/lessons/day06.json` | `def`/`return`, `raise ValueError` |
| `../lab_app/content/lessons/day07.json` | 1주차 누적 복습 |
| `../lab_app/tests/test_real_content.py` | 실제 콘텐츠 검증 + 흔한 실수 채점 테스트 |
| `CLAUDE.md`, `summary.html` | 이 단계 기록, 요약 보고서 |

## Results
| Day | 주제 | 문제 (빈칸 / 작성) | 테스트 (공개 / 숨김) | 예제 코드 (실행 검증) | 퀴즈 | 채점 방식 |
|---|---|---|---|---|---|---|
| 1 | print·변수·자료형 | 1 / 1 | 2 / 0 | 3 (3) | 3 | 출력 |
| 2 | 연산자·입력·형 변환 | 1 / 1 | 3 / 5 | 4 (3) | 3 | 입력 → 출력 |
| 3 | 문자열 | 1 / 1 | 2 / 4 | 3 (3) | 3 | 입력 → 출력, f-string 필수 |
| 4 | 조건문 | 1 / 1 | 5 / 8 | 3 (3) | 3 | 입력 → 출력, 경계값 |
| 5 | 반복문 | 1 / 1 | 3 / 6 | 4 (4) | 3 | 입력 → 출력, for 필수·sum 금지 |
| 6 | 함수 기초 | 1 / 1 | 4 / 5 | 2 (2) | 2 | 반환값, 예외, 실수 오차 |
| 7 | 누적 복습 | 1 / 2 (1개 선택) | 6 / 11 | 2 (2) | 4 | 혼합 |
| **합계** | | **15 (필수 14)** | **25 / 39** | **21 (20)** | **21** | |

- Day 2의 `input()` 예제 1개는 입력이 필요해서 `runnable: false`(표시 전용)로 두었다.
- `.venv\Scripts\python -m pytest` → **106 passed** (기존 87 + 신규 19), 약 29초

## Issues & open questions
- **Day 1 문제는 입력이 없어** 출력을 그대로 `print("총액: 13500")`처럼 써도 통과한다. 첫날이라 입력을 배우기 전이므로 허용했고, 테스트로도 명시했다. 정적 검사로 "변수 사용"을 강제하려면 `checks`에 새 규칙 종류가 필요하다.
- Day 7 개념 예제에 `ch.isupper()`와 리스트 `[7, 2, 9, 4]`가 처음 등장한다. 리스트는 tip에서 "2주차에 배움"이라고 안내했다. 문제 풀이에는 필요하지 않다.
- 숨김 테스트 내용은 JSON에 그대로 있다(개인용, 01단계에서 허용).
- 화면에서 Markdown 표·코드 블록이 의도대로 보이는지는 04단계에서 확인해야 한다.
- 빌더 스크립트는 남기지 않았다. 대량 수정이 필요하면 다시 만들어야 한다.

## Status
Done — 커리큘럼과 Day 1~7 작성, 엔진 기반 자동 검증 통과 (last updated: 2026-10-16)
