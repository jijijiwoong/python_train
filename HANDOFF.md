# HANDOFF

- **활성 단계**: 03_content — 168일 전체 수업 작성 완료(Day 1~168). 기록: `03_content/CLAUDE.md`(마지막 섹션), `03_content/WORKLOG.md`.
- **미완료**
  - 커밋·push: 사용자가 직접 한다(에이전트는 push 금지, 커밋은 요청 시에만).
  - 3·4단계 수업을 앱 화면에서 직접 확인(그림, 긴 코드, torch 실행 대기 시간).
- **다음 실행 단계**
  1. `.venv\Scripts\python -m pytest` (기본, 약 2.5분) / `-m heavy` (3·4단계, 약 30분)
  2. 앱에서 Day 64(그래프), Day 145(CNN), Day 166(그리드 탐색) 정도를 열어 표시·대기 시간 확인
  3. 커밋 → push
- **알려진 문제**
  - 빌더 스크립트는 `tools/content_builders/`에 있다(사용법은 그 폴더의 README). JSON이 기준 원본이다.
  - 3·4단계 기대값은 torch 2.14.1+cpu / scikit-learn 1.9.1 기준. 버전이 다르면 일부 heavy 검사가 tol을 넘을 수 있다.
