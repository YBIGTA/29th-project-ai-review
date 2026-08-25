from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "basic_statistics.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "basic_statistics.json"


def term(
    term_id: str,
    ko: str,
    en: str = "",
    *,
    abbreviations: list[str] | None = None,
    aliases: list[str] | None = None,
    symbols: list[str] | None = None,
    not_equivalent_to: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "term_id": term_id,
        "canonical_ko": ko,
        "canonical_en": en,
        "abbreviations": abbreviations or [],
        "accepted_aliases": aliases or [],
        "symbols": symbols or [],
        "not_equivalent_to": not_equivalent_to or [],
    }


TERMINOLOGY = [
    term("random_variable", "확률변수", "random variable", symbols=["X"]),
    term("sample_space", "표본공간", "sample space", symbols=["Ω"]),
    term("expected_value", "기댓값", "expected value", aliases=["기대값", "평균"], symbols=["E(X)"]),
    term("variance", "분산", "variance", symbols=["Var(X)", "σ²"], not_equivalent_to=["variable"]),
    term("variable", "변수", "variable", not_equivalent_to=["variance"]),
    term("standard_deviation", "표준편차", "standard deviation", abbreviations=["SD"], symbols=["σ"]),
    term("population", "모집단", "population"),
    term("sample", "표본", "sample"),
    term("sampling", "표본추출", "sampling"),
    term("cluster_sampling", "군집표본추출", "cluster sampling", aliases=["군집표본"]),
    term("stratified_sampling", "층화표본추출", "stratified sampling", aliases=["층화표본"]),
    term("simple_random_sampling", "단순무작위표본추출", "simple random sampling", abbreviations=["SRS"], aliases=["단순무작위표본"]),
    term("covariance", "공분산", "covariance", abbreviations=["Cov"], symbols=["Cov(X,Y)"]),
    term("correlation", "상관계수", "correlation coefficient", aliases=["상관관계", "피어슨 상관계수"], symbols=["ρ", "r"], not_equivalent_to=["causation"]),
    term("causation", "인과관계", "causation", aliases=["인과성"], not_equivalent_to=["correlation"]),
    term("independence", "독립성", "independence", aliases=["통계적 독립"], not_equivalent_to=["zero_covariance"]),
    term("zero_covariance", "공분산이 0", "zero covariance", aliases=["무상관"], not_equivalent_to=["independence"]),
    term("conditional_probability", "조건부확률", "conditional probability", symbols=["P(A|B)"]),
    term("bayes_theorem", "베이즈 정리", "Bayes' theorem", aliases=["베이즈 규칙"]),
    term("iterated_expectation", "전체기댓값법칙", "law of iterated expectations", aliases=["반복기댓값법칙", "tower property"], symbols=["E(X)=E(E(X|Y))"]),
    term("hypothesis_testing", "가설검정", "hypothesis testing"),
    term("null_hypothesis", "귀무가설", "null hypothesis", abbreviations=["H0", "H₀"]),
    term("alternative_hypothesis", "대립가설", "alternative hypothesis", abbreviations=["H1", "H₁"]),
    term("significance_level", "유의수준", "significance level", symbols=["α"]),
    term("test_statistic", "검정통계량", "test statistic"),
    term("p_value", "p-value", "p-value", aliases=["p값", "유의확률"], symbols=["p"], not_equivalent_to=["null_probability"]),
    term("null_probability", "귀무가설이 참일 확률", "probability that the null is true", symbols=["P(H0|data)"], not_equivalent_to=["p_value"]),
    term("type_i_error", "1종 오류", "type I error", aliases=["제1종 오류", "false positive"], symbols=["α"]),
    term("type_ii_error", "2종 오류", "type II error", aliases=["제2종 오류", "false negative"], symbols=["β"]),
    term("statistical_power", "검정력", "statistical power", aliases=["power"], symbols=["1-β"]),
    term("standard_error", "표준오차", "standard error", abbreviations=["SE", "S.E."]),
    term("confidence_interval", "신뢰구간", "confidence interval", abbreviations=["CI"], not_equivalent_to=["fixed_interval_probability"]),
    term("confidence_level", "신뢰수준", "confidence level"),
    term("fixed_interval_probability", "계산된 구간에 모수가 있을 확률", "probability that a fixed interval contains the parameter", not_equivalent_to=["confidence_interval"]),
    term("anova", "분산분석", "analysis of variance", abbreviations=["ANOVA"]),
    term("between_group_variation", "집단 간 변동", "between-group variation", abbreviations=["SSB", "MSB"]),
    term("within_group_variation", "집단 내 변동", "within-group variation", abbreviations=["SSW", "MSW"]),
    term("f_statistic", "F 통계량", "F statistic", aliases=["F 검정통계량"], symbols=["F=MSB/MSW"]),
    term("normality", "정규성", "normality"),
    term("homoscedasticity", "등분산성", "homoscedasticity", aliases=["분산의 동질성"]),
    term("shapiro_wilk", "Shapiro-Wilk 검정", "Shapiro-Wilk test", aliases=["샤피로-윌크 검정"]),
    term("qq_plot", "Q-Q plot", "quantile-quantile plot", aliases=["Q-Q 도표", "분위수-분위수 도표"]),
    term("durbin_watson", "Durbin-Watson 검정", "Durbin-Watson test", abbreviations=["DW"], aliases=["더빈-왓슨 검정"]),
    term("levene", "Levene 검정", "Levene's test", aliases=["레빈 검정"]),
    term("bartlett", "Bartlett 검정", "Bartlett's test", aliases=["바틀렛 검정"]),
    term("kruskal_wallis", "Kruskal-Wallis 검정", "Kruskal-Wallis test", aliases=["크루스칼-왈리스 검정"]),
    term("welch_anova", "Welch ANOVA", "Welch's ANOVA", aliases=["웰치 분산분석", "웰치 ANOVA"]),
    term("one_way_anova", "일원분산분석", "one-way ANOVA", aliases=["일원 ANOVA"]),
    term("two_way_anova", "이원분산분석", "two-way ANOVA", aliases=["이원 ANOVA"]),
    term("interaction", "교호작용", "interaction", aliases=["상호작용", "interaction term"]),
    term("tukey_hsd", "Tukey HSD", "Tukey honestly significant difference", aliases=["튜키 사후검정", "튜키 HSD"]),
    term("regression", "회귀분석", "regression analysis"),
    term("linear_regression", "선형회귀", "linear regression"),
    term("ols", "최소제곱법", "ordinary least squares", abbreviations=["OLS"], aliases=["최소자승법"]),
    term("residual", "잔차", "residual", symbols=["e", "ε"]),
    term("exogeneity", "외생성", "exogeneity"),
    term("r_squared", "결정계수", "coefficient of determination", abbreviations=["R-squared"], symbols=["R²"]),
    term("adjusted_r_squared", "조정 결정계수", "adjusted R-squared", aliases=["수정 결정계수"], symbols=["adjusted R²"]),
    term("multicollinearity", "다중공선성", "multicollinearity"),
    term("vif", "분산팽창계수", "variance inflation factor", abbreviations=["VIF"]),
    term("pca", "주성분분석", "principal component analysis", abbreviations=["PCA"]),
    term("ridge", "릿지 회귀", "ridge regression", aliases=["Ridge"]),
    term("omitted_variable_bias", "누락변수편향", "omitted variable bias", abbreviations=["OVB"]),
    term("glm", "일반화선형모형", "generalized linear model", abbreviations=["GLM"]),
    term("logistic_regression", "로지스틱 회귀", "logistic regression"),
    term("sigmoid", "시그모이드 함수", "sigmoid function", aliases=["로지스틱 함수"]),
    term("odds", "오즈", "odds", aliases=["승산"]),
    term("log_odds", "로그 오즈", "log-odds", aliases=["로짓", "logit"]),
    term("maximum_likelihood", "최대우도추정", "maximum likelihood estimation", abbreviations=["MLE"], aliases=["최대가능도추정"]),
]


def unit(
    unit_id: str,
    kind: str,
    source_type: str,
    source_excerpt: str,
    normalized_explanation: str,
    term_ids: list[str],
    source_status: str = "verified",
) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "type": kind,
        "source_type": source_type,
        "source_excerpt": source_excerpt,
        "normalized_explanation": normalized_explanation,
        "source_status": source_status,
        "term_ids": term_ids,
    }


