"""Week 15 (Day 99-105): 결정 트리와 앙상블."""
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 15, "ml", 60
F = {"compare": {"mode": "float", "tol": 1e-6}}


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


def cancer(seed):
    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)


# ---------------------------------------------------------------- references
def ref_tree(depth, seed):
    iris = load_iris()
    Xtr, Xte, ytr, yte = train_test_split(iris.data, iris.target, test_size=0.3, random_state=seed, stratify=iris.target)
    m = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(Xtr, ytr)
    root = iris.feature_names[m.tree_.feature[0]]
    return [int(m.get_depth()), int(m.get_n_leaves()), round(m.score(Xte, yte), 4), root]


def gini(labels):
    labels = np.array(labels)
    if len(labels) == 0:
        return 0.0
    p = np.bincount(labels) / len(labels)
    return float(1 - (p ** 2).sum())


def entropy(labels):
    labels = np.array(labels)
    p = np.bincount(labels) / len(labels)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def ref_best_split(xs, ys):
    xs, ys = np.array(xs, float), np.array(ys)
    best = None
    for th in sorted(set(xs.tolist()))[:-1]:
        left, right = ys[xs <= th], ys[xs > th]
        w = (len(left) * gini(left) + len(right) * gini(right)) / len(ys)
        if best is None or w < best[1] - 1e-12:
            best = (th, w)
    return [best[0], round(best[1], 4)]


def ref_forest(ns, seed):
    Xtr, Xte, ytr, yte = cancer(seed)
    tree = DecisionTreeClassifier(random_state=0).fit(Xtr, ytr).score(Xte, yte)
    return [round(tree, 4), [round(RandomForestClassifier(n_estimators=n, random_state=0).fit(Xtr, ytr).score(Xte, yte), 4) for n in ns]]


def ref_boost(lrs, seed):
    Xtr, Xte, ytr, yte = cancer(seed)
    return [round(GradientBoostingClassifier(learning_rate=lr, n_estimators=50, random_state=0).fit(Xtr, ytr).score(Xte, yte), 4) for lr in lrs]


def ref_importance(k):
    data = load_breast_cancer()
    m = RandomForestClassifier(n_estimators=100, random_state=0).fit(data.data, data.target)
    order = np.argsort(m.feature_importances_)[::-1][:k]
    return [[str(data.feature_names[i]), round(float(m.feature_importances_[i]), 4)] for i in order]


def ref_perm(seed):
    data = load_wine()
    Xtr, Xte, ytr, yte = train_test_split(data.data, data.target, test_size=0.3, random_state=seed, stratify=data.target)
    m = RandomForestClassifier(n_estimators=100, random_state=0).fit(Xtr, ytr)
    r = permutation_importance(m, Xte, yte, n_repeats=5, random_state=0)
    return str(data.feature_names[int(np.argmax(r.importances_mean))])


