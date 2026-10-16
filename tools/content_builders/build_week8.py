"""Week 8 (Day 50-56): NumPy. Expected values come from numpy reference code in this builder."""
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from textwrap import dedent

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import code, ex, lesson, lines, quiz, t, text, tip, write_lessons  # noqa: E402

W, ST = 8, "advanced_data"
TL = 10


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def run_block(src):
    """Expected output of a concept example = what numpy prints for it (deterministic on this machine)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        exec(dedent(src).lstrip("\n"), {})
    return buf.getvalue()


def ncode(src):
    return code(src, run_block(src))


# ---------------------------------------------------------------- references
def ref_describe(v):
    a = np.array(v)
    return [a.ndim, list(a.shape), int(a.size), str(a.dtype)]


def ref_bmi(h, w):
    return np.round(np.array(w) / (np.array(h) / 100) ** 2, 1).tolist()


def ref_clip(v, lo, hi):
    return np.clip(np.array(v), lo, hi).tolist()


def ref_best(scores, names):
    a = np.array(scores)
    return [names[int(a.sum(axis=1).argmax())], a.max(axis=0).tolist()]


def ref_linear(X, Wm, b):
    return np.round(np.array(X) @ np.array(Wm) + np.array(b), 3).tolist()


def ref_pi(n, seed):
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2))
    inside = ((pts ** 2).sum(axis=1) <= 1).sum()
    return round(4 * inside / n, 4)


def ref_report(scores):
    a = np.array(scores, dtype=float)
    z = (a - a.mean()) / a.std()
    return {"mean": round(float(a.mean()), 2), "std": round(float(a.std()), 2),
            "above": int((a > a.mean()).sum()), "z_max": round(float(z.max()), 2)}


def ref_dice(n, seed):
    rng = np.random.default_rng(seed)
    rolls = rng.integers(1, 7, size=n)
    counts = np.bincount(rolls, minlength=7)[1:]
    return [int(c) for c in counts]


# ====================================================================== Day 50
desc_cases = [([1, 2, 3], "t1", "1차원 정수"), ([[1.5, 2], [3, 4]], "t2", "2차원 실수"), ([[[1]]], "h1", ""), ([], "h2", "")]
day50 = L(
    50, "NumPy 배열 만들기", W, ["numpy_array", "module"],
    ["NumPy 배열(ndarray)을 만들고 shape, ndim, dtype을 확인할 수 있다.", "arange, linspace, zeros, ones로 배열을 생성할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "7주차까지 파이썬 문법을 다졌습니다. 이번 주부터 **데이터 분석 도구**를 배웁니다. 첫 번째는 숫자 계산의 기본 도구 **NumPy**입니다. "
        "리스트보다 훨씬 빠르고, 이후의 pandas·scikit-learn·PyTorch가 모두 NumPy 방식을 따릅니다."),
        "quiz": [quiz("d50_review_q1", "`[x * 2 for x in [1, 2, 3]]`의 결과는?", ["`[2, 4, 6]`", "`[1, 2, 3, 1, 2, 3]`", "`6`", "오류"], 0,
                      "NumPy에서는 이것을 `배열 * 2` 한 번으로 씁니다.")]},
    concept={"title": "숫자 데이터를 담는 배열", "blocks": [
        text("관례적으로 `import numpy as np`로 불러옵니다. `np.array(리스트)`로 배열을 만들고, `shape`(모양), `ndim`(차원 수), `size`(원소 수), `dtype`(자료형)을 확인합니다. "
             "배열의 원소는 **모두 같은 자료형**입니다."),
        ncode('''
            import numpy as np

            a = np.array([1, 2, 3])
            print(a)
            print(a.shape, a.ndim, a.dtype)
            b = np.array([[1.5, 2], [3, 4]])
            print(b)
            print(b.shape, b.size, b.dtype)
        '''),
        text("자주 쓰는 생성 함수입니다. `arange`는 `range`처럼, `linspace(시작, 끝, 개수)`는 끝을 포함해 같은 간격으로 나눕니다."),
        ncode('''
            import numpy as np

            print(np.arange(0, 10, 2))
            print(np.linspace(0, 1, 5))
            print(np.zeros((2, 3)))
            print(np.ones(3, dtype=int))
        '''),
        tip("`np.array([1, 2.5])`처럼 정수와 실수가 섞이면 모두 실수(float64)로 바뀝니다. 출력할 때 쉼표가 없고 공백으로 구분되는 것이 리스트와의 차이예요."),
    ]},
    fill_intro="`arange`로 범위 배열을 만드세요.",
    coding_intro="배열의 기본 정보를 꺼내 보세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`import numpy as np`, `np.array(리스트)`.",
        "`shape`(모양 튜플), `ndim`(차원), `size`(개수), `dtype`(자료형).",
        "`np.arange`, `np.linspace`, `np.zeros`, `np.ones`.",
        "배열의 원소는 모두 같은 자료형."],
        "quiz": [
            quiz("d50_summary_q1", "`np.zeros((3, 4)).shape`는?", ["`(4, 3)`", "`(3, 4)`", "`12`", "`3`"], 1, ""),
            quiz("d50_summary_q2", "`np.linspace(0, 10, 3)`의 결과는?", ["`[0, 5, 10]` (실수)", "`[0, 3, 6]`", "`[0, 10]`", "`[3, 6, 9]`"], 0, "끝값 10을 포함해 3개로 나눕니다.")]},
    exercises=[
        ex("d50_fill_1", "fill_blank", "범위 배열",
           "`start`부터 `stop` 직전까지 `step` 간격의 NumPy 배열을 반환하세요.\n\n예: `make_range(0, 10, 3)` → `[0, 3, 6, 9]` (배열은 채점 시 리스트로 비교됩니다)",
           ["numpy_array"], 1,
           '''
            import numpy as ____


            def make_range(start, stop, step):
                return np.____(start, stop, step)
           ''',
           [t("t1", args=[0, 10, 3], ret=[0, 3, 6, 9], desc="기본"), t("h1", args=[5, 5, 1], ret=[]), t("h2", args=[10, 0, -4], ret=[10, 6, 2])],
           ["NumPy를 불러올 때 쓰는 관례적인 별명입니다.", "파이썬 `range`와 비슷한 이름의 NumPy 함수입니다."],
           '''
            import numpy as np


            def make_range(start, stop, step):
                return np.arange(start, stop, step)
           ''', mode="function", name="make_range", time_limit=TL),
        ex("d50_code_1", "coding", "배열 정보",
           "리스트를 배열로 바꿔 `[차원 수, 모양(리스트), 원소 수, 자료형 이름]`을 반환하세요. 자료형 이름은 `str(배열.dtype)`입니다.\n\n"
           "예: `describe([1, 2, 3])` → `[1, [3], 3, \"int64\"]`",
           ["numpy_array"], 1,
           '''
            import numpy as np


            def describe(values):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[v], ret=ref_describe(v), desc=d) for v, tid, d in desc_cases],
           ["`a = np.array(values)`로 만든 뒤 속성들을 읽으세요.", "`shape`는 튜플이므로 `list()`로 바꿉니다."],
           '''
            import numpy as np


            def describe(values):
                a = np.array(values)
                return [a.ndim, list(a.shape), a.size, str(a.dtype)]
           ''', mode="function", name="describe", time_limit=TL),
    ])

# ====================================================================== Day 51
bmi_cases = [(([170, 160], [65, 50]), "t1", "두 명"), (([180], [90]), "h1", ""), (([150, 175, 200], [40, 70, 100]), "h2", "")]
day51 = L(
    51, "배열 연산과 브로드캐스팅", W, ["numpy_ops", "numpy_array"],
    ["반복문 없이 배열 전체에 연산을 적용할 수 있다(벡터화).", "모양이 다른 배열끼리의 브로드캐스팅 규칙을 이해한다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `np.array`, `arange`, `linspace`로 배열을 만들고 `shape`, `dtype`을 확인했습니다.",
            "quiz": [quiz("d51_review_q1", "`np.array([[1, 2, 3]]).shape`는?", ["`(3,)`", "`(1, 3)`", "`(3, 1)`", "`3`"], 1, "")]},
    concept={"title": "반복문 없이 계산하기", "blocks": [
        text("배열끼리의 `+ - * / **`는 **같은 위치의 원소끼리** 계산됩니다. 숫자 하나와 계산하면 모든 원소에 적용됩니다. 이를 **벡터화**라고 하며, for문보다 훨씬 빠릅니다."),
        ncode('''
            import numpy as np

            a = np.array([1, 2, 3, 4])
            b = np.array([10, 20, 30, 40])
            print(a + b)
            print(a * 2)
            print(a ** 2)
            print(a > 2)
            print(np.sqrt(a))
        '''),
        text("**브로드캐스팅**: 모양이 달라도 한쪽 차원이 1이면 늘려서 맞춥니다. (2, 3) 배열에 (3,) 배열을 더하면 각 행에 더해집니다."),
        ncode('''
            import numpy as np

            m = np.array([[1, 2, 3], [4, 5, 6]])
            print(m + np.array([10, 20, 30]))
            col = np.array([1, 2, 3]).reshape(3, 1)
            print(col * np.array([1, 10]))
        '''),
        tip("모양을 맞출 수 없으면 `ValueError: operands could not be broadcast together`가 납니다. 뒤쪽 차원부터 비교해 같거나 1이어야 합니다."),
    ]},
    fill_intro="최소값 0, 최대값 1로 맞추는 정규화를 완성하세요.",
    coding_intro="반복문 없이 배열 연산으로 BMI를 계산하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "배열 연산은 원소별로, 숫자와의 연산은 전체에 적용.",
        "비교 연산의 결과는 불리언 배열.",
        "`np.sqrt`, `np.exp`, `np.round` 등 수학 함수도 원소별.",
        "브로드캐스팅: 뒤쪽 차원부터 같거나 1이면 계산 가능."],
        "quiz": [
            quiz("d51_summary_q1", "`np.array([1, 2]) * np.array([3, 4])`의 결과는?", ["`[3, 8]`", "11", "`[4, 6]`", "오류"], 0, "원소별 곱입니다."),
            quiz("d51_summary_q2", "(4, 3) 배열과 브로드캐스팅되는 것은?", ["(4,)", "(3,)", "(2, 3)", "(3, 4)"], 1, "")]},
    exercises=[
        ex("d51_fill_1", "fill_blank", "최소-최대 정규화",
           "값들을 `(x - 최소) / (최대 - 최소)`로 바꿔 0~1 범위 배열을 반환하세요(값이 2개 이상이고 모두 같지는 않다고 가정).",
           ["numpy_ops"], 1,
           '''
            import numpy as np


            def normalize(values):
                a = np.array(values, dtype=float)
                return (a - a.____()) / (a.max() ____ a.min())
           ''',
           [t("t1", args=[[0, 5, 10]], ret=[0.0, 0.5, 1.0], desc="0~10"),
            t("h1", args=[[3, 1, 2]], ret=[1.0, 0.0, 0.5]), t("h2", args=[[-2, 2]], ret=[0.0, 1.0])],
           ["가장 작은 값을 구하는 배열 메서드입니다.", "범위(최대와 최소의 차이)를 구하는 연산자입니다."],
           '''
            import numpy as np


            def normalize(values):
                a = np.array(values, dtype=float)
                return (a - a.min()) / (a.max() - a.min())
           ''', mode="function", name="normalize", time_limit=TL),
        ex("d51_code_1", "coding", "BMI 한 번에 계산",
           "키(cm) 목록과 몸무게(kg) 목록을 받아 BMI = 몸무게 / (키 m)² 를 **소수 첫째 자리까지 반올림**한 배열로 반환하세요. `for` 문은 쓸 수 없습니다.\n\n"
           "예: `bmi([170, 160], [65, 50])` → `[22.5, 19.5]`",
           ["numpy_ops"], 2,
           '''
            import numpy as np


            def bmi(heights_cm, weights_kg):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_bmi(*a), desc=d) for a, tid, d in bmi_cases],
           ["두 목록을 배열로 바꾸세요. 키는 100으로 나눠 미터로 바꿉니다.", "제곱은 `** 2`, 반올림은 `np.round(배열, 1)`."],
           '''
            import numpy as np


            def bmi(heights_cm, weights_kg):
                h = np.array(heights_cm) / 100
                w = np.array(weights_kg)
                return np.round(w / h ** 2, 1)
           ''', mode="function", name="bmi", checks={"forbidden_syntax": ["for"]}, time_limit=TL),
    ])

# ====================================================================== Day 52
clip_cases = [(([1, 5, 12, -3], 0, 10), "t1", "양쪽 바깥"), (([], 0, 1), "h1", ""), (([2.5, 7], 3, 5), "h2", "")]
day52 = L(
    52, "인덱싱과 불리언 마스크", W, ["numpy_indexing", "numpy_array"],
    ["1·2차원 배열을 인덱싱·슬라이싱할 수 있다.", "조건으로 만든 불리언 마스크로 원소를 고르고 바꿀 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 반복문 없이 배열 전체를 계산했습니다. 비교 연산의 결과는 불리언 배열이었죠.",
            "quiz": [quiz("d52_review_q1", "`np.array([1, 5, 3]) > 2`의 결과는?", ["`[False, True, True]`", "`[5, 3]`", "`True`", "2"], 0, "")]},
    concept={"title": "원하는 원소만 꺼내기", "blocks": [
        text("1차원은 리스트와 같고, 2차원은 `m[행, 열]`처럼 쉼표로 씁니다. `m[:, 0]`은 모든 행의 0번째 열입니다."),
        ncode('''
            import numpy as np

            a = np.arange(10)
            print(a[2], a[-1], a[1:4], a[::-1])
            m = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
            print(m[1, 2])
            print(m[0])
            print(m[:, 0])
            print(m[:2, 1:])
        '''),
        text("**불리언 마스크**: 같은 모양의 True/False 배열로 인덱싱하면 True인 원소만 남습니다. 조건을 묶을 때는 `&`(그리고), `|`(또는)와 괄호를 씁니다. 마스크로 값을 한꺼번에 바꿀 수도 있습니다."),
        ncode('''
            import numpy as np

            a = np.array([3, 8, 1, 9, 5])
            print(a[a > 4])
            print(a[(a > 2) & (a < 9)])
            print(a[[0, 2]])
            a[a > 6] = 0
            print(a)
        '''),
        tip("배열에서는 `and`/`or` 대신 `&`/`|`를 쓰고, 각 조건을 반드시 괄호로 감싸야 합니다. `a > 2 & a < 9`는 연산자 우선순위 때문에 다르게 계산됩니다."),
    ]},
    fill_intro="양수만 골라내는 마스크를 완성하세요.",
    coding_intro="마스크로 범위를 벗어난 값을 경계값으로 바꾸세요(`np.clip` 사용 금지).",
    summary={"title": "오늘의 핵심 정리", "points": [
        "2차원: `m[행, 열]`, `m[:, 0]` 한 열, `m[0]` 한 행.",
        "`a[조건]`으로 거르기, `a[조건] = 값`으로 한꺼번에 바꾸기.",
        "조건 결합은 `&`, `|`와 괄호.",
        "`a[[0, 2]]`처럼 인덱스 목록으로 고를 수도 있다."],
        "quiz": [
            quiz("d52_summary_q1", "`m = np.arange(6).reshape(2, 3)`일 때 `m[1, 0]`은?", ["1", "3", "4", "0"], 1, "`[[0,1,2],[3,4,5]]`의 1행 0열."),
            quiz("d52_summary_q2", "`a[(a > 1) | (a < -1)]`의 뜻은?", ["1보다 크고 -1보다 작은 값", "1보다 크거나 -1보다 작은 값", "-1~1 사이 값", "오류"], 1, "")]},
    exercises=[
        ex("d52_fill_1", "fill_blank", "양수만",
           "값 중 0보다 큰 것만 담은 배열을 반환하세요.",
           ["numpy_indexing"], 1,
           '''
            import numpy as np


            def positives(values):
                a = np.array(values)
                return a[a ____ 0]
           ''',
           [t("t1", args=[[3, -1, 0, 2]], ret=[3, 2], desc="섞인 값"), t("h1", args=[[-5]], ret=[]), t("h2", args=[[0.5, -0.5]], ret=[0.5])],
           ["\"0보다 크다\"를 나타내는 비교 연산자입니다.", "마스크 `a > 0`을 대괄호 안에 넣는 방식입니다."],
           '''
            import numpy as np


            def positives(values):
                a = np.array(values)
                return a[a > 0]
           ''', mode="function", name="positives", time_limit=TL),
        ex("d52_code_1", "coding", "범위 밖 값 자르기",
           "`low`보다 작은 값은 `low`로, `high`보다 큰 값은 `high`로 바꾼 배열을 반환하세요. 불리언 마스크를 사용하고 `np.clip`은 쓸 수 없습니다.\n\n"
           "예: `clip_values([1, 5, 12, -3], 0, 10)` → `[1, 5, 10, 0]`",
           ["numpy_indexing"], 2,
           '''
            import numpy as np


            def clip_values(values, low, high):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_clip(*a), desc=d) for a, tid, d in clip_cases],
           ["원본을 바꾸지 않으려면 `np.array(values)`로 새 배열을 만드세요.", "`a[a < low] = low`처럼 마스크 위치에 값을 넣을 수 있습니다."],
           '''
            import numpy as np


            def clip_values(values, low, high):
                a = np.array(values)
                a[a < low] = low
                a[a > high] = high
                return a
           ''', mode="function", name="clip_values", checks={"forbidden_calls": ["clip"]}, time_limit=TL),
    ])

# ====================================================================== Day 53
best_cases = [(([[80, 90, 70], [95, 60, 85], [70, 75, 80]], ["민준", "서연", "지호"]), "t1", "3명 3과목"),
              (([[1, 2]], ["a"]), "h1", ""), (([[5, 5], [9, 0], [1, 9]], ["x", "y", "z"]), "h2", "")]
day53 = L(
    53, "집계와 축", W, ["numpy_aggregate", "numpy_indexing"],
    ["sum, mean, max, argmax, std 등 집계 함수를 쓸 수 있다.", "axis로 행 방향·열 방향 집계를 구분할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 인덱싱과 불리언 마스크로 원소를 골랐습니다.",
            "quiz": [quiz("d53_review_q1", "2차원 배열 `m`에서 모든 행의 첫 번째 열은?", ["`m[0]`", "`m[:, 0]`", "`m[0, :]`", "`m[0][0]`"], 1, "")]},
    concept={"title": "요약 통계 내기", "blocks": [
        text("`sum`, `mean`, `max`, `min`, `std`(표준편차)는 배열 전체를 하나의 값으로 요약합니다. `argmax`/`argmin`은 가장 큰/작은 값의 **위치**를 돌려줍니다."),
        ncode('''
            import numpy as np

            a = np.array([4, 9, 1, 7])
            print(a.sum(), a.mean(), a.max(), a.argmax())
            print(a.std().round(3))
            print(np.cumsum(a))
        '''),
        text("2차원에서 `axis=0`은 **세로 방향(열별)**, `axis=1`은 **가로 방향(행별)** 집계입니다. \"이 축을 따라 눌러서 없앤다\"고 생각하면 됩니다."),
        ncode('''
            import numpy as np

            scores = np.array([[80, 90, 70],
                               [95, 60, 85]])
            print(scores.sum(axis=0))
            print(scores.sum(axis=1))
            print(scores.mean(axis=1))
            print(scores.argmax(axis=1))
        '''),
        tip("행 = 학생, 열 = 과목인 표라면 `axis=0`은 과목별(학생들을 합침), `axis=1`은 학생별(과목들을 합침) 결과입니다."),
    ]},
    fill_intro="과목(열)별 평균을 구하세요.",
    coding_intro="axis와 argmax로 1등 학생과 과목별 최고점을 찾으세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`sum`, `mean`, `max`, `min`, `std`로 요약.",
        "`argmax`/`argmin`은 위치(인덱스).",
        "`axis=0` 열별(세로), `axis=1` 행별(가로).",
        "`np.cumsum`은 누적 합."],
        "quiz": [
            quiz("d53_summary_q1", "(3, 4) 배열의 `sum(axis=0)` 결과 모양은?", ["(3,)", "(4,)", "(3, 4)", "스칼라"], 1, "0번 축(3)이 사라집니다."),
            quiz("d53_summary_q2", "`np.array([2, 8, 5]).argmax()`는?", ["8", "1", "2", "0"], 1, "")]},
    exercises=[
        ex("d53_fill_1", "fill_blank", "과목별 평균",
           "행 = 학생, 열 = 과목인 점수 표에서 **과목별 평균** 배열을 반환하세요.",
           ["numpy_aggregate"], 1,
           '''
            import numpy as np


            def subject_means(scores):
                return np.array(scores).____(axis=____)
           ''',
           [t("t1", args=[[[80, 90], [60, 70]]], ret=[70.0, 80.0], desc="2×2"), t("h1", args=[[[1, 2, 3]]], ret=[1.0, 2.0, 3.0])],
           ["평균을 구하는 배열 메서드입니다.", "학생(행)들을 눌러 합치는 축 번호입니다."],
           '''
            import numpy as np


            def subject_means(scores):
                return np.array(scores).mean(axis=0)
           ''', mode="function", name="subject_means", time_limit=TL),
        ex("d53_code_1", "coding", "1등과 과목별 최고점",
           "점수 표(행 = 학생, 열 = 과목)와 이름 목록을 받아 `[총점이 가장 높은 학생 이름, 과목별 최고점 리스트]`를 반환하세요. 동점이면 앞 학생입니다.\n\n"
           "예: `([[80, 90, 70], [95, 60, 85], [70, 75, 80]], [\"민준\", \"서연\", \"지호\"])` → `[\"민준\", [95, 90, 85]]`",
           ["numpy_aggregate", "numpy_indexing"], 2,
           '''
            import numpy as np


            def best(scores, names):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_best(*a), desc=d) for a, tid, d in best_cases],
           ["학생별 총점은 `axis=1` 합계, 그중 가장 큰 위치는 `argmax()`입니다.", "과목별 최고점은 `axis=0` 최댓값입니다.",
            "`argmax()`가 돌려주는 위치로 `names`에서 이름을 꺼내세요(`int()`로 바꾸면 안전합니다)."],
           '''
            import numpy as np


            def best(scores, names):
                a = np.array(scores)
                top = int(a.sum(axis=1).argmax())
                return [names[top], a.max(axis=0)]
           ''', mode="function", name="best", time_limit=TL),
    ])

# ====================================================================== Day 54
lin_cases = [(([[1, 2], [3, 4]], [[1, 0, 1], [0, 1, 1]], [0, 0, 1]), "t1", "2×2 @ 2×3"), (([[1, 1]], [[2], [3]], [0.5]), "h1", ""),
             (([[0.5, -1], [2, 0], [1, 1]], [[1, 2], [3, 4]], [1, -1]), "h2", "")]
day54 = L(
    54, "모양 바꾸기와 행렬 곱", W, ["numpy_reshape", "numpy_ops"],
    ["reshape, 전치(T), 이어 붙이기로 배열 모양을 바꿀 수 있다.", "@ 연산자로 행렬 곱을 계산할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `axis`로 행별·열별 집계를 했습니다.",
            "quiz": [quiz("d54_review_q1", "학생별(행별) 평균을 구하는 코드는?", ["`m.mean(axis=0)`", "`m.mean(axis=1)`", "`m.mean()`", "`m.T.mean()`"], 1, "")]},
    concept={"title": "모양을 바꾸고 곱하기", "blocks": [
        text("`reshape(행, 열)`은 원소 수는 그대로 두고 모양만 바꿉니다. `-1`을 쓰면 나머지 크기를 자동 계산합니다. `T`는 행과 열을 바꿉니다(전치)."),
        ncode('''
            import numpy as np

            a = np.arange(6)
            m = a.reshape(2, 3)
            print(m)
            print(m.T)
            print(a.reshape(3, -1).shape)
            print(m.flatten())
            print(np.concatenate([a[:2], a[-2:]]))
            print(np.vstack([[1, 2], [3, 4]]))
        '''),
        text("`A @ B`는 **행렬 곱**입니다. (n, k) @ (k, m) → (n, m)으로, 앞 행렬의 열 수와 뒤 행렬의 행 수가 같아야 합니다. 딥러닝의 신경망 층이 바로 이 연산이에요."),
        ncode('''
            import numpy as np

            X = np.array([[1, 2], [3, 4]])
            W = np.array([[1, 0, 1], [0, 1, 1]])
            print(X @ W)
            print((X @ W).shape)
            print(X * X)
        '''),
        tip("`*`는 원소별 곱, `@`는 행렬 곱입니다. 헷갈리면 결과의 모양(shape)을 먼저 확인하세요."),
    ]},
    fill_intro="원하는 행 수로 모양을 바꾸세요.",
    coding_intro="신경망 한 층의 계산 `X @ W + b`를 구현하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`reshape(행, 열)`, `-1`은 자동 계산, `T`는 전치.",
        "`flatten()`은 1차원으로 펼치기.",
        "`np.concatenate`, `np.vstack`, `np.hstack`으로 잇기.",
        "`A @ B`: (n, k) @ (k, m) → (n, m)."],
        "quiz": [
            quiz("d54_summary_q1", "(2, 3) @ (3, 4)의 결과 모양은?", ["(2, 4)", "(3, 3)", "(2, 3)", "오류"], 0, ""),
            quiz("d54_summary_q2", "`np.arange(12).reshape(4, -1).shape`는?", ["(4, 3)", "(3, 4)", "(4, 12)", "오류"], 0, "")]},
    exercises=[
        ex("d54_fill_1", "fill_blank", "모양 바꾸기",
           "1차원 값 목록을 `rows`개의 행을 가진 2차원 배열로 바꿔 반환하세요(열 수는 자동).",
           ["numpy_reshape"], 1,
           '''
            import numpy as np


            def to_rows(values, rows):
                return np.array(values).____(rows, ____)
           ''',
           [t("t1", args=[[1, 2, 3, 4, 5, 6], 2], ret=[[1, 2, 3], [4, 5, 6]], desc="2행"), t("h1", args=[[1, 2, 3, 4], 4], ret=[[1], [2], [3], [4]])],
           ["모양을 바꾸는 배열 메서드입니다.", "나머지 크기를 자동으로 계산하게 하는 값입니다."],
           '''
            import numpy as np


            def to_rows(values, rows):
                return np.array(values).reshape(rows, -1)
           ''', mode="function", name="to_rows", time_limit=TL),
        ex("d54_code_1", "coding", "선형 층 계산",
           "입력 `X`(n×k), 가중치 `W`(k×m), 편향 `b`(길이 m)를 받아 `X @ W + b`를 계산하고 **소수 셋째 자리까지 반올림**한 배열을 반환하세요.\n\n"
           "예: `([[1, 2], [3, 4]], [[1, 0, 1], [0, 1, 1]], [0, 0, 1])` → `[[1, 2, 4], [3, 4, 8]]`",
           ["numpy_reshape", "numpy_ops"], 2,
           '''
            import numpy as np


            def linear(X, W, b):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_linear(*a), desc=d, compare={"mode": "float", "tol": 1e-9}) for a, tid, d in lin_cases],
           ["세 목록을 모두 배열로 바꾸세요.", "행렬 곱 결과(n×m)에 길이 m인 편향을 더하면 브로드캐스팅으로 각 행에 더해집니다.", "반올림은 `np.round(배열, 3)`."],
           '''
            import numpy as np


            def linear(X, W, b):
                out = np.array(X) @ np.array(W) + np.array(b)
                return np.round(out, 3)
           ''', mode="function", name="linear", time_limit=TL),
    ])

# ====================================================================== Day 55
dice_cases = [((10, 0), "t1", "10번"), ((600, 42), "h1", ""), ((1, 7), "h2", "")]
pi_cases = [((1000, 0), "t1", "1000개"), ((50000, 1), "h1", ""), ((10, 3), "h2", "")]
day55 = L(
    55, "난수와 시뮬레이션", W, ["numpy_random", "numpy_aggregate"],
    ["np.random.default_rng(seed)로 재현 가능한 난수를 만들 수 있다.", "난수로 확률 실험(시뮬레이션)을 할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `reshape`와 행렬 곱 `@`를 배웠습니다.",
            "quiz": [quiz("d55_review_q1", "`*`와 `@`의 차이는?", ["같다", "`*` 원소별 곱, `@` 행렬 곱", "`*` 행렬 곱, `@` 원소별 곱", "`@`는 문자열용"], 1, "")]},
    concept={"title": "무작위로 실험하기", "blocks": [
        text("`rng = np.random.default_rng(시드)`로 난수 생성기를 만듭니다. 시드가 같으면 매번 같은 난수가 나와 결과를 재현할 수 있습니다. "
             "`integers(낮음, 높음, size)`는 높음을 **포함하지 않는** 정수, `random(size)`는 0~1 실수, `normal(평균, 표준편차, size)`는 정규분포입니다."),
        ncode('''
            import numpy as np

            rng = np.random.default_rng(42)
            print(rng.integers(1, 7, size=5))
            print(rng.random(3).round(3))
            print(rng.normal(170, 5, size=3).round(1))
            print(rng.choice(["가위", "바위", "보"], size=4))
        '''),
        text("주사위를 많이 던지면 평균이 3.5에 가까워집니다(큰 수의 법칙). `np.bincount`는 각 값이 몇 번 나왔는지 셉니다."),
        ncode('''
            import numpy as np

            rng = np.random.default_rng(0)
            rolls = rng.integers(1, 7, size=6000)
            print(rolls.mean().round(2))
            print(np.bincount(rolls)[1:])
        '''),
        tip("머신러닝·딥러닝에서도 데이터 나누기, 가중치 초기화에 난수를 씁니다. 시드를 고정해야 실험 결과를 비교할 수 있어요."),
    ]},
    fill_intro="시드를 고정해 주사위 눈 횟수를 세세요.",
    coding_intro="몬테카를로 방법으로 원주율을 추정하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`rng = np.random.default_rng(seed)`: 시드로 재현성 확보.",
        "`integers`(끝 미포함), `random`, `normal`, `choice`.",
        "많이 반복한 실험의 평균은 기댓값에 가까워진다.",
        "`np.bincount`로 정수 값별 횟수 세기."],
        "quiz": [
            quiz("d55_summary_q1", "`rng.integers(1, 7)`이 만들 수 있는 값은?", ["0~6", "1~6", "1~7", "0~7"], 1, "끝값 7은 포함하지 않습니다."),
            quiz("d55_summary_q2", "같은 시드로 만든 생성기 두 개가 만드는 첫 난수는?", ["항상 같다", "항상 다르다", "가끔 같다", "오류"], 0, "")]},
    exercises=[
        ex("d55_fill_1", "fill_blank", "주사위 눈 세기",
           "시드 `seed`인 생성기로 주사위를 `n`번 던져, 1~6 각 눈이 나온 횟수 리스트(길이 6)를 반환하세요.",
           ["numpy_random"], 1,
           '''
            import numpy as np


            def dice_counts(n, seed):
                rng = np.random.____(seed)
                rolls = rng.integers(1, ____, size=n)
                return np.bincount(rolls, minlength=7)[1:]
           ''',
           [t(tid, args=list(a), ret=ref_dice(*a), desc=d) for a, tid, d in dice_cases],
           ["시드를 받아 난수 생성기를 만드는 함수 이름입니다(default로 시작).", "1~6이 나오려면 끝값은 6보다 하나 커야 합니다."],
           '''
            import numpy as np


            def dice_counts(n, seed):
                rng = np.random.default_rng(seed)
                rolls = rng.integers(1, 7, size=n)
                return np.bincount(rolls, minlength=7)[1:]
           ''', mode="function", name="dice_counts", time_limit=TL),
        ex("d55_code_1", "coding", "원주율 추정",
           "시드 `seed`인 생성기에서 `rng.random((n, 2))`로 0~1 사이 점 n개를 만들고, 원점에서 거리가 1 이하(`x² + y² <= 1`)인 점의 비율 × 4를 "
           "**소수 넷째 자리까지 반올림**해 반환하세요. `for` 문은 쓸 수 없습니다.",
           ["numpy_random", "numpy_ops", "numpy_aggregate"], 2,
           '''
            import numpy as np


            def estimate_pi(n, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_pi(*a), desc=d, compare={"mode": "float", "tol": 1e-9}) for a, tid, d in pi_cases],
           ["`rng.random((n, 2))`로 만든 (n, 2) 배열의 각 행이 점 하나입니다. 제곱해서 `axis=1`로 더하면 거리의 제곱입니다.",
            "조건 `<= 1`의 불리언 배열을 `sum()`하면 True 개수가 됩니다.", "결과는 `round(4 * 개수 / n, 4)`."],
           '''
            import numpy as np


            def estimate_pi(n, seed):
                rng = np.random.default_rng(seed)
                pts = rng.random((n, 2))
                inside = ((pts ** 2).sum(axis=1) <= 1).sum()
                return round(4 * inside / n, 4)
           ''', mode="function", name="estimate_pi", checks={"forbidden_syntax": ["for"]}, time_limit=TL),
    ])

# ====================================================================== Day 56 (review)
rep_cases = [([60, 70, 80, 90, 100], "t1", "기본"), ([50, 50, 80], "h1", ""), ([1, 2, 3, 4, 100], "h2", "")]
gol_cases = [([[0, 1, 0], [0, 1, 0], [0, 1, 0]], "t1", "깜빡이"), ([[1, 1], [1, 1]], "h1", ""), ([[0, 0, 0], [0, 1, 0], [0, 0, 0]], "h2", "")]


def ref_life(grid):
    g = np.array(grid)
    p = np.pad(g, 1)
    n = sum(np.roll(np.roll(p, dr, 0), dc, 1) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0))[1:-1, 1:-1]
    return ((n == 3) | ((g == 1) & (n == 2))).astype(int).tolist()


day56 = L(
    56, "8주차 누적 복습", W, ["numpy_array", "numpy_ops", "numpy_indexing", "numpy_aggregate", "numpy_reshape", "numpy_random"],
    ["NumPy의 생성·연산·마스크·집계를 조합해 데이터를 요약할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 50 | 배열 만들기 | `np.array`, `arange`, `linspace`, `shape` |\n"
        "| 51 | 연산 | 원소별 연산, 브로드캐스팅 |\n"
        "| 52 | 인덱싱 | `m[행, 열]`, 마스크 `a[a > 0]` |\n"
        "| 53 | 집계 | `sum/mean/max`, `axis`, `argmax` |\n"
        "| 54 | 모양·곱 | `reshape`, `T`, `@` |\n"
        "| 55 | 난수 | `default_rng(seed)`, 시뮬레이션 |"),
        "quiz": [
            quiz("d56_review_q1", "점수 배열에서 평균보다 높은 점수의 개수는?", ["`(a > a.mean()).sum()`", "`a.mean().sum()`", "`len(a > a.mean())`", "`a.argmax()`"], 0, ""),
            quiz("d56_review_q2", "(5, 3) 배열의 열별 최댓값 모양은?", ["(5,)", "(3,)", "(5, 3)", "스칼라"], 1, "")]},
    concept={"title": "표준화(z-점수)", "blocks": [
        text("값에서 평균을 빼고 표준편차로 나눈 것을 **z-점수**라고 합니다. 단위가 다른 데이터를 비교하거나, 머신러닝 전에 특성의 크기를 맞출 때 씁니다."),
        ncode('''
            import numpy as np

            a = np.array([60, 70, 80, 90, 100])
            z = (a - a.mean()) / a.std()
            print(z.round(2))
            print(z.mean().round(2), z.std().round(2))
        '''),
        tip("도전 문제의 \"생명 게임\"은 이웃 칸 수를 세는 문제입니다. `np.pad`로 테두리에 0을 두르면 가장자리 처리가 쉬워집니다."),
    ]},
    fill_intro="z-점수 공식을 완성하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "8주차 마무리", "points": [
        "벡터화(반복문 없이)로 빠르고 짧게.",
        "마스크로 거르고, axis로 요약하고, `@`로 곱한다.",
        "z-점수 = (x − 평균) / 표준편차.",
        "다음 주: pandas로 이름표가 붙은 표 데이터를 다룬다."],
        "quiz": [
            quiz("d56_summary_q1", "z-점수의 평균은?", ["0", "1", "원래 평균", "알 수 없음"], 0, ""),
            quiz("d56_summary_q2", "NumPy에서 반복문 대신 배열 연산을 쓰는 가장 큰 이유는?", ["코드가 길어져서", "속도와 간결함", "정확도가 낮아서", "메모리를 더 써서"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d56_fill_1", "fill_blank", "z-점수",
           "값들의 z-점수 배열을 **소수 둘째 자리까지 반올림**해 반환하세요.",
           ["numpy_aggregate", "numpy_ops"], 1,
           '''
            import numpy as np


            def zscores(values):
                a = np.array(values, dtype=float)
                return np.round((a - a.____()) / a.____(), 2)
           ''',
           [t("t1", args=[[60, 70, 80, 90, 100]], ret=np.round((np.array([60, 70, 80, 90, 100]) - 80) / np.array([60, 70, 80, 90, 100]).std(), 2).tolist(), desc="기본"),
            t("h1", args=[[1, 3]], ret=[-1.0, 1.0])],
           ["평균을 구하는 메서드입니다.", "표준편차(standard deviation)를 구하는 메서드입니다."],
           '''
            import numpy as np


            def zscores(values):
                a = np.array(values, dtype=float)
                return np.round((a - a.mean()) / a.std(), 2)
           ''', mode="function", name="zscores", time_limit=TL),
        ex("d56_code_1", "coding", "점수 리포트",
           "점수 목록을 받아 딕셔너리를 반환하세요.\n\n"
           "- `mean`, `std`: 평균·표준편차(소수 둘째 자리 반올림, 파이썬 float)\n- `above`: 평균보다 큰 점수 개수(int)\n"
           "- `z_max`: 가장 큰 z-점수(소수 둘째 자리 반올림)\n\n예: `[60, 70, 80, 90, 100]` → `{\"mean\": 80.0, \"std\": 14.14, \"above\": 2, \"z_max\": 1.41}`",
           ["numpy_aggregate", "numpy_ops", "numpy_indexing"], 2,
           '''
            import numpy as np


            def report(scores):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[s], ret=ref_report(s), desc=d, compare={"mode": "float", "tol": 1e-9}) for s, tid, d in rep_cases],
           ["배열로 바꾼 뒤 `mean()`, `std()`를 구하세요. `round(float(값), 2)`로 파이썬 실수로 만들면 깔끔합니다.",
            "평균보다 큰 개수는 마스크의 `sum()`, z-점수 최댓값은 `((a - 평균) / 표준편차).max()`."],
           '''
            import numpy as np


            def report(scores):
                a = np.array(scores, dtype=float)
                mean, std = a.mean(), a.std()
                z = (a - mean) / std
                return {"mean": round(float(mean), 2), "std": round(float(std), 2),
                        "above": int((a > mean).sum()), "z_max": round(float(z.max()), 2)}
           ''', mode="function", name="report", time_limit=TL),
        ex("d56_code_2", "coding", "[도전] 생명 게임 한 세대",
           "0/1 격자를 받아 콘웨이의 생명 게임 다음 세대를 반환하세요(격자 밖은 죽은 칸).\n\n"
           "- 살아 있는 칸(1)은 이웃(8방향) 중 살아 있는 칸이 2개 또는 3개면 살아남습니다.\n- 죽은 칸(0)은 이웃이 정확히 3개면 살아납니다.",
           ["numpy_indexing", "numpy_ops", "numpy_reshape"], 3,
           '''
            import numpy as np


            def next_generation(grid):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=[g], ret=ref_life(g), desc=d) for g, tid, d in gol_cases],
           ["`np.pad(g, 1)`로 테두리를 0으로 두르면 모든 칸이 8개의 이웃을 가집니다.",
            "이웃 수는 패딩된 배열에서 8방향으로 한 칸씩 옮긴 부분 배열(슬라이싱)들을 더해 구할 수 있습니다.",
            "규칙은 `(이웃 == 3) | ((g == 1) & (이웃 == 2))`이고, `astype(int)`로 0/1로 바꿉니다."],
           '''
            import numpy as np


            def next_generation(grid):
                g = np.array(grid)
                p = np.pad(g, 1)
                rows, cols = g.shape
                neighbors = np.zeros_like(g)
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if (dr, dc) != (0, 0):
                            neighbors += p[1 + dr:1 + dr + rows, 1 + dc:1 + dc + cols]
                alive = (neighbors == 3) | ((g == 1) & (neighbors == 2))
                return alive.astype(int)
           ''', mode="function", name="next_generation", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day50, day51, day52, day53, day54, day55, day56])