U = unit
PAGE_DATA: dict[int, dict[str, Any]] = {
    1: {"page_role": "cover", "term_ids": [], "evidence_units": []},
    2: {"page_role": "table_of_contents", "term_ids": ["hypothesis_testing", "regression"], "evidence_units": []},
    3: {"page_role": "section_divider", "term_ids": [], "evidence_units": []},
    4: {"page_role": "core_content", "term_ids": ["random_variable", "sample_space", "expected_value", "variance", "standard_deviation"], "evidence_units": [
        U("basic_statistics_p4_u01", "definition", "text_and_visual", "확률변수: 표본공간(발생 가능한 사건의 집합)의 원소를 실수로 대응시키는 함수", "확률변수는 표본공간의 각 결과를 실수에 대응시키는 함수다.", ["random_variable", "sample_space"]),
        U("basic_statistics_p4_u02", "definition", "text_and_formula", "기댓값(Expected Value): 어떤 시행을 무한히 반복했을 때 얻을 수 있는 값들의 평균; E(X)=Σxᵢf(xᵢ) 또는 ∫xf(x)dx", "기댓값은 반복 시행에서 얻는 값의 장기 평균이며, 이산·연속 확률변수에서 값에 확률을 가중해 계산한다.", ["expected_value", "random_variable"]),
        U("basic_statistics_p4_u03", "definition", "text_and_visual", "분산(Variable): 데이터가 평균에서 얼마나 떨어져 있는지를 나타내는 수치; 평균이 같고 SD가 다른 두 분포", "분산은 값들이 평균에서 떨어진 정도, 표준편차는 그 퍼짐의 크기를 나타낸다.", ["variance", "standard_deviation"]),
    ], "source_issues": [{"issue_id": "basic_statistics_p4_i01", "source_text": "분산 (Variable)", "issue_type": "typo", "correction": "분산의 영어 용어는 Variance이며 Variable은 변수다.", "evaluation_policy": "warn"}]},
    5: {"page_role": "core_content", "term_ids": ["population", "sample", "sampling", "cluster_sampling", "stratified_sampling", "simple_random_sampling"], "evidence_units": [
        U("basic_statistics_p5_u01", "relation", "text_and_visual", "표본추출을 통해 모집단을 ‘추정’한다.", "모집단 전체를 직접 조사하는 대신 표본을 추출해 모집단의 특성을 추정한다.", ["population", "sample", "sampling"]),
        U("basic_statistics_p5_u02", "procedure", "text", "표본분포의 특성에 따라 cluster sampling, stratified sampling, simple random sampling 등의 방법을 선택한다.", "자료와 표본의 특성을 고려해 군집·층화·단순무작위 표본추출 등을 선택하고, 일부로 전체를 평가하는 타당성을 검토한다.", ["sampling", "cluster_sampling", "stratified_sampling", "simple_random_sampling"]),
    ]},
    6: {"page_role": "core_content", "term_ids": ["covariance", "correlation", "causation", "independence", "zero_covariance"], "evidence_units": [
        U("basic_statistics_p6_u01", "formula", "text_and_visual", "Cov(x,y)=E(xy)-E(x)E(y); 양의 관계·음의 관계·관계 없음 산점도", "공분산은 두 변수가 함께 변하는 방향을 나타낸다.", ["covariance"]),
        U("basic_statistics_p6_u02", "formula", "formula", "ρ=Cov(X,Y)/√(Var(X)Var(Y)), -1≤ρ≤1", "상관계수는 공분산을 두 변수의 표준편차로 표준화하며 -1과 1 사이에서 관계의 방향과 강도를 나타낸다.", ["covariance", "correlation", "variance"]),
        U("basic_statistics_p6_u03", "warning", "text", "통계적 상관관계는 인과관계와 다르다.", "상관관계가 관찰되어도 그것만으로 인과관계를 뜻하지 않는다.", ["correlation", "causation"]),
    ], "source_issues": [{"issue_id": "basic_statistics_p6_i01", "source_text": "공분산이 0이면 두 확률변수는 서로 독립이다.", "issue_type": "incorrect", "correction": "공분산 0은 무상관을 뜻하지만 일반적으로 독립을 보장하지 않는다.", "evaluation_policy": "exclude"}]},
    7: {"page_role": "core_content", "term_ids": ["conditional_probability", "bayes_theorem", "iterated_expectation"], "evidence_units": [
        U("basic_statistics_p7_u01", "definition", "text_and_visual", "P(A|B)=P(A∩B)/P(B)", "조건부확률은 사건 B가 주어졌을 때 사건 A가 일어날 확률이다.", ["conditional_probability"]),
        U("basic_statistics_p7_u02", "formula", "text_and_formula", "Bayes Theorem: P(A|B)P(B)=P(B|A)P(A)", "베이즈 정리는 조건부확률의 조건 방향을 바꾸어 미지의 사건을 알려진 사건으로 접근하게 한다.", ["conditional_probability", "bayes_theorem"]),
        U("basic_statistics_p7_u03", "formula", "text_and_formula", "E(X)=E(E(X|Y))", "전체기댓값법칙은 Y가 주어졌을 때의 X의 조건부 기댓값을 Y에 대해 다시 평균낸다.", ["iterated_expectation", "conditional_probability", "expected_value"]),
    ]},
    8: {"page_role": "section_divider", "term_ids": ["hypothesis_testing"], "evidence_units": []},
    9: {"page_role": "core_content", "term_ids": ["hypothesis_testing", "null_hypothesis", "alternative_hypothesis", "significance_level", "test_statistic", "p_value"], "evidence_units": [
        U("basic_statistics_p9_u01", "procedure", "text", "Step1. 귀무·대립가설 세우기; Step2. 유의수준 선택; Step3. 검정통계량 계산; Step4. p-value 계산; Step5. 귀무가설에 대한 판단", "가설검정은 가설 설정, 유의수준 선택, 검정통계량과 p-value 계산, 귀무가설 판단 순서로 진행한다.", ["hypothesis_testing", "null_hypothesis", "alternative_hypothesis", "significance_level", "test_statistic", "p_value"]),
        U("basic_statistics_p9_u02", "procedure", "visual", "자료 유형과 정규성에 따른 Hypothesis Testing 선택 트리", "자료의 연속형·범주형 여부, 정규성 등 자료 특성과 가정에 따라 검정법을 선택한다.", ["hypothesis_testing", "normality"]),
    ], "source_issues": [{"issue_id": "basic_statistics_p9_i01", "source_text": "귀무가설에 대한 판단(accept? reject?)", "issue_type": "ambiguous", "correction": "통상 ‘기각’ 또는 ‘기각하지 못함’으로 표현하며, 데이터가 귀무가설을 참으로 확정하지 않는다.", "evaluation_policy": "warn"}]},
    10: {"page_role": "core_content", "term_ids": ["null_hypothesis", "alternative_hypothesis"], "evidence_units": [
        U("basic_statistics_p10_u01", "interpretation", "text", "특정 가설이 참임을 데이터로 직접 입증하는 건 논리적으로 불가능에 가깝다. 귀류법을 사용하여 결론의 모순을 찾는 방식으로 접근한다.", "가설검정은 특정 가설을 직접 증명하기보다 귀무가설 아래에서 관측 결과가 얼마나 모순적인지 살피는 구조다.", ["hypothesis_testing", "null_hypothesis"]),
        U("basic_statistics_p10_u02", "interpretation", "text", "차이 없음(딱 하나의 분포)으로 둠으로써 계산을 용이하게 만드는 것", "귀무가설의 ‘차이 없음’은 계산 가능한 기준 분포를 제공한다.", ["null_hypothesis"]),
    ]},
    11: {"page_role": "core_content", "term_ids": ["type_i_error", "type_ii_error", "statistical_power", "null_hypothesis"], "evidence_units": [
        U("basic_statistics_p11_u01", "definition", "text_and_visual", "1종 오류: 귀무가설이 실제로 참이지만 귀무가설을 기각하는 오류; 실제 음성을 양성으로 판정; α", "1종 오류는 참인 귀무가설을 기각하는 오류이며 false positive와 α에 대응한다.", ["type_i_error", "null_hypothesis"]),
        U("basic_statistics_p11_u02", "definition", "text_and_visual", "2종 오류: 귀무가설이 실제로 거짓이지만 귀무가설을 채택하는 오류; 실제 양성을 음성으로 판정; β", "2종 오류는 거짓인 귀무가설을 기각하지 못하는 오류이며 false negative와 β에 대응한다.", ["type_ii_error", "null_hypothesis"]),
    ], "source_issues": [{"issue_id": "basic_statistics_p11_i01", "source_text": "beta (power..)", "issue_type": "ambiguous", "correction": "β는 2종 오류 확률이고 검정력은 1-β다.", "evaluation_policy": "warn"}]},
    12: {"page_role": "example", "term_ids": ["type_i_error", "type_ii_error"], "evidence_units": [
        U("basic_statistics_p12_u01", "relation", "text_and_visual", "기준을 빡빡하게 잡을수록 1종 오류는 줄지만 2종 오류가 늘어난다; 기준을 느슨하게 잡으면 1종 오류는 늘고 2종 오류는 감소한다.", "같은 판정 문제에서 임계값을 엄격하게 하면 1종 오류가 줄고 2종 오류가 늘 수 있으며, 느슨하게 하면 반대 방향의 trade-off가 생긴다.", ["type_i_error", "type_ii_error"]),
    ]},
    13: {"page_role": "example", "term_ids": ["type_i_error", "type_ii_error", "null_hypothesis", "alternative_hypothesis"], "evidence_units": [
        U("basic_statistics_p13_u01", "relation", "visual", "겹치는 귀무가설·대립가설 분포와 한 판정 경계에서 표시된 Type I error 및 Type II error 영역", "귀무가설과 대립가설 분포가 겹치면 하나의 판정 경계에서 1종 오류와 2종 오류 영역이 함께 생긴다.", ["type_i_error", "type_ii_error", "null_hypothesis", "alternative_hypothesis"]),
    ]},
    14: {"page_role": "core_content", "term_ids": ["p_value", "null_hypothesis", "null_probability"], "evidence_units": [
        U("basic_statistics_p14_u01", "definition", "text_and_visual", "귀무가설이 참이라 가정했을 때, 지금 관측한 데이터(혹은 그보다 더 극단적인 데이터)가 나올 확률", "p-value는 귀무가설이 참이라는 조건 아래 관측 데이터 또는 더 극단적인 데이터가 나올 확률이다.", ["p_value", "null_hypothesis"]),
        U("basic_statistics_p14_u02", "interpretation", "text", "P-value가 작다는 것은 가정과 데이터 사이에 긴장이 크다는 신호일 뿐이다.", "작은 p-value는 귀무가설과 데이터가 잘 맞지 않는다는 신호이지 귀무가설이 거짓일 확률 자체는 아니다.", ["p_value", "null_hypothesis", "null_probability"]),
    ]},
    15: {"page_role": "core_content", "term_ids": ["test_statistic", "standard_error", "p_value", "confidence_interval"], "evidence_units": [
        U("basic_statistics_p15_u01", "relation", "text_and_formula", "검정통계량의 기본형=관측된 차이/그 차이의 불확실성(표준오차); 표본크기가 커지면 표준오차가 작아지고 검정통계량이 커져 p-value가 작아진다.", "표본크기가 커지면 표준오차가 작아져 같은 관측 차이에서도 검정통계량이 커지고 p-value가 작아지기 쉽다.", ["test_statistic", "standard_error", "p_value"]),
        U("basic_statistics_p15_u02", "warning", "text", "가설검정은 만능이 아니다; p-value, 신뢰구간 모두를 다 살펴보아야 한다.", "p-value 하나만으로 결론내리지 말고 신뢰구간과 함께 해석한다.", ["p_value", "confidence_interval"]),
    ]},
    16: {"page_role": "core_content", "term_ids": ["p_value", "null_probability"], "evidence_units": [
        U("basic_statistics_p16_u01", "warning", "text", "P-value: P(데이터|귀무가설); 귀무가설이 참일 확률: P(귀무가설|데이터)", "p-value는 모수에 대한 확률이나 귀무가설에 대한 믿음의 정도가 아니며 P(data|H0)를 P(H0|data)로 뒤집어 해석하면 안 된다.", ["p_value", "null_hypothesis", "null_probability"]),
    ]},
    17: {"page_role": "core_content", "term_ids": ["confidence_interval", "confidence_level", "fixed_interval_probability"], "evidence_units": [
        U("basic_statistics_p17_u01", "definition", "text", "이 구간을 만드는 절차를 무한히 반복했을 때, 그렇게 만들어진 구간들 중 ~~%가 true parameter를 포함한다.", "95% 신뢰구간은 같은 구간 생성 절차를 반복할 때 생성된 구간의 95%가 참 모수를 포함하도록 하는 절차다.", ["confidence_interval", "confidence_level"]),
        U("basic_statistics_p17_u02", "relation", "text", "신뢰구간은 추정의 불확실성을 구간의 폭으로 정량화한다. 신뢰수준을 올리면 임계값이 커져 구간이 넓어진다.", "신뢰수준을 높이면 구간이 넓어져 더 안전하지만 구체성과 정보량은 낮아진다.", ["confidence_interval", "confidence_level"]),
        U("basic_statistics_p17_u03", "warning", "text_and_formula", "V(x1-x2)=V(x1)+V(x2)-2Cov(x1,x2); x1,x2의 신뢰구간을 따로 보면 x1-x2의 신뢰구간과 다른 결과가 나올 수도 있다.", "두 집단 차이는 각 집단의 신뢰구간만 따로 비교하지 말고 차이의 분산과 공분산을 반영해 계산한다.", ["confidence_interval", "variance", "covariance"]),
    ]},
    18: {"page_role": "core_content", "term_ids": ["confidence_interval", "confidence_level", "fixed_interval_probability"], "evidence_units": [
        U("basic_statistics_p18_u01", "warning", "text", "이 신뢰구간에 모수가 있을 확률이 95%다?", "빈도주의 신뢰구간에서 이미 계산된 특정 95% 구간에 모수가 있을 확률이 95%라고 해석하지 않는다.", ["confidence_interval", "fixed_interval_probability"]),
        U("basic_statistics_p18_u02", "interpretation", "text", "신뢰수준을 올리는 것은 더 좋은 게 아니라 더 안전하지만 덜 구체적인 것", "높은 신뢰수준은 더 안전하지만 구간을 넓혀 구체성을 낮추므로 언제나 더 유용한 것은 아니다.", ["confidence_interval", "confidence_level"]),
        U("basic_statistics_p18_u03", "warning", "text", "신뢰수준을 고정하지 않고 폭만 비교하면 의미가 없다.", "신뢰구간 폭은 신뢰수준을 같게 둔 뒤 비교해야 한다.", ["confidence_interval", "confidence_level"]),
    ]},
    19: {"page_role": "core_content", "term_ids": ["anova", "between_group_variation", "within_group_variation"], "evidence_units": [
        U("basic_statistics_p19_u01", "interpretation", "text", "두 개 이상 그룹의 평균 비교를 분산을 통해 분석한다. 데이터 전체의 변동을 그룹 간 변동과 그룹 내 변동으로 쪼개서 비교한다.", "ANOVA는 두 개 이상 집단의 평균 차이를 전체 변동의 집단 간 부분과 집단 내 부분으로 나누어 분석한다.", ["anova", "between_group_variation", "within_group_variation"]),
        U("basic_statistics_p19_u02", "relation", "text", "이 차이가 잡음 대비 충분히 큰가를 보는 것이 중요하다.", "집단 평균 차이가 집단 내 잡음에 비해 충분히 큰지 판단한다.", ["between_group_variation", "within_group_variation"]),
    ]},
    20: {"page_role": "core_content", "term_ids": ["anova", "between_group_variation", "within_group_variation", "f_statistic"], "evidence_units": [
        U("basic_statistics_p20_u01", "procedure", "text_and_formula", "SST=SSB+SSW; MSB=SSB/(k-1), MSW=SSW/(n-k)", "총변동을 SST=SSB+SSW로 분해하고 각 제곱합을 자유도로 나누어 MSB와 MSW를 구한다.", ["anova", "between_group_variation", "within_group_variation"]),
        U("basic_statistics_p20_u02", "interpretation", "text_and_formula", "F=MSB/MSW; F가 크다: 그룹 간 신호가 그룹 내 잡음보다 훨씬 크다.", "F 통계량은 MSB/MSW이며 값이 크면 집단 간 신호가 집단 내 잡음보다 상대적으로 크다.", ["f_statistic", "between_group_variation", "within_group_variation"]),
    ]},
    21: {"page_role": "core_content", "term_ids": ["anova", "independence", "normality", "homoscedasticity", "f_statistic"], "evidence_units": [
        U("basic_statistics_p21_u01", "assumption", "text", "Important Assumptions: 1. 독립성 2. 정규성 3. 등분산성", "ANOVA에서 관측치 독립성, 집단별 정규성, 집단 간 등분산성을 점검한다.", ["anova", "independence", "normality", "homoscedasticity"]),
    ], "source_issues": [{"issue_id": "basic_statistics_p21_i01", "source_text": "정규성이 깨지면 f test 자체가 불가능", "issue_type": "overgeneralized", "correction": "정규성 위반이 F 검정을 항상 불가능하게 만드는 것은 아니며 표본크기·균형성·위반 정도와 대안을 함께 검토해야 한다.", "evaluation_policy": "exclude"}]},
    22: {"page_role": "core_content", "term_ids": ["independence", "durbin_watson"], "evidence_units": [
        U("basic_statistics_p22_u01", "assumption", "text", "독립성은 대부분 검정보다는 연구 설계 단계에서 확보하는 가정", "독립성은 통계 검정보다 데이터 수집과 연구 설계에서 우선 확보한다.", ["independence"]),
        U("basic_statistics_p22_u02", "diagnostic", "text", "시계열처럼 순서가 있는 경우 Durbin-Watson 검정으로 autocorrelation 확인; 일반적인 경우 데이터 수집 과정 자체를 점검", "순서가 있는 자료는 Durbin-Watson으로 자기상관을 확인하고 일반 자료는 수집 과정을 점검한다.", ["independence", "durbin_watson"]),
    ]},
    23: {"page_role": "core_content", "term_ids": ["normality", "shapiro_wilk", "qq_plot"], "evidence_units": [
        U("basic_statistics_p23_u01", "diagnostic", "text", "Shapiro-Wilk test; 표본 크기가 작을 때 많이 쓴다. 아주 크면 작은 이탈에도 유의하고 너무 작아도 검정력이 부족하다.", "Shapiro-Wilk 검정은 정규성을 검정하며 표본이 매우 크거나 매우 작을 때 검정력 해석에 주의한다.", ["normality", "shapiro_wilk"]),
        U("basic_statistics_p23_u02", "diagnostic", "text_and_visual", "Q-Q plot: 데이터 분위수와 이론적 분포 분위수를 짝지은 산점도; 직선에 가까울수록 정규성 가정이 성립", "Q-Q plot의 점들이 기준 직선에 가까운지 보고 정규성을 시각적으로 점검한다.", ["normality", "qq_plot"]),
    ]},
    24: {"page_role": "core_content", "term_ids": ["normality", "kruskal_wallis", "one_way_anova"], "evidence_units": [
        U("basic_statistics_p24_u01", "comparison", "text", "Kruskal-Wallis test: 평균이 아니라 rank 기반으로 비교하는 비모수적 검정법; 원자료를 순위로 변환해 그룹 간 위치를 검정", "정규성 가정이 어렵다면 원자료를 순위로 바꾸어 독립 집단의 위치 차이를 비교하는 Kruskal-Wallis 검정을 one-way ANOVA의 비모수 대안으로 고려한다.", ["normality", "kruskal_wallis", "one_way_anova"]),
    ]},
    25: {"page_role": "supplementary_reference", "term_ids": ["kruskal_wallis"], "evidence_units": [
        U("basic_statistics_p25_u01", "procedure", "visual", "Kruskal-Wallis 참고 인포그래픽: 모든 집단의 관측값을 합쳐 순위를 매기고 동순위에 평균순위를 부여한 뒤 집단별 순위합과 H 통계량을 계산", "Kruskal-Wallis 절차를 설명하는 참고 이미지지만 일부 글자가 훼손되어 있어 평가의 직접 근거로 사용하지 않는다.", ["kruskal_wallis"], "needs_review"),
    ], "source_issues": [{"issue_id": "basic_statistics_p25_i01", "source_text": "Kruskal-Wallis 영문 참고 이미지의 일부 공식·예시 문자가 훼손되어 있음", "issue_type": "ambiguous", "correction": "핵심 평가는 글자가 명확한 24쪽의 순위 기반 비모수 검정 설명을 사용한다.", "evaluation_policy": "exclude"}]},
    26: {"page_role": "core_content", "term_ids": ["homoscedasticity", "levene", "bartlett", "normality"], "evidence_units": [
        U("basic_statistics_p26_u01", "procedure", "text", "Levene's test: 각 관측치를 그룹 평균으로부터의 절댓값 편차로 변환한 뒤 그 편차들에 대해 ANOVA를 돌린다.", "Levene 검정은 각 관측값을 집단 중심으로부터의 절대편차로 바꾸고 그 편차를 비교해 등분산성을 점검한다.", ["homoscedasticity", "levene", "anova"]),
        U("basic_statistics_p26_u02", "comparison", "text", "Bartlett's test는 Levene's test보다 검정력은 높지만 정규성 가정에 훨씬 민감하다. 정규성이 의심스러우면 Levene이 더 안전한 선택", "Bartlett 검정은 정규성 위반에 민감하므로 정규성이 의심스러우면 Levene 검정을 고려한다.", ["homoscedasticity", "bartlett", "levene", "normality"]),
    ]},
    27: {"page_role": "core_content", "term_ids": ["homoscedasticity", "welch_anova", "anova"], "evidence_units": [
        U("basic_statistics_p27_u01", "comparison", "text", "일반 ANOVA는 모든 그룹이 같은 분산을 공유한다고 가정; Welch's ANOVA는 그룹별 분산이 다르다는 걸 인정하고 자유도를 조정", "등분산성이 성립하지 않으면 집단별로 다른 분산을 반영하고 자유도를 조정하는 Welch ANOVA를 고려한다.", ["homoscedasticity", "welch_anova", "anova"]),
    ]},
    28: {"page_role": "core_content", "term_ids": ["one_way_anova", "two_way_anova", "interaction"], "evidence_units": [
        U("basic_statistics_p28_u01", "definition", "text_and_visual", "One-way: 마케팅 채널에 따라 고객의 평균 금액이 다른가? 요인=마케팅 채널 1개", "One-way ANOVA는 한 요인의 여러 수준에서 집단 평균을 비교한다.", ["one_way_anova"]),
        U("basic_statistics_p28_u02", "definition", "text_and_visual", "Two-way: 마케팅 채널×고객 연령대에 따라 평균 금액이 다른가? 각 요인 단독+Interaction Term", "Two-way ANOVA는 두 요인의 주효과와 한 요인의 효과가 다른 요인의 수준에 따라 달라지는 교호작용을 함께 살핀다.", ["two_way_anova", "interaction"]),
    ]},
    29: {"page_role": "core_content", "term_ids": ["anova", "f_statistic", "tukey_hsd"], "evidence_units": [
        U("basic_statistics_p29_u01", "interpretation", "text", "F test는 그룹들 간 차이가 있다는 것만 알려줄 뿐 어느 쌍이 다른지는 알려주지 않는다.", "ANOVA의 F 검정이 유의해도 어느 집단 쌍이 다른지는 알 수 없어 사후검정이 필요하다.", ["anova", "f_statistic", "tukey_hsd"]),
        U("basic_statistics_p29_u02", "procedure", "text_and_formula", "Tukey HSD: 모든 쌍 중 가장 크게 벌어진 차이를 기준으로 전체 오류율을 5%로 통제하면서 모든 쌍을 동시에 비교", "Tukey HSD는 모든 집단 쌍을 동시에 비교하면서 전체 가족오류율을 통제한다.", ["tukey_hsd"]),
    ]},
    30: {"page_role": "example", "term_ids": ["tukey_hsd"], "evidence_units": [
        U("basic_statistics_p30_u01", "example", "text_and_visual", "iris의 species별 petal_length Tukey HSD 결과: 세 쌍 모두 reject=True이고 setosa-virginica 평균차이가 가장 큼", "iris 예제에서 세 종의 petal_length 평균은 모든 쌍에서 유의하게 다르고 setosa와 virginica의 평균 차이가 가장 크다.", ["tukey_hsd"]),
    ]},
    31: {"page_role": "section_divider", "term_ids": ["regression"], "evidence_units": []},
    32: {"page_role": "core_content", "term_ids": ["correlation", "regression", "linear_regression"], "evidence_units": [
        U("basic_statistics_p32_u01", "comparison", "text_and_visual", "상관계수는 두 변수 관계의 방향과 강도만 말하며 X가 1만큼 늘어날 때 Y가 얼마나 변하는지에 대한 정량적 변화율은 말하지 않는다. 이 변화율을 추정하는 것이 회귀분석이다.", "상관계수는 관계의 방향과 강도를 요약하고 회귀분석은 X 변화에 따른 Y의 정량적 변화율을 추정한다.", ["correlation", "regression", "linear_regression"]),
    ]},
    33: {"page_role": "core_content", "term_ids": ["linear_regression", "ols", "residual", "multicollinearity", "ridge"], "evidence_units": [
        U("basic_statistics_p33_u01", "formula", "text_and_formula", "Yᵢ=β₀+β₁Xᵢ₁+…+βₚXᵢₚ+εᵢ; ε는 관측하지 못한 모든 것을 담으며 관측된 X로 설명 가능한 부분과 그렇지 않은 부분을 분리", "선형회귀는 반응을 설명변수의 선형결합과 오차항으로 나눈다.", ["linear_regression", "residual"]),
        U("basic_statistics_p33_u02", "formula", "text_and_formula", "β̂=arg minβ Σ(Yᵢ-Xᵢᵀβ)²", "최소제곱법은 잔차제곱합을 최소화하는 회귀계수를 찾는다.", ["ols", "residual", "linear_regression"]),
        U("basic_statistics_p33_u03", "formula", "text_and_formula", "XᵀXβ=XᵀY; β̂=(XᵀX)⁻¹XᵀY; (XᵀX)⁻¹이 존재해야 하며 다중공선성 문제로 이어진다.", "정규방정식에서 XᵀX가 가역이면 최소제곱 해를 얻으며, 특이하거나 거의 특이하면 해 계산이 불가능하거나 불안정해진다.", ["ols", "multicollinearity", "ridge"]),
    ]},
    34: {"page_role": "core_content", "term_ids": ["linear_regression", "ols", "residual"], "evidence_units": [
        U("basic_statistics_p34_u01", "formula", "formula", "단순 선형회귀 SSE를 β₀,β₁로 미분해 0으로 두고 β̂₁=Σ(xᵢ-x̄)(yᵢ-ȳ)/Σ(xᵢ-x̄)², β̂₀=ȳ-β̂₁x̄를 얻음", "단순선형회귀는 SSE를 최소화해 기울기와 절편을 추정한다.", ["linear_regression", "ols"]),
        U("basic_statistics_p34_u02", "formula", "formula", "다중 선형회귀 J(β)=||y-Xβ||²; Xᵀ(y-Xβ)=0; β=(XᵀX)⁻¹Xᵀy", "다중선형회귀도 행렬 형태의 잔차제곱합을 최소화하는 정규방정식으로 계수를 추정한다.", ["linear_regression", "ols"]),
    ]},
    35: {"page_role": "core_content", "term_ids": ["linear_regression", "exogeneity", "homoscedasticity", "independence", "normality", "residual", "standard_error", "p_value", "qq_plot"], "evidence_units": [
        U("basic_statistics_p35_u01", "assumption", "text_and_visual", "선형성: 파라미터에 대해 선형; 위반 시 왜곡된 관계를 추정; Residual vs Fitted(곡선)", "선형회귀는 파라미터에 대한 선형성을 가정하며 곡선형 잔차 패턴은 위반 신호다.", ["linear_regression", "residual"]),
        U("basic_statistics_p35_u02", "assumption", "visual", "외생성: E[ε|X]=0; 위반 시 편향됨·인과 해석 불가능; 도메인 지식/설계", "오차의 조건부 평균이 0이라는 외생성이 깨지면 계수가 편향되고 인과 해석이 어렵다.", ["exogeneity", "residual"]),
        U("basic_statistics_p35_u03", "assumption", "text_and_visual", "등분산성(잔차); 위반 시 S.E., p-value, t-stat이 틀리게 나옴; Residual vs Fitted(깔때기)", "잔차 등분산성이 깨지면 표준오차와 검정 통계량 해석이 부정확해질 수 있으며 깔때기형 잔차도로 점검한다.", ["homoscedasticity", "residual", "standard_error", "p_value"]),
        U("basic_statistics_p35_u04", "assumption", "text_and_visual", "독립성(잔차): 오차들끼리 서로 상관성이 없어야 함; Residual vs Order", "오차들 사이에 상관이 없어야 하며 관측 순서에 따른 잔차도로 점검한다.", ["independence", "residual"]),
        U("basic_statistics_p35_u05", "assumption", "text_and_visual", "정규성(잔차): 소표본 검정에서 챙겨야 하고 대표본에서는 CLT로 근사; QQ Plot", "잔차 정규성은 특히 소표본 추론에서 점검하며 Q-Q plot을 활용한다.", ["normality", "residual", "qq_plot"]),
    ]},
    36: {"page_role": "core_content", "term_ids": ["residual", "homoscedasticity", "linear_regression"], "evidence_units": [
        U("basic_statistics_p36_u01", "interpretation", "text", "잔차는 ‘설명되지 못한’ 부분으로 랜덤성을 가진다. 패턴이 보인다면 잔차에 대한 가정이 흔들리는 것", "적절한 모형의 잔차는 설명되지 않은 무작위 부분이므로 잔차도에 체계적인 패턴이 없어야 한다.", ["residual"]),
        U("basic_statistics_p36_u02", "diagnostic", "text_and_visual", "깔때기 모양: 등분산성 위배; 곡선 패턴: 선형성 위배", "깔때기형 잔차는 이분산성, 곡선형 잔차는 선형성 위반의 신호가 될 수 있다.", ["residual", "homoscedasticity", "linear_regression"]),
    ]},
    37: {"page_role": "core_content", "term_ids": ["r_squared", "adjusted_r_squared", "regression", "causation"], "evidence_units": [
        U("basic_statistics_p37_u01", "definition", "text_and_formula", "R²=SSR/SST=1-SSE/SST; 종속변수 분산 중 모델이 설명하는 비율", "R²는 종속변수의 전체 변동 중 회귀모형이 설명하는 비율이다.", ["r_squared", "regression"]),
        U("basic_statistics_p37_u02", "warning", "text_and_formula", "변수를 추가하면 R²는 절대 안 줄어든다 → adjusted R² 사용", "설명변수를 추가하면 R²는 감소하지 않으므로 모형 비교에는 조정 R²도 함께 본다.", ["r_squared", "adjusted_r_squared"]),
        U("basic_statistics_p37_u03", "warning", "text", "R²가 높다고 예측력/인과관계가 보장되지 않는다: R²는 in-sample, 인과관계도 아님", "높은 R²는 표본 밖 예측력이나 인과관계를 보장하지 않는다.", ["r_squared", "causation"]),
        U("basic_statistics_p37_u04", "warning", "text_and_formula", "R²는 관측된 X의 분산 범위에 의존적이다 → 다른 연구나 표본의 R²를 단순 비교하는 건 위험", "R²는 관측된 설명변수의 분산 범위에도 의존하므로 서로 다른 표본의 값을 단순 비교하면 위험하다.", ["r_squared"]),
    ]},
    38: {"page_role": "core_content", "term_ids": ["multicollinearity", "vif", "pca", "ridge", "omitted_variable_bias"], "evidence_units": [
        U("basic_statistics_p38_u01", "definition", "text", "설명변수 간 상관관계가 높을 때 발생하는 문제; XᵀX에서 계수 계산이 불가능하거나 매우 어렵다.", "다중공선성은 설명변수끼리 강하게 상관되어 XᵀX가 특이하거나 거의 특이해지고 계수 계산이 불가능하거나 불안정해지는 문제다.", ["multicollinearity"]),
        U("basic_statistics_p38_u02", "diagnostic", "text_and_formula", "VIF로 진단; VIFⱼ=1/(1-Rⱼ²)", "VIF는 한 설명변수를 나머지 설명변수로 회귀한 R²를 이용해 다중공선성에 따른 계수 분산 증가를 진단한다.", ["multicollinearity", "vif", "r_squared"]),
        U("basic_statistics_p38_u03", "procedure", "text", "해결방법: PCA, Ridge, 변수 제거; Ridge는 분산을 줄이고 bias 증가; 변수 제거는 omitted variable bias 우려", "PCA·Ridge·변수 제거 등을 고려할 수 있으나 Ridge의 bias-variance trade-off와 변수 제거의 누락변수편향 위험을 검토한다.", ["multicollinearity", "pca", "ridge", "omitted_variable_bias"]),
    ], "source_issues": [
        {"issue_id": "basic_statistics_p38_i01", "source_text": "XᵀX → nearly nonsingular", "issue_type": "typo", "correction": "다중공선성이 심하면 XᵀX는 singular 또는 nearly singular에 가까워진다.", "evaluation_policy": "warn"},
        {"issue_id": "basic_statistics_p38_i02", "source_text": "VIF>100이면 심각한 다중공선성이다.", "issue_type": "overgeneralized", "correction": "VIF 임계값은 절대 기준이 아니므로 값과 분석 맥락을 함께 판단한다.", "evaluation_policy": "exclude"},
    ]},
    39: {"page_role": "core_content", "term_ids": ["multicollinearity", "regression", "causation", "standard_error"], "evidence_units": [
        U("basic_statistics_p39_u01", "interpretation", "text", "다중공선성이 있어도 계수는 여전히 unbiased estimator; 편향이 아니라 분산이 폭증", "다중공선성은 그 자체로 계수를 편향시키기보다 계수 분산과 표준오차를 크게 만든다.", ["multicollinearity", "standard_error"]),
        U("basic_statistics_p39_u02", "comparison", "text", "전체 모델의 예측력에는 크게 영향을 주지 않을 수도 있지만 개별 계수를 고유한 효과로 해석할 때 문제; 예측 목적에는 덜 치명적, 인과적·구조적 해석 목적에는 치명적", "다중공선성은 전체 예측보다 개별 계수의 고유 효과를 해석할 때 더 큰 문제가 될 수 있어 분석 목적에 따라 판단한다.", ["multicollinearity", "regression", "causation"]),
    ]},
    40: {"page_role": "core_content", "term_ids": ["glm", "logistic_regression"], "evidence_units": [
        U("basic_statistics_p40_u01", "definition", "text", "GLM(Generalized Linear Model): 선형회귀의 가정을 만족시킬 수 없는 경우; Multiple linear regression의 일반화; Logistic, Poisson, Ordinal Regression", "GLM은 선형회귀를 일반화한 모형군으로 로지스틱·포아송·순서형 회귀 등을 포함한다.", ["glm", "logistic_regression"]),
    ], "source_issues": [{"issue_id": "basic_statistics_p40_i01", "source_text": "Genearlized Linear Model", "issue_type": "typo", "correction": "Generalized Linear Model", "evaluation_policy": "warn"}]},
    41: {"page_role": "core_content", "term_ids": ["logistic_regression", "sigmoid", "odds", "log_odds", "maximum_likelihood"], "evidence_units": [
        U("basic_statistics_p41_u01", "relation", "text_and_formula", "종속변수가 Binary(0 또는 1)일 때 원하는 것은 확률 [0,1]; Solution: sigmoid; p=P(Y=1|X)=1/(1+e^-(β₀+β₁X))", "로지스틱 회귀는 이진 반응의 확률을 시그모이드 함수로 0과 1 사이에 제한한다.", ["logistic_regression", "sigmoid"]),
        U("basic_statistics_p41_u02", "interpretation", "text_and_formula", "log(p/(1-p))=β₀+β₁X; X가 1만큼 증가할 때 odds가 e^β₁배", "로그 오즈는 선형예측자와 같고 X가 1 증가하면 오즈는 exp(β₁)배가 된다.", ["odds", "log_odds", "logistic_regression"]),
        U("basic_statistics_p41_u03", "procedure", "text", "계수의 추정은 gradient descent나 MLE로 할 수 있다.", "로지스틱 회귀 계수는 최대우도추정이나 이를 최적화하는 경사하강법으로 구할 수 있다.", ["logistic_regression", "maximum_likelihood"]),
    ]},
    42: {"page_role": "closing", "term_ids": [], "evidence_units": []},
}


