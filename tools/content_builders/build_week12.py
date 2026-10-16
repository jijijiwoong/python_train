"""Week 12 (Day 78-84): 회귀."""
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 12, "ml", 30
F = {"compare": {"mode": "float", "tol": 1e-6}}


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


# ---------------------------------------------------------------- references
def ref_ls(xs, ys):
    x, y = np.array(xs, float), np.array(ys, float)
    w = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()
    return [round(float(w), 4), round(float(y.mean() - w * x.mean()), 4)]


def ref_bmi_model(seed):
    X, y = load_diabetes(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X[:, [2]], y, test_size=0.2, random_state=seed)
    m = LinearRegression().fit(Xtr, ytr)
    return [round(float(m.coef_[0]), 2), round(float(m.intercept_), 2), round(m.score(Xte, yte), 4)]


def ref_metrics(y_true, y_pred):
    yt, yp = np.array(y_true, float), np.array(y_pred, float)
    mse = float(((yt - yp) ** 2).mean())
    return {"mse": round(mse, 4), "rmse": round(mse ** 0.5, 4), "mae": round(float(np.abs(yt - yp).mean()), 4),
            "r2": round(float(1 - ((yt - yp) ** 2).sum() / ((yt - yt.mean()) ** 2).sum()), 4)}


def make_wave(n, seed):
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(0, 6, n))
    y = np.sin(x) + rng.normal(0, 0.3, n)
    return x.reshape(-1, 1), y


def ref_poly(degrees, seed):
    X, y = make_wave(60, seed)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed)
    out = []
    for d in degrees:
        pf = PolynomialFeatures(d)
        m = LinearRegression().fit(pf.fit_transform(Xtr), ytr)
        out.append([round(mean_squared_error(ytr, m.predict(pf.transform(Xtr))), 4),
                    round(mean_squared_error(yte, m.predict(pf.transform(Xte))), 4)])
    return out


def ref_step(xs, ys, w, b, lr):
    x, y = np.array(xs, float), np.array(ys, float)
    e = (w * x + b) - y
    return [round(float(w - lr * 2 * (e * x).mean()), 4), round(float(b - lr * 2 * e.mean()), 4)]


def ref_lasso(alphas):
    X, y = load_diabetes(return_X_y=True)
    return [int((Lasso(alpha=a).fit(X, y).coef_ == 0).sum()) for a in alphas]


def ref_gd(xs, ys, lr, epochs):
    x, y = np.array(xs, float), np.array(ys, float)
    w = b = 0.0
    losses = []
    for _ in range(epochs):
        pred = w * x + b
        err = pred - y
        losses.append(float((err ** 2).mean()))
        w -= lr * 2 * (err * x).mean()
        b -= lr * 2 * err.mean()
    return [round(w, 3), round(b, 3), losses[-1] < losses[0]]


def ref_compare(seed):
    X, y = load_diabetes(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed)
    return {name: round(model.fit(Xtr, ytr).score(Xte, yte), 4)
            for name, model in [("linear", LinearRegression()), ("ridge", Ridge(alpha=1.0)), ("lasso", Lasso(alpha=0.1))]}


def ref_gd_multi(lr, epochs):
    X, y = load_diabetes(return_X_y=True)
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)
    w, b = np.zeros(Xs.shape[1]), 0.0
    for _ in range(epochs):
        err = Xs @ w + b - y
        w -= lr * 2 * Xs.T @ err / len(y)
        b -= lr * 2 * err.mean()
    sk = LinearRegression().fit(Xs, y)
    return [round(float(r2_score(y, Xs @ w + b)), 3), round(float(sk.score(Xs, y)), 3)]


