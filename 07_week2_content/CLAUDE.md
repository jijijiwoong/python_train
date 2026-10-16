# 07_week2_content — Claude 작업 메모

## Current state (last updated 2026-10-16)
- Done: Day 8~14 (2주차: 리스트와 튜플) JSON 작성, curriculum.json 등록, test_real_content.py 확장.
- 검증: `ContentRepository().warnings == []`, 14개 Day 모두 `verify_lesson()` 통과, `pytest` 173 passed.
- 커밋은 하지 않았다 (요청 없음).

## Key decisions in effect
- Day 구성: 8 리스트 기초 / 9 리스트 바꾸기 / 10 리스트와 반복문 / 11 정렬·내장 함수·split / 12 튜플 / 13 중첩 리스트·enumerate·zip / 14 누적 복습 — 한 Day에 새 개념 하나씩.
- 새 개념 태그 8개: list, list_method, list_iteration, sorting, tuple, unpacking, nested_list, enumerate_zip.
- Day 13·14는 Day 7처럼 선택 도전 문제 1개(`required: false`)를 둔다 — 4분에 필수 코딩 2개는 많음.
- 리스트 컴프리헨션은 쓰지 않았다 (7주차 주제).
- `join`은 3주차(문자열 심화)로 미뤘다. 출력은 리스트 repr 또는 개수로 설계했다.
- JSON에는 튜플이 없으므로 쌍 인자는 `[이름, 점수]` 리스트로 넘긴다. 튜플 반환은 harness가 list로 바꿔 비교한다.
- 테스트 기대값은 손으로 계산해 빌더에 하드코딩했다 (모범 답안으로 만들지 않음).

## Important files
- `../lab_app/content/lessons/day08.json` ~ `day14.json` — 기준 원본. 이제 JSON을 직접 편집한다.
- `../lab_app/content/curriculum.json` — concepts 8개, days 7줄 추가.
- `../lab_app/tests/test_real_content.py` — Day 1~14, 복습일 [7, 14], 흔한 실수 8건, 도전 문제 3개 파라미터화.
- `../01_design/content_schema.md` §7, `../README.md` §7·9 — 2주차 반영.
- 빌더 스크립트는 세션 스크래치 폴더에만 있었다 (저장소에 없음).

## Known pitfalls
- Git Bash heredoc 안의 Python 문자열에서 `\\n`이 실제 줄바꿈으로 바뀌었다 → 코드 문자열이 들어가는 수정은 스크립트 파일로 작성해 실행할 것.
- `remove()`는 없는 값이면 스스로 ValueError를 낸다 → d09_code_1은 명시적 검사 없이도 예외 테스트를 통과한다 (의도적으로 허용, tip에 설명).
- `items[-0:]`은 리스트 전체 → d14_code_2 정답은 `cut = len - k % len`으로 처리.

## Next actions
- 대시보드(`lab_app/views/dashboard.py`)가 모든 Day를 한 줄의 열로 그려 14개 카드가 좁아짐 → UI 쪽 후속 작업 필요 (이번 범위 밖).
- 화면에서 Day 8~14 표·코드 블록 렌더링을 눈으로 확인.
- 3주차(Day 15~21: 딕셔너리, 집합, 문자열 심화).
