from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "eda_fe.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "eda_fe.json"


def term(term_id: str, ko: str, en: str = "", *, abbreviations=None, aliases=None,
         symbols=None, not_equivalent_to=None) -> dict[str, Any]:
    return {"term_id": term_id, "canonical_ko": ko, "canonical_en": en,
            "abbreviations": abbreviations or [], "accepted_aliases": aliases or [],
            "symbols": symbols or [], "not_equivalent_to": not_equivalent_to or []}


TERMINOLOGY = [
    term("eda", "탐색적 데이터 분석", "exploratory data analysis", abbreviations=["EDA"], aliases=["탐색적 분석"]),
    term("preprocessing", "데이터 전처리", "data preprocessing", aliases=["전처리"]),
    term("feature_engineering", "특성공학", "feature engineering", abbreviations=["FE"], aliases=["피처 엔지니어링"]),
    term("data_type", "데이터 타입", "data type", abbreviations=["dtype"]),
    term("label_encoding", "라벨 인코딩", "label encoding", aliases=["순서형 인코딩", "ordinal encoding"]),
    term("one_hot_encoding", "원핫 인코딩", "one-hot encoding", aliases=["one hot encoding"]),
    term("dummy_encoding", "더미 인코딩", "dummy encoding"),
    term("missing_value", "결측치", "missing value", aliases=["NA", "NaN", "null"]),
    term("imputation", "결측치 대체", "imputation", aliases=["대체"]),
    term("outlier", "이상치", "outlier", aliases=["이상값"]),
    term("standard_deviation_rule", "3시그마 규칙", "three-sigma rule", aliases=["3 sigma rule"]),
    term("iqr", "사분위 범위", "interquartile range", abbreviations=["IQR"], symbols=["Q3-Q1"]),
    term("class_imbalance", "클래스 불균형", "class imbalance", aliases=["불균형 데이터"]),
    term("accuracy", "정확도", "accuracy"),
    term("precision", "정밀도", "precision"),
    term("recall", "재현율", "recall", aliases=["sensitivity"]),
    term("f1", "F1 점수", "F1-score", abbreviations=["F1"]),
    term("pr_auc", "PR AUC", "precision-recall area under curve", abbreviations=["PR-AUC"]),
    term("undersampling", "언더샘플링", "undersampling", aliases=["under sampling"]),
    term("oversampling", "오버샘플링", "oversampling", aliases=["over sampling"]),
    term("smote", "SMOTE", "synthetic minority over-sampling technique", abbreviations=["SMOTE"]),
    term("focal_loss", "포컬 로스", "focal loss"),
    term("multicollinearity", "다중공선성", "multicollinearity"),
    term("vif", "분산팽창계수", "variance inflation factor", abbreviations=["VIF"], symbols=["1/(1-R²)"]),
    term("scaling", "스케일링", "feature scaling", aliases=["정규화", "표준화"]),
    term("standard_scaler", "표준 스케일링", "standard scaling", aliases=["Z-score normalization", "standardization"]),
    term("minmax_scaler", "최소-최대 스케일링", "min-max scaling", aliases=["normalization"]),
    term("robust_scaler", "로버스트 스케일링", "robust scaling"),
    term("merge", "데이터 병합", "merge", aliases=["join", "pd.merge"]),
    term("groupby", "그룹화", "group by", aliases=["groupby", "pd.groupby"]),
    term("feature_selection", "특성 선택", "feature selection"),
    term("feature_extraction", "특성 추출", "feature extraction"),
    term("dimensionality_reduction", "차원 축소", "dimensionality reduction"),
    term("curse_dimensionality", "차원의 저주", "curse of dimensionality"),
    term("filter_method", "필터 방식", "filter method"),
    term("wrapper_method", "래퍼 방식", "wrapper method"),
    term("rfe", "재귀적 특성 제거", "recursive feature elimination", abbreviations=["RFE"]),
    term("embedded_method", "임베디드 방식", "embedded method"),
    term("lasso", "라쏘", "Lasso", aliases=["L1 regularization"]),
    term("derived_feature", "파생변수", "derived feature", aliases=["파생 특성"]),
    term("lag", "지연 변수", "lag feature", aliases=["lag"]),
    term("moving_average", "이동평균", "moving average", aliases=["rolling mean"]),
    term("data_leakage", "데이터 누수", "data leakage", aliases=["누수", "leakage"]),
    term("target_encoding", "타깃 인코딩", "target encoding"),
    term("train_test_contamination", "훈련-테스트 오염", "train-test contamination", aliases=["train test contamination"]),
    term("pca", "주성분분석", "principal component analysis", abbreviations=["PCA"]),
    term("lda", "선형판별분석", "linear discriminant analysis", abbreviations=["LDA"]),
    term("tokenization", "토큰화", "tokenization"),
    term("vectorization", "벡터화", "vectorization"),
    term("tfidf", "TF-IDF", "term frequency-inverse document frequency", abbreviations=["TF-IDF"]),
    term("embedding", "임베딩", "embedding"),
    term("augmentation", "데이터 증강", "data augmentation"),
]