# ====================================================================== Day 78
ls_cases = [(([1, 2, 3, 4], [3, 5, 7, 9]), "t1", "y = 2x + 1"), (([0, 1, 2], [1, 1, 4]), "h1", ""), (([10, 20, 30, 40], [5, 4, 2, 1]), "h2", "")]
day78 = L(
    78, "선형 회귀의 원리", W, ["linear_regression", "numpy_aggregate"],
    ["데이터에 가장 잘 맞는 직선(y = wx + b)을 찾는 것이 선형 회귀임을 설명할 수 있다.", "최소제곱법으로 기울기와 절편을 직접 계산할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "11주차에는 범주를 맞히는 **분류**를 했습니다. 이번 주는 숫자를 맞히는 **회귀**입니다. 가장 기본은 데이터를 지나는 **직선**을 찾는 선형 회귀예요."),
        "quiz": [quiz("d78_review_q1", "공부 시간으로 점수(0~100 숫자)를 예측하는 문제는?", ["분류", "회귀", "군집", "검색"], 1, "")]},
    concept={"title": "가장 잘 맞는 직선", "blocks": [
        text("직선 `y = w·x + b`에서 **w**는 기울기(x가 1 늘 때 y 변화), **b**는 절편입니다. 각 점과 직선 사이의 세로 차이(**잔차**)를 제곱해 더한 값이 가장 작은 직선을 고르는 것을 **최소제곱법**이라고 합니다."),
        C('''
            import numpy as np

            x = np.array([1, 2, 3, 4, 5])
            y = np.array([2.1, 3.9, 6.2, 7.8, 10.1])
            w, b = np.polyfit(x, y, 1)
            print(round(w, 3), round(b, 3))
            pred = w * x + b
            print(np.round(y - pred, 2))
            print(round(w * 6 + b, 2))
        '''),
        text("공식으로 쓰면 `w = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)²`, `b = ȳ − w·x̄`입니다(x̄, ȳ는 평균). NumPy로 한 줄씩 계산할 수 있어요."),
        tip("잔차를 그냥 더하지 않고 제곱하는 이유: 양수·음수 오차가 서로 지워지지 않게 하고, 큰 오차를 더 무겁게 벌주기 위해서입니다."),
    ]},
    fill_intro="`np.polyfit`으로 직선을 맞추세요.",
    coding_intro="최소제곱 공식으로 기울기와 절편을 직접 구하세요(`polyfit` 사용 금지).",
    summary={"title": "오늘의 핵심 정리", "points": [
        "선형 회귀: `y = w·x + b`.",
        "잔차 = 실제 − 예측, 잔차 제곱합 최소 = 최소제곱법.",
        "`np.polyfit(x, y, 1)` → `[w, b]`.",
        "w = Σ(x−x̄)(y−ȳ)/Σ(x−x̄)², b = ȳ − w·x̄."],
        "quiz": [
            quiz("d78_summary_q1", "`y = 3x + 2`에서 x = 4일 때 예측값은?", ["12", "14", "9", "20"], 1, ""),
            quiz("d78_summary_q2", "잔차는?", ["예측 − 평균", "실제 − 예측", "기울기 × 절편", "x − y"], 1, "")]},
    exercises=[
        ex("d78_fill_1", "fill_blank", "직선 맞추기",
           "`np.polyfit`으로 1차 직선을 맞춰 `[기울기, 절편]`(소수 넷째 자리)을 반환하세요.",
           ["linear_regression"], 1,
           '''
            import numpy as np


            def fit_line(xs, ys):
                w, b = np.____(xs, ys, ____)
                return [round(float(w), 4), round(float(b), 4)]
           ''',
           [t(tid, args=list(a), ret=ref_ls(*a), desc=d, **F) for a, tid, d in ls_cases],
           ["다항식을 맞추는 NumPy 함수입니다(poly…).", "직선은 1차 다항식입니다."],
           '''
            import numpy as np


            def fit_line(xs, ys):
                w, b = np.polyfit(xs, ys, 1)
                return [round(float(w), 4), round(float(b), 4)]
           ''', mode="function", name="fit_line", time_limit=TL),
        ex("d78_code_1", "coding", "최소제곱 직접 계산",
           "최소제곱 공식으로 기울기 w와 절편 b를 계산해 `[w, b]`(소수 넷째 자리)를 반환하세요. `np.polyfit`은 쓸 수 없습니다.",
           ["linear_regression", "numpy_aggregate"], 2,
           '''
            import numpy as np


            def least_squares(xs, ys):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_ls(*a), desc=d, **F) for a, tid, d in ls_cases],
           ["x, y를 실수 배열로 바꾸고 각각의 평균을 구하세요.", "분자는 `((x - x평균) * (y - y평균)).sum()`, 분모는 `((x - x평균) ** 2).sum()`.",
            "절편은 `y평균 - w * x평균`."],
           '''
            import numpy as np


            def least_squares(xs, ys):
                x = np.array(xs, dtype=float)
                y = np.array(ys, dtype=float)
                w = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()
                b = y.mean() - w * x.mean()
                return [round(float(w), 4), round(float(b), 4)]
           ''', mode="function", name="least_squares", checks={"forbidden_calls": ["polyfit"]}, time_limit=TL),
    ])

# ====================================================================== Day 79
day79 = L(
    79, "scikit-learn 선형 회귀", W, ["linear_regression", "sklearn_api", "train_test"],
    ["LinearRegression으로 회귀 모델을 학습하고 coef_, intercept_를 해석할 수 있다.", "회귀 모델의 score(R²)를 구할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 최소제곱법으로 직선을 직접 맞췄습니다.",
            "quiz": [quiz("d79_review_q1", "최소제곱법이 최소로 만드는 것은?", ["잔차의 합", "잔차 제곱의 합", "기울기", "데이터 수"], 1, "")]},
    concept={"title": "같은 일을 scikit-learn으로", "blocks": [
        text("`LinearRegression`도 분류 모델과 똑같이 `fit` → `predict` → `score`입니다. 학습된 기울기는 `coef_`(특성마다 하나), 절편은 `intercept_`에 저장됩니다. X는 항상 **2차원**이어야 합니다."),
        C('''
            import numpy as np
            from sklearn.linear_model import LinearRegression

            x = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
            y = np.array([2.1, 3.9, 6.2, 7.8, 10.1])
            model = LinearRegression().fit(x, y)
            print(model.coef_.round(3), round(model.intercept_, 3))
            print(model.predict([[6]]).round(2))
        '''),
        text("당뇨병(diabetes) 데이터는 환자 442명의 특성 10개로 1년 뒤 병 진행 정도(숫자)를 예측하는 회귀 데이터입니다. 특성 하나(BMI, 2번 열)만 써 볼게요."),
        C('''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split

            X, y = load_diabetes(return_X_y=True)
            X_bmi = X[:, [2]]
            X_train, X_test, y_train, y_test = train_test_split(X_bmi, y, test_size=0.2, random_state=0)
            model = LinearRegression().fit(X_train, y_train)
            print(round(model.coef_[0], 1), round(model.score(X_test, y_test), 3))
        '''),
        tip("회귀 모델의 `score`는 정확도가 아니라 **R²(결정계수)**입니다. 1이면 완벽, 0이면 \"평균만 찍는 것\"과 같은 수준입니다(Day 80)."),
    ]},
    fill_intro="LinearRegression으로 기울기와 절편을 구하세요.",
    coding_intro="당뇨병 데이터의 BMI 특성 하나로 회귀 모델을 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`LinearRegression().fit(X, y)` (X는 2차원).",
        "`coef_` 기울기(특성별), `intercept_` 절편.",
        "회귀의 `score` = R².",
        "`X[:, [2]]`처럼 대괄호 두 번이면 열 하나를 2차원으로 고른다."],
        "quiz": [
            quiz("d79_summary_q1", "특성이 3개인 선형 회귀의 `coef_` 길이는?", ["1", "3", "4", "알 수 없음"], 1, ""),
            quiz("d79_summary_q2", "`X[:, 2]`와 `X[:, [2]]`의 모양 차이는?", ["같다", "(n,)과 (n, 1)", "(1, n)과 (n,)", "오류"], 1, "")]},
    exercises=[
        ex("d79_fill_1", "fill_blank", "기울기와 절편",
           "`LinearRegression`으로 xs, ys에 직선을 맞춰 `[기울기, 절편]`(소수 넷째 자리)을 반환하세요.",
           ["linear_regression", "sklearn_api"], 1,
           '''
            import numpy as np
            from sklearn.linear_model import LinearRegression


            def sk_line(xs, ys):
                X = np.array(xs).reshape(-1, 1)
                model = LinearRegression().fit(X, ys)
                return [round(float(model.____[0]), 4), round(float(model.____), 4)]
           ''',
           [t(tid, args=list(a), ret=ref_ls(*a), desc=d, **F) for a, tid, d in ls_cases],
           ["학습된 기울기가 저장된 속성입니다(coef…).", "학습된 절편이 저장된 속성입니다(intercept…)."],
           '''
            import numpy as np
            from sklearn.linear_model import LinearRegression


            def sk_line(xs, ys):
                X = np.array(xs).reshape(-1, 1)
                model = LinearRegression().fit(X, ys)
                return [round(float(model.coef_[0]), 4), round(float(model.intercept_), 4)]
           ''', mode="function", name="sk_line", time_limit=TL),
        ex("d79_code_1", "coding", "BMI로 예측하기",
           "당뇨병 데이터에서 BMI(2번 열)만 특성으로 써서 `test_size=0.2, random_state=seed`로 나누고 선형 회귀를 학습하세요. "
           "`[기울기(소수 둘째 자리), 절편(소수 둘째 자리), 테스트 R²(소수 넷째 자리)]`를 반환하세요.",
           ["linear_regression", "train_test"], 2,
           '''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split


            def bmi_model(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_bmi_model(0), desc="시드 0", **F), t("h1", args=[42], ret=ref_bmi_model(42), **F)],
           ["`X[:, [2]]`로 BMI 열을 2차원으로 고르세요.", "학습 후 `coef_[0]`, `intercept_`, `score(X_test, y_test)`."],
           '''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import LinearRegression
            from sklearn.model_selection import train_test_split


            def bmi_model(seed):
                X, y = load_diabetes(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X[:, [2]], y, test_size=0.2, random_state=seed)
                model = LinearRegression().fit(X_train, y_train)
                return [
                    round(float(model.coef_[0]), 2),
                    round(float(model.intercept_), 2),
                    round(model.score(X_test, y_test), 4),
                ]
           ''', mode="function", name="bmi_model", time_limit=TL),
    ])