def wine_split(seed):
    X, y = load_wine(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    mean, std = Xtr.mean(axis=0), Xtr.std(axis=0)
    return (Xtr - mean) / std, (Xte - mean) / std, ytr, yte


def ref_voting(voting, seed):
    Xtr, Xte, ytr, yte = wine_split(seed)
    members = [("lr", LogisticRegression()), ("knn", KNeighborsClassifier()), ("tree", DecisionTreeClassifier(random_state=0))]
    scores = {n: round(m.fit(Xtr, ytr).score(Xte, yte), 4) for n, m in members}
    scores["vote"] = round(VotingClassifier(members, voting=voting).fit(Xtr, ytr).score(Xte, yte), 4)
    return scores


def ref_cv_trees(folds):
    X, y = load_breast_cancer(return_X_y=True)
    models = {"tree": DecisionTreeClassifier(max_depth=4, random_state=0),
              "forest": RandomForestClassifier(n_estimators=100, random_state=0),
              "boost": GradientBoostingClassifier(random_state=0)}
    scores = {k: round(float(cross_val_score(m, X, y, cv=folds).mean()), 4) for k, m in models.items()}
    return {"scores": scores, "best": max(scores, key=scores.get)}


def ref_best_split_2d(X, y):
    X, y = np.array(X, float), np.array(y)
    best = None
    for f in range(X.shape[1]):
        for th in sorted(set(X[:, f].tolist()))[:-1]:
            left, right = y[X[:, f] <= th], y[X[:, f] > th]
            w = (len(left) * gini(left) + len(right) * gini(right)) / len(y)
            if best is None or w < best[2] - 1e-12:
                best = (f, th, w)
    return [best[0], best[1], round(best[2], 4)]


# ====================================================================== Day 99
day99 = L(
    99, "결정 트리", W, ["decision_tree", "sklearn_api"],
    ["결정 트리가 \"질문\"을 반복해 데이터를 나누는 모델임을 설명할 수 있다.", "트리의 깊이·잎 수·첫 질문을 확인하고 export_text로 규칙을 읽을 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "14주차에는 모델을 제대로 평가하는 법을 배웠습니다. 이번 주는 실무에서 가장 많이 쓰이는 모델 계열인 **트리와 앙상블**입니다. 결정 트리는 Day 96에서 잠깐 써 봤죠."),
        "quiz": [quiz("d99_review_q1", "결정 트리의 깊이를 제한하지 않으면 생기기 쉬운 문제는?", ["과소적합", "과적합", "학습 불가", "정확도 0"], 1, "")]},
    concept={"title": "스무고개처럼 나누기", "blocks": [
        text("결정 트리는 \"꽃잎 길이 ≤ 2.45cm?\" 같은 **예/아니오 질문**으로 데이터를 둘씩 나누는 일을 반복합니다. 더 나눌 필요가 없는 끝 칸(**잎**)에 도달하면 그 칸의 다수 클래스로 예측합니다. "
             "규칙을 사람이 그대로 읽을 수 있다는 것이 큰 장점입니다."),
        C('''
            from sklearn.datasets import load_iris
            from sklearn.tree import DecisionTreeClassifier, export_text

            iris = load_iris()
            model = DecisionTreeClassifier(max_depth=2, random_state=0).fit(iris.data, iris.target)
            print(export_text(model, feature_names=iris.feature_names))
            print(model.get_depth(), model.get_n_leaves())
        '''),
        tip("트리는 특성의 크기(단위)에 영향을 받지 않아 **스케일링이 필요 없습니다**. 대신 깊어질수록 과적합되기 쉬워 `max_depth`, `min_samples_leaf` 등으로 제한합니다."),
    ]},
    fill_intro="깊이를 제한한 트리를 학습하세요.",
    coding_intro="트리의 구조와 첫 질문을 확인하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "결정 트리 = 예/아니오 질문의 연속, 잎에서 다수결.",
        "`export_text`로 규칙을 글로 읽기.",
        "`get_depth()`, `get_n_leaves()`로 구조 확인.",
        "스케일링 불필요, 깊이 제한으로 과적합 방지."],
        "quiz": [
            quiz("d99_summary_q1", "깊이 2인 이진 트리의 잎은 최대 몇 개?", ["2", "3", "4", "8"], 2, ""),
            quiz("d99_summary_q2", "결정 트리의 장점은?", ["스케일링 필수", "규칙을 사람이 읽을 수 있다", "항상 가장 정확하다", "과적합이 없다"], 1, "")]},
    exercises=[
        ex("d99_fill_1", "fill_blank", "깊이 제한 트리",
           "iris 전체로 `max_depth=depth`, `random_state=0` 결정 트리를 학습해 `[깊이, 잎 수]`를 반환하세요.",
           ["decision_tree"], 1,
           '''
            from sklearn.datasets import load_iris
            from sklearn.tree import ____


            def tree_shape(depth):
                X, y = load_iris(return_X_y=True)
                model = DecisionTreeClassifier(max_depth=____, random_state=0).fit(X, y)
                return [int(model.get_depth()), int(model.get_n_leaves())]
           ''',
           [t("t1", args=[2], ret=[2, 3], desc="깊이 2"), t("h1", args=[1], ret=[1, 2])],
           ["결정 트리 분류기 클래스 이름입니다.", "깊이 제한으로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.tree import DecisionTreeClassifier


            def tree_shape(depth):
                X, y = load_iris(return_X_y=True)
                model = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X, y)
                return [int(model.get_depth()), int(model.get_n_leaves())]
           ''', mode="function", name="tree_shape", time_limit=TL),
        ex("d99_code_1", "coding", "트리 해부",
           "iris를 `test_size=0.3, random_state=seed, stratify=y`로 나누고 `max_depth=depth`, `random_state=0` 트리를 학습하세요. "
           "`[깊이, 잎 수, 테스트 정확도(소수 넷째 자리), 첫 질문(뿌리)에 쓰인 특성 이름]`을 반환합니다. 뿌리 특성 번호는 `model.tree_.feature[0]`입니다.",
           ["decision_tree", "dataset"], 2,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier


            def inspect_tree(depth, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[3, 0], ret=ref_tree(3, 0), desc="깊이 3", **F), t("h1", args=[None, 2], ret=ref_tree(None, 2), **F)],
           ["`iris = load_iris()`로 특성 이름까지 받아 두세요.", "특성 이름은 `iris.feature_names[번호]`."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier


            def inspect_tree(depth, seed):
                iris = load_iris()
                X_train, X_test, y_train, y_test = train_test_split(
                    iris.data, iris.target, test_size=0.3, random_state=seed, stratify=iris.target
                )
                model = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
                root = iris.feature_names[model.tree_.feature[0]]
                return [int(model.get_depth()), int(model.get_n_leaves()), round(model.score(X_test, y_test), 4), root]
           ''', mode="function", name="inspect_tree", time_limit=TL),
    ])

# ====================================================================== Day 100
split_cases = [(([1, 2, 3, 4, 5, 6], [0, 0, 0, 1, 1, 1]), "t1", "깔끔한 경계"), (([3, 1, 2, 5, 4], [1, 0, 0, 1, 0]), "h1", ""),
               (([1, 2, 3, 4], [0, 1, 0, 1]), "h2", "")]
