"""Curriculum additions for Day 15+ (new concept tags and day list). Used for temp validation and the final merge."""

NEW_CONCEPTS = {
    # week 3
    "dict": "딕셔너리", "dict_iteration": "딕셔너리 순회", "nested_dict": "중첩 딕셔너리·그룹화", "set": "집합",
    "string_parsing": "문자열 나누기·합치기", "formatting": "출력 서식",
    # week 4
    "default_args": "기본값·키워드 인자", "variadic_args": "가변 인자(*args, **kwargs)", "scope": "변수의 범위",
    "lambda": "lambda와 key 함수", "recursion": "재귀", "module": "모듈과 import",
    # week 5
    "try_except": "예외 처리(try/except)", "custom_exception": "예외 발생과 전달", "file_io": "파일 입출력",
    "text_processing": "텍스트 데이터 처리",
}

DAYS = [
    (15, "딕셔너리 기초"), (16, "딕셔너리 순회와 개수 세기"), (17, "딕셔너리 활용: 중첩과 그룹화"), (18, "집합"),
    (19, "문자열 메서드 심화"), (20, "문자열 서식과 문자 다루기"), (21, "3주차 누적 복습"),
    (22, "기본값과 키워드 인자"), (23, "가변 인자와 여러 값 반환"), (24, "변수의 범위"), (25, "lambda와 정렬 기준"),
    (26, "재귀 함수"), (27, "모듈과 import"), (28, "4주차 누적 복습"),
    (29, "예외 처리 try/except"), (30, "예외 발생시키기와 전달"), (31, "파일 읽고 쓰기"), (32, "텍스트 데이터 처리"),
    (33, "미니 프로젝트 1: 단어 빈도 분석"), (34, "미니 프로젝트 2: 가계부"), (35, "1단계 마무리 누적 복습"),
]


def day_entries(upto: int) -> list[dict]:
    return [{"day": d, "title": title, "file": f"lessons/day{d:02d}.json", "is_review": d % 7 == 0}
            for d, title in DAYS if d <= upto]