# ====================================================================== Day 80
met_cases = [(([3, 5, 7, 9], [2.5, 5.5, 7, 8]), "t1", "기본"), (([1, 2, 3], [1, 2, 3]), "h1", "완벽"), (([10, 20, 30, 40], [25, 25, 25, 25]), "h2", "")]
day80 = L(
    80, "회귀 모델 평가", W, ["regression_metrics", "numpy_aggregate"],
    ["MSE, RMSE, MAE, R²의 뜻과 차이를 설명할 수 있다.", "지표를 직접 계산하고 sklearn.metrics와 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 `LinearRegression`으로 회귀 모델을 학습했고, `score`가 R²라는 것을 봤습니다.",
            "quiz": [quiz("d80_review_q1", "R² = 0의 의미는?", ["완벽한 예측", "평균만 찍는 것과 같은 수준", "음수 예측", "학습 실패 오류"], 1, "")]},
    concept={"title": "얼마나 틀렸나 재기", "blocks": [
        text("- **MSE**: 오차 제곱의 평균(큰 오차를 크게 벌줌)\n- **RMSE**: MSE의 제곱근(원래 단위로 해석)\n- **MAE**: 오차 절댓값의 평균(직관적, 이상치에 덜 민감)\n"
             "- **R²**: 1 − (오차 제곱합 / 평균과의 차 제곱합). 평균만 찍는 모델 대비 얼마나 나은가"),
        C('''
            import numpy as np
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

            y_true = np.array([3, 5, 7, 9])
            y_pred = np.array([2.5, 5.5, 7, 8])
            mse = ((y_true - y_pred) ** 2).mean()
            print(mse, mean_squared_error(y_true, y_pred))
            print(round(mse ** 0.5, 4), mean_absolute_error(y_true, y_pred))
            print(round(r2_score(y_true, y_pred), 4))
        '''),
        tip("지표마다 단위와 해석이 다릅니다. 보고할 때는 \"RMSE 3.2(점)\"처럼 단위와 함께 쓰고, 여러 모델은 **같은 지표, 같은 테스트 데이터**로 비교하세요."),
    ]},
    fill_intro="MSE 공식을 완성하세요.",
    coding_intro="네 가지 지표를 직접 계산하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "MSE = 평균((y − ŷ)²), RMSE = √MSE.",
        "MAE = 평균(|y − ŷ|).",
        "R² = 1 − Σ(y−ŷ)² / Σ(y−ȳ)².",
        "`sklearn.metrics`의 `mean_squared_error`, `mean_absolute_error`, `r2_score`."],
        "quiz": [
            quiz("d80_summary_q1", "오차 [1, −1, 2]의 MAE는?", ["0.67", "1.33", "2", "6"], 1, "(1+1+2)/3"),
            quiz("d80_summary_q2", "이상치(큰 오차)에 더 민감한 지표는?", ["MAE", "MSE", "둘 다 같다", "R²는 무관"], 1, "")]},
    exercises=[
        ex("d80_fill_1", "fill_blank", "MSE",
           "실제값과 예측값으로 MSE(소수 넷째 자리)를 반환하세요.",
           ["regression_metrics"], 1,
           '''
            import numpy as np


            def mse(y_true, y_pred):
                diff = np.array(y_true) - np.array(y_pred)
                return round(float((diff ____ 2).____()), 4)
           ''',
           [t(tid, args=list(a), ret=ref_metrics(*a)["mse"], desc=d, **F) for a, tid, d in met_cases],
           ["제곱 연산자입니다.", "평균을 구하는 메서드입니다."],
           '''
            import numpy as np


            def mse(y_true, y_pred):
                diff = np.array(y_true) - np.array(y_pred)
                return round(float((diff ** 2).mean()), 4)
           ''', mode="function", name="mse", time_limit=TL),
        ex("d80_code_1", "coding", "회귀 지표 4종",
           "실제값과 예측값으로 `{\"mse\", \"rmse\", \"mae\", \"r2\"}` 딕셔너리(각 소수 넷째 자리)를 반환하세요. NumPy로 직접 계산하세요.",
           ["regression_metrics", "numpy_aggregate"], 2,
           '''
            import numpy as np


            def metrics(y_true, y_pred):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_metrics(*a), desc=d, **F) for a, tid, d in met_cases],
           ["오차 `e = y - ŷ`를 먼저 구하세요.", "R²의 분모는 `((y - y.mean()) ** 2).sum()`.", "값은 `round(float(...), 4)`."],
           '''
            import numpy as np


            def metrics(y_true, y_pred):
                y = np.array(y_true, dtype=float)
                p = np.array(y_pred, dtype=float)
                e = y - p
                mse = float((e ** 2).mean())
                r2 = 1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum()
                return {"mse": round(mse, 4), "rmse": round(mse ** 0.5, 4),
                        "mae": round(float(np.abs(e).mean()), 4), "r2": round(float(r2), 4)}
           ''', mode="function", name="metrics", time_limit=TL),
    ])

# ====================================================================== Day 81
poly_cases = [(([1, 3, 15], 0), "t1", "차수 1·3·15"), (([2, 5], 1), "h1", "")]
day81 = L(
    81, "다항 회귀", W, ["polynomial", "linear_regression", "overfitting"],
    ["PolynomialFeatures로 곡선 관계를 선형 회귀로 다룰 수 있다.", "차수가 너무 높으면 학습 오차는 줄지만 테스트 오차가 커질 수 있음을 확인한다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 MSE, RMSE, MAE, R²로 회귀 모델을 평가했습니다.",
            "quiz": [quiz("d81_review_q1", "RMSE의 장점은?", ["항상 0~1", "원래 값과 같은 단위", "계산이 없음", "이상치 무시"], 1, "")]},
    concept={"title": "직선으로 곡선 맞추기", "blocks": [
        text("x 하나로 `x, x², x³…`처럼 새 특성을 만들어 선형 회귀에 넣으면 곡선을 맞출 수 있습니다. `PolynomialFeatures(degree)`가 이 특성들을 만들어 줍니다."),
        C('''
            import numpy as np
            from sklearn.preprocessing import PolynomialFeatures

            x = np.array([[2], [3]])
            print(PolynomialFeatures(3).fit_transform(x))
        '''),
        text("차수를 올리면 학습 데이터에는 점점 더 잘 맞지만, 너무 높으면 잡음까지 외워 새 데이터에서 틀립니다(**과적합**, Day 96에서 자세히)."),
        C('''
            import numpy as np
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_squared_error
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import PolynomialFeatures

            rng = np.random.default_rng(0)
            x = np.sort(rng.uniform(0, 6, 60)).reshape(-1, 1)
            y = np.sin(x).ravel() + rng.normal(0, 0.3, 60)
            X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)
            for degree in [1, 3, 15]:
                pf = PolynomialFeatures(degree)
                model = LinearRegression().fit(pf.fit_transform(X_train), y_train)
                train_mse = mean_squared_error(y_train, model.predict(pf.transform(X_train)))
                test_mse = mean_squared_error(y_test, model.predict(pf.transform(X_test)))
                print(degree, round(train_mse, 3), round(test_mse, 3))
        '''),
        tip("변환기는 학습 데이터에 `fit_transform`, 테스트 데이터에는 `transform`만 씁니다. 테스트 데이터의 정보가 학습에 새지 않게 하기 위해서예요(17주차 파이프라인으로 자동화)."),
    ]},
    fill_intro="다항 특성을 만드세요.",
    coding_intro="차수별 학습·테스트 MSE를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`PolynomialFeatures(d)`로 x → [1, x, x², …, x^d].",
        "다항 특성 + 선형 회귀 = 다항 회귀.",
        "차수↑ → 학습 오차↓, 너무 높으면 테스트 오차↑(과적합).",
        "변환기: 학습은 `fit_transform`, 테스트는 `transform`."],
        "quiz": [
            quiz("d81_summary_q1", "`PolynomialFeatures(2).fit_transform([[3]])`의 결과는?", ["`[[3, 9]]`", "`[[1, 3, 9]]`", "`[[9]]`", "`[[1, 3]]`"], 1, ""),
            quiz("d81_summary_q2", "학습 오차는 매우 작은데 테스트 오차가 크다면?", ["과소적합", "과적합", "정상", "데이터 부족 아님"], 1, "")]},
    exercises=[
        ex("d81_fill_1", "fill_blank", "다항 특성",
           "값 x 하나에 대해 `degree`차까지의 다항 특성 리스트를 반환하세요.\n\n예: `poly_features(3, 2)` → `[1.0, 3.0, 9.0]`",
           ["polynomial"], 1,
           '''
            from sklearn.preprocessing import ____


            def poly_features(x, degree):
                pf = PolynomialFeatures(____)
                return pf.fit_transform([[x]])[0]
           ''',
           [t("t1", args=[3, 2], ret=[1.0, 3.0, 9.0], desc="x=3, 2차"), t("h1", args=[2, 3], ret=[1.0, 2.0, 4.0, 8.0])],
           ["다항 특성을 만드는 변환기 클래스 이름입니다.", "차수로 쓸 매개변수입니다."],
           '''
            from sklearn.preprocessing import PolynomialFeatures


            def poly_features(x, degree):
                pf = PolynomialFeatures(degree)
                return pf.fit_transform([[x]])[0]
           ''', mode="function", name="poly_features", time_limit=TL),
        ex("d81_code_1", "coding", "차수별 오차",
           "아래 `make_wave(60, seed)`로 데이터를 만들고 `test_size=0.3, random_state=seed`로 나눈 뒤, `degrees`의 각 차수로 다항 회귀를 학습하세요. "
           "차수마다 `[학습 MSE, 테스트 MSE]`(소수 넷째 자리)를 담은 리스트를 반환합니다.",
           ["polynomial", "regression_metrics", "overfitting"], 2,
           '''
            import numpy as np
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_squared_error
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import PolynomialFeatures


            def make_wave(n, seed):
                rng = np.random.default_rng(seed)
                x = np.sort(rng.uniform(0, 6, n))
                y = np.sin(x) + rng.normal(0, 0.3, n)
                return x.reshape(-1, 1), y


            def degree_errors(degrees, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_poly(*a), desc=d, **F) for a, tid, d in poly_cases],
           ["데이터를 한 번 나눈 뒤 차수마다 `PolynomialFeatures(d)`를 새로 만드세요.",
            "학습 특성은 `fit_transform(X_train)`, 테스트 특성은 `transform(X_test)`.", "`mean_squared_error`로 두 오차를 구해 반올림합니다."],
           '''
            import numpy as np
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_squared_error
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import PolynomialFeatures


            def make_wave(n, seed):
                rng = np.random.default_rng(seed)
                x = np.sort(rng.uniform(0, 6, n))
                y = np.sin(x) + rng.normal(0, 0.3, n)
                return x.reshape(-1, 1), y


            def degree_errors(degrees, seed):
                X, y = make_wave(60, seed)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)
                results = []
                for d in degrees:
                    pf = PolynomialFeatures(d)
                    model = LinearRegression().fit(pf.fit_transform(X_train), y_train)
                    train_mse = mean_squared_error(y_train, model.predict(pf.transform(X_train)))
                    test_mse = mean_squared_error(y_test, model.predict(pf.transform(X_test)))
                    results.append([round(train_mse, 4), round(test_mse, 4)])
                return results
           ''', mode="function", name="degree_errors", time_limit=TL),
    ])

