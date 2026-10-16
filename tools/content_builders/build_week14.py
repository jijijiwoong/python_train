"""Week 14 (Day 92-98): 모델 평가와 교차 검증."""
import sys
from pathlib import Path

import numpy as np
from sklearn.datasets import load_breast_cancer, load_iris, load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 14, "ml", 60
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
def ref_counts(yt, yp):
    yt, yp = np.array(yt), np.array(yp)
    return {"tp": int(((yt == 1) & (yp == 1)).sum()), "fp": int(((yt == 0) & (yp == 1)).sum()),
            "fn": int(((yt == 1) & (yp == 0)).sum()), "tn": int(((yt == 0) & (yp == 0)).sum())}


def ref_prf(yt, yp):
    return {"precision": round(float(precision_score(yt, yp, zero_division=0)), 4),
            "recall": round(float(recall_score(yt, yp, zero_division=0)), 4),
            "f1": round(float(f1_score(yt, yp, zero_division=0)), 4)}


def ref_auc(seed):
    Xtr, Xte, ytr, yte = cancer_split(seed)
    proba = LogisticRegression().fit(Xtr, ytr).predict_proba(Xte)[:, 1]
    rnd = np.random.default_rng(seed).random(len(yte))
    return [round(float(roc_auc_score(yte, proba)), 4), round(float(roc_auc_score(yte, rnd)), 4)]


def ref_cv(folds):
    X, y = load_wine(return_X_y=True)
    out = {}
    for name, m in [("knn", KNeighborsClassifier()), ("tree", DecisionTreeClassifier(random_state=0))]:
        s = cross_val_score(m, X, y, cv=folds)
        out[name] = [round(float(s.mean()), 4), round(float(s.std()), 4)]
    return out


def ref_depths(depths, seed):
    X, y = load_breast_cancer(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    out = []
    for d in depths:
        m = DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr)
        out.append([round(m.score(Xtr, ytr), 4), round(m.score(Xte, yte), 4)])
    return out


def ref_grid(ks, seed):
    X, y = load_iris(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    g = GridSearchCV(KNeighborsClassifier(), {"n_neighbors": ks}, cv=5).fit(Xtr, ytr)
    return [int(g.best_params_["n_neighbors"]), round(float(g.best_score_), 4), round(float(g.score(Xte, yte)), 4)]


def ref_selection(seed):
    Xtr, Xte, ytr, yte = cancer_split(seed)
    g = GridSearchCV(SVC(), {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]}, cv=5, scoring="f1").fit(Xtr, ytr)
    pred = g.predict(Xte)
    cm = confusion_matrix(yte, pred)
    return {"best": {"C": float(g.best_params_["C"]), "kernel": g.best_params_["kernel"]},
            "cv_f1": round(float(g.best_score_), 4), "test_f1": round(float(f1_score(yte, pred)), 4), "matrix": cm.tolist()}


def ref_manual_cv(k):
    X, y = load_iris(return_X_y=True)
    scores = []
    for tr, te in KFold(n_splits=k, shuffle=True, random_state=0).split(X):
        scores.append(KNeighborsClassifier().fit(X[tr], y[tr]).score(X[te], y[te]))
    sk = cross_val_score(KNeighborsClassifier(), X, y, cv=KFold(n_splits=k, shuffle=True, random_state=0))
    return [round(float(np.mean(scores)), 4), round(float(sk.mean()), 4)]


YT1 = [1, 0, 1, 1, 0, 0, 1, 0]
YP1 = [1, 0, 0, 1, 1, 0, 1, 0]
cm_cases = [((YT1, YP1), "t1", "8개"), (([1, 1, 1], [0, 0, 0]), "h1", ""), (([0, 0, 1, 1], [1, 1, 1, 1]), "h2", "")]
SPLIT_HELPER = '''
            def cancer_split(seed):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
                mean, std = X_train.mean(axis=0), X_train.std(axis=0)
                return (X_train - mean) / std, (X_test - mean) / std, y_train, y_test
'''

