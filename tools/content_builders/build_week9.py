"""Week 9 (Day 57-63): pandas."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 9, "advanced_data", 15


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


# ---------------------------------------------------------------- shared sample data
STUDENTS = {"이름": ["민준", "서연", "지호", "하나", "도윤"], "반": ["A", "B", "A", "B", "A"],
            "국어": [85, 92, 78, 66, 90], "수학": [70, 88, 95, 72, 60]}


# ---------------------------------------------------------------- references
def ref_summary(data):
    df = pd.DataFrame(data)
    means = df.mean(numeric_only=True).round(2)
    return {"rows": len(df), "cols": list(df.columns), "means": {k: float(v) for k, v in means.items()}}


def ref_filter(data, subject, cut, cls):
    df = pd.DataFrame(data)
    sel = df[(df[subject] >= cut) & (df["반"] == cls)].sort_values(subject, ascending=False)
    return sel["이름"].tolist()


def ref_grades(data):
    df = pd.DataFrame(data)
    df["평균"] = ((df["국어"] + df["수학"]) / 2).round(1)
    df["학점"] = df["평균"].apply(lambda m: "A" if m >= 90 else "B" if m >= 80 else "C" if m >= 70 else "F")
    df = df.sort_values(["평균", "이름"], ascending=[False, True])
    return df[["이름", "평균", "학점"]].to_dict("records")


def ref_clean(data):
    df = pd.DataFrame(data)
    df = df.dropna(subset=["이름"])
    filled = int(df[["국어", "수학"]].isna().sum().sum())
    for col in ["국어", "수학"]:
        df[col] = df[col].fillna(df[col].median())
    return [df.to_dict("records"), filled]


def ref_sales(data):
    df = pd.DataFrame(data)
    df["매출"] = df["가격"] * df["수량"]
    g = df.groupby("분류").agg(매출=("매출", "sum"), 건수=("매출", "size")).reset_index()
    g = g.sort_values(["매출", "분류"], ascending=[False, True])
    return [[r.분류, int(r.매출), int(r.건수)] for r in g.itertuples()]


def ref_revenue(orders, products):
    df = pd.merge(pd.DataFrame(orders), pd.DataFrame(products), on="상품", how="left")
    df["금액"] = df["수량"] * df["가격"]
    s = df.groupby("고객")["금액"].sum().sort_values(ascending=False)
    return {k: int(v) for k, v in s.items()}


def ref_pivot(data):
    df = pd.DataFrame(data)
    p = df.pivot_table(index="반", columns="성별", values="점수", aggfunc="mean").round(1)
    return {cls: {col: (None if pd.isna(v) else float(v)) for col, v in row.items()} for cls, row in p.iterrows()}


def ref_analysis(data):
    df = pd.DataFrame(data)
    df["총점"] = df["국어"] + df["수학"]
    best = df.loc[df["총점"].idxmax(), "이름"]
    cls_mean = df.groupby("반")["총점"].mean().round(1)
    return {"best": best, "class_mean": {k: float(v) for k, v in cls_mean.items()},
            "over_150": int((df["총점"] > 150).sum())}


# ====================================================================== Day 57
sum_cases = [(STUDENTS, "t1", "학생 표"), ({"x": [1, 2], "y": [3.5, 4.5], "z": ["a", "b"]}, "h1", ""), ({"v": [10]}, "h2", "")]
day57 = L(
    57, "Series와 DataFrame", W, ["pandas_basics", "dict"],
    ["pandas의 Series(1차원)와 DataFrame(표)을 만들 수 있다.", "shape, columns, head, dtypes로 표의 구조를 확인할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "8주차 NumPy 배열은 숫자에 강하지만 행·열에 이름이 없습니다. **pandas**는 NumPy 위에 이름표(인덱스·열 이름)를 붙여 "
        "엑셀 같은 표 데이터를 다루게 해 줍니다. 관례적으로 `import pandas as pd`로 불러옵니다."),
        "quiz": [quiz("d57_review_q1", "(4, 3) 배열의 `mean(axis=0)` 결과 모양은?", ["(4,)", "(3,)", "스칼라", "(4, 3)"], 1, "")]},
    concept={"title": "이름표가 있는 데이터", "blocks": [
        text("**Series**는 이름표(인덱스)가 붙은 1차원 데이터입니다. 인덱스로 값을 찾고, NumPy처럼 계산할 수 있습니다."),
        C('''
            import pandas as pd

            s = pd.Series([85, 92, 78], index=["민준", "서연", "지호"])
            print(s)
            print(s["서연"])
            print(s.mean())
        '''),
        text("**DataFrame**은 여러 Series를 열로 모은 표입니다. 딕셔너리(열 이름 → 값 목록)로 만드는 방법이 가장 흔합니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({
                "이름": ["민준", "서연", "지호"],
                "국어": [85, 92, 78],
                "수학": [70, 88, 95],
            })
            print(df)
            print(df.shape)
            print(df.columns.tolist())
            print(df.head(2))
        '''),
        tip("실제 파일은 `pd.read_csv(\"파일.csv\")`로 바로 DataFrame으로 읽습니다(Day 32의 CSV를 한 줄로!). 이 앱에서는 파일 대신 코드 안에서 표를 만들어 연습합니다."),
    ]},
    fill_intro="딕셔너리로 DataFrame을 만들고 모양을 확인하세요.",
    coding_intro="표의 기본 정보를 요약하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`import pandas as pd`.",
        "`pd.Series(값, index=이름표)`: 이름표 있는 1차원.",
        "`pd.DataFrame({열이름: 값목록})`: 표.",
        "`shape`, `columns`, `head(n)`, `dtypes`로 구조 확인."],
        "quiz": [
            quiz("d57_summary_q1", "행 5개, 열 3개인 DataFrame의 `shape`는?", ["(3, 5)", "(5, 3)", "15", "5"], 1, ""),
            quiz("d57_summary_q2", "`df.head(2)`의 결과는?", ["처음 2행", "처음 2열", "마지막 2행", "2번째 행"], 0, "")]},
    exercises=[
        ex("d57_fill_1", "fill_blank", "표 만들기",
           "열 이름 → 값 목록 딕셔너리로 DataFrame을 만들고 `[행 수, 열 수]`를 반환하세요.",
           ["pandas_basics"], 1,
           '''
            import pandas as pd


            def table_shape(data):
                df = pd.____(data)
                return list(df.____)
           ''',
           [t("t1", args=[{"a": [1, 2, 3], "b": [4, 5, 6]}], ret=[3, 2], desc="3×2"), t("h1", args=[{"x": [1]}], ret=[1, 1])],
           ["표를 만드는 pandas 클래스 이름입니다.", "(행 수, 열 수) 튜플을 담은 속성입니다."],
           '''
            import pandas as pd


            def table_shape(data):
                df = pd.DataFrame(data)
                return list(df.shape)
           ''', mode="function", name="table_shape", time_limit=TL),
        ex("d57_code_1", "coding", "표 요약",
           "열 이름 → 값 목록 딕셔너리를 DataFrame으로 만들고 다음을 반환하세요.\n\n"
           "- `rows`: 행 수, `cols`: 열 이름 리스트\n- `means`: **숫자 열**의 평균(소수 둘째 자리 반올림) 딕셔너리\n\n"
           "숫자 열만 평균을 내려면 `df.mean(numeric_only=True)`를 쓰세요.",
           ["pandas_basics"], 2,
           '''
            import pandas as pd


            def summary(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[d_], ret=ref_summary(d_), desc=ds, compare={"mode": "float", "tol": 1e-9}) for d_, tid, ds in sum_cases],
           ["`len(df)`는 행 수, `list(df.columns)`는 열 이름입니다.",
            "`df.mean(numeric_only=True).round(2)`는 Series이고, `.to_dict()`로 딕셔너리가 됩니다."],
           '''
            import pandas as pd


            def summary(data):
                df = pd.DataFrame(data)
                means = df.mean(numeric_only=True).round(2)
                return {"rows": len(df), "cols": list(df.columns), "means": means.to_dict()}
           ''', mode="function", name="summary", time_limit=TL),
    ])

# ====================================================================== Day 58
day58 = L(
    58, "데이터 선택과 필터", W, ["pandas_select", "pandas_basics"],
    ["열 선택, loc/iloc로 원하는 행·열을 꺼낼 수 있다.", "조건(불리언 마스크)으로 행을 거를 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 Series와 DataFrame을 만들고 구조를 확인했습니다.",
            "quiz": [quiz("d58_review_q1", "DataFrame의 열 이름 목록을 얻는 속성은?", ["`df.index`", "`df.columns`", "`df.shape`", "`df.names`"], 1, "")]},
    concept={"title": "원하는 부분만 꺼내기", "blocks": [
        text("`df[\"열\"]`은 한 열(Series), `df[[\"열1\", \"열2\"]]`는 여러 열(DataFrame)입니다. 행은 `loc[인덱스 이름, 열 이름]`(이름 기준) 또는 `iloc[번호, 번호]`(위치 기준)로 꺼냅니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["민준", "서연", "지호"], "국어": [85, 92, 78], "수학": [70, 88, 95]})
            print(df["국어"].tolist())
            print(df[["이름", "수학"]])
            print(df.loc[1, "이름"])
            print(df.iloc[2].tolist())
        '''),
        text("NumPy처럼 조건으로 만든 마스크로 행을 거릅니다. 조건은 `&`, `|`와 괄호로 묶고, `loc[조건, 열]`로 거른 행의 특정 열만 꺼낼 수 있습니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["민준", "서연", "지호"], "국어": [85, 92, 78], "수학": [70, 88, 95]})
            print(df[df["수학"] >= 80])
            print(df[(df["국어"] > 80) & (df["수학"] > 80)]["이름"].tolist())
            print(df.loc[df["국어"] < 90, "이름"].tolist())
        '''),
        tip("`df[조건]`의 결과도 DataFrame이라 이어서 열을 고를 수 있습니다. 거른 결과의 인덱스는 원래 번호를 유지합니다(0, 2처럼 건너뛸 수 있음)."),
    ]},
    fill_intro="기준 이상인 학생 이름을 꺼내세요.",
    coding_intro="여러 조건으로 거르고 정렬해 이름 목록을 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`df[\"열\"]`, `df[[\"열1\", \"열2\"]]`.",
        "`loc[행 이름, 열 이름]`, `iloc[행 번호, 열 번호]`.",
        "`df[조건]`, 여러 조건은 `&`/`|`와 괄호.",
        "`loc[조건, \"열\"]`로 거른 행의 열만."],
        "quiz": [
            quiz("d58_summary_q1", "위치(번호) 기준으로 행을 꺼내는 것은?", ["`loc`", "`iloc`", "`at`", "`df[0]`"], 1, ""),
            quiz("d58_summary_q2", "`df[df[\"점수\"] > 90]`의 결과는?", ["불리언 Series", "점수가 90 초과인 행들", "점수 열", "오류"], 1, "")]},
    exercises=[
        ex("d58_fill_1", "fill_blank", "기준 이상 이름",
           "`{\"이름\": [...], \"점수\": [...]}` 데이터에서 점수가 `cut` 이상인 학생의 이름 리스트를 반환하세요.",
           ["pandas_select"], 1,
           '''
            import pandas as pd


            def names_over(data, cut):
                df = pd.DataFrame(data)
                return df.____[df["점수"] >= cut, "____"].tolist()
           ''',
           [t("t1", args=[{"이름": ["a", "b", "c"], "점수": [50, 80, 90]}, 80], ret=["b", "c"], desc="기본"),
            t("h1", args=[{"이름": ["x"], "점수": [1]}, 2], ret=[])],
           ["조건과 열 이름을 함께 쓰는 이름 기준 접근자입니다.", "꺼낼 열 이름입니다."],
           '''
            import pandas as pd


            def names_over(data, cut):
                df = pd.DataFrame(data)
                return df.loc[df["점수"] >= cut, "이름"].tolist()
           ''', mode="function", name="names_over", time_limit=TL),
        ex("d58_code_1", "coding", "반별 우수 학생",
           "학생 데이터(이름·반·국어·수학 열)에서 반이 `class_name`이고 `subject` 점수가 `cut` 이상인 학생 이름을 **그 과목 점수 높은 순**으로 반환하세요.\n\n"
           "예: `(학생표, \"국어\", 80, \"A\")` → `[\"도윤\", \"민준\"]`",
           ["pandas_select", "pandas_basics"], 2,
           '''
            import pandas as pd


            def top_in_class(data, subject, cut, class_name):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[STUDENTS, "국어", 80, "A"], ret=ref_filter(STUDENTS, "국어", 80, "A"), desc="A반 국어"),
            t("h1", args=[STUDENTS, "수학", 70, "B"], ret=ref_filter(STUDENTS, "수학", 70, "B")),
            t("h2", args=[STUDENTS, "수학", 100, "A"], ret=[])],
           ["두 조건을 `&`로 묶은 마스크로 거르세요(각 조건은 괄호로).",
            "정렬은 `sort_values(열, ascending=False)`입니다(Day 59에서 자세히).", "마지막에 `[\"이름\"].tolist()`."],
           '''
            import pandas as pd


            def top_in_class(data, subject, cut, class_name):
                df = pd.DataFrame(data)
                selected = df[(df[subject] >= cut) & (df["반"] == class_name)]
                return selected.sort_values(subject, ascending=False)["이름"].tolist()
           ''', mode="function", name="top_in_class", time_limit=TL),
    ])

# ====================================================================== Day 59
small = {"이름": ["민준", "서연", "지호", "하나"], "국어": [85, 92, 78, 60], "수학": [95, 88, 61, 70]}
day59 = L(
    59, "정렬·새 열·apply", W, ["pandas_transform", "pandas_select", "lambda"],
    ["sort_values로 정렬하고 계산으로 새 열을 만들 수 있다.", "apply, map, str 메서드로 열의 값을 변환할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `loc`, `iloc`, 조건 마스크로 원하는 데이터를 골랐습니다.",
            "quiz": [quiz("d59_review_q1", "`df.loc[df[\"수학\"] > 80, \"이름\"]`이 돌려주는 것은?", ["수학 80 초과인 사람의 이름", "모든 이름", "수학 점수", "오류"], 0, "")]},
    concept={"title": "표 다듬기", "blocks": [
        text("`sort_values(열, ascending=False)`로 정렬하고, `df[\"새 열\"] = 계산식`으로 열을 추가합니다. 열끼리의 계산은 NumPy처럼 행마다 이루어집니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["민준", "서연", "지호"], "국어": [85, 92, 78], "수학": [95, 88, 61]})
            df["총점"] = df["국어"] + df["수학"]
            print(df.sort_values("총점", ascending=False))
        '''),
        text("`apply(함수)`는 열의 값마다 함수를 적용하고, `map(딕셔너리)`는 값을 바꿔치기합니다. 문자열 열은 `.str.메서드()`로 한꺼번에 처리합니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["kim", "lee"], "점수": [72, 95], "반": ["A", "B"]})
            df["결과"] = df["점수"].apply(lambda s: "합격" if s >= 80 else "재시험")
            df["담임"] = df["반"].map({"A": "박선생", "B": "최선생"})
            df["이름"] = df["이름"].str.upper()
            print(df)
        '''),
        tip("여러 기준 정렬은 `sort_values([\"열1\", \"열2\"], ascending=[False, True])`처럼 리스트로 줍니다. Day 25의 `key=lambda` 정렬과 같은 개념이에요."),
    ]},
    fill_intro="총점 열을 만들고 정렬하세요.",
    coding_intro="평균과 학점 열을 만들어 정렬된 기록으로 반환하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`df.sort_values(열, ascending=False)`, 여러 기준은 리스트.",
        "`df[\"새 열\"] = 식`으로 열 추가.",
        "`apply(함수)`, `map(딕셔너리)`, `.str.메서드()`.",
        "`to_dict(\"records\")`는 행마다 딕셔너리인 리스트."],
        "quiz": [
            quiz("d59_summary_q1", "점수 내림차순 정렬은?", ["`sort_values(\"점수\")`", "`sort_values(\"점수\", ascending=False)`", "`sort(\"점수\")`", "`df.sort()`"], 1, ""),
            quiz("d59_summary_q2", "`df[\"이름\"].str.len()`의 결과는?", ["이름 열의 길이(행 수)", "각 이름의 글자 수", "오류", "열 개수"], 1, "")]},
    exercises=[
        ex("d59_fill_1", "fill_blank", "총점 순위",
           "국어·수학 점수로 `총점` 열을 만들고, 총점 높은 순으로 정렬한 **이름 리스트**를 반환하세요.",
           ["pandas_transform"], 1,
           '''
            import pandas as pd


            def ranking(data):
                df = pd.DataFrame(data)
                df["총점"] = df["국어"] ____ df["수학"]
                return df.sort_values("총점", ascending=____)["이름"].tolist()
           ''',
           [t("t1", args=[small], ret=["민준", "서연", "지호", "하나"], desc="기본"), t("h1", args=[{"이름": ["a", "b"], "국어": [0, 1], "수학": [0, 0]}], ret=["b", "a"])],
           ["두 열을 더하는 연산자입니다.", "높은 순(내림차순)이 되도록 오름차순 여부를 정하세요."],
           '''
            import pandas as pd


            def ranking(data):
                df = pd.DataFrame(data)
                df["총점"] = df["국어"] + df["수학"]
                return df.sort_values("총점", ascending=False)["이름"].tolist()
           ''', mode="function", name="ranking", time_limit=TL),
        ex("d59_code_1", "coding", "평균과 학점",
           "국어·수학 점수로 `평균`(소수 첫째 자리 반올림)과 `학점`(90 이상 A, 80 이상 B, 70 이상 C, 그 외 F) 열을 만드세요. "
           "평균 높은 순(같으면 이름 순)으로 정렬해 `이름`, `평균`, `학점` 세 열만 `to_dict(\"records\")`로 반환하세요.",
           ["pandas_transform", "lambda", "conditional_expr"], 2,
           '''
            import pandas as pd


            def add_grades(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[small], ret=ref_grades(small), desc="기본", compare={"mode": "float", "tol": 1e-9}),
            t("h1", args=[STUDENTS], ret=ref_grades(STUDENTS), compare={"mode": "float", "tol": 1e-9})],
           ["평균 열은 `((국어 + 수학) / 2).round(1)`.", "학점은 평균 열에 `apply`로 함수(또는 lambda)를 적용합니다.",
            "`sort_values([\"평균\", \"이름\"], ascending=[False, True])` 후 `df[[\"이름\", \"평균\", \"학점\"]].to_dict(\"records\")`."],
           '''
            import pandas as pd


            def to_grade(m):
                if m >= 90:
                    return "A"
                if m >= 80:
                    return "B"
                if m >= 70:
                    return "C"
                return "F"


            def add_grades(data):
                df = pd.DataFrame(data)
                df["평균"] = ((df["국어"] + df["수학"]) / 2).round(1)
                df["학점"] = df["평균"].apply(to_grade)
                df = df.sort_values(["평균", "이름"], ascending=[False, True])
                return df[["이름", "평균", "학점"]].to_dict("records")
           ''', mode="function", name="add_grades", time_limit=TL),
    ])

# ====================================================================== Day 60
messy = {"이름": ["민준", None, "지호", "하나", "도윤"], "국어": [85, 90, None, 66, 70], "수학": [70, 88, 95, None, None]}
messy2 = {"이름": ["a", "b"], "국어": [None, 4], "수학": [1, 3]}
day60 = L(
    60, "결측치 처리", W, ["pandas_missing", "pandas_select"],
    ["빈 값(결측치, NaN)을 찾고 개수를 셀 수 있다.", "dropna, fillna로 결측치를 지우거나 채울 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 정렬과 새 열, `apply`를 배웠습니다.",
            "quiz": [quiz("d60_review_q1", "열마다 함수를 적용해 새 값으로 바꾸는 메서드는?", ["`sort_values`", "`apply`", "`head`", "`shape`"], 1, "")]},
    concept={"title": "비어 있는 칸 다루기", "blocks": [
        text("실제 데이터에는 빈 칸이 흔합니다. pandas는 빈 값을 **NaN**(Not a Number)으로 표시합니다. `isna()`로 찾고, `sum()`으로 열별 개수를 셉니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["민준", None, "지호"], "점수": [85, 90, None]})
            print(df)
            print(df.isna().sum())
        '''),
        text("`dropna()`는 빈 값이 있는 행을 지우고(`subset=[열]`로 특정 열만 볼 수 있음), `fillna(값)`은 빈 값을 채웁니다. 숫자는 평균·중앙값으로 채우는 경우가 많습니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["민준", None, "지호"], "점수": [85, 90, None]})
            print(df.dropna())
            print(df.dropna(subset=["이름"]))
            df["점수"] = df["점수"].fillna(df["점수"].mean())
            print(df["점수"].tolist())
        '''),
        tip("결측치를 지우면 데이터가 줄고, 채우면 없는 값을 지어내는 셈입니다. 어떤 방법이 맞는지는 데이터의 의미에 따라 다릅니다. 평균은 극단값에 흔들리므로 중앙값(`median`)이 더 안전할 때도 있어요."),
    ]},
    fill_intro="점수 열의 빈 값을 평균으로 채우세요.",
    coding_intro="이름이 없는 행은 지우고, 점수의 빈 값은 열의 중앙값으로 채우세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "결측치 = NaN, `isna()`로 찾고 `isna().sum()`으로 개수.",
        "`dropna()` 행 삭제, `subset=[열]`로 특정 열 기준.",
        "`fillna(값)`으로 채우기 (평균·중앙값 등).",
        "지울지 채울지는 데이터의 의미를 보고 정한다."],
        "quiz": [
            quiz("d60_summary_q1", "열별 결측치 개수를 구하는 코드는?", ["`df.isna().sum()`", "`df.count()`", "`df.dropna()`", "`len(df)`"], 0, ""),
            quiz("d60_summary_q2", "극단값이 있을 때 결측치를 채우기에 더 안전한 대표값은?", ["평균", "중앙값", "최댓값", "0"], 1, "")]},
    exercises=[
        ex("d60_fill_1", "fill_blank", "평균으로 채우기",
           "`점수` 열의 빈 값(None)을 그 열의 평균으로 채운 점수 리스트를 반환하세요.",
           ["pandas_missing"], 1,
           '''
            import pandas as pd


            def fill_scores(data):
                df = pd.DataFrame(data)
                df["점수"] = df["점수"].____(df["점수"].____())
                return df["점수"].tolist()
           ''',
           [t("t1", args=[{"점수": [80, None, 100]}], ret=[80.0, 90.0, 100.0], desc="하나 비어 있음"), t("h1", args=[{"점수": [1, 2]}], ret=[1, 2])],
           ["빈 값을 채우는 메서드입니다.", "평균을 구하는 메서드입니다."],
           '''
            import pandas as pd


            def fill_scores(data):
                df = pd.DataFrame(data)
                df["점수"] = df["점수"].fillna(df["점수"].mean())
                return df["점수"].tolist()
           ''', mode="function", name="fill_scores", time_limit=TL),
        ex("d60_code_1", "coding", "데이터 청소",
           "이름·국어·수학 열이 있는 데이터를 정리하세요.\n\n"
           "1. `이름`이 비어 있는 행은 지웁니다.\n2. 남은 행에서 국어·수학의 빈 값 개수를 셉니다.\n3. 국어·수학의 빈 값을 **각 열의 중앙값**(남은 행 기준)으로 채웁니다.\n\n"
           "`[정리된 표의 to_dict(\"records\"), 채운 칸 수]`를 반환하세요.",
           ["pandas_missing", "pandas_select"], 2,
           '''
            import pandas as pd


            def clean(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[messy], ret=ref_clean(messy), desc="여러 결측치", compare={"mode": "float", "tol": 1e-9}),
            t("h1", args=[messy2], ret=ref_clean(messy2), compare={"mode": "float", "tol": 1e-9})],
           ["`df.dropna(subset=[\"이름\"])`로 이름 없는 행을 먼저 지우세요.",
            "채우기 전에 `df[[\"국어\", \"수학\"]].isna().sum().sum()`으로 빈 칸 수를 셉니다(`int()`로 바꾸기).",
            "열마다 `df[열] = df[열].fillna(df[열].median())`."],
           '''
            import pandas as pd


            def clean(data):
                df = pd.DataFrame(data)
                df = df.dropna(subset=["이름"])
                filled = int(df[["국어", "수학"]].isna().sum().sum())
                for col in ["국어", "수학"]:
                    df[col] = df[col].fillna(df[col].median())
                return [df.to_dict("records"), filled]
           ''', mode="function", name="clean", time_limit=TL),
    ])

# ====================================================================== Day 61
SALES = {"상품": ["펜", "노트", "물", "빵", "펜", "우유"], "분류": ["문구", "문구", "식품", "식품", "문구", "식품"],
         "가격": [1000, 3000, 800, 2500, 1000, 1800], "수량": [3, 1, 5, 2, 2, 1]}
day61 = L(
    61, "그룹별 집계", W, ["pandas_groupby", "pandas_transform"],
    ["groupby로 그룹별 합계·평균·개수를 구할 수 있다.", "agg로 여러 집계를 한 번에 계산할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 결측치를 찾고 지우거나 채웠습니다.",
            "quiz": [quiz("d61_review_q1", "이름 열이 빈 행만 지우는 코드는?", ["`df.dropna()`", "`df.dropna(subset=[\"이름\"])`", "`df.fillna(\"이름\")`", "`df.isna()`"], 1, "")]},
    concept={"title": "기준별로 묶어 요약하기", "blocks": [
        text("`groupby(기준열)`은 Day 17의 **그룹화 패턴**을 한 줄로 해 줍니다. 그다음 열을 고르고 `sum`, `mean`, `count`, `size` 등으로 요약합니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"반": ["A", "B", "A", "B", "A"], "점수": [85, 92, 78, 66, 90]})
            print(df.groupby("반")["점수"].mean())
            print(df.groupby("반").size())
        '''),
        text("`agg`로 여러 집계를 한 번에 하고, 결과 열 이름도 정할 수 있습니다. `reset_index()`는 그룹 이름을 다시 일반 열로 돌려놓습니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"반": ["A", "B", "A", "B", "A"], "점수": [85, 92, 78, 66, 90]})
            result = df.groupby("반").agg(평균=("점수", "mean"), 최고=("점수", "max"), 인원=("점수", "size"))
            print(result.reset_index())
        '''),
        tip("groupby 결과의 인덱스는 그룹 이름입니다. 딕셔너리로 바꾸려면 `.to_dict()`, 일반 표로 쓰려면 `.reset_index()`를 붙이세요."),
    ]},
    fill_intro="반별 평균을 딕셔너리로 반환하세요.",
    coding_intro="분류별 매출 합계와 판매 건수를 구해 매출 순으로 정리하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`df.groupby(기준)[열].집계()`.",
        "`size()`는 그룹별 행 수.",
        "`agg(이름=(열, \"함수\"))`로 여러 집계.",
        "`reset_index()`로 그룹 이름을 열로."],
        "quiz": [
            quiz("d61_summary_q1", "반별 학생 수를 구하는 코드는?", ["`df.groupby(\"반\").size()`", "`df[\"반\"].sum()`", "`df.size`", "`len(df.groupby(\"반\"))`"], 0, ""),
            quiz("d61_summary_q2", "`df.groupby(\"반\")[\"점수\"].max()`의 결과 인덱스는?", ["0, 1, 2…", "반 이름", "점수", "열 이름"], 1, "")]},
    exercises=[
        ex("d61_fill_1", "fill_blank", "반별 평균",
           "`반`, `점수` 열이 있는 데이터에서 반별 평균 점수를 `{반: 평균}` 딕셔너리로 반환하세요.",
           ["pandas_groupby"], 1,
           '''
            import pandas as pd


            def class_means(data):
                df = pd.DataFrame(data)
                return df.____("반")["점수"].mean().____()
           ''',
           [t("t1", args=[{"반": ["A", "B", "A"], "점수": [80, 70, 90]}], ret={"A": 85.0, "B": 70.0}, desc="기본"), t("h1", args=[{"반": ["X"], "점수": [5]}], ret={"X": 5.0})],
           ["기준 열로 묶는 메서드입니다.", "Series를 딕셔너리로 바꾸는 메서드입니다."],
           '''
            import pandas as pd


            def class_means(data):
                df = pd.DataFrame(data)
                return df.groupby("반")["점수"].mean().to_dict()
           ''', mode="function", name="class_means", time_limit=TL),
        ex("d61_code_1", "coding", "분류별 매출",
           "상품·분류·가격·수량 데이터에서 `매출 = 가격 × 수량` 열을 만들고, 분류별 **매출 합계와 판매 건수**(행 수)를 구하세요. "
           "매출 높은 순(같으면 분류 이름 순)으로 `[분류, 매출, 건수]` 리스트들을 반환하세요.",
           ["pandas_groupby", "pandas_transform"], 2,
           '''
            import pandas as pd


            def sales_by_category(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[SALES], ret=ref_sales(SALES), desc="기본"),
            t("h1", args=[{"상품": ["a", "b"], "분류": ["x", "y"], "가격": [10, 5], "수량": [1, 2]}], ret=ref_sales({"상품": ["a", "b"], "분류": ["x", "y"], "가격": [10, 5], "수량": [1, 2]}))],
           ["새 열을 만든 뒤 `groupby(\"분류\").agg(매출=(\"매출\", \"sum\"), 건수=(\"매출\", \"size\"))`.",
            "`reset_index()` 후 `sort_values([\"매출\", \"분류\"], ascending=[False, True])`.",
            "`itertuples()`나 `values.tolist()`로 행을 리스트로 바꿉니다. 숫자는 `int()`로."],
           '''
            import pandas as pd


            def sales_by_category(data):
                df = pd.DataFrame(data)
                df["매출"] = df["가격"] * df["수량"]
                g = df.groupby("분류").agg(매출=("매출", "sum"), 건수=("매출", "size")).reset_index()
                g = g.sort_values(["매출", "분류"], ascending=[False, True])
                return [[row.분류, int(row.매출), int(row.건수)] for row in g.itertuples()]
           ''', mode="function", name="sales_by_category", time_limit=TL),
    ])

# ====================================================================== Day 62
ORDERS = {"고객": ["민준", "서연", "민준", "지호"], "상품": ["펜", "노트", "노트", "펜"], "수량": [2, 1, 3, 5]}
PRODUCTS = {"상품": ["펜", "노트"], "가격": [1000, 3000]}
day62 = L(
    62, "데이터 합치기", W, ["pandas_merge", "pandas_groupby"],
    ["merge로 공통 열을 기준으로 두 표를 이을 수 있다.", "concat으로 표를 위아래로 붙일 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `groupby`로 그룹별 요약을 했습니다.",
            "quiz": [quiz("d62_review_q1", "groupby 결과의 그룹 이름을 일반 열로 돌리는 메서드는?", ["`to_dict`", "`reset_index`", "`sort_values`", "`head`"], 1, "")]},
    concept={"title": "여러 표를 하나로", "blocks": [
        text("`pd.merge(왼쪽, 오른쪽, on=\"공통열\", how=\"left\")`는 공통 열 값이 같은 행끼리 옆으로 잇습니다(엑셀의 VLOOKUP). "
             "`how`는 `inner`(양쪽 모두 있는 것만), `left`(왼쪽 기준), `outer`(전부)."),
        C('''
            import pandas as pd

            students = pd.DataFrame({"번호": [1, 2, 3], "이름": ["민준", "서연", "지호"]})
            scores = pd.DataFrame({"번호": [1, 3, 4], "점수": [85, 78, 99]})
            print(pd.merge(students, scores, on="번호"))
            print(pd.merge(students, scores, on="번호", how="left"))
        '''),
        text("`pd.concat([표1, 표2])`는 같은 열을 가진 표를 위아래로 붙입니다. `ignore_index=True`로 인덱스를 새로 매깁니다."),
        C('''
            import pandas as pd

            jan = pd.DataFrame({"상품": ["펜"], "수량": [3]})
            feb = pd.DataFrame({"상품": ["노트", "펜"], "수량": [1, 2]})
            print(pd.concat([jan, feb], ignore_index=True))
        '''),
        tip("`how=\"left\"`에서 오른쪽에 짝이 없는 행은 NaN이 됩니다. 합친 뒤에는 Day 60에서 배운 결측치 확인을 습관처럼 하세요."),
    ]},
    fill_intro="주문 표에 상품 가격을 붙이세요.",
    coding_intro="주문과 상품 표를 합쳐 고객별 구매 금액을 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`pd.merge(a, b, on=열, how=...)`: 옆으로 잇기.",
        "`inner`, `left`, `outer`의 차이.",
        "`pd.concat([a, b], ignore_index=True)`: 위아래로 붙이기.",
        "합친 뒤 결측치를 확인한다."],
        "quiz": [
            quiz("d62_summary_q1", "왼쪽 표의 행을 모두 유지하며 합치는 옵션은?", ["`how=\"inner\"`", "`how=\"left\"`", "`how=\"right\"`", "`axis=1`"], 1, ""),
            quiz("d62_summary_q2", "1월·2월 판매 표(같은 열)를 위아래로 붙이는 함수는?", ["`pd.merge`", "`pd.concat`", "`df.join`", "`groupby`"], 1, "")]},
    exercises=[
        ex("d62_fill_1", "fill_blank", "가격 붙이기",
           "주문 표와 상품 표를 `상품` 열로 합쳐(`how=\"left\"`) **주문 순서대로의 가격 리스트**를 반환하세요.",
           ["pandas_merge"], 1,
           '''
            import pandas as pd


            def prices(orders, products):
                df = pd.____(pd.DataFrame(orders), pd.DataFrame(products), on="____", how="left")
                return df["가격"].tolist()
           ''',
           [t("t1", args=[ORDERS, PRODUCTS], ret=[1000, 3000, 3000, 1000], desc="기본"),
            t("h1", args=[{"고객": ["a", "b"], "상품": ["y", "x"], "수량": [1, 1]}, {"상품": ["x", "y"], "가격": [5, 7]}], ret=[7, 5])],
           ["두 표를 공통 열로 잇는 pandas 함수입니다.", "두 표에 모두 있는 열 이름입니다."],
           '''
            import pandas as pd


            def prices(orders, products):
                df = pd.merge(pd.DataFrame(orders), pd.DataFrame(products), on="상품", how="left")
                return df["가격"].tolist()
           ''', mode="function", name="prices", time_limit=TL),
        ex("d62_code_1", "coding", "고객별 구매 금액",
           "주문 표(고객·상품·수량)와 상품 표(상품·가격)를 합쳐 `금액 = 수량 × 가격`을 구하고, 고객별 합계를 **금액 큰 순**으로 `{고객: 금액}` 딕셔너리로 반환하세요.",
           ["pandas_merge", "pandas_groupby"], 2,
           '''
            import pandas as pd


            def revenue_by_customer(orders, products):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[ORDERS, PRODUCTS], ret=ref_revenue(ORDERS, PRODUCTS), desc="기본"),
            t("h1", args=[{"고객": ["a"], "상품": ["x"], "수량": [4]}, {"상품": ["x"], "가격": [25]}], ret={"a": 100})],
           ["`pd.merge(..., on=\"상품\", how=\"left\")`로 합친 뒤 금액 열을 만드세요.",
            "`groupby(\"고객\")[\"금액\"].sum()`을 `sort_values(ascending=False)`로 정렬합니다.",
            "딕셔너리로 바꿀 때 값은 `int()`로 바꿔 두면 깔끔합니다."],
           '''
            import pandas as pd


            def revenue_by_customer(orders, products):
                df = pd.merge(pd.DataFrame(orders), pd.DataFrame(products), on="상품", how="left")
                df["금액"] = df["수량"] * df["가격"]
                totals = df.groupby("고객")["금액"].sum().sort_values(ascending=False)
                return {name: int(amount) for name, amount in totals.items()}
           ''', mode="function", name="revenue_by_customer", time_limit=TL),
    ])

# ====================================================================== Day 63 (review)
PIV = {"반": ["A", "A", "B", "B", "A"], "성별": ["남", "여", "여", "여", "남"], "점수": [80, 90, 70, 75, 60]}
day63 = L(
    63, "9주차 누적 복습", W, ["pandas_basics", "pandas_select", "pandas_transform", "pandas_missing", "pandas_groupby", "pandas_merge"],
    ["pandas의 선택·변환·결측치·그룹·합치기를 조합해 질문에 답할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 57 | 기본 | `pd.DataFrame`, `shape`, `columns` |\n"
        "| 58 | 선택 | `loc`, `iloc`, `df[조건]` |\n"
        "| 59 | 변환 | `sort_values`, 새 열, `apply`, `map` |\n"
        "| 60 | 결측치 | `isna`, `dropna`, `fillna` |\n"
        "| 61 | 그룹 | `groupby`, `agg`, `size` |\n"
        "| 62 | 합치기 | `merge`, `concat` |"),
        "quiz": [
            quiz("d63_review_q1", "\"반별 평균 총점\"을 구하는 순서로 알맞은 것은?", ["groupby → 새 열", "새 열(총점) → groupby → mean", "merge → dropna", "sort → head"], 1, ""),
            quiz("d63_review_q2", "`df[\"총점\"].idxmax()`가 돌려주는 것은?", ["가장 큰 총점", "가장 큰 총점이 있는 행의 인덱스", "열 이름", "총점 개수"], 1, "")]},
    concept={"title": "질문 → 코드", "blocks": [
        text("데이터 분석은 **질문을 코드로 옮기는 일**입니다. \"누가 1등인가?\" → 새 열 + `idxmax`, \"반별로 어떤가?\" → `groupby`, \"몇 명인가?\" → 조건의 `sum()`."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"이름": ["민준", "서연", "지호"], "반": ["A", "B", "A"], "국어": [85, 92, 78], "수학": [70, 88, 95]})
            df["총점"] = df["국어"] + df["수학"]
            print(df.loc[df["총점"].idxmax(), "이름"])
            print(df.groupby("반")["총점"].mean().to_dict())
            print(int((df["총점"] > 160).sum()))
        '''),
        tip("`pivot_table(index=행, columns=열, values=값, aggfunc=\"mean\")`은 엑셀의 피벗 테이블처럼 두 기준으로 동시에 요약합니다(도전 문제)."),
    ]},
    fill_intro="가장 높은 값을 가진 행의 이름을 찾으세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "9주차 마무리", "points": [
        "질문을 선택·변환·그룹 연산으로 번역한다.",
        "`idxmax`로 최댓값 행 찾기, 조건의 `sum()`으로 개수 세기.",
        "`pivot_table`로 두 기준 요약.",
        "다음 주: 그래프로 데이터를 보고 탐색적 분석을 한다."],
        "quiz": [
            quiz("d63_summary_q1", "점수가 80 이상인 학생 수는?", ["`df[\"점수\"] >= 80`", "`(df[\"점수\"] >= 80).sum()`", "`df[\"점수\"].count()`", "`len(df)`"], 1, ""),
            quiz("d63_summary_q2", "행=반, 열=성별로 평균 점수 표를 만드는 것은?", ["`groupby`", "`pivot_table`", "`concat`", "`merge`"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d63_fill_1", "fill_blank", "최고 점수의 주인",
           "`이름`과 `점수` 열이 있는 데이터에서 점수가 가장 높은 사람의 이름을 반환하세요.",
           ["pandas_select", "pandas_basics"], 1,
           '''
            import pandas as pd


            def top_name(data):
                df = pd.DataFrame(data)
                return df.loc[df["점수"].____(), "____"]
           ''',
           [t("t1", args=[{"이름": ["a", "b", "c"], "점수": [3, 9, 1]}], ret="b", desc="기본"), t("h1", args=[{"이름": ["x"], "점수": [0]}], ret="x")],
           ["가장 큰 값이 있는 **인덱스**를 돌려주는 메서드입니다.", "꺼낼 열 이름입니다."],
           '''
            import pandas as pd


            def top_name(data):
                df = pd.DataFrame(data)
                return df.loc[df["점수"].idxmax(), "이름"]
           ''', mode="function", name="top_name", time_limit=TL),
        ex("d63_code_1", "coding", "성적 분석",
           "이름·반·국어·수학 데이터를 분석해 딕셔너리를 반환하세요.\n\n"
           "- `best`: 총점(국어+수학) 1등의 이름\n- `class_mean`: 반별 총점 평균(소수 첫째 자리 반올림) 딕셔너리\n- `over_150`: 총점이 150 초과인 학생 수",
           ["pandas_select", "pandas_transform", "pandas_groupby"], 2,
           '''
            import pandas as pd


            def analyze(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[STUDENTS], ret=ref_analysis(STUDENTS), desc="학생 표", compare={"mode": "float", "tol": 1e-9}),
            t("h1", args=[{"이름": ["a", "b"], "반": ["X", "X"], "국어": [100, 50], "수학": [51, 50]}],
              ret=ref_analysis({"이름": ["a", "b"], "반": ["X", "X"], "국어": [100, 50], "수학": [51, 50]}), compare={"mode": "float", "tol": 1e-9})],
           ["먼저 총점 열을 만드세요.", "1등은 `idxmax`, 반별 평균은 `groupby(\"반\")[\"총점\"].mean().round(1).to_dict()`.", "개수는 조건 마스크의 `sum()`을 `int()`로."],
           '''
            import pandas as pd


            def analyze(data):
                df = pd.DataFrame(data)
                df["총점"] = df["국어"] + df["수학"]
                best = df.loc[df["총점"].idxmax(), "이름"]
                class_mean = df.groupby("반")["총점"].mean().round(1).to_dict()
                return {"best": best, "class_mean": class_mean, "over_150": int((df["총점"] > 150).sum())}
           ''', mode="function", name="analyze", time_limit=TL),
        ex("d63_code_2", "coding", "[도전] 피벗 테이블",
           "반·성별·점수 데이터로 행 = 반, 열 = 성별인 평균 점수 피벗 테이블(소수 첫째 자리 반올림)을 만들고 `{반: {성별: 평균}}` 딕셔너리로 반환하세요. 값이 없는 칸은 `None`입니다.",
           ["pandas_groupby", "pandas_missing"], 3,
           '''
            import pandas as pd


            def pivot(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[PIV], ret=ref_pivot(PIV), desc="빈 칸 포함", compare={"mode": "float", "tol": 1e-9}),
            t("h1", args=[{"반": ["C", "C"], "성별": ["남", "여"], "점수": [10, 20]}], ret={"C": {"남": 10.0, "여": 20.0}}, compare={"mode": "float", "tol": 1e-9})],
           ["`df.pivot_table(index=\"반\", columns=\"성별\", values=\"점수\", aggfunc=\"mean\").round(1)`.",
            "행마다 `iterrows()`로 돌며 안쪽 딕셔너리를 만들고, `pd.isna(값)`이면 `None`을 넣으세요."],
           '''
            import pandas as pd


            def pivot(data):
                df = pd.DataFrame(data)
                table = df.pivot_table(index="반", columns="성별", values="점수", aggfunc="mean").round(1)
                result = {}
                for cls, row in table.iterrows():
                    result[cls] = {col: (None if pd.isna(v) else float(v)) for col, v in row.items()}
                return result
           ''', mode="function", name="pivot", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day57, day58, day59, day60, day61, day62, day63])
