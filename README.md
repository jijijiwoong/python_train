# Python Learning Lab

매일 15분씩 **Python 기초 → 심화·데이터 분석 → 머신러닝 → PyTorch 딥러닝** 순서로 공부하는 개인용 로컬 학습 앱입니다.
읽기만 하는 강의가 아니라 직접 코드를 쓰고 실행하고 자동 채점을 받으며 진도를 쌓습니다.

- 하루 수업 구성(15분): 복습 2분 → 핵심 개념 4분 → 빈칸 채우기 3분 → 직접 작성 4분 → 정리·점검 2분
- 화면: 대시보드 · 오늘의 수업 · 코드 실습 · 오답 노트 · 학습 기록
- 현재 수업: **Day 1~14** (1주차 기초 문법, 2주차 리스트와 튜플. Day 7·14는 누적 복습). 전체 로드맵은 168일(24주)입니다.
- 기술: Python 3.12 이상 · Streamlit · SQLite · JSON 콘텐츠 · pytest

> ⚠️ 이 앱은 **내 PC에서 내가 쓴 코드만** 실행하는 용도입니다. 코드는 별도 프로세스에서 실행되어 앱이 멈추지 않지만, 완전한 보안 샌드박스는 아닙니다. 그래서 앱은 이 PC(`localhost`)에서만 열리도록 되어 있습니다.

---

## 1. 설치 (처음 한 번)

Windows PowerShell에서 실행합니다. **모든 명령은 프로젝트 폴더에서 실행해야 합니다.**

```powershell
cd C:\Users\jiwoo\python_train
```

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
```

- Python 3.12 이상이 필요합니다(`python --version`으로 확인). 개발·검증 환경은 Python 3.14.6입니다.
- 가상환경 `.venv`는 이 프로젝트 전용입니다. 전역 Python에는 아무것도 설치하지 않습니다.

## 2. 앱 실행

```powershell
.\run_app.cmd
```

- 탐색기에서 `run_app.cmd`를 **더블클릭**해도 됩니다. 몇 초 뒤 브라우저가 `http://localhost:8501`로 자동으로 열립니다.
- 종료: 실행 창에서 `Ctrl + C`를 누르거나 창을 닫습니다.
- `run_app.cmd`를 쓰지 않고 직접 실행할 때는 **반드시 `--server.address localhost`를 붙이세요**. 붙이지 않으면 앱이 보안 안내만 보여 주고 실행되지 않습니다.

```powershell
.venv\Scripts\python -m streamlit run lab_app\app.py --server.address localhost --server.headless true --browser.gatherUsageStats false
```

## 3. 사용 방법

1. **대시보드**에서 오늘의 수업을 확인하고 **학습 시작**을 누릅니다.
2. **오늘의 수업**에서 위쪽 단계 버튼이나 아래 **다음 단계 →**로 이동합니다. 마지막으로 보던 단계는 자동으로 기억됩니다.
3. 문제 풀이
   - **▶ 실행**: 채점 없이 코드를 돌려 봅니다. `input()`에 넣을 값은 "실행할 때 넣을 입력값"에 한 줄씩 적습니다.
   - **✔ 채점**: 공개 테스트와 숨김 테스트로 채점합니다. 숨김 테스트는 통과 여부만 알려 줍니다.
   - **💡 힌트**: 한 단계씩 열립니다. 정답 코드는 들어 있지 않습니다.
   - **📖 모범 답안**: 한 번 이상 채점한 뒤에 열 수 있습니다. 열람 기록이 남습니다.
   - **↺ 처음 코드로**: 시작 코드로 되돌립니다.
4. 그날의 **필수 문제를 모두 통과**하고 **정리 퀴즈를 제출**하면 수업이 완료되고 다음 Day가 열립니다. 읽기만 하거나 시간이 지나는 것으로는 완료되지 않습니다.
5. 틀린 문제는 **오답 노트**에 자동으로 쌓입니다. 메모를 남기고 **다시 풀기**로 재도전할 수 있습니다.
6. **학습 기록**에서 날짜별 이력, 개념별 성취도를 보고 **이어하기**로 마지막 위치에서 다시 시작합니다.
7. **코드 실습 → 자유 실습**은 채점·기록 없이 마음대로 코드를 실행해 보는 공간입니다.

- 실행 제한: 5초 (무한 루프는 자동으로 멈추고, 멈추기 전까지의 출력은 보여 줍니다) · 출력 20,000자
- 학습일·연속 학습은 문제를 제출하거나 퀴즈를 푼 날만 셉니다(PC 시간 기준).

## 4. 테스트

```powershell
.venv\Scripts\python -m pytest
```

- 173개 테스트, 약 1분. 실제 학습 기록은 건드리지 않고 임시 DB를 씁니다.
- 커버리지 보기: `.venv\Scripts\python -m pytest --cov=lab_app`
- 수업 내용이 올바른지 검사하는 테스트도 포함됩니다. 모든 모범 답안이 통과하는지, 시작 코드는 통과하지 않는지, 예제 출력이 맞는지 확인합니다.

## 5. 폴더 구조