def unit(unit_id: str, kind: str, source_type: str, excerpt: str,
         explanation: str, term_ids: list[str]) -> dict[str, Any]:
    return {"unit_id": unit_id, "type": kind, "source_type": source_type,
            "source_excerpt": excerpt, "normalized_explanation": explanation,
            "source_status": "verified", "term_ids": term_ids}


U = unit
ROLES = {1: "cover", 2: "table_of_contents", 3: "section_divider", 7: "section_divider",
         24: "section_divider", 35: "section_divider", 42: "closing"}
PAGE_DATA = {page: {"page_role": ROLES.get(page, "core_content"), "term_ids": [],
                    "evidence_units": []} for page in range(1, 43)}


def page(number: int, term_ids: list[str], units: list[dict[str, Any]], *, role: str | None = None,
         source_issues: list[dict[str, str]] | None = None) -> None:
    PAGE_DATA[number]["term_ids"] = term_ids
    PAGE_DATA[number]["evidence_units"] = units
    if role:
        PAGE_DATA[number]["page_role"] = role
    if source_issues:
        PAGE_DATA[number]["source_issues"] = source_issues


page(4, ["eda", "preprocessing", "feature_engineering"], [
    U("eda_fe_p4_u01", "relation", "text", "Garbage in, Garbage out; 좋은 입력 데이터가 좋은 결과의 기본", "모델이 좋아도 입력 품질이 나쁘면 결과가 나빠지므로 EDA·전처리·특성공학이 필요하다.", ["eda", "preprocessing", "feature_engineering"]),
])
page(5, ["eda", "preprocessing", "feature_engineering"], [
    U("eda_fe_p5_u01", "comparison", "text", "EDA: 데이터 구조·타입·분포·이상치 탐색으로 방향 결정 / 전처리: 결측치·이상치·정규화·인코딩 / FE: 특성 생성·제거·변형", "EDA는 이해와 방향 설정, 전처리는 정제, FE는 정보력 있는 특성 구성을 담당한다.", ["eda", "preprocessing", "feature_engineering"]),
])
page(6, ["eda", "preprocessing", "feature_engineering"], [
    U("eda_fe_p6_u01", "procedure", "text_and_visual", "문제 정의 → 데이터 수집 → EDA·전처리·FE → 분석/모델링 → 결과/결론", "분석은 문제와 목표를 정하고 데이터를 수집·탐색·정제·가공한 뒤 모델링과 결론으로 이어진다.", ["eda", "preprocessing", "feature_engineering"]),
])
page(8, ["eda", "data_type", "missing_value", "outlier", "class_imbalance", "multicollinearity"], [
    U("eda_fe_p8_u01", "procedure", "text", "데이터 형태 → 변수 타입 → 결측치·이상치 → 종속변수 분포 → 변수 간 및 변수-종속변수 관계 파악", "EDA에서는 구조·타입·품질·타깃 분포·변수 관계를 체계적으로 점검한다.", ["eda", "data_type", "missing_value", "outlier", "class_imbalance", "multicollinearity"]),
])
page(10, ["eda", "data_type"], [
    U("eda_fe_p10_u01", "procedure", "visual", "데이터의 행·열 크기, 변수명, 샘플 행과 용어집을 확인하는 예시", "행·열, 변수명, 샘플 값을 보고 용어집·도메인 자료로 각 열의 의미를 파악한다.", ["eda", "data_type"]),
])
page(11, ["label_encoding", "one_hot_encoding", "dummy_encoding", "multicollinearity"], [
    U("eda_fe_p11_u01", "comparison", "text", "Label Encoding: 0,1,2,3 할당; 등급처럼 순서가 있는 범주 / One-hot: 각 범주별 0,1 열; 색상처럼 순서 없는 범주", "순서형 범주는 라벨 인코딩, 명목형 범주는 원핫 인코딩을 고려한다.", ["label_encoding", "one_hot_encoding"]),
    U("eda_fe_p11_u02", "comparison", "text", "Dummy Encoding: One-hot에서 column 하나 제거; 다중공선성 해결; 기준 범주가 생김", "더미 인코딩은 원핫 열 하나를 제거해 완전 다중공선성을 피하는 대신 기준 범주가 생긴다.", ["dummy_encoding", "one_hot_encoding", "multicollinearity"]),
])
page(12, ["data_type"], [
    U("eda_fe_p12_u01", "diagnostic", "visual", "변수의 숫자형·범주형·날짜형 의미와 int·float·object 등 실제 dtype을 확인하는 예시", "변수의 개념적 타입과 저장된 dtype을 확인하고 불일치하면 변환한다.", ["data_type"]),
])
page(13, ["missing_value", "imputation"], [
    U("eda_fe_p13_u01", "procedure", "text", "연속형은 중앙값·평균값, 범주형은 최빈값; 도메인 지식, 결측 지표, 관련 변수, 결측 비율이 높은 열 삭제를 고려", "대표값 대체만 자동 적용하지 말고 도메인·원인·결측 자체의 정보성·관련 변수·삭제 비용을 비교한다.", ["missing_value", "imputation"]),
])
page(14, ["outlier", "standard_deviation_rule", "iqr"], [
    U("eda_fe_p14_u01", "diagnostic", "text", "3시그마, Boxplot IQR(Q1-1.5×IQR, Q3+1.5×IQR), 클러스터링, AutoEncoder로 이상치 탐지", "분포와 목적에 맞게 3시그마·IQR·클러스터링·오토인코더 등으로 이상치 후보를 찾는다.", ["outlier", "standard_deviation_rule", "iqr"]),
    U("eda_fe_p14_u02", "procedure", "text", "이상치 처리: 제거, 로그·제곱근 변환, 대체, 그대로 활용; 이상탐지에서는 필요할 수 있음", "후보가 오류인지 의미 있는 신호인지 판단한 뒤 제거·변환·대체·유지를 선택한다.", ["outlier"]),
])
page(15, ["outlier"], [
    U("eda_fe_p15_u01", "warning", "text", "주의: 이상치 제거는 학습할 때에만 사용", "이상치 제거는 훈련 데이터에 적용하고 검증·테스트 관측치를 성능 평가 전에 제거해 평가 분포를 바꾸지 않는다.", ["outlier"]),
])
page(16, ["class_imbalance", "accuracy", "precision", "recall", "f1", "pr_auc"], [
    U("eda_fe_p16_u01", "warning", "text", "클래스 불균형에서는 모두 다수 class로 예측해도 성능이 좋아 보이므로 accuracy는 잘못 평가할 수 있음", "불균형 분류에서 정확도만 보면 다수 클래스 예측 모델을 과대평가할 수 있다.", ["class_imbalance", "accuracy"]),
    U("eda_fe_p16_u02", "comparison", "text", "Precision, Recall, F1-Score, PR AUC로 소수 클래스 탐지 성능 평가", "정밀도·재현율·F1·PR AUC 등을 문제의 오류 비용에 맞게 함께 본다.", ["precision", "recall", "f1", "pr_auc", "class_imbalance"]),
])
page(17, ["class_imbalance", "undersampling", "oversampling", "smote"], [
    U("eda_fe_p17_u01", "comparison", "text", "Under Sampling은 다수 class를 줄여 정보 손실·과소적합 우려 / Over Sampling은 소수 class를 늘려 왜곡·과적합 우려", "언더샘플링의 정보 손실과 오버샘플링의 왜곡·과적합 위험을 데이터 크기와 모델에 맞게 비교한다.", ["class_imbalance", "undersampling", "oversampling", "smote"]),
])
page(18, ["class_imbalance", "focal_loss"], [
    U("eda_fe_p18_u01", "procedure", "text", "Focal Loss: 소수 class에 대한 loss 가중치 부여 / Minority-aware fine tuning: 전체 학습 후 소수 클래스 중심 학습", "샘플링 외에도 어려운·소수 예제에 더 집중하는 손실함수나 추가 학습을 사용할 수 있다.", ["class_imbalance", "focal_loss"]),
])
page(19, ["multicollinearity"], [
    U("eda_fe_p19_u01", "diagnostic", "text", "변수 분포·변수 간 상관관계·변수-종속변수 관계를 탐색해 중요 특성과 다중공선성을 파악", "분포와 상관, 타깃과의 관계를 통해 중요 특성과 다중공선성 후보를 찾는다.", ["multicollinearity"]),
])
page(20, ["multicollinearity", "vif", "pca", "lasso"], [
    U("eda_fe_p20_u01", "definition", "text", "다중공선성: 독립변수들 간에 강한 상관관계; feature importance가 왜곡될 수 있음", "다중공선성은 설명변수 간 강한 관계로 계수·중요도 해석을 불안정하게 만든다.", ["multicollinearity"]),
    U("eda_fe_p20_u02", "procedure", "text_and_formula", "VIF=1/(1-R²); 일반적으로 10 이상을 참고하지만 절대적이지 않음; 변수 제거·결합, Ridge·Lasso, PCA", "VIF를 맥락적으로 해석하고 변수 제거·결합·규제·PCA 등의 대안을 비교한다.", ["multicollinearity", "vif", "pca", "lasso"]),
])
page(21, ["scaling"], [
    U("eda_fe_p21_u01", "relation", "text", "특성마다 범위가 크게 다르면 큰 범위의 특성을 과도하게 중요시할 수 있음", "스케일링은 특성 단위·범위가 거리·분산 계산을 과도하게 지배하는 것을 막는다.", ["scaling"]),
    U("eda_fe_p21_u02", "comparison", "text", "KNN, SVM, PCA, ANN 등 거리·분산 기반 알고리즘은 scale에 민감; Decision Tree 계열은 영향이 작음", "KNN·SVM·PCA·신경망은 스케일에 민감하고 트리 계열은 상대적으로 덜 민감하다.", ["scaling"]),
], source_issues=[{"issue_id": "eda_fe_p21_i01", "source_text": "로지스틱 회귀에서는 성능의 변화 없음", "issue_type": "overgeneralized", "correction": "규제, 최적화, 수치 안정성에 따라 로지스틱 회귀도 스케일링의 영향을 받을 수 있다.", "evaluation_policy": "exclude"}])
page(22, ["scaling", "standard_scaler", "minmax_scaler", "robust_scaler", "iqr"], [
    U("eda_fe_p22_u01", "comparison", "text", "Standard: 평균·표준편차 / Min-Max: 최소·최대로 [0,1] / Robust: 중앙값·IQR", "Standard는 평균·표준편차, Min-Max는 최소·최대, Robust는 중앙값·IQR로 변환한다.", ["standard_scaler", "minmax_scaler", "robust_scaler", "iqr"]),
    U("eda_fe_p22_u02", "procedure", "text", "이상치가 없으면 Standard, 특정 범위가 필요하면 Min-Max, 이상치가 많으면 Robust", "분포, 이상치, 필요 값 범위를 고려해 스케일러를 선택한다. Min-Max는 최소·최대를 쓰므로 일반적으로 이상치에 민감하다.", ["standard_scaler", "minmax_scaler", "robust_scaler"]),
], source_issues=[{"issue_id": "eda_fe_p22_i01", "source_text": "Min-Max Scaling: 이상치에 강건", "issue_type": "incorrect", "correction": "Min-Max Scaling은 최솟값과 최댓값을 사용하므로 일반적으로 이상치에 민감하다.", "evaluation_policy": "exclude"}])
page(23, ["merge", "groupby"], [
    U("eda_fe_p23_u01", "comparison", "text", "pd.merge: 공통 key와 Inner/Outer/Left/Right로 데이터프레임 병합 / pd.groupby: 특정 열로 묶어 평균·합계·개수 집계", "merge는 키를 기준으로 표를 결합하고 groupby는 그룹별 통계를 집계한다.", ["merge", "groupby"]),
])
page(25, ["feature_engineering", "feature_selection", "feature_extraction", "pca", "lda"], [
    U("eda_fe_p25_u01", "comparison", "text", "FE는 Feature Selection + Feature Extraction; PCA는 레이블 없이 분산이 최대인 축, LDA는 클래스 구분력이 최대인 축", "특성 선택은 원변수를 고르고 특성 추출은 새 표현을 만든다. PCA는 비지도 분산, LDA는 지도 클래스 분리를 기준으로 한다.", ["feature_engineering", "feature_selection", "feature_extraction", "pca", "lda"]),
])
page(26, ["feature_engineering"], [
    U("eda_fe_p26_u01", "procedure", "text", "FE는 ‘특징 생성 → 성능 확인 → 개선’을 반복하는 과정", "특성공학은 특성을 설계하고 검증 성능을 확인한 뒤 개선하는 반복 과정이다.", ["feature_engineering"]),
])
page(27, ["curse_dimensionality", "dimensionality_reduction", "feature_selection", "feature_extraction", "multicollinearity"], [
    U("eda_fe_p27_u01", "relation", "text", "데이터보다 입력변수가 많아 모델이 복잡하면 학습 지연·과적합·다중공선성; 특성 선택·추출로 차원 축소", "차원에 비해 표본이 부족하면 복잡도·과적합·불안정성이 커지므로 선택·추출로 차원을 줄인다.", ["curse_dimensionality", "dimensionality_reduction", "feature_selection", "feature_extraction", "multicollinearity"]),
])
page(28, ["feature_selection", "filter_method", "wrapper_method", "rfe"], [
    U("eda_fe_p28_u01", "comparison", "text", "Filter는 상관계수·카이제곱 등으로 빠르지만 상호작용을 못 보고, Wrapper는 RFE 등 모델 반복 학습으로 상호작용을 보지만 계산 비용이 큼", "Filter는 빠른 단변량 기준, Wrapper는 비용이 큰 모델 성능 기준이므로 상호작용 반영과 계산량을 비교한다.", ["feature_selection", "filter_method", "wrapper_method", "rfe"]),
])
page(29, ["feature_selection", "embedded_method", "lasso"], [
    U("eda_fe_p29_u01", "comparison", "text", "Embedded는 모델 학습에 변수 선택이 내장; Lasso는 L1 penalty로 계수를 0, Random Forest·XGBoost는 분기 기여도; 결과는 모델에 의존", "Embedded는 학습과 선택을 같이 하여 효율적이지만 선택 결과가 모델에 의존한다.", ["feature_selection", "embedded_method", "lasso"]),
])
page(30, ["derived_feature", "lag", "moving_average"], [
    U("eda_fe_p30_u01", "example", "text", "나이·시간 범주화, 이름·날짜 분리, lag·이동평균·요일·주말 여부 생성", "범주화·열 분리·시계열 요약으로 원자료의 경향과 도메인 정보를 파생변수로 표현한다.", ["derived_feature", "lag", "moving_average"]),
])
page(31, ["data_leakage", "target_encoding", "lag", "moving_average"], [
    U("eda_fe_p31_u01", "definition", "text", "실제 예측 시점에 알 수 없는 test·미래 정보가 학습에 새어 들어가 검증 성능이 부풀려지는 현상", "데이터 누수는 배포 시점에 사용할 수 없는 정답·미래·테스트 정보가 학습에 들어가 평가를 과대하는 현상이다.", ["data_leakage"]),
    U("eda_fe_p31_u02", "warning", "text", "Target Encoding은 자기 fold를 제외하고 평균 계산; Lag/Rolling은 현재 시점 이전 데이터만 사용", "타깃 인코딩은 out-of-fold로, 시계열 특성은 과거 데이터로만 계산해 누수를 막는다.", ["data_leakage", "target_encoding", "lag", "moving_average"]),
])
page(32, ["pca", "feature_extraction", "dimensionality_reduction"], [
    U("eda_fe_p32_u01", "procedure", "text_and_visual", "PCA는 상관관계를 반영해 분산을 가장 잘 설명하는 직교 축을 순서대로 생성; 누적 설명력 80~95% 참고", "PCA는 원변수의 상관 구조를 선형결합한 직교 주성분으로 요약하고 누적 설명분산을 보고 개수를 정한다.", ["pca", "feature_extraction", "dimensionality_reduction"]),
    U("eda_fe_p32_u02", "warning", "text", "PC1, PC2는 원래 변수의 선형결합이어서 의미 해석이 어려움; 원본 변수를 유지하지 않음", "PCA는 차원을 줄이지만 원변수를 유지하지 않고 주성분 해석이 어려워 해석성이 중요한 도메인에서 신중해야 한다.", ["pca", "feature_extraction"]),
])
page(39, ["data_leakage", "label_encoding", "one_hot_encoding", "derived_feature", "scaling"], [
    U("eda_fe_p39_u01", "example", "text", "이탈 정의에 직접 쓴 ‘마지막 구매 후 경과일’을 제거하지 않으면 Target Leakage", "타깃을 정의한 정보를 특성으로 그대로 주면 정답 누수가 발생한다.", ["data_leakage"]),
])
page(40, ["train_test_contamination", "data_leakage"], [
    U("eda_fe_p40_u01", "example", "text_and_visual", "A의 test set 데이터가 B의 train set에 들어갈 수 있어 A test로 두 모델을 비교한 결과를 신뢰할 수 없음", "공통 테스트 샘플이 비교 대상 모델의 훈련에 포함되면 훈련-테스트 오염으로 성능 비교가 무효해진다.", ["train_test_contamination", "data_leakage"]),
])
page(41, ["class_imbalance", "accuracy", "precision", "recall", "f1"], [
    U("eda_fe_p41_u01", "example", "text", "이탈 5%인 불균형에서 모두 비이탈로 예측해도 95%; 88% accuracy만으로 신뢰 불가, Recall·Precision·F1 필요", "다수 클래스 비율보다 낮은 정확도도 나올 수 있으므로 정밀도·재현율·F1으로 소수 클래스 성능을 확인한다.", ["class_imbalance", "accuracy", "precision", "recall", "f1"]),
])


