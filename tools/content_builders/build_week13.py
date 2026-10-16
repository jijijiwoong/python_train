"""Week 13 (Day 85-91): 분류."""
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_breast_cancer, load_digits, make_moons
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 13, "ml", 40
F = {"compare": {"mode": "float", "tol": 1e-6}}


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


def cancer_split(seed):
    X, y = load_breast_cancer(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    mean, std = Xtr.mean(axis=0), Xtr.std(axis=0)
    return (Xtr - mean) / std, (Xte - mean) / std, ytr, yte


# ---------------------------------------------------------------- references
def ref_sigmoid(zs):
    return np.round(1 / (1 + np.exp(-np.array(zs, float))), 4).tolist()


def ref_cancer_lr(seed):
    Xtr, Xte, ytr, yte = cancer_split(seed)
    m = LogisticRegression().fit(Xtr, ytr)
    return [Xtr.shape[1], round(m.score(Xte, yte), 4)]


def ref_thresholds(ths, seed):
    Xtr, Xte, ytr, yte = cancer_split(seed)
    proba = LogisticRegression().fit(Xtr, ytr).predict_proba(Xte)[:, 1]
    out = []
    for th in ths:
        pred = (proba >= th).astype(int)
        out.append([int(pred.sum()), round(float((pred == yte).mean()), 4)])
    return out


def ref_moons(noise, seed):
    X, y = make_moons(n_samples=300, noise=noise, random_state=seed)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed)
    return {"logistic": round(LogisticRegression().fit(Xtr, ytr).score(Xte, yte), 4),
            "knn": round(KNeighborsClassifier(n_neighbors=5).fit(Xtr, ytr).score(Xte, yte), 4)}


def ref_svm(C_, seed):
    X, y = make_moons(n_samples=300, noise=0.25, random_state=seed)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed)
    out = {}
    for k in ["linear", "rbf"]:
        m = SVC(kernel=k, C=C_).fit(Xtr, ytr)
        out[k] = [round(m.score(Xte, yte), 4), int(m.n_support_.sum())]
    return out


TRAIN_TEXTS = ["무료 쿠폰 지금 받기", "오늘 회의 몇 시에 할까요", "당첨 축하 무료 상품 받기", "점심 같이 먹어요",
               "지금 클릭 무료 이벤트", "내일 수업 자료 보내 드려요", "특가 할인 쿠폰 당첨", "회의 자료 확인 부탁드려요"]
TRAIN_LABELS = ["스팸", "정상", "스팸", "정상", "스팸", "정상", "스팸", "정상"]


def ref_spam(texts):
    vec = CountVectorizer()
    model = MultinomialNB().fit(vec.fit_transform(TRAIN_TEXTS), TRAIN_LABELS)
    return [len(vec.vocabulary_), model.predict(vec.transform(texts)).tolist()]


def ref_digits(k, seed):
    X, y = load_digits(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    pred = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr).predict(Xte)
    per = [float((pred[yte == d] == d).mean()) for d in range(10)]
    return [round(float((pred == yte).mean()), 4), int(np.argmin(per))]


def ref_compare(seed):
    Xtr, Xte, ytr, yte = cancer_split(seed)
    models = {"logistic": LogisticRegression(), "knn": KNeighborsClassifier(), "svm": SVC(),
              "tree": DecisionTreeClassifier(random_state=0)}
    scores = {k: round(m.fit(Xtr, ytr).score(Xte, yte), 4) for k, m in models.items()}
    best = max(scores, key=scores.get)
    return {"scores": scores, "best": best}


def ref_lr_scratch(lr, epochs):
    X, y = make_moons(n_samples=200, noise=0.2, random_state=0)
    w, b = np.zeros(2), 0.0
    for _ in range(epochs):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        w -= lr * X.T @ (p - y) / len(y)
        b -= lr * (p - y).mean()
    acc = float(((1 / (1 + np.exp(-(X @ w + b))) >= 0.5) == y).mean())
    sk = LogisticRegression().fit(X, y).score(X, y)
    return [round(acc, 3), round(float(sk), 3)]


