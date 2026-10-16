"""Week 16 (Day 106-112): 비지도 학습."""
import sys
from pathlib import Path

import numpy as np
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.datasets import load_digits, load_wine, make_blobs, make_moons
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score

sys.path.insert(0, str(Path(__file__).parent))
from cb_common import ex, lesson, quiz, t, text, tip, write_lessons  # noqa: E402
from cb_data import ncode  # noqa: E402

W, ST, TL = 16, "ml", 60
F = {"compare": {"mode": "float", "tol": 1e-6}}


def L(*a, **k):
    return lesson(*a, stage=ST, **k)


def C(src):
    return ncode(src, TL)


def std(X):
    return (X - X.mean(axis=0)) / X.std(axis=0)


# ---------------------------------------------------------------- references
def ref_kmeans(k, seed):
    X, _ = make_blobs(n_samples=300, centers=4, random_state=seed)
    m = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    return [sorted(np.bincount(m.labels_).tolist(), reverse=True), round(float(m.inertia_), 2)]


def ref_best_k(ks, seed):
    X, _ = make_blobs(n_samples=300, centers=4, cluster_std=1.2, random_state=seed)
    scores = [round(float(silhouette_score(X, KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X))), 4) for k in ks]
    return [ks[int(np.argmax(scores))], scores]


def ref_dbscan(eps_list):
    X, _ = make_moons(n_samples=300, noise=0.06, random_state=0)
    out = []
    for eps in eps_list:
        labels = DBSCAN(eps=eps, min_samples=5).fit_predict(X)
        out.append([int(len(set(labels)) - (1 if -1 in labels else 0)), int((labels == -1).sum())])
    return out


def ref_pca_components(threshold):
    X = std(load_wine().data)
    return int(PCA(n_components=threshold).fit(X).n_components_)


def ref_recon(ks):
    X = load_digits().data
    out = []
    for k in ks:
        p = PCA(n_components=k, random_state=0).fit(X)
        rec = p.inverse_transform(p.transform(X))
        out.append(round(float(((X - rec) ** 2).mean()), 3))
    return out


def outlier_data(seed):
    rng = np.random.default_rng(seed)
    normal = rng.normal(0, 1, size=(200, 2))
    outliers = np.array([[6, 6], [-7, 5], [8, -6], [-6, -7]])
    return np.vstack([normal, outliers])


def ref_iforest(contamination, seed):
    X = outlier_data(seed)
    pred = IsolationForest(contamination=contamination, random_state=0).fit_predict(X)
    flagged = np.where(pred == -1)[0]
    return [int(len(flagged)), int(np.isin(np.arange(200, 204), flagged).sum())]


CUSTOMERS = None


def customer_data():
    rng = np.random.default_rng(7)
    a = rng.normal([20, 30, 2], [3, 5, 1], size=(60, 3))
    b = rng.normal([45, 80, 10], [5, 8, 2], size=(40, 3))
    c = rng.normal([35, 50, 25], [4, 6, 3], size=(30, 3))
    return np.vstack([a, b, c])


def ref_segments(k):
    X = customer_data()
    Xs = std(X)
    m = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
    sizes = np.bincount(m.labels_)
    order = np.argsort(sizes)[::-1]
    means = [np.round(X[m.labels_ == c].mean(axis=0), 1).tolist() for c in order]
    return {"sizes": sizes[order].tolist(), "means": means, "silhouette": round(float(silhouette_score(Xs, m.labels_)), 4)}


