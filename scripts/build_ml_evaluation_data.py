from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data/processed/machine_learning.json"
RUBRIC_PATH = ROOT / "data/evaluation/rubrics/machine_learning.json"


def T(i, ko, en="", abbr=None, aliases=None):
    return {"term_id": i, "canonical_ko": ko, "canonical_en": en, "abbreviations": abbr or [], "accepted_aliases": aliases or [], "symbols": [], "not_equivalent_to": []}


TERMINOLOGY = [
    T("ml", "머신러닝", "machine learning", ["ML"]), T("eda", "탐색적 데이터 분석", "exploratory data analysis", ["EDA"]),
    T("feature_engineering", "특성공학", "feature engineering", ["FE"], ["피처 엔지니어링"]), T("validation", "검증", "validation"),
    T("train_set", "학습 세트", "training set", aliases=["train set"]), T("validation_set", "검증 세트", "validation set"), T("test_set", "테스트 세트", "test set"),
    T("cross_validation", "교차 검증", "cross-validation", ["CV"]), T("fold", "폴드", "fold"), T("stratification", "층화", "stratification"),
    T("group_split", "그룹 분할", "group split"), T("time_split", "시간 분할", "time-based split"), T("leakage", "데이터 누수", "data leakage"),
    T("pipeline", "파이프라인", "pipeline"), T("baseline", "베이스라인", "baseline"), T("linear_model", "선형 모델", "linear model"),
    T("logistic_regression", "로지스틱 회귀", "logistic regression"), T("decision_tree", "의사결정나무", "decision tree"),
    T("random_forest", "랜덤 포레스트", "random forest", ["RF"]), T("boosting", "부스팅", "boosting"), T("xgboost", "XGBoost", "XGBoost"),
    T("lightgbm", "LightGBM", "LightGBM", ["LGBM"]), T("catboost", "CatBoost", "CatBoost"), T("svm", "서포트 벡터 머신", "support vector machine", ["SVM"]),
    T("knn", "K-최근접 이웃", "k-nearest neighbors", ["KNN"]), T("neural_network", "신경망", "neural network", ["NN"]),
    T("scaling", "스케일링", "feature scaling"), T("missing_value", "결측치", "missing value"), T("outlier", "이상치", "outlier"),
    T("interaction", "상호작용", "interaction"), T("categorical", "범주형 변수", "categorical variable"), T("one_hot", "원핫 인코딩", "one-hot encoding"),
    T("ordinal_encoding", "순서형 인코딩", "ordinal encoding"), T("target_encoding", "타깃 인코딩", "target encoding"),
    T("class_imbalance", "클래스 불균형", "class imbalance"), T("class_weight", "클래스 가중치", "class weight"), T("threshold", "분류 임계값", "classification threshold"),
    T("smote", "SMOTE", "synthetic minority oversampling technique", ["SMOTE"]), T("accuracy", "정확도", "accuracy"), T("precision", "정밀도", "precision"),
    T("recall", "재현율", "recall"), T("f1", "F1 점수", "F1 score", ["F1"]), T("oof", "OOF 예측", "out-of-fold prediction", ["OOF"]),
    T("calibration", "확률 보정", "probability calibration"), T("hyperparameter", "하이퍼파라미터", "hyperparameter"), T("early_stopping", "조기 종료", "early stopping"),
]


PAGE_TITLES = [
    "Machine Learning 표지", "강의 목차", "Introduction", "ML 프로젝트 전체 흐름", "문제 정의와 데이터 질문", "모델과 결론 질문", "고객 이탈 문제 정의", "모델 밖의 산출물", "의사결정 설명 질문",
    "유효한 실험", "EDA·FE와 실험 규칙", "Train·Validation·Test", "분할 전략", "데이터 누수", "Validation의 역할", "Fold별 Pipeline",
    "모델 선택", "가설 기반 모델 비교", "모델 선택 기준 1", "모델 선택 기준 2", "제약 안의 최선", "Baseline과 선형 모델", "Decision Tree", "Random Forest", "Boosting", "XGBoost·LightGBM·CatBoost", "조건부 모델 선택",
    "모델별 전처리", "모델별 Pipeline", "모델별 전처리 비교", "Scaling과 결측치", "이상치 처리", "Feature Engineering 원칙", "선형 모델의 FE", "트리 모델의 FE", "트리 FE Anti-pattern 1", "트리 FE Anti-pattern 2", "유용한 새 정보", "범주형 변수 판단", "One-hot과 Ordinal", "Target Encoding과 CatBoost", "불균형 학습 순서", "Sampling 주의",
    "평가와 개선", "오류 비용과 지표", "Fold 변동성", "Fold 실패와 OOF", "진단 후 튜닝", "탐색 방법", "Early Stopping", "강의 마무리",
]