# ====================================================================== Day 85
day85 = L(
    85, "로지스틱 회귀", W, ["logistic_regression", "sklearn_api"],
    ["시그모이드 함수가 점수를 0~1 확률로 바꾸는 원리를 설명할 수 있다.", "LogisticRegression으로 이진 분류 모델을 학습할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "12주차에는 숫자를 예측하는 회귀를 배웠습니다. 이번 주는 다시 **분류**입니다. 첫 모델 **로지스틱 회귀**는 이름에 \"회귀\"가 있지만 "
        "선형 회귀의 점수를 확률로 바꿔 **분류**하는 모델입니다."),
        "quiz": [quiz("d85_review_q1", "선형 회귀 `w·x + b`의 출력 범위는?", ["0~1", "-1~1", "제한 없음", "0 이상"], 2, "그래서 확률로 쓰려면 변환이 필요합니다.")]},
    concept={"title": "점수를 확률로", "blocks": [
        text("**시그모이드** `σ(z) = 1 / (1 + e^(−z))`는 어떤 숫자든 0~1로 바꿉니다. z가 크면 1에, 작으면 0에 가깝고, z = 0이면 0.5입니다. "
             "로지스틱 회귀는 `z = w·x + b`를 계산해 시그모이드로 \"양성일 확률\"을 만들고, 0.5 이상이면 양성으로 분류합니다."),
        C('''
            import numpy as np

            z = np.array([-5, -1, 0, 1, 5])
            print(np.round(1 / (1 + np.exp(-z)), 3))
        '''),
        text("유방암 데이터는 종양 특성 30개로 악성(0)/양성(1)을 가리는 이진 분류 문제입니다. 특성 크기가 제각각이라 **학습 데이터의 평균·표준편차로 표준화**한 뒤 학습합니다(테스트도 학습 데이터 기준으로 변환)."),
        C('''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split

            X, y = load_breast_cancer(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
            mean, std = X_train.mean(axis=0), X_train.std(axis=0)
            X_train, X_test = (X_train - mean) / std, (X_test - mean) / std
            model = LogisticRegression().fit(X_train, y_train)
            print(round(model.score(X_test, y_test), 4))
            print(model.coef_.shape)
        '''),
        tip("표준화에 테스트 데이터의 평균을 쓰면 시험 정보를 미리 보는 셈(데이터 누수)입니다. 항상 학습 데이터로만 기준을 정하세요."),
    ]},
    fill_intro="시그모이드 함수를 완성하세요.",
    coding_intro="유방암 데이터로 로지스틱 회귀를 학습하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "시그모이드 σ(z) = 1/(1+e^(−z)) → 0~1.",
        "로지스틱 회귀 = 선형 점수 + 시그모이드 → 확률 → 0.5 기준 분류.",
        "`LogisticRegression().fit(X, y)`.",
        "표준화 기준은 학습 데이터로만."],
        "quiz": [
            quiz("d85_summary_q1", "σ(0)의 값은?", ["0", "0.5", "1", "e"], 1, ""),
            quiz("d85_summary_q2", "로지스틱 회귀는 어떤 문제에 쓰나?", ["회귀", "분류", "군집", "압축"], 1, "")]},
    exercises=[
        ex("d85_fill_1", "fill_blank", "시그모이드",
           "점수 목록에 시그모이드를 적용한 값(소수 넷째 자리)을 반환하세요.",
           ["logistic_regression"], 1,
           '''
            import numpy as np


            def sigmoid(zs):
                z = np.array(zs, dtype=float)
                return np.round(1 / (1 + np.____(____)), 4)
           ''',
           [t("t1", args=[[-1, 0, 2]], ret=ref_sigmoid([-1, 0, 2]), desc="기본", **F), t("h1", args=[[10, -10]], ret=ref_sigmoid([10, -10]), **F)],
           ["e의 거듭제곱을 계산하는 NumPy 함수입니다.", "식 1/(1+e^(−z))에서 지수 부분입니다."],
           '''
            import numpy as np


            def sigmoid(zs):
                z = np.array(zs, dtype=float)
                return np.round(1 / (1 + np.exp(-z)), 4)
           ''', mode="function", name="sigmoid", time_limit=TL),
        ex("d85_code_1", "coding", "유방암 분류",
           "유방암 데이터를 `test_size=0.25, random_state=seed, stratify=y`로 나누고, **학습 데이터의 평균·표준편차로** 학습·테스트를 표준화한 뒤 로지스틱 회귀를 학습하세요. "
           "`[특성 수, 테스트 정확도(소수 넷째 자리)]`를 반환합니다.",
           ["logistic_regression", "train_test"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split


            def cancer_accuracy(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_cancer_lr(0), desc="시드 0", **F), t("h1", args=[3], ret=ref_cancer_lr(3), **F)],
           ["나눈 뒤 `X_train.mean(axis=0)`, `X_train.std(axis=0)`를 구하세요.", "학습·테스트 모두 `(X - mean) / std`로 바꿉니다.", "특성 수는 `X_train.shape[1]`."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split


            def cancer_accuracy(seed):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                mean, std = X_train.mean(axis=0), X_train.std(axis=0)
                X_train, X_test = (X_train - mean) / std, (X_test - mean) / std
                model = LogisticRegression().fit(X_train, y_train)
                return [X_train.shape[1], round(model.score(X_test, y_test), 4)]
           ''', mode="function", name="cancer_accuracy", time_limit=TL),
    ])

# ====================================================================== Day 86
SPLIT_HELPER = '''
            def cancer_split(seed):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                mean, std = X_train.mean(axis=0), X_train.std(axis=0)
                return (X_train - mean) / std, (X_test - mean) / std, y_train, y_test
'''
day86 = L(
    86, "확률과 결정 임계값", W, ["decision_boundary", "logistic_regression"],
    ["predict_proba로 클래스별 확률을 얻을 수 있다.", "임계값을 바꾸면 양성 예측 수와 정확도가 어떻게 달라지는지 설명할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 로지스틱 회귀가 시그모이드로 확률을 만든다는 것을 배웠습니다.",
            "quiz": [quiz("d86_review_q1", "로지스틱 회귀의 기본 분류 기준 확률은?", ["0.1", "0.5", "0.9", "1"], 1, "")]},
    concept={"title": "얼마나 확신하나", "blocks": [
        text("`predict_proba(X)`는 샘플마다 각 클래스의 확률을 돌려줍니다(열 순서는 `classes_`). `predict`는 이 확률이 0.5 이상인 쪽을 고른 결과입니다. "
             "임계값을 직접 정하면 \"확실할 때만 양성\"(높은 임계값) 또는 \"조금이라도 의심되면 양성\"(낮은 임계값)처럼 조절할 수 있습니다."),
        C('''
            import numpy as np
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split

            X, y = load_breast_cancer(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
            mean, std = X_train.mean(axis=0), X_train.std(axis=0)
            model = LogisticRegression().fit((X_train - mean) / std, y_train)
            proba = model.predict_proba((X_test - mean) / std)
            print(proba[:3].round(3))
            for th in [0.3, 0.5, 0.9]:
                pred = (proba[:, 1] >= th).astype(int)
                print(th, pred.sum(), round((pred == y_test).mean(), 3))
        '''),
        tip("암 검진처럼 놓치면 위험한 문제는 임계값을 낮춰 양성을 더 많이 잡고, 스팸 필터처럼 잘못 거르면 곤란한 문제는 임계값을 높입니다(14주차 정밀도·재현율)."),
    ]},
    fill_intro="양성 확률이 임계값 이상인 개수를 세세요.",
    coding_intro="임계값별 양성 예측 수와 정확도를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`predict_proba(X)[:, 1]` = 양성(클래스 1) 확률.",
        "`predict`는 임계값 0.5와 같다.",
        "임계값↑ → 양성 예측↓(더 신중), 임계값↓ → 양성 예측↑.",
        "임계값은 문제의 비용에 맞게 정한다."],
        "quiz": [
            quiz("d86_summary_q1", "임계값을 0.5에서 0.9로 올리면 양성 예측 수는?", ["늘어난다", "줄어들거나 같다", "변함없다", "0이 된다"], 1, ""),
            quiz("d86_summary_q2", "`predict_proba`의 각 행 합은?", ["0", "0.5", "1", "클래스 수"], 2, "")]},
    exercises=[
        ex("d86_fill_1", "fill_blank", "임계값 이상 개수",
           "확률 목록에서 임계값 이상인 것의 개수를 반환하세요.",
           ["decision_boundary"], 1,
           '''
            import numpy as np


            def count_positive(probs, threshold):
                p = np.array(probs)
                return int((p ____ threshold).____())
           ''',
           [t("t1", args=[[0.2, 0.5, 0.9], 0.5], ret=2, desc="0.5 기준"), t("h1", args=[[0.1, 0.2], 0.9], ret=0), t("h2", args=[[0.3, 0.6, 0.6], 0.3], ret=3)],
           ["\"이상\"을 나타내는 비교 연산자입니다.", "True의 개수를 세려면 더하면 됩니다."],
           '''
            import numpy as np


            def count_positive(probs, threshold):
                p = np.array(probs)
                return int((p >= threshold).sum())
           ''', mode="function", name="count_positive", time_limit=TL),
        ex("d86_code_1", "coding", "임계값 비교",
           "주어진 `cancer_split(seed)`로 표준화된 데이터를 얻고 로지스틱 회귀를 학습하세요. `thresholds`의 각 임계값마다 "
           "`[양성(1) 예측 개수, 테스트 정확도(소수 넷째 자리)]`를 담은 리스트를 반환합니다.",
           ["decision_boundary", "logistic_regression", "numpy_ops"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
''' + SPLIT_HELPER + '''

            def threshold_report(thresholds, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[0.3, 0.5, 0.9], 0], ret=ref_thresholds([0.3, 0.5, 0.9], 0), desc="세 임계값", **F),
            t("h1", args=[[0.1, 0.99], 2], ret=ref_thresholds([0.1, 0.99], 2), **F)],
           ["양성 확률은 `predict_proba(X_test)[:, 1]`.", "임계값마다 `(확률 >= th).astype(int)`로 예측을 만들고 개수와 `(pred == y_test).mean()`을 구합니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
''' + SPLIT_HELPER + '''

            def threshold_report(thresholds, seed):
                X_train, X_test, y_train, y_test = cancer_split(seed)
                proba = LogisticRegression().fit(X_train, y_train).predict_proba(X_test)[:, 1]
                report = []
                for th in thresholds:
                    pred = (proba >= th).astype(int)
                    report.append([int(pred.sum()), round(float((pred == y_test).mean()), 4)])
                return report
           ''', mode="function", name="threshold_report", time_limit=TL),
    ])

# ====================================================================== Day 87
day87 = L(
    87, "결정 경계", W, ["decision_boundary", "knn", "logistic_regression"],
    ["모델이 특성 공간을 나누는 경계(결정 경계)를 그림으로 이해할 수 있다.", "선형 모델과 비선형 모델의 경계 차이를 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 확률과 임계값으로 분류를 조절했습니다.",
            "quiz": [quiz("d87_review_q1", "양성 확률을 얻는 코드는?", ["`predict(X)`", "`predict_proba(X)[:, 1]`", "`score(X)`", "`coef_`"], 1, "")]},
    concept={"title": "모델은 공간을 나눈다", "blocks": [
        text("특성이 2개면 데이터를 평면에 찍을 수 있고, 모델은 평면을 클래스별 구역으로 나눕니다. 그 경계선이 **결정 경계**입니다. 로지스틱 회귀의 경계는 **직선**, KNN은 구불구불한 곡선입니다."),
        C('''
            import matplotlib.pyplot as plt
            import numpy as np
            from sklearn.datasets import make_moons
            from sklearn.linear_model import LogisticRegression
            from sklearn.neighbors import KNeighborsClassifier

            X, y = make_moons(n_samples=200, noise=0.25, random_state=0)
            xx, yy = np.meshgrid(np.linspace(-1.5, 2.5, 200), np.linspace(-1, 1.5, 200))
            grid = np.c_[xx.ravel(), yy.ravel()]
            fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
            for ax, model in zip(axes, [LogisticRegression(), KNeighborsClassifier(n_neighbors=5)]):
                model.fit(X, y)
                ax.contourf(xx, yy, model.predict(grid).reshape(xx.shape), alpha=0.3)
                ax.scatter(X[:, 0], X[:, 1], c=y, s=12)
                ax.set_title(f"{type(model).__name__} ({model.score(X, y):.2f})")
            print("그림 2개")
        '''),
        tip("`make_moons`는 초승달 두 개가 맞물린 모양의 연습용 데이터를 만듭니다. 직선 하나로는 잘 나눌 수 없어서 선형 모델의 한계를 보기 좋아요."),
    ]},
    fill_intro="초승달 데이터를 만들고 크기를 확인하세요.",
    coding_intro="초승달 데이터에서 선형 모델과 KNN을 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "결정 경계 = 클래스가 바뀌는 경계선.",
        "로지스틱 회귀는 직선(평면) 경계, KNN은 유연한 경계.",
        "`make_moons(n_samples, noise, random_state)`: 비선형 연습 데이터.",
        "`contourf`로 격자 예측을 칠하면 경계가 보인다."],
        "quiz": [
            quiz("d87_summary_q1", "초승달 모양 데이터에 더 유리한 모델은?", ["로지스틱 회귀", "KNN", "둘 다 같다", "선형 회귀"], 1, ""),
            quiz("d87_summary_q2", "특성이 2개일 때 로지스틱 회귀의 결정 경계 모양은?", ["직선", "원", "곡선", "점"], 0, "")]},
    exercises=[
        ex("d87_fill_1", "fill_blank", "초승달 데이터",
           "`make_moons`로 `n`개 샘플(noise=0.2, random_state=0)을 만들어 `[X 모양 리스트, 클래스 1의 개수]`를 반환하세요.",
           ["decision_boundary"], 1,
           '''
            from sklearn.datasets import ____


            def moons_info(n):
                X, y = make_moons(n_samples=____, noise=0.2, random_state=0)
                return [list(X.shape), int(y.sum())]
           ''',
           [t("t1", args=[100], ret=[[100, 2], 50], desc="100개"), t("h1", args=[30], ret=[[30, 2], 15])],
           ["초승달 데이터 생성 함수 이름입니다.", "샘플 수로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import make_moons


            def moons_info(n):
                X, y = make_moons(n_samples=n, noise=0.2, random_state=0)
                return [list(X.shape), int(y.sum())]
           ''', mode="function", name="moons_info", time_limit=TL),
        ex("d87_code_1", "coding", "선형 vs 비선형",
           "`make_moons(n_samples=300, noise=noise, random_state=seed)`로 데이터를 만들고 `test_size=0.3, random_state=seed`로 나눈 뒤, "
           "`LogisticRegression()`과 `KNeighborsClassifier(n_neighbors=5)`의 테스트 정확도(소수 넷째 자리)를 `{\"logistic\": …, \"knn\": …}`로 반환하세요.",
           ["decision_boundary", "knn", "logistic_regression"], 2,
           '''
            from sklearn.datasets import make_moons
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def compare_on_moons(noise, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0.25, 0], ret=ref_moons(0.25, 0), desc="noise 0.25", **F), t("h1", args=[0.1, 5], ret=ref_moons(0.1, 5), **F)],
           ["데이터 생성 → 나누기 → 두 모델 각각 `fit` → `score`.", "딕셔너리 키 이름에 주의하세요."],
           '''
            from sklearn.datasets import make_moons
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def compare_on_moons(noise, seed):
                X, y = make_moons(n_samples=300, noise=noise, random_state=seed)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)
                logistic = LogisticRegression().fit(X_train, y_train).score(X_test, y_test)
                knn = KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train).score(X_test, y_test)
                return {"logistic": round(logistic, 4), "knn": round(knn, 4)}
           ''', mode="function", name="compare_on_moons", time_limit=TL),
    ])