```
python_train/
├── README.md              이 문서
├── run_app.cmd            앱 실행 파일 (localhost 전용)
├── requirements.txt       의존성
├── pyproject.toml         pytest 설정
├── index.html             개발 단계별 진행 현황 (더블클릭으로 열기)
├── 01_design/ … 06_release/   개발 단계별 작업 기록(CLAUDE.md)과 요약 보고서(summary.html)
└── lab_app/               앱 코드
    ├── app.py             진입점 (내비게이션, localhost 검사)
    ├── components.py      화면 공통 부품 (에디터, 채점 결과, 퀴즈)
    ├── config.py          경로·제한값
    ├── views/             화면 5개
    ├── core/              엔진: 콘텐츠 로드·검증, 코드 실행(runner/harness), 채점, DB, 진도·통계
    ├── llm/               향후 AI 연동 인터페이스 (현재 사용 안 함)
    ├── content/           수업 JSON (curriculum.json, lessons/dayNN.json)
    ├── data/              learning.db — 내 학습 기록 (git 제외)
    └── tests/             pytest
```

## 6. 학습 기록 관리

- 기록 파일: `lab_app\data\learning.db` (SQLite). 앱을 끄고 다시 켜도 그대로 유지됩니다.
- **백업**: 앱을 종료한 뒤 파일을 복사합니다.

```powershell
Copy-Item lab_app\data\learning.db "learning_backup_$(Get-Date -Format yyyyMMdd).db"
```

- **처음부터 다시 시작**: 앱을 종료하고 `learning.db`를 다른 이름으로 옮기면 다음 실행 때 빈 기록으로 시작합니다. 지우기 전에 백업을 권장합니다.
- 다른 위치의 DB를 쓰려면 실행 전에 `$env:LAB_DB_PATH = "D:\경로\learning.db"`를 설정합니다.

## 7. 수업 추가하기 (Day 15~)

수업은 코드와 분리된 JSON 파일입니다. **Python 코드를 고치지 않고** 추가할 수 있습니다.

1. `lab_app\content\lessons\day15.json` 파일을 만듭니다. 형식은 `day01.json`~`day14.json`을 참고하세요.
   - 필드 설명: `01_design\content_schema.md`
2. `lab_app\content\curriculum.json`의 `days` 목록에 한 줄을 추가합니다. 7의 배수 Day는 `"is_review": true`입니다.
3. 검사를 실행합니다.

```powershell
.venv\Scripts\python -m pytest lab_app\tests\test_real_content.py
```

- 파일 형식이 틀리면 앱 화면에 오류 위치가 표시되고, 테스트도 어디가 틀렸는지 알려 줍니다.
- 테스트는 섹션 순서·15분 합계, 모범 답안 통과, 시작 코드 불통과, 예제 출력 일치, 힌트에 정답 노출 여부, 한국어 굵게 표시 오류까지 확인합니다.
- `test_weeks_one_and_two_are_complete_and_clean`은 현재 Day 1~14를 기준으로 작성되어 있습니다. Day를 추가하면 이 테스트의 Day 목록과 복습일 목록도 함께 수정하세요.

## 8. 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| `No module named pytest` 또는 `No module named streamlit` | 프로젝트 폴더가 아닌 곳(예: `C:\Users\jiwoo`)에서 실행해 다른 `.venv`가 잡혔습니다. `cd C:\Users\jiwoo\python_train` 후 다시 실행하세요. |
| `[오류] .venv 가상환경이 없습니다` | 1장의 설치 명령을 먼저 실행하세요. |
| 설치 중 `OSError: [Errno 2] No such file or directory … Long Path` | Windows 경로 길이 제한(260자)입니다. Streamlit 안의 파일 경로가 깁니다. 프로젝트를 `C:\Users\jiwoo\python_train`처럼 짧은 경로에 두거나, Windows "긴 경로 사용"을 켜세요. |
| 앱에 "이 PC에서만 실행할 수 있습니다"만 보임 | `--server.address localhost` 없이 실행했습니다. `run_app.cmd`를 사용하세요. |
| `Port 8501 is already in use` | 이미 앱이 실행 중입니다. 열려 있는 실행 창을 닫거나 브라우저에서 `http://localhost:8501`을 여세요. |
| "수업 파일(JSON)에 오류가 있어…" 화면 | 표시된 파일과 위치의 JSON을 고친 뒤 앱을 다시 시작하세요. |
| 코드를 고쳤는데 채점이 예전 코드로 됨 | 에디터 밖을 한 번 클릭한 뒤 채점하세요. 에디터는 입력을 잠시 멈추거나 포커스가 빠질 때 내용을 전달합니다. |

## 9. 다음 단계 (미구현)

- AI(LLM) 코드 리뷰·힌트: `lab_app\llm\base.py`의 `CodeReviewer`/`HintProvider`를 구현해 연결합니다. 채점 결과는 바꾸지 않고 피드백만 추가하는 구조입니다.
- 자동 알림, 상세 성취도 분석
- Day 15 이후 콘텐츠 (3주차: 딕셔너리, 집합, 문자열 심화)

## 검증된 버전

Python 3.14.6 · streamlit 1.66.0 · streamlit-code-editor 0.1.22 · pandas 3.0.6 · pytest 9.1.1 · pytest-cov 7.1.0 (Windows 11)