CONTENT_OVERRIDES = {
    11: "1종 오류는 참인 귀무가설을 기각하는 오류로 α에 대응한다. 2종 오류는 거짓인 귀무가설을 기각하지 못하는 오류로 β에 대응한다. 검정력은 β와 구분해서 해석해야 한다.",
    21: "ANOVA에서는 관측치 독립성, 집단별 정규성, 집단 간 등분산성을 점검한다. 슬라이드의 ‘정규성이 깨지면 F 검정 자체가 불가능하다’는 절대적 표현은 평가 근거에서 제외한다.",
    25: "Kruskal-Wallis 절차를 설명하는 영문 참고 이미지이지만 일부 글자와 공식이 훼손되어 있어 직접 평가 근거로 사용하지 않는다.",
    37: "R²=SSR/SST는 종속변수 변동 중 모델이 설명한 비율이다. 변수를 추가하면 감소하지 않으므로 조정 R²를 함께 본다. 높은 R²는 표본 밖 예측력이나 인과관계를 보장하지 않고, 관측된 X의 분산 범위에도 영향을 받는다.",
    38: "설명변수끼리 상관이 높으면 XᵀX가 특이하거나 거의 특이해져 계수 계산과 해석이 불안정해진다. VIF로 진단하고 PCA, Ridge, 변수 제거 등을 고려하되 Ridge의 편향-분산 trade-off와 변수 제거의 누락변수편향 위험을 검토한다.",
}


