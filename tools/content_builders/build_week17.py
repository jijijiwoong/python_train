"""Week 17 (Day 113-119): 특성 공학과 파이프라인, 3단계 마무리."""
import sys
from pathlib import Path
from textwrap import dedent

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 17, "ml", 60
F = {"compare": {"mode": "float", "tol": 1e-6}}


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


CHURN_SRC = '''
def churn_data(n, seed):
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 70, n).astype(float)
    monthly = rng.normal(50, 20, n).round(1)
    plan = rng.choice(["basic", "standard", "premium"], n)
    region = rng.choice(["서울", "부산", "대구"], n)
    complaints = rng.poisson(1.0, n)
    score = 0.04 * (age - 40) - 0.03 * (monthly - 50) + 0.8 * complaints - 0.6 * (plan == "premium")
    churn = (score + rng.normal(0, 0.8, n) > 0.8).astype(int)
    age[rng.random(n) < 0.08] = np.nan
    monthly[rng.random(n) < 0.05] = np.nan
    return pd.DataFrame({"age": age, "monthly": monthly, "plan": plan, "region": region,
                         "complaints": complaints, "churn": churn})
'''
exec(CHURN_SRC)  # defines churn_data for the reference code below
CHURN_HELPER = "\n" + "\n".join("            " + line if line else "" for line in dedent(CHURN_SRC).strip("\n").split("\n")) + "\n"

NUM, CAT = ["age", "monthly", "complaints"], ["plan", "region"]


def churn_pipeline(model):
    pre = ColumnTransformer([
        ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
    ])
    return Pipeline([("prep", pre), ("model", model)])


