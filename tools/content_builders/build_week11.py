"""Week 11 (Day 71-77): 머신러닝 개요와 scikit-learn."""
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_iris, load_wine
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 11, "ml", 30


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


F = {"compare": {"mode": "float", "tol": 1e-9}}


# ---------------------------------------------------------------- references
def ref_1nn(train_x, train_y, query):
    tx = np.array(train_x, dtype=float)
    return [train_y[int(np.abs(tx - q).argmin())] for q in query]


def ref_iris_means():
    iris = load_iris()
    return {name: np.round(iris.data[iris.target == i].mean(axis=0), 2).tolist() for i, name in enumerate(iris.target_names)}


def ref_split(test_size, seed):
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=seed, stratify=y)
    return [len(Xtr), len(Xte), np.bincount(yte).tolist()]


def ref_knn(k, seed):
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    return round(KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr).score(Xte, yte), 4)


def ref_best_k(ks, seed):
    X, y = load_wine(return_X_y=True)
    Xtr, Xval, ytr, yval = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    scores = [round(KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr).score(Xval, yval), 4) for k in ks]
    best = ks[int(np.argmax(scores))]
    return [best, scores]


def ref_baseline(seed):
    X, y = load_wine(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    base = DummyClassifier(strategy="most_frequent").fit(Xtr, ytr).score(Xte, yte)
    knn = KNeighborsClassifier(n_neighbors=5).fit(Xtr, ytr).score(Xte, yte)
    return [round(base, 4), round(knn, 4)]


def ref_wine_report(k, seed):
    data = load_wine()
    X, y = data.data, data.target
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    model = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
    pred = model.predict(Xte)
    per_class = {str(data.target_names[c]): round(float((pred[yte == c] == c).mean()), 4) for c in np.unique(y)}
    return {"train": len(Xtr), "test": len(Xte), "accuracy": round(model.score(Xte, yte), 4), "per_class": per_class}


def ref_knn_scratch(k, seed):
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    preds = []
    for x in Xte:
        d = ((Xtr - x) ** 2).sum(axis=1)
        nearest = ytr[np.argsort(d, kind="stable")[:k]]
        preds.append(int(np.bincount(nearest, minlength=3).argmax()))
    mine = float((np.array(preds) == yte).mean())
    sk = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr).score(Xte, yte)
    return [round(mine, 4), round(sk, 4)]


# ====================================================================== Day 71
nn_cases = [(([1.0, 2.0, 8.0, 9.0], ["작음", "작음", "큼", "큼"], [1.5, 7.0, 4.0]), "t1", "기본"),
            (([0, 10], ["a", "b"], [5.1, 4.9, -3]), "h1", ""), (([3], ["x"], [100]), "h2", "")]