CONTENT_OVERRIDES = {
    15: "이상치가 오류인지 의미 있는 신호인지 판단한다. 이상치 제거는 훈련 데이터에만 적용하고 검증·테스트 관측치를 성능 평가 전에 제거하지 않는다.",
    21: "특성 범위를 통일하면 큰 단위가 거리·분산 계산을 지배하는 것을 막는다. KNN·SVM·PCA·신경망은 스케일에 민감하고 트리 계열은 상대적으로 덜 민감하다. 로지스틱 회귀가 항상 영향을 받지 않는다는 원문의 절대적 표현은 평가 근거에서 제외한다.",
    22: "Standard Scaling은 평균·표준편차, Min-Max Scaling은 최소·최대, Robust Scaling은 중앙값·IQR를 사용한다. Min-Max는 일반적으로 이상치에 민감하므로 원문의 ‘이상치에 강건’ 표현은 평가 근거에서 제외한다.",
    26: "특성공학은 특성을 생성하고 성능을 확인한 뒤 개선하는 과정을 반복한다.",
}


CLAIM_LINKS = {
    "eda.role_separation": (["eda_fe_p5_u01"], ["eda", "preprocessing", "feature_engineering"]),
    "eda.gigo": (["eda_fe_p4_u01"], ["eda", "preprocessing", "feature_engineering"]),
    "eda.analysis_flow": (["eda_fe_p6_u01"], ["eda", "preprocessing", "feature_engineering"]),
    "eda.check_sequence": (["eda_fe_p8_u01"], ["eda", "data_type", "missing_value", "outlier", "class_imbalance", "multicollinearity"]),
    "eda.structure_domain": (["eda_fe_p10_u01"], ["eda", "data_type"]),
    "eda.dtype": (["eda_fe_p12_u01"], ["data_type"]),
    "eda.label_for_order": (["eda_fe_p11_u01"], ["label_encoding"]),
    "eda.onehot_for_nominal": (["eda_fe_p11_u01"], ["one_hot_encoding"]),
    "eda.dummy_baseline": (["eda_fe_p11_u02"], ["dummy_encoding", "one_hot_encoding", "multicollinearity"]),
    "eda.missing_strategy": (["eda_fe_p13_u01"], ["missing_value", "imputation"]),
    "eda.missing_cause": (["eda_fe_p13_u01"], ["missing_value", "imputation"]),
    "eda.outlier_detection": (["eda_fe_p14_u01"], ["outlier", "standard_deviation_rule", "iqr"]),
    "eda.outlier_judgment": (["eda_fe_p14_u02"], ["outlier"]),
    "eda.train_only_rule": (["eda_fe_p15_u01"], ["outlier"]),
    "eda.accuracy_problem": (["eda_fe_p16_u01", "eda_fe_p41_u01"], ["class_imbalance", "accuracy"]),
    "eda.imbalance_metrics": (["eda_fe_p16_u02", "eda_fe_p41_u01"], ["class_imbalance", "precision", "recall", "f1", "pr_auc"]),
    "eda.sampling_tradeoff": (["eda_fe_p17_u01"], ["class_imbalance", "undersampling", "oversampling", "smote"]),
    "eda.loss_finetuning": (["eda_fe_p18_u01"], ["class_imbalance", "focal_loss"]),
    "eda.distribution_relation": (["eda_fe_p19_u01"], ["multicollinearity"]),
    "eda.multicollinearity": (["eda_fe_p20_u01", "eda_fe_p20_u02"], ["multicollinearity", "vif", "pca", "lasso"]),
    "eda.scaling_reason": (["eda_fe_p21_u01"], ["scaling"]),
    "eda.algorithm_sensitivity": (["eda_fe_p21_u02"], ["scaling"]),
    "eda.scaler_formulas": (["eda_fe_p22_u01"], ["standard_scaler", "minmax_scaler", "robust_scaler", "iqr"]),
    "eda.scaler_choice": (["eda_fe_p22_u02"], ["standard_scaler", "minmax_scaler", "robust_scaler"]),
    "eda.merge_groupby": (["eda_fe_p23_u01"], ["merge", "groupby"]),
    "eda.operation_choice": (["eda_fe_p23_u01"], ["merge", "groupby"]),
    "eda.selection_extraction": (["eda_fe_p25_u01"], ["feature_selection", "feature_extraction", "pca", "lda"]),
    "eda.curse": (["eda_fe_p27_u01"], ["curse_dimensionality", "dimensionality_reduction", "feature_selection", "feature_extraction"]),
    "eda.pca_tradeoff": (["eda_fe_p32_u01", "eda_fe_p32_u02"], ["pca", "feature_extraction", "dimensionality_reduction"]),
    "eda.filter": (["eda_fe_p28_u01"], ["feature_selection", "filter_method"]),
    "eda.wrapper": (["eda_fe_p28_u01"], ["feature_selection", "wrapper_method", "rfe"]),
    "eda.embedded": (["eda_fe_p29_u01"], ["feature_selection", "embedded_method", "lasso"]),
    "eda.derived_features": (["eda_fe_p30_u01"], ["derived_feature", "lag", "moving_average"]),
    "eda.iterative_fe": (["eda_fe_p26_u01"], ["feature_engineering"]),
    "eda.domain_validation": (["eda_fe_p26_u01", "eda_fe_p30_u01"], ["feature_engineering", "derived_feature"]),
    "eda.leakage_definition": (["eda_fe_p31_u01", "eda_fe_p39_u01", "eda_fe_p40_u01"], ["data_leakage", "train_test_contamination"]),
    "eda.target_encoding": (["eda_fe_p31_u02"], ["data_leakage", "target_encoding"]),
    "eda.time_features": (["eda_fe_p31_u02"], ["data_leakage", "lag", "moving_average"]),
}