# ---------------------------------------------------------------- references
def ref_scaling(seed):
    X, y = load_wine(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    raw = KNeighborsClassifier().fit(Xtr, ytr).score(Xte, yte)
    sc = StandardScaler().fit(Xtr)
    scaled = KNeighborsClassifier().fit(sc.transform(Xtr), ytr).score(sc.transform(Xte), yte)
    return [round(raw, 4), round(scaled, 4)]


def ref_onehot(values):
    enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore").fit(np.array(values).reshape(-1, 1))
    return [enc.categories_[0].tolist(), enc.transform([["unknown"], [values[0]]]).astype(int).tolist()]


def ref_impute(rows, strategy):
    imp = SimpleImputer(strategy=strategy)
    return np.round(imp.fit_transform(np.array(rows, dtype=float)), 3).tolist()


def ref_churn(seed):
    df = churn_data(400, seed)
    X, y = df.drop(columns="churn"), df["churn"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    pipe = churn_pipeline(LogisticRegression()).fit(Xtr, ytr)
    return [int(pipe.named_steps["prep"].transform(Xte).shape[1]), round(pipe.score(Xte, yte), 4)]


def ref_kbest(ks, seed):
    data = load_breast_cancer()
    Xtr, Xte, ytr, yte = train_test_split(data.data, data.target, test_size=0.3, random_state=seed, stratify=data.target)
    out = []
    for k in ks:
        pipe = make_pipeline(StandardScaler(), SelectKBest(f_classif, k=k), LogisticRegression()).fit(Xtr, ytr)
        out.append(round(pipe.score(Xte, yte), 4))
    sel = SelectKBest(f_classif, k=3).fit(Xtr, ytr)
    return [out, [str(n) for n in data.feature_names[sel.get_support()]]]


def ref_project(seed):
    df = churn_data(600, seed)
    X, y = df.drop(columns="churn"), df["churn"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    grid = GridSearchCV(churn_pipeline(LogisticRegression()), {"model__C": [0.01, 0.1, 1, 10]}, cv=5, scoring="roc_auc").fit(Xtr, ytr)
    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(yte, grid.predict_proba(Xte)[:, 1])
    return {"best_C": float(grid.best_params_["model__C"]), "cv_auc": round(float(grid.best_score_), 4),
            "test_auc": round(float(auc), 4), "churn_rate": round(float(y.mean()), 4)}


def ref_final(seed):
    df = churn_data(600, seed)
    X, y = df.drop(columns="churn"), df["churn"]
    models = {"logistic": LogisticRegression(), "knn": KNeighborsClassifier(n_neighbors=15),
              "forest": RandomForestClassifier(n_estimators=100, random_state=0)}
    scores = {k: round(float(cross_val_score(churn_pipeline(m), X, y, cv=5, scoring="roc_auc").mean()), 4) for k, m in models.items()}
    return {"scores": scores, "best": max(scores, key=scores.get)}


class ClipTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, low_q=0.05, high_q=0.95):
        self.low_q, self.high_q = low_q, high_q

    def fit(self, X, y=None):
        X = np.asarray(X, float)
        self.low_, self.high_ = np.quantile(X, self.low_q, axis=0), np.quantile(X, self.high_q, axis=0)
        return self

    def transform(self, X):
        return np.clip(np.asarray(X, float), self.low_, self.high_)


def ref_clip(train, test):
    tr = ClipTransformer().fit(train)
    return np.round(tr.transform(test), 3).tolist()


# ====================================================================== Day 113
day113 = L(
    113, "특성 스케일링", W, ["scaling", "knn"],
    ["StandardScaler, MinMaxScaler로 특성 크기를 맞출 수 있다.", "스케일러를 학습 데이터에만 fit해야 하는 이유를 설명할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "지금까지 여러 번 \"학습 데이터의 평균·표준편차로 표준화\"를 직접 계산했습니다. 이번 주는 이런 **전처리**를 scikit-learn 도구로 정리하고, "
        "모델과 하나로 묶는 **파이프라인**으로 3단계를 마무리합니다."),
        "quiz": [quiz("d113_review_q1", "거리 기반이라 특성 크기에 민감한 모델은?", ["결정 트리", "KNN", "랜덤 포레스트", "나이브 베이즈"], 1, "")]},
    concept={"title": "단위 맞추기", "blocks": [
        text("- **StandardScaler**: 평균 0, 표준편차 1로(z-점수)\n- **MinMaxScaler**: 최솟값 0, 최댓값 1로\n\n"
             "스케일러도 추정기라 `fit`(평균 등을 배움) → `transform`(변환)입니다. **학습 데이터로만 fit**하고 테스트에는 transform만 하세요."),
        C('''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.preprocessing import MinMaxScaler, StandardScaler

            X, y = load_wine(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            print("원본", round(KNeighborsClassifier().fit(X_train, y_train).score(X_test, y_test), 4))
            for scaler in [StandardScaler(), MinMaxScaler()]:
                scaler.fit(X_train)
                knn = KNeighborsClassifier().fit(scaler.transform(X_train), y_train)
                print(type(scaler).__name__, round(knn.score(scaler.transform(X_test), y_test), 4))
        '''),
        tip("Day 75에서 와인 데이터 KNN 정확도가 낮았던 이유가 바로 스케일이었습니다. 트리 계열은 스케일링이 필요 없지만, 해도 해가 되지는 않습니다."),
    ]},
    fill_intro="StandardScaler로 변환하세요.",
    coding_intro="스케일링 전후의 KNN 정확도를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "StandardScaler(평균 0·표준편차 1), MinMaxScaler(0~1).",
        "`fit(X_train)` → `transform(X_train)`, `transform(X_test)`.",
        "테스트로 fit하면 데이터 누수.",
        "거리·경사하강 기반 모델에 특히 중요."],
        "quiz": [
            quiz("d113_summary_q1", "MinMaxScaler 변환 후 학습 데이터의 최댓값은?", ["0", "1", "평균", "표준편차"], 1, ""),
            quiz("d113_summary_q2", "스케일러를 fit해야 하는 데이터는?", ["테스트", "학습", "전체", "검증+테스트"], 1, "")]},
    exercises=[
        ex("d113_fill_1", "fill_blank", "표준화 도구",
           "StandardScaler를 학습 데이터로 학습해 테스트 데이터를 변환한 결과(소수 넷째 자리)를 반환하세요.",
           ["scaling"], 1,
           '''
            import numpy as np
            from sklearn.preprocessing import ____


            def scale(train, test):
                scaler = StandardScaler().____(train)
                return np.round(scaler.transform(test), 4)
           ''',
           [t("t1", args=[[[0], [2], [4]], [[2], [6]]], ret=np.round(StandardScaler().fit([[0], [2], [4]]).transform([[2], [6]]), 4).tolist(), desc="기본", **F),
            t("h1", args=[[[1, 10], [3, 30]], [[1, 20]]], ret=np.round(StandardScaler().fit([[1, 10], [3, 30]]).transform([[1, 20]]), 4).tolist(), **F)],
           ["평균 0, 표준편차 1로 바꾸는 스케일러 클래스 이름입니다.", "학습시키는 메서드입니다."],
           '''
            import numpy as np
            from sklearn.preprocessing import StandardScaler


            def scale(train, test):
                scaler = StandardScaler().fit(train)
                return np.round(scaler.transform(test), 4)
           ''', mode="function", name="scale", time_limit=TL),
        ex("d113_code_1", "coding", "스케일링 효과",
           "와인 데이터를 `test_size=0.3, random_state=seed, stratify=y`로 나누고, KNN(기본 설정)의 테스트 정확도를 **원본**과 **StandardScaler 적용** 두 경우로 구해 `[원본, 스케일링]`(소수 넷째 자리)을 반환하세요.",
           ["scaling", "knn"], 2,
           '''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.preprocessing import StandardScaler


            def scaling_effect(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_scaling(0), desc="시드 0", **F), t("h1", args=[2], ret=ref_scaling(2), **F)],
           ["원본으로 한 번 학습·평가하세요.", "스케일러를 학습 데이터로만 `fit`한 뒤 두 데이터를 `transform`해서 다시 학습·평가합니다."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import train_test_split
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.preprocessing import StandardScaler


            def scaling_effect(seed):
                X, y = load_wine(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                raw = KNeighborsClassifier().fit(X_train, y_train).score(X_test, y_test)
                scaler = StandardScaler().fit(X_train)
                knn = KNeighborsClassifier().fit(scaler.transform(X_train), y_train)
                scaled = knn.score(scaler.transform(X_test), y_test)
                return [round(raw, 4), round(scaled, 4)]
           ''', mode="function", name="scaling_effect", time_limit=TL),
    ])

