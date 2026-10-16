"""Week 10 (Day 64-70): 시각화와 EDA. Plot exercises are graded by inspecting the Axes the learner drew on."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 10, "advanced_data", 20


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


SHOW_TIP = ("이 앱에서는 코드 실행이 끝날 때 열려 있는 그래프가 **이미지로 실행 결과 아래에 표시**됩니다. "
            "`plt.show()`는 쓰지 않아도 됩니다(써도 괜찮아요). 한글 글꼴은 앱이 자동으로 설정합니다.")

# ---------------------------------------------------------------- references
def ref_hist(values, bins):
    counts, _ = np.histogram(values, bins=bins)
    return counts.tolist()


def ref_profile(data):
    df = pd.DataFrame(data)
    num = {c: {"mean": round(float(df[c].mean()), 2), "min": float(df[c].min()), "max": float(df[c].max())}
           for c in df.select_dtypes("number").columns}
    cat = {c: df[c].value_counts().index[0] for c in df.select_dtypes(exclude="number").columns}
    return {"rows": len(df), "numeric": num, "top": cat}


def ref_iqr(values):
    s = pd.Series(values, dtype=float)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return sorted(s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)].tolist())


SALES = {"월": [1, 1, 2, 2, 2, 3, 3], "상품": ["펜", "노트", "펜", "노트", "가방", "펜", "가방"],
         "매출": [3000, 6000, 4000, 3000, 20000, 5000, 15000]}


def ref_monthly(data):
    df = pd.DataFrame(data)
    monthly = df.groupby("월")["매출"].sum()
    best = df.groupby("상품")["매출"].sum().sort_values(ascending=False)
    growth = [round(float(x), 1) for x in (monthly.pct_change() * 100).dropna()]
    return {"monthly": [int(v) for v in monthly], "best": best.index[0], "growth": growth}


def ref_moving(values, window):
    return [round(float(x), 2) for x in pd.Series(values, dtype=float).rolling(window).mean().dropna()]


# ====================================================================== Day 64
day64 = L(
    64, "matplotlib 기초", W, ["matplotlib", "module"],
    ["matplotlib으로 선 그래프를 그리고 제목·축 이름·범례를 붙일 수 있다.", "Figure와 Axes의 관계를 이해한다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "9주차에는 pandas로 표를 다루고 요약했습니다. 숫자 표만 봐서는 흐름을 놓치기 쉽습니다. 이번 주는 **그래프**로 데이터를 보고(시각화), "
        "데이터를 탐색하는 방법(EDA)을 배웁니다."),
        "quiz": [quiz("d64_review_q1", "반별 평균을 구하는 pandas 코드는?", ["`df.mean(\"반\")`", "`df.groupby(\"반\")[\"점수\"].mean()`", "`df[\"반\"].mean()`", "`df.pivot()`"], 1, "")]},
    concept={"title": "첫 그래프 그리기", "blocks": [
        text("관례적으로 `import matplotlib.pyplot as plt`로 불러옵니다. `fig, ax = plt.subplots()`는 그림판(**Figure**)과 그 안의 그래프 영역(**Axes**)을 만듭니다. "
             "이후 `ax.메서드()`로 그리고 꾸밉니다."),
        C('''
            import matplotlib.pyplot as plt

            months = [1, 2, 3, 4]
            sales = [120, 150, 90, 180]
            fig, ax = plt.subplots()
            ax.plot(months, sales, marker="o", label="판매량")
            ax.set_title("월별 판매량")
            ax.set_xlabel("월")
            ax.set_ylabel("개수")
            ax.legend()
            print(ax.get_title(), len(ax.lines))
        '''),
        text("`plot`을 여러 번 부르면 같은 Axes에 선이 겹쳐 그려집니다. `label`을 주고 `legend()`를 부르면 범례가 생깁니다."),
        C('''
            import matplotlib.pyplot as plt
            import numpy as np

            x = np.linspace(0, 2 * np.pi, 50)
            fig, ax = plt.subplots()
            ax.plot(x, np.sin(x), label="sin")
            ax.plot(x, np.cos(x), label="cos", linestyle="--")
            ax.legend()
            ax.grid(True)
            print([line.get_label() for line in ax.lines])
        '''),
        tip(SHOW_TIP),
    ]},
    fill_intro="제목이 있는 선 그래프를 그리세요. `check`는 채점용으로, 그린 그래프의 정보를 꺼냅니다.",
    coding_intro="두 과목 점수를 선 두 개로 그리고 범례를 붙이세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`fig, ax = plt.subplots()`: 그림판과 그래프 영역.",
        "`ax.plot(x, y, label=..., marker=...)`: 선 그래프.",
        "`set_title`, `set_xlabel`, `set_ylabel`, `legend`, `grid`.",
        "같은 Axes에 여러 번 그리면 겹쳐진다."],
        "quiz": [
            quiz("d64_summary_q1", "범례를 표시하려면 `plot`에 무엇을 주고 무엇을 호출해야 하나?", ["`title`과 `show()`", "`label`과 `legend()`", "`marker`와 `grid()`", "`color`와 `bar()`"], 1, ""),
            quiz("d64_summary_q2", "`plt.subplots()`가 돌려주는 두 값은?", ["(x, y)", "(Figure, Axes)", "(Axes, legend)", "(title, label)"], 1, "")]},
    exercises=[
        ex("d64_fill_1", "fill_blank", "제목 있는 선 그래프",
           "`draw(ax, xs, ys, title)`가 주어진 Axes에 선 그래프를 그리고 제목을 붙이도록 완성하세요.",
           ["matplotlib"], 1,
           '''
            import matplotlib.pyplot as plt


            def draw(ax, xs, ys, title):
                ax.____(xs, ys)
                ax.set_title(____)


            def check(xs, ys, title):
                fig, ax = plt.subplots()
                draw(ax, xs, ys, title)
                return [ax.get_title(), len(ax.lines), ax.lines[0].get_ydata().tolist()]
           ''',
           [t("t1", args=[[1, 2, 3], [5, 3, 4], "점수"], ret=["점수", 1, [5, 3, 4]], desc="기본"), t("h1", args=[[0], [0], ""], ret=["", 1, [0]])],
           ["선 그래프를 그리는 Axes 메서드입니다.", "제목으로 쓸 매개변수 이름입니다."],
           '''
            import matplotlib.pyplot as plt


            def draw(ax, xs, ys, title):
                ax.plot(xs, ys)
                ax.set_title(title)


            def check(xs, ys, title):
                fig, ax = plt.subplots()
                draw(ax, xs, ys, title)
                return [ax.get_title(), len(ax.lines), ax.lines[0].get_ydata().tolist()]
           ''', mode="function", name="check", time_limit=TL),
        ex("d64_code_1", "coding", "두 과목 비교 그래프",
           "`plot_scores(ax, names, kor, math)`를 작성하세요. 같은 Axes에 국어 점수(`label=\"국어\"`)와 수학 점수(`label=\"수학\"`)를 이름을 x축으로 하는 선 두 개로 그리고, "
           "제목 `\"과목별 점수\"`, 범례를 붙입니다. `check`는 채점용입니다.",
           ["matplotlib"], 2,
           '''
            import matplotlib.pyplot as plt


            def plot_scores(ax, names, kor, math):
                # 여기에 코드를 작성하세요
                pass


            def check(names, kor, math):
                fig, ax = plt.subplots()
                plot_scores(ax, names, kor, math)
                legend = ax.get_legend()
                labels = [t.get_text() for t in legend.get_texts()] if legend else []
                return [ax.get_title(), labels, [line.get_ydata().tolist() for line in ax.lines]]
           ''',
           [t("t1", args=[["민준", "서연"], [85, 92], [70, 88]], ret=["과목별 점수", ["국어", "수학"], [[85, 92], [70, 88]]], desc="두 명"),
            t("h1", args=[["a"], [1], [2]], ret=["과목별 점수", ["국어", "수학"], [[1], [2]]])],
           ["`ax.plot(names, kor, label=\"국어\")`처럼 선마다 `label`을 줍니다.", "마지막에 `ax.set_title(...)`과 `ax.legend()`를 호출하세요."],
           '''
            import matplotlib.pyplot as plt


            def plot_scores(ax, names, kor, math):
                ax.plot(names, kor, marker="o", label="국어")
                ax.plot(names, math, marker="s", label="수학")
                ax.set_title("과목별 점수")
                ax.legend()


            def check(names, kor, math):
                fig, ax = plt.subplots()
                plot_scores(ax, names, kor, math)
                legend = ax.get_legend()
                labels = [t.get_text() for t in legend.get_texts()] if legend else []
                return [ax.get_title(), labels, [line.get_ydata().tolist() for line in ax.lines]]
           ''', mode="function", name="check", time_limit=TL),
    ])

# ====================================================================== Day 65
hist_cases = [(([1, 2, 2, 3, 3, 3, 4, 4, 5, 10], 3), "t1", "구간 3개"), (([0, 1], 2), "h1", ""), ((list(range(20)), 4), "h2", "")]
day65 = L(
    65, "막대·히스토그램·산점도", W, ["plot_types", "matplotlib"],
    ["범주 비교는 막대, 분포는 히스토그램, 관계는 산점도로 그릴 수 있다.", "목적에 맞는 그래프 종류를 고를 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `ax.plot`으로 선 그래프를 그렸습니다. 선 그래프는 **시간에 따른 변화**를 보기 좋습니다.",
            "quiz": [quiz("d65_review_q1", "그래프에 범례를 표시하는 메서드는?", ["`ax.title()`", "`ax.legend()`", "`ax.label()`", "`plt.show()`"], 1, "")]},
    concept={"title": "목적에 맞는 그래프", "blocks": [
        text("**막대**(`bar`)는 범주끼리 크기를 비교하고, **히스토그램**(`hist`)은 값이 어느 구간에 몰려 있는지(분포), **산점도**(`scatter`)는 두 값의 관계를 봅니다."),
        C('''
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
            axes[0].bar(["A", "B", "C"], [30, 45, 25], color="tab:blue")
            axes[0].set_title("막대: 반별 인원")
            counts, edges, _ = axes[1].hist([1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5)
            axes[1].set_title("히스토그램: 분포")
            axes[2].scatter([1, 2, 3, 4, 5], [2, 4, 5, 4, 6])
            axes[2].set_title("산점도: 관계")
            print(counts.tolist())
        '''),
        tip("막대 그래프의 막대들은 `ax.patches`에 들어 있고 `get_height()`로 높이를 읽을 수 있습니다. 채점은 이렇게 그린 결과를 꺼내 확인합니다."),
        tip(SHOW_TIP),
    ]},
    fill_intro="막대 그래프를 그리세요.",
    coding_intro="히스토그램을 그리고 구간별 개수를 돌려주세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`ax.bar(범주, 값)`: 비교.",
        "`ax.hist(값, bins=n)`: 분포, 반환값의 첫째가 구간별 개수.",
        "`ax.scatter(x, y)`: 두 변수의 관계.",
        "`plt.subplots(1, 3)`으로 여러 그래프를 나란히."],
        "quiz": [
            quiz("d65_summary_q1", "학생 키의 분포를 보기에 알맞은 그래프는?", ["선", "막대", "히스토그램", "산점도"], 2, ""),
            quiz("d65_summary_q2", "공부 시간과 점수의 관계를 보기에 알맞은 그래프는?", ["파이", "히스토그램", "산점도", "막대"], 2, "")]},
    exercises=[
        ex("d65_fill_1", "fill_blank", "막대 그래프",
           "범주와 값으로 막대 그래프를 그리세요.",
           ["plot_types"], 1,
           '''
            import matplotlib.pyplot as plt


            def draw_bars(ax, labels, values):
                ax.____(labels, ____)


            def check(labels, values):
                fig, ax = plt.subplots()
                draw_bars(ax, labels, values)
                return [p.get_height() for p in ax.patches]
           ''',
           [t("t1", args=[["A", "B"], [3, 5]], ret=[3, 5], desc="기본"), t("h1", args=[["x", "y", "z"], [0, 2.5, 1]], ret=[0, 2.5, 1])],
           ["막대 그래프를 그리는 Axes 메서드입니다.", "막대 높이로 쓸 매개변수입니다."],
           '''
            import matplotlib.pyplot as plt


            def draw_bars(ax, labels, values):
                ax.bar(labels, values)


            def check(labels, values):
                fig, ax = plt.subplots()
                draw_bars(ax, labels, values)
                return [p.get_height() for p in ax.patches]
           ''', mode="function", name="check", time_limit=TL),
        ex("d65_code_1", "coding", "점수 분포",
           "`draw_hist(ax, values, bins)`를 작성하세요. 히스토그램을 그리고, 제목 `\"점수 분포\"`를 붙인 뒤 **구간별 개수를 정수 리스트로 반환**합니다. `check`는 채점용입니다.",
           ["plot_types", "matplotlib"], 2,
           '''
            import matplotlib.pyplot as plt


            def draw_hist(ax, values, bins):
                # 여기에 코드를 작성하세요
                pass


            def check(values, bins):
                fig, ax = plt.subplots()
                counts = draw_hist(ax, values, bins)
                return [ax.get_title(), counts, len(ax.patches)]
           ''',
           [t(tid, args=list(a), ret=["점수 분포", ref_hist(*a), a[1]], desc=d) for a, tid, d in hist_cases],
           ["`ax.hist(values, bins=bins)`는 (개수 배열, 구간 경계, 막대들) 세 값을 돌려줍니다.", "개수 배열을 `int`로 바꾼 리스트로 반환하세요."],
           '''
            import matplotlib.pyplot as plt


            def draw_hist(ax, values, bins):
                counts, edges, bars = ax.hist(values, bins=bins, edgecolor="white")
                ax.set_title("점수 분포")
                return [int(c) for c in counts]


            def check(values, bins):
                fig, ax = plt.subplots()
                counts = draw_hist(ax, values, bins)
                return [ax.get_title(), counts, len(ax.patches)]
           ''', mode="function", name="check", time_limit=TL),
    ])

# ====================================================================== Day 66
day66 = L(
    66, "pandas 그래프와 여러 그래프", W, ["matplotlib", "pandas_groupby", "plot_types"],
    ["pandas의 plot으로 표에서 바로 그래프를 그릴 수 있다.", "subplots로 여러 그래프를 한 그림에 배치할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 막대·히스토그램·산점도를 목적에 맞게 골랐습니다.",
            "quiz": [quiz("d66_review_q1", "`ax.hist`가 돌려주는 첫 번째 값은?", ["구간 경계", "구간별 개수", "막대 객체", "평균"], 1, "")]},
    concept={"title": "표에서 바로 그리기", "blocks": [
        text("pandas의 Series·DataFrame은 `.plot(kind=종류, ax=축)`으로 바로 그릴 수 있습니다. 인덱스가 x축, 값이 y축이 됩니다. groupby 결과를 그대로 그리면 편합니다."),
        C('''
            import matplotlib.pyplot as plt
            import pandas as pd

            df = pd.DataFrame({"분류": ["문구", "식품", "문구", "식품"], "매출": [3000, 4000, 2000, 2500]})
            totals = df.groupby("분류")["매출"].sum()
            fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
            totals.plot(kind="bar", ax=axes[0], title="분류별 매출")
            df["매출"].cumsum().plot(ax=axes[1], marker="o", title="누적 매출")
            fig.tight_layout()
            print(totals.to_dict())
        '''),
        tip("`plt.subplots(행, 열)`의 `axes`는 배열입니다. 1행 2열이면 `axes[0]`, `axes[1]`, 2행 2열이면 `axes[0, 1]`처럼 씁니다. `fig.tight_layout()`은 제목이 겹치지 않게 간격을 맞춥니다."),
        tip(SHOW_TIP),
    ]},
    fill_intro="1행 2열 그래프 판을 만드세요.",
    coding_intro="두 그래프로 이루어진 작은 대시보드를 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`series.plot(kind=\"bar\", ax=ax)`처럼 pandas에서 바로 그리기.",
        "`plt.subplots(행, 열)` → `axes` 배열.",
        "`fig.tight_layout()`으로 간격 정리.",
        "groupby 결과는 바로 그래프로 그리기 좋다."],
        "quiz": [
            quiz("d66_summary_q1", "2행 2열 subplots에서 오른쪽 위 그래프는?", ["`axes[0, 1]`", "`axes[1, 0]`", "`axes[1]`", "`axes[2]`"], 0, ""),
            quiz("d66_summary_q2", "Series를 막대 그래프로 그리는 코드는?", ["`s.bar()`", "`s.plot(kind=\"bar\")`", "`plt.series(s)`", "`s.hist(kind=\"bar\")`"], 1, "")]},
    exercises=[
        ex("d66_fill_1", "fill_blank", "그래프 판 나누기",
           "1행 `n`열짜리 그래프 판을 만들어 Axes 개수와 그림 크기 정보를 반환하세요.",
           ["matplotlib"], 1,
           '''
            import matplotlib.pyplot as plt


            def make_panels(n):
                fig, axes = plt.____(1, ____)
                return len(axes)
           ''',
           [t("t1", args=[2], ret=2, desc="2개"), t("h1", args=[3], ret=3)],
           ["그림판과 Axes를 함께 만드는 함수입니다.", "열 개수로 쓸 매개변수입니다."],
           '''
            import matplotlib.pyplot as plt


            def make_panels(n):
                fig, axes = plt.subplots(1, n)
                return len(axes)
           ''', mode="function", name="make_panels", time_limit=TL),
        ex("d66_code_1", "coding", "매출 대시보드",
           "`dashboard(data)`를 작성하세요(`data`: 분류·매출 열). 1행 2열 그래프를 만들어\n\n"
           "- 왼쪽: 분류별 매출 합계 막대 그래프, 제목 `\"분류별 매출\"`\n- 오른쪽: 매출 누적 합 선 그래프, 제목 `\"누적 매출\"`\n\n"
           "`fig, axes`를 반환하세요. `check`는 채점용입니다.",
           ["matplotlib", "pandas_groupby", "plot_types"], 2,
           '''
            import matplotlib.pyplot as plt
            import pandas as pd


            def dashboard(data):
                # 여기에 코드를 작성하세요
                pass


            def check(data):
                fig, axes = dashboard(data)
                left, right = axes[0], axes[1]
                return [left.get_title(), [p.get_height() for p in left.patches],
                        right.get_title(), right.lines[0].get_ydata().tolist()]
           ''',
           [t("t1", args=[{"분류": ["문구", "식품", "문구"], "매출": [3000, 4000, 2000]}],
              ret=["분류별 매출", [5000, 4000], "누적 매출", [3000, 7000, 9000]], desc="기본"),
            t("h1", args=[{"분류": ["b", "a"], "매출": [1, 2]}], ret=["분류별 매출", [2, 1], "누적 매출", [1, 3]])],
           ["`df.groupby(\"분류\")[\"매출\"].sum()`을 `.plot(kind=\"bar\", ax=axes[0])`으로 그리세요(분류 이름 순으로 정렬됩니다).",
            "누적 합은 `df[\"매출\"].cumsum()`, 오른쪽 Axes에 선으로 그립니다.", "제목은 `ax.set_title`이나 `plot(title=...)`으로 붙입니다."],
           '''
            import matplotlib.pyplot as plt
            import pandas as pd


            def dashboard(data):
                df = pd.DataFrame(data)
                fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
                df.groupby("분류")["매출"].sum().plot(kind="bar", ax=axes[0])
                axes[0].set_title("분류별 매출")
                df["매출"].cumsum().plot(ax=axes[1], marker="o")
                axes[1].set_title("누적 매출")
                fig.tight_layout()
                return fig, axes


            def check(data):
                fig, axes = dashboard(data)
                left, right = axes[0], axes[1]
                return [left.get_title(), [p.get_height() for p in left.patches],
                        right.get_title(), right.lines[0].get_ydata().tolist()]
           ''', mode="function", name="check", time_limit=TL),
    ])

# ====================================================================== Day 67
PROF = {"이름": ["민준", "서연", "지호", "하나"], "반": ["A", "B", "A", "A"], "키": [172.5, 160.0, 181.0, 158.5], "점수": [85, 92, 78, 66]}
day67 = L(
    67, "EDA 1: 데이터 살펴보기", W, ["eda", "pandas_basics", "pandas_groupby"],
    ["describe, value_counts, nunique로 데이터를 빠르게 요약할 수 있다.", "숫자 열과 범주 열을 구분해 살펴볼 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 pandas에서 바로 그래프를 그리고 여러 그래프를 배치했습니다.",
            "quiz": [quiz("d67_review_q1", "제목이 겹치지 않게 간격을 맞추는 코드는?", ["`fig.tight_layout()`", "`ax.grid()`", "`plt.legend()`", "`ax.set_title()`"], 0, "")]},
    concept={"title": "처음 보는 데이터와 친해지기", "blocks": [
        text("**탐색적 데이터 분석**(EDA)은 모델을 만들기 전에 데이터를 이리저리 살펴보는 단계입니다. 먼저 크기·열·자료형을 보고, 숫자 열은 `describe()`, 범주 열은 `value_counts()`로 요약합니다."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"반": ["A", "B", "A", "A"], "키": [172.5, 160.0, 181.0, 158.5], "점수": [85, 92, 78, 66]})
            print(df.describe().round(1))
            print(df["반"].value_counts())
            print(df["반"].nunique())
            print(df.select_dtypes("number").columns.tolist())
        '''),
        tip("`describe()`의 `25%`, `50%`, `75%`는 사분위수입니다. `50%`가 중앙값이에요. 평균과 중앙값이 많이 다르면 한쪽으로 치우친 데이터일 수 있습니다."),
    ]},
    fill_intro="범주 열의 값별 개수를 딕셔너리로 반환하세요.",
    coding_intro="데이터 프로필(요약 보고서)을 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "EDA = 모델링 전에 데이터 살펴보기.",
        "숫자 열: `describe()`(개수·평균·표준편차·사분위수).",
        "범주 열: `value_counts()`, `nunique()`.",
        "`select_dtypes(\"number\")`로 숫자 열만 고르기."],
        "quiz": [
            quiz("d67_summary_q1", "`describe()`의 `50%` 값은?", ["평균", "중앙값", "최댓값의 절반", "표준편차"], 1, ""),
            quiz("d67_summary_q2", "범주 열에서 값별 개수를 세는 메서드는?", ["`count()`", "`value_counts()`", "`describe()`", "`size`"], 1, "")]},
    exercises=[
        ex("d67_fill_1", "fill_blank", "값별 개수",
           "`반` 열의 값별 개수를 딕셔너리로 반환하세요.",
           ["eda"], 1,
           '''
            import pandas as pd


            def class_counts(data):
                df = pd.DataFrame(data)
                return df["반"].____().____()
           ''',
           [t("t1", args=[PROF], ret={"A": 3, "B": 1}, desc="기본"), t("h1", args=[{"반": ["X"]}], ret={"X": 1})],
           ["값별 개수를 세는 Series 메서드입니다.", "Series를 딕셔너리로 바꾸는 메서드입니다."],
           '''
            import pandas as pd


            def class_counts(data):
                df = pd.DataFrame(data)
                return df["반"].value_counts().to_dict()
           ''', mode="function", name="class_counts", time_limit=TL),
        ex("d67_code_1", "coding", "데이터 프로필",
           "데이터를 받아 다음을 담은 딕셔너리를 반환하세요.\n\n"
           "- `rows`: 행 수\n- `numeric`: 숫자 열마다 `{\"mean\": 평균(소수 둘째 자리), \"min\": 최솟값, \"max\": 최댓값}` (값은 float)\n"
           "- `top`: 숫자가 아닌 열마다 가장 많이 나온 값",
           ["eda", "pandas_basics"], 2,
           '''
            import pandas as pd


            def profile(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[PROF], ret=ref_profile(PROF), desc="학생 표", compare={"mode": "float", "tol": 1e-9}),
            t("h1", args=[{"x": [1, 3], "y": ["a", "a"]}], ret=ref_profile({"x": [1, 3], "y": ["a", "a"]}), compare={"mode": "float", "tol": 1e-9})],
           ["숫자 열은 `df.select_dtypes(\"number\").columns`, 그 밖은 `select_dtypes(exclude=\"number\")`.",
            "가장 많이 나온 값은 `value_counts().index[0]`입니다.", "숫자는 `float()`로 바꿔 넣으세요."],
           '''
            import pandas as pd


            def profile(data):
                df = pd.DataFrame(data)
                numeric = {}
                for col in df.select_dtypes("number").columns:
                    numeric[col] = {
                        "mean": round(float(df[col].mean()), 2),
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                    }
                top = {}
                for col in df.select_dtypes(exclude="number").columns:
                    top[col] = df[col].value_counts().index[0]
                return {"rows": len(df), "numeric": numeric, "top": top}
           ''', mode="function", name="profile", time_limit=TL),
    ])

# ====================================================================== Day 68
iqr_cases = [([10, 12, 11, 13, 12, 50, 11, -20], "t1", "양쪽 이상치"), ([1, 2, 3, 4], "h1", ""), ([5, 5, 5, 5, 6, 100], "h2", "")]
day68 = L(
    68, "EDA 2: 상관관계와 이상치", W, ["eda", "plot_types", "pandas_select"],
    ["상관계수로 두 변수의 관계 방향과 세기를 읽을 수 있다.", "IQR 규칙으로 이상치를 찾을 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `describe`, `value_counts`로 데이터를 요약했습니다.",
            "quiz": [quiz("d68_review_q1", "`describe()`의 `25%`와 `75%`는?", ["최솟값·최댓값", "1사분위수·3사분위수", "평균±표준편차", "결측치 비율"], 1, "")]},
    concept={"title": "관계와 튀는 값 찾기", "blocks": [
        text("**상관계수**(`corr`)는 -1~1 사이 값으로, 1에 가까우면 함께 증가, -1에 가까우면 반대로 움직이고, 0 근처면 직선 관계가 거의 없다는 뜻입니다. 산점도와 함께 보세요."),
        C('''
            import pandas as pd

            df = pd.DataFrame({"공부시간": [1, 2, 3, 4, 5], "점수": [55, 62, 70, 74, 85], "결석": [5, 4, 4, 2, 1]})
            print(df.corr().round(2))
            print(round(df["공부시간"].corr(df["점수"]), 3))
        '''),
        text("**IQR 규칙**: 3사분위수 − 1사분위수를 IQR이라 할 때, `Q1 − 1.5×IQR`보다 작거나 `Q3 + 1.5×IQR`보다 큰 값을 이상치로 봅니다(상자 그림의 점들)."),
        C('''
            import pandas as pd

            s = pd.Series([10, 12, 11, 13, 12, 50, 11])
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            print(q1, q3, iqr)
            print(s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)].tolist())
        '''),
        tip("상관관계는 인과관계가 아닙니다. 아이스크림 판매량과 물놀이 사고는 함께 늘지만, 둘 다 \"더위\"라는 공통 원인 때문이에요."),
    ]},
    fill_intro="두 열의 상관계수를 구하세요.",
    coding_intro="IQR 규칙으로 이상치를 찾으세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`df.corr()`, `s1.corr(s2)`: -1~1, 부호는 방향, 크기는 세기.",
        "상관관계 ≠ 인과관계.",
        "IQR = Q3 − Q1, 범위 밖(1.5배)은 이상치.",
        "이상치는 오류일 수도, 중요한 사건일 수도 있다."],
        "quiz": [
            quiz("d68_summary_q1", "상관계수 -0.9의 의미는?", ["관계 없음", "강한 양의 관계", "강한 음의 관계", "약한 관계"], 2, ""),
            quiz("d68_summary_q2", "Q1=10, Q3=20일 때 이상치 상한은?", ["25", "30", "35", "40"], 2, "IQR=10, 20 + 1.5×10 = 35")]},
    exercises=[
        ex("d68_fill_1", "fill_blank", "상관계수",
           "두 열 `x`, `y`의 상관계수를 소수 셋째 자리까지 반올림해 반환하세요.",
           ["eda"], 1,
           '''
            import pandas as pd


            def correlation(data):
                df = pd.DataFrame(data)
                return round(df["x"].____(df["____"]), 3)
           ''',
           [t("t1", args=[{"x": [1, 2, 3], "y": [2, 4, 6]}], ret=1.0, desc="완전한 양의 관계"),
            t("h1", args=[{"x": [1, 2, 3, 4], "y": [4, 3, 3, 1]}], ret=round(pd.Series([1, 2, 3, 4]).corr(pd.Series([4, 3, 3, 1])), 3), compare={"mode": "float", "tol": 1e-9})],
           ["상관계수를 구하는 Series 메서드입니다.", "비교할 다른 열 이름입니다."],
           '''
            import pandas as pd


            def correlation(data):
                df = pd.DataFrame(data)
                return round(df["x"].corr(df["y"]), 3)
           ''', mode="function", name="correlation", time_limit=TL),
        ex("d68_code_1", "coding", "이상치 찾기",
           "값 목록에서 IQR 규칙(1.5배)으로 판단한 이상치를 **오름차순 리스트**로 반환하세요. 사분위수는 `pd.Series(...).quantile()`의 기본 방식으로 계산합니다.",
           ["eda", "pandas_select"], 2,
           '''
            import pandas as pd


            def outliers(values):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[v], ret=ref_iqr(v), desc=d, compare={"mode": "float", "tol": 1e-9}) for v, tid, d in iqr_cases],
           ["값을 실수형 Series로 만든 뒤 `quantile(0.25)`, `quantile(0.75)`를 구하세요.",
            "하한·상한을 계산해 마스크 `(s < 하한) | (s > 상한)`으로 거릅니다.", "`sorted(...tolist())`로 정렬해 반환합니다."],
           '''
            import pandas as pd


            def outliers(values):
                s = pd.Series(values, dtype=float)
                q1, q3 = s.quantile(0.25), s.quantile(0.75)
                iqr = q3 - q1
                low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                return sorted(s[(s < low) | (s > high)].tolist())
           ''', mode="function", name="outliers", time_limit=TL),
    ])

# ====================================================================== Day 69 (mini project)
day69 = L(
    69, "미니 프로젝트: 판매 데이터 분석", W, ["eda", "pandas_groupby", "matplotlib", "pandas_transform"],
    ["질문을 세우고 pandas로 답을 구한 뒤 그래프로 보여 줄 수 있다."],
    review={"title": "프로젝트 준비", "content_md": (
        "오늘은 작은 판매 데이터로 **분석 보고서**를 만듭니다. 질문은 세 가지입니다.\n\n"
        "1. 월별 매출은 얼마인가?\n2. 가장 많이 팔린 상품은?\n3. 매출은 지난달보다 몇 % 늘었나(증감률)?"),
        "quiz": [quiz("d69_review_q1", "월별 매출 합계를 구하는 코드는?", ["`df[\"월\"].sum()`", "`df.groupby(\"월\")[\"매출\"].sum()`", "`df.sum(\"매출\")`", "`df.pivot()`"], 1, "")]},
    concept={"title": "증감률과 보고 그래프", "blocks": [
        text("`pct_change()`는 바로 앞 값 대비 변화율을 계산합니다(첫 값은 비교 대상이 없어 NaN). ×100 하면 %입니다."),
        C('''
            import pandas as pd

            monthly = pd.Series([9000, 27000, 20000], index=[1, 2, 3])
            print((monthly.pct_change() * 100).round(1).tolist())
        '''),
        C('''
            import matplotlib.pyplot as plt
            import pandas as pd

            df = pd.DataFrame({"월": [1, 1, 2, 2, 3], "매출": [3000, 6000, 4000, 23000, 20000]})
            monthly = df.groupby("월")["매출"].sum()
            fig, ax = plt.subplots()
            monthly.plot(kind="bar", ax=ax, title="월별 매출", rot=0)
            for i, v in enumerate(monthly):
                ax.text(i, v, f"{v:,}", ha="center", va="bottom")
            print(monthly.tolist())
        '''),
        tip("보고서 그래프에는 값을 직접 적어 주면(`ax.text`) 읽는 사람이 축 눈금을 따라가지 않아도 됩니다."),
    ]},
    fill_intro="월별 매출 합계 리스트를 반환하세요.",
    coding_intro="세 질문에 답하는 분석 함수를 완성하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "분석은 질문 → 집계 → 시각화 순서.",
        "`pct_change()`로 증감률.",
        "그래프에 값 표시(`ax.text`)로 읽기 쉽게.",
        "다음 시간: 2단계 마무리 복습."],
        "quiz": [
            quiz("d69_summary_q1", "1월 100 → 2월 150일 때 증감률은?", ["50%", "150%", "-33%", "1.5%"], 0, ""),
            quiz("d69_summary_q2", "`pct_change()` 결과의 첫 값은?", ["0", "NaN", "100", "첫 값 그대로"], 1, "")]},
    exercises=[
        ex("d69_fill_1", "fill_blank", "월별 매출",
           "월·매출 열이 있는 데이터에서 월 순서대로의 매출 합계 리스트를 반환하세요.",
           ["pandas_groupby"], 1,
           '''
            import pandas as pd


            def monthly_totals(data):
                df = pd.DataFrame(data)
                return df.groupby("____")["매출"].____().tolist()
           ''',
           [t("t1", args=[SALES], ret=[9000, 27000, 20000], desc="기본"), t("h1", args=[{"월": [2, 1], "매출": [5, 7]}], ret=[7, 5])],
           ["묶을 기준 열입니다.", "합계를 구하는 메서드입니다."],
           '''
            import pandas as pd


            def monthly_totals(data):
                df = pd.DataFrame(data)
                return df.groupby("월")["매출"].sum().tolist()
           ''', mode="function", name="monthly_totals", time_limit=TL),
        ex("d69_code_1", "coding", "판매 분석 보고",
           "월·상품·매출 데이터를 분석해 딕셔너리를 반환하세요.\n\n"
           "- `monthly`: 월 순서대로 매출 합계(정수 리스트)\n- `best`: 매출 합계가 가장 큰 상품\n"
           "- `growth`: 두 번째 달부터 전월 대비 증감률(%) 리스트(소수 첫째 자리 반올림)\n\n선택: 월별 매출 막대 그래프도 그려 보세요(채점에는 영향 없음).",
           ["eda", "pandas_groupby", "pandas_transform"], 2,
           '''
            import pandas as pd


            def analyze_sales(data):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[SALES], ret=ref_monthly(SALES), desc="기본", compare={"mode": "float", "tol": 1e-9}),
            t("h1", args=[{"월": [1, 2, 3], "상품": ["a", "b", "a"], "매출": [100, 50, 100]}],
              ret=ref_monthly({"월": [1, 2, 3], "상품": ["a", "b", "a"], "매출": [100, 50, 100]}), compare={"mode": "float", "tol": 1e-9})],
           ["월별 합계는 `groupby(\"월\")`, 상품별 합계는 `groupby(\"상품\")` 후 정렬하거나 `idxmax()`.",
            "증감률은 월별 합계에 `pct_change() * 100`을 하고 `dropna()`로 첫 NaN을 빼세요.", "숫자들은 `int()`, `round(float(x), 1)`로 정리합니다."],
           '''
            import pandas as pd


            def analyze_sales(data):
                df = pd.DataFrame(data)
                monthly = df.groupby("월")["매출"].sum()
                best = df.groupby("상품")["매출"].sum().idxmax()
                growth = (monthly.pct_change() * 100).dropna()
                return {"monthly": [int(v) for v in monthly], "best": best,
                        "growth": [round(float(g), 1) for g in growth]}
           ''', mode="function", name="analyze_sales", time_limit=TL),
    ])

# ====================================================================== Day 70 (stage 2 review)
mv_cases = [(([1, 2, 3, 4, 5], 3), "t1", "창 크기 3"), (([10, 20], 2), "h1", ""), (([5, 1, 5, 1, 5, 1], 2), "h2", "")]
day70 = L(
    70, "2단계 마무리 누적 복습", W, ["class", "comprehension", "numpy_ops", "pandas_groupby", "matplotlib", "eda"],
    ["객체지향·파이썬다운 문법·NumPy·pandas·시각화를 조합해 작은 분석 도구를 만들 수 있다."],
    review={"title": "2단계 5주 돌아보기", "content_md": (
        "| 주차 | 주제 | 핵심 |\n|---|---|---|\n"
        "| 6 | 객체지향 | 클래스, 메서드, 특수 메서드, 상속, property, dataclass |\n"
        "| 7 | 파이썬다운 코드 | 컴프리헨션, 이터레이터·제너레이터, 클로저, 데코레이터 |\n"
        "| 8 | NumPy | 배열, 벡터화·브로드캐스팅, 마스크, axis, `@`, 난수 |\n"
        "| 9 | pandas | 선택·변환·결측치·groupby·merge |\n"
        "| 10 | 시각화·EDA | 선·막대·히스토그램·산점도, describe, 상관·이상치 |\n\n"
        "다음 3단계부터는 이 도구들로 **머신러닝 모델**을 만듭니다."),
        "quiz": [
            quiz("d70_review_q1", "머신러닝 전에 데이터의 분포·결측치·이상치를 살피는 단계는?", ["배포", "EDA", "학습", "평가"], 1, ""),
            quiz("d70_review_q2", "pandas가 내부적으로 데이터를 저장하는 데 쓰는 라이브러리는?", ["matplotlib", "NumPy", "json", "csv"], 1, "")]},
    concept={"title": "클래스로 분석 도구 묶기", "blocks": [
        text("자주 하는 분석을 클래스로 묶으면 재사용하기 쉽습니다. 데이터는 속성으로, 분석 단계는 메서드로 둡니다."),
        C('''
            import pandas as pd

            class Report:
                def __init__(self, data):
                    self.df = pd.DataFrame(data)

                def total(self, col):
                    return int(self.df[col].sum())

                def top(self, by, col):
                    return self.df.groupby(by)[col].sum().idxmax()

            r = Report({"상품": ["펜", "노트", "펜"], "매출": [3000, 6000, 4000]})
            print(r.total("매출"), r.top("상품", "매출"))
        '''),
        tip("**이동 평균**(도전 문제)은 최근 몇 개 값의 평균으로, 들쭉날쭉한 시계열의 흐름을 부드럽게 보여 줍니다. pandas의 `rolling(창 크기).mean()`이 계산해 줍니다."),
    ]},
    fill_intro="리스트 컴프리헨션과 NumPy를 함께 써 보세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "2단계 마무리", "points": [
        "클래스로 데이터와 분석 동작을 묶는다.",
        "NumPy로 계산, pandas로 표 처리, matplotlib으로 보여 준다.",
        "EDA로 데이터를 이해한 뒤 모델링한다.",
        "다음: 3단계 머신러닝(scikit-learn)."],
        "quiz": [
            quiz("d70_summary_q1", "`s.rolling(3).mean()`의 처음 두 값은?", ["0", "NaN", "첫 값", "평균"], 1, "창이 다 차지 않으면 NaN입니다."),
            quiz("d70_summary_q2", "3단계에서 주로 쓸 머신러닝 라이브러리는?", ["pandas", "scikit-learn", "matplotlib", "json"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d70_fill_1", "fill_blank", "제곱 평균",
           "숫자 목록에서 짝수만 골라 제곱한 값들의 평균을 반환하세요(짝수가 하나 이상 있다고 가정).",
           ["comprehension", "numpy_aggregate"], 1,
           '''
            import numpy as np


            def even_square_mean(values):
                squares = [x * x for x in values ____ x % 2 == 0]
                return float(np.____(squares))
           ''',
           [t("t1", args=[[1, 2, 3, 4]], ret=10.0, desc="2, 4"), t("h1", args=[[0]], ret=0.0)],
           ["컴프리헨션에서 조건을 붙이는 키워드입니다.", "평균을 구하는 NumPy 함수입니다."],
           '''
            import numpy as np


            def even_square_mean(values):
                squares = [x * x for x in values if x % 2 == 0]
                return float(np.mean(squares))
           ''', mode="function", name="even_square_mean", time_limit=TL),
        ex("d70_code_1", "coding", "판매 리포트 클래스",
           "`SalesReport` 클래스를 작성하세요.\n\n"
           "- `__init__(self, data)`: 상품·분류·가격·수량 데이터로 DataFrame을 만들고 `매출 = 가격 × 수량` 열을 추가\n"
           "- `total()`: 전체 매출(int)\n- `by(col)`: 기준 열별 매출 합계를 큰 순으로 `{값: 매출}` 딕셔너리\n"
           "- `__len__`: 행 수\n\n`check`는 채점용입니다.",
           ["class", "dunder", "pandas_groupby"], 2,
           '''
            import pandas as pd

            # 여기에 SalesReport 클래스를 작성하세요


            def check(data):
                r = SalesReport(data)
                return [len(r), r.total(), r.by("분류"), r.by("상품")]
           ''',
           [t("t1", args=[{"상품": ["펜", "노트", "물"], "분류": ["문구", "문구", "식품"], "가격": [1000, 3000, 800], "수량": [3, 1, 5]}],
              ret=[3, 10000, {"문구": 6000, "식품": 4000}, {"펜": 3000, "노트": 3000, "물": 4000}], desc="기본"),
            t("h1", args=[{"상품": ["a"], "분류": ["x"], "가격": [2], "수량": [2]}], ret=[1, 4, {"x": 4}, {"a": 4}])],
           ["`__init__`에서 데이터를 DataFrame으로 바꿔 속성에 저장한 뒤 매출 열을 추가하세요.",
            "`by`는 `groupby(col)[\"매출\"].sum().sort_values(ascending=False)`를 `{k: int(v)}`로 바꿉니다.",
            "`__len__`은 `len(self.df)`."],
           '''
            import pandas as pd


            class SalesReport:
                def __init__(self, data):
                    self.df = pd.DataFrame(data)
                    self.df["매출"] = self.df["가격"] * self.df["수량"]

                def total(self):
                    return int(self.df["매출"].sum())

                def by(self, col):
                    sums = self.df.groupby(col)["매출"].sum().sort_values(ascending=False)
                    return {key: int(value) for key, value in sums.items()}

                def __len__(self):
                    return len(self.df)


            def check(data):
                r = SalesReport(data)
                return [len(r), r.total(), r.by("분류"), r.by("상품")]
           ''', mode="function", name="check", checks={"required_syntax": ["class"]}, time_limit=TL),
        ex("d70_code_2", "coding", "[도전] 이동 평균",
           "값 목록과 창 크기 `window`를 받아 이동 평균을 계산하세요. 창이 다 차지 않은 앞부분은 빼고, 소수 둘째 자리까지 반올림한 리스트를 반환합니다.\n\n"
           "예: `moving_average([1, 2, 3, 4, 5], 3)` → `[2.0, 3.0, 4.0]`",
           ["numpy_aggregate", "pandas_transform"], 2,
           '''
            import pandas as pd


            def moving_average(values, window):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_moving(*a), desc=d, compare={"mode": "float", "tol": 1e-9}) for a, tid, d in mv_cases],
           ["`pd.Series(values, dtype=float).rolling(window).mean()`.", "앞쪽 NaN은 `dropna()`로 지우고, 값마다 `round(float(x), 2)`."],
           '''
            import pandas as pd


            def moving_average(values, window):
                averages = pd.Series(values, dtype=float).rolling(window).mean().dropna()
                return [round(float(x), 2) for x in averages]
           ''', mode="function", name="moving_average", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day64, day65, day66, day67, day68, day69, day70])