REQUIRED_ELEMENTS = {
    "eda.role_separation": ["EDA는 탐색과 방향 설정", "전처리는 결측·이상·스케일·범주 정제", "FE는 특성 생성·제거·변형"],
    "eda.gigo": ["입력 데이터 품질이 모델 결과의 기반이라는 인과관계"],
    "eda.analysis_flow": ["문제·목표 정의와 데이터 수집", "EDA·전처리·FE 후 모델링과 결론으로 이어지는 흐름"],
    "eda.check_sequence": ["구조·타입", "결측치·이상치", "타깃 분포와 변수 관계 점검"],
    "eda.structure_domain": ["행·열, 변수명, 샘플 값 확인", "용어집·도메인 자료로 열 의미 파악"],
    "eda.dtype": ["숫자·범주·날짜라는 의미상 타입", "int·float·object 등 실제 dtype 확인과 필요 시 변환"],
    "eda.label_for_order": ["순서가 있는 범주에 라벨·순서형 인코딩을 고려", "명목형에 쓰면 거짓 순서를 줄 수 있는 한계"],
    "eda.onehot_for_nominal": ["순서 없는 범주를 각각 0·1 열로 표현", "범주가 많으면 차원이 커지는 한계"],
    "eda.dummy_baseline": ["원핫 열 하나를 제거", "완전 다중공선성을 줄이지만 기준 범주가 생김"],
    "eda.missing_strategy": ["평균·중앙값·최빈값 대체 선택지", "도메인·원인·결측 지표·관련 변수·열 삭제를 함께 고려"],
    "eda.missing_cause": ["단순 대체 전 결측 원인과 도메인 의미를 확인", "결측 자체가 정보일 수 있음"],
    "eda.outlier_detection": ["3시그마는 정규분포에 가까울 경우", "IQR 경계 또는 클러스터링·오토인코더 등 대안"],
    "eda.outlier_judgment": ["이상치가 오류인지 의미 있는 신호인지 판단", "제거·변환·대체·유지 선택"],
    "eda.train_only_rule": ["이상치 제거는 훈련 데이터에 적용", "검증·테스트 관측치를 성능 평가 전에 제거하지 않음"],
    "eda.accuracy_problem": ["다수 클래스만 예측해도 정확도가 높을 수 있음", "불균형에서 정확도만으로 모델을 평가하면 안 됨"],
    "eda.imbalance_metrics": ["정밀도·재현율·F1·PR AUC 등 소수 클래스 성능 지표", "문제의 오류 비용에 맞는 지표 선택"],
    "eda.sampling_tradeoff": ["언더샘플링의 정보 손실·과소적합 위험", "오버샘플링의 왜곡·과적합 위험"],
    "eda.loss_finetuning": ["Focal Loss로 어려운·소수 예제에 더 큰 손실 가중치", "전체 학습 후 소수 클래스 중심 추가 학습"],
    "eda.distribution_relation": ["변수 분포와 변수 간 상관 탐색", "타깃과의 관계로 중요 특성과 다중공선성 후보 파악"],
    "eda.multicollinearity": ["설명변수 간 강한 상관으로 계수·중요도 해석이 불안정", "VIF를 맥락적으로 진단", "제거·결합·규제·PCA 등 대응"],
    "eda.scaling_reason": ["단위·범위가 큰 특성이 거리·분산 계산을 지배하는 문제", "특성 범위를 맞추는 목적"],
    "eda.algorithm_sensitivity": ["KNN·SVM·PCA·신경망의 스케일 민감성", "트리 계열은 상대적으로 덜 민감함"],
    "eda.scaler_formulas": ["Standard는 평균·표준편차", "Min-Max는 최소·최대", "Robust는 중앙값·IQR"],
    "eda.scaler_choice": ["이상치·필요 범위·분포에 따른 선택", "Min-Max는 일반적으로 이상치에 민감하고 Robust는 상대적으로 강건함"],
    "eda.merge_groupby": ["merge는 공통 key와 조인 방식으로 표 병합", "groupby는 특정 열로 묶어 통계량 집계"],
    "eda.operation_choice": ["표 결합에는 merge", "그룹별 통계에는 groupby"],
    "eda.selection_extraction": ["특성 선택은 원변수를 고름", "특성 추출은 기존 변수를 결합한 새 표현", "PCA는 비지도 분산, LDA는 지도 클래스 구분 기준"],
    "eda.curse": ["특성에 비해 표본이 부족할 때 학습 지연·과적합·불안정성", "선택·추출로 차원 축소"],
    "eda.pca_tradeoff": ["상관 구조를 반영한 직교 주성분으로 차원 축소", "누적 설명분산 기준", "선형결합이어서 원변수를 유지하지 않고 해석성이 떨어짐"],
    "eda.filter": ["모델 없이 상관계수·카이제곱 등 통계량으로 빠르게 선택", "변수 간 상호작용을 놓칠 수 있음"],
    "eda.wrapper": ["RFE 등으로 모델을 반복 학습해 변수 조합 비교", "상호작용을 반영하지만 계산 비용이 큼"],
    "eda.embedded": ["모델 학습 과정 안에 변수 선택이 내장", "Lasso L1 또는 트리 중요도 예", "결과가 모델에 의존"],
    "eda.derived_features": ["범주화·열 분리·lag·이동평균·요일 등 파생변수 예", "원자료의 경향과 정보를 명확히 하는 목적"],
    "eda.iterative_fe": ["특성 생성", "검증 성능 확인", "결과에 따른 개선의 반복"],
    "eda.domain_validation": ["파생변수가 원자료의 경향을 더 뚜렷하게 표현하는지 확인", "생성 후 성능을 확인하고 반복 개선"],
    "eda.leakage_definition": ["실제 예측 시점에 알 수 없는 타깃·미래·테스트 정보가 학습에 포함", "검증 성능이 실제보다 부풀려짐", "타깃 직결 특성·훈련-테스트 오염 예"],
    "eda.target_encoding": ["행 자신의 타깃이 범주 평균에 포함되면 누수", "자기 fold를 제외한 out-of-fold 타깃 인코딩"],
    "eda.time_features": ["lag·rolling 계산에 현재 이후 미래 데이터를 포함하지 않음", "현재 시점 이전 데이터만 사용"],
}