# ====================================================================== Day 88
day88 = L(
    88, "서포트 벡터 머신", W, ["svm", "decision_boundary"],
    ["SVM이 경계와 가장 가까운 점(서포트 벡터) 사이 간격을 넓히는 모델임을 설명할 수 있다.", "커널(linear, rbf)과 C의 역할을 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 결정 경계를 그려 선형·비선형 모델을 비교했습니다.",
            "quiz": [quiz("d88_review_q1", "직선 하나로 나누기 어려운 데이터에서 로지스틱 회귀의 한계는?", ["느리다", "경계가 직선이라 곡선 경계를 못 만든다", "확률을 못 낸다", "학습이 안 된다"], 1, "")]},
    concept={"title": "가장 넓은 길 찾기", "blocks": [
        text("**SVM**은 두 클래스 사이에 가능한 한 **넓은 길(마진)**을 내는 경계를 찾습니다. 길 가장자리에 걸친 점들을 **서포트 벡터**라고 합니다. "
             "**커널**을 쓰면 데이터를 높은 차원으로 옮긴 것처럼 계산해 곡선 경계를 만들 수 있습니다(`rbf`가 대표적). `C`가 크면 학습 데이터를 더 정확히 맞추려 하고(과적합 위험), 작으면 넓은 길을 우선합니다."),
        C('''
            from sklearn.datasets import make_moons
            from sklearn.model_selection import train_test_split
            from sklearn.svm import SVC

            X, y = make_moons(n_samples=300, noise=0.25, random_state=0)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
            for kernel in ["linear", "rbf"]:
                model = SVC(kernel=kernel, C=1.0).fit(X_train, y_train)
                print(kernel, round(model.score(X_test, y_test), 3), model.n_support_.sum())
        '''),
        tip("SVM도 거리를 쓰기 때문에 특성 스케일에 민감합니다. 실제 데이터에서는 표준화 후 사용하세요."),
    ]},
    fill_intro="커널을 지정해 SVM을 학습하세요.",
    coding_intro="커널별 정확도와 서포트 벡터 수를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "SVM: 마진(길)을 최대화하는 경계.",
        "서포트 벡터: 경계를 결정하는 가장자리 점들.",
        "`kernel=\"linear\"` 직선, `\"rbf\"` 곡선 경계.",
        "`C`↑ 학습 데이터에 더 맞춤, `C`↓ 넓은 마진."],
        "quiz": [
            quiz("d88_summary_q1", "곡선 경계를 만들 수 있는 커널은?", ["linear", "rbf", "둘 다 아님", "C"], 1, ""),
            quiz("d88_summary_q2", "`n_support_`가 알려 주는 것은?", ["클래스 수", "클래스별 서포트 벡터 수", "정확도", "특성 수"], 1, "")]},
    exercises=[
        ex("d88_fill_1", "fill_blank", "SVM 학습",
           "초승달 데이터(`n_samples=200, noise=0.2, random_state=0`) 전체로 `SVC(kernel=kernel)`을 학습해 학습 정확도(소수 넷째 자리)를 반환하세요.",
           ["svm"], 1,
           '''
            from sklearn.datasets import make_moons
            from sklearn.svm import ____


            def svm_train_acc(kernel):
                X, y = make_moons(n_samples=200, noise=0.2, random_state=0)
                model = SVC(kernel=____).fit(X, y)
                return round(model.score(X, y), 4)
           ''',
           [t("t1", args=["rbf"], ret=round(SVC(kernel="rbf").fit(*make_moons(n_samples=200, noise=0.2, random_state=0)).score(*make_moons(n_samples=200, noise=0.2, random_state=0)), 4), desc="rbf", **F),
            t("h1", args=["linear"], ret=round(SVC(kernel="linear").fit(*make_moons(n_samples=200, noise=0.2, random_state=0)).score(*make_moons(n_samples=200, noise=0.2, random_state=0)), 4), **F)],
           ["서포트 벡터 분류기 클래스 이름입니다(세 글자).", "커널 이름으로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import make_moons
            from sklearn.svm import SVC


            def svm_train_acc(kernel):
                X, y = make_moons(n_samples=200, noise=0.2, random_state=0)
                model = SVC(kernel=kernel).fit(X, y)
                return round(model.score(X, y), 4)
           ''', mode="function", name="svm_train_acc", time_limit=TL),
        ex("d88_code_1", "coding", "커널 비교",
           "`make_moons(n_samples=300, noise=0.25, random_state=seed)`를 `test_size=0.3, random_state=seed`로 나누고, `linear`와 `rbf` 커널(`C=C`) SVM 각각의 "
           "`[테스트 정확도(소수 넷째 자리), 서포트 벡터 총수]`를 `{\"linear\": […], \"rbf\": […]}`로 반환하세요.",
           ["svm", "decision_boundary"], 2,
           '''
            from sklearn.datasets import make_moons
            from sklearn.model_selection import train_test_split
            from sklearn.svm import SVC


            def kernel_report(C, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[1.0, 0], ret=ref_svm(1.0, 0), desc="C=1", **F), t("h1", args=[10.0, 3], ret=ref_svm(10.0, 3), **F)],
           ["커널 이름 리스트를 돌며 모델을 만드세요.", "서포트 벡터 총수는 `int(model.n_support_.sum())`."],
           '''
            from sklearn.datasets import make_moons
            from sklearn.model_selection import train_test_split
            from sklearn.svm import SVC


            def kernel_report(C, seed):
                X, y = make_moons(n_samples=300, noise=0.25, random_state=seed)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)
                report = {}
                for kernel in ["linear", "rbf"]:
                    model = SVC(kernel=kernel, C=C).fit(X_train, y_train)
                    report[kernel] = [round(model.score(X_test, y_test), 4), int(model.n_support_.sum())]
                return report
           ''', mode="function", name="kernel_report", time_limit=TL),
    ])