CLAIM_LINKS: dict[str, tuple[list[str], list[str]]] = {
    "stats.random_variable": (["basic_statistics_p4_u01"], ["random_variable", "sample_space"]),
    "stats.expectation_variance": (["basic_statistics_p4_u02", "basic_statistics_p4_u03"], ["expected_value", "variance", "standard_deviation"]),
    "stats.sample_population": (["basic_statistics_p5_u01", "basic_statistics_p5_u02"], ["population", "sample", "sampling"]),
    "stats.sample_inference": (["basic_statistics_p5_u01"], ["population", "sample", "sampling"]),
    "stats.covariance_direction": (["basic_statistics_p6_u01"], ["covariance"]),
    "stats.correlation_scaled": (["basic_statistics_p6_u02"], ["correlation", "covariance", "variance"]),
    "stats.correlation_not_causation": (["basic_statistics_p6_u03"], ["correlation", "causation"]),
    "stats.conditional_definition": (["basic_statistics_p7_u01"], ["conditional_probability"]),
    "stats.conditional_bayes": (["basic_statistics_p7_u01", "basic_statistics_p7_u02"], ["conditional_probability", "bayes_theorem"]),
    "stats.test_steps": (["basic_statistics_p9_u01"], ["hypothesis_testing", "null_hypothesis", "alternative_hypothesis", "significance_level", "test_statistic", "p_value"]),
    "stats.test_selection": (["basic_statistics_p9_u02"], ["hypothesis_testing", "normality"]),
    "stats.type1_error": (["basic_statistics_p11_u01"], ["type_i_error", "null_hypothesis"]),
    "stats.type2_error": (["basic_statistics_p11_u02"], ["type_ii_error", "null_hypothesis"]),
    "stats.error_tradeoff": (["basic_statistics_p12_u01", "basic_statistics_p13_u01"], ["type_i_error", "type_ii_error"]),
    "stats.p_value_definition": (["basic_statistics_p14_u01"], ["p_value", "null_hypothesis"]),
    "stats.p_value_not_h0_probability": (["basic_statistics_p14_u02", "basic_statistics_p16_u01"], ["p_value", "null_hypothesis", "null_probability"]),
    "stats.sample_size_effect": (["basic_statistics_p15_u01", "basic_statistics_p15_u02"], ["test_statistic", "standard_error", "p_value", "confidence_interval"]),
    "stats.ci_repeated_sampling": (["basic_statistics_p17_u01"], ["confidence_interval", "confidence_level"]),
    "stats.ci_width": (["basic_statistics_p17_u02", "basic_statistics_p18_u02"], ["confidence_interval", "confidence_level"]),
    "stats.ci_fixed_interval": (["basic_statistics_p18_u01"], ["confidence_interval", "fixed_interval_probability"]),
    "stats.anova_purpose": (["basic_statistics_p19_u01", "basic_statistics_p19_u02"], ["anova", "between_group_variation", "within_group_variation"]),
    "stats.anova_decomposition": (["basic_statistics_p20_u01"], ["anova", "between_group_variation", "within_group_variation"]),
    "stats.f_ratio": (["basic_statistics_p20_u02"], ["f_statistic", "between_group_variation", "within_group_variation"]),
    "stats.anova_assumptions": (["basic_statistics_p21_u01"], ["anova", "independence", "normality", "homoscedasticity"]),
    "stats.assumption_checks": (["basic_statistics_p22_u01", "basic_statistics_p22_u02", "basic_statistics_p23_u01", "basic_statistics_p23_u02", "basic_statistics_p26_u01", "basic_statistics_p26_u02"], ["independence", "durbin_watson", "normality", "shapiro_wilk", "qq_plot", "homoscedasticity", "levene", "bartlett"]),
    "stats.anova_alternatives": (["basic_statistics_p24_u01", "basic_statistics_p27_u01"], ["anova", "normality", "homoscedasticity", "kruskal_wallis", "welch_anova"]),
    "stats.alternative_conditions": (["basic_statistics_p24_u01", "basic_statistics_p27_u01"], ["normality", "homoscedasticity", "kruskal_wallis", "welch_anova"]),
    "stats.anova_design": (["basic_statistics_p28_u01", "basic_statistics_p28_u02"], ["one_way_anova", "two_way_anova", "interaction"]),
    "stats.posthoc": (["basic_statistics_p29_u01", "basic_statistics_p29_u02"], ["anova", "f_statistic", "tukey_hsd"]),
    "stats.correlation_vs_regression": (["basic_statistics_p32_u01"], ["correlation", "regression", "linear_regression"]),
    "stats.ols_objective": (["basic_statistics_p33_u01", "basic_statistics_p33_u02", "basic_statistics_p34_u01", "basic_statistics_p34_u02"], ["linear_regression", "ols", "residual"]),
    "stats.normal_equation": (["basic_statistics_p33_u03"], ["ols", "multicollinearity"]),
    "stats.regression_assumptions": (["basic_statistics_p35_u01", "basic_statistics_p35_u02", "basic_statistics_p35_u03", "basic_statistics_p35_u04", "basic_statistics_p35_u05"], ["linear_regression", "exogeneity", "homoscedasticity", "independence", "normality", "residual"]),
    "stats.residual_diagnostics": (["basic_statistics_p36_u01", "basic_statistics_p36_u02"], ["residual", "homoscedasticity", "linear_regression"]),
    "stats.r_squared": (["basic_statistics_p37_u01", "basic_statistics_p37_u02", "basic_statistics_p37_u03", "basic_statistics_p37_u04"], ["r_squared", "adjusted_r_squared", "causation"]),
    "stats.multicollinearity_effect": (["basic_statistics_p38_u01"], ["multicollinearity"]),
    "stats.multicollinearity_diagnosis": (["basic_statistics_p38_u02", "basic_statistics_p38_u03"], ["multicollinearity", "vif", "pca", "ridge", "omitted_variable_bias"]),
    "stats.prediction_interpretation": (["basic_statistics_p39_u01", "basic_statistics_p39_u02"], ["multicollinearity", "standard_error", "causation"]),
    "stats.glm_scope": (["basic_statistics_p40_u01"], ["glm", "logistic_regression"]),
    "stats.logistic_sigmoid": (["basic_statistics_p41_u01"], ["logistic_regression", "sigmoid"]),
    "stats.logistic_odds": (["basic_statistics_p41_u02"], ["logistic_regression", "odds", "log_odds"]),
}