CRITICAL_ERRORS = {
    "eda.role_separation": ["EDA·전처리·FE의 역할을 서로 뒤바꿔 설명"],
    "eda.label_for_order": ["명목형 범주에 라벨 숫자를 주어도 모델이 순서로 절대 해석하지 않는다고 단정"],
    "eda.onehot_for_nominal": ["원핫 인코딩이 범주 간 순서 관계를 임의로 부여한다고 설명"],
    "eda.missing_strategy": ["모든 결측치는 원인과 분포를 보지 않고 평균으로 대체하면 된다고 설명"],
    "eda.outlier_judgment": ["탐지된 이상치는 항상 오류이므로 무조건 삭제해야 한다고 설명"],
    "eda.train_only_rule": ["성능을 높이기 위해 검증·테스트의 불편한 관측치도 평가 전에 제거해도 된다고 설명"],
    "eda.accuracy_problem": ["심한 클래스 불균형에서 정확도 하나만으로 소수 클래스 탐지력을 판단해도 된다고 설명"],
    "eda.sampling_tradeoff": ["언더·오버샘플링은 정보 손실·왜곡·과적합 위험이 전혀 없다고 설명"],
    "eda.multicollinearity": ["VIF 10을 모든 도메인의 절대적 자동 삭제 기준으로 설명"],
    "eda.algorithm_sensitivity": ["트리 계열이 거리 기반 알고리즘이어서 스케일에 매우 민감하다고 설명"],
    "eda.scaler_formulas": ["Standard·Min-Max·Robust의 기준 통계량을 서로 뒤바꿔 설명"],
    "eda.scaler_choice": ["Min-Max Scaling이 최솟값·최댓값을 사용하지만 이상치에 강건하다고 설명"],
    "eda.selection_extraction": ["특성 선택과 특성 추출의 정의를 서로 뒤바꿔 설명"],
    "eda.filter": ["Filter 방식이 반드시 모델을 반복 학습해야 한다고 설명"],
    "eda.wrapper": ["Wrapper가 모델을 학습하지 않고 통계량만으로 선택한다고 설명"],
    "eda.pca_tradeoff": ["PCA가 원본 변수를 그대로 선택하므로 해석성이 항상 유지된다고 설명"],
    "eda.leakage_definition": ["미래·테스트·타깃 정보가 학습에 들어가도 검증 성능의 신뢰성에 영향이 없다고 설명"],
    "eda.target_encoding": ["타깃 인코딩에 행 자신의 정답을 포함해도 누수가 아니라고 설명"],
    "eda.time_features": ["예측 시점 이후의 미래 값을 rolling·lag 특성에 포함해도 된다고 설명"],
}


