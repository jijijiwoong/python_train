# 03_content WORKLOG

이전 작업(Day 1~7, Day 15~35)은 `CLAUDE.md`의 Process에 기록되어 있다. 이 파일은 Day 36 이후부터 시간 순으로 적는다.

## 2026-10-16 · Claude Code · Day 36~70 (2단계)
- 변경: `.venv`에 numpy·matplotlib·scikit-learn·scipy·torch 설치. 엔진 보완(`core/harness.py`, `runner.py`, `models.py`, `content.py`, `checks.py`, `progress.py`, `matplotlibrc`, `components.py`, `config.py`). `lessons/day36~70.json`, `curriculum.json`.
- 이유: NumPy·pandas 반환값 채점, matplotlib 그림 표시, 무거운 import의 실행 시간.
- 결과: Day 36~70 자기 검증 통과, 경고 0.

## 2026-10-16 · Claude Code · Day 71~119 (3단계 머신러닝)
- 변경: `lessons/day71~119.json`, `curriculum.json`, `tests/test_real_content.py`(heavy 마커), `pyproject.toml`.
- 이유: scikit-learn 수업 49일. sklearn import로 검사가 느려 기본 pytest에서 분리.
- 결과: 17주차 경고(100자 초과 줄, Day 119 숨김 테스트 누락)를 고친 뒤 병합. 경고 0.

## 2026-10-16 · Claude Code · Day 120~168 (4단계 딥러닝)
- 변경: `lessons/day120~168.json`, `curriculum.json`, `tests/test_real_content.py`(도전 문제 검사 확장, 딥러닝 흔한 실수 2건), `requirements.txt`, `README.md`, `01_design/content_schema.md`.
- 결정: 기대값은 모범 답안을 빌더에서 실행해 계산. 학습 결과 비교는 시드 명시 + float tol. 23주차 전이 학습은 실험 결과(처음부터 학습이 더 좋음)를 그대로 보여 주고 이유를 설명. 증강은 "어긋난 테스트" 견고성으로 평가.
- 결과: 49일 모두 자기 검증 통과, 경고 0. pytest 기본 257 passed. heavy 100 passed.
- 미해결: 3·4단계 화면 육안 확인 안 함. 다른 torch/sklearn 버전에서 tol 초과 가능.

## 2026-10-16 · Claude Code · 빌더 보존
- 변경: `tools/content_builders/`(새 폴더, 사용자 승인)에 빌더·헬퍼·검증·병합 스크립트 32개와 README 복사. `cb_data.py`의 matplotlibrc 절대 경로를 프로젝트 기준 상대 경로로 변경.
- 결과: 프로젝트 사본으로 18주차·10주차를 다시 만들어 Day 64·70·120·126이 현재 JSON과 바이트 단위로 같음을 확인.