# ====================================================================== Day 114
day114 = L(
    114, "범주형 인코딩", W, ["encoding", "pandas_transform"],
    ["원-핫 인코딩으로 범주형 특성을 숫자로 바꿀 수 있다.", "처음 보는 범주(handle_unknown)를 안전하게 처리할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 숫자 특성의 크기를 맞추는 스케일링을 배웠습니다. 문자로 된 특성은 어떻게 할까요?",
            "quiz": [quiz("d114_review_q1", "모델이 직접 다룰 수 있는 값은?", ["문자열", "숫자", "둘 다", "날짜만"], 1, "")]},
    concept={"title": "글자 범주를 숫자로", "blocks": [
        text("\"basic/standard/premium\" 같은 범주를 0, 1, 2로 바꾸면 모델이 \"premium은 basic의 2배\" 같은 없는 순서를 배울 수 있습니다. **원-핫 인코딩**은 범주마다 0/1 열을 하나씩 만듭니다."),
        C('''
            import numpy as np
            import pandas as pd
            from sklearn.preprocessing import OneHotEncoder

            plans = np.array(["basic", "premium", "basic", "standard"]).reshape(-1, 1)
            enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore").fit(plans)
            print(enc.categories_)
            print(enc.transform([["premium"], ["gold"]]))
            print(pd.get_dummies(pd.Series(["A", "B", "A"]), dtype=int))
        '''),
        tip("`handle_unknown=\"ignore\"`를 주면 학습 때 없던 범주(\"gold\")가 들어와도 오류 없이 모두 0인 행이 됩니다. pandas의 `get_dummies`는 빠르게 볼 때 편하지만, 학습·테스트 열을 맞춰야 하니 모델용으로는 OneHotEncoder가 안전합니다."),
    ]},
    fill_intro="원-핫 인코더를 만드세요.",
    coding_intro="범주 목록과 변환 결과를 확인하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "범주형 → 원-핫(범주마다 0/1 열).",
        "`OneHotEncoder(handle_unknown=\"ignore\")`로 새 범주 대비.",
        "`categories_`로 배운 범주 확인.",
        "순서 없는 범주를 0, 1, 2로 바꾸면 없는 순서가 생긴다."],
        "quiz": [
            quiz("d114_summary_q1", "범주 3개를 원-핫 인코딩하면 열 수는?", ["1", "2", "3", "6"], 2, ""),
            quiz("d114_summary_q2", "handle_unknown=\"ignore\"에서 새 범주의 변환 결과는?", ["오류", "모두 0", "모두 1", "첫 범주로"], 1, "")]},
    exercises=[
        ex("d114_fill_1", "fill_blank", "인코더 만들기",
           "값 목록으로 원-핫 인코더를 학습해 범주 수를 반환하세요.",
           ["encoding"], 1,
           '''
            import numpy as np
            from sklearn.preprocessing import ____


            def category_count(values):
                enc = OneHotEncoder().fit(np.array(values).reshape(-1, ____))
                return len(enc.categories_[0])
           ''',
           [t("t1", args=[["a", "b", "a", "c"]], ret=3, desc="기본"), t("h1", args=[["x"]], ret=1)],
           ["원-핫 인코더 클래스 이름입니다.", "열 하나짜리 2차원으로 바꾸려면 열 수를 1로 줍니다."],
           '''
            import numpy as np
            from sklearn.preprocessing import OneHotEncoder


            def category_count(values):
                enc = OneHotEncoder().fit(np.array(values).reshape(-1, 1))
                return len(enc.categories_[0])
           ''', mode="function", name="category_count", time_limit=TL),
        ex("d114_code_1", "coding", "원-핫 변환",
           "값 목록으로 `OneHotEncoder(sparse_output=False, handle_unknown=\"ignore\")`를 학습하고, `[\"unknown\"]`과 `[목록의 첫 값]` 두 행을 변환하세요. "
           "`[범주 리스트, 변환 결과(정수 리스트의 리스트)]`를 반환합니다.",
           ["encoding"], 2,
           '''
            import numpy as np
            from sklearn.preprocessing import OneHotEncoder


            def encode(values):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[["basic", "premium", "basic", "standard"]], ret=ref_onehot(["basic", "premium", "basic", "standard"]), desc="요금제"),
            t("h1", args=[["서울", "부산"]], ret=ref_onehot(["서울", "부산"]))],
           ["값을 `(n, 1)` 모양으로 바꿔 fit 하세요.", "`enc.transform([[\"unknown\"], [values[0]]])`의 결과를 `astype(int)`로."],
           '''
            import numpy as np
            from sklearn.preprocessing import OneHotEncoder


            def encode(values):
                enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
                enc.fit(np.array(values).reshape(-1, 1))
                encoded = enc.transform([["unknown"], [values[0]]]).astype(int)
                return [enc.categories_[0].tolist(), encoded.tolist()]
           ''', mode="function", name="encode", time_limit=TL),
    ])

# ====================================================================== Day 115
imp_cases = [(([[1, None], [3, 4], [None, 8]], "mean"), "t1", "평균"), (([[1, 2], [None, 2], [5, 9], [7, None]], "median"), "h1", ""),
             (([[1, 1], [1, None], [2, 1]], "most_frequent"), "h2", "")]
day115 = L(
    115, "결측치 대체", W, ["imputation", "pandas_missing"],
    ["SimpleImputer로 결측치를 평균·중앙값·최빈값으로 채울 수 있다.", "대체 값도 학습 데이터로만 정해야 함을 안다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 범주를 원-핫 인코딩했습니다. Day 60에서는 pandas로 결측치를 채웠죠.",
            "quiz": [quiz("d115_review_q1", "학습 때 없던 범주를 안전하게 처리하는 OneHotEncoder 옵션은?", ["`sparse_output=False`", "`handle_unknown=\"ignore\"`", "`drop=\"first\"`", "`dtype=int`"], 1, "")]},
    concept={"title": "빈칸 채우기 도구", "blocks": [
        text("**SimpleImputer**는 열마다 대체 값을 학습(`fit`)하고 빈칸을 채웁니다(`transform`). `strategy`는 `mean`, `median`, `most_frequent`(범주에도 사용), `constant`가 있습니다. "
             "Day 60의 `fillna`와 같은 일이지만, 학습 데이터로 정한 값을 테스트에 그대로 적용할 수 있어 파이프라인에 넣기 좋습니다."),
        C('''
            import numpy as np
            from sklearn.impute import SimpleImputer

            train = np.array([[1, 10], [np.nan, 20], [3, np.nan], [5, 40]])
            imp = SimpleImputer(strategy="median").fit(train)
            print(imp.statistics_)
            print(imp.transform([[np.nan, np.nan]]))
        '''),
        tip("`add_indicator=True`를 주면 \"원래 비어 있었는지\" 0/1 열을 추가합니다. 비어 있다는 사실 자체가 정보일 때 유용합니다."),
    ]},
    fill_intro="중앙값으로 결측치를 채우세요.",
    coding_intro="전략별로 결측치를 채우세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`SimpleImputer(strategy=...)`: mean, median, most_frequent, constant.",
        "`statistics_`: 열별 대체 값.",
        "학습 데이터로 fit → 테스트에 transform.",
        "`add_indicator=True`로 결측 여부 열 추가."],
        "quiz": [
            quiz("d115_summary_q1", "범주형 열의 결측치에 알맞은 전략은?", ["mean", "median", "most_frequent", "없음"], 2, ""),
            quiz("d115_summary_q2", "`statistics_`에 담긴 것은?", ["결측 개수", "열별 대체 값", "정확도", "범주 목록"], 1, "")]},
    exercises=[
        ex("d115_fill_1", "fill_blank", "중앙값 대체",
           "2차원 데이터(None은 결측)를 중앙값으로 채운 결과를 반환하세요.",
           ["imputation"], 1,
           '''
            import numpy as np
            from sklearn.impute import ____


            def fill_median(rows):
                X = np.array(rows, dtype=float)
                return SimpleImputer(strategy="____").fit_transform(X)
           ''',
           [t("t1", args=[[[1, None], [3, 4], [None, 8]]], ret=ref_impute([[1, None], [3, 4], [None, 8]], "median"), desc="기본", **F),
            t("h1", args=[[[None], [10], [2], [3]]], ret=ref_impute([[None], [10], [2], [3]], "median"), **F)],
           ["결측치 대체 클래스 이름입니다.", "중앙값 전략 이름입니다."],
           '''
            import numpy as np
            from sklearn.impute import SimpleImputer


            def fill_median(rows):
                X = np.array(rows, dtype=float)
                return SimpleImputer(strategy="median").fit_transform(X)
           ''', mode="function", name="fill_median", time_limit=TL),
        ex("d115_code_1", "coding", "전략별 대체",
           "2차원 데이터(None은 결측)와 전략 이름을 받아 SimpleImputer로 채운 결과(소수 셋째 자리)를 반환하세요.",
           ["imputation"], 2,
           '''
            import numpy as np
            from sklearn.impute import SimpleImputer


            def impute(rows, strategy):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_impute(*a), desc=d, **F) for a, tid, d in imp_cases],
           ["`np.array(rows, dtype=float)`이면 None이 NaN이 됩니다.", "`np.round(..., 3)`로 정리하세요."],
           '''
            import numpy as np
            from sklearn.impute import SimpleImputer


            def impute(rows, strategy):
                X = np.array(rows, dtype=float)
                return np.round(SimpleImputer(strategy=strategy).fit_transform(X), 3)
           ''', mode="function", name="impute", time_limit=TL),
    ])