CORE = set(range(4, 10)) | set(range(11, 17)) | set(range(18, 28)) | set(range(29, 44)) | set(range(45, 51))
DIVIDERS = {3, 10, 17, 28, 44}
TOC = {2}


CONTENT = {
    4: "머신러닝 프로젝트는 문제 정의, 데이터 이해, EDA, 검증 설계, 전처리·특성공학, 베이스라인, 학습·튜닝, 평가·선택, 오류 분석, 비즈니스 결론의 흐름으로 진행한다.",
    7: "고객 이탈은 고객-월 관측 단위와 과거 90일 입력, 향후 30일 이탈 타깃, 월별 예측 시점을 명시하고 위험 점수를 실제 개입과 효과 측정에 연결한다.",
    12: "학습 세트로 모델을 적합하고 검증 세트 또는 학습 내부 교차 검증으로 선택하며, 테스트 세트는 최종 일반화 성능 확인까지 보존한다.",
    13: "무작위·층화 분할 외에도 동일 개체 반복 관측에는 그룹 분할, 시간 순서가 있는 예측에는 시간 분할을 사용하며 층화만으로 누수를 해결할 수 없다.",
    14: "분할 전에 전체 데이터로 결측치 대체·스케일링·특성 선택·SMOTE를 적합하면 검증 정보가 학습에 들어가는 데이터 누수가 발생한다.",
    16: "교차 검증에서는 각 fold의 학습 부분에만 전처리와 모델을 적합하고 검증 부분에는 변환만 적용하는 Pipeline을 사용한다.",
    18: "모델 선택은 많은 모델을 무작정 나열하기보다 데이터와 제약에 근거한 가설을 세우고 같은 분할과 지표로 비교한다.",
    22: "단순한 베이스라인과 선형·로지스틱 회귀는 비교 기준과 해석 가능한 출발점을 제공한다.",
    23: "의사결정나무는 비선형 임계값과 상호작용을 표현하지만 깊어지면 과적합하고 데이터 변화에 불안정할 수 있다.",
    24: "랜덤 포레스트는 여러 트리의 예측을 평균 또는 투표해 단일 트리의 분산과 불안정성을 줄인다.",
    25: "부스팅은 앞선 모델의 잔차나 오류를 다음 약한 학습기가 순차적으로 보완한다.",
    26: "XGBoost는 범용적이고, LightGBM은 큰 데이터와 빠른 반복에, CatBoost는 범주형·고카디널리티 처리에 강점이 있다.",
    29: "스케일링은 선형 모델·SVM에 중요하고 트리는 임계값 분기라 상대적으로 덜 민감하며 CatBoost는 범주형 변수를 직접 다룰 수 있다.",
    33: "특성공학은 개수를 늘리는 일이 아니라 모델이 쓰기 어려운 도메인·시간·집계 정보를 유효한 표현으로 추가하는 일이다.",
    34: "선형 모델은 상호작용과 비선형 변환을 명시해야 복잡한 관계를 표현할 수 있다.",
    35: "트리 모델은 임계값과 일부 상호작용을 스스로 학습하므로 무분별한 다항·상호작용 특성은 중복과 비용을 늘릴 수 있다.",
    39: "범주형 변수는 순서 존재 여부와 카디널리티를 확인해 인코딩 전략을 고른다.",
    40: "원핫 인코딩은 순서 없는 범주에, 순서형 인코딩은 실제 순서가 있는 범주에 사용한다.",
    41: "타깃 인코딩은 누수를 막도록 fold 내부에서 적합해야 하며 CatBoost는 범주형 변수 처리 대안이 될 수 있다. 식별자라고 해서 자동으로 유용한 특성은 아니다.",
    42: "불균형 문제는 먼저 오류 비용과 사용 목적, 적절한 지표를 정하고 층화, 클래스 가중치, 임계값을 검토한 뒤 필요하면 샘플링한다.",
    43: "SMOTE 같은 샘플링은 학습 fold에만 적용하며 시간·개체·범주 중심 데이터와 라벨 노이즈, 보정·해석성 영향을 점검한다.",
    45: "평가 지표는 오류 비용에 맞춰 정확도·정밀도·재현율·F1 등을 선택한다.",
    46: "교차 검증 평균뿐 아니라 표준편차, 최악 fold 등 변동성을 함께 확인한다.",
    47: "OOF 예측은 학습 데이터 전체에 대한 fold 밖 예측을 모아 임계값·보정·오류 분석 등에 활용한다.",
    48: "하이퍼파라미터 튜닝은 검증과 오류 진단 뒤 복잡도·학습률·규제·샘플링 등 중요한 축을 대상으로 수행한다.",
    50: "Early stopping은 테스트 세트가 아닌 검증 성능으로 과도한 반복을 막으며, 잘못된 검증 설계나 데이터 문제를 고치지는 못한다.",
}
CONTENT.update({
    5:"문제 정의 단계에서는 예측 대상과 관측 단위, 예측 시점, 데이터 생성 과정과 실제 의사결정에 필요한 출력을 먼저 확인한다.",
    6:"모델링 단계에서는 비교 기준과 검증 방법, 오류 비용, 결과 해석과 비즈니스 결론까지 설명할 수 있어야 한다.",
    8:"산출물은 모델 파일뿐 아니라 데이터·검증 설계, 재현 가능한 Pipeline, 오류 분석, 해석과 운영 제안을 포함한다.",
    9:"각 선택의 이유, 대안, 검증 근거와 한계를 설명할 수 있어야 모델 결과가 의사결정 근거가 된다.",
    11:"EDA와 FE는 split·preprocessing·model·metric 선택에 정보를 주지만 비교 모델에는 공통 실험 규칙을 먼저 세운다.",
    15:"Validation은 모델 성능을 측정하고 선택하는 용도이며 validation 정보로 전처리 기준을 적합하면 누수가 된다.",
    19:"데이터 표본 수·특성 수·희소성 같은 크기와 형태, 선형·비선형 관계 및 상호작용 복잡도를 고려한다.",
    20:"변수 타입과 전처리, 설명 가능성, 학습·추론 시간과 메모리·운영 비용도 모델 선택 기준이다.",
    21:"최고 모델은 절대적이지 않고 데이터와 해석·운영 제약 안에서 검증 성능과 비용의 균형이 좋은 모델이다.",
    27:"SVM·KNN·신경망도 데이터 크기, 차원, 거리 구조, 비선형성과 연산 제약이 맞는 조건에서 후보가 된다.",
    30:"같은 원자료라도 선형·거리 기반 모델, 트리, 범주형 특화 모델은 scaling·encoding·결측 처리 요구가 다르다.",
    31:"Scaling 기준과 결측치 대체 통계는 학습 fold에서만 추정하고 모델 민감도와 결측 의미를 고려해 적용한다.",
    32:"이상치는 오류인지 희귀 신호인지 먼저 판단하고 모델 강건성, 변환·절단의 정보 손실을 고려해 처리한다.",
    36:"트리에 임의 구간화나 대량 다항 특성을 추가하면 원래 학습할 분기를 중복하고 잡음·복잡도를 늘릴 수 있다.",
    37:"가능한 모든 상호작용을 생성하거나 같은 정보를 여러 형태로 복제하면 차원과 과적합 위험이 높아진다.",
    38:"트리에서도 예측 시점에 사용 가능한 도메인 지식, 기간 집계, 시간 경과와 그룹 통계는 유용한 특성이 된다.",
    49:"Grid는 정해진 조합, random은 공간 표본, Bayesian·Optuna 방식은 이전 결과를 이용해 다음 탐색 지점을 정한다.",
})