day100 = L(
    100, "불순도 계산", W, ["impurity", "decision_tree"],
    ["지니 불순도와 엔트로피를 계산할 수 있다.", "트리가 불순도를 가장 많이 줄이는 질문을 고르는 원리를 구현할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 결정 트리가 질문을 반복해 데이터를 나누는 것을 봤습니다. 질문은 어떻게 고를까요?",
            "quiz": [quiz("d100_review_q1", "트리의 끝 칸(예측이 정해지는 곳)을 부르는 이름은?", ["뿌리", "잎", "가지", "노드 0"], 1, "")]},
    concept={"title": "얼마나 섞여 있나", "blocks": [
        text("**지니 불순도** = 1 − Σ pᵢ² (pᵢ: 클래스 비율). 한 클래스만 있으면 0, 반반 섞이면 0.5입니다. **엔트로피** = −Σ pᵢ log₂ pᵢ 도 비슷한 \"섞임 정도\"입니다. "
             "트리는 나눈 뒤 두 칸의 불순도를 **샘플 수로 가중 평균**한 값이 가장 작아지는 질문을 고릅니다."),
        C('''
            import numpy as np

            def gini(labels):
                p = np.bincount(labels) / len(labels)
                return 1 - (p ** 2).sum()

            print(gini(np.array([0, 0, 0, 0])), gini(np.array([0, 0, 1, 1])), round(gini(np.array([0, 1, 2])), 4))
            y = np.array([0, 0, 0, 1, 1, 1])
            x = np.array([1, 2, 3, 4, 5, 6])
            for th in [2, 3, 4]:
                left, right = y[x <= th], y[x > th]
                weighted = (len(left) * gini(left) + len(right) * gini(right)) / len(y)
                print(th, round(weighted, 4))
        '''),
        tip("scikit-learn 트리는 기본으로 지니를 쓰고, `criterion=\"entropy\"`로 바꿀 수 있습니다. 둘의 결과는 대부분 비슷합니다."),
    ]},
    fill_intro="지니 불순도를 계산하세요.",
    coding_intro="한 특성에서 가장 좋은 분할 기준값을 찾으세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "지니 = 1 − Σp², 순수하면 0.",
        "엔트로피 = −Σ p log₂ p.",
        "분할 평가 = 왼쪽·오른쪽 불순도의 샘플 수 가중 평균.",
        "트리는 이 값을 가장 작게 만드는 질문을 고른다."],
        "quiz": [
            quiz("d100_summary_q1", "레이블 [0, 0, 1, 1]의 지니 불순도는?", ["0", "0.25", "0.5", "1"], 2, ""),
            quiz("d100_summary_q2", "한 클래스만 있는 칸의 엔트로피는?", ["0", "0.5", "1", "무한대"], 0, "")]},
    exercises=[
        ex("d100_fill_1", "fill_blank", "지니 불순도",
           "정수 레이블 목록의 지니 불순도(소수 넷째 자리)를 반환하세요.",
           ["impurity"], 1,
           '''
            import numpy as np


            def gini(labels):
                labels = np.array(labels)
                p = np.____(labels) / len(labels)
                return round(float(1 - (p ____ 2).sum()), 4)
           ''',
           [t("t1", args=[[0, 0, 1, 1]], ret=0.5, desc="반반"), t("h1", args=[[2, 2, 2]], ret=0.0), t("h2", args=[[0, 1, 2]], ret=round(gini([0, 1, 2]), 4), **F)],
           ["값별 개수를 세는 NumPy 함수입니다(Day 55).", "제곱 연산자입니다."],
           '''
            import numpy as np


            def gini(labels):
                labels = np.array(labels)
                p = np.bincount(labels) / len(labels)
                return round(float(1 - (p ** 2).sum()), 4)
           ''', mode="function", name="gini", time_limit=TL),
        ex("d100_code_1", "coding", "최적 분할 찾기",
           "특성 값 `xs`와 레이블 `ys`를 받아, `x <= 기준값`으로 나눌 때 가중 지니가 가장 작은 기준값을 찾으세요. 후보는 서로 다른 x 값 중 **가장 큰 값을 뺀** 값들이고, "
           "동점이면 작은 기준값입니다. `[기준값, 가중 지니(소수 넷째 자리)]`를 반환합니다.",
           ["impurity", "decision_tree", "numpy_indexing"], 3,
           '''
            import numpy as np


            def best_split(xs, ys):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_best_split(*a), desc=d, **F) for a, tid, d in split_cases],
           ["지니 함수를 하나 만들어 두세요(빈 목록이면 0).", "후보는 `sorted(set(xs))[:-1]`. 기준마다 `ys[x <= th]`, `ys[x > th]`로 나눕니다.",
            "가중 지니가 지금까지의 최솟값보다 **작을 때만** 바꾸면 동점에서 작은 기준값이 남습니다."],
           '''
            import numpy as np


            def gini(labels):
                if len(labels) == 0:
                    return 0.0
                p = np.bincount(labels) / len(labels)
                return 1 - (p ** 2).sum()


            def best_split(xs, ys):
                x = np.array(xs, dtype=float)
                y = np.array(ys)
                best_th, best_score = None, None
                for th in sorted(set(x.tolist()))[:-1]:
                    left, right = y[x <= th], y[x > th]
                    score = (len(left) * gini(left) + len(right) * gini(right)) / len(y)
                    if best_score is None or score < best_score:
                        best_th, best_score = th, score
                return [best_th, round(float(best_score), 4)]
           ''', mode="function", name="best_split", time_limit=TL),
    ])

# ====================================================================== Day 101
day101 = L(
    101, "랜덤 포레스트", W, ["random_forest", "ensemble"],
    ["여러 트리의 투표로 예측하는 랜덤 포레스트의 원리를 설명할 수 있다.", "트리 개수에 따른 성능 변화를 단일 트리와 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 트리가 불순도를 줄이는 질문을 고르는 원리를 구현했습니다.",
            "quiz": [quiz("d101_review_q1", "단일 결정 트리의 약점은?", ["느리다", "작은 데이터 변화에도 구조가 크게 바뀌고 과적합되기 쉽다", "확률을 못 낸다", "숫자 특성 불가"], 1, "")]},
    concept={"title": "숲은 나무보다 현명하다", "blocks": [
        text("**랜덤 포레스트**는 ① 데이터를 무작위로 다시 뽑고(부트스트랩) ② 각 질문마다 특성도 일부만 무작위로 고려해 서로 조금씩 다른 트리를 많이 만든 뒤, **투표**로 예측합니다. "
             "개별 트리의 실수가 서로 상쇄되어 단일 트리보다 안정적이고 정확합니다."),
        C('''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier

            X, y = load_breast_cancer(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            print("tree", round(DecisionTreeClassifier(random_state=0).fit(X_train, y_train).score(X_test, y_test), 4))
            for n in [1, 10, 100]:
                forest = RandomForestClassifier(n_estimators=n, random_state=0).fit(X_train, y_train)
                print(n, round(forest.score(X_test, y_test), 4))
        '''),
        tip("트리 수(`n_estimators`)를 늘리면 대체로 좋아지다가 어느 순간 수렴합니다. 과적합 걱정은 적지만 학습·예측 시간이 늘어납니다."),
    ]},
    fill_intro="랜덤 포레스트를 학습하세요.",
    coding_intro="단일 트리와 트리 수별 포레스트를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "랜덤 포레스트 = 무작위로 다양화한 트리들의 투표.",
        "부트스트랩 샘플 + 질문마다 무작위 특성 일부.",
        "`RandomForestClassifier(n_estimators, random_state)`.",
        "단일 트리보다 안정적이고 과적합에 강하다."],
        "quiz": [
            quiz("d101_summary_q1", "랜덤 포레스트가 예측을 합치는 방법(분류)은?", ["평균", "투표", "최댓값", "곱"], 1, ""),
            quiz("d101_summary_q2", "트리를 무작위로 다양하게 만드는 이유는?", ["속도", "서로 다른 실수를 하게 해 투표로 상쇄하려고", "메모리 절약", "규칙을 읽기 쉽게"], 1, "")]},
    exercises=[
        ex("d101_fill_1", "fill_blank", "포레스트 학습",
           "유방암 데이터를 `test_size=0.3, random_state=0, stratify=y`로 나누고, 트리 `n`개의 랜덤 포레스트(`random_state=0`) 테스트 정확도(소수 넷째 자리)를 반환하세요.",
           ["random_forest"], 1,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import ____
            from sklearn.model_selection import train_test_split


            def forest_acc(n):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                model = RandomForestClassifier(n_estimators=____, random_state=0).fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''',
           [t("t1", args=[50], ret=ref_forest([50], 0)[1][0], desc="50그루", **F), t("h1", args=[5], ret=ref_forest([5], 0)[1][0], **F)],
           ["랜덤 포레스트 분류기 클래스 이름입니다.", "트리 개수로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split


            def forest_acc(n):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                model = RandomForestClassifier(n_estimators=n, random_state=0).fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''', mode="function", name="forest_acc", time_limit=TL),
        ex("d101_code_1", "coding", "나무 vs 숲",
           "유방암 데이터를 `test_size=0.3, random_state=seed, stratify=y`로 나누고 `[단일 트리(random_state=0) 정확도, [트리 수별 포레스트 정확도 리스트]]`(소수 넷째 자리)를 반환하세요. 포레스트는 `random_state=0`.",
           ["random_forest", "decision_tree"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier


            def tree_vs_forest(ns, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[1, 10, 100], 0], ret=ref_forest([1, 10, 100], 0), desc="1·10·100", **F), t("h1", args=[[3, 30], 1], ret=ref_forest([3, 30], 1), **F)],
           ["단일 트리 점수를 먼저 구하세요.", "트리 수마다 새 포레스트를 학습해 점수 목록을 만듭니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier


            def tree_vs_forest(ns, seed):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                tree = DecisionTreeClassifier(random_state=0).fit(X_train, y_train).score(X_test, y_test)
                forests = []
                for n in ns:
                    forest = RandomForestClassifier(n_estimators=n, random_state=0).fit(X_train, y_train)
                    forests.append(round(forest.score(X_test, y_test), 4))
                return [round(tree, 4), forests]
           ''', mode="function", name="tree_vs_forest", time_limit=TL),
    ])

# ====================================================================== Day 102
day102 = L(
    102, "부스팅", W, ["boosting", "ensemble"],
    ["앞 모델의 실수를 다음 모델이 보완하는 부스팅의 원리를 설명할 수 있다.", "학습률과 트리 개수의 관계를 실험할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 서로 독립적인 트리들의 투표(랜덤 포레스트)를 배웠습니다.",
            "quiz": [quiz("d102_review_q1", "랜덤 포레스트의 트리들은 어떻게 만들어지나?", ["순서대로 앞 트리를 보완", "서로 독립적으로(병렬)", "하나만", "무작위 숫자"], 1, "")]},
    concept={"title": "실수를 이어서 고치기", "blocks": [
        text("**부스팅**은 작은 트리를 **순서대로** 만들되, 각 트리가 앞 트리들이 틀린 부분(잔차)을 줄이도록 학습합니다. `learning_rate`는 각 트리의 기여를 줄여 천천히 배우게 하고, "
             "대신 `n_estimators`가 더 필요합니다. 표 데이터에서 가장 강력한 모델 중 하나입니다(XGBoost, LightGBM도 이 계열)."),
        C('''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import train_test_split

            X, y = load_breast_cancer(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            for lr in [0.01, 0.1, 1.0]:
                model = GradientBoostingClassifier(learning_rate=lr, n_estimators=50, random_state=0).fit(X_train, y_train)
                print(lr, round(model.score(X_test, y_test), 4))
        '''),
        tip("큰 데이터에는 `HistGradientBoostingClassifier`가 훨씬 빠르고 결측치도 그대로 다룰 수 있습니다."),
    ]},
    fill_intro="그래디언트 부스팅 모델을 학습하세요.",
    coding_intro="학습률별 정확도를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "부스팅 = 순차적으로 앞의 실수를 보완하는 앙상블.",
        "`learning_rate`↓ → 천천히, 대신 트리 더 많이.",
        "`GradientBoostingClassifier`, 큰 데이터엔 `HistGradientBoosting…`.",
        "랜덤 포레스트는 병렬·투표, 부스팅은 순차·보완."],
        "quiz": [
            quiz("d102_summary_q1", "부스팅에서 트리들이 만들어지는 방식은?", ["독립적으로", "순서대로 앞의 실수를 보완", "무작위 하나", "사람이 직접"], 1, ""),
            quiz("d102_summary_q2", "learning_rate를 아주 작게 하면 보통 필요한 것은?", ["트리 수 감소", "트리 수 증가", "스케일링", "더 큰 깊이"], 1, "")]},
    exercises=[
        ex("d102_fill_1", "fill_blank", "부스팅 학습",
           "유방암 데이터를 `test_size=0.3, random_state=0, stratify=y`로 나누고 `GradientBoostingClassifier(n_estimators=n, random_state=0)`의 테스트 정확도(소수 넷째 자리)를 반환하세요.",
           ["boosting"], 1,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import ____
            from sklearn.model_selection import train_test_split


            def boost_acc(n):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                model = GradientBoostingClassifier(n_estimators=____, random_state=0).fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''',
           [t("t1", args=[30], ret=round(GradientBoostingClassifier(n_estimators=30, random_state=0).fit(*cancer(0)[::2]).score(*cancer(0)[1::2]), 4), desc="30개", **F),
            t("h1", args=[5], ret=round(GradientBoostingClassifier(n_estimators=5, random_state=0).fit(*cancer(0)[::2]).score(*cancer(0)[1::2]), 4), **F)],
           ["그래디언트 부스팅 분류기 클래스 이름입니다.", "트리 개수로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import train_test_split


            def boost_acc(n):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                model = GradientBoostingClassifier(n_estimators=n, random_state=0).fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''', mode="function", name="boost_acc", time_limit=TL),
        ex("d102_code_1", "coding", "학습률 실험",
           "유방암 데이터를 `test_size=0.3, random_state=seed, stratify=y`로 나누고 `learning_rates`의 각 값으로 `GradientBoostingClassifier(learning_rate=값, n_estimators=50, random_state=0)`를 학습해 "
           "테스트 정확도(소수 넷째 자리) 리스트를 반환하세요.",
           ["boosting"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import train_test_split


            def lr_scores(learning_rates, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[0.01, 0.1, 1.0], 0], ret=ref_boost([0.01, 0.1, 1.0], 0), desc="세 학습률", **F), t("h1", args=[[0.3], 2], ret=ref_boost([0.3], 2), **F)],
           ["학습률마다 새 모델을 만드세요.", "`n_estimators=50`, `random_state=0`을 잊지 마세요."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.model_selection import train_test_split


            def lr_scores(learning_rates, seed):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                scores = []
                for lr in learning_rates:
                    model = GradientBoostingClassifier(learning_rate=lr, n_estimators=50, random_state=0)
                    scores.append(round(model.fit(X_train, y_train).score(X_test, y_test), 4))
                return scores
           ''', mode="function", name="lr_scores", time_limit=TL),
    ])

# ====================================================================== Day 103
day103 = L(
    103, "특성 중요도", W, ["feature_importance", "random_forest"],
    ["트리 모델의 feature_importances_로 어떤 특성이 예측에 많이 쓰였는지 볼 수 있다.", "순열 중요도로 모델과 무관하게 중요도를 측정할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 부스팅을 배웠습니다. 이제 \"모델이 무엇을 보고 판단했나\"를 알아봅니다.",
            "quiz": [quiz("d103_review_q1", "표 데이터에서 특히 강력한 모델 계열은?", ["KNN", "부스팅", "선형 회귀", "나이브 베이즈"], 1, "")]},
    concept={"title": "무엇을 보고 판단했나", "blocks": [
        text("트리 모델은 각 특성이 불순도를 얼마나 줄였는지 합산한 **특성 중요도**(`feature_importances_`, 합 = 1)를 줍니다. "
             "**순열 중요도**는 특성 하나의 값을 무작위로 섞었을 때 점수가 얼마나 떨어지는지로 중요도를 재며, 어떤 모델에도 쓸 수 있습니다."),
        C('''
            import numpy as np
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier

            data = load_breast_cancer()
            model = RandomForestClassifier(n_estimators=100, random_state=0).fit(data.data, data.target)
            order = np.argsort(model.feature_importances_)[::-1][:3]
            for i in order:
                print(data.feature_names[i], round(model.feature_importances_[i], 4))
        '''),
        tip("중요도가 높다고 원인이라는 뜻은 아닙니다(Day 68의 상관 ≠ 인과). 또 서로 비슷한 특성이 여럿이면 중요도가 나눠져 각각 낮게 보일 수 있습니다."),
    ]},
    fill_intro="가장 중요한 특성의 위치를 찾으세요.",
    coding_intro="중요도 상위 k개 특성을 이름과 함께 반환하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`feature_importances_`: 트리 모델의 특성 중요도(합 1).",
        "`np.argsort(...)[::-1]`로 큰 순서 정렬.",
        "순열 중요도: 섞었을 때 점수 하락량, 모델 무관.",
        "중요도 ≠ 인과관계."],
        "quiz": [
            quiz("d103_summary_q1", "`feature_importances_`의 합은?", ["0", "1", "특성 수", "정확도"], 1, ""),
            quiz("d103_summary_q2", "순열 중요도가 큰 특성은?", ["섞어도 점수가 그대로", "섞으면 점수가 크게 떨어짐", "값이 큰 특성", "결측치가 많은 특성"], 1, "")]},
    exercises=[
        ex("d103_fill_1", "fill_blank", "가장 중요한 특성",
           "중요도 목록에서 가장 큰 값의 위치를 반환하세요.",
           ["feature_importance"], 1,
           '''
            import numpy as np


            def top_index(importances):
                return int(np.____(importances))
           ''',
           [t("t1", args=[[0.1, 0.6, 0.3]], ret=1, desc="기본"), t("h1", args=[[0.5, 0.2, 0.3]], ret=0)],
           ["가장 큰 값의 위치를 돌려주는 NumPy 함수입니다(arg…).", "가장 작은 값의 위치는 `argmin`이었죠. 그 반대입니다."],
           '''
            import numpy as np


            def top_index(importances):
                return int(np.argmax(importances))
           ''', mode="function", name="top_index", time_limit=TL),
        ex("d103_code_1", "coding", "중요 특성 순위",
           "유방암 데이터 전체로 `RandomForestClassifier(n_estimators=100, random_state=0)`를 학습해, 중요도 상위 `k`개 특성을 `[이름, 중요도(소수 넷째 자리)]` 리스트로 큰 순서대로 반환하세요.",
           ["feature_importance", "random_forest", "numpy_aggregate"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier


            def top_features(k):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[3], ret=ref_importance(3), desc="상위 3", **F), t("h1", args=[1], ret=ref_importance(1), **F)],
           ["`return_X_y` 없이 데이터셋 객체를 받아 두면 `feature_names`도 쓸 수 있습니다.", "`np.argsort(중요도)[::-1][:k]`가 상위 k개의 위치입니다."],
           '''
            import numpy as np
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import RandomForestClassifier


            def top_features(k):
                data = load_breast_cancer()
                model = RandomForestClassifier(n_estimators=100, random_state=0).fit(data.data, data.target)
                order = np.argsort(model.feature_importances_)[::-1][:k]
                return [[str(data.feature_names[i]), round(float(model.feature_importances_[i]), 4)] for i in order]
           ''', mode="function", name="top_features", time_limit=TL),
    ])

# ====================================================================== Day 104
WINE_HELPER = '''
            def wine_split(seed):
                X, y = load_wine(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                mean, std = X_train.mean(axis=0), X_train.std(axis=0)
                return (X_train - mean) / std, (X_test - mean) / std, y_train, y_test
'''
day104 = L(
    104, "앙상블 비교", W, ["ensemble", "logistic_regression", "knn"],
    ["서로 다른 종류의 모델을 투표로 묶는 VotingClassifier를 쓸 수 있다.", "hard 투표와 soft 투표의 차이를 설명할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 특성 중요도로 모델이 무엇을 보는지 확인했습니다.",
            "quiz": [quiz("d104_review_q1", "어떤 모델에도 쓸 수 있는 중요도 측정법은?", ["feature_importances_", "순열 중요도", "coef_", "n_support_"], 1, "")]},
    concept={"title": "다른 관점 모으기", "blocks": [
        text("**VotingClassifier**는 종류가 다른 모델들(로지스틱 회귀, KNN, 트리 등)의 예측을 합칩니다. `hard`는 예측 클래스의 다수결, `soft`는 클래스 확률의 평균으로 결정합니다. "
             "서로 다른 방식으로 틀리는 모델을 섞을수록 효과가 큽니다."),
        C('''
            from sklearn.datasets import load_wine
            from sklearn.ensemble import VotingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier

            X, y = load_wine(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)
            mean, std = X_train.mean(axis=0), X_train.std(axis=0)
            X_train, X_test = (X_train - mean) / std, (X_test - mean) / std
            members = [("lr", LogisticRegression()), ("knn", KNeighborsClassifier()), ("tree", DecisionTreeClassifier(random_state=0))]
            for name, m in members:
                print(name, round(m.fit(X_train, y_train).score(X_test, y_test), 4))
            vote = VotingClassifier(members, voting="soft").fit(X_train, y_train)
            print("vote", round(vote.score(X_test, y_test), 4))
        '''),
        tip("soft 투표는 모든 모델이 `predict_proba`를 지원해야 합니다. 앙상블이 항상 최고는 아니지만, 대체로 개별 모델보다 안정적입니다."),
    ]},
    fill_intro="투표 앙상블을 만드세요.",
    coding_intro="개별 모델과 투표 앙상블을 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "VotingClassifier: 서로 다른 모델의 예측을 합침.",
        "hard = 클래스 다수결, soft = 확률 평균.",
        "다양한 방식으로 틀리는 모델을 섞을수록 효과적.",
        "앙상블: 배깅(포레스트), 부스팅, 투표."],
        "quiz": [
            quiz("d104_summary_q1", "soft 투표에 필요한 것은?", ["모든 모델의 predict_proba", "같은 종류의 모델", "스케일링 금지", "홀수 개 모델"], 0, ""),
            quiz("d104_summary_q2", "세 모델이 A, A, B를 예측하면 hard 투표 결과는?", ["A", "B", "무승부", "확률 평균"], 0, "")]},
    exercises=[
        ex("d104_fill_1", "fill_blank", "투표 앙상블",
           "두 모델을 묶은 hard 투표 앙상블의 iris 학습 정확도(소수 넷째 자리)를 반환하세요.",
           ["ensemble"], 1,
           '''
            from sklearn.datasets import load_iris
            from sklearn.ensemble import ____
            from sklearn.linear_model import LogisticRegression
            from sklearn.tree import DecisionTreeClassifier


            def vote_acc():
                X, y = load_iris(return_X_y=True)
                members = [("lr", LogisticRegression(max_iter=1000)), ("tree", DecisionTreeClassifier(random_state=0))]
                model = VotingClassifier(members, voting="____").fit(X, y)
                return round(model.score(X, y), 4)
           ''',
           [t("t1", args=[], ret=round(VotingClassifier([("lr", LogisticRegression(max_iter=1000)), ("tree", DecisionTreeClassifier(random_state=0))], voting="hard").fit(*load_iris(return_X_y=True)).score(*load_iris(return_X_y=True)), 4), desc="hard", **F)],
           ["투표 앙상블 클래스 이름입니다.", "클래스 다수결 방식의 이름입니다."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.ensemble import VotingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.tree import DecisionTreeClassifier


            def vote_acc():
                X, y = load_iris(return_X_y=True)
                members = [("lr", LogisticRegression(max_iter=1000)), ("tree", DecisionTreeClassifier(random_state=0))]
                model = VotingClassifier(members, voting="hard").fit(X, y)
                return round(model.score(X, y), 4)
           ''', mode="function", name="vote_acc", time_limit=TL),
        ex("d104_code_1", "coding", "개별 vs 앙상블",
           "주어진 `wine_split(seed)`의 표준화 데이터로 `LogisticRegression()`, `KNeighborsClassifier()`, `DecisionTreeClassifier(random_state=0)`(이름 `lr`, `knn`, `tree`)와 "
           "이들의 `VotingClassifier(voting=voting)`(이름 `vote`)의 테스트 정확도(소수 넷째 자리) 딕셔너리를 반환하세요.",
           ["ensemble", "logistic_regression", "knn", "decision_tree"], 2,
           '''
            from sklearn.datasets import load_wine
            from sklearn.ensemble import VotingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier
''' + WINE_HELPER + '''

            def ensemble_report(voting, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=["soft", 1], ret=ref_voting("soft", 1), desc="soft", **F), t("h1", args=["hard", 3], ret=ref_voting("hard", 3), **F)],
           ["`(이름, 모델)` 튜플 리스트를 만들어 개별 점수를 먼저 구하세요.", "같은 리스트로 `VotingClassifier(members, voting=voting)`을 만들어 학습합니다."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.ensemble import VotingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier
''' + WINE_HELPER + '''

            def ensemble_report(voting, seed):
                X_train, X_test, y_train, y_test = wine_split(seed)
                members = [("lr", LogisticRegression()), ("knn", KNeighborsClassifier()),
                           ("tree", DecisionTreeClassifier(random_state=0))]
                scores = {}
                for name, model in members:
                    scores[name] = round(model.fit(X_train, y_train).score(X_test, y_test), 4)
                vote = VotingClassifier(members, voting=voting).fit(X_train, y_train)
                scores["vote"] = round(vote.score(X_test, y_test), 4)
                return scores
           ''', mode="function", name="ensemble_report", time_limit=TL),
    ])