REQUIRED_ELEMENTS: dict[str, list[str]] = {
    "stats.random_variable": ["표본공간의 각 결과를 실수에 대응시키는 함수라는 의미"],
    "stats.expectation_variance": ["기댓값을 확률가중평균 또는 반복 시행의 장기 평균으로 설명", "분산을 평균 또는 기댓값 주변의 퍼짐으로 설명"],
    "stats.sample_population": ["표본으로 모집단을 추정한다는 관계", "표본의 대표성과 상황에 맞는 표본추출 방법을 검토해야 한다는 점"],
    "stats.sample_inference": ["모집단 전체 조사의 현실적 어려움", "표본으로 모집단 특성을 추정한다는 목적"],
    "stats.covariance_direction": ["공분산이 두 변수의 공동 변화 방향을 나타낸다는 점"],
    "stats.correlation_scaled": ["공분산을 두 변수의 표준편차로 표준화한다는 점", "값의 범위가 -1에서 1이라는 점", "부호는 방향이고 절댓값은 강도라는 해석"],
    "stats.correlation_not_causation": ["상관관계만으로 인과관계를 결론낼 수 없다는 구분"],
    "stats.conditional_definition": ["사건 B가 주어졌을 때 사건 A가 일어날 확률이라는 조건 방향"],
    "stats.conditional_bayes": ["주어진 조건 아래의 확률이라는 의미", "베이즈 정리가 조건부확률의 방향을 바꾸는 데 사용된다는 점"],
    "stats.test_steps": ["귀무가설과 대립가설 설정", "유의수준과 검정통계량·p-value 계산", "계산 결과를 기준으로 귀무가설 기각 여부 판단"],
    "stats.test_selection": ["자료 특성과 검정 가정을 확인", "그 결과에 따라 적절한 검정법을 선택"],
    "stats.type1_error": ["참인 귀무가설을 기각하는 오류", "유의수준 alpha와의 연결"],
    "stats.type2_error": ["거짓인 귀무가설을 기각하지 못하는 오류", "beta와의 연결"],
    "stats.error_tradeoff": ["같은 판정 기준에서 1종 오류와 2종 오류 사이에 trade-off가 생길 수 있다는 점", "오류 비용을 고려해 기준을 정해야 한다는 점"],
    "stats.p_value_definition": ["귀무가설이 참이라는 조건", "관측 데이터 또는 더 극단적인 데이터가 나올 확률"],
    "stats.p_value_not_h0_probability": ["p-value가 귀무가설 자체가 참일 확률이 아니라는 구분"],
    "stats.sample_size_effect": ["표본크기가 커지면 표준오차가 작아진다는 관계", "같은 효과에서도 p-value가 작아질 수 있어 신뢰구간과 함께 해석해야 한다는 점"],
    "stats.ci_repeated_sampling": ["같은 구간 생성 절차를 반복한다는 관점", "그 구간들의 95%가 참 모수를 포함한다는 해석"],
    "stats.ci_width": ["신뢰수준을 높이면 구간이 넓어진다는 관계", "안전성과 구체성 사이의 trade-off"],
    "stats.ci_fixed_interval": ["계산이 끝난 특정 빈도주의 신뢰구간에 모수의 95% 확률을 직접 부여하지 않는다는 점"],
    "stats.anova_purpose": ["둘 이상 집단의 평균 차이를 분석", "집단 간 변동과 집단 내 변동을 비교"],
    "stats.anova_decomposition": ["SST를 SSB와 SSW로 분해", "각 변동을 자유도로 나누어 MSB와 MSW를 계산"],
    "stats.f_ratio": ["F 통계량이 MSB를 MSW로 나눈 값", "F가 클수록 집단 간 신호가 집단 내 잡음보다 상대적으로 크다는 해석"],
    "stats.anova_assumptions": ["관측치 독립성", "집단별 정규성", "집단 간 등분산성"],
    "stats.assumption_checks": ["독립성은 설계와 수집 과정을 우선 확인", "정규성은 Shapiro-Wilk 또는 Q-Q plot으로 점검", "등분산성은 Levene 또는 Bartlett 검정 등으로 점검"],
    "stats.anova_alternatives": ["어떤 ANOVA 가정이 위반되었는지 확인", "위반된 가정에 맞는 대안 검정을 선택"],
    "stats.alternative_conditions": ["정규성이 어려울 때 Kruskal-Wallis 고려", "등분산성이 어려울 때 Welch ANOVA 고려"],
    "stats.anova_design": ["일원 ANOVA는 한 요인의 집단 평균을 분석", "이원 ANOVA는 두 요인과 상호작용을 분석"],
    "stats.posthoc": ["ANOVA의 유의한 결과만으로 어느 집단 쌍이 다른지는 알 수 없다는 점", "Tukey HSD 같은 사후검정과 다중비교 오류 통제"],
    "stats.correlation_vs_regression": ["상관계수는 관계의 방향과 강도를 요약", "회귀는 X 변화에 따른 Y의 정량적 변화율을 추정"],
    "stats.ols_objective": ["선형회귀 모형 Y=Xβ+ε", "잔차제곱합을 최소화하는 계수를 추정"],
    "stats.normal_equation": ["X'X가 가역일 때 정규방정식의 최소제곱 해를 구할 수 있다는 점", "비가역 또는 거의 특이한 상태와 다중공선성의 연결"],
    "stats.regression_assumptions": ["선형성", "오차의 외생성", "등분산성", "독립성", "정규성"],
    "stats.residual_diagnostics": ["적절한 모형의 잔차도에는 체계적 패턴이 없어야 한다는 점", "깔때기 모양은 이분산성, 곡선은 선형성 위반 신호라는 해석"],
    "stats.r_squared": ["R²가 종속변수 변동 중 모델이 설명한 비율이라는 의미", "변수 추가 시 R²가 감소하지 않아 조정 R²를 함께 본다는 점", "높은 R²가 표본 밖 예측력이나 인과관계를 보장하지 않는다는 점"],
    "stats.multicollinearity_effect": ["설명변수 간 강한 상관이 X'X를 거의 특이하게 만든다는 점", "계수 분산과 계산·해석의 불안정성이 커진다는 점"],
    "stats.multicollinearity_diagnosis": ["VIF 등을 이용한 진단", "PCA·Ridge·변수 제거 같은 대응 방법", "변수 제거 시 누락변수편향 위험"],
    "stats.prediction_interpretation": ["다중공선성이 전체 예측보다 개별 계수 해석에 더 큰 문제가 될 수 있다는 점", "분석 목적에 따라 대응을 달리해야 한다는 점"],
    "stats.glm_scope": ["반응변수 분포와 연결함수를 달리해 선형모형을 일반화한다는 점", "로지스틱·포아송·순서형 회귀 등의 예"],
    "stats.logistic_sigmoid": ["이진 반응을 다룬다는 점", "시그모이드로 예측값을 0과 1 사이 확률로 제한"],
    "stats.logistic_odds": ["로그 오즈가 선형예측자와 같다는 점", "X가 1 증가하면 오즈가 exp(β1)배가 된다는 해석"],
}