def ref_kmeans_step(points, centers):
    P, Cn = np.array(points, float), np.array(centers, float)
    labels = ((P[:, None, :] - Cn[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
    new = np.array([P[labels == j].mean(axis=0) if (labels == j).any() else Cn[j] for j in range(len(Cn))])
    return [labels.tolist(), np.round(new, 3).tolist()]


# ====================================================================== Day 106
day106 = L(
    106, "k-평균 군집", W, ["kmeans", "ml_basics"],
    ["정답 없이 비슷한 데이터끼리 묶는 군집(비지도 학습)을 설명할 수 있다.", "KMeans로 군집을 만들고 중심·크기·inertia를 확인할 수 있다."],
    review={"title": "지난주 돌아보기", "content_md": (
        "지금까지는 정답(y)이 있는 **지도 학습**이었습니다. 이번 주는 정답 없이 데이터의 구조를 찾는 **비지도 학습**입니다. 첫 번째는 비슷한 것끼리 묶는 **군집**이에요."),
        "quiz": [quiz("d106_review_q1", "고객을 구매 패턴으로 몇 그룹으로 나누되 미리 정해진 그룹 이름이 없다면?", ["분류", "회귀", "군집", "검증"], 2, "")]},
    concept={"title": "중심을 찾아 묶기", "blocks": [
        text("**k-평균**은 ① 중심 k개를 정하고 ② 각 점을 가장 가까운 중심에 배정한 뒤 ③ 중심을 배정된 점들의 평균으로 옮기는 일을 반복합니다. "
             "`inertia_`는 각 점과 자기 중심 사이 거리 제곱의 합(작을수록 촘촘)입니다."),
        C('''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs

            X, _ = make_blobs(n_samples=300, centers=3, random_state=0)
            model = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
            print(np.bincount(model.labels_))
            print(model.cluster_centers_.round(2))
            print(round(model.inertia_, 2))
        '''),
        tip("군집 번호(0, 1, 2)에는 의미가 없고 실행 설정에 따라 바뀔 수 있습니다. 그래서 채점은 **크기를 정렬한 값**처럼 번호와 무관한 결과로 합니다. k-평균도 거리를 쓰므로 특성 스케일을 맞추는 것이 좋습니다."),
    ]},
    fill_intro="KMeans로 군집을 만드세요.",
    coding_intro="군집 크기와 inertia를 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "비지도 학습: 정답 없이 구조 찾기.",
        "k-평균: 배정 → 중심 이동 반복.",
        "`labels_`, `cluster_centers_`, `inertia_`.",
        "군집 번호 자체는 의미가 없다."],
        "quiz": [
            quiz("d106_summary_q1", "k-평균에서 사람이 정해야 하는 값은?", ["중심 위치", "군집 수 k", "레이블", "inertia"], 1, ""),
            quiz("d106_summary_q2", "inertia가 작다는 것은?", ["군집이 촘촘하다", "군집이 많다", "정확도가 높다", "데이터가 적다"], 0, "")]},
    exercises=[
        ex("d106_fill_1", "fill_blank", "군집 만들기",
           "`make_blobs(n_samples=200, centers=3, random_state=0)` 데이터를 `KMeans(n_clusters=k, n_init=10, random_state=0)`로 묶어 군집 크기를 큰 순으로 반환하세요.",
           ["kmeans"], 1,
           '''
            import numpy as np
            from sklearn.cluster import ____
            from sklearn.datasets import make_blobs


            def cluster_sizes(k):
                X, _ = make_blobs(n_samples=200, centers=3, random_state=0)
                model = KMeans(n_clusters=____, n_init=10, random_state=0).fit(X)
                return sorted(np.bincount(model.labels_).tolist(), reverse=True)
           ''',
           [t("t1", args=[3], ret=sorted(np.bincount(KMeans(n_clusters=3, n_init=10, random_state=0).fit(make_blobs(n_samples=200, centers=3, random_state=0)[0]).labels_).tolist(), reverse=True), desc="k=3"),
            t("h1", args=[2], ret=sorted(np.bincount(KMeans(n_clusters=2, n_init=10, random_state=0).fit(make_blobs(n_samples=200, centers=3, random_state=0)[0]).labels_).tolist(), reverse=True))],
           ["k-평균 군집 클래스 이름입니다.", "군집 수로 쓸 매개변수입니다."],
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs


            def cluster_sizes(k):
                X, _ = make_blobs(n_samples=200, centers=3, random_state=0)
                model = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
                return sorted(np.bincount(model.labels_).tolist(), reverse=True)
           ''', mode="function", name="cluster_sizes", time_limit=TL),
        ex("d106_code_1", "coding", "군집 요약",
           "`make_blobs(n_samples=300, centers=4, random_state=seed)`의 X를 `KMeans(n_clusters=k, n_init=10, random_state=0)`로 묶어 `[큰 순 군집 크기 리스트, inertia(소수 둘째 자리)]`를 반환하세요.",
           ["kmeans"], 2,
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs


            def summarize_clusters(k, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[4, 0], ret=ref_kmeans(4, 0), desc="k=4", **F), t("h1", args=[2, 5], ret=ref_kmeans(2, 5), **F)],
           ["`make_blobs(...)`는 (X, y)를 돌려주지만 군집에는 X만 씁니다.", "크기는 `np.bincount(model.labels_)`를 큰 순으로 정렬합니다."],
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs


            def summarize_clusters(k, seed):
                X, _ = make_blobs(n_samples=300, centers=4, random_state=seed)
                model = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
                sizes = sorted(np.bincount(model.labels_).tolist(), reverse=True)
                return [sizes, round(float(model.inertia_), 2)]
           ''', mode="function", name="summarize_clusters", time_limit=TL),
    ])

# ====================================================================== Day 107
day107 = L(
    107, "군집 수 정하기", W, ["cluster_eval", "kmeans"],
    ["엘보 방법(inertia 곡선)으로 적당한 k를 살펴볼 수 있다.", "실루엣 점수로 군집의 품질을 비교해 k를 고를 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 k-평균으로 군집을 만들었습니다. 그런데 k는 어떻게 정할까요?",
            "quiz": [quiz("d107_review_q1", "k를 늘리면 inertia는 보통?", ["커진다", "작아진다", "변함없다", "0이 된다"], 1, "그래서 inertia만으로는 k를 정할 수 없습니다.")]},
    concept={"title": "몇 개로 묶을까", "blocks": [
        text("- **엘보 방법**: k를 늘리며 inertia를 그리면 어느 지점부터 감소가 완만해집니다(팔꿈치). 그 근처가 적당한 k입니다.\n"
             "- **실루엣 점수**(−1~1): 각 점이 자기 군집과는 가깝고 다른 군집과는 먼 정도의 평균. 클수록 좋습니다."),
        C('''
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs
            from sklearn.metrics import silhouette_score

            X, _ = make_blobs(n_samples=300, centers=4, cluster_std=1.2, random_state=1)
            for k in [2, 3, 4, 5, 6]:
                model = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
                print(k, round(model.inertia_, 1), round(silhouette_score(X, model.labels_), 3))
        '''),
        tip("실제 데이터는 경계가 애매해 \"정답 k\"가 없는 경우가 많습니다. 지표와 함께 **군집을 해석할 수 있는지**(예: 고객 그룹에 이름을 붙일 수 있는지)도 기준이 됩니다."),
    ]},
    fill_intro="실루엣 점수를 계산하세요.",
    coding_intro="실루엣 점수로 가장 좋은 k를 고르세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "inertia는 k가 클수록 무조건 작아진다.",
        "엘보: 감소가 꺾이는 지점.",
        "`silhouette_score(X, labels)`: −1~1, 클수록 좋음.",
        "지표 + 해석 가능성으로 k를 정한다."],
        "quiz": [
            quiz("d107_summary_q1", "실루엣 점수가 0에 가까우면?", ["군집이 명확", "군집 경계가 애매", "완벽", "오류"], 1, ""),
            quiz("d107_summary_q2", "실루엣 점수 계산에 필요한 것은?", ["정답 레이블", "데이터와 군집 레이블", "inertia", "중심 개수만"], 1, "")]},
    exercises=[
        ex("d107_fill_1", "fill_blank", "실루엣 점수",
           "`make_blobs(n_samples=200, centers=3, random_state=0)`를 k개로 묶은 결과의 실루엣 점수(소수 넷째 자리)를 반환하세요.",
           ["cluster_eval"], 1,
           '''
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs
            from sklearn.metrics import ____


            def silhouette_of(k):
                X, _ = make_blobs(n_samples=200, centers=3, random_state=0)
                labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
                return round(float(silhouette_score(X, ____)), 4)
           ''',
           [t("t1", args=[3], ret=round(float(silhouette_score(make_blobs(n_samples=200, centers=3, random_state=0)[0], KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(make_blobs(n_samples=200, centers=3, random_state=0)[0]))), 4), desc="k=3", **F),
            t("h1", args=[5], ret=round(float(silhouette_score(make_blobs(n_samples=200, centers=3, random_state=0)[0], KMeans(n_clusters=5, n_init=10, random_state=0).fit_predict(make_blobs(n_samples=200, centers=3, random_state=0)[0]))), 4), **F)],
           ["실루엣 점수 함수 이름입니다.", "두 번째 인자는 군집 레이블입니다."],
           '''
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs
            from sklearn.metrics import silhouette_score


            def silhouette_of(k):
                X, _ = make_blobs(n_samples=200, centers=3, random_state=0)
                labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
                return round(float(silhouette_score(X, labels)), 4)
           ''', mode="function", name="silhouette_of", time_limit=TL),
        ex("d107_code_1", "coding", "최적의 k",
           "`make_blobs(n_samples=300, centers=4, cluster_std=1.2, random_state=seed)`의 X에 대해 후보 `ks`마다 실루엣 점수(소수 넷째 자리)를 구해 `[가장 좋은 k, 점수 리스트]`를 반환하세요(동점이면 앞 후보).",
           ["cluster_eval", "kmeans"], 2,
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs
            from sklearn.metrics import silhouette_score


            def choose_k(ks, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[2, 3, 4, 5, 6], 1], ret=ref_best_k([2, 3, 4, 5, 6], 1), desc="2~6", **F), t("h1", args=[[3, 8], 4], ret=ref_best_k([3, 8], 4), **F)],
           ["k마다 `fit_predict`로 레이블을 얻고 실루엣 점수를 계산하세요.", "가장 좋은 위치는 `np.argmax(scores)`."],
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs
            from sklearn.metrics import silhouette_score


            def choose_k(ks, seed):
                X, _ = make_blobs(n_samples=300, centers=4, cluster_std=1.2, random_state=seed)
                scores = []
                for k in ks:
                    labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
                    scores.append(round(float(silhouette_score(X, labels)), 4))
                return [ks[int(np.argmax(scores))], scores]
           ''', mode="function", name="choose_k", time_limit=TL),
    ])

# ====================================================================== Day 108
day108 = L(
    108, "계층 군집과 DBSCAN", W, ["hierarchical", "kmeans"],
    ["가까운 것부터 합쳐 가는 계층 군집을 설명할 수 있다.", "밀도 기반 DBSCAN으로 모양이 자유로운 군집과 잡음(노이즈)을 찾을 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 실루엣 점수로 k를 골랐습니다. k-평균은 둥근 덩어리 모양에 잘 맞습니다.",
            "quiz": [quiz("d108_review_q1", "k-평균이 잘 못하는 군집 모양은?", ["둥근 덩어리", "초승달처럼 휘어진 모양", "크기가 비슷한 공", "멀리 떨어진 덩어리"], 1, "")]},
    concept={"title": "다른 방식의 군집", "blocks": [
        text("- **계층 군집**(`AgglomerativeClustering`): 모든 점을 따로 시작해 가장 가까운 것끼리 차례로 합칩니다. 합친 과정이 나무 그림(덴드로그램)으로 남습니다.\n"
             "- **DBSCAN**: 반경 `eps` 안에 이웃이 `min_samples`개 이상인 밀집 지역을 군집으로 이어 붙이고, 어디에도 속하지 않는 점은 **잡음(레이블 −1)**으로 둡니다. k를 미리 정하지 않아도 됩니다."),
        C('''
            import numpy as np
            from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
            from sklearn.datasets import make_moons

            X, y = make_moons(n_samples=300, noise=0.06, random_state=0)
            for model in [KMeans(n_clusters=2, n_init=10, random_state=0), AgglomerativeClustering(n_clusters=2, linkage="single"), DBSCAN(eps=0.2, min_samples=5)]:
                labels = model.fit_predict(X)
                agree = max((labels == y).mean(), (labels == 1 - y).mean())
                print(type(model).__name__, sorted(set(labels.tolist())), round(agree, 3))
        '''),
        tip("DBSCAN의 `eps`가 너무 작으면 대부분이 잡음이 되고, 너무 크면 모두 한 군집이 됩니다. 이 역시 특성 스케일에 민감합니다."),
    ]},
    fill_intro="DBSCAN의 잡음 개수를 세세요.",
    coding_intro="eps에 따른 군집 수와 잡음 수를 조사하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "계층 군집: 가까운 것부터 합치기, `linkage` 방식 선택.",
        "DBSCAN: 밀도로 군집, 잡음은 −1, k 불필요.",
        "휘어진 모양에는 DBSCAN·single linkage가 유리.",
        "`eps`, `min_samples`가 핵심 설정."],
        "quiz": [
            quiz("d108_summary_q1", "DBSCAN에서 레이블 −1의 의미는?", ["첫 군집", "잡음(어느 군집에도 속하지 않음)", "오류", "가장 큰 군집"], 1, ""),
            quiz("d108_summary_q2", "군집 수를 미리 정하지 않아도 되는 방법은?", ["KMeans", "DBSCAN", "AgglomerativeClustering(n_clusters=3)", "PCA"], 1, "")]},
    exercises=[
        ex("d108_fill_1", "fill_blank", "잡음 세기",
           "군집 레이블 목록에서 잡음(−1)의 개수를 반환하세요.",
           ["hierarchical"], 1,
           '''
            import numpy as np


            def noise_count(labels):
                return int((np.array(labels) == ____).____())
           ''',
           [t("t1", args=[[0, 0, -1, 1, -1]], ret=2, desc="기본"), t("h1", args=[[0, 1]], ret=0)],
           ["DBSCAN이 잡음에 붙이는 레이블 값입니다.", "True의 개수를 세는 메서드입니다."],
           '''
            import numpy as np


            def noise_count(labels):
                return int((np.array(labels) == -1).sum())
           ''', mode="function", name="noise_count", time_limit=TL),
        ex("d108_code_1", "coding", "eps 실험",
           "`make_moons(n_samples=300, noise=0.06, random_state=0)`의 X에 `DBSCAN(eps=eps, min_samples=5)`를 적용해, `eps_list`의 각 값마다 `[군집 수(잡음 제외), 잡음 수]`를 반환하세요.",
           ["hierarchical"], 2,
           '''
            from sklearn.cluster import DBSCAN
            from sklearn.datasets import make_moons


            def eps_report(eps_list):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[0.05, 0.2, 1.0]], ret=ref_dbscan([0.05, 0.2, 1.0]), desc="세 eps"), t("h1", args=[[0.1]], ret=ref_dbscan([0.1]))],
           ["eps마다 `fit_predict(X)`로 레이블을 구하세요.", "군집 수는 `len(set(labels))`에서 −1이 있으면 1을 뺍니다."],
           '''
            from sklearn.cluster import DBSCAN
            from sklearn.datasets import make_moons


            def eps_report(eps_list):
                X, _ = make_moons(n_samples=300, noise=0.06, random_state=0)
                report = []
                for eps in eps_list:
                    labels = DBSCAN(eps=eps, min_samples=5).fit_predict(X)
                    clusters = len(set(labels)) - (1 if -1 in labels else 0)
                    report.append([int(clusters), int((labels == -1).sum())])
                return report
           ''', mode="function", name="eps_report", time_limit=TL),
    ])