# ====================================================================== Day 92
day92 = L(
    92, "정확도의 함정과 혼동 행렬", W, ["confusion_matrix", "sklearn_api"],
    ["불균형 데이터에서 정확도만 보면 위험한 이유를 설명할 수 있다.", "TP, FP, FN, TN과 혼동 행렬을 읽고 계산할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "13주차에는 여러 분류 모델을 정확도로 비교했습니다. 이번 주는 **평가를 제대로 하는 법**을 배웁니다. 정확도 하나만으로는 놓치는 것이 많습니다."),
        "quiz": [quiz("d92_review_q1", "환자 100명 중 2명만 병이 있을 때, \"모두 정상\"이라고 하는 모델의 정확도는?", ["2%", "50%", "98%", "100%"], 2,
                      "정확도는 높지만 환자를 한 명도 못 찾는 쓸모없는 모델입니다.")]},
    concept={"title": "무엇을 맞히고 무엇을 틀렸나", "blocks": [
        text("이진 분류의 결과는 네 가지입니다(양성 = 1).\n\n"
             "| | 예측 양성 | 예측 음성 |\n|---|---|---|\n| **실제 양성** | TP (맞게 찾음) | FN (놓침) |\n| **실제 음성** | FP (헛잡음) | TN (맞게 거름) |\n\n"
             "scikit-learn의 `confusion_matrix(y_true, y_pred)`는 `[[TN, FP], [FN, TP]]` 순서로 돌려줍니다(행 = 실제, 열 = 예측, 0 먼저)."),
        C('''
            from sklearn.metrics import confusion_matrix

            y_true = [1, 0, 1, 1, 0, 0, 1, 0]
            y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
            cm = confusion_matrix(y_true, y_pred)
            print(cm)
            tn, fp, fn, tp = cm.ravel()
            print("TP", tp, "FP", fp, "FN", fn, "TN", tn)
        '''),
        tip("다중 분류의 혼동 행렬은 클래스 수 × 클래스 수 표입니다. 대각선이 맞힌 개수이고, 대각선 밖의 큰 값이 \"자주 헷갈리는 쌍\"입니다."),
    ]},
    fill_intro="혼동 행렬을 구하세요.",
    coding_intro="TP, FP, FN, TN을 직접 세세요(`confusion_matrix` 사용 금지).",
    summary={"title": "오늘의 핵심 정리", "points": [
        "불균형 데이터에서 정확도는 속기 쉽다.",
        "TP·FN(실제 양성), FP·TN(실제 음성).",
        "`confusion_matrix` → `[[TN, FP], [FN, TP]]`.",
        "대각선 = 맞힌 것, 그 밖 = 틀린 유형."],
        "quiz": [
            quiz("d92_summary_q1", "병이 있는데 정상으로 예측한 경우는?", ["TP", "FP", "FN", "TN"], 2, ""),
            quiz("d92_summary_q2", "`confusion_matrix`의 [0][1] 칸은?", ["TP", "FP", "FN", "TN"], 1, "행 0(실제 음성), 열 1(예측 양성)")]},
    exercises=[
        ex("d92_fill_1", "fill_blank", "혼동 행렬",
           "실제값·예측값으로 혼동 행렬을 리스트로 반환하세요.",
           ["confusion_matrix"], 1,
           '''
            from sklearn.metrics import ____


            def matrix(y_true, y_pred):
                return confusion_matrix(____, y_pred).tolist()
           ''',
           [t(tid, args=list(a), ret=confusion_matrix(*a, labels=[0, 1]).tolist() if tid != "h1" else [[0, 0], [3, 0]], desc=d)
            for a, tid, d in cm_cases if tid != "h1"] + [t("h1", args=[[1, 1, 0], [0, 1, 0]], ret=confusion_matrix([1, 1, 0], [0, 1, 0]).tolist())],
           ["혼동 행렬을 계산하는 함수 이름입니다.", "첫 번째 인자는 실제값입니다."],
           '''
            from sklearn.metrics import confusion_matrix


            def matrix(y_true, y_pred):
                return confusion_matrix(y_true, y_pred).tolist()
           ''', mode="function", name="matrix", time_limit=TL),
        ex("d92_code_1", "coding", "네 가지 개수",
           "실제값과 예측값(0/1)으로 `{\"tp\", \"fp\", \"fn\", \"tn\"}` 개수 딕셔너리를 반환하세요. NumPy 마스크로 직접 세고 `confusion_matrix`는 쓸 수 없습니다.",
           ["confusion_matrix", "numpy_indexing"], 2,
           '''
            import numpy as np


            def counts(y_true, y_pred):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_counts(*a), desc=d) for a, tid, d in cm_cases],
           ["두 목록을 배열로 바꾸세요.", "TP는 `((yt == 1) & (yp == 1)).sum()`처럼 두 조건을 `&`로 묶어 셉니다.", "`int()`로 바꿔 넣으세요."],
           '''
            import numpy as np


            def counts(y_true, y_pred):
                yt = np.array(y_true)
                yp = np.array(y_pred)
                return {"tp": int(((yt == 1) & (yp == 1)).sum()), "fp": int(((yt == 0) & (yp == 1)).sum()),
                        "fn": int(((yt == 1) & (yp == 0)).sum()), "tn": int(((yt == 0) & (yp == 0)).sum())}
           ''', mode="function", name="counts", checks={"forbidden_calls": ["confusion_matrix"]}, time_limit=TL),
    ])

# ====================================================================== Day 93
prf_cases = [((YT1, YP1), "t1", "기본"), (([1, 0, 1, 0], [1, 0, 1, 0]), "h1", "완벽"), (([1, 1, 0, 0], [0, 0, 0, 0]), "h2", "양성 예측 없음")]
day93 = L(
    93, "정밀도·재현율·F1", W, ["precision_recall", "confusion_matrix"],
    ["정밀도와 재현율의 뜻과 둘 사이의 균형을 설명할 수 있다.", "F1 점수를 계산하고 상황에 맞는 지표를 고를 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 TP, FP, FN, TN과 혼동 행렬을 배웠습니다.",
            "quiz": [quiz("d93_review_q1", "스팸이 아닌 메일을 스팸으로 잘못 거른 것은?", ["TP", "FP", "FN", "TN"], 1, "")]},
    concept={"title": "두 가지 질문", "blocks": [
        text("- **정밀도** = TP / (TP + FP): \"양성이라고 한 것 중 진짜 양성 비율\" → 헛잡음이 비쌀 때(스팸 필터)\n"
             "- **재현율** = TP / (TP + FN): \"진짜 양성 중 찾아낸 비율\" → 놓치면 위험할 때(암 검진)\n"
             "- **F1** = 2 × 정밀도 × 재현율 / (정밀도 + 재현율): 둘의 조화 평균\n\n임계값을 낮추면 재현율↑ 정밀도↓, 높이면 반대입니다."),
        C('''
            from sklearn.metrics import f1_score, precision_score, recall_score

            y_true = [1, 0, 1, 1, 0, 0, 1, 0]
            y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
            print(precision_score(y_true, y_pred), recall_score(y_true, y_pred), round(f1_score(y_true, y_pred), 4))
        '''),
        tip("양성 예측이 하나도 없으면 정밀도의 분모가 0이 됩니다. scikit-learn은 경고와 함께 0을 돌려주며, `zero_division=0`으로 경고를 끌 수 있습니다."),
    ]},
    fill_intro="정밀도 공식을 완성하세요.",
    coding_intro="정밀도·재현율·F1을 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "정밀도 = TP/(TP+FP), 재현율 = TP/(TP+FN).",
        "F1 = 정밀도와 재현율의 조화 평균.",
        "놓치면 위험 → 재현율, 헛잡으면 비쌈 → 정밀도.",
        "임계값으로 둘의 균형을 조절한다."],
        "quiz": [
            quiz("d93_summary_q1", "TP=8, FP=2, FN=4일 때 정밀도는?", ["0.8", "0.67", "0.5", "0.4"], 0, "8/(8+2)"),
            quiz("d93_summary_q2", "암 검진 모델에서 가장 중요하게 볼 지표는?", ["정밀도", "재현율", "정확도", "학습 시간"], 1, "")]},
    exercises=[
        ex("d93_fill_1", "fill_blank", "정밀도",
           "TP와 FP 개수로 정밀도(소수 넷째 자리)를 반환하세요. 분모가 0이면 0을 반환합니다.",
           ["precision_recall"], 1,
           '''
            def precision(tp, fp):
                if tp + fp == 0:
                    return 0
                return round(tp / (tp ____ ____), 4)
           ''',
           [t("t1", args=[8, 2], ret=0.8, desc="기본"), t("h1", args=[0, 0], ret=0), t("h2", args=[1, 2], ret=round(1 / 3, 4), **F)],
           ["분모는 \"양성이라고 예측한 전체\"입니다.", "TP에 무엇을 더해야 할까요?"],
           '''
            def precision(tp, fp):
                if tp + fp == 0:
                    return 0
                return round(tp / (tp + fp), 4)
           ''', mode="function", name="precision", time_limit=TL),
        ex("d93_code_1", "coding", "세 지표",
           "실제값·예측값으로 `{\"precision\", \"recall\", \"f1\"}`(소수 넷째 자리)를 반환하세요. 분모가 0이면 0입니다(`zero_division=0`).",
           ["precision_recall"], 2,
           '''
            from sklearn.metrics import f1_score, precision_score, recall_score


            def prf(y_true, y_pred):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_prf(*a), desc=d, **F) for a, tid, d in prf_cases],
           ["세 함수 모두 `(y_true, y_pred, zero_division=0)`로 부를 수 있습니다.", "`round(float(값), 4)`로 정리하세요."],
           '''
            from sklearn.metrics import f1_score, precision_score, recall_score


            def prf(y_true, y_pred):
                return {"precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
                        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
                        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4)}
           ''', mode="function", name="prf", time_limit=TL),
    ])