# ====================================================================== Day 116
day116 = L(
    116, "ColumnTransformer와 Pipeline", W, ["pipeline", "scaling", "encoding", "imputation"],
    ["열 종류별로 다른 전처리를 ColumnTransformer로 묶을 수 있다.", "전처리와 모델을 Pipeline으로 묶어 누수 없이 학습·평가할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "이번 주 배운 스케일링·인코딩·결측치 대체를 이제 한 번에 묶습니다.",
            "quiz": [quiz("d116_review_q1", "전처리 도구들의 공통 사용법은?", ["fit → transform", "predict → score", "fit → predict", "load → split"], 0, "")]},
    concept={"title": "전처리 + 모델 = 하나", "blocks": [
        text("**Pipeline**은 여러 단계를 이어 하나의 추정기로 만듭니다. `fit`하면 각 전처리를 학습 데이터로만 학습하고 모델까지 학습합니다. "
             "**ColumnTransformer**는 숫자 열과 범주 열에 서로 다른 전처리를 적용합니다. 이렇게 묶으면 교차 검증·그리드 탐색에서도 누수가 생기지 않습니다."),
        C('''
            import numpy as np
            import pandas as pd
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline, make_pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler

            df = pd.DataFrame({"age": [25, np.nan, 47, 33], "plan": ["basic", "premium", "basic", "standard"], "churn": [0, 0, 1, 1]})
            pre = ColumnTransformer([
                ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), ["age"]),
                ("cat", OneHotEncoder(handle_unknown="ignore"), ["plan"]),
            ])
            pipe = Pipeline([("prep", pre), ("model", LogisticRegression())])
            pipe.fit(df[["age", "plan"]], df["churn"])
            print(pipe.named_steps["prep"].transform(df[["age", "plan"]]).shape)
            print(pipe.predict(pd.DataFrame({"age": [60], "plan": ["gold"]})))
        '''),
        tip("파이프라인 단계의 설정은 `단계이름__매개변수` 형식으로 부릅니다. 예: 그리드 탐색에서 `{\"model__C\": [0.1, 1]}`(Day 118)."),
    ]},
    fill_intro="숫자 열용 전처리 파이프라인을 만드세요.",
    coding_intro="고객 이탈 데이터로 전체 파이프라인을 만드세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`Pipeline([(이름, 단계), …])` 또는 `make_pipeline(…)`.",
        "`ColumnTransformer([(이름, 변환기, 열 목록), …])`.",
        "fit 한 번으로 전처리·모델 모두 학습 데이터 기준.",
        "설정 접근: `단계이름__매개변수`."],
        "quiz": [
            quiz("d116_summary_q1", "파이프라인의 가장 큰 장점은?", ["빠르다", "전처리 누수를 막고 코드를 하나로 묶는다", "정확도 100%", "GPU 사용"], 1, ""),
            quiz("d116_summary_q2", "숫자 열과 범주 열에 다른 처리를 하는 도구는?", ["Pipeline", "ColumnTransformer", "GridSearchCV", "PCA"], 1, "")]},
    exercises=[
        ex("d116_fill_1", "fill_blank", "숫자 전처리 파이프라인",
           "중앙값 대체 → 표준화 파이프라인을 만들어 데이터를 변환한 결과(소수 넷째 자리)를 반환하세요.",
           ["pipeline", "imputation", "scaling"], 1,
           '''
            import numpy as np
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import ____
            from sklearn.preprocessing import StandardScaler


            def numeric_prep(rows):
                X = np.array(rows, dtype=float)
                pipe = make_pipeline(SimpleImputer(strategy="median"), ____())
                return np.round(pipe.fit_transform(X), 4)
           ''',
           [t("t1", args=[[[1], [None], [3]]], ret=np.round(make_pipeline(SimpleImputer(strategy="median"), StandardScaler()).fit_transform(np.array([[1], [np.nan], [3]])), 4).tolist(), desc="기본", **F),
            t("h1", args=[[[2, 5], [4, None], [None, 1]]], ret=np.round(make_pipeline(SimpleImputer(strategy="median"), StandardScaler()).fit_transform(np.array([[2, 5], [4, np.nan], [np.nan, 1]])), 4).tolist(), **F)],
           ["단계들을 이어 파이프라인을 만드는 함수 이름입니다(make_…).", "표준화 스케일러 클래스 이름입니다."],
           '''
            import numpy as np
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler


            def numeric_prep(rows):
                X = np.array(rows, dtype=float)
                pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
                return np.round(pipe.fit_transform(X), 4)
           ''', mode="function", name="numeric_prep", time_limit=TL),
        ex("d116_code_1", "coding", "이탈 예측 파이프라인",
           "주어진 `churn_data(400, seed)`로 X(`churn` 제외)와 y(`churn`)를 만들고 `test_size=0.25, random_state=seed, stratify=y`로 나누세요. 파이프라인:\n\n"
           "- 숫자 열 `age, monthly, complaints`: 중앙값 대체 → 표준화\n- 범주 열 `plan, region`: `OneHotEncoder(handle_unknown=\"ignore\")`\n- 모델: `LogisticRegression()`\n\n"
           "`[전처리 후 특성 수, 테스트 정확도(소수 넷째 자리)]`를 반환하세요. 전처리 단계 이름은 `prep`, 모델 단계는 `model`.",
           ["pipeline", "scaling", "encoding", "imputation"], 3,
           '''
            import numpy as np
            import pandas as pd
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import Pipeline, make_pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler
''' + CHURN_HELPER + '''

            def churn_model(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_churn(0), desc="시드 0", **F), t("h1", args=[1], ret=ref_churn(1), **F)],
           ["`df.drop(columns=\"churn\")`, `df[\"churn\"]`로 X, y를 나누세요.",
            "개념 설명의 ColumnTransformer 구조를 그대로 쓰되 열 목록만 바꾸면 됩니다.",
            "특성 수는 `pipe.named_steps[\"prep\"].transform(X_test).shape[1]`."],
           '''
            import numpy as np
            import pandas as pd
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import Pipeline, make_pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler
''' + CHURN_HELPER + '''

            def churn_model(seed):
                df = churn_data(400, seed)
                X, y = df.drop(columns="churn"), df["churn"]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                pre = ColumnTransformer([
                    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
                     ["age", "monthly", "complaints"]),
                    ("cat", OneHotEncoder(handle_unknown="ignore"), ["plan", "region"]),
                ])
                pipe = Pipeline([("prep", pre), ("model", LogisticRegression())]).fit(X_train, y_train)
                n_features = pipe.named_steps["prep"].transform(X_test).shape[1]
                return [int(n_features), round(pipe.score(X_test, y_test), 4)]
           ''', mode="function", name="churn_model", time_limit=TL),
    ])

# ====================================================================== Day 117
day117 = L(
    117, "특성 선택", W, ["feature_selection", "pipeline"],
    ["통계 점수로 유용한 특성 k개를 고르는 SelectKBest를 쓸 수 있다.", "특성 수에 따른 성능 변화를 파이프라인으로 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 전처리와 모델을 파이프라인으로 묶었습니다.",
            "quiz": [quiz("d117_review_q1", "파이프라인 단계의 매개변수 이름 형식은?", ["`단계.매개변수`", "`단계__매개변수`", "`매개변수_단계`", "`단계:매개변수`"], 1, "")]},
    concept={"title": "꼭 필요한 특성만", "blocks": [
        text("특성이 많다고 항상 좋은 것은 아닙니다. 쓸모없는 특성은 잡음이 되고 계산만 늘립니다. **SelectKBest**는 특성마다 정답과의 관련성 점수(분류는 `f_classif`)를 매겨 상위 k개만 남깁니다. "
             "Lasso(Day 82)나 트리 중요도(Day 103)도 특성 선택에 쓸 수 있습니다."),
        C('''
            from sklearn.datasets import load_breast_cancer
            from sklearn.feature_selection import SelectKBest, f_classif

            data = load_breast_cancer()
            selector = SelectKBest(f_classif, k=3).fit(data.data, data.target)
            print(data.feature_names[selector.get_support()])
            print(selector.transform(data.data).shape)
        '''),
        tip("특성 선택도 학습 데이터로만 해야 합니다. 전체 데이터로 고른 뒤 교차 검증하면 누수가 생겨 점수가 부풀려집니다. 파이프라인에 넣으면 자동으로 지켜집니다."),
    ]},
    fill_intro="상위 k개 특성을 고르세요.",
    coding_intro="특성 수별 정확도와 상위 3개 특성을 확인하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`SelectKBest(f_classif, k)`: 점수 상위 k개 특성.",
        "`get_support()`로 선택된 특성 확인.",
        "특성 선택도 학습 데이터로만 → 파이프라인에 넣기.",
        "Lasso·트리 중요도도 선택에 쓸 수 있다."],
        "quiz": [
            quiz("d117_summary_q1", "`get_support()`가 돌려주는 것은?", ["점수", "선택 여부(불리언) 배열", "정확도", "특성 이름"], 1, ""),
            quiz("d117_summary_q2", "특성 선택을 전체 데이터로 하면 생기는 문제는?", ["속도 저하", "데이터 누수", "과소적합", "결측치"], 1, "")]},
    exercises=[
        ex("d117_fill_1", "fill_blank", "상위 k개",
           "유방암 데이터 전체에서 `f_classif` 기준 상위 `k`개 특성을 고른 뒤의 데이터 모양을 반환하세요.",
           ["feature_selection"], 1,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.feature_selection import ____, f_classif


            def selected_shape(k):
                X, y = load_breast_cancer(return_X_y=True)
                return list(SelectKBest(f_classif, k=____).fit_transform(X, y).shape)
           ''',
           [t("t1", args=[5], ret=[569, 5], desc="5개"), t("h1", args=[1], ret=[569, 1])],
           ["상위 k개를 고르는 클래스 이름입니다.", "고를 개수로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.feature_selection import SelectKBest, f_classif


            def selected_shape(k):
                X, y = load_breast_cancer(return_X_y=True)
                return list(SelectKBest(f_classif, k=k).fit_transform(X, y).shape)
           ''', mode="function", name="selected_shape", time_limit=TL),
        ex("d117_code_1", "coding", "특성 수 실험",
           "유방암 데이터를 `test_size=0.3, random_state=seed, stratify=y`로 나누고, `ks`의 각 k마다 `make_pipeline(StandardScaler(), SelectKBest(f_classif, k=k), LogisticRegression())`의 테스트 정확도(소수 넷째 자리)를 구하세요. "
           "또 학습 데이터로 고른 상위 3개 특성 이름을 구해 `[정확도 리스트, 이름 리스트]`를 반환합니다.",
           ["feature_selection", "pipeline"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.feature_selection import SelectKBest, f_classif
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler


            def k_experiment(ks, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[1, 5, 30], 0], ret=ref_kbest([1, 5, 30], 0), desc="1·5·30", **F), t("h1", args=[[10], 3], ret=ref_kbest([10], 3), **F)],
           ["k마다 파이프라인을 새로 만들어 학습·평가하세요.", "이름은 `SelectKBest(f_classif, k=3).fit(X_train, y_train)`의 `get_support()`로 `feature_names`를 거릅니다."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.feature_selection import SelectKBest, f_classif
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler


            def k_experiment(ks, seed):
                data = load_breast_cancer()
                X_train, X_test, y_train, y_test = train_test_split(
                    data.data, data.target, test_size=0.3, random_state=seed, stratify=data.target
                )
                scores = []
                for k in ks:
                    pipe = make_pipeline(StandardScaler(), SelectKBest(f_classif, k=k), LogisticRegression())
                    scores.append(round(pipe.fit(X_train, y_train).score(X_test, y_test), 4))
                selector = SelectKBest(f_classif, k=3).fit(X_train, y_train)
                return [scores, [str(name) for name in data.feature_names[selector.get_support()]]]
           ''', mode="function", name="k_experiment", time_limit=TL),
    ])