def _role(page):
    if page == 1: return "cover"
    if page in TOC: return "table_of_contents"
    if page in DIVIDERS: return "section_divider"
    if page == 51: return "closing"
    return "core_content" if page in CORE else "supplementary_reference"


def _curate(page):
    title = PAGE_TITLES[page - 1]
    content = CONTENT.get(page, f"{title}에서 머신러닝 프로젝트의 판단 기준과 적용 맥락을 설명한다." if _role(page) == "core_content" else f"{title} 페이지이다.")
    return [{"topic": title, "concepts": [title], "visual_description": f"{title}의 핵심 도식과 설명을 제시한다." if _role(page) == "core_content" else f"{title} 페이지이다.", "content": content}]


CURATION = {page: _curate(page) for page in range(1, 52)}


def U(i, p, kind, excerpt, explanation, terms):
    return {"unit_id": i, "page": p, "type": kind, "source_type": "text", "source_excerpt": excerpt, "normalized_explanation": explanation, "source_status": "verified", "term_ids": terms}


UNITS = [
    U("ml_p4_flow",4,"procedure","문제 정의 → 데이터 이해/수집 → EDA → 검증 전략 → 전처리/FE → Baseline → 학습/Tuning → 평가/선택 → 해석/Error Analysis → 비즈니스 결론","프로젝트 의사결정은 문제 정의부터 평가와 활용 결론까지 연결된다.",["ml","eda","feature_engineering","validation","baseline"]),
    U("ml_p7_churn",7,"example","관측 단위 customer-month / 과거 90일 / 향후 30일 / 매월 1회 예측 / Risk score","예측 단위·시점·입력 기간·타깃 기간과 활용을 명시한다.",["ml","threshold"]),
    U("ml_p12_split",12,"procedure","Train / Validation / Test / CV는 Train 안에서 / Test는 마지막까지 보존","학습·선택·최종 평가 데이터를 분리한다.",["train_set","validation_set","test_set","cross_validation"]),
    U("ml_p13_strategy",13,"comparison","Random/Stratified / Group / Time split / Stratification은 leakage를 해결하지 않음","데이터 생성 구조에 맞춰 분할한다.",["stratification","group_split","time_split","leakage"]),
    U("ml_p14_leak",14,"warning","split 전에 전체 데이터로 imputer/scaler/feature selection/SMOTE fit","검증 정보로 전처리를 적합하면 누수다.",["leakage","scaling","smote"]),
    U("ml_p15_validation",15,"warning","Validation은 성능을 측정하는 용도 / preprocessing 기준을 정하는 데 사용하지 않음","검증 정보로 전처리 기준을 적합하지 않는다.",["validation","validation_set","leakage"]),
    U("ml_p16_pipe",16,"procedure","각 fold의 training에만 imputation/scaling/encoding/feature selection/sampling/model fit, validation에는 transform","전처리와 샘플링을 fold 안에 넣는다.",["pipeline","fold","cross_validation","leakage"]),
    U("ml_p18_hypothesis",18,"procedure","왜 이 모델을 비교하는가? / model zoo가 아니라 hypothesis-driven comparison","근거 있는 후보를 동일 조건으로 비교한다.",["ml","validation"]),
    U("ml_p19_criteria",19,"comparison","데이터 크기·형태 / 관계 복잡도 / 변수 타입·전처리 / 설명 가능성 / 계산·운영 비용","성능 외 제약을 포함해 모델을 고른다.",["ml","feature_engineering"]),
    U("ml_p22_baseline",22,"definition","Baseline / Logistic Regression / Linear model","단순 모델은 해석 가능한 비교 기준이다.",["baseline","logistic_regression","linear_model"]),
    U("ml_p23_tree",23,"comparison","비선형 관계 / 깊은 tree는 overfitting / 데이터 변화에 불안정","트리의 표현력과 분산 위험을 함께 본다.",["decision_tree"]),
    U("ml_p24_rf",24,"definition","여러 Decision Tree의 결과를 평균/투표","랜덤 포레스트는 앙상블로 단일 트리 분산을 줄인다.",["random_forest","decision_tree"]),
    U("ml_p25_boost",25,"procedure","이전 모델의 residual/error를 다음 모델이 순차적으로 학습","부스팅은 오류를 순차 보완한다.",["boosting"]),
    U("ml_p26_gbm",26,"comparison","XGBoost / LightGBM / CatBoost / categorical/high-cardinality","부스팅 구현별 데이터·운영 강점이 다르다.",["xgboost","lightgbm","catboost","categorical"]),
    U("ml_p29_modelprep",29,"comparison","Linear/SVM: scaling 중요 / Tree: scale 영향 작음 / CatBoost: categorical 직접 처리","전처리는 모델 특성에 맞춘다.",["linear_model","svm","decision_tree","catboost","scaling","categorical"]),
    U("ml_p33_fe",33,"definition","Feature Engineering은 많을수록 좋은 것이 아님 / 새로운 정보와 유효한 표현","특성 수보다 정보와 모델 적합성이 중요하다.",["feature_engineering"]),
    U("ml_p34_linearfe",34,"relation","Linear model은 interaction/nonlinear transform을 명시적으로 추가","선형 모델에는 필요한 관계를 특성으로 표현한다.",["linear_model","interaction","feature_engineering"]),
    U("ml_p35_treefe",35,"warning","Tree는 threshold/interaction을 학습 / 무분별한 polynomial·all interactions","트리에 중복 변환을 대량 추가하지 않는다.",["decision_tree","interaction","feature_engineering"]),
    U("ml_p39_cat",39,"procedure","ordered? / cardinality?","순서와 카디널리티로 범주형 처리법을 정한다.",["categorical","ordinal_encoding"]),
    U("ml_p40_encoding",40,"comparison","One-hot Encoding / Ordinal Encoding","명목형과 순서형을 구분한다.",["one_hot","ordinal_encoding","categorical"]),
    U("ml_p41_target",41,"warning","Target Encoding / CatBoost / ID와 순서 ID는 자동으로 유용하지 않음","타깃 인코딩 누수와 식별자 오용을 막는다.",["target_encoding","catboost","leakage"]),
    U("ml_p42_imb",42,"procedure","오류 비용·사용 목적 → metric → stratified → class weight → threshold → sampling","샘플링 전에 목적·지표·가중치·임계값을 검토한다.",["class_imbalance","stratification","class_weight","threshold","smote"]),
    U("ml_p43_sampling",43,"warning","sampling은 training fold에만 / time·entity·categorical·label noise·calibration 주의","샘플링은 fold 내부에서 데이터 구조와 부작용을 점검한다.",["smote","fold","time_split","group_split","calibration"]),
    U("ml_p45_metrics",45,"comparison","Accuracy / Recall / Precision / F1 / error cost","오류 비용에 맞는 지표를 선택한다.",["accuracy","recall","precision","f1"]),
    U("ml_p46_variance",46,"interpretation","mean뿐 아니라 fold variance/std/worst fold","평균과 변동성·취약 fold를 함께 본다.",["fold","cross_validation"]),
    U("ml_p47_oof",47,"procedure","OOF predictions / threshold / calibration / error analysis / stacking","OOF 예측은 학습 표본의 fold 밖 예측을 모은다.",["oof","fold","threshold","calibration"]),
    U("ml_p48_tune",48,"procedure","진단 후 중요한 parameter만 CV로 tuning / complexity, learning rate, regularization, sampling","튜닝은 검증 진단 이후 제한된 핵심 축에 집중한다.",["hyperparameter","cross_validation"]),
    U("ml_p50_es",50,"warning","early stopping에 Test 사용 금지 / fold별 optimum / validation·data 문제를 고치지 못함","조기 종료는 검증 데이터로 반복 수를 제어한다.",["early_stopping","validation_set","test_set","fold"]),
]