day71 = L(
    71, "머신러닝이란", W, ["ml_basics", "numpy_ops"],
    ["규칙을 직접 짜는 프로그래밍과 데이터에서 규칙을 배우는 머신러닝의 차이를 설명할 수 있다.", "특성(X), 정답(y), 학습, 예측의 뜻을 안다."],
    review={"title": "3단계 시작", "content_md": (
        "2단계까지 Python과 데이터 도구(NumPy·pandas·matplotlib)를 익혔습니다. **3단계는 머신러닝**입니다.\n\n"
        "지금까지는 `if 점수 >= 60: \"합격\"`처럼 규칙을 **사람이 직접** 썼습니다. 머신러닝은 예시 데이터(입력과 정답)를 보여 주고 규칙을 **컴퓨터가 찾게** 합니다."),
        "quiz": [quiz("d71_review_q1", "다음 중 머신러닝이 특히 유용한 경우는?", ["규칙이 명확한 세금 계산", "규칙을 말로 정하기 어려운 사진 속 고양이 찾기", "1부터 100까지 더하기", "파일 복사"], 1, "")]},
    concept={"title": "데이터에서 규칙 배우기", "blocks": [
        text("**특성(X)**은 입력(예: 꽃잎 길이), **정답(y, 레이블)**은 맞혀야 할 값(예: 품종)입니다. 정답이 있는 예시로 규칙을 배우는 것을 **지도 학습**이라고 하며, "
             "정답이 범주면 **분류**, 숫자면 **회귀**입니다."),
        text("가장 단순한 학습 방법 하나: 새 데이터와 **가장 가까운 예시의 정답을 그대로 따라 하기**(최근접 이웃). 학습 = 예시를 기억하기, 예측 = 가장 가까운 것 찾기입니다."),
        C('''
            import numpy as np

            train_x = np.array([150, 160, 175, 185])
            train_y = ["S", "M", "L", "XL"]
            for height in [158, 181]:
                nearest = np.abs(train_x - height).argmin()
                print(height, "->", train_y[nearest])
        '''),
        tip("머신러닝 모델이 잘하는지는 **처음 보는 데이터**로 확인해야 합니다. 이미 본 예시만 맞히는 건 외운 것일 수도 있으니까요(Day 73에서 자세히)."),
    ]},
    fill_intro="가장 가까운 예시의 위치를 찾으세요.",
    coding_intro="1차원 최근접 이웃 분류기를 NumPy로 직접 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "머신러닝 = 데이터에서 규칙을 배우는 방법.",
        "특성 X(입력), 정답 y(레이블); 지도 학습은 정답이 있는 예시로 배운다.",
        "범주 맞히기는 분류, 숫자 맞히기는 회귀.",
        "최근접 이웃: 가장 비슷한 예시의 정답을 따른다."],
        "quiz": [
            quiz("d71_summary_q1", "집값(숫자)을 예측하는 문제는?", ["분류", "회귀", "군집", "검색"], 1, ""),
            quiz("d71_summary_q2", "스팸/정상 메일을 가르는 문제는?", ["분류", "회귀", "정렬", "압축"], 0, "")]},
    exercises=[
        ex("d71_fill_1", "fill_blank", "가장 가까운 예시",
           "숫자 목록 `xs`에서 `q`와 가장 가까운 값의 **위치(인덱스)**를 반환하세요.",
           ["ml_basics"], 1,
           '''
            import numpy as np


            def nearest_index(xs, q):
                distances = np.____(np.array(xs) - q)
                return int(distances.____())
           ''',
           [t("t1", args=[[1, 5, 9], 6], ret=1, desc="기본"), t("h1", args=[[0, 10], -3], ret=0), t("h2", args=[[2, 4, 8], 7.5], ret=2)],
           ["거리는 차이의 절댓값입니다. 절댓값을 구하는 NumPy 함수입니다.", "가장 작은 값의 위치를 돌려주는 메서드입니다."],
           '''
            import numpy as np


            def nearest_index(xs, q):
                distances = np.abs(np.array(xs) - q)
                return int(distances.argmin())
           ''', mode="function", name="nearest_index", time_limit=TL),
        ex("d71_code_1", "coding", "최근접 이웃 분류기",
           "학습 데이터(`train_x` 숫자 목록, `train_y` 정답 목록)를 기억했다가, `queries`의 각 값마다 **가장 가까운 학습 데이터의 정답**을 예측한 리스트를 반환하세요. "
           "거리가 같으면 앞쪽 예시를 따릅니다.",
           ["ml_basics", "numpy_ops"], 2,
           '''
            import numpy as np


            def predict_1nn(train_x, train_y, queries):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_1nn(*a), desc=d) for a, tid, d in nn_cases],
           ["`train_x`를 배열로 바꾸고, 질문 값마다 `np.abs(배열 - q).argmin()`으로 가장 가까운 위치를 찾으세요.",
            "그 위치의 `train_y` 값을 결과 리스트에 담습니다. `argmin`은 같은 값이면 앞쪽 위치를 줍니다."],
           '''
            import numpy as np


            def predict_1nn(train_x, train_y, queries):
                xs = np.array(train_x, dtype=float)
                predictions = []
                for q in queries:
                    nearest = int(np.abs(xs - q).argmin())
                    predictions.append(train_y[nearest])
                return predictions
           ''', mode="function", name="predict_1nn", time_limit=TL),
    ])

# ====================================================================== Day 72
day72 = L(
    72, "데이터셋과 특성", W, ["dataset", "pandas_groupby", "numpy_aggregate"],
    ["scikit-learn 내장 데이터셋을 불러와 X, y, 특성 이름, 클래스 이름을 확인할 수 있다.", "클래스별 특성 평균으로 데이터를 이해할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 특성(X)·정답(y)과 최근접 이웃 아이디어를 배웠습니다.",
            "quiz": [quiz("d72_review_q1", "지도 학습에 꼭 필요한 것은?", ["정답(레이블)이 있는 예시", "그래프", "GPU", "인터넷"], 0, "")]},
    concept={"title": "붓꽃(iris) 데이터", "blocks": [
        text("scikit-learn에는 연습용 데이터셋이 들어 있습니다. **붓꽃(iris)** 데이터는 꽃 150송이의 꽃받침·꽃잎 길이와 너비(특성 4개)로 품종 3가지를 맞히는 문제입니다."),
        C('''
            from sklearn.datasets import load_iris

            iris = load_iris()
            print(iris.data.shape, iris.target.shape)
            print(iris.feature_names)
            print(iris.target_names)
            print(iris.data[0], iris.target[0])
        '''),
        text("`as_frame=True`로 불러오면 pandas DataFrame으로 받아 EDA(10주차)를 할 수 있습니다."),
        C('''
            from sklearn.datasets import load_iris

            df = load_iris(as_frame=True).frame
            print(df.shape)
            print(df.groupby("target")["petal length (cm)"].mean().round(2).to_dict())
        '''),
        tip("모델을 만들기 전에 클래스별로 특성이 어떻게 다른지 보면, 어떤 특성이 구분에 쓸모 있을지 감을 잡을 수 있습니다. 붓꽃은 꽃잎 길이만으로도 품종이 꽤 갈립니다."),
    ]},
    fill_intro="iris 데이터의 모양을 확인하세요.",
    coding_intro="품종별 특성 평균을 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`load_iris()` → `data`(X), `target`(y), `feature_names`, `target_names`.",
        "X의 모양 = (샘플 수, 특성 수).",
        "`as_frame=True`로 DataFrame 받기.",
        "클래스별 특성 평균으로 데이터를 이해한다."],
        "quiz": [
            quiz("d72_summary_q1", "iris의 X 모양 (150, 4)에서 4는?", ["클래스 수", "특성 수", "샘플 수", "결측치 수"], 1, ""),
            quiz("d72_summary_q2", "iris의 클래스(품종) 수는?", ["2", "3", "4", "150"], 1, "")]},
    exercises=[
        ex("d72_fill_1", "fill_blank", "데이터 모양",
           "iris 데이터를 불러와 `[샘플 수, 특성 수, 클래스 수]`를 반환하세요.",
           ["dataset"], 1,
           '''
            from sklearn.datasets import load_iris


            def iris_shape():
                iris = ____()
                n_samples, n_features = iris.data.____
                return [n_samples, n_features, len(iris.target_names)]
           ''',
           [t("t1", args=[], ret=[150, 4, 3], desc="iris")],
           ["iris 데이터셋을 불러오는 함수 이름입니다.", "배열의 모양을 담은 속성입니다."],
           '''
            from sklearn.datasets import load_iris


            def iris_shape():
                iris = load_iris()
                n_samples, n_features = iris.data.shape
                return [n_samples, n_features, len(iris.target_names)]
           ''', mode="function", name="iris_shape", time_limit=TL),
        ex("d72_code_1", "coding", "품종별 특성 평균",
           "iris 데이터에서 품종 이름 → 특성 4개의 평균(소수 둘째 자리 반올림) 리스트 딕셔너리를 반환하세요.\n\n"
           "예: `{\"setosa\": [5.01, 3.43, 1.46, 0.25], ...}`",
           ["dataset", "numpy_aggregate", "numpy_indexing"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_iris


            def class_means():
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[], ret=ref_iris_means(), desc="3품종", **F)],
           ["`iris.data[iris.target == i]`로 i번 품종의 행만 고르세요.", "고른 행의 `mean(axis=0)`이 특성별 평균입니다.", "`enumerate(iris.target_names)`로 번호와 이름을 함께 돌면 편합니다."],
           '''
            import numpy as np
            from sklearn.datasets import load_iris


            def class_means():
                iris = load_iris()
                result = {}
                for i, name in enumerate(iris.target_names):
                    rows = iris.data[iris.target == i]
                    result[str(name)] = np.round(rows.mean(axis=0), 2).tolist()
                return result
           ''', mode="function", name="class_means", time_limit=TL),
    ])

# ====================================================================== Day 73
split_cases = [((0.2, 0), "t1", "20%"), ((0.3, 42), "h1", ""), ((0.5, 7), "h2", "")]
day73 = L(
    73, "학습 데이터와 테스트 데이터", W, ["train_test", "dataset"],
    ["모델 평가를 위해 데이터를 학습용과 테스트용으로 나누는 이유를 설명할 수 있다.", "train_test_split의 test_size, random_state, stratify를 쓸 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 iris 데이터셋의 구조를 살펴봤습니다.",
            "quiz": [quiz("d73_review_q1", "`load_iris().target`에 담긴 것은?", ["특성 값", "정답(품종 번호)", "특성 이름", "그래프"], 1, "")]},
    concept={"title": "시험 문제는 미리 보여 주지 않는다", "blocks": [
        text("모델이 학습에 쓴 데이터로 평가하면 \"답을 외운\" 모델도 좋아 보입니다. 그래서 일부(보통 20~30%)를 **테스트 데이터**로 떼어 두고, 학습이 끝난 뒤 한 번만 평가합니다."),
        C('''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split

            X, y = load_iris(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=0, stratify=y
            )
            print(X_train.shape, X_test.shape)
            print(np.bincount(y_train), np.bincount(y_test))
        '''),
        tip("`random_state`를 고정하면 매번 같은 방식으로 나뉘어 결과를 재현할 수 있습니다. `stratify=y`는 클래스 비율을 학습·테스트에서 똑같이 유지해 줍니다."),
    ]},
    fill_intro="데이터를 나누고 크기를 확인하세요.",
    coding_intro="층화(stratify) 분할 후 테스트 데이터의 클래스 분포를 보고하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "평가는 학습에 쓰지 않은 테스트 데이터로.",
        "`train_test_split(X, y, test_size=, random_state=, stratify=)`.",
        "반환 순서: `X_train, X_test, y_train, y_test`.",
        "`stratify=y`로 클래스 비율 유지."],
        "quiz": [
            quiz("d73_summary_q1", "150개 데이터를 `test_size=0.2`로 나누면 테스트 개수는?", ["20", "30", "120", "15"], 1, ""),
            quiz("d73_summary_q2", "`random_state`를 고정하는 이유는?", ["정확도 향상", "결과 재현", "속도 향상", "결측치 제거"], 1, "")]},
    exercises=[
        ex("d73_fill_1", "fill_blank", "나누기",
           "iris를 `test_size`, `random_state=0`으로 나눠 `[학습 개수, 테스트 개수]`를 반환하세요.",
           ["train_test"], 1,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import ____


            def split_sizes(test_size):
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=____, random_state=0)
                return [len(X_train), len(X_test)]
           ''',
           [t("t1", args=[0.2], ret=[120, 30], desc="20%"), t("h1", args=[0.5], ret=[75, 75])],
           ["데이터를 나누는 함수 이름입니다.", "테스트 비율로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split


            def split_sizes(test_size):
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=0)
                return [len(X_train), len(X_test)]
           ''', mode="function", name="split_sizes", time_limit=TL),
        ex("d73_code_1", "coding", "층화 분할 보고",
           "iris를 `test_size`, `random_state=seed`, **클래스 비율을 유지**하도록 나눈 뒤 `[학습 개수, 테스트 개수, 테스트의 클래스별 개수 리스트]`를 반환하세요.",
           ["train_test"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split


            def stratified_report(test_size, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_split(*a), desc=d) for a, tid, d in split_cases],
           ["`stratify=y`를 넘기세요.", "클래스별 개수는 `np.bincount(y_test)`."],
           '''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split


            def stratified_report(test_size, seed):
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=seed, stratify=y
                )
                return [len(X_train), len(X_test), np.bincount(y_test)]
           ''', mode="function", name="stratified_report", time_limit=TL),
    ])

# ====================================================================== Day 74
knn_cases = [((3, 0), "t1", "k=3"), ((1, 1), "h1", ""), ((15, 2), "h2", "")]
day74 = L(
    74, "첫 모델: k-최근접 이웃", W, ["knn", "sklearn_api", "train_test"],
    ["KNeighborsClassifier로 모델을 만들고 fit, predict, score를 쓸 수 있다.", "k(이웃 수)의 의미를 설명할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 학습·테스트 데이터를 나눴습니다.",
            "quiz": [quiz("d74_review_q1", "`train_test_split`의 반환 순서는?", ["X_train, y_train, X_test, y_test", "X_train, X_test, y_train, y_test", "X, y", "train, test"], 1, "")]},
    concept={"title": "fit → predict → score", "blocks": [
        text("**k-최근접 이웃(KNN)**은 Day 71의 아이디어를 넓힌 것입니다. 가장 가까운 **k개** 이웃의 다수결로 정답을 정합니다. scikit-learn 모델은 모두 같은 3단계로 씁니다."),
        C('''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier

            X, y = load_iris(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            model = KNeighborsClassifier(n_neighbors=3)
            model.fit(X_train, y_train)
            print(model.predict(X_test[:5]))
            print(y_test[:5])
            print(round(model.score(X_test, y_test), 3))
        '''),
        tip("`score`는 분류 모델에서 **정확도**(맞힌 비율)입니다. k가 너무 작으면 잡음에 휘둘리고, 너무 크면 경계가 뭉개집니다."),
    ]},
    fill_intro="KNN 모델을 학습시키세요.",
    coding_intro="k와 시드를 바꿔 가며 테스트 정확도를 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`model = KNeighborsClassifier(n_neighbors=k)`.",
        "`fit(X_train, y_train)` → 학습, `predict(X)` → 예측.",
        "`score(X_test, y_test)` → 정확도.",
        "k: 다수결에 참여하는 이웃 수."],
        "quiz": [
            quiz("d74_summary_q1", "모델을 학습시키는 메서드는?", ["`train`", "`fit`", "`learn`", "`score`"], 1, ""),
            quiz("d74_summary_q2", "이웃 5개 중 A가 3개, B가 2개면 KNN(k=5)의 예측은?", ["A", "B", "무승부", "오류"], 0, "")]},
    exercises=[
        ex("d74_fill_1", "fill_blank", "학습과 평가",
           "iris를 `test_size=0.3, random_state=0, stratify=y`로 나눈 뒤 k=5 KNN을 학습시키고 테스트 정확도(소수 넷째 자리)를 반환하세요.",
           ["knn", "sklearn_api"], 1,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def knn5():
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                model = KNeighborsClassifier(n_neighbors=5)
                model.____(X_train, y_train)
                return round(model.____(X_test, y_test), 4)
           ''',
           [t("t1", args=[], ret=ref_knn(5, 0), desc="k=5", **F)],
           ["학습시키는 메서드입니다.", "정확도를 계산하는 메서드입니다."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def knn5():
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                model = KNeighborsClassifier(n_neighbors=5)
                model.fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''', mode="function", name="knn5", time_limit=TL),
        ex("d74_code_1", "coding", "KNN 정확도",
           "iris를 `test_size=0.3, random_state=seed, stratify=y`로 나누고, 이웃 수 `k`인 KNN의 테스트 정확도를 소수 넷째 자리까지 반환하세요.",
           ["knn", "sklearn_api", "train_test"], 2,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def knn_accuracy(k, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_knn(*a), desc=d, **F) for a, tid, d in knn_cases],
           ["`load_iris(return_X_y=True)` → 나누기 → 모델 만들기 → `fit` → `score` 순서입니다.", "반올림은 `round(값, 4)`."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def knn_accuracy(k, seed):
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.3, random_state=seed, stratify=y
                )
                model = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''', mode="function", name="knn_accuracy", time_limit=TL),
    ])