# ====================================================================== Day 109
day109 = L(
    109, "주성분 분석(PCA)", W, ["pca", "numpy_aggregate"],
    ["PCA가 데이터의 분산이 큰 방향으로 새 축을 만들어 차원을 줄이는 방법임을 설명할 수 있다.", "설명된 분산 비율로 필요한 주성분 수를 정할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 DBSCAN과 계층 군집을 배웠습니다. 오늘은 또 다른 비지도 학습, **차원 축소**입니다.",
            "quiz": [quiz("d109_review_q1", "비지도 학습의 공통점은?", ["정답 레이블을 쓰지 않는다", "항상 분류다", "테스트 데이터가 없다", "트리를 쓴다"], 0, "")]},
    concept={"title": "중요한 방향만 남기기", "blocks": [
        text("특성이 많으면 계산이 느리고 시각화가 어렵습니다. **PCA**는 데이터가 가장 넓게 퍼진 방향을 첫 번째 축(주성분)으로, 그와 수직이면서 다음으로 넓은 방향을 두 번째 축으로… 새 축을 만듭니다. "
             "앞의 몇 개 축만 남기면 정보를 많이 유지한 채 차원을 줄일 수 있습니다. `explained_variance_ratio_`는 각 축이 설명하는 분산의 비율입니다."),
        C('''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.decomposition import PCA

            X = load_wine().data
            Xs = (X - X.mean(axis=0)) / X.std(axis=0)
            pca = PCA().fit(Xs)
            print(pca.explained_variance_ratio_[:4].round(3))
            print(np.cumsum(pca.explained_variance_ratio_)[:4].round(3))
            print(PCA(n_components=0.9).fit(Xs).n_components_)
        '''),
        tip("PCA 전에는 특성을 **표준화**해야 단위가 큰 특성이 분산을 독차지하지 않습니다. `n_components=0.9`처럼 비율을 주면 그만큼의 분산을 설명하는 최소 개수를 골라 줍니다."),
    ]},
    fill_intro="PCA로 데이터의 차원을 줄이세요.",
    coding_intro="원하는 분산 비율을 위해 필요한 주성분 수를 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "PCA: 분산이 큰 방향으로 새 축, 앞쪽 축만 남겨 차원 축소.",
        "`explained_variance_ratio_`, 누적합은 `np.cumsum`.",
        "`PCA(n_components=0.9)`: 90% 분산을 설명하는 최소 개수.",
        "PCA 전에 표준화."],
        "quiz": [
            quiz("d109_summary_q1", "첫 번째 주성분의 특징은?", ["분산이 가장 작은 방향", "분산이 가장 큰 방향", "첫 번째 특성 그대로", "정답과 가장 관련"], 1, ""),
            quiz("d109_summary_q2", "PCA 전에 표준화하는 이유는?", ["속도", "단위가 큰 특성이 결과를 지배하지 않게", "레이블 필요", "음수 제거"], 1, "")]},
    exercises=[
        ex("d109_fill_1", "fill_blank", "차원 줄이기",
           "와인 데이터를 표준화한 뒤 `PCA(n_components=k)`로 변환한 결과의 모양을 반환하세요.",
           ["pca"], 1,
           '''
            from sklearn.datasets import load_wine
            from sklearn.decomposition import ____


            def reduced_shape(k):
                X = load_wine().data
                Xs = (X - X.mean(axis=0)) / X.std(axis=0)
                return list(PCA(n_components=k).____(Xs).shape)
           ''',
           [t("t1", args=[2], ret=[178, 2], desc="2차원"), t("h1", args=[5], ret=[178, 5])],
           ["주성분 분석 클래스 이름입니다.", "학습과 변환을 한 번에 하는 메서드입니다."],
           '''
            from sklearn.datasets import load_wine
            from sklearn.decomposition import PCA


            def reduced_shape(k):
                X = load_wine().data
                Xs = (X - X.mean(axis=0)) / X.std(axis=0)
                return list(PCA(n_components=k).fit_transform(Xs).shape)
           ''', mode="function", name="reduced_shape", time_limit=TL),
        ex("d109_code_1", "coding", "필요한 주성분 수",
           "와인 데이터를 표준화한 뒤, 누적 설명 분산 비율이 `threshold` 이상이 되는 **최소 주성분 수**를 반환하세요. `PCA()`로 전체를 학습한 뒤 `np.cumsum`으로 직접 찾으세요.",
           ["pca", "numpy_aggregate"], 2,
           '''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.decomposition import PCA


            def components_needed(threshold):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0.9], ret=ref_pca_components(0.9), desc="90%"), t("h1", args=[0.5], ret=ref_pca_components(0.5)), t("h2", args=[0.99], ret=ref_pca_components(0.99))],
           ["누적 비율 배열에서 `threshold` 이상이 처음 나오는 위치를 찾으세요.", "`np.argmax(cumulative >= threshold)`는 첫 True의 위치입니다. 개수는 위치 + 1."],
           '''
            import numpy as np
            from sklearn.datasets import load_wine
            from sklearn.decomposition import PCA


            def components_needed(threshold):
                X = load_wine().data
                Xs = (X - X.mean(axis=0)) / X.std(axis=0)
                cumulative = np.cumsum(PCA().fit(Xs).explained_variance_ratio_)
                return int(np.argmax(cumulative >= threshold)) + 1
           ''', mode="function", name="components_needed", time_limit=TL),
    ])

# ====================================================================== Day 110
day110 = L(
    110, "PCA 활용: 시각화와 압축", W, ["pca", "matplotlib"],
    ["고차원 데이터를 2차원으로 줄여 시각화할 수 있다.", "주성분 수에 따른 복원 오차로 압축 정도를 판단할 수 있다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 PCA로 차원을 줄이고 설명된 분산을 확인했습니다.",
            "quiz": [quiz("d110_review_q1", "누적 설명 분산 비율을 구하는 함수는?", ["`np.sum`", "`np.cumsum`", "`np.mean`", "`np.argmax`"], 1, "")]},
    concept={"title": "64차원을 2차원으로", "blocks": [
        text("digits(64차원)를 PCA로 2차원으로 줄이면 숫자별로 어느 정도 모이는 모습을 그림으로 볼 수 있습니다. 또 `inverse_transform`으로 원래 공간에 되돌리면, 몇 개 축만으로 이미지를 얼마나 복원하는지(압축) 알 수 있습니다."),
        C('''
            import matplotlib.pyplot as plt
            from sklearn.datasets import load_digits
            from sklearn.decomposition import PCA

            digits = load_digits()
            points = PCA(n_components=2, random_state=0).fit_transform(digits.data)
            fig, ax = plt.subplots(figsize=(6, 5))
            scatter = ax.scatter(points[:, 0], points[:, 1], c=digits.target, cmap="tab10", s=8)
            fig.colorbar(scatter, ax=ax)
            ax.set_title("digits를 2차원으로")
            print(points.shape)
        '''),
        C('''
            from sklearn.datasets import load_digits
            from sklearn.decomposition import PCA

            X = load_digits().data
            for k in [2, 10, 30]:
                pca = PCA(n_components=k, random_state=0).fit(X)
                restored = pca.inverse_transform(pca.transform(X))
                print(k, round(((X - restored) ** 2).mean(), 3))
        '''),
        tip("2차원 시각화에서 겹쳐 보인다고 분류가 불가능한 것은 아닙니다. 나머지 62차원에 구분 정보가 남아 있을 수 있어요. 더 좋은 시각화 기법으로 t-SNE, UMAP이 있습니다."),
    ]},
    fill_intro="PCA로 줄였다가 되돌리세요.",
    coding_intro="주성분 수별 복원 오차를 구하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "PCA 2차원 → 산점도로 고차원 데이터 보기.",
        "`inverse_transform`으로 원래 공간 복원.",
        "주성분↑ → 복원 오차↓ (압축률과의 균형).",
        "PCA는 전처리(속도·잡음 제거)로도 쓴다."],
        "quiz": [
            quiz("d110_summary_q1", "주성분 수를 늘리면 복원 오차는?", ["커진다", "작아진다", "변함없다", "0으로 고정"], 1, ""),
            quiz("d110_summary_q2", "PCA 결과를 원래 차원으로 되돌리는 메서드는?", ["`transform`", "`inverse_transform`", "`fit`", "`predict`"], 1, "")]},
    exercises=[
        ex("d110_fill_1", "fill_blank", "줄였다 되돌리기",
           "digits 데이터를 `PCA(n_components=k, random_state=0)`로 줄였다가 되돌린 결과의 모양을 반환하세요.",
           ["pca"], 1,
           '''
            from sklearn.datasets import load_digits
            from sklearn.decomposition import PCA


            def restored_shape(k):
                X = load_digits().data
                pca = PCA(n_components=k, random_state=0).fit(X)
                restored = pca.____(pca.____(X))
                return list(restored.shape)
           ''',
           [t("t1", args=[5], ret=[1797, 64], desc="k=5"), t("h1", args=[1], ret=[1797, 64])],
           ["되돌리는 메서드입니다(inverse_…).", "먼저 줄이는 메서드입니다."],
           '''
            from sklearn.datasets import load_digits
            from sklearn.decomposition import PCA


            def restored_shape(k):
                X = load_digits().data
                pca = PCA(n_components=k, random_state=0).fit(X)
                restored = pca.inverse_transform(pca.transform(X))
                return list(restored.shape)
           ''', mode="function", name="restored_shape", time_limit=TL),
        ex("d110_code_1", "coding", "압축과 복원 오차",
           "digits 데이터에 대해 `ks`의 각 주성분 수로 `PCA(n_components=k, random_state=0)`를 학습해 줄였다 되돌리고, 원본과의 평균 제곱 오차(소수 셋째 자리) 리스트를 반환하세요.",
           ["pca", "regression_metrics"], 2,
           '''
            from sklearn.datasets import load_digits
            from sklearn.decomposition import PCA


            def reconstruction_errors(ks):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[[2, 10, 30]], ret=ref_recon([2, 10, 30]), desc="2·10·30", **F), t("h1", args=[[1, 64]], ret=ref_recon([1, 64]), **F)],
           ["k마다 PCA를 새로 학습하세요.", "오차는 `((X - restored) ** 2).mean()`."],
           '''
            from sklearn.datasets import load_digits
            from sklearn.decomposition import PCA


            def reconstruction_errors(ks):
                X = load_digits().data
                errors = []
                for k in ks:
                    pca = PCA(n_components=k, random_state=0).fit(X)
                    restored = pca.inverse_transform(pca.transform(X))
                    errors.append(round(float(((X - restored) ** 2).mean()), 3))
                return errors
           ''', mode="function", name="reconstruction_errors", time_limit=TL),
    ])