# ====================================================================== Day 105 (review)
split2d = [(([[1, 5], [2, 4], [3, 8], [4, 1]], [0, 0, 1, 1]), "t1", "특성 0"), (([[1, 1], [2, 9], [3, 2], [4, 8]], [0, 1, 0, 1]), "h1", "")]
day105 = L(
    105, "15주차 누적 복습", W, ["decision_tree", "impurity", "random_forest", "boosting", "feature_importance", "ensemble"],
    ["트리 계열 모델을 교차 검증으로 비교하고 가장 좋은 모델을 고를 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 99 | 결정 트리 | 질문으로 나누기, `export_text` |\n| 100 | 불순도 | 지니·엔트로피, 가중 평균 |\n"
        "| 101 | 랜덤 포레스트 | 배깅 + 투표 |\n| 102 | 부스팅 | 순차 보완, learning_rate |\n"
        "| 103 | 특성 중요도 | `feature_importances_`, 순열 중요도 |\n| 104 | 투표 앙상블 | hard / soft |"),
        "quiz": [
            quiz("d105_review_q1", "트리 모델에 스케일링이 필요 없는 이유는?", ["값의 순서(크기 비교)만 쓰기 때문", "항상 정규화되어 있어서", "느려서", "확률을 안 써서"], 0, ""),
            quiz("d105_review_q2", "트리 수가 많아질수록 과적합 위험이 크게 늘지 않는 모델은?", ["단일 트리", "랜덤 포레스트", "깊은 트리", "KNN"], 1, "")]},
    concept={"title": "트리 계열 한눈에", "blocks": [
        text("| 모델 | 방식 | 장점 | 주의 |\n|---|---|---|---|\n| 결정 트리 | 질문 반복 | 해석 쉬움 | 과적합 |\n"
             "| 랜덤 포레스트 | 병렬 + 투표 | 안정적, 설정 쉬움 | 크고 느릴 수 있음 |\n| 부스팅 | 순차 보완 | 높은 성능 | 설정에 민감 |"),
        tip("도전 문제는 특성이 여러 개일 때 최적 분할을 찾는 것, 즉 트리가 뿌리에서 하는 일 그대로입니다."),
    ]},
    fill_intro="엔트로피를 계산하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "15주차 마무리", "points": [
        "트리는 질문으로 나누고, 불순도로 질문을 고른다.",
        "앙상블(배깅·부스팅·투표)은 단일 모델보다 강하다.",
        "중요도로 모델이 보는 것을 확인한다.",
        "다음 주: 정답 없이 구조를 찾는 비지도 학습."],
        "quiz": [
            quiz("d105_summary_q1", "레이블 [0, 1]의 엔트로피는?", ["0", "0.5", "1", "2"], 2, ""),
            quiz("d105_summary_q2", "다음 주 비지도 학습의 특징은?", ["정답 레이블 없이 학습", "항상 회귀", "트리만 사용", "테스트 데이터 불필요"], 0, "")]},
    is_review=True,
    exercises=[
        ex("d105_fill_1", "fill_blank", "엔트로피",
           "정수 레이블 목록의 엔트로피(밑 2, 소수 넷째 자리)를 반환하세요.",
           ["impurity"], 1,
           '''
            import numpy as np


            def entropy(labels):
                p = np.bincount(labels) / len(labels)
                p = p[p ____ 0]
                return round(float(-(p * np.____(p)).sum()), 4)
           ''',
           [t("t1", args=[[0, 1]], ret=1.0, desc="반반"), t("h1", args=[[1, 1, 1]], ret=0.0), t("h2", args=[[0, 0, 1, 2]], ret=round(entropy([0, 0, 1, 2]), 4), **F)],
           ["0인 비율은 log가 정의되지 않으니 0보다 큰 것만 남깁니다.", "밑이 2인 로그 함수입니다."],
           '''
            import numpy as np


            def entropy(labels):
                p = np.bincount(labels) / len(labels)
                p = p[p > 0]
                return round(float(-(p * np.log2(p)).sum()), 4)
           ''', mode="function", name="entropy", time_limit=TL),
        ex("d105_code_1", "coding", "트리 계열 결정전",
           "유방암 데이터 전체로 `DecisionTreeClassifier(max_depth=4, random_state=0)`(`tree`), `RandomForestClassifier(n_estimators=100, random_state=0)`(`forest`), "
           "`GradientBoostingClassifier(random_state=0)`(`boost`)를 `folds`-겹 교차 검증하세요. 평균 정확도(소수 넷째 자리)를 담은 `scores`와 최고 모델 이름 `best`를 반환합니다.",
           ["decision_tree", "random_forest", "boosting", "cross_validation"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
            from sklearn.model_selection import cross_val_score
            from sklearn.tree import DecisionTreeClassifier


            def tree_family(folds):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[5], ret=ref_cv_trees(5), desc="5겹", **F), t("h1", args=[3], ret=ref_cv_trees(3), **F)],
           ["이름 → 모델 딕셔너리를 만들고 `cross_val_score(...).mean()`.", "최고 모델은 `max(scores, key=scores.get)`."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
            from sklearn.model_selection import cross_val_score
            from sklearn.tree import DecisionTreeClassifier


            def tree_family(folds):
                X, y = load_breast_cancer(return_X_y=True)
                models = {"tree": DecisionTreeClassifier(max_depth=4, random_state=0),
                          "forest": RandomForestClassifier(n_estimators=100, random_state=0),
                          "boost": GradientBoostingClassifier(random_state=0)}
                scores = {}
                for name, model in models.items():
                    scores[name] = round(float(cross_val_score(model, X, y, cv=folds).mean()), 4)
                return {"scores": scores, "best": max(scores, key=scores.get)}
           ''', mode="function", name="tree_family", time_limit=120),
        ex("d105_code_2", "coding", "[도전] 여러 특성의 최적 분할",
           "2차원 특성 `X`(리스트의 리스트)와 레이블 `y`로, 모든 특성 f와 기준값(그 특성의 서로 다른 값 중 최댓값 제외)에 대해 `X[:, f] <= 기준값` 분할의 가중 지니를 계산해 "
           "가장 작은 `[특성 번호, 기준값, 가중 지니(소수 넷째 자리)]`를 반환하세요. 동점이면 앞 특성, 작은 기준값입니다.",
           ["impurity", "decision_tree", "numpy_indexing"], 3,
           '''
            import numpy as np


            def best_split_2d(X, y):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_best_split_2d(*a), desc=d, **F) for a, tid, d in split2d],
           ["Day 100의 `best_split`을 특성마다 반복하는 구조입니다.", "열 f의 값은 `X[:, f]`. 새 최솟값이 **더 작을 때만** 바꿉니다."],
           '''
            import numpy as np


            def gini(labels):
                if len(labels) == 0:
                    return 0.0
                p = np.bincount(labels) / len(labels)
                return 1 - (p ** 2).sum()


            def best_split_2d(X, y):
                X = np.array(X, dtype=float)
                y = np.array(y)
                best = None
                for f in range(X.shape[1]):
                    for th in sorted(set(X[:, f].tolist()))[:-1]:
                        left, right = y[X[:, f] <= th], y[X[:, f] > th]
                        score = (len(left) * gini(left) + len(right) * gini(right)) / len(y)
                        if best is None or score < best[2]:
                            best = [f, th, score]
                return [best[0], best[1], round(float(best[2]), 4)]
           ''', mode="function", name="best_split_2d", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day99, day100, day101, day102, day103, day104, day105])