CRITICAL_ERRORS: dict[str, list[str]] = {
    "stats.expectation_variance": ["분산이 클수록 데이터가 평균 주변에 더 안정적으로 모인다고 설명", "분산이 작을수록 데이터가 더 넓게 퍼진다고 설명"],
    "stats.sample_population": ["특정 표본추출 방법이 대표성을 완벽하게 보장한다고 단정"],
    "stats.covariance_direction": ["공분산이 0이면 일반적으로 두 변수가 독립이라고 단정"],
    "stats.correlation_scaled": ["공분산 원값만으로 서로 다른 단위의 관계 강도를 직접 비교할 수 있다고 설명"],
    "stats.correlation_not_causation": ["높은 상관관계만으로 인과관계를 결론낼 수 있다고 설명"],
    "stats.conditional_definition": ["P(A|B)를 B가 일어났을 때 A가 아니라 A가 일어났을 때 B의 확률로 설명"],
    "stats.conditional_bayes": ["P(A|B)와 P(B|A)를 관련 확률 고려 없이 단순히 같은 값으로 교환"],
    "stats.type1_error": ["1종 오류를 거짓인 귀무가설을 기각하지 못하는 오류로 설명"],
    "stats.type2_error": ["2종 오류를 참인 귀무가설을 기각하는 오류로 설명"],
    "stats.p_value_definition": ["p-value를 귀무가설이 참일 확률로 설명"],
    "stats.p_value_not_h0_probability": ["p-value가 작을수록 귀무가설이 거짓일 확률이 직접 커진다고 설명"],
    "stats.ci_repeated_sampling": ["특정 계산된 구간에 모수가 들어 있을 확률이 95%라고 설명"],
    "stats.ci_width": ["같은 조건에서 신뢰수준을 높이면 구간이 좁아진다고 설명", "넓은 구간일수록 더 정밀한 추정이라고 설명"],
    "stats.ci_fixed_interval": ["빈도주의의 특정 95% 신뢰구간에 모수의 95% 확률을 직접 부여"],
    "stats.f_ratio": ["F 통계량을 MSW/MSB로 설명하거나 작을수록 집단 차이가 크다고 설명"],
    "stats.anova_assumptions": ["정규성 위반 시 표본크기와 위반 정도에 관계없이 F 검정이 항상 불가능하다고 단정"],
    "stats.alternative_conditions": ["정규성 위반과 등분산성 위반에 대한 대안 검정을 서로 뒤바꾸어 설명"],
    "stats.posthoc": ["유의한 ANOVA 결과만으로 어느 집단 쌍이 다른지 바로 특정할 수 있다고 설명"],
    "stats.correlation_vs_regression": ["상관 또는 회귀계수만으로 인과관계를 확정"],
    "stats.ols_objective": ["OLS가 잔차 절댓값 합이나 잔차 자체의 합을 최소화한다고 설명"],
    "stats.r_squared": ["높은 R²가 표본 밖 예측력이나 인과관계를 보장한다고 설명", "설명변수를 추가하면 R²가 감소한다고 설명"],
    "stats.multicollinearity_diagnosis": ["VIF의 하나의 임계값만으로 모든 맥락에서 자동 판정", "변수 제거에 누락변수편향 위험이 없다고 설명"],
    "stats.prediction_interpretation": ["다중공선성이 있으면 예측이 언제나 불가능하다고 단정"],
    "stats.logistic_sigmoid": ["로지스틱 회귀의 선형예측값 자체가 항상 0과 1 사이라고 설명"],
    "stats.logistic_odds": ["X가 1 증가할 때 확률 자체가 exp(β1)배가 된다고 설명"],
}


