"""Curriculum additions for stage 3 (Day 71-119, machine learning)."""

NEW_CONCEPTS = {
    # week 11
    "ml_basics": "머신러닝 개념", "dataset": "데이터셋과 특성", "train_test": "학습·테스트 분리", "knn": "k-최근접 이웃",
    "sklearn_api": "scikit-learn 사용법",
    # week 12
    "linear_regression": "선형 회귀", "regression_metrics": "회귀 평가 지표", "polynomial": "다항 회귀",
    "regularization": "규제(Ridge·Lasso)", "gradient_descent": "경사하강법",
    # week 13
    "logistic_regression": "로지스틱 회귀", "decision_boundary": "확률과 결정 경계", "svm": "서포트 벡터 머신",
    "naive_bayes": "나이브 베이즈와 텍스트", "multiclass": "다중 분류",
    # week 14
    "confusion_matrix": "혼동 행렬", "precision_recall": "정밀도·재현율·F1", "roc_auc": "ROC·AUC",
    "cross_validation": "교차 검증", "overfitting": "과적합과 과소적합", "hyperparameter": "하이퍼파라미터 탐색",
    # week 15
    "decision_tree": "결정 트리", "impurity": "불순도(지니·엔트로피)", "random_forest": "랜덤 포레스트",
    "boosting": "부스팅", "feature_importance": "특성 중요도", "ensemble": "앙상블",
    # week 16
    "kmeans": "k-평균 군집", "cluster_eval": "군집 평가", "hierarchical": "계층 군집·DBSCAN", "pca": "주성분 분석(PCA)",
    "anomaly": "이상치 탐지",
    # week 17
    "scaling": "특성 스케일링", "encoding": "범주형 인코딩", "imputation": "결측치 대체", "pipeline": "파이프라인",
    "feature_selection": "특성 선택",
}

DAYS = [
    (71, "머신러닝이란"), (72, "데이터셋과 특성"), (73, "학습 데이터와 테스트 데이터"), (74, "첫 모델: k-최근접 이웃"),
    (75, "k 고르기와 모델 비교"), (76, "scikit-learn의 공통 패턴"), (77, "11주차 누적 복습"),
    (78, "선형 회귀의 원리"), (79, "scikit-learn 선형 회귀"), (80, "회귀 모델 평가"), (81, "다항 회귀"),
    (82, "규제: Ridge와 Lasso"), (83, "경사하강법 직접 구현"), (84, "12주차 누적 복습"),
    (85, "로지스틱 회귀"), (86, "확률과 결정 임계값"), (87, "결정 경계"), (88, "서포트 벡터 머신"),
    (89, "나이브 베이즈와 텍스트 분류"), (90, "다중 분류"), (91, "13주차 누적 복습"),
    (92, "정확도의 함정과 혼동 행렬"), (93, "정밀도·재현율·F1"), (94, "ROC 곡선과 AUC"), (95, "교차 검증"),
    (96, "과적합과 과소적합"), (97, "하이퍼파라미터 탐색"), (98, "14주차 누적 복습"),
    (99, "결정 트리"), (100, "불순도 계산"), (101, "랜덤 포레스트"), (102, "부스팅"),
    (103, "특성 중요도"), (104, "앙상블 비교"), (105, "15주차 누적 복습"),
    (106, "k-평균 군집"), (107, "군집 수 정하기"), (108, "계층 군집과 DBSCAN"), (109, "주성분 분석(PCA)"),
    (110, "PCA 활용: 시각화와 압축"), (111, "이상치 탐지"), (112, "16주차 누적 복습"),
    (113, "특성 스케일링"), (114, "범주형 인코딩"), (115, "결측치 대체"), (116, "ColumnTransformer와 Pipeline"),
    (117, "특성 선택"), (118, "프로젝트: 전체 파이프라인"), (119, "3단계 마무리 누적 복습"),
]