MAP = {
    "ml.project_flow":["ml_p4_flow"], "ml.problem_unit":["ml_p7_churn"], "ml.split_roles":["ml_p12_split"], "ml.split_strategy":["ml_p13_strategy"],
    "ml.leakage":["ml_p14_leak"], "ml.validation_boundary":["ml_p15_validation"], "ml.fold_pipeline":["ml_p16_pipe"], "ml.hypothesis_selection":["ml_p18_hypothesis"], "ml.selection_constraints":["ml_p19_criteria"],
    "ml.baseline":["ml_p22_baseline"], "ml.linear_role":["ml_p22_baseline"], "ml.tree":["ml_p23_tree"], "ml.random_forest":["ml_p24_rf"], "ml.boosting":["ml_p25_boost"], "ml.boosting_variants":["ml_p26_gbm"],
    "ml.model_specific_preprocessing":["ml_p29_modelprep"], "ml.scaling_sensitivity":["ml_p29_modelprep"], "ml.fe_principle":["ml_p33_fe"], "ml.linear_fe":["ml_p34_linearfe"], "ml.tree_fe":["ml_p35_treefe"],
    "ml.categorical_choice":["ml_p39_cat"], "ml.encoding":["ml_p40_encoding"], "ml.target_encoding":["ml_p41_target"], "ml.imbalance_order":["ml_p42_imb"], "ml.sampling_fold":["ml_p43_sampling"],
    "ml.metric_cost":["ml_p45_metrics"], "ml.cv_variability":["ml_p46_variance"], "ml.oof":["ml_p47_oof"], "ml.tuning":["ml_p48_tune"], "ml.early_stopping":["ml_p50_es"],
}