# ====================================================================== Day 94
day94 = L(
    94, "ROC 곡선과 AUC", W, ["roc_auc", "decision_boundary"],
    ["임계값을 모두 바꿔 가며 그린 ROC 곡선의 의미를 설명할 수 있다.", "AUC로 임계값과 상관없는 모델 성능을 비교할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 정밀도·재현율이 임계값에 따라 바뀌는 것을 배웠습니다.",
            "quiz": [quiz("d94_review_q1", "재현율의 다른 이름은?", ["특이도", "민감도(TPR)", "정밀도", "정확도"], 1, "")]},
    concept={"title": "모든 임계값을 한 번에", "blocks": [
        text("**ROC 곡선**은 임계값을 1에서 0까지 내리며 x축 = 거짓 양성 비율(FPR = FP/(FP+TN)), y축 = 참 양성 비율(TPR = 재현율)을 그린 것입니다. "
             "곡선 아래 넓이 **AUC**가 1이면 완벽, 0.5면 동전 던지기 수준입니다. AUC는 \"무작위로 고른 양성이 음성보다 높은 점수를 받을 확률\"로도 해석됩니다."),
        C('''
            import matplotlib.pyplot as plt
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import roc_auc_score, roc_curve
            from sklearn.model_selection import train_test_split

            X, y = load_breast_cancer(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
            mean, std = X_train.mean(axis=0), X_train.std(axis=0)
            proba = LogisticRegression().fit((X_train - mean) / std, y_train).predict_proba((X_test - mean) / std)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, proba)
            fig, ax = plt.subplots()
            ax.plot(fpr, tpr, label=f"AUC {roc_auc_score(y_test, proba):.3f}")
            ax.plot([0, 1], [0, 1], linestyle="--", label="무작위")
            ax.set_xlabel("FPR")
            ax.set_ylabel("TPR")
            ax.legend()
            print(round(roc_auc_score(y_test, proba), 4))
        '''),
        tip("AUC에는 `predict`의 0/1이 아니라 `predict_proba`의 **확률(점수)**을 넣어야 합니다."),
    ]},
    fill_intro="AUC를 계산하세요.",
    coding_intro="학습한 모델과 무작위 점수의 AUC를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "ROC: x = FPR, y = TPR(재현율), 임계값을 모두 훑는다.",
        "AUC: 1 완벽, 0.5 무작위.",
        "AUC에는 확률(점수)을 넣는다.",
        "AUC는 임계값과 무관한 비교에 좋다."],
        "quiz": [
            quiz("d94_summary_q1", "AUC 0.5의 의미는?", ["완벽", "무작위 수준", "항상 틀림", "과적합"], 1, ""),
            quiz("d94_summary_q2", "`roc_auc_score`에 넣어야 하는 것은?", ["예측 클래스(0/1)", "양성 확률", "정확도", "혼동 행렬"], 1, "")]},
    exercises=[
        ex("d94_fill_1", "fill_blank", "AUC 계산",
           "실제값과 점수로 AUC(소수 넷째 자리)를 반환하세요.",
           ["roc_auc"], 1,
           '''
            from sklearn.metrics import ____


            def auc(y_true, scores):
                return round(float(roc_auc_score(y_true, ____)), 4)
           ''',
           [t("t1", args=[[0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]], ret=0.75, desc="기본"), t("h1", args=[[0, 1], [0.2, 0.9]], ret=1.0),
            t("h2", args=[[1, 0, 1, 0], [0.3, 0.6, 0.2, 0.5]], ret=0.0)],
           ["AUC를 계산하는 함수 이름입니다.", "두 번째 인자는 점수(확률)입니다."],
           '''
            from sklearn.metrics import roc_auc_score


            def auc(y_true, scores):
                return round(float(roc_auc_score(y_true, scores)), 4)
           ''', mode="function", name="auc", time_limit=TL),
        ex("d94_code_1", "coding", "모델 vs 무작위",
           "주어진 `cancer_split(seed)`로 로지스틱 회귀를 학습해 테스트 양성 확률의 AUC를 구하고, `np.random.default_rng(seed).random(테스트 개수)`로 만든 무작위 점수의 AUC도 구하세요. "
           "`[모델 AUC, 무작위 AUC]`(소수 넷째 자리)를 반환합니다.",
           ["roc_auc", "logistic_regression", "numpy_random"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import roc_auc_score
            from sklearn.model_selection import train_test_split
''' + SPLIT_HELPER + '''

            def auc_vs_random(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_auc(0), desc="시드 0", **F), t("h1", args=[4], ret=ref_auc(4), **F)],
           ["양성 확률은 `predict_proba(X_test)[:, 1]`.", "무작위 점수는 테스트 개수만큼 만들고 같은 `y_test`로 AUC를 구합니다."],
           '''
            import numpy as np
            from sklearn.datasets import load_breast_cancer
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import roc_auc_score
            from sklearn.model_selection import train_test_split
''' + SPLIT_HELPER + '''

            def auc_vs_random(seed):
                X_train, X_test, y_train, y_test = cancer_split(seed)
                proba = LogisticRegression().fit(X_train, y_train).predict_proba(X_test)[:, 1]
                random_scores = np.random.default_rng(seed).random(len(y_test))
                return [round(float(roc_auc_score(y_test, proba)), 4), round(float(roc_auc_score(y_test, random_scores)), 4)]
           ''', mode="function", name="auc_vs_random", time_limit=TL),
    ])