# ====================================================================== Day 75
bestk_cases = [(([1, 3, 5, 7, 9], 0), "t1", "와인 데이터"), (([2, 4], 1), "h1", ""), (([1, 15, 30], 3), "h2", "")]
day75 = L(
    75, "k 고르기와 모델 비교", W, ["knn", "train_test", "sklearn_api"],
    ["여러 설정을 검증 데이터로 비교해 가장 좋은 값을 고를 수 있다.", "테스트 데이터를 설정 고르기에 쓰면 안 되는 이유를 안다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 KNN으로 첫 모델을 학습하고 정확도를 쟀습니다.",
            "quiz": [quiz("d75_review_q1", "분류 모델의 `score`가 기본으로 계산하는 것은?", ["오차", "정확도", "손실", "시간"], 1, "")]},
    concept={"title": "설정값을 데이터로 고르기", "blocks": [
        text("k처럼 사람이 정해 줘야 하는 값을 **하이퍼파라미터**라고 합니다. 여러 후보를 시험해 가장 좋은 것을 고르는데, 이때는 테스트가 아닌 **검증(validation) 데이터**를 씁니다. "
             "테스트 데이터로 고르면 테스트 점수가 실제보다 좋게 나옵니다."),
        C('''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier

            X, y = load_wine(return_X_y=True)
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            for k in [1, 5, 15]:
                acc = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train).score(X_val, y_val)
                print(k, round(acc, 3))
        '''),
        tip("와인 데이터는 특성마다 단위(크기)가 크게 달라서 거리 기반인 KNN이 불리합니다. 17주차에 배울 **스케일링**을 하면 정확도가 크게 오릅니다."),
    ]},
    fill_intro="k 후보마다 검증 정확도를 구하세요.",
    coding_intro="가장 좋은 k와 점수 목록을 반환하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "하이퍼파라미터 = 사람이 정하는 설정값(k 등).",
        "후보 비교는 검증 데이터로, 테스트는 마지막에 한 번.",
        "같은 점수면 단순한 쪽(앞쪽 후보)을 고르는 규칙을 정해 둔다.",
        "거리 기반 모델은 특성 크기(스케일)에 민감하다."],
        "quiz": [
            quiz("d75_summary_q1", "하이퍼파라미터를 고를 때 쓰면 안 되는 데이터는?", ["학습", "검증", "테스트", "모두 괜찮다"], 2, ""),
            quiz("d75_summary_q2", "KNN의 k는?", ["모델이 학습하는 값", "하이퍼파라미터", "정답", "특성"], 1, "")]},
    exercises=[
        ex("d75_fill_1", "fill_blank", "후보별 점수",
           "와인 데이터를 `test_size=0.3, random_state=0, stratify=y`로 학습·검증으로 나누고, `ks`의 각 k에 대한 검증 정확도(소수 넷째 자리) 리스트를 반환하세요.",
           ["knn"], 1,
           '''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def k_scores(ks):
                X, y = load_wine(return_X_y=True)
                X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                scores = []
                for k in ks:
                    model = KNeighborsClassifier(n_neighbors=____).fit(X_train, y_train)
                    scores.append(round(model.score(X_val, ____), 4))
                return scores
           ''',
           [t("t1", args=[[1, 5]], ret=ref_best_k([1, 5], 0)[1], desc="k=1,5", **F), t("h1", args=[[3, 9]], ret=ref_best_k([3, 9], 0)[1], **F)],
           ["반복 변수입니다.", "검증용 정답입니다."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def k_scores(ks):
                X, y = load_wine(return_X_y=True)
                X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
                scores = []
                for k in ks:
                    model = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)
                    scores.append(round(model.score(X_val, y_val), 4))
                return scores
           ''', mode="function", name="k_scores", time_limit=TL),
        ex("d75_code_1", "coding", "최적의 k",
           "와인 데이터를 `test_size=0.3, random_state=seed, stratify=y`로 학습·검증으로 나누고, 후보 `ks` 중 검증 정확도가 가장 높은 k와 점수 목록(소수 넷째 자리)을 `[best_k, scores]`로 반환하세요. 동점이면 앞 후보입니다.",
           ["knn", "hyperparameter", "train_test"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def best_k(ks, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_best_k(*a), desc=d, **F) for a, tid, d in bestk_cases],
           ["점수 목록을 먼저 만드세요.", "`np.argmax(scores)`는 최댓값의 첫 위치를 줍니다. 그 위치의 k를 고릅니다."],
           '''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def best_k(ks, seed):
                X, y = load_wine(return_X_y=True)
                X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                scores = []
                for k in ks:
                    model = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)
                    scores.append(round(model.score(X_val, y_val), 4))
                return [ks[int(np.argmax(scores))], scores]
           ''', mode="function", name="best_k", time_limit=TL),
    ])

# ====================================================================== Day 76
base_cases = [((0,), "t1", "시드 0"), ((1,), "h1", ""), ((5,), "h2", "")]
day76 = L(
    76, "scikit-learn의 공통 패턴", W, ["sklearn_api", "train_test"],
    ["scikit-learn의 추정기(estimator) 공통 인터페이스를 설명할 수 있다.", "아무것도 배우지 않는 기준 모델(baseline)과 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 검증 데이터로 k를 골랐습니다.",
            "quiz": [quiz("d76_review_q1", "검증 데이터의 역할은?", ["최종 성능 보고", "하이퍼파라미터 고르기", "학습", "결측치 채우기"], 1, "")]},
    concept={"title": "모든 모델은 같은 모양", "blocks": [
        text("scikit-learn의 모델(추정기)은 종류와 상관없이 `fit`, `predict`, `score`를 가집니다. 그래서 모델만 바꿔 끼우며 비교하기 쉽습니다. 학습이 끝나면 배운 값은 이름 끝에 `_`가 붙은 속성(`classes_` 등)에 저장됩니다."),
        C('''
            from sklearn.datasets import load_wine
            from sklearn.dummy import DummyClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier

            X, y = load_wine(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
            for model in [DummyClassifier(strategy="most_frequent"), KNeighborsClassifier()]:
                model.fit(X_train, y_train)
                print(type(model).__name__, round(model.score(X_test, y_test), 3), model.classes_)
        '''),
        tip("**기준 모델**(가장 흔한 클래스만 찍는 모델)보다 나은지 꼭 확인하세요. 90%가 정상인 데이터에서 \"항상 정상\"만 찍어도 정확도 90%입니다."),
    ]},
    fill_intro="기준 모델의 정확도를 구하세요.",
    coding_intro="기준 모델과 KNN을 같은 방식으로 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "모든 추정기: `fit` / `predict` / `score`.",
        "학습된 값은 `_`로 끝나는 속성(`classes_`, `coef_` 등).",
        "`DummyClassifier`로 기준 성능 확인.",
        "모델은 바꿔 끼우며 같은 코드로 비교한다."],
        "quiz": [
            quiz("d76_summary_q1", "70%가 A인 데이터에서 \"항상 A\" 모델의 정확도는?", ["30%", "50%", "70%", "100%"], 2, ""),
            quiz("d76_summary_q2", "학습 후 생기는 속성의 이름 특징은?", ["대문자", "끝에 `_`", "앞에 `__`", "숫자 포함"], 1, "")]},
    exercises=[
        ex("d76_fill_1", "fill_blank", "기준 모델",
           "와인 데이터를 `test_size=0.25, random_state=0, stratify=y`로 나누고 가장 흔한 클래스만 예측하는 모델의 테스트 정확도(소수 넷째 자리)를 반환하세요.",
           ["sklearn_api"], 1,
           '''
            from sklearn.datasets import load_wine
            from sklearn.dummy import ____
            from sklearn.model_selection import train_test_split


            def baseline():
                X, y = load_wine(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
                model = DummyClassifier(strategy="____").fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''',
           [t("t1", args=[], ret=ref_baseline(0)[0], desc="most_frequent", **F)],
           ["기준 분류 모델의 클래스 이름입니다.", "가장 흔한 클래스를 고르는 전략 이름입니다(most_…)."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.dummy import DummyClassifier
            from sklearn.model_selection import train_test_split


            def baseline():
                X, y = load_wine(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
                model = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
                return round(model.score(X_test, y_test), 4)
           ''', mode="function", name="baseline", time_limit=TL),
        ex("d76_code_1", "coding", "기준 모델 vs KNN",
           "와인 데이터를 `test_size=0.25, random_state=seed, stratify=y`로 나누고, `DummyClassifier(strategy=\"most_frequent\")`와 `KNeighborsClassifier(n_neighbors=5)`의 테스트 정확도를 `[기준, KNN]`(소수 넷째 자리)으로 반환하세요. "
           "두 모델을 리스트에 담아 반복문 하나로 처리해 보세요.",
           ["sklearn_api", "knn"], 2,
           '''
            from sklearn.datasets import load_wine
            from sklearn.dummy import DummyClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def compare(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_baseline(*a), desc=d, **F) for a, tid, d in base_cases],
           ["모델 두 개를 리스트로 만들고 `for model in models:`로 돌며 `fit` → `score`.", "결과를 같은 순서로 리스트에 담아 반환합니다."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.dummy import DummyClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def compare(seed):
                X, y = load_wine(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                models = [DummyClassifier(strategy="most_frequent"), KNeighborsClassifier(n_neighbors=5)]
                scores = []
                for model in models:
                    model.fit(X_train, y_train)
                    scores.append(round(model.score(X_test, y_test), 4))
                return scores
           ''', mode="function", name="compare", checks={"required_syntax": ["for"]}, time_limit=TL),
    ])