# ====================================================================== Day 82
day82 = L(
    82, "규제: Ridge와 Lasso", W, ["regularization", "linear_regression"],
    ["규제가 가중치를 작게 만들어 과적합을 줄이는 원리를 설명할 수 있다.", "Ridge와 Lasso의 차이(Lasso는 일부 가중치를 0으로)를 확인할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 다항 회귀에서 차수가 높으면 과적합이 생기는 것을 봤습니다.",
            "quiz": [quiz("d82_review_q1", "과적합 모델의 특징은?", ["학습·테스트 오차 모두 큼", "학습 오차 작고 테스트 오차 큼", "둘 다 작음", "테스트만 작음"], 1, "")]},
    concept={"title": "가중치에 벌점 주기", "blocks": [
        text("**규제**는 \"오차를 줄이되 가중치(coef)가 너무 커지지 않게\" 벌점을 더하는 방법입니다. `alpha`가 클수록 벌점이 커져 가중치가 0 쪽으로 줄어듭니다.\n\n"
             "- **Ridge**: 가중치 제곱에 벌점 → 골고루 작게\n- **Lasso**: 가중치 절댓값에 벌점 → 쓸모없는 특성의 가중치를 정확히 0으로(특성 선택 효과)"),
        C('''
            import numpy as np
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Lasso, LinearRegression, Ridge

            X, y = load_diabetes(return_X_y=True)
            for model in [LinearRegression(), Ridge(alpha=1.0), Lasso(alpha=1.0)]:
                model.fit(X, y)
                print(type(model).__name__, round(np.abs(model.coef_).sum(), 1), int((model.coef_ == 0).sum()))
        '''),
        tip("규제는 특성 크기(스케일)에 영향을 받습니다. diabetes 데이터는 이미 표준화되어 있지만, 일반 데이터에서는 먼저 스케일링(17주차)을 하세요."),
    ]},
    fill_intro="Ridge 모델을 학습시켜 가중치 크기를 확인하세요.",
    coding_intro="alpha에 따라 Lasso가 0으로 만드는 가중치 개수를 세세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "규제 = 오차 + 가중치 벌점, `alpha`로 세기 조절.",
        "Ridge: 제곱 벌점, 가중치를 골고루 줄임.",
        "Lasso: 절댓값 벌점, 일부 가중치를 0으로.",
        "규제는 과적합을 줄이는 대표적인 방법."],
        "quiz": [
            quiz("d82_summary_q1", "alpha를 키우면 가중치는?", ["커진다", "0 쪽으로 작아진다", "변함없다", "음수가 된다"], 1, ""),
            quiz("d82_summary_q2", "쓸모없는 특성을 자동으로 빼 주는 효과가 있는 것은?", ["Ridge", "Lasso", "LinearRegression", "PolynomialFeatures"], 1, "")]},
    exercises=[
        ex("d82_fill_1", "fill_blank", "Ridge 가중치 크기",
           "당뇨병 데이터 전체로 `Ridge(alpha=alpha)`를 학습해 가중치 절댓값 합(소수 첫째 자리)을 반환하세요.",
           ["regularization"], 1,
           '''
            import numpy as np
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import ____


            def ridge_size(alpha):
                X, y = load_diabetes(return_X_y=True)
                model = Ridge(alpha=____).fit(X, y)
                return round(float(np.abs(model.coef_).sum()), 1)
           ''',
           [t("t1", args=[1.0], ret=round(float(np.abs(Ridge(alpha=1.0).fit(*load_diabetes(return_X_y=True)).coef_).sum()), 1), desc="alpha=1", **F),
            t("h1", args=[10.0], ret=round(float(np.abs(Ridge(alpha=10.0).fit(*load_diabetes(return_X_y=True)).coef_).sum()), 1), **F)],
           ["제곱 벌점 규제 회귀 모델의 클래스 이름입니다.", "규제 세기로 쓸 매개변수입니다."],
           '''
            import numpy as np
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Ridge


            def ridge_size(alpha):
                X, y = load_diabetes(return_X_y=True)
                model = Ridge(alpha=alpha).fit(X, y)
                return round(float(np.abs(model.coef_).sum()), 1)
           ''', mode="function", name="ridge_size", time_limit=TL),
        ex("d82_code_1", "coding", "Lasso가 지운 특성 수",
           "당뇨병 데이터 전체로 `alphas`의 각 값마다 `Lasso(alpha=값)`을 학습해, 가중치가 정확히 0인 특성의 개수 리스트를 반환하세요.",
           ["regularization", "numpy_indexing"], 2,
           '''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Lasso


            def zero_counts(alphas):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[0.01, 0.5, 2.0]], ret=ref_lasso([0.01, 0.5, 2.0]), desc="세 alpha"), t("h1", args=[[5.0]], ret=ref_lasso([5.0]))],
           ["alpha마다 새 Lasso 모델을 만들어 `fit`.", "`(model.coef_ == 0).sum()`을 `int()`로 바꿔 리스트에 담습니다."],
           '''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Lasso


            def zero_counts(alphas):
                X, y = load_diabetes(return_X_y=True)
                counts = []
                for alpha in alphas:
                    model = Lasso(alpha=alpha).fit(X, y)
                    counts.append(int((model.coef_ == 0).sum()))
                return counts
           ''', mode="function", name="zero_counts", time_limit=TL),
    ])

# ====================================================================== Day 83
gd_cases = [(([1, 2, 3, 4], [3, 5, 7, 9], 0.05, 2000), "t1", "y = 2x + 1"), (([0, 1, 2], [1, 3, 5], 0.1, 1000), "h1", ""),
            (([1, 2, 3], [2, 2, 2], 0.05, 500), "h2", "")]
day83 = L(
    83, "경사하강법 직접 구현", W, ["gradient_descent", "linear_regression", "numpy_ops"],
    ["손실(오차)을 줄이는 방향으로 가중치를 조금씩 바꾸는 경사하강법을 설명할 수 있다.", "NumPy로 선형 회귀의 경사하강법을 구현할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 Ridge·Lasso로 가중치에 벌점을 줬습니다.",
            "quiz": [quiz("d83_review_q1", "Lasso의 특징은?", ["가중치를 키운다", "일부 가중치를 정확히 0으로 만든다", "비선형 모델이다", "분류 전용"], 1, "")]},
    concept={"title": "내리막길 따라가기", "blocks": [
        text("공식으로 답을 구할 수 없는 모델(특히 딥러닝)은 **경사하강법**으로 학습합니다. 손실(예: MSE)이 줄어드는 방향(기울기의 반대)으로 가중치를 **학습률**만큼 조금씩 옮기는 일을 반복합니다.\n\n"
             "MSE를 w, b로 미분하면: `dw = 2·평균((ŷ−y)·x)`, `db = 2·평균(ŷ−y)` → `w -= lr·dw`, `b -= lr·db`"),
        C('''
            import numpy as np

            x = np.array([1, 2, 3, 4], dtype=float)
            y = np.array([3, 5, 7, 9], dtype=float)
            w, b, lr = 0.0, 0.0, 0.05
            for epoch in range(1, 1001):
                error = (w * x + b) - y
                w -= lr * 2 * (error * x).mean()
                b -= lr * 2 * error.mean()
                if epoch in (1, 10, 100, 1000):
                    print(epoch, round((error ** 2).mean(), 4), round(w, 3), round(b, 3))
        '''),
        tip("학습률이 너무 크면 손실이 오히려 커지며 튀고(발산), 너무 작으면 아주 느립니다. 이 감각은 4단계 딥러닝에서 그대로 쓰입니다."),
    ]},
    fill_intro="경사하강법 한 단계를 완성하세요.",
    coding_intro="경사하강법으로 직선을 학습하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "경사하강법: 손실의 기울기 반대 방향으로 조금씩 이동.",
        "선형 회귀: `dw = 2·mean(e·x)`, `db = 2·mean(e)` (e = ŷ − y).",
        "학습률: 너무 크면 발산, 너무 작으면 느림.",
        "에폭(epoch) = 데이터 전체를 한 번 사용한 학습 단위."],
        "quiz": [
            quiz("d83_summary_q1", "기울기 dw가 양수면 w는 어느 쪽으로?", ["증가", "감소", "그대로", "0으로"], 1, "기울기 반대 방향"),
            quiz("d83_summary_q2", "손실이 매 에폭 커지기만 한다면 의심할 것은?", ["학습률이 너무 큼", "데이터가 너무 적음", "에폭이 너무 많음", "정상"], 0, "")]},
    exercises=[
        ex("d83_fill_1", "fill_blank", "한 단계 업데이트",
           "현재 `w, b`에서 경사하강법을 **한 번** 적용한 새 `[w, b]`(소수 넷째 자리)를 반환하세요.",
           ["gradient_descent"], 1,
           '''
            import numpy as np


            def step(xs, ys, w, b, lr):
                x = np.array(xs, dtype=float)
                y = np.array(ys, dtype=float)
                error = (w * x + b) - y
                w = w ____ lr * 2 * (error * x).mean()
                b = b - lr * 2 * error.____()
                return [round(float(w), 4), round(float(b), 4)]
           ''',
           [t("t1", args=[[1, 2], [2, 4], 0.0, 0.0, 0.1], ret=ref_step([1, 2], [2, 4], 0.0, 0.0, 0.1), desc="첫 단계", **F),
            t("h1", args=[[1, 2, 3], [1, 1, 1], 1.0, 0.0, 0.01], ret=ref_step([1, 2, 3], [1, 1, 1], 1.0, 0.0, 0.01), **F)],
           ["기울기의 반대 방향으로 이동하므로 빼야 합니다.", "평균을 구하는 메서드입니다."],
           '''
            import numpy as np


            def step(xs, ys, w, b, lr):
                x = np.array(xs, dtype=float)
                y = np.array(ys, dtype=float)
                error = (w * x + b) - y
                w = w - lr * 2 * (error * x).mean()
                b = b - lr * 2 * error.mean()
                return [round(float(w), 4), round(float(b), 4)]
           ''', mode="function", name="step", time_limit=TL),
        ex("d83_code_1", "coding", "경사하강법 학습",
           "w = b = 0에서 시작해 `epochs`번 경사하강법을 반복하세요. `[최종 w(소수 셋째 자리), 최종 b(소수 셋째 자리), 마지막 손실 < 첫 손실]`을 반환합니다. "
           "손실은 매 반복의 **업데이트 전** MSE입니다.",
           ["gradient_descent", "numpy_ops"], 2,
           '''
            import numpy as np


            def train_gd(xs, ys, lr, epochs):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_gd(*a), desc=d, **F) for a, tid, d in gd_cases],
           ["반복마다: 예측 → 오차 → 손실 기록 → w, b 업데이트 순서입니다.", "손실 목록의 첫 값과 마지막 값을 비교하세요.", "반환할 때 `round(float(w), 3)`."],
           '''
            import numpy as np


            def train_gd(xs, ys, lr, epochs):
                x = np.array(xs, dtype=float)
                y = np.array(ys, dtype=float)
                w = b = 0.0
                losses = []
                for _ in range(epochs):
                    error = (w * x + b) - y
                    losses.append(float((error ** 2).mean()))
                    w -= lr * 2 * (error * x).mean()
                    b -= lr * 2 * error.mean()
                return [round(float(w), 3), round(float(b), 3), losses[-1] < losses[0]]
           ''', mode="function", name="train_gd", time_limit=TL),
    ])