def apply_evaluation_data(processed_path: Path = PROCESSED_PATH,
                          rubric_path: Path = RUBRIC_PATH) -> None:
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id") != "eda_fe":
        raise ValueError("EDA·FE processed 파일이 아닙니다.")
    pages = {chunk["page"]: chunk for chunk in payload["chunks"]}
    if set(pages) != set(PAGE_DATA):
        raise ValueError("EDA·FE PDF의 1~42쪽이 모두 존재해야 합니다.")
    payload["schema_version"] = "2.1.0"
    payload["terminology"] = TERMINOLOGY
    for page_number, metadata in PAGE_DATA.items():
        pages[page_number].update(metadata)
        pages[page_number].setdefault("source_issues", [])
        if page_number in CONTENT_OVERRIDES:
            pages[page_number]["content"] = CONTENT_OVERRIDES[page_number]
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    unit_lookup = {u["unit_id"]: (chunk, u) for chunk in payload["chunks"] for u in chunk["evidence_units"]}
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    rubric["schema_version"] = "2.2.0"
    claims = {claim["claim_id"]: claim for obj in rubric["top_level_objectives"]
              for sub in obj["sub_objectives"] for claim in sub["claims"]}
    if set(claims) != set(CLAIM_LINKS) or set(claims) != set(REQUIRED_ELEMENTS):
        raise ValueError("EDA·FE claim·evidence·판정 기준 목록이 일치하지 않습니다.")
    for claim_id, (unit_ids, term_ids) in CLAIM_LINKS.items():
        claim = claims[claim_id]
        claim["term_ids"] = term_ids
        claim["evaluation_criteria"] = {"required_elements": REQUIRED_ELEMENTS[claim_id],
                                        "critical_errors": CRITICAL_ERRORS.get(claim_id, [])}
        claim["evidence"] = []
        for unit_id in unit_ids:
            chunk, source = unit_lookup[unit_id]
            claim["evidence"].append({"page": chunk["page"], "chunk_id": chunk["chunk_id"],
                                      "unit_id": unit_id, "source_excerpt": source["source_excerpt"],
                                      "source_status": source["source_status"], "review_note": ""})
    claims["eda.train_only_rule"]["text"] = "이상치 제거는 훈련 데이터에만 적용하고 검증·테스트 관측치를 평가 전에 제거하지 않는다."
    claims["eda.scaler_choice"]["text"] = "분포·이상치·필요 값 범위를 고려해 Standard·Min-Max·Robust Scaling을 선택하며, Min-Max는 일반적으로 이상치에 민감하다."
    claims["eda.domain_validation"]["text"] = "파생변수가 원자료의 경향을 더 뚜렷하게 표현하는지와 성능을 확인하며 반복적으로 개선한다."
    rubric["excluded_source_claims"] = [
        {"page": chunk["page"], "chunk_id": chunk["chunk_id"],
         "source_text": issue["source_text"], "reason": issue["correction"]}
        for chunk in payload["chunks"] for issue in chunk.get("source_issues", [])
        if issue.get("evaluation_policy") == "exclude"
    ]
    rubric_path.write_text(json.dumps(rubric, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    apply_evaluation_data()
    print(f"updated: {PROCESSED_PATH.relative_to(ROOT)}")
    print(f"updated: {RUBRIC_PATH.relative_to(ROOT)}")