ERRORS = {
    "ml.split_roles":["테스트 세트를 반복적인 모델 선택과 튜닝에 사용해도 된다고 설명"], "ml.leakage":["전체 데이터로 전처리를 적합한 뒤 교차 검증해도 누수가 아니라고 설명"],
    "ml.fold_pipeline":["검증 fold까지 포함해 scaler나 SMOTE를 적합한다고 설명"], "ml.tree":["의사결정나무는 깊어질수록 항상 일반화가 좋아진다고 설명"],
    "ml.random_forest":["랜덤 포레스트가 하나의 트리만 깊게 학습하는 모델이라고 설명"], "ml.boosting":["부스팅의 모든 모델이 서로의 오류와 무관하게 완전히 독립 학습된다고 설명"],
    "ml.model_specific_preprocessing":["모든 모델에 동일 전처리가 언제나 필수라고 설명"], "ml.encoding":["순서 없는 범주에 임의 숫자를 부여해 그 대소관계를 의미 있는 순서로 해석"],
    "ml.target_encoding":["전체 데이터의 타깃 평균으로 인코딩한 뒤 검증해도 누수가 아니라고 설명"], "ml.imbalance_order":["불균형이면 목적과 지표 검토 없이 정확도와 SMOTE만 사용하면 된다고 설명"],
    "ml.sampling_fold":["검증·테스트 데이터에도 SMOTE를 적용한다고 설명"], "ml.metric_cost":["모든 분류 문제에서 정확도 하나가 항상 충분하다고 설명"],
    "ml.early_stopping":["테스트 성능을 반복 확인해 early stopping 시점을 선택한다고 설명"],
}