# ====================================================================== Day 95
day95 = L(
    95, "교차 검증", W, ["cross_validation", "train_test"],
    ["한 번의 분할이 운에 좌우될 수 있음을 이해한다.", "cross_val_score와 KFold로 k-겹 교차 검증을 할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 ROC 곡선과 AUC를 배웠습니다.",
            "quiz": [quiz("d95_review_q1", "AUC가 1에 가까울수록?", ["무작위", "양성과 음성을 잘 구분", "과소적합", "느림"], 1, "")]},
    concept={"title": "여러 번 나눠서 평균 내기", "blocks": [
        text("데이터를 한 번만 나누면 어떤 샘플이 테스트에 들어갔는지에 따라 점수가 크게 달라질 수 있습니다. **k-겹 교차 검증**은 데이터를 k조각으로 나눠, "
             "각 조각을 한 번씩 검증용으로 쓰며 k번 학습·평가한 뒤 평균을 냅니다."),
        C('''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import KFold, cross_val_score
            from sklearn.neighbors import KNeighborsClassifier

            X, y = load_wine(return_X_y=True)
            scores = cross_val_score(KNeighborsClassifier(), X, y, cv=5)
            print(scores.round(3))
            print(round(scores.mean(), 4), round(scores.std(), 4))
            for train_idx, test_idx in KFold(n_splits=3, shuffle=True, random_state=0).split(X):
                print(len(train_idx), len(test_idx))
        '''),
        tip("분류 문제에서 `cv=5`처럼 숫자만 주면 클래스 비율을 유지하는 StratifiedKFold가 쓰입니다. 평균과 함께 **표준편차**도 보세요. 크면 결과가 불안정하다는 뜻입니다."),
    ]},
    fill_intro="교차 검증 평균 점수를 구하세요.",
    coding_intro="두 모델을 교차 검증으로 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "k-겹 교차 검증: k번 학습·평가 후 평균.",
        "`cross_val_score(모델, X, y, cv=k)`.",
        "`KFold(n_splits, shuffle, random_state).split(X)`로 직접 나누기.",
        "평균은 성능, 표준편차는 안정성."],
        "quiz": [
            quiz("d95_summary_q1", "5-겹 교차 검증에서 모델을 몇 번 학습하나?", ["1", "4", "5", "10"], 2, ""),
            quiz("d95_summary_q2", "교차 검증의 장점은?", ["빠르다", "한 번의 분할 운에 덜 좌우된다", "테스트 데이터가 필요 없다", "정확도가 오른다"], 1, "")]},
    exercises=[
        ex("d95_fill_1", "fill_blank", "교차 검증 평균",
           "iris 데이터로 KNN(기본 설정)의 `folds`-겹 교차 검증 평균 정확도(소수 넷째 자리)를 반환하세요.",
           ["cross_validation"], 1,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import ____
            from sklearn.neighbors import KNeighborsClassifier


            def cv_mean(folds):
                X, y = load_iris(return_X_y=True)
                scores = cross_val_score(KNeighborsClassifier(), X, y, cv=____)
                return round(float(scores.mean()), 4)
           ''',
           [t("t1", args=[5], ret=round(float(cross_val_score(KNeighborsClassifier(), *load_iris(return_X_y=True), cv=5).mean()), 4), desc="5겹", **F),
            t("h1", args=[3], ret=round(float(cross_val_score(KNeighborsClassifier(), *load_iris(return_X_y=True), cv=3).mean()), 4), **F)],
           ["교차 검증 점수를 구하는 함수 이름입니다.", "겹 수로 쓸 매개변수입니다."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import cross_val_score
            from sklearn.neighbors import KNeighborsClassifier


            def cv_mean(folds):
                X, y = load_iris(return_X_y=True)
                scores = cross_val_score(KNeighborsClassifier(), X, y, cv=folds)
                return round(float(scores.mean()), 4)
           ''', mode="function", name="cv_mean", time_limit=TL),
        ex("d95_code_1", "coding", "교차 검증 비교",
           "와인 데이터로 `KNeighborsClassifier()`와 `DecisionTreeClassifier(random_state=0)`를 `folds`-겹 교차 검증하고 "
           "`{\"knn\": [평균, 표준편차], \"tree\": [평균, 표준편차]}`(소수 넷째 자리)를 반환하세요.",
           ["cross_validation", "sklearn_api"], 2,
           '''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import cross_val_score
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier


            def cv_compare(folds):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[5], ret=ref_cv(5), desc="5겹", **F), t("h1", args=[3], ret=ref_cv(3), **F)],
           ["이름 → 모델을 돌며 `cross_val_score(모델, X, y, cv=folds)`.", "점수 배열의 `mean()`, `std()`를 `round(float(...), 4)`."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.model_selection import cross_val_score
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier


            def cv_compare(folds):
                X, y = load_wine(return_X_y=True)
                result = {}
                for name, model in [("knn", KNeighborsClassifier()), ("tree", DecisionTreeClassifier(random_state=0))]:
                    scores = cross_val_score(model, X, y, cv=folds)
                    result[name] = [round(float(scores.mean()), 4), round(float(scores.std()), 4)]
                return result
           ''', mode="function", name="cv_compare", time_limit=TL),
    ])

