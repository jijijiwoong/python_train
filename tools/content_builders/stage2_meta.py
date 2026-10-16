"""Curriculum additions for stage 2 (Day 36-70)."""

NEW_CONCEPTS = {
    # week 6
    "class": "클래스와 객체", "method": "메서드", "dunder": "특수 메서드", "inheritance": "상속",
    "property": "캡슐화와 프로퍼티", "classmethod": "클래스 변수·classmethod·dataclass",
    # week 7
    "comprehension": "컴프리헨션", "conditional_expr": "조건부 표현식", "iterator": "이터레이터",
    "generator": "제너레이터", "closure": "일급 함수와 클로저", "decorator": "데코레이터",
    # week 8
    "numpy_array": "NumPy 배열", "numpy_ops": "배열 연산·브로드캐스팅", "numpy_indexing": "배열 인덱싱·마스크",
    "numpy_aggregate": "집계와 축(axis)", "numpy_reshape": "모양 바꾸기·행렬 곱", "numpy_random": "난수와 시뮬레이션",
    # week 9
    "pandas_basics": "Series·DataFrame", "pandas_select": "데이터 선택·필터", "pandas_transform": "정렬·새 열·apply",
    "pandas_missing": "결측치 처리", "pandas_groupby": "그룹별 집계", "pandas_merge": "합치기(merge·concat)",
    # week 10
    "matplotlib": "matplotlib 그래프", "plot_types": "그래프 종류", "eda": "탐색적 데이터 분석",
}

DAYS = [
    (36, "클래스와 객체"), (37, "메서드"), (38, "특수 메서드"), (39, "상속"), (40, "캡슐화와 프로퍼티"),
    (41, "클래스 변수와 dataclass"), (42, "6주차 누적 복습"),
    (43, "리스트 컴프리헨션"), (44, "딕셔너리·집합 컴프리헨션과 조건부 표현식"), (45, "이터레이터"), (46, "제너레이터"),
    (47, "일급 함수와 클로저"), (48, "데코레이터"), (49, "7주차 누적 복습"),
    (50, "NumPy 배열 만들기"), (51, "배열 연산과 브로드캐스팅"), (52, "인덱싱과 불리언 마스크"), (53, "집계와 축"),
    (54, "모양 바꾸기와 행렬 곱"), (55, "난수와 시뮬레이션"), (56, "8주차 누적 복습"),
    (57, "Series와 DataFrame"), (58, "데이터 선택과 필터"), (59, "정렬·새 열·apply"), (60, "결측치 처리"),
    (61, "그룹별 집계"), (62, "데이터 합치기"), (63, "9주차 누적 복습"),
    (64, "matplotlib 기초"), (65, "막대·히스토그램·산점도"), (66, "pandas 그래프와 여러 그래프"),
    (67, "EDA 1: 데이터 살펴보기"), (68, "EDA 2: 상관관계와 이상치"), (69, "미니 프로젝트: 판매 데이터 분석"),
    (70, "2단계 마무리 누적 복습"),
]


def day_entries(first: int, upto: int) -> list[dict]:
    return [{"day": d, "title": title, "file": f"lessons/day{d:02d}.json", "is_review": d % 7 == 0}
            for d, title in DAYS if first <= d <= upto]