def C(i, role, text, category="explanation_application"):
    return {"claim_id":i,"role":role,"category":category,"text":text,"weight":1.0,"evidence":[],"term_ids":[],"evaluation_criteria":{"required_elements":[text],"critical_errors":ERRORS.get(i,[])}}


def S(i, title, summary, claims): return {"sub_objective_id":i,"title":title,"summary":summary,"claims":claims}
def O(i, title, desc, subs):
    n=sum(len(s["claims"]) for s in subs)
    return {"objective_id":i,"title":title,"selection_description":desc,"supporting_claim_slots":2 if n<=8 else 3,"sub_objectives":subs}


def build_rubric():
    objectives = [
        O("ml.valid_experiment","유효한 문제 정의와 실험 설계","예측 문제를 명세하고 일반화 성능을 누수 없이 검증한다.",[
            S("ml.experiment.problem","문제와 활용 정의","단위·시점·활용을 명확히 한다.",[C("ml.project_flow","supporting","머신러닝 프로젝트는 문제 정의부터 데이터·검증·모델링·오류 분석과 실제 활용 결론까지 연결된다."),C("ml.problem_unit","essential","예측 문제는 관측 단위, 입력 관측 기간, 예측 대상 기간, 예측 시점과 결과의 사용 방식을 구체화해야 한다.","core_understanding")]),
            S("ml.experiment.split","데이터 분할","학습·선택·평가 역할을 분리한다.",[C("ml.split_roles","essential","모델은 학습 세트에 적합하고 검증 세트나 학습 내부 CV로 선택하며 테스트 세트는 마지막 일반화 평가까지 보존한다.","core_understanding"),C("ml.split_strategy","supporting","반복 개체는 group split, 시간 예측은 time split을 고려하며 stratification만으로 개체·시간 누수를 해결할 수 없다.")]),
            S("ml.experiment.leakage","누수 방지 Pipeline","전처리를 fold 내부에서 수행한다.",[C("ml.leakage","essential","분할 전에 전체 데이터로 대체·스케일링·특성 선택·SMOTE를 적합하면 검증 정보가 학습에 들어가는 누수다.","core_understanding"),C("ml.validation_boundary","supporting","Validation은 모델 성능을 측정하는 자료이지 전체 전처리 기준을 미리 적합하는 자료가 아니다."),C("ml.fold_pipeline","supporting","교차 검증의 각 fold에서 전처리·샘플링·모델은 training 부분에만 fit하고 validation에는 transform과 예측만 적용한다.")])]),
        O("ml.model_selection","근거 기반 모델 선택","데이터·관계·해석·운영 제약에 맞는 후보를 비교한다.",[
            S("ml.selection.process","비교 원칙","가설과 동일 조건을 사용한다.",[C("ml.hypothesis_selection","essential","모델 선택은 model zoo 나열이 아니라 후보가 적합할 이유를 세우고 같은 분할·지표로 비교하는 가설 기반 과정이다.","core_understanding"),C("ml.selection_constraints","supporting","데이터 크기·형태, 관계 복잡도, 변수 타입·전처리, 설명 가능성, 계산·운영 비용을 함께 고려한다.")]),
            S("ml.selection.baseline","Baseline과 선형 모델","복잡한 모델의 비교 출발점을 둔다.",[C("ml.baseline","essential","단순 baseline은 복잡한 모델이 실제로 개선했는지 판단하는 최소 비교 기준을 제공한다."),C("ml.linear_role","supporting","선형·로지스틱 회귀는 해석 가능한 출발점이며 관계가 단순하거나 설명 가능성이 중요할 때 유용하다.")]),
            S("ml.selection.trees","Tree ensemble","트리 계열의 차이를 설명한다.",[C("ml.tree","essential","의사결정나무는 비선형 임계값과 상호작용을 표현하지만 깊어지면 과적합하고 데이터 변화에 불안정할 수 있다."),C("ml.random_forest","supporting","랜덤 포레스트는 여러 트리 예측을 평균·투표해 단일 트리의 분산과 불안정성을 줄인다."),C("ml.boosting","supporting","부스팅은 앞선 모델의 잔차나 오류를 다음 약한 학습기가 순차적으로 보완한다."),C("ml.boosting_variants","supporting","XGBoost·LightGBM·CatBoost는 구현과 데이터 처리 특성이 달라 데이터 규모·속도·범주형 구조에 따라 선택한다.")])]),
        O("ml.model_specific_pipeline","모델별 전처리와 특성공학","모델의 귀납적 편향과 데이터 구조에 맞춰 표현을 설계한다.",[
            S("ml.preprocess.model","모델별 전처리","모든 모델에 같은 변환을 강제하지 않는다.",[C("ml.model_specific_preprocessing","essential","스케일링은 선형 모델·SVM에 중요하고 트리는 상대적으로 덜 민감하며 CatBoost는 범주형 변수를 직접 처리할 수 있어 전처리는 모델별로 달라야 한다.","core_understanding"),C("ml.scaling_sensitivity","supporting","거리·내적과 계수 크기에 민감한 모델과 임계값 분기 기반 트리는 scaling 영향이 서로 다르다.")]),
            S("ml.preprocess.fe","Feature Engineering","새 정보와 필요한 관계를 표현한다.",[C("ml.fe_principle","essential","Feature Engineering은 특성을 무조건 늘리는 일이 아니라 도메인·시간·집계의 새 정보를 모델이 쓸 수 있게 표현하는 일이다."),C("ml.linear_fe","supporting","선형 모델은 상호작용과 비선형 변환을 명시적으로 추가해야 복잡한 관계를 표현할 수 있다."),C("ml.tree_fe","supporting","트리는 임계값과 일부 상호작용을 학습하므로 무분별한 binning·다항·전체 상호작용 특성은 중복과 비용을 늘릴 수 있다.")]),
            S("ml.preprocess.category","범주형 처리","순서·카디널리티·누수를 점검한다.",[C("ml.categorical_choice","essential","범주형 변수는 실제 순서의 존재와 카디널리티를 확인해 처리 전략을 정한다."),C("ml.encoding","supporting","순서 없는 범주는 one-hot, 실제 순서가 있는 범주는 ordinal encoding을 고려한다."),C("ml.target_encoding","supporting","Target encoding은 fold 내부에서 적합해 누수를 막아야 하며 식별자 열은 자동으로 유용한 범주형 특성이 아니다.")])]),
        O("ml.evaluation_improvement","평가·불균형 대응과 튜닝","오류 비용, 검증 변동성과 오류 분석을 바탕으로 개선한다.",[
            S("ml.eval.imbalance","불균형 대응","샘플링 전 목적과 지표를 정한다.",[C("ml.imbalance_order","essential","클래스 불균형은 오류 비용과 사용 목적·지표를 정한 뒤 stratification, class weight, threshold를 검토하고 필요할 때 sampling한다.","core_understanding"),C("ml.sampling_fold","supporting","SMOTE 같은 sampling은 training fold에만 적용하고 시간·개체 구조, 범주형 비중, 라벨 노이즈와 calibration 영향을 점검한다.")]),
            S("ml.eval.metrics","평가 해석","평균 외 변동성과 fold 실패를 본다.",[C("ml.metric_cost","essential","Accuracy·precision·recall·F1 중 실제 오류 비용과 의사결정 목적에 맞는 지표를 선택한다."),C("ml.cv_variability","supporting","교차 검증 평균뿐 아니라 표준편차·최악 fold와 fold별 실패 원인을 확인한다."),C("ml.oof","supporting","OOF prediction은 각 표본의 fold 밖 예측을 모아 threshold·calibration·오류 분석에 활용한다.")]),
            S("ml.eval.tuning","튜닝과 조기 종료","진단 이후 검증 데이터로 개선한다.",[C("ml.tuning","essential","하이퍼파라미터 튜닝은 오류 진단 뒤 CV로 복잡도·학습률·규제·샘플링 같은 중요한 축에 집중한다."),C("ml.early_stopping","supporting","Early stopping은 test가 아닌 validation 성능으로 반복 수를 제어하며 잘못된 데이터나 검증 설계를 고치지는 못한다.")])]),
    ]
    return {"schema_version":"2.2.0","lecture_id":"machine_learning","lecture_name":"Machine Learning","assessment":{"mode":"selected_topic_recall","target_seconds":120,"max_seconds":120,"score_policy":{"essential_points":60,"supporting_points":20,"coverage_points":20}},"top_level_objectives":objectives,"excluded_source_claims":[]}