def apply_evaluation_data(
    processed_path: Path = PROCESSED_PATH,
    rubric_path: Path = RUBRIC_PATH,
) -> None:
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id") != "basic_statistics":
        raise ValueError("기초통계 processed 파일이 아닙니다.")
    pages = {chunk["page"]: chunk for chunk in payload["chunks"]}
    if set(pages) != set(PAGE_DATA):
        raise ValueError("기초통계 PDF의 1~42쪽이 모두 존재해야 합니다.")

    payload["schema_version"] = "2.1.0"
    payload["terminology"] = TERMINOLOGY
    for page, metadata in PAGE_DATA.items():
        chunk = pages[page]
        chunk.update(metadata)
        chunk.setdefault("source_issues", [])
        if page in CONTENT_OVERRIDES:
            chunk["content"] = CONTENT_OVERRIDES[page]

    processed_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    unit_lookup = {
        evidence["unit_id"]: (chunk, evidence)
        for chunk in payload["chunks"]
        for evidence in chunk["evidence_units"]
    }
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    rubric["schema_version"] = "2.2.0"
    claims = {
        claim["claim_id"]: claim
        for objective in rubric["top_level_objectives"]
        for sub_objective in objective["sub_objectives"]
        for claim in sub_objective["claims"]
    }
    if set(claims) != set(CLAIM_LINKS):
        raise ValueError("Rubric Claim 목록과 atomic evidence 연결표가 다릅니다.")
    if set(REQUIRED_ELEMENTS) != set(claims):
        raise ValueError("모든 기초통계 Claim에 required_elements가 필요합니다.")
    unknown_critical_error_claims = set(CRITICAL_ERRORS) - set(claims)
    if unknown_critical_error_claims:
        raise ValueError(
            f"없는 Claim의 critical_errors입니다: {sorted(unknown_critical_error_claims)}"
        )
    for claim_id, (unit_ids, term_ids) in CLAIM_LINKS.items():
        claim = claims[claim_id]
        claim["term_ids"] = term_ids
        claim["evaluation_criteria"] = {
            "required_elements": REQUIRED_ELEMENTS[claim_id],
            "critical_errors": CRITICAL_ERRORS.get(claim_id, []),
        }
        claim["evidence"] = []
        for unit_id in unit_ids:
            chunk, evidence_unit = unit_lookup[unit_id]
            claim["evidence"].append({
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"],
                "unit_id": unit_id,
                "source_excerpt": evidence_unit["source_excerpt"],
                "source_status": evidence_unit["source_status"],
                "review_note": "",
            })

    claims["stats.type2_error"]["text"] = "2종 오류는 거짓인 귀무가설을 기각하지 못하는 오류이며 β로 나타낸다."
    claims["stats.anova_alternatives"]["text"] = "ANOVA 가정이 어려우면 위반된 가정에 맞는 대안 검정을 선택해야 한다."
    claims["stats.r_squared"]["text"] = "R²는 종속변수 변동 중 모델이 설명한 비율이며, 변수 추가 시 감소하지 않고 높은 값이 표본 밖 예측력이나 인과관계를 보장하지 않으므로 조정 R²와 함께 해석한다."
    rubric["excluded_source_claims"] = [
        {
            "page": chunk["page"],
            "chunk_id": chunk["chunk_id"],
            "source_text": issue["source_text"],
            "reason": issue["correction"],
        }
        for chunk in payload["chunks"]
        for issue in chunk["source_issues"]
        if issue["evaluation_policy"] == "exclude"
    ]
    rubric_path.write_text(
        json.dumps(rubric, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    apply_evaluation_data()
    print(PROCESSED_PATH)