# ====================================================================== Day 77 (review)
day77 = L(
    77, "11주차 누적 복습", W, ["ml_basics", "dataset", "train_test", "knn", "sklearn_api"],
    ["데이터 불러오기 → 나누기 → 학습 → 평가 → 보고의 전체 흐름을 직접 구성할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 71 | 머신러닝이란 | 특성 X, 정답 y, 분류·회귀 |\n"
        "| 72 | 데이터셋 | `load_iris`, `feature_names`, `target_names` |\n"
        "| 73 | 데이터 나누기 | `train_test_split`, `stratify`, `random_state` |\n"
        "| 74 | KNN | `fit`, `predict`, `score` |\n"
        "| 75 | k 고르기 | 검증 데이터, 하이퍼파라미터 |\n"
        "| 76 | 공통 패턴 | 추정기 인터페이스, 기준 모델 |"),
        "quiz": [
            quiz("d77_review_q1", "올바른 순서는?", ["학습 → 나누기 → 평가", "나누기 → 학습 → 평가", "평가 → 학습 → 나누기", "나누기 → 평가 → 학습"], 1, ""),
            quiz("d77_review_q2", "클래스별 정확도를 보는 이유는?", ["전체 정확도가 특정 클래스의 약점을 가릴 수 있어서", "속도", "코드가 짧아서", "필요 없다"], 0, "")]},
    concept={"title": "클래스별로 들여다보기", "blocks": [
        text("전체 정확도가 높아도 특정 클래스를 자주 틀릴 수 있습니다. 예측과 정답을 클래스별로 비교해 보세요(다음 주의 혼동 행렬로 이어집니다)."),
        C('''
            import numpy as np

            y_true = np.array([0, 0, 1, 1, 2, 2])
            y_pred = np.array([0, 0, 1, 2, 2, 2])
            for c in [0, 1, 2]:
                mask = y_true == c
                print(c, (y_pred[mask] == c).mean())
        '''),
        tip("도전 문제에서는 KNN을 NumPy만으로 직접 만들어 scikit-learn 결과와 비교합니다. 거리 계산 → 가까운 k개 → 다수결의 세 단계예요."),
    ]},
    fill_intro="와인 데이터의 클래스 이름을 확인하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "11주차 마무리", "points": [
        "머신러닝 흐름: 데이터 → 나누기 → 학습 → 평가.",
        "테스트 데이터는 마지막에, 설정 고르기는 검증 데이터로.",
        "기준 모델과 클래스별 성능을 함께 본다.",
        "다음 주: 숫자를 예측하는 회귀."],
        "quiz": [
            quiz("d77_summary_q1", "KNN에서 예측이 느려지는 주된 이유는?", ["학습이 오래 걸려서", "예측 때마다 모든 학습 데이터와 거리를 계산해서", "GPU가 없어서", "k가 작아서"], 1, ""),
            quiz("d77_summary_q2", "다음 주에 배울 \"숫자 예측\" 문제는?", ["분류", "회귀", "군집", "차원 축소"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d77_fill_1", "fill_blank", "와인 클래스",
           "와인 데이터의 클래스 이름 리스트와 특성 수를 `[이름 리스트, 특성 수]`로 반환하세요.",
           ["dataset"], 1,
           '''
            from sklearn.datasets import load_wine


            def wine_info():
                wine = load_wine()
                return [list(wine.____), wine.data.shape[____]]
           ''',
           [t("t1", args=[], ret=[list(load_wine().target_names), 13], desc="wine")],
           ["클래스 이름이 담긴 속성입니다(target_…).", "모양 튜플에서 특성 수의 위치입니다."],
           '''
            from sklearn.datasets import load_wine


            def wine_info():
                wine = load_wine()
                return [list(wine.target_names), wine.data.shape[1]]
           ''', mode="function", name="wine_info", time_limit=TL),
        ex("d77_code_1", "coding", "와인 분류 보고서",
           "와인 데이터를 `test_size=0.25, random_state=seed, stratify=y`로 나누고 KNN(이웃 `k`개)을 학습해 딕셔너리를 반환하세요.\n\n"
           "- `train`, `test`: 데이터 개수\n- `accuracy`: 테스트 정확도(소수 넷째 자리)\n- `per_class`: 클래스 이름 → 그 클래스 테스트 샘플 중 맞힌 비율(소수 넷째 자리)",
           ["knn", "train_test", "dataset", "numpy_indexing"], 3,
           '''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def wine_report(k, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[5, 0], ret=ref_wine_report(5, 0), desc="k=5", **F), t("h1", args=[1, 3], ret=ref_wine_report(1, 3), **F)],
           ["`data = load_wine()`로 이름까지 받아 두세요.", "예측 `pred`를 구한 뒤 클래스 c마다 `(pred[y_test == c] == c).mean()`.",
            "클래스 이름은 `str(data.target_names[c])`."],
           '''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def wine_report(k, seed):
                data = load_wine()
                X_train, X_test, y_train, y_test = train_test_split(
                    data.data, data.target, test_size=0.25, random_state=seed, stratify=data.target
                )
                model = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train)
                pred = model.predict(X_test)
                per_class = {}
                for c in np.unique(data.target):
                    per_class[str(data.target_names[c])] = round(float((pred[y_test == c] == c).mean()), 4)
                return {"train": len(X_train), "test": len(X_test),
                        "accuracy": round(model.score(X_test, y_test), 4), "per_class": per_class}
           ''', mode="function", name="wine_report", time_limit=TL),
        ex("d77_code_2", "coding", "[도전] KNN 직접 만들기",
           "iris를 `test_size=0.3, random_state=seed, stratify=y`로 나누고, NumPy만으로 KNN(유클리드 거리 제곱, 이웃 `k`개 다수결, 동률이면 번호가 작은 클래스)을 구현해 "
           "`[내 정확도, scikit-learn KNN 정확도]`(소수 넷째 자리)를 반환하세요. 거리가 같은 이웃은 학습 데이터에서 앞에 있는 것을 먼저 고릅니다(`np.argsort(..., kind=\"stable\")`).",
           ["knn", "numpy_aggregate", "numpy_indexing"], 3,
           '''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def knn_from_scratch(k, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[5, 0], ret=ref_knn_scratch(5, 0), desc="k=5", **F), t("h1", args=[3, 2], ret=ref_knn_scratch(3, 2), **F)],
           ["테스트 샘플 x마다 `((X_train - x) ** 2).sum(axis=1)`로 거리를 구하세요.",
            "`np.argsort(거리, kind=\"stable\")[:k]` 위치의 정답들을 `np.bincount(..., minlength=3).argmax()`로 다수결합니다.",
            "정확도는 `(예측 배열 == y_test).mean()`."],
           '''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def knn_from_scratch(k, seed):
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                predictions = []
                for x in X_test:
                    distances = ((X_train - x) ** 2).sum(axis=1)
                    nearest = y_train[np.argsort(distances, kind="stable")[:k]]
                    predictions.append(np.bincount(nearest, minlength=3).argmax())
                mine = float((np.array(predictions) == y_test).mean())
                sk = KNeighborsClassifier(n_neighbors=k).fit(X_train, y_train).score(X_test, y_test)
                return [round(mine, 4), round(sk, 4)]
           ''', mode="function", name="knn_from_scratch", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day71, day72, day73, day74, day75, day76, day77])