def apply_evaluation_data(processed_path=PROCESSED_PATH, rubric_path=RUBRIC_PATH):
    data=json.loads(Path(processed_path).read_text(encoding="utf-8")); pages={x["page"]:x for x in data["chunks"]}
    if set(pages)!=set(range(1,52)): raise ValueError("ML PDF 1~51쪽이 필요합니다.")
    data["schema_version"]="2.1.0"; data["terminology"]=TERMINOLOGY
    for p in pages:
        pages[p].update(page_role=_role(p), term_ids=[], evidence_units=[], source_issues=[])
    lookup={}
    for raw in UNITS:
        unit=dict(raw); p=unit.pop("page"); pages[p]["term_ids"]=list(dict.fromkeys(pages[p]["term_ids"]+unit["term_ids"])); pages[p]["evidence_units"].append(unit); lookup[unit["unit_id"]]=(pages[p],unit)
    Path(processed_path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    rubric=build_rubric(); claims={c["claim_id"]:c for o in rubric["top_level_objectives"] for s in o["sub_objectives"] for c in s["claims"]}
    if set(claims)!=set(MAP): raise ValueError(f"Claim mismatch: {set(claims)^set(MAP)}")
    for cid,uids in MAP.items():
        terms=[]
        for uid in uids:
            chunk,unit=lookup[uid]; terms+=unit["term_ids"]; claims[cid]["evidence"].append({"page":chunk["page"],"chunk_id":chunk["chunk_id"],"unit_id":uid,"source_excerpt":unit["source_excerpt"],"source_status":"verified","review_note":""})
        claims[cid]["term_ids"]=list(dict.fromkeys(terms))
    Path(rubric_path).parent.mkdir(parents=True,exist_ok=True); Path(rubric_path).write_text(json.dumps(rubric,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