# ====================================================================== Day 84 (review)
day84 = L(
    84, "12주차 누적 복습", W, ["linear_regression", "regression_metrics", "polynomial", "regularization", "gradient_descent"],
    ["여러 회귀 모델을 같은 기준으로 비교하고 결과를 해석할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 78 | 원리 | 최소제곱, `polyfit` |\n| 79 | sklearn | `LinearRegression`, `coef_`, `intercept_` |\n"
        "| 80 | 평가 | MSE, RMSE, MAE, R² |\n| 81 | 다항 | `PolynomialFeatures`, 과적합 |\n"
        "| 82 | 규제 | Ridge, Lasso, `alpha` |\n| 83 | 경사하강법 | `w -= lr·dw` |"),
        "quiz": [
            quiz("d84_review_q1", "여러 회귀 모델을 공정하게 비교하려면?", ["모델마다 다른 테스트 데이터", "같은 테스트 데이터와 같은 지표", "학습 점수만 비교", "가장 복잡한 모델 선택"], 1, ""),
            quiz("d84_review_q2", "경사하강법 전에 특성을 표준화하면 좋은 이유는?", ["특성 크기가 비슷해져 학습이 안정적", "정확도가 항상 100%", "규제가 필요 없어짐", "데이터가 줄어듦"], 0, "")]},
    concept={"title": "모델 비교 표 만들기", "blocks": [
        text("같은 데이터 분할에서 여러 모델을 학습해 같은 지표로 비교하면, 무엇이 나은지 공정하게 판단할 수 있습니다."),
        C('''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Lasso, LinearRegression, Ridge
            from sklearn.model_selection import train_test_split

            X, y = load_diabetes(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)
            models = {"linear": LinearRegression(), "ridge": Ridge(alpha=1.0), "lasso": Lasso(alpha=0.1)}
            for name, model in models.items():
                print(name, round(model.fit(X_train, y_train).score(X_test, y_test), 4))
        '''),
        tip("도전 문제는 특성 10개짜리 경사하강법입니다. 행렬 곱 `X @ w`(Day 54)로 모든 샘플의 예측을 한 번에 계산하고, 기울기는 `X.T @ 오차 / n`입니다."),
    ]},
    fill_intro="RMSE를 구하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "12주차 마무리", "points": [
        "회귀 = 숫자 예측, 기본은 선형 회귀.",
        "평가는 같은 데이터·같은 지표로.",
        "다항 특성은 표현력을, 규제는 안정성을 준다.",
        "다음 주: 분류 모델(로지스틱 회귀, SVM, 나이브 베이즈)."],
        "quiz": [
            quiz("d84_summary_q1", "R²가 음수라면?", ["완벽", "평균만 찍는 것보다 못함", "계산 오류", "과소적합 아님"], 1, ""),
            quiz("d84_summary_q2", "다음 주 배울 로지스틱 회귀는 어떤 문제용?", ["회귀", "분류", "군집", "차원 축소"], 1, "이름과 달리 분류 모델입니다.")]},
    is_review=True,
    exercises=[
        ex("d84_fill_1", "fill_blank", "RMSE",
           "실제값·예측값의 RMSE(소수 넷째 자리)를 반환하세요.",
           ["regression_metrics"], 1,
           '''
            from sklearn.metrics import mean_squared_error


            def rmse(y_true, y_pred):
                return round(____(y_true, y_pred) ** ____, 4)
           ''',
           [t(tid, args=list(a), ret=ref_metrics(*a)["rmse"], desc=d, **F) for a, tid, d in met_cases],
           ["MSE를 구하는 함수입니다.", "제곱근은 0.5 제곱입니다."],
           '''
            from sklearn.metrics import mean_squared_error


            def rmse(y_true, y_pred):
                return round(mean_squared_error(y_true, y_pred) ** 0.5, 4)
           ''', mode="function", name="rmse", time_limit=TL),
        ex("d84_code_1", "coding", "회귀 모델 비교",
           "당뇨병 데이터를 `test_size=0.25, random_state=seed`로 나누고, `LinearRegression()`, `Ridge(alpha=1.0)`, `Lasso(alpha=0.1)`의 테스트 R²(소수 넷째 자리)를 "
           "`{\"linear\": …, \"ridge\": …, \"lasso\": …}`로 반환하세요.",
           ["linear_regression", "regularization", "regression_metrics"], 2,
           '''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Lasso, LinearRegression, Ridge
            from sklearn.model_selection import train_test_split


            def compare_models(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_compare(0), desc="시드 0", **F), t("h1", args=[7], ret=ref_compare(7), **F)],
           ["이름 → 모델 딕셔너리를 만들고 `items()`로 돌며 학습·평가하세요.", "`model.fit(...).score(...)`처럼 이어 쓸 수 있습니다."],
           '''
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import Lasso, LinearRegression, Ridge
            from sklearn.model_selection import train_test_split


            def compare_models(seed):
                X, y = load_diabetes(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed)
                models = {"linear": LinearRegression(), "ridge": Ridge(alpha=1.0), "lasso": Lasso(alpha=0.1)}
                scores = {}
                for name, model in models.items():
                    scores[name] = round(model.fit(X_train, y_train).score(X_test, y_test), 4)
                return scores
           ''', mode="function", name="compare_models", time_limit=TL),
        ex("d84_code_2", "coding", "[도전] 다변수 경사하강법",
           "당뇨병 데이터 전체(X는 열마다 `(X - 평균) / 표준편차`로 표준화)에 대해 w = 0 벡터, b = 0에서 시작해 `epochs`번 경사하강법을 하세요. "
           "기울기: `dw = 2 · Xᵀ(ŷ − y) / n`, `db = 2 · 평균(ŷ − y)`.\n\n"
           "`[내 모델의 R², LinearRegression의 R²]`(같은 표준화 데이터로 학습·평가, 소수 셋째 자리)를 반환하세요.",
           ["gradient_descent", "numpy_reshape", "linear_regression"], 3,
           '''
            import numpy as np
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score


            def multi_gd(lr, epochs):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0.1, 500], ret=ref_gd_multi(0.1, 500), desc="lr 0.1", **F), t("h1", args=[0.05, 300], ret=ref_gd_multi(0.05, 300), **F)],
           ["표준화는 열마다 평균을 빼고 표준편차로 나누는 것입니다(`axis=0`).", "반복마다 `err = Xs @ w + b - y`, `w -= lr * 2 * Xs.T @ err / n`.",
            "비교 모델은 `LinearRegression().fit(Xs, y).score(Xs, y)`."],
           '''
            import numpy as np
            from sklearn.datasets import load_diabetes
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score


            def multi_gd(lr, epochs):
                X, y = load_diabetes(return_X_y=True)
                Xs = (X - X.mean(axis=0)) / X.std(axis=0)
                w = np.zeros(Xs.shape[1])
                b = 0.0
                for _ in range(epochs):
                    err = Xs @ w + b - y
                    w -= lr * 2 * Xs.T @ err / len(y)
                    b -= lr * 2 * err.mean()
                mine = r2_score(y, Xs @ w + b)
                sk = LinearRegression().fit(Xs, y).score(Xs, y)
                return [round(float(mine), 3), round(float(sk), 3)]
           ''', mode="function", name="multi_gd", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day78, day79, day80, day81, day82, day83, day84])