# ====================================================================== Day 96
day96 = L(
    96, "과적합과 과소적합", W, ["overfitting", "decision_tree"],
    ["학습 점수와 검증 점수의 차이로 과적합·과소적합을 진단할 수 있다.", "모델 복잡도(트리 깊이)에 따른 점수 변화를 관찰할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 교차 검증으로 안정적인 성능 추정을 했습니다.",
            "quiz": [quiz("d96_review_q1", "교차 검증 점수의 표준편차가 크다면?", ["매우 안정적", "분할에 따라 결과가 크게 흔들림", "과소적합", "정확도 100%"], 1, "")]},
    concept={"title": "외우기와 일반화 사이", "blocks": [
        text("- **과소적합**: 모델이 너무 단순해 학습 데이터도 잘 못 맞춤(학습·검증 점수 모두 낮음)\n"
             "- **과적합**: 학습 데이터를 외워 학습 점수는 높지만 검증 점수가 낮음(차이가 큼)\n\n결정 트리는 깊이(`max_depth`)를 키울수록 복잡해집니다."),
        C('''
            from sklearn.datasets import load_breast_cancer
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier

            X, y = load_breast_cancer(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            for depth in [1, 3, None]:
                model = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
                print(depth, round(model.score(X_train, y_train), 3), round(model.score(X_test, y_test), 3))
        '''),
        tip("과적합을 줄이는 방법: 모델 단순화(깊이 제한), 규제(Day 82), 데이터 늘리기, 앙상블(15주차), 딥러닝에서는 드롭아웃(20주차)."),
    ]},
    fill_intro="학습·테스트 점수 차이를 구하세요.",
    coding_intro="트리 깊이별 학습·테스트 정확도를 비교하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "과소적합: 둘 다 낮음 → 더 복잡한 모델.",
        "과적합: 학습↑ 검증↓ → 단순화·규제·데이터.",
        "`max_depth`로 트리 복잡도 조절.",
        "학습 점수만 보면 과적합을 놓친다."],
        "quiz": [
            quiz("d96_summary_q1", "학습 0.99, 검증 0.70이라면?", ["과소적합", "과적합", "정상", "데이터 누수 없음"], 1, ""),
            quiz("d96_summary_q2", "학습 0.60, 검증 0.58이라면?", ["과소적합", "과적합", "완벽", "누수"], 0, "")]},
    exercises=[
        ex("d96_fill_1", "fill_blank", "점수 차이",
           "학습 점수와 테스트 점수를 받아 `[차이(소수 넷째 자리), 과적합 의심 여부]`를 반환하세요. 차이가 `limit`보다 크면 과적합 의심입니다.",
           ["overfitting"], 1,
           '''
            def gap(train_score, test_score, limit):
                diff = round(train_score ____ test_score, 4)
                return [diff, diff ____ limit]
           ''',
           [t("t1", args=[0.99, 0.8, 0.1], ret=[0.19, True], desc="과적합", **F), t("h1", args=[0.9, 0.88, 0.05], ret=[0.02, False], **F)],
           ["학습 점수에서 테스트 점수를 빼세요.", "\"보다 크다\" 비교 연산자입니다."],
           '''
            def gap(train_score, test_score, limit):
                diff = round(train_score - test_score, 4)
                return [diff, diff > limit]
           ''', mode="function", name="gap", time_limit=TL),
        ex("d96_code_1", "coding", "깊이별 점수",
           "유방암 데이터를 `test_size=0.3, random_state=seed, stratify=y`로 나누고, `depths`의 각 깊이(`None`은 제한 없음)로 `DecisionTreeClassifier(max_depth=깊이, random_state=0)`를 학습해 "
           "`[학습 정확도, 테스트 정확도]`(소수 넷째 자리) 리스트를 반환하세요.",
           ["overfitting", "decision_tree"], 2,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier


            def depth_scores(depths, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[1, 3, None], 0], ret=ref_depths([1, 3, None], 0), desc="1·3·None", **F), t("h1", args=[[2, 6], 5], ret=ref_depths([2, 6], 5), **F)],
           ["깊이마다 새 모델을 만들어 학습하세요.", "같은 모델로 `score(X_train, y_train)`, `score(X_test, y_test)`."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.model_selection import train_test_split
            from sklearn.tree import DecisionTreeClassifier


            def depth_scores(depths, seed):
                X, y = load_breast_cancer(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                result = []
                for depth in depths:
                    model = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_train, y_train)
                    result.append([round(model.score(X_train, y_train), 4), round(model.score(X_test, y_test), 4)])
                return result
           ''', mode="function", name="depth_scores", time_limit=TL),
    ])

# ====================================================================== Day 97
day97 = L(
    97, "하이퍼파라미터 탐색", W, ["hyperparameter", "cross_validation"],
    ["GridSearchCV로 여러 하이퍼파라미터 조합을 교차 검증으로 비교할 수 있다.", "best_params_, best_score_를 해석하고 테스트로 최종 확인할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 깊이에 따른 과적합을 관찰했습니다. 적당한 깊이는 어떻게 고를까요?",
            "quiz": [quiz("d97_review_q1", "하이퍼파라미터를 고를 때 쓰면 안 되는 데이터는?", ["학습", "검증(교차 검증)", "테스트", "모두 괜찮다"], 2, "")]},
    concept={"title": "조합을 자동으로 시험하기", "blocks": [
        text("`GridSearchCV(모델, {이름: 후보 목록}, cv=k)`는 모든 조합을 교차 검증으로 평가하고 가장 좋은 조합으로 **학습 데이터 전체에 다시 학습**까지 해 둡니다. "
             "결과는 `best_params_`, `best_score_`(교차 검증 평균)에 있고, 객체 자체로 `predict`, `score`를 쓸 수 있습니다."),
        C('''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import GridSearchCV, train_test_split
            from sklearn.svm import SVC

            X, y = load_iris(return_X_y=True)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
            grid = GridSearchCV(SVC(), {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]}, cv=5)
            grid.fit(X_train, y_train)
            print(grid.best_params_, round(grid.best_score_, 4))
            print(round(grid.score(X_test, y_test), 4))
        '''),
        tip("조합 수 × 겹 수만큼 학습하므로 후보를 너무 많이 주면 오래 걸립니다. `scoring=\"f1\"`처럼 기준 지표도 바꿀 수 있어요."),
    ]},
    fill_intro="그리드 탐색을 실행하세요.",
    coding_intro="KNN의 이웃 수를 그리드 탐색으로 고르고 테스트로 확인하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "`GridSearchCV(모델, 후보 딕셔너리, cv=k).fit(X_train, y_train)`.",
        "`best_params_`, `best_score_`(교차 검증 평균).",
        "가장 좋은 조합으로 자동 재학습 → 바로 `score(X_test, y_test)`.",
        "`scoring`으로 기준 지표 지정."],
        "quiz": [
            quiz("d97_summary_q1", "후보 C 3개 × kernel 2개, cv=5면 학습 횟수(재학습 제외)는?", ["6", "10", "30", "15"], 2, ""),
            quiz("d97_summary_q2", "`best_score_`는 무엇의 점수인가?", ["테스트", "교차 검증 평균", "학습", "최악"], 1, "")]},
    exercises=[
        ex("d97_fill_1", "fill_blank", "그리드 탐색",
           "iris 전체로 `SVC`의 C 후보 `cs`를 5-겹 그리드 탐색해 가장 좋은 C 값을 반환하세요.",
           ["hyperparameter"], 1,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import ____
            from sklearn.svm import SVC


            def best_c(cs):
                X, y = load_iris(return_X_y=True)
                grid = GridSearchCV(SVC(), {"C": cs}, cv=5).fit(X, y)
                return grid.____["C"]
           ''',
           [t("t1", args=[[0.01, 1, 100]], ret=GridSearchCV(SVC(), {"C": [0.01, 1, 100]}, cv=5).fit(*load_iris(return_X_y=True)).best_params_["C"], desc="세 후보"),
            t("h1", args=[[0.001, 0.1]], ret=GridSearchCV(SVC(), {"C": [0.001, 0.1]}, cv=5).fit(*load_iris(return_X_y=True)).best_params_["C"])],
           ["그리드 탐색 클래스 이름입니다.", "가장 좋은 조합이 담긴 속성입니다(best_…)."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import GridSearchCV
            from sklearn.svm import SVC


            def best_c(cs):
                X, y = load_iris(return_X_y=True)
                grid = GridSearchCV(SVC(), {"C": cs}, cv=5).fit(X, y)
                return grid.best_params_["C"]
           ''', mode="function", name="best_c", time_limit=TL),
        ex("d97_code_1", "coding", "이웃 수 고르기",
           "iris를 `test_size=0.3, random_state=seed, stratify=y`로 나누고, 학습 데이터로 KNN의 `n_neighbors` 후보 `ks`를 5-겹 그리드 탐색하세요. "
           "`[최적 k, 교차 검증 최고 점수(소수 넷째 자리), 테스트 정확도(소수 넷째 자리)]`를 반환합니다.",
           ["hyperparameter", "knn", "cross_validation"], 2,
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import GridSearchCV, train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def tune_knn(ks, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[1, 3, 5, 7, 9], 0], ret=ref_grid([1, 3, 5, 7, 9], 0), desc="다섯 후보", **F), t("h1", args=[[2, 20], 3], ret=ref_grid([2, 20], 3), **F)],
           ["후보 딕셔너리는 `{\"n_neighbors\": ks}`.", "탐색 객체로 바로 `score(X_test, y_test)`를 부를 수 있습니다."],
           '''
            from sklearn.datasets import load_iris
            from sklearn.model_selection import GridSearchCV, train_test_split
            from sklearn.neighbors import KNeighborsClassifier


            def tune_knn(ks, seed):
                X, y = load_iris(return_X_y=True)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
                grid = GridSearchCV(KNeighborsClassifier(), {"n_neighbors": ks}, cv=5).fit(X_train, y_train)
                return [int(grid.best_params_["n_neighbors"]), round(float(grid.best_score_), 4), round(float(grid.score(X_test, y_test)), 4)]
           ''', mode="function", name="tune_knn", time_limit=TL),
    ])

# ====================================================================== Day 98 (review)
day98 = L(
    98, "14주차 누적 복습", W, ["confusion_matrix", "precision_recall", "roc_auc", "cross_validation", "hyperparameter"],
    ["지표 선택 → 교차 검증 탐색 → 테스트 확인 → 오류 분석의 평가 흐름을 완성할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 92 | 혼동 행렬 | TP·FP·FN·TN |\n| 93 | 정밀도·재현율 | F1, 임계값 균형 |\n| 94 | ROC·AUC | 확률 점수로 평가 |\n"
        "| 95 | 교차 검증 | `cross_val_score`, `KFold` |\n| 96 | 과적합 | 학습 vs 검증 점수 |\n| 97 | 그리드 탐색 | `GridSearchCV` |"),
        "quiz": [
            quiz("d98_review_q1", "불균형 이진 분류에서 모델을 고를 때 정확도보다 나은 기준은?", ["학습 시간", "F1 또는 AUC", "특성 수", "트리 깊이"], 1, ""),
            quiz("d98_review_q2", "최종 성능 보고에 쓰는 데이터는?", ["교차 검증", "학습", "한 번도 안 쓴 테스트", "전체"], 2, "")]},
    concept={"title": "평가 보고서의 구성", "blocks": [
        text("좋은 평가 보고서는 ① 어떤 지표를 왜 골랐는지 ② 교차 검증으로 고른 설정 ③ 테스트 점수 ④ 혼동 행렬로 본 오류 유형을 담습니다."),
        C('''
            from sklearn.metrics import classification_report

            y_true = [1, 0, 1, 1, 0, 0, 1, 0]
            y_pred = [1, 0, 0, 1, 1, 0, 1, 0]
            print(classification_report(y_true, y_pred, digits=3))
        '''),
        tip("`classification_report`는 클래스별 정밀도·재현율·F1과 표본 수(support)를 한 번에 보여 줍니다. 도전 문제는 KFold를 직접 돌리는 교차 검증입니다."),
    ]},
    fill_intro="클래스별 F1을 구하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "14주차 마무리", "points": [
        "지표는 문제의 비용에 맞게(정밀도·재현율·F1·AUC).",
        "설정은 교차 검증으로, 최종 확인은 테스트로.",
        "혼동 행렬로 오류 유형을 해석한다.",
        "다음 주: 결정 트리와 앙상블."],
        "quiz": [
            quiz("d98_summary_q1", "`classification_report`의 support는?", ["정확도", "클래스별 실제 샘플 수", "F1", "임계값"], 1, ""),
            quiz("d98_summary_q2", "다음 주 배울 \"여러 트리를 합치는\" 모델은?", ["KNN", "랜덤 포레스트", "SVM", "PCA"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d98_fill_1", "fill_blank", "클래스별 F1",
           "다중 분류 실제값·예측값으로 클래스별 F1(소수 넷째 자리) 리스트를 반환하세요.",
           ["precision_recall"], 1,
           '''
            import numpy as np
            from sklearn.metrics import ____


            def per_class_f1(y_true, y_pred):
                scores = f1_score(y_true, y_pred, average=____)
                return np.round(scores, 4)
           ''',
           [t("t1", args=[[0, 1, 2, 2, 1, 0], [0, 2, 2, 2, 1, 0]], ret=np.round(f1_score([0, 1, 2, 2, 1, 0], [0, 2, 2, 2, 1, 0], average=None), 4).tolist(), desc="3클래스", **F),
            t("h1", args=[[0, 1], [0, 1]], ret=[1.0, 1.0], **F)],
           ["F1 점수 함수 이름입니다.", "클래스별 점수를 그대로 받으려면 평균 방식을 \"없음\"으로 줍니다(파이썬 값)."],
           '''
            import numpy as np
            from sklearn.metrics import f1_score


            def per_class_f1(y_true, y_pred):
                scores = f1_score(y_true, y_pred, average=None)
                return np.round(scores, 4)
           ''', mode="function", name="per_class_f1", time_limit=TL),
        ex("d98_code_1", "coding", "모델 선택 보고서",
           "주어진 `cancer_split(seed)`의 학습 데이터로 `SVC`의 `{\"C\": [0.1, 1, 10], \"kernel\": [\"linear\", \"rbf\"]}`를 **F1 기준**(`scoring=\"f1\"`) 5-겹 그리드 탐색하세요. 반환값:\n\n"
           "- `best`: `{\"C\": 실수, \"kernel\": 문자열}`\n- `cv_f1`: 교차 검증 최고 F1, `test_f1`: 테스트 F1 (소수 넷째 자리)\n- `matrix`: 테스트 혼동 행렬(리스트)",
           ["hyperparameter", "precision_recall", "confusion_matrix", "svm"], 3,
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.metrics import confusion_matrix, f1_score
            from sklearn.model_selection import GridSearchCV, train_test_split
            from sklearn.svm import SVC
''' + SPLIT_HELPER + '''

            def selection_report(seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0], ret=ref_selection(0), desc="시드 0", **F), t("h1", args=[2], ret=ref_selection(2), **F)],
           ["`GridSearchCV(SVC(), 후보, cv=5, scoring=\"f1\").fit(X_train, y_train)`.", "테스트 예측은 `grid.predict(X_test)`.",
            "`float(grid.best_params_[\"C\"])`처럼 자료형을 맞추세요."],
           '''
            from sklearn.datasets import load_breast_cancer
            from sklearn.metrics import confusion_matrix, f1_score
            from sklearn.model_selection import GridSearchCV, train_test_split
            from sklearn.svm import SVC
''' + SPLIT_HELPER + '''

            def selection_report(seed):
                X_train, X_test, y_train, y_test = cancer_split(seed)
                params = {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]}
                grid = GridSearchCV(SVC(), params, cv=5, scoring="f1").fit(X_train, y_train)
                pred = grid.predict(X_test)
                best = {"C": float(grid.best_params_["C"]), "kernel": grid.best_params_["kernel"]}
                return {
                    "best": best,
                    "cv_f1": round(float(grid.best_score_), 4),
                    "test_f1": round(float(f1_score(y_test, pred)), 4),
                    "matrix": confusion_matrix(y_test, pred).tolist(),
                }
           ''', mode="function", name="selection_report", time_limit=TL),
        ex("d98_code_2", "coding", "[도전] 교차 검증 직접 구현",
           "iris에 대해 `KFold(n_splits=k, shuffle=True, random_state=0).split(X)`가 주는 인덱스로 직접 반복하며 KNN(기본 설정)을 학습·평가하세요. "
           "`[내 평균 정확도, 같은 KFold를 cv로 준 cross_val_score 평균]`(소수 넷째 자리)를 반환합니다.",
           ["cross_validation", "knn", "numpy_indexing"], 3,
           '''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import KFold, cross_val_score
            from sklearn.neighbors import KNeighborsClassifier


            def manual_cv(k):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[5], ret=ref_manual_cv(5), desc="5겹", **F), t("h1", args=[3], ret=ref_manual_cv(3), **F)],
           ["`for train_idx, test_idx in KFold(...).split(X):` 안에서 `X[train_idx]`로 고르세요.", "점수 목록의 평균과 `cross_val_score(..., cv=KFold(...))`의 평균을 비교합니다."],
           '''
            import numpy as np
            from sklearn.datasets import load_iris
            from sklearn.model_selection import KFold, cross_val_score
            from sklearn.neighbors import KNeighborsClassifier


            def manual_cv(k):
                X, y = load_iris(return_X_y=True)
                kfold = KFold(n_splits=k, shuffle=True, random_state=0)
                scores = []
                for train_idx, test_idx in kfold.split(X):
                    model = KNeighborsClassifier().fit(X[train_idx], y[train_idx])
                    scores.append(model.score(X[test_idx], y[test_idx]))
                sk = cross_val_score(KNeighborsClassifier(), X, y, cv=kfold)
                return [round(float(np.mean(scores)), 4), round(float(sk.mean()), 4)]
           ''', mode="function", name="manual_cv", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day92, day93, day94, day95, day96, day97, day98])