# ====================================================================== Day 118 (project)
PIPE_SRC = '''
            def make_pipe(model):
                pre = ColumnTransformer([
                    ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
                     ["age", "monthly", "complaints"]),
                    ("cat", OneHotEncoder(handle_unknown="ignore"), ["plan", "region"]),
                ])
                return Pipeline([("prep", pre), ("model", model)])
'''
IMPORTS = '''
            import numpy as np
            import pandas as pd
            from sklearn.compose import ColumnTransformer
            from sklearn.impute import SimpleImputer
            from sklearn.pipeline import Pipeline, make_pipeline
            from sklearn.preprocessing import OneHotEncoder, StandardScaler
'''
day118 = L(
    118, "프로젝트: 전체 파이프라인", W, ["pipeline", "hyperparameter", "roc_auc", "cross_validation"],
    ["데이터 이해 → 파이프라인 → 그리드 탐색 → 테스트 평가의 전체 머신러닝 프로젝트를 수행할 수 있다."],
    review={"title": "프로젝트 준비", "content_md": (
        "오늘은 3단계에서 배운 것을 모아 **고객 이탈 예측** 프로젝트를 합니다.\n\n"
        "1. 이탈 비율 확인(불균형 여부)\n2. 전처리 + 모델 파이프라인\n3. AUC 기준 그리드 탐색(`model__C`)\n4. 테스트 AUC로 최종 확인"),
        "quiz": [quiz("d118_review_q1", "이탈 고객이 적은(불균형) 데이터에서 정확도 대신 볼 지표는?", ["inertia", "AUC·F1", "R²", "MSE"], 1, "")]},
    concept={"title": "파이프라인 + 그리드 탐색", "blocks": [
        text("파이프라인을 `GridSearchCV`에 넣으면 교차 검증의 각 겹마다 전처리가 다시 학습되어 누수가 없습니다. 모델 매개변수는 `model__C`처럼 단계 이름과 함께 씁니다."),
        C('''
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import GridSearchCV
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler

            X, y = load_breast_cancer(return_X_y=True)
            pipe = Pipeline([("scale", StandardScaler()), ("model", LogisticRegression())])
            grid = GridSearchCV(pipe, {"model__C": [0.01, 0.1, 1, 10]}, cv=5, scoring="roc_auc").fit(X, y)
            print(grid.best_params_, round(grid.best_score_, 4))
        '''),
        tip("프로젝트 보고에는 최종 숫자뿐 아니라 \"이탈률 몇 %인 데이터에서, 어떤 전처리와 모델로, 교차 검증 AUC 얼마 → 테스트 AUC 얼마\"처럼 맥락을 함께 적으세요."),
    ]},
    fill_intro="이탈 비율을 계산하세요.",
    coding_intro="프로젝트 전체를 완성하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "프로젝트 흐름: 데이터 확인 → 파이프라인 → 탐색 → 테스트.",
        "파이프라인 + GridSearchCV = 누수 없는 탐색.",
        "불균형이면 AUC·F1로 평가.",
        "결과는 맥락과 함께 보고한다."],
        "quiz": [
            quiz("d118_summary_q1", "그리드 탐색에서 파이프라인의 LogisticRegression C를 지정하는 이름은?", ["`C`", "`model__C`", "`LogisticRegression.C`", "`prep__C`"], 1, ""),
            quiz("d118_summary_q2", "최종 성능 보고에 쓰는 것은?", ["best_score_", "테스트 점수", "학습 점수", "inertia"], 1, "")]},
    exercises=[
        ex("d118_fill_1", "fill_blank", "이탈 비율",
           "주어진 `churn_data(n, 0)`의 이탈 비율(`churn` 평균, 소수 넷째 자리)을 반환하세요.",
           ["pandas_basics"], 1,
           IMPORTS + CHURN_HELPER + '''

            def churn_rate(n):
                df = churn_data(n, 0)
                return round(float(df["____"].____()), 4)
           ''',
           [t("t1", args=[600], ret=round(float(churn_data(600, 0)["churn"].mean()), 4), desc="600명", **F), t("h1", args=[100], ret=round(float(churn_data(100, 0)["churn"].mean()), 4), **F)],
           ["정답 열 이름입니다.", "0/1 열의 평균이 곧 비율입니다."],
           IMPORTS + CHURN_HELPER + '''

            def churn_rate(n):
                df = churn_data(n, 0)
                return round(float(df["churn"].mean()), 4)
           ''', mode="function", name="churn_rate", time_limit=TL),
        ex("d118_code_1", "coding", "이탈 예측 프로젝트",
           "`churn_data(600, seed)`로 데이터를 만들고 `test_size=0.25, random_state=seed, stratify=y`로 나누세요. 주어진 `make_pipe(LogisticRegression())`로 "
           "`{\"model__C\": [0.01, 0.1, 1, 10]}`를 5-겹, `scoring=\"roc_auc\"`로 그리드 탐색합니다. 반환값:\n\n"
           "- `best_C`(실수), `cv_auc`, `test_auc`(테스트 양성 확률의 AUC), `churn_rate`(전체 y 평균) — 숫자는 소수 넷째 자리",
           ["pipeline", "hyperparameter", "roc_auc"], 3,
           IMPORTS + '''            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import roc_auc_score
            from sklearn.model_selection import GridSearchCV, train_test_split
''' + CHURN_HELPER + PIPE_SRC + '''

            def churn_project(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_project(0), desc="시드 0", **F), t("h1", args=[3], ret=ref_project(3), **F)],
           ["그리드 탐색 객체로 `predict_proba(X_test)[:, 1]`을 구해 `roc_auc_score`에 넣으세요.", "`float(grid.best_params_[\"model__C\"])`."],
           IMPORTS + '''            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import roc_auc_score
            from sklearn.model_selection import GridSearchCV, train_test_split
''' + CHURN_HELPER + PIPE_SRC + '''

            def churn_project(seed):
                df = churn_data(600, seed)
                X, y = df.drop(columns="churn"), df["churn"]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                grid = GridSearchCV(make_pipe(LogisticRegression()), {"model__C": [0.01, 0.1, 1, 10]}, cv=5, scoring="roc_auc")
                grid.fit(X_train, y_train)
                test_auc = roc_auc_score(y_test, grid.predict_proba(X_test)[:, 1])
                return {
                    "best_C": float(grid.best_params_["model__C"]),
                    "cv_auc": round(float(grid.best_score_), 4),
                    "test_auc": round(float(test_auc), 4),
                    "churn_rate": round(float(y.mean()), 4),
                }
           ''', mode="function", name="churn_project", time_limit=TL),
    ])

# ====================================================================== Day 119 (stage 3 review)
clip_cases = [(([[1], [2], [3], [4], [100]], [[0], [50], [200]]), "t1", "1열"), (([[0, 10], [5, 20], [10, 30]], [[-5, 25]]), "h1", "")]
day119 = L(
    119, "3단계 마무리 누적 복습", W, ["pipeline", "cross_validation", "random_forest", "logistic_regression", "knn"],
    ["여러 모델을 같은 파이프라인 구조로 교차 검증해 비교하고, 직접 만든 변환기를 파이프라인에 넣을 수 있다."],
    review={"title": "3단계 7주 돌아보기", "content_md": (
        "| 주차 | 주제 | 핵심 |\n|---|---|---|\n"
        "| 11 | 시작 | 데이터 분할, KNN, 추정기 API |\n| 12 | 회귀 | 선형 회귀, 평가 지표, 규제, 경사하강법 |\n"
        "| 13 | 분류 | 로지스틱, 임계값, SVM, 나이브 베이즈 |\n| 14 | 평가 | 혼동 행렬, F1, AUC, 교차 검증, 그리드 탐색 |\n"
        "| 15 | 트리·앙상블 | 불순도, 포레스트, 부스팅, 중요도 |\n| 16 | 비지도 | k-평균, DBSCAN, PCA, 이상치 |\n| 17 | 파이프라인 | 스케일링, 인코딩, 대체, ColumnTransformer |\n\n"
        "다음 4단계에서는 **PyTorch로 신경망을 직접 만들고 학습**합니다. 경사하강법(Day 83)과 로지스틱 회귀(Day 91)가 그 출발점이에요."),
        "quiz": [
            quiz("d119_review_q1", "누수 없이 교차 검증하려면 전처리를 어디에 두어야 하나?", ["교차 검증 전에 전체 데이터에", "파이프라인 안에", "테스트 데이터에만", "필요 없다"], 1, ""),
            quiz("d119_review_q2", "신경망 학습에 쓰는 기본 방법은?", ["최소제곱 공식", "경사하강법", "k-평균", "투표"], 1, "")]},
    concept={"title": "나만의 변환기", "blocks": [
        text("`BaseEstimator`, `TransformerMixin`을 상속하고 `fit`(학습 데이터로 기준을 배움, `self` 반환)과 `transform`(변환)을 만들면 파이프라인에 넣을 수 있는 변환기가 됩니다. "
             "배운 값은 이름 끝에 `_`를 붙여 저장하는 것이 관례입니다."),
        C('''
            import numpy as np
            from sklearn.base import BaseEstimator, TransformerMixin

            class LogTransformer(BaseEstimator, TransformerMixin):
                def fit(self, X, y=None):
                    return self

                def transform(self, X):
                    return np.log1p(np.asarray(X, dtype=float))

            print(LogTransformer().fit_transform([[0], [9], [99]]).round(3))
        '''),
        tip("도전 문제는 학습 데이터의 분위수(예: 5%, 95%)로 극단값을 잘라내는 변환기입니다. `np.quantile(X, q, axis=0)`과 `np.clip`을 쓰세요."),
    ]},
    fill_intro="파이프라인 단계 이름 목록을 확인하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "3단계 마무리", "points": [
        "머신러닝 = 데이터 → 전처리 → 모델 → 평가 → 개선의 반복.",
        "파이프라인으로 누수 없이, 교차 검증으로 공정하게.",
        "문제에 맞는 지표(F1·AUC·R²)를 고른다.",
        "다음: 4단계 PyTorch 딥러닝."],
        "quiz": [
            quiz("d119_summary_q1", "직접 만든 변환기의 `fit`이 돌려줘야 하는 것은?", ["None", "self", "변환 결과", "점수"], 1, ""),
            quiz("d119_summary_q2", "4단계에서 쓸 딥러닝 라이브러리는?", ["scikit-learn", "PyTorch", "pandas", "matplotlib"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d119_fill_1", "fill_blank", "단계 이름",
           "스케일러와 모델로 만든 파이프라인의 단계 이름 리스트를 반환하세요.",
           ["pipeline"], 1,
           '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import ____
            from sklearn.preprocessing import StandardScaler


            def step_names():
                pipe = Pipeline([("scale", StandardScaler()), ("model", LogisticRegression())])
                return list(pipe.____.keys())
           ''',
           [t("t1", args=[], ret=["scale", "model"], desc="두 단계")],
           ["단계 목록으로 파이프라인을 만드는 클래스 이름입니다.", "이름 → 단계 딕셔너리 속성입니다(named_…)."],
           '''
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler


            def step_names():
                pipe = Pipeline([("scale", StandardScaler()), ("model", LogisticRegression())])
                return list(pipe.named_steps.keys())
           ''', mode="function", name="step_names", time_limit=TL),
        ex("d119_code_1", "coding", "최종 모델 비교",
           "`churn_data(600, seed)` 전체로, 주어진 `make_pipe`에 `LogisticRegression()`(`logistic`), `KNeighborsClassifier(n_neighbors=15)`(`knn`), "
           "`RandomForestClassifier(n_estimators=100, random_state=0)`(`forest`)를 넣어 5-겹 교차 검증 AUC 평균(소수 넷째 자리)을 `scores`로, 최고 모델 이름을 `best`로 반환하세요.",
           ["pipeline", "cross_validation", "roc_auc"], 3,
           IMPORTS + '''            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import cross_val_score
            from sklearn.neighbors import KNeighborsClassifier
''' + CHURN_HELPER + PIPE_SRC + '''

            def final_comparison(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_final(0), desc="시드 0", **F),
            t("h1", args=[1], ret=ref_final(1), desc="다른 시드", **F)],
           ["모델 딕셔너리를 돌며 `cross_val_score(make_pipe(모델), X, y, cv=5, scoring=\"roc_auc\")`.", "최고 모델은 `max(scores, key=scores.get)`."],
           IMPORTS + '''            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import cross_val_score
            from sklearn.neighbors import KNeighborsClassifier
''' + CHURN_HELPER + PIPE_SRC + '''

            def final_comparison(seed):
                df = churn_data(600, seed)
                X, y = df.drop(columns="churn"), df["churn"]
                models = {"logistic": LogisticRegression(), "knn": KNeighborsClassifier(n_neighbors=15),
                          "forest": RandomForestClassifier(n_estimators=100, random_state=0)}
                scores = {}
                for name, model in models.items():
                    auc = cross_val_score(make_pipe(model), X, y, cv=5, scoring="roc_auc").mean()
                    scores[name] = round(float(auc), 4)
                return {"scores": scores, "best": max(scores, key=scores.get)}
           ''', mode="function", name="final_comparison", time_limit=120),
        ex("d119_code_2", "coding", "[도전] 극단값 자르기 변환기",
           "`ClipTransformer(low_q=0.05, high_q=0.95)` 변환기를 만드세요. `fit`은 학습 데이터 열마다 `low_q`, `high_q` 분위수를 `low_`, `high_`로 저장하고, "
           "`transform`은 값을 그 범위로 자릅니다(`np.clip`). `check`는 채점용으로 `[[변환 결과(소수 셋째 자리)]]`를 돌려줍니다.",
           ["pipeline", "class", "numpy_aggregate"], 3,
           '''
            import numpy as np
            from sklearn.base import BaseEstimator, TransformerMixin

            # 여기에 ClipTransformer 클래스를 작성하세요


            def check(train, test):
                transformer = ClipTransformer().fit(train)
                return np.round(transformer.transform(test), 3)
           ''',
           [t(tid, args=list(a), ret=ref_clip(*a), desc=d, **F) for a, tid, d in clip_cases],
           ["`__init__`에서 `low_q`, `high_q`를 같은 이름의 속성으로 저장하세요(scikit-learn 관례).",
            "`fit`: `np.quantile(X, self.low_q, axis=0)` 등을 저장하고 `self` 반환.", "`transform`: `np.clip(X, self.low_, self.high_)`."],
           '''
            import numpy as np
            from sklearn.base import BaseEstimator, TransformerMixin


            class ClipTransformer(BaseEstimator, TransformerMixin):
                def __init__(self, low_q=0.05, high_q=0.95):
                    self.low_q = low_q
                    self.high_q = high_q

                def fit(self, X, y=None):
                    X = np.asarray(X, dtype=float)
                    self.low_ = np.quantile(X, self.low_q, axis=0)
                    self.high_ = np.quantile(X, self.high_q, axis=0)
                    return self

                def transform(self, X):
                    return np.clip(np.asarray(X, dtype=float), self.low_, self.high_)


            def check(train, test):
                transformer = ClipTransformer().fit(train)
                return np.round(transformer.transform(test), 3)
           ''', mode="function", name="check", checks={"required_syntax": ["class"]}, required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day113, day114, day115, day116, day117, day118, day119])