# ====================================================================== Day 111
OUT_HELPER = '''
            def outlier_data(seed):
                rng = np.random.default_rng(seed)
                normal = rng.normal(0, 1, size=(200, 2))
                outliers = np.array([[6, 6], [-7, 5], [8, -6], [-6, -7]])
                return np.vstack([normal, outliers])
'''
day111 = L(
    111, "이상치 탐지", W, ["anomaly", "eda"],
    ["정상 데이터와 다른 드문 데이터(이상치)를 찾는 비지도 방법을 쓸 수 있다.", "IsolationForest의 contamination 설정을 이해한다."],
    review={"title": "어제 배운 내용 떠올리기", "content_md": "어제는 PCA로 시각화와 압축을 했습니다. Day 68의 IQR 규칙도 이상치 탐지의 한 방법이었죠.",
            "quiz": [quiz("d111_review_q1", "IQR 규칙은 몇 개의 특성을 한 번에 보나?", ["한 개", "두 개", "모든 특성", "레이블"], 0, "여러 특성을 함께 보려면 다른 방법이 필요합니다.")]},
    concept={"title": "고립시키기 쉬운 점 찾기", "blocks": [
        text("**IsolationForest**는 무작위로 특성과 기준값을 골라 데이터를 계속 나눌 때, **적은 횟수 만에 혼자 떨어지는 점**을 이상치로 봅니다(드물고 멀리 있어서). "
             "`contamination`은 이상치 비율의 추정치이고, `predict`/`fit_predict`는 정상 1, 이상치 −1을 돌려줍니다."),
        C('''
            import numpy as np
            from sklearn.ensemble import IsolationForest

            rng = np.random.default_rng(0)
            X = np.vstack([rng.normal(0, 1, size=(200, 2)), [[6, 6], [-7, 5], [8, -6], [-6, -7]]])
            pred = IsolationForest(contamination=0.02, random_state=0).fit_predict(X)
            flagged = np.where(pred == -1)[0]
            print(len(flagged), flagged)
        '''),
        tip("이상치 탐지는 카드 부정 사용, 공장 센서 고장처럼 **정답 레이블을 모으기 어려운** 문제에 씁니다. 찾은 이상치가 진짜 문제인지는 사람이 확인해야 합니다."),
    ]},
    fill_intro="이상치로 판정된 위치를 찾으세요.",
    coding_intro="IsolationForest로 심어 둔 이상치를 몇 개 찾는지 확인하세요.",
    summary={"title": "오늘의 핵심 정리", "points": [
        "이상치 탐지: 드물고 다른 데이터를 레이블 없이 찾기.",
        "IsolationForest: 빨리 고립되는 점 = 이상치.",
        "`contamination`: 이상치 비율 추정, 결과 1 / −1.",
        "탐지 결과는 사람이 검토한다."],
        "quiz": [
            quiz("d111_summary_q1", "IsolationForest에서 −1은?", ["정상", "이상치", "군집 0", "오류"], 1, ""),
            quiz("d111_summary_q2", "contamination을 0.1로 주면?", ["약 10%를 이상치로 표시", "10개만 표시", "정확도 10%", "트리 10개"], 0, "")]},
    exercises=[
        ex("d111_fill_1", "fill_blank", "이상치 위치",
           "예측 결과(1 또는 −1) 목록에서 −1인 위치(인덱스) 리스트를 반환하세요.",
           ["anomaly"], 1,
           '''
            import numpy as np


            def anomaly_indices(pred):
                return np.____(np.array(pred) == ____)[0]
           ''',
           [t("t1", args=[[1, -1, 1, -1]], ret=[1, 3], desc="기본"), t("h1", args=[[1, 1]], ret=[])],
           ["조건이 참인 위치를 돌려주는 NumPy 함수입니다(wh…).", "이상치를 뜻하는 값입니다."],
           '''
            import numpy as np


            def anomaly_indices(pred):
                return np.where(np.array(pred) == -1)[0]
           ''', mode="function", name="anomaly_indices", time_limit=TL),
        ex("d111_code_1", "coding", "숨은 이상치 찾기",
           "주어진 `outlier_data(seed)`는 정상 점 200개(0~199번)와 심어 둔 이상치 4개(200~203번)를 돌려줍니다. `IsolationForest(contamination=contamination, random_state=0)`로 "
           "`[이상치로 표시된 개수, 그중 심어 둔 이상치의 개수]`를 반환하세요.",
           ["anomaly", "numpy_indexing"], 2,
           '''
            import numpy as np
            from sklearn.ensemble import IsolationForest
''' + OUT_HELPER + '''

            def detect(contamination, seed):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[0.02, 0], ret=ref_iforest(0.02, 0), desc="2%"), t("h1", args=[0.05, 3], ret=ref_iforest(0.05, 3))],
           ["`fit_predict(X)`로 예측하고 −1인 위치를 구하세요.", "그 위치 중 200 이상인 것의 개수가 찾은 심은 이상치 수입니다."],
           '''
            import numpy as np
            from sklearn.ensemble import IsolationForest
''' + OUT_HELPER + '''

            def detect(contamination, seed):
                X = outlier_data(seed)
                pred = IsolationForest(contamination=contamination, random_state=0).fit_predict(X)
                flagged = np.where(pred == -1)[0]
                return [int(len(flagged)), int((flagged >= 200).sum())]
           ''', mode="function", name="detect", time_limit=TL),
    ])

# ====================================================================== Day 112 (review)
CUST_HELPER = '''
            def customer_data():
                rng = np.random.default_rng(7)
                a = rng.normal([20, 30, 2], [3, 5, 1], size=(60, 3))
                b = rng.normal([45, 80, 10], [5, 8, 2], size=(40, 3))
                c = rng.normal([35, 50, 25], [4, 6, 3], size=(30, 3))
                return np.vstack([a, b, c])
'''
step_cases = [(([[0, 0], [0, 1], [5, 5], [6, 5]], [[0, 0], [5, 5]]), "t1", "두 군집"), (([[1, 1], [2, 2], [9, 9]], [[0, 0], [10, 10]]), "h1", "")]
day112 = L(
    112, "16주차 누적 복습", W, ["kmeans", "cluster_eval", "pca", "anomaly", "hierarchical"],
    ["표준화 → 군집 → 평가 → 해석의 비지도 분석 흐름을 완성할 수 있다."],
    review={"title": "한 주 돌아보기", "content_md": (
        "| Day | 주제 | 핵심 |\n|---|---|---|\n"
        "| 106 | k-평균 | 배정·이동 반복, inertia |\n| 107 | k 고르기 | 엘보, 실루엣 |\n| 108 | 계층·DBSCAN | 합치기, 밀도, 잡음 −1 |\n"
        "| 109 | PCA | 분산 큰 방향, 설명 분산 |\n| 110 | PCA 활용 | 2D 시각화, 복원 오차 |\n| 111 | 이상치 | IsolationForest |"),
        "quiz": [
            quiz("d112_review_q1", "고객 세분화 전에 특성 스케일을 맞춰야 하는 이유는?", ["k-평균이 거리를 쓰기 때문", "레이블이 필요해서", "속도", "PCA 금지"], 0, ""),
            quiz("d112_review_q2", "군집 결과를 해석하는 좋은 방법은?", ["군집 번호 외우기", "군집별 특성 평균 비교", "정확도 계산", "inertia만 보기"], 1, "")]},
    concept={"title": "군집에 이름 붙이기", "blocks": [
        text("군집을 만든 뒤에는 군집별 **원래 단위의 특성 평균**을 보고 \"젊고 적게 쓰는 고객\", \"자주 오는 고액 고객\"처럼 이름을 붙입니다. 계산은 표준화 데이터로, 해석은 원래 데이터로 합니다."),
        tip("도전 문제에서는 k-평균의 한 단계(배정 → 중심 이동)를 NumPy로 직접 구현합니다. `P[:, None, :] - C[None, :, :]`처럼 축을 추가하면 모든 점과 모든 중심의 차이를 한 번에 계산할 수 있어요(브로드캐스팅)."),
    ]},
    fill_intro="표준화 공식을 완성하세요.",
    coding_intro="첫 번째 문제는 필수, 두 번째 문제는 **도전 문제**(선택)입니다.",
    summary={"title": "16주차 마무리", "points": [
        "비지도 흐름: 표준화 → 군집/차원 축소 → 평가 → 해석.",
        "번호는 의미 없음, 크기·평균으로 설명.",
        "PCA로 보고, 이상치는 따로 검토.",
        "다음 주: 전처리와 파이프라인으로 3단계 마무리."],
        "quiz": [
            quiz("d112_summary_q1", "k-평균 한 단계의 순서는?", ["중심 이동 → 배정", "배정 → 중심 이동", "PCA → 배정", "정렬 → 배정"], 1, ""),
            quiz("d112_summary_q2", "군집 해석에 쓰는 데이터는?", ["표준화된 데이터", "원래 단위 데이터", "레이블", "PCA 축만"], 1, "")]},
    is_review=True,
    exercises=[
        ex("d112_fill_1", "fill_blank", "표준화",
           "2차원 배열(리스트)을 열마다 표준화해 소수 넷째 자리로 반환하세요.",
           ["scaling", "numpy_aggregate"], 1,
           '''
            import numpy as np


            def standardize(X):
                X = np.array(X, dtype=float)
                return np.round((X - X.mean(axis=____)) / X.____(axis=0), 4)
           ''',
           [t("t1", args=[[[1, 10], [3, 30]]], ret=[[-1.0, -1.0], [1.0, 1.0]], desc="두 행", **F), t("h1", args=[[[0, 5], [2, 5], [4, 8]]], ret=np.round((np.array([[0, 5], [2, 5], [4, 8]]) - np.array([[0, 5], [2, 5], [4, 8]]).mean(axis=0)) / np.array([[0, 5], [2, 5], [4, 8]]).std(axis=0), 4).tolist(), **F)],
           ["열마다(세로 방향) 평균을 구하는 축 번호입니다.", "표준편차 메서드입니다."],
           '''
            import numpy as np


            def standardize(X):
                X = np.array(X, dtype=float)
                return np.round((X - X.mean(axis=0)) / X.std(axis=0), 4)
           ''', mode="function", name="standardize", time_limit=TL),
        ex("d112_code_1", "coding", "고객 세분화",
           "주어진 `customer_data()`(나이, 월 방문 수, 월 구매액)를 표준화해 `KMeans(n_clusters=k, n_init=10, random_state=0)`로 묶으세요. 반환값:\n\n"
           "- `sizes`: 군집 크기(큰 순)\n- `means`: 같은 순서로, 각 군집의 **원래 단위** 특성 평균(소수 첫째 자리)\n- `silhouette`: 표준화 데이터 기준 실루엣(소수 넷째 자리)",
           ["kmeans", "cluster_eval", "scaling"], 3,
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
''' + CUST_HELPER + '''

            def segment(k):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t("t1", args=[3], ret=ref_segments(3), desc="k=3", **F), t("h1", args=[2], ret=ref_segments(2), **F)],
           ["표준화 데이터로 군집, 원래 데이터로 평균을 계산합니다.", "크기 `np.bincount(labels)`를 큰 순으로 정렬한 위치(`np.argsort(...)[::-1]`)를 구하세요.",
            "그 순서대로 `X[labels == c].mean(axis=0)`."],
           '''
            import numpy as np
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
''' + CUST_HELPER + '''

            def segment(k):
                X = customer_data()
                Xs = (X - X.mean(axis=0)) / X.std(axis=0)
                labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(Xs)
                sizes = np.bincount(labels)
                order = np.argsort(sizes)[::-1]
                means = [np.round(X[labels == c].mean(axis=0), 1).tolist() for c in order]
                return {"sizes": sizes[order].tolist(), "means": means, "silhouette": round(float(silhouette_score(Xs, labels)), 4)}
           ''', mode="function", name="segment", time_limit=TL),
        ex("d112_code_2", "coding", "[도전] k-평균 한 단계",
           "점 목록과 중심 목록을 받아 k-평균 한 단계를 수행하세요. ① 각 점을 거리 제곱이 가장 작은 중심에 배정 ② 중심을 배정된 점들의 평균으로 이동(배정된 점이 없으면 그대로). "
           "`[배정 리스트, 새 중심(소수 셋째 자리)]`를 반환합니다.",
           ["kmeans", "numpy_ops", "numpy_aggregate"], 3,
           '''
            import numpy as np


            def kmeans_step(points, centers):
                # 여기에 코드를 작성하세요
                pass
           ''',
           [t(tid, args=list(a), ret=ref_kmeans_step(*a), desc=d, **F) for a, tid, d in step_cases],
           ["`((P[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)`는 (점 수, 중심 수) 거리 행렬입니다.", "`argmin(axis=1)`로 배정, 중심 j는 `P[labels == j].mean(axis=0)`."],
           '''
            import numpy as np


            def kmeans_step(points, centers):
                P = np.array(points, dtype=float)
                C = np.array(centers, dtype=float)
                distances = ((P[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
                labels = distances.argmin(axis=1)
                new_centers = []
                for j in range(len(C)):
                    members = P[labels == j]
                    new_centers.append(members.mean(axis=0) if len(members) else C[j])
                return [labels.tolist(), np.round(np.array(new_centers), 3).tolist()]
           ''', mode="function", name="kmeans_step", required=False, time_limit=TL),
    ])

if __name__ == "__main__":
    write_lessons(Path(sys.argv[1]), [day106, day107, day108, day109, day110, day111, day112])