# ====================================================================== Day 89
day89 = L(
    89, "나이브 베이즈와 텍스트 분류", W, ["naive_bayes", "sklearn_api"],
    ["CountVectorizer로 문장을 단어 개수 벡터로 바꿀 수 있다.", "MultinomialNB로 간단한 텍스트 분류기를 만들 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 SVM과 커널을 배웠습니다.",
            "quiz": [quiz("d89_review_q1", "SVM에서 경계를 결정하는 점들을 부르는 이름은?", ["이웃", "서포트 벡터", "센트로이드", "이상치"], 1, "")]},
    concept={"title": "글자를 숫자로", "blocks": [
        text("모델은 숫자만 다룹니다. **CountVectorizer**는 모든 문장에 나온 단어로 사전을 만들고, 문장마다 각 단어가 몇 번 나왔는지 세어 숫자 벡터로 바꿉니다(Bag of Words)."),
        C('''
            from sklearn.feature_extraction.text import CountVectorizer

            texts = ["무료 쿠폰 받기", "회의 자료 받기", "무료 무료 이벤트"]
            vec = CountVectorizer()
            X = vec.fit_transform(texts)
            print(sorted(vec.vocabulary_))
            print(X.toarray())
        '''),
        text("**나이브 베이즈**는 \"스팸 메일에는 '무료'가 자주 나온다\" 같은 단어별 확률을 세어 두었다가, 새 문장의 단어들로 각 클래스일 확률을 계산합니다. 빠르고 텍스트에 잘 맞습니다."),
        C('''
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.naive_bayes import MultinomialNB

            texts = ["무료 쿠폰 받기", "회의 자료 받기", "당첨 무료 이벤트", "점심 회의 시간"]
            labels = ["스팸", "정상", "스팸", "정상"]
            vec = CountVectorizer()
            model = MultinomialNB().fit(vec.fit_transform(texts), labels)
            print(model.predict(vec.transform(["무료 당첨 쿠폰", "회의 시간 확인"])))
        '''),
        tip("새 문장은 반드시 학습 때 만든 사전으로 `transform`만 합니다. 사전에 없던 단어는 무시됩니다. 한국어는 조사가 붙어 단어가 달라지기 쉬워서, 실무에서는 형태소 분석기로 먼저 나눕니다."),
    ]},
    fill_intro="문장들의 단어 사전 크기를 구하세요.",
    coding_intro="주어진 학습 문장으로 스팸 분류기를 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`CountVectorizer`: 문장 → 단어 개수 벡터, `vocabulary_`가 사전.",
        "학습 문장은 `fit_transform`, 새 문장은 `transform`.",
        "`MultinomialNB`: 단어 확률 기반 분류, 텍스트에 강함.",
        "모델은 숫자만 다룬다 → 텍스트는 벡터화가 먼저."],
        "quiz": [
            quiz("d89_summary_q1", "학습 때 없던 단어가 새 문장에 있으면?", ["오류", "무시된다", "사전에 추가된다", "스팸으로 분류"], 1, ""),
            quiz("d89_summary_q2", "Bag of Words가 잃어버리는 정보는?", ["단어 개수", "단어 순서", "단어 종류", "문장 수"], 1, "")]},
    exercises=[
        ex("d89_fill_1", "fill_blank", "단어 사전",
           "문장 목록으로 CountVectorizer를 학습해 사전의 단어 수를 반환하세요.",
           ["naive_bayes"], 1,
           '''
            from sklearn.feature_extraction.text import ____


            def vocab_size(texts):
                vec = CountVectorizer()
                vec.____(texts)
                return len(vec.vocabulary_)
           ''',
           [t("t1", args=[["apple banana", "banana cherry"]], ret=3, desc="기본"), t("h1", args=[["hello hello", "world"]], ret=2)],
           ["단어 개수 벡터를 만드는 클래스 이름입니다.", "사전을 만드는 학습 메서드입니다."],
           '''
            from sklearn.feature_extraction.text import CountVectorizer


            def vocab_size(texts):
                vec = CountVectorizer()
                vec.fit(texts)
                return len(vec.vocabulary_)
           ''', mode="function", name="vocab_size", time_limit=TL),
        ex("d89_code_1", "coding", "스팸 분류기",
           "주어진 `TRAIN_TEXTS`, `TRAIN_LABELS`로 CountVectorizer + MultinomialNB를 학습하고, `texts`의 예측 결과를 구하세요. "
           "`[사전 단어 수, 예측 리스트]`를 반환합니다.",
           ["naive_bayes", "sklearn_api"], 2,
           '''
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.naive_bayes import MultinomialNB

            TRAIN_TEXTS = ["무료 쿠폰 지금 받기", "오늘 회의 몇 시에 할까요", "당첨 축하 무료 상품 받기", "점심 같이 먹어요",
                           "지금 클릭 무료 이벤트", "내일 수업 자료 보내 드려요", "특가 할인 쿠폰 당첨", "회의 자료 확인 부탁드려요"]
            TRAIN_LABELS = ["스팸", "정상", "스팸", "정상", "스팸", "정상", "스팸", "정상"]


            def classify(texts):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[["무료 쿠폰 당첨", "회의 자료 보내 드려요"]], ret=ref_spam(["무료 쿠폰 당첨", "회의 자료 보내 드려요"]), desc="두 문장"),
            t("h1", args=[["지금 할인 이벤트 클릭", "점심 먹어요", "처음 보는 단어"]], ret=ref_spam(["지금 할인 이벤트 클릭", "점심 먹어요", "처음 보는 단어"]))],
           ["`vec.fit_transform(TRAIN_TEXTS)`로 학습 행렬을 만들고 `MultinomialNB().fit(..., TRAIN_LABELS)`.",
            "예측은 `model.predict(vec.transform(texts))`이고 `.tolist()`로 바꿉니다."],
           '''
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.naive_bayes import MultinomialNB

            TRAIN_TEXTS = ["무료 쿠폰 지금 받기", "오늘 회의 몇 시에 할까요", "당첨 축하 무료 상품 받기", "점심 같이 먹어요",
                           "지금 클릭 무료 이벤트", "내일 수업 자료 보내 드려요", "특가 할인 쿠폰 당첨", "회의 자료 확인 부탁드려요"]
            TRAIN_LABELS = ["스팸", "정상", "스팸", "정상", "스팸", "정상", "스팸", "정상"]


            def classify(texts):
                vec = CountVectorizer()
                model = MultinomialNB().fit(vec.fit_transform(TRAIN_TEXTS), TRAIN_LABELS)
                predictions = model.predict(vec.transform(texts))
                return [len(vec.vocabulary_), predictions.tolist()]
           ''', mode="function", name="classify", time_limit=TL),
    ])

# ====================================================================== Day 90
day90 = L(
    90, "다중 분류", W, ["multiclass", "knn", "dataset"],
    ["클래스가 3개 이상인 문제를 학습하고 클래스별 성능을 확인할 수 있다.", "손글씨 숫자(digits) 이미지를 특성 벡터로 다룰 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 텍스트를 벡터로 바꿔 나이브 베이즈로 분류했습니다.",
            "quiz": [quiz("d90_review_q1", "새 문장을 벡터로 바꿀 때 쓰는 메서드는?", ["`fit`", "`fit_transform`", "`transform`", "`predict`"], 2, "")]},
    concept={"title": "0~9 손글씨 숫자", "blocks": [
        text("**digits** 데이터는 8×8 픽셀 흑백 손글씨 숫자 1797장입니다. 이미지 한 장을 픽셀 64개짜리 벡터로 펼쳐 특성으로 씁니다. 정답은 0~9 열 가지(다중 분류)입니다."),
        C('''
            import matplotlib.pyplot as plt
            from sklearn.datasets import load_digits

            digits = load_digits()
            print(digits.images.shape, digits.data.shape)
            print(digits.images[0].astype(int))
            fig, axes = plt.subplots(1, 5, figsize=(8, 2))
            for ax, img, label in zip(axes, digits.images, digits.target):
                ax.imshow(img, cmap="gray_r")
                ax.set_title(label)
                ax.axis("off")
        '''),
        text("scikit-learn 분류 모델은 다중 분류를 자동으로 지원합니다. 전체 정확도와 함께 **어떤 숫자를 자주 틀리는지** 보면 모델을 이해하는 데 도움이 됩니다."),
        tip("다중 분류의 혼동 행렬(다음 주)을 보면 \"8을 3으로 착각\" 같은 패턴이 드러납니다. 4단계에서는 같은 문제를 CNN으로 풉니다."),
    ]},
    fill_intro="digits 데이터의 구조를 확인하세요.",
    coding_intro="KNN으로 숫자를 분류하고 가장 약한 숫자를 찾으세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "이미지 → 픽셀 벡터로 펼쳐 특성으로.",
        "`load_digits()`: 8×8 이미지, 64 특성, 10 클래스.",
        "분류 모델은 다중 분류를 자동 지원.",
        "클래스별 정확도로 약점을 찾는다."],
        "quiz": [
            quiz("d90_summary_q1", "8×8 이미지를 펼친 특성 수는?", ["8", "16", "64", "10"], 2, ""),
            quiz("d90_summary_q2", "digits의 클래스 수는?", ["2", "8", "10", "64"], 2, "")]},
    exercises=[
        ex("d90_fill_1", "fill_blank", "digits 구조",
           "digits 데이터의 `[이미지 모양 리스트(전체), 특성 수, 클래스 수]`를 반환하세요.",
           ["multiclass", "dataset"], 1,
           '''
            from sklearn.datasets import load_digits


            def digits_info():
                d = ____()
                return [list(d.images.shape), d.data.shape[1], len(d.____)]
           ''',
           [t("t1", args=[], ret=[[1797, 8, 8], 64, 10], desc="digits")],
           ["digits 데이터셋을 불러오는 함수입니다.", "클래스 이름 목록이 담긴 속성입니다(target_…)."],
           '''
            from sklearn.datasets import load_digits


            def digits_info():
                d = load_digits()
                return [list(d.images.shape), d.data.shape[1], len(d.target_names)]
           ''', mode="function", name="digits_info", time_limit=TL),
        ex("d90_code_1", "coding", "가장 약한 숫자",
           "digits를 `test_size=0.25, random_state=seed, stratify=y`로 나누고 KNN(이웃 `k`개)을 학습하세요. "
           "`[테스트 정확도(소수 넷째 자리), 클래스별 정확도가 가장 낮은 숫자]`를 반환합니다(동률이면 작은 숫자).",
           ["multiclass", "knn", "numpy_indexing"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_digits
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def weakest_digit(k, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[3, 0], ret=ref_digits(3, 0), desc="k=3", **F), t("h1", args=[1, 4], ret=ref_digits(1, 4), **F)],
           ["예측 `pred`를 구한 뒤 숫자 d마다 `(pred[y_test == d] == d).mean()`.", "가장 낮은 위치는 `np.argmin(목록)`."],
           '''
            import numpy as np
            from sklearn.datasets import load_digits
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def weakest_digit(k, seed):
                X, y = load_digits(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                pred = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train).predict(X_test)
                per_digit = [float((pred[y_test == d] == d).mean()) for d in range(10)]
                return [round(float((pred == y_test).mean()), 4), int(np.argmin(per_digit))]
           ''', mode="function", name="weakest_digit", time_limit=TL),
    ])

# ====================================================================== Day 91 (review)
day91 = L(
    91, "13주차 누적 복습", W, ["logistic_regression", "decision_boundary", "svm", "naive_bayes", "multiclass"],
    ["여러 분류 모델을 같은 데이터에서 비교하고 가장 좋은 모델을 고를 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 85 | 로지스틱 회귀 | 시그모이드, 확률 |\n| 86 | 임계값 | `predict_proba`, 기준 조절 |\n"
        "| 87 | 결정 경계 | 선형 vs 비선형 |\n| 88 | SVM | 마진, 커널, C |\n"
        "| 89 | 나이브 베이즈 | CountVectorizer, 텍스트 |\n| 90 | 다중 분류 | digits, 클래스별 정확도 |"),
        "quiz": [
            quiz("d91_review_q1", "텍스트 분류에 특히 자주 쓰는 빠른 모델은?", ["SVM rbf", "나이브 베이즈", "KNN", "선형 회귀"], 1, ""),
            quiz("d91_review_q2", "모델을 비교할 때 지켜야 할 것은?", ["모델마다 다른 분할", "같은 분할·같은 지표", "학습 정확도만 비교", "가장 최신 모델 선택"], 1, "")]},
    concept={"title": "로지스틱 회귀의 학습", "blocks": [
        text("로지스틱 회귀도 경사하강법으로 학습합니다. 손실은 **로그 손실**(교차 엔트로피)이고, 기울기는 선형 회귀와 거의 같은 모양입니다: "
             "`dw = Xᵀ(p − y) / n`, `db = 평균(p − y)` (p는 시그모이드 확률). 4단계 신경망의 마지막 층이 바로 이 구조입니다."),
        C('''
            import numpy as np

            X = np.array([[0.0], [1.0], [2.0], [3.0]])
            y = np.array([0, 0, 1, 1])
            w, b = np.zeros(1), 0.0
            for _ in range(2000):
                p = 1 / (1 + np.exp(-(X @ w + b)))
                w -= 0.5 * X.T @ (p - y) / len(y)
                b -= 0.5 * (p - y).mean()
            print(np.round(1 / (1 + np.exp(-(X @ w + b))), 2))
        '''),
        tip("도전 문제에서 직접 만든 모델과 scikit-learn의 결과를 비교해 보세요. scikit-learn은 기본으로 약한 규제(L2)가 걸려 있어 숫자가 조금 다를 수 있습니다."),
    ]},
    fill_intro="여러 모델을 한 줄씩 비교할 준비를 하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "13주차 마무리", "points": [
        "분류 모델: 로지스틱 회귀, KNN, SVM, 나이브 베이즈, (다음 주 트리).",
        "확률·임계값으로 결정을 조절한다.",
        "비교는 같은 조건에서.",
        "다음 주: 정확도 너머의 평가(혼동 행렬, 정밀도·재현율, 교차 검증)."],
        "quiz": [
            quiz("d91_summary_q1", "로지스틱 회귀의 손실 함수는?", ["MSE", "로그 손실(교차 엔트로피)", "MAE", "정확도"], 1, ""),
            quiz("d91_summary_q2", "다음 주에 배울, 정확도 외의 평가 도구는?", ["혼동 행렬", "PCA", "KMeans", "CountVectorizer"], 0, "")]},
    is_review=True,
    exercises=[
        ex("d91_fill_1", "fill_blank", "모델 이름 목록",
           "모델 객체 리스트를 받아 각 모델의 **클래스 이름** 리스트를 반환하세요. `check`가 모델을 만들어 넘깁니다.",
           ["sklearn_api"], 1,
           '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC


            def model_names(models):
                return [____(m).____ for m in models]


            def check():
                return model_names([LogisticRegression(), SVC()])
           ''',
           [t("t1", args=[], ret=["LogisticRegression", "SVC"], desc="두 모델")],
           ["객체의 클래스를 알려 주는 내장 함수입니다.", "클래스의 이름을 담은 특수 속성입니다(양쪽 밑줄)."],
           '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC


            def model_names(models):
                return [type(m).__name__ for m in models]


            def check():
                return model_names([LogisticRegression(), SVC()])
           ''', mode="function", name="check", time_limit=TL),
        ex("d91_code_1", "coding", "분류 모델 대결",
           "주어진 `cancer_split(seed)`로 표준화된 유방암 데이터를 얻고, `LogisticRegression()`, `KNeighborsClassifier()`, `SVC()`, `DecisionTreeClassifier(random_state=0)`의 "
           "테스트 정확도(소수 넷째 자리)를 `{\"logistic\", \"knn\", \"svm\", \"tree\"}` 키로 모은 `scores`와 가장 높은 모델 이름 `best`(동률이면 앞 순서)를 반환하세요.",
           ["logistic_regression", "svm", "knn", "sklearn_api"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.svm import SVC
            from sklearn.tree import DecisionTreeClassifier
''' + SPLIT_HELPER + '''

            def battle(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_compare(0), desc="시드 0", **F), t("h1", args=[1], ret=ref_compare(1), **F)],
           ["이름 → 모델 딕셔너리를 위 순서대로 만들고 돌면서 점수를 기록하세요.", "`max(scores, key=scores.get)`은 값이 가장 큰 첫 키를 돌려줍니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.svm import SVC
            from sklearn.tree import DecisionTreeClassifier
''' + SPLIT_HELPER + '''

            def battle(seed):
                X_train, X_test, y_train, y_test = cancer_split(seed)
                models = {"logistic": LogisticRegression(), "knn": KNeighborsClassifier(), "svm": SVC(),
                          "tree": DecisionTreeClassifier(random_state=0)}
                scores = {}
                for name, model in models.items():
                    scores[name] = round(model.fit(X_train, y_train).score(X_test, y_test), 4)
                return {"scores": scores, "best": max(scores, key=scores.get)}
           ''', mode="function", name="battle", time_limit=TL),
        ex("d91_code_2", "coding", "[도전] 로지스틱 회귀 직접 학습",
           "`make_moons(n_samples=200, noise=0.2, random_state=0)` 데이터에 대해 w = 0 벡터, b = 0에서 시작해 `epochs`번 경사하강법(`dw = Xᵀ(p − y)/n`, `db = 평균(p − y)`)을 하세요. "
           "`[내 모델의 학습 정확도(확률 0.5 이상을 1로), LogisticRegression의 학습 정확도]`(소수 셋째 자리)를 반환합니다.",
           ["logistic_regression", "gradient_descent", "numpy_reshape"], 3,
           '''
            import numpy as np
            from sklearn.datasets import make_moons
            from sklearn.linear_model import LogisticRegression


            def lr_from_scratch(lr, epochs):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0.5, 1000], ret=ref_lr_scratch(0.5, 1000), desc="lr 0.5", **F), t("h1", args=[0.1, 300], ret=ref_lr_scratch(0.1, 300), **F)],
           ["확률 p는 선형 점수 `X @ w + b`에 Day 85의 시그모이드를 씌운 값입니다.", "문제의 기울기 식을 그대로 코드로 옮겨 w, b에서 학습률만큼 빼세요. `X.T @ (p - y)`가 행렬 곱 부분입니다.",
            "학습 후 다시 확률을 계산해 `>= 0.5`와 `y`를 비교합니다."],
           '''
            import numpy as np
            from sklearn.datasets import make_moons
            from sklearn.linear_model import LogisticRegression


            def lr_from_scratch(lr, epochs):
                X, y = make_moons(n_samples=200, noise=0.2, random_state=0)
                w = np.zeros(2)
                b = 0.0
                for _ in range(epochs):
                    p = 1 / (1 + np.exp(-(X @ w + b)))
                    w -= lr * X.T @ (p - y) / len(y)
                    b -= lr * (p - y).mean()
                final = 1 / (1 + np.exp(-(X @ w + b)))
                mine = float(((final >= 0.5) == y).mean())
                sk = LogisticRegression().fit(X, y).score(X, y)
                return [round(mine, 3), round(float(sk), 3)]
           ''', mode="function", name="lr_from_scratch", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day85, day86, day87, day88, day89, day90, day91])
