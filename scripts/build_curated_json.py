from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import LECTURES, Settings, resolve_pdf_path
from src.io_utils import write_json
from src.pdf_loader import load_pdf_pages
from src.schemas import Chunk, LectureDocument


def curated(
    topic: str,
    concepts: list[str],
    visual_description: str,
    content: str,
) -> list[dict[str, object]]:
    return [{
        "topic": topic,
        "concepts": concepts,
        "visual_description": visual_description,
        "content": content,
    }]


CURATION: dict[str, dict[int, list[dict[str, object]]]] = {
    "basic_statistics": {
        1: curated("기초 통계 강의 표지", ["기초 통계"], "2026 Summer YBIGTA 기초 통계 강의 표지이며 발표자는 28기 전영찬으로 표시된다.", "2026 Summer YBIGTA 기초 통계 강의의 표지이다."),
        2: curated("기초 통계 강의 목차", ["확률 복습", "가설검정", "회귀분석"], "Review, Hypothesis Testing, Regression Analysis의 세 섹션이 번호와 함께 배치되어 있다.", "강의는 확률·통계 복습, 가설검정, 회귀분석 순서로 구성된다."),
        3: curated("확률·통계 복습", ["확률", "통계"], "Review 섹션의 시작을 알리는 구분 슬라이드이다.", "확률변수, 표본, 공분산, 조건부확률을 복습하는 섹션의 시작 페이지이다."),
        4: curated("확률변수와 기댓값·분산", ["확률변수", "기댓값", "분산", "표준편차"], "동전 표본공간을 확률변수 값으로 대응시키는 도식, 이산·연속 기댓값 공식, 평균은 같지만 표준편차가 다른 두 정규분포 곡선이 제시된다.", "확률변수는 표본공간의 각 결과를 실수에 대응시키는 함수다. 기댓값은 가능한 값에 확률을 가중한 평균이며, 분산은 값들이 평균에서 떨어진 정도를 나타낸다. 슬라이드는 평균은 같지만 표준편차가 다른 분포를 비교한다."),
        5: curated("모집단과 표본", ["모집단", "표본", "표본추출", "군집표본", "층화표본", "단순무작위표본"], "큰 모집단 원 안에 작은 표본 원을 겹쳐 일부 고객으로 모든 고객을 추정하는 관계를 나타낸다.", "표본추출로 모집단을 추정한다. 표본분포의 특성에 따라 군집표본추출, 층화표본추출, 단순무작위표본추출 등을 선택하며 표본의 대표성을 검토해야 한다."),
        6: curated("공분산과 상관계수", ["공분산", "상관계수", "상관관계", "인과관계"], "양의 관계, 음의 관계, 관계 없음의 세 산점도가 사분면별 점 분포로 비교되고 공분산과 상관계수 공식이 함께 제시된다.", "공분산은 두 변수가 함께 변하는 방향을 나타내고, 상관계수는 공분산을 두 변수의 표준편차로 나누어 -1과 1 사이에서 관계의 방향과 강도를 나타낸다. 상관관계는 인과관계와 다르다."),
        7: curated("조건부확률과 베이즈 정리", ["조건부확률", "베이즈 정리", "전체확률법칙", "전체기댓값법칙"], "조건부확률 공식과 A·B 사건의 벤다이어그램, 베이즈 정리와 반복기댓값 공식이 함께 배치된다.", "조건부확률은 알려진 사건 B 아래에서 A의 확률을 계산한다. 베이즈 정리는 조건의 방향을 바꾸고, 전체기댓값법칙은 조건부 기댓값을 다시 평균낸다."),
        8: curated("가설검정 섹션", ["가설검정"], "Hypothesis Testing이라는 큰 제목의 구분 슬라이드이다.", "가설 설정, 오류, p-value, 신뢰구간과 ANOVA를 다루는 섹션의 시작 페이지이다."),
        9: curated("가설검정 절차", ["귀무가설", "유의수준", "검정통계량", "p-value"], "왼쪽에는 자료 유형과 정규성에 따른 검정법 선택 트리가 있고, 오른쪽에는 가설검정의 다섯 단계가 나열된다.", "가설검정은 귀무·대립가설 설정, 유의수준 선택, 검정통계량 계산, p-value 계산, 귀무가설 판단의 순서로 진행한다. 자료 특성과 가정에 따라 검정법을 선택한다."),
        10: curated("귀무가설을 기각하는 구조", ["귀무가설", "대립가설", "귀류법"], "텍스트로 귀무가설을 기본값으로 두는 논리를 질문과 화살표로 설명한다.", "특정 가설을 직접 증명하기 어렵기 때문에 귀무가설 아래에서 관측 결과의 모순을 찾는 귀류법적 구조를 사용한다. 차이 없음은 하나의 분포로 계산 가능한 기본값 역할을 한다."),
        11: curated("1종 오류와 2종 오류", ["1종 오류", "2종 오류", "alpha", "beta", "검정력"], "임신 여부를 잘못 판정하는 두 사진으로 false positive와 false negative를 대비한다.", "1종 오류는 참인 귀무가설을 기각하는 오류로 alpha와 연결되고, 2종 오류는 거짓 귀무가설을 기각하지 못하는 오류로 beta 및 검정력과 연결된다."),
        12: curated("오류의 트레이드오프", ["1종 오류", "2종 오류", "의사결정 임계값", "트레이드오프"], "고백 여부와 상대의 호감 여부를 2×2 표로 나타낸 연애 비유와 두 오류의 비용이 설명된다.", "판정 기준을 엄격하게 잡으면 1종 오류는 줄지만 2종 오류가 늘고, 느슨하게 잡으면 반대가 된다. 슬라이드는 고백 여부의 비유로 두 오류가 서로 trade-off 관계임을 설명한다."),
        13: curated("1종·2종 오류의 분포 표현", ["귀무가설 분포", "대립가설 분포", "1종 오류", "2종 오류"], "겹치는 두 종 모양 분포에서 귀무가설과 대립가설을 표시하고, 경계 양쪽의 1종 오류 영역은 빨강, 2종 오류 영역은 청록으로 칠했다.", "귀무가설과 대립가설의 분포가 겹치면 하나의 판정 경계에서 1종 오류와 2종 오류가 동시에 발생할 수 있으며 두 영역 사이에 트레이드오프가 생긴다."),
        14: curated("p-value의 정의와 해석", ["p-value", "귀무가설", "극단성"], "귀무가설 분포의 꼬리 영역을 초록색 p-value로 표시하고 관측값 위치와 가능성이 낮은 영역을 함께 나타낸다.", "p-value는 귀무가설이 참이라고 가정했을 때 지금 관측한 데이터 또는 더 극단적인 데이터가 나올 확률이다. 작다는 것은 가정과 데이터 사이의 긴장이 크다는 뜻이지 귀무가설이 거짓일 확률 그 자체가 아니다."),
        15: curated("검정통계량과 표본크기", ["검정통계량", "표준오차", "표본크기", "p-value"], "관측된 차이를 그 차이의 불확실성인 표준오차로 나누는 검정통계량 기본형이 제시된다.", "표본크기가 커지면 표준오차가 작아지고 같은 관측 차이에서도 검정통계량이 커져 p-value가 작아지기 쉽다. 슬라이드는 가설검정을 단독으로 해석하지 말고 p-value와 신뢰구간을 함께 살펴야 한다고 강조한다."),
        16: curated("p-value의 흔한 오류", ["p-value", "조건부확률", "통계적 유의성"], "P(데이터|귀무가설)과 P(귀무가설|데이터)를 큰 빨간 글씨와 밈 이미지로 구분한다.", "p-value는 모수에 대한 확률이나 귀무가설이 참일 믿음의 정도가 아니다. P(데이터|귀무가설)와 P(귀무가설|데이터)의 조건 방향을 바꾸어 해석하면 안 된다."),
        17: curated("신뢰구간", ["신뢰구간", "점추정", "불확실성", "신뢰수준"], "신뢰구간의 반복표집 정의와 정확도·정보량의 트레이드오프, 두 집단 차이의 분산 공식이 텍스트와 수식으로 제시된다.", "신뢰구간은 동일한 생성 절차를 무한히 반복했을 때 정해진 비율의 구간이 참 모수를 포함하도록 만드는 절차이다. 신뢰수준을 높이면 구간은 넓어지며, 두 집단 차이는 각 집단 구간을 단순 비교하지 말고 차이의 분산으로 계산해야 한다."),
        18: curated("신뢰구간의 흔한 오류", ["신뢰구간", "신뢰수준", "구간 폭"], "잘못된 해석을 질문 형식으로 제시하고 핵심 교정 문장을 빨간색으로 강조한다.", "계산된 특정 95% 신뢰구간에 모수가 있을 확률이 95%라고 해석하면 안 된다. 신뢰수준이 높으면 더 안전하지만 덜 구체적이고, 신뢰수준을 고정하지 않은 채 폭만 비교하는 것도 의미가 없다."),
        19: curated("분산분석의 목적", ["ANOVA", "집단 간 변동", "집단 내 변동"], "ANOVA의 영문 철자를 크게 분해해 보여주고 평균 차이를 왜 분산으로 검정하는지 설명한다.", "ANOVA는 두 개 이상 집단의 평균 차이를 전체 변동을 집단 간 변동과 집단 내 변동으로 나누어 분석한다. 집단 간 차이가 집단 내 잡음에 비해 충분히 큰지를 본다."),
        20: curated("ANOVA의 F 통계량", ["SST", "SSB", "SSW", "자유도", "F 통계량"], "총변동 분해, 자유도 정규화, F 비율 계산을 Step 1~3으로 크게 배치한다.", "ANOVA는 SST=SSB+SSW로 변동을 분해하고 자유도로 나눈 MSB와 MSW를 구한다. F=MSB/MSW가 크면 집단 간 신호가 집단 내 잡음보다 크다고 판단한다."),
        21: curated("ANOVA의 주요 가정", ["독립성", "정규성", "등분산성", "F 검정"], "독립성, 정규성, 등분산성의 세 가정을 번호로 나열한 텍스트 중심 슬라이드이다.", "ANOVA의 F 검정을 위해 관측치 독립성, 집단별 정규성, 집단 간 등분산성을 점검해야 한다."),
        22: curated("독립성 가정 점검", ["독립성", "Durbin-Watson", "자기상관", "연구 설계"], "독립성은 주로 연구 설계에서 확보한다는 설명과 시계열·일반 자료의 점검법이 구분되어 있다.", "독립성은 데이터 수집과 연구 설계에서 확보하는 것이 우선이다. 순서가 있는 시계열은 Durbin-Watson으로 자기상관을 확인하고 일반 자료는 수집 과정을 점검한다."),
        23: curated("정규성 가정 점검", ["Shapiro-Wilk", "Q-Q plot", "정규성", "검정력"], "Shapiro-Wilk 설명 옆에 이론적 분위수와 표본 분위수가 직선에 가까운 Q-Q plot이 제시된다.", "소표본에서는 Shapiro-Wilk 검정을 사용할 수 있고, Q-Q plot의 점들이 기준 직선에 가까운지 시각적으로 확인한다. 너무 큰 표본과 너무 작은 표본 모두 검정력 해석에 주의한다."),
        24: curated("Kruskal-Wallis 검정", ["Kruskal-Wallis", "비모수 검정", "순위", "ANOVA 대안"], "정규성이 없을 때 Kruskal-Wallis를 쓰자는 문구가 크게 강조된다.", "Kruskal-Wallis는 원자료를 순위로 바꿔 세 개 이상 독립 집단의 위치 차이를 비교하는 비모수 검정으로, one-way ANOVA의 대안이 될 수 있다."),
        25: curated("Kruskal-Wallis 절차 참고자료", ["Kruskal-Wallis", "순위합", "H 통계량"], "영문 인포그래픽이 검정의 가정, 모든 관측값 순위화, 집단별 순위합, H 통계량과 활용 예시를 한 장에 정리한다.", "Kruskal-Wallis 검정은 모든 집단의 관측값을 합쳐 순위를 매기고 동순위는 평균순위를 부여한 뒤 집단별 순위합으로 H 통계량을 계산한다."),
        26: curated("등분산성 검정", ["Levene 검정", "Bartlett 검정", "등분산성", "정규성"], "Levene 검정의 절대편차 변환 절차와 Bartlett 검정의 장단점을 위아래로 비교한다.", "Levene 검정은 각 관측값을 집단 평균으로부터의 절대편차로 바꾸어 ANOVA를 적용해 분산을 비교한다. Bartlett 검정은 검정력이 높지만 정규성 위반에 민감하므로 의심스러우면 Levene 검정이 안전하다."),
        27: curated("Welch ANOVA", ["Welch ANOVA", "이분산성", "자유도 조정"], "Welch 주스병 이미지를 말장난으로 사용하고 일반 ANOVA와 Welch ANOVA의 차이를 설명한다.", "등분산성이 성립하지 않으면 Welch ANOVA를 사용한다. 그룹별 분산이 다름을 인정하고 그 특성을 반영해 자유도를 조정한다."),
        28: curated("One-way와 Two-way ANOVA", ["One-way ANOVA", "Two-way ANOVA", "주효과", "교호작용"], "마케팅 채널 하나만 보는 질문과 채널×연령대를 보는 질문, 금액 표와 교호작용 수식을 좌우로 비교한다.", "One-way ANOVA는 한 요인의 수준별 평균을 비교한다. Two-way ANOVA는 두 요인의 주효과와 한 요인의 효과가 다른 요인 수준에 따라 달라지는 교호작용을 함께 검정한다."),
        29: curated("Tukey HSD 사후검정", ["사후검정", "Tukey HSD", "다중비교", "가족오류율"], "Tukey HSD 판단식과 statsmodels의 pairwise_tukeyhsd 코드 예시가 함께 제시된다.", "ANOVA의 F 검정은 차이가 존재한다는 것만 알려주므로 어떤 집단 쌍이 다른지 사후검정이 필요하다. Tukey HSD는 전체 가족오류율을 통제하며 모든 쌍을 동시에 비교한다."),
        30: curated("Tukey HSD 예제", ["Tukey HSD", "iris", "petal_length", "species"], "주피터 노트북 화면에 iris 세 종의 petal_length를 비교하는 코드와 meandiff, p-adj, 신뢰구간, reject 열의 결과표가 보인다.", "iris 자료의 세 species 간 petal_length 평균을 Tukey HSD로 비교한 결과 모든 쌍이 유의하며 setosa와 virginica의 평균 차이가 가장 크게 나타난다."),
        31: curated("회귀분석 섹션", ["회귀분석"], "Regression Analysis라는 큰 제목의 구분 슬라이드이다.", "선형회귀의 원리, 가정, 진단, 다중공선성, 일반화선형모형을 다루는 섹션의 시작 페이지이다."),
        32: curated("상관관계와 회귀분석", ["상관계수", "회귀분석", "변화율"], "같은 양의 관계 산점도를 상관관계와 선형회귀로 나란히 보여주며 회귀 쪽에는 적합 직선이 추가된다.", "상관계수는 변수 관계의 방향과 강도를 요약하지만 X가 변할 때 Y가 얼마나 변하는지 직접 말하지 않는다. 회귀분석은 이 정량적 변화율을 추정한다."),
        33: curated("최소제곱 회귀 추정", ["선형모형", "오차항", "최소제곱", "정규방정식"], "모델 설정, 제곱오차 목적함수, 행렬 미분과 정규방정식 해를 3단계 설명 상자로 제시한다.", "선형회귀는 Y=Xβ+ε로 모델을 설정하고 잔차제곱합을 최소화한다. 미분한 정규방정식에서 X'X가 가역이면 β̂=(X'X)^(-1)X'Y를 얻으며, 비가역성은 다중공선성과 연결된다."),
        34: curated("단순·다중 선형회귀 해", ["단순 선형회귀", "다중 선형회귀", "SSE", "OLS"], "왼쪽은 단순회귀의 SSE 미분과 기울기·절편 공식을, 오른쪽은 행렬형 다중회귀의 미분과 닫힌해를 빨간 상자로 비교한다.", "단순회귀와 다중회귀 모두 SSE를 계수에 대해 미분해 0으로 두는 최소제곱법으로 추정한다. 단순회귀는 기울기와 절편 공식, 다중회귀는 행렬 정규방정식으로 표현된다."),
        35: curated("선형회귀 가정", ["선형성", "외생성", "등분산성", "독립성", "정규성"], "다섯 가정을 글머리표로 설명하고 위반 시 문제와 확인 도구를 요약한 표를 배치한다.", "선형회귀는 선형성, 오차의 외생성, 등분산성, 독립성, 정규성 가정을 점검한다. 위반하면 계수 왜곡, 표준오차와 p-value 오류, 해석 문제 등이 생기며 잔차도·순서도·Q-Q plot으로 진단한다."),
        36: curated("잔차도 진단", ["잔차", "잔차도", "등분산성", "선형성"], "좋은 무작위 잔차도와 깔때기형·곡선형의 부적절한 잔차도를 비교하며 각각 등분산성과 선형성 위반으로 표시한다.", "잔차는 모델이 설명하지 못한 확률적 부분이어야 하므로 잔차도에 패턴이 없어야 한다. 깔때기 모양은 이분산성, 곡선 패턴은 선형성 위반 신호이다."),
        37: curated("결정계수", ["R²", "조정 R²", "SST", "SSR", "SSE"], "SST=SSR+SSE 분해와 R² 및 조정 R² 공식이 제시된다.", "R²=SSR/SST는 종속변수 분산 중 모델이 설명한 비율이다. 변수를 추가하면 감소하지 않으므로 조정 R²를 함께 보고, 높은 R²가 표본 밖 예측력을 반드시 보장하지 않으며 표본의 X 분산 범위에도 영향을 받는다는 점을 주의한다."),
        38: curated("다중공선성", ["다중공선성", "VIF", "PCA", "Ridge", "누락변수편향"], "상관행렬 히트맵과 VIF 공식이 제시되고 해결법이 글머리표로 정리된다.", "설명변수끼리 상관이 높으면 X'X가 거의 특이해져 계수 분산과 계산 불안정성이 커진다. VIF로 진단하고 PCA, Ridge, 변수 제거 등을 고려하되 변수 제거에는 누락변수편향 위험이 있다."),
        39: curated("예측력과 해석가능성", ["다중공선성", "비편향 추정량", "예측", "해석"], "예측 목적과 개별 계수 해석 목적을 텍스트로 대비한다.", "다중공선성은 계수의 편향보다 분산을 키운다. 전체 예측에는 영향이 작을 수 있지만 개별 계수의 고유 효과를 인과적·구조적으로 해석하려면 치명적일 수 있어 목적에 따라 다르게 판단한다."),
        40: curated("일반화선형모형", ["GLM", "로지스틱 회귀", "포아송 회귀", "순서형 회귀"], "GLM 제목 아래 선형회귀 가정을 만족시키기 어려운 경우와 대표 모형들을 나열한다.", "일반화선형모형은 다중선형회귀를 일반화해 반응변수의 분포와 연결함수를 달리한다. 로지스틱, 포아송, 순서형 회귀 등이 포함된다."),
        41: curated("로지스틱 회귀", ["로지스틱 회귀", "이진 종속변수", "시그모이드", "오즈", "최대우도"], "선형회귀 직선과 로지스틱 S자 곡선을 비교하고 시그모이드 확률식, 로그 오즈식, 계수 해석을 수식으로 연결한다.", "이진 종속변수에서는 시그모이드로 예측값을 0과 1 사이 확률로 제한한다. 로그 오즈는 선형예측자와 같고 X가 1 증가하면 오즈는 exp(β1)배가 된다. 계수는 최대우도나 경사하강법으로 추정할 수 있다."),
        42: curated("기초 통계 강의 마무리", ["기초 통계"], "'감사합니다'라는 큰 문구로 강의를 마무리한다.", "기초 통계 강의의 종료 페이지이다."),
    },
    "crawling": {
        1: [{
            "topic": "크롤링 강의 표지",
            "concepts": ["크롤링"],
            "visual_description": "2026 Summer YBIGTA 크롤링 강의의 표지이며 발표자는 28기 남궁현종으로 표시된다.",
            "content": "2026 Summer YBIGTA 크롤링 강의 표지. 발표자는 28기 남궁현종이다.",
        }],
        2: [{
            "topic": "크롤링 강의 목차",
            "concepts": ["크롤링", "크롤링 도구", "실습", "과제"],
            "visual_description": "목차가 크롤링의 정의, 크롤링 도구, 실습, 과제의 네 부분으로 순서대로 제시된다.",
            "content": "강의는 크롤링이란 무엇인지, 크롤링 도구, 실습, 과제 순으로 구성된다.",
        }],
        3: [{
            "topic": "크롤링이란",
            "concepts": ["크롤링"],
            "visual_description": "크롤링 개념 설명의 시작을 알리는 구분 슬라이드이다.",
            "content": "크롤링의 정의와 필요성을 설명하는 첫 번째 강의 섹션의 시작 페이지이다.",
        }],
        4: [{
            "topic": "크롤링의 필요성",
            "concepts": ["데이터 수집", "크롤링", "자동화"],
            "visual_description": "SK하이닉스 검색 결과 화면이 예시로 제시되고, 검색 결과 약 2,240만 건이 강조되어 있다. 많은 정보를 일일이 찾는 대신 필요한 정보를 자동 수집하는 흐름을 보여준다.",
            "content": "데이터가 매우 많은 환경에서는 원하는 정보를 일일이 검색하는 방식이 느리므로, 필요한 정보를 자동으로 수집하는 크롤링이 필요하다.",
        }],
        5: [{
            "topic": "크롤링의 정의와 목적",
            "concepts": ["Crawling", "웹", "데이터 수집"],
            "visual_description": "텍스트 중심 슬라이드로 Crawling의 사전적 표현인 '기어다닌다'를 웹상에서 데이터를 긁어 모으는 과정에 연결한다.",
            "content": "크롤링은 웹상을 돌아다니며 데이터를 긁어 모으는 작업이다. 분석에 필요한 데이터가 없을 때 웹에서 필요한 데이터를 수집하기 위해 사용한다.",
        }],
        6: [{
            "topic": "웹 크롤링의 흐름",
            "concepts": ["웹 크롤링", "검색 서비스", "데이터 수집"],
            "visual_description": "Google 로고에서 가운데의 웹 수집을 나타내는 로고를 거쳐 네이버와 다음 등 포털 로고로 이어지는 화살표 흐름이 배치되어, 여러 웹 서비스 사이에서 정보를 찾아다니는 이미지를 보여준다.",
            "content": "크롤링이 웹상을 돌아다니며 여러 웹 서비스의 데이터를 수집하는 개념임을 검색·포털 서비스 로고의 흐름으로 설명한다.",
        }],
        7: [{
            "topic": "웹 스크래핑",
            "concepts": ["스크래핑", "정보 추출", "CSV"],
            "visual_description": "실시간 주식 차트 웹 화면에서 SK하이닉스, 삼성전자, SK스퀘어 등 필요한 종목 정보만 골라 '실시간 차트.csv'로 만드는 흐름을 화살표로 표현한다.",
            "content": "스크래핑은 웹에서 수집 가능한 내용 가운데 필요한 정보만 선택해 가져오는 작업이다. 실시간 주식 차트에서 특정 종목 정보만 CSV로 추출하는 예시가 제시된다.",
        }],
        8: [{
            "topic": "웹 크롤링과 웹 스크래핑 비교",
            "concepts": ["웹 크롤링", "웹 스크래핑", "중복 제거", "확장성"],
            "visual_description": "목적과 용도, 작동 방식, 중복 제어, 리소스와 확장성, 활용 예시를 행으로 둔 비교표가 웹 크롤링과 웹 스크래핑의 차이를 나란히 보여준다.",
            "content": "웹 크롤링은 페이지와 링크를 따라 콘텐츠를 폭넓게 자동 수집하므로 중복 제거와 많은 리소스가 필요할 수 있다. 웹 스크래핑은 여러 소스에서 필요한 정보만 추출해 리소스는 적게 들지만 범위가 제한된다. 실제로 용어는 혼용되지만 원리 차이는 구분해야 한다.",
        }],
        9: [{
            "topic": "HTML의 개념",
            "concepts": ["HTML", "HyperText", "마크업 언어", "마크업 태그", "렌더링"],
            "visual_description": "HTML의 영문 전체 명칭에서 Hyper, Text, Markup, Language의 앞글자가 색으로 강조되어 있다.",
            "content": "HTML은 HyperText 기능을 가진 웹 문서를 만드는 마크업 언어이며 웹 페이지의 뼈대를 구성한다. 마크업 태그가 문서 구조를 표현하고 웹 브라우저가 HTML 콘텐츠를 시각적으로 렌더링한다.",
        }],
        10: [{
            "topic": "HTML 태그",
            "concepts": ["HTML 태그", "시작 태그", "종료 태그"],
            "visual_description": "`<tagname>환영합니다 29기</tagname>` 예시에서 시작 태그, 내용, 종료 태그의 범위를 괄호 표시로 구분한다.",
            "content": "HTML 태그는 엘리먼트의 시작과 끝을 지정한다. 시작 태그는 `<태그이름>`, 종료 태그는 슬래시를 포함한 `</태그이름>` 형태이며 두 태그 사이에 내용이 들어간다.",
        }],
        11: [{
            "topic": "HTML 속성",
            "concepts": ["HTML 속성", "속성 이름", "속성값", "CSS"],
            "visual_description": "`<tagname attr=\"value\">환영합니다 29기</tagname>` 예시에서 태그 이름은 파란색, 속성 이름은 빨간색, 속성값은 초록색으로 구분되고 각각의 위치가 표시된다.",
            "content": "HTML 속성은 엘리먼트에 추가 정보를 넣는 요소로 `<태그이름 속성이름=\"속성값\">` 형태로 표현한다. 속성은 CSS를 사용할 때 활용된다.",
        }],
        12: [{
            "topic": "HTML 엘리먼트",
            "concepts": ["HTML 엘리먼트", "태그", "속성", "내용"],
            "visual_description": "시작 태그부터 속성과 내용, 종료 태그까지의 전체 범위를 큰 괄호로 묶어 하나의 엘리먼트임을 표시한다.",
            "content": "HTML 엘리먼트는 시작 태그부터 종료 태그까지 속성과 내용을 포함한 전체 객체이다. HTML 문서는 이러한 엘리먼트들의 집합이다.",
        }],
        13: [{
            "topic": "HTML 문서 구조 예시",
            "concepts": ["DOCTYPE", "html", "body", "h1", "p"],
            "visual_description": "왼쪽 코드 예시가 `DOCTYPE`, `html`, `body`, `h1`, `p`의 중첩 구조를 들여쓰기로 보여주며, 오른쪽 설명이 각 태그의 역할을 연결한다.",
            "content": "DOCTYPE는 HTML 문서 종류를 정의한다. `<html>`은 웹페이지 전체를 감싸고 `<body>`에는 화면에 보이는 내용이 들어간다. `<h1>`은 제목, `<p>`는 문단을 표현한다.",
        }],
        14: [{
            "topic": "Requests의 GET과 POST 요청",
            "concepts": ["Requests", "GET", "POST", "HTTP 응답 코드", "Selenium"],
            "visual_description": "슬라이드가 GET 요청과 POST 요청을 좌우로 비교한다. GET 쪽에는 `requests.get` 코드 예시가 있고, POST 쪽에는 로그인·데이터 제출과 Selenium 대응이 제시된다. 응답 코드 200과 403/404도 함께 강조된다.",
            "content": "GET 요청은 페이지 열람과 검색 같은 읽기 작업으로 크롤링의 핵심이며 `requests.get`으로 요청할 수 있다. POST 요청은 로그인이나 데이터 제출 같은 쓰기 작업으로 Selenium으로 주로 대응한다. 응답 코드 200은 정상, 403과 404는 차단 또는 오류 여부 확인이 필요하다.",
        }],
        15: [{
            "topic": "크롤링 도구",
            "concepts": ["크롤링 도구"],
            "visual_description": "BeautifulSoup과 Selenium 등 크롤링 도구 설명의 시작을 알리는 구분 슬라이드이다.",
            "content": "크롤링에 사용하는 도구를 설명하는 두 번째 강의 섹션의 시작 페이지이다.",
        }],
        16: [{
            "topic": "BeautifulSoup",
            "concepts": ["BeautifulSoup", "HTML", "XML", "파싱", "requests", "urllib"],
            "visual_description": "BeautifulSoup 로고가 함께 배치되어 있으며 장점과 단점이 텍스트로 대비된다.",
            "content": "BeautifulSoup은 HTML과 XML 문서를 파싱해 데이터 추출에 유용한 분석 트리를 만드는 패키지이다. requests나 urllib로 HTML을 내려받고 BeautifulSoup으로 데이터를 추출한다. 코드가 간단하고 빠르지만 동적 페이지 크롤링은 까다롭다.",
        }],
        17: [{
            "topic": "Selenium",
            "concepts": ["Selenium", "브라우저 자동화", "Chrome", "동적 페이지"],
            "visual_description": "Selenium 로고가 제시되고, 버튼 클릭·스크롤 같은 브라우저 조작 가능성과 복잡한 코드·느린 속도가 장단점으로 대비된다.",
            "content": "Selenium은 Chrome 브라우저를 이용해 키보드와 마우스로 수행하는 웹 동작을 자동화하며 동적 웹사이트에 유리하다. 버튼 클릭과 스크롤이 가능하지만 코드가 복잡하고 속도가 느리다.",
        }],
        18: [{
            "topic": "크롤링 주의사항",
            "concepts": ["robots.txt", "사이트 부하", "time.sleep", "User-Agent", "법적 이슈", "CAPTCHA"],
            "visual_description": "주의사항을 robots.txt 확인, 사이트 부하 방지, 법적 이슈 주의의 세 묶음으로 나눠 굵은 제목과 글머리표로 제시한다.",
            "content": "크롤링 전 robots.txt로 허용 여부를 확인하고 요청 사이에 1~3초 간격을 두며 짧은 시간에 너무 많은 페이지를 요청하지 않아야 한다. 필요하면 User-Agent를 설정한다. 개인정보와 유료 서비스 크롤링을 피하고 학습·비영리 목적으로 제한적으로 사용하며 CAPTCHA가 있는 사이트는 피하는 것이 권장된다.",
        }],
        19: [{
            "topic": "크롤링 실습",
            "concepts": ["크롤링 실습"],
            "visual_description": "크롤링 실습 섹션의 시작을 알리는 구분 슬라이드이며 구체적인 실습 내용은 이 페이지에 제시되지 않는다.",
            "content": "크롤링 실습 섹션의 구분 페이지이다.",
        }],
        20: [{
            "topic": "크롤링 과제",
            "concepts": ["크롤링 과제"],
            "visual_description": "과제 섹션의 시작을 알리는 구분 슬라이드이며 구체적인 과제 내용은 이 페이지에 제시되지 않는다.",
            "content": "크롤링 과제 섹션의 구분 페이지이다.",
        }],
        21: [{
            "topic": "크롤링 강의 마무리",
            "concepts": ["크롤링"],
            "visual_description": "'감사합니다'라는 큰 문구로 강의를 마무리하는 슬라이드이다.",
            "content": "크롤링 강의의 종료 페이지이다.",
        }],
    },
}

CURATION["eda_fe"] = {
    1: curated("EDA·FE 강의 표지", ["EDA", "전처리", "Feature Engineering"], "2026 Summer YBIGTA EDA & FE 표지이며 발표자는 28기 양진완이다.", "EDA, 데이터 전처리, 특성공학 강의의 표지이다."),
    2: curated("EDA·FE 강의 목차", ["Introduction", "EDA", "Preprocessing", "FE", "DA Interview"], "Introduction, EDA & Preprocessing, FE, DA Interview의 네 섹션을 번호로 제시한다.", "강의는 소개, EDA와 전처리, 특성공학, 데이터 분석 면접 문제 순으로 구성된다."),
    3: curated("Introduction 섹션", ["Introduction"], "Introduction 섹션의 시작을 알리는 구분 슬라이드이다.", "EDA·전처리·특성공학의 필요성을 소개하는 섹션의 시작이다."),
    4: curated("Garbage in, Garbage out", ["데이터 품질", "EDA", "전처리", "Feature Engineering"], "쓰레기봉투 옆 구형 컴퓨터에 Garbage in, garbage out 문구가 있는 삽화가 배치된다.", "좋은 입력 데이터가 좋은 결과의 기본이다. EDA, 전처리, 특성공학은 데이터 특성을 이해하고 모델이나 사람이 학습하기 좋은 자료를 만드는 프로젝트의 근간이다."),
    5: curated("EDA·전처리·FE의 역할", ["EDA", "데이터 전처리", "Feature Engineering"], "세 작업의 정의와 주요 작업을 글머리표로 구분한다.", "EDA는 구조·타입·분포·이상치를 탐색해 방향을 정하고, 전처리는 결측치·이상치·스케일·범주를 정제하며, FE는 특성을 생성·제거·변형해 성능을 높인다."),
    6: curated("데이터 분석 프로세스", ["문제 정의", "데이터 수집", "EDA", "전처리", "FE", "모델링"], "문제 정의에서 데이터 수집, EDA·전처리·FE, 분석·모델링, 결과·결론으로 이어지는 수평 타임라인이 그려져 있다.", "분석은 문제와 목표 정의, 데이터 수집, EDA·전처리·FE, 모델 선정·학습·튜닝, 결과와 결론 순으로 진행한다."),
    7: curated("EDA와 전처리 섹션", ["EDA", "데이터 전처리"], "EDA & Preprocessing이라는 큰 제목의 구분 슬라이드이다.", "탐색적 데이터 분석과 전처리 방법을 다루는 섹션의 시작이다."),
    8: curated("EDA 과정", ["데이터 구조", "변수 타입", "결측치", "이상치", "종속변수", "상관관계"], "EDA의 다섯 단계를 번호와 설명으로 나열한다.", "EDA에서는 데이터 형태, 변수 타입, 결측치·이상치, 종속변수 분포, 변수 간 및 변수-종속변수 관계를 차례로 파악한다."),
    9: curated("예제 야구 데이터", ["Statcast", "데이터프레임", "변수"], "Savant 출처 표시와 함께 선수명, 타석, 삼진율, 타구속도 등 많은 열을 가진 2025 야구 통계 표가 제시된다.", "이후 EDA 예제에 사용하는 Statcast 선수 데이터의 전체적인 행·열 구조와 변수 구성을 보여준다."),
    10: curated("데이터 형태 파악 예제", ["pandas", "head", "데이터 구조", "도메인 지식"], "df.head() 출력과 Statcast 용어집 화면을 함께 배치해 값과 변수 의미를 연결한다.", "데이터의 크기, 변수명과 샘플 행을 확인하고 용어집 등 도메인 자료로 각 열의 의미를 파악한다."),
    11: curated("범주형 데이터 인코딩", ["Label Encoding", "One-hot Encoding", "Dummy Encoding"], "색상 열이 정수 라벨과 여러 0·1 더미 열로 바뀌는 표를 사용해 인코딩 방식을 비교한다.", "순서가 있는 범주는 라벨 인코딩, 순서 없는 범주는 원핫 인코딩을 고려한다. 더미 인코딩은 원핫 열 하나를 제거해 다중공선성을 줄이지만 기준 범주가 생긴다."),
    12: curated("변수 타입 확인", ["dtype", "수치형", "범주형"], "df.dtypes 출력 화면에서 object, int64, float64 형식이 열별로 표시된다.", "각 변수가 수치형·범주형·날짜형 중 무엇인지와 pandas 데이터 타입을 확인하고 필요하면 변환한다."),
    13: curated("결측치 확인과 대체", ["결측치", "Imputation", "도메인 지식", "결측 지표"], "df.isnull().sum()과 결측 행 출력 화면 옆에 대체 전략이 나열된다.", "연속형은 평균·중앙값, 범주형은 최빈값 등으로 대체할 수 있으나 도메인과 결측 원인을 고려한다. 결측 자체를 지표로 만들거나 관련 변수로 대체하고 결측 비율이 높으면 열 삭제도 검토한다."),
    14: curated("이상치 탐지와 처리", ["3시그마", "IQR", "KNN", "DBSCAN", "AutoEncoder"], "여러 야구 변수의 boxplot 그리드와 3시그마·IQR·클러스터링·오토인코더 탐지법을 나란히 제시한다.", "이상치는 정규분포의 3시그마, boxplot의 1.5×IQR, 클러스터링 거리, 오토인코더 등으로 탐지하고 제거·변환·대체하거나 목적에 따라 유지한다."),
    15: curated("이상치 처리 주의", ["이상치", "학습 데이터", "데이터 누수"], "같은 boxplot 그리드 옆에 '이상치 제거는 학습할 때에만 사용'이라는 회색 경고 상자가 크게 보인다.", "이상치가 실제 오류인지 중요한 신호인지 먼저 판단한다. 제거 기준은 학습 데이터에서 정하고 검증·테스트 데이터 정보를 사용하지 않도록 주의한다."),
    16: curated("클래스 불균형과 평가 지표", ["클래스 불균형", "Accuracy", "Precision", "Recall", "F1", "PR AUC"], "MVP 여부 막대그래프에서 False가 압도적으로 많고 오른쪽에 대안 평가 지표가 설명된다.", "클래스 불균형에서는 정확도가 모델을 과대평가할 수 있다. 정밀도, 재현율, F1-score, PR AUC 등 소수 클래스 탐지 성능을 반영하는 지표를 사용한다."),
    17: curated("언더샘플링과 오버샘플링", ["Under Sampling", "Over Sampling", "SMOTE", "ADASYN", "TomekLinks"], "다수 클래스를 줄이는 그림과 소수 클래스를 복제하는 그림을 좌우로 비교한다.", "언더샘플링은 다수 클래스를 줄여 정보 손실과 과소적합 위험이 있고, 오버샘플링은 소수 클래스를 늘려 왜곡과 과적합 위험이 있다."),
    18: curated("불균형 학습 전략", ["Focal Loss", "Minority-aware fine tuning", "클래스 불균형"], "불균형 막대그래프와 샘플링 그림 위에 Focal Loss와 소수 클래스 중심 미세조정 전략을 강조한다.", "Focal Loss는 소수·어려운 예제의 손실 가중치를 높이고, minority-aware fine tuning은 전체 데이터 학습 후 소수 클래스 중심으로 추가 학습한다."),
    19: curated("변수 분포와 관계 탐색", ["분포", "상관행렬", "다중공선성", "Feature"], "여러 변수 히스토그램 그리드와 상관계수 히트맵을 함께 보여준다.", "각 변수 분포와 변수 간 상관관계를 탐색하고 종속변수와의 관계를 확인해 중요한 특성을 식별하며 다중공선성을 점검한다."),
    20: curated("다중공선성 진단과 해결", ["다중공선성", "VIF", "Ridge", "Lasso", "PCA"], "VIF 설명 옆에 Ridge의 원형 제약과 Lasso의 마름모 제약에서 해가 닿는 모습을 비교한다.", "독립변수 간 강한 상관은 중요도를 왜곡할 수 있다. VIF로 진단하고 변수 제거·결합, Ridge·Lasso, PCA 등을 적용하되 도메인 의미를 고려한다."),
    21: curated("스케일링 필요성", ["Scaling", "KNN", "SVM", "PCA", "ANN"], "MinMaxScaler와 StandardScaler 사용 코드 화면이 제시된다.", "특성 범위를 통일하면 큰 단위의 특성이 과도하게 지배하는 것을 막는다. 거리·분산 기반 KNN, SVM, PCA, 신경망은 스케일에 민감한 반면 트리 계열은 영향이 작다."),
    22: curated("스케일링 방법 비교", ["Standard Scaling", "Min-Max Scaling", "Robust Scaling", "IQR"], "Z-score, Min-Max, 중앙값·IQR 기반 Robust Scaling의 수식이 세로로 비교된다.", "Standard Scaling은 평균과 표준편차로 표준화하고, Min-Max Scaling은 최솟값과 최댓값을 기준으로 보통 0과 1 사이로 변환하며, Robust Scaling은 중앙값과 IQR을 사용한다."),
    23: curated("데이터 병합과 그룹화", ["pd.merge", "pd.groupby", "Inner Join", "Outer Join", "집계"], "Inner·Outer·Left·Right 조인의 결과표와 이름별 점수를 그룹화해 평균내는 흐름도가 좌우에 있다.", "pd.merge는 공통 key로 데이터프레임을 합치며 조인 방식에 따라 포함 범위가 달라진다. pd.groupby는 특정 열로 묶어 평균·합계·개수 등을 계산한다."),
    24: curated("Feature Engineering 섹션", ["Feature Engineering"], "Feature Engineering이라는 큰 제목의 구분 슬라이드이다.", "특성 선택, 특성 추출과 데이터 누수를 다루는 섹션의 시작이다."),
    25: curated("특성 선택과 특성 추출", ["Feature Selection", "Feature Extraction", "PCA", "LDA", "SVD"], "Feature Selection과 Feature Extraction을 두 단계 상자로 나누고 PCA·SVD·LDA를 하위 방법으로 표시한다.", "특성공학은 유용한 변수를 고르는 특성 선택과 기존 변수를 결합해 차원을 줄이는 특성 추출로 구성된다. PCA는 비지도 분산 축, LDA는 지도형 클래스 구분 축을 찾는다."),
    26: curated("반복적인 특성공학 과정", ["Feature Engineering", "반복 개선", "성능 검증"], "데이터 과학자의 시간 사용 원그래프와 특성 테스트·결정·생성·작동 확인·개선이 순환하는 도식이 함께 있다.", "특성공학은 특성을 생성하고 성능을 확인한 뒤 개선하는 과정을 반복한다. 데이터 정리와 조직화가 실무 시간의 큰 부분을 차지한다는 시각 자료가 제시된다."),
    27: curated("차원의 저주와 차원 축소", ["차원의 저주", "차원 축소", "Feature Selection", "Feature Extraction"], "문제, 해결, 방법을 굵은 소제목으로 나눠 설명한다.", "입력변수가 데이터보다 많고 모델이 복잡하면 학습 지연, 과적합, 다중공선성이 생길 수 있다. 중요한 변수를 선택하거나 잠재 특성을 추출해 차원을 낮춘다."),
    28: curated("Filter와 Wrapper 특성 선택", ["Filter", "Wrapper", "RFE", "상호작용"], "Filter는 한 번 통과하는 흐름, Wrapper는 변수 집합과 모델 학습을 반복하는 흐름으로 비교된다.", "Filter는 상관계수·카이제곱 등 통계량으로 빠르게 고르지만 상호작용을 놓친다. Wrapper는 RFE처럼 모델을 반복 학습해 상호작용을 반영하지만 계산비용이 크다."),
    29: curated("Embedded 특성 선택", ["Embedded", "Lasso", "Feature Importance", "Random Forest", "XGBoost"], "학습과 선택이 순환하는 Embedded 흐름도와 Filter·Wrapper·Embedded 비교표가 제시된다.", "Embedded 방식은 모델 학습 안에서 선택한다. Lasso는 L1 패널티로 계수를 0으로 만들고 트리 모델은 분기 기여도로 중요도를 계산하며 결과는 모델에 의존한다."),
    30: curated("파생변수 생성", ["파생변수", "Feature Split", "lag", "이동평균"], "나이를 young/middle 등으로 범주화한 표와 날짜를 year·month·day로 나눈 표가 예시로 있다.", "지표 변수 생성, 문자열·날짜 열 분리, 시계열 lag·이동평균·요일 같은 시간 특성 생성으로 변수의 경향과 정보를 더 명확하게 만든다."),
    31: curated("Data Leakage", ["Data Leakage", "Target Encoding", "K-fold", "Lag", "Rolling"], "누수 전 전체 평균 인코딩과 자기 행을 제외한 K-fold 인코딩을 빨강·초록 표로 비교한다.", "예측 시점에 알 수 없는 테스트·미래 정보가 학습에 들어가면 검증 성능이 부풀려진다. Target Encoding은 자기 fold를 제외하고, 시계열 lag·rolling은 현재보다 과거 데이터만 사용한다."),
    32: curated("PCA 특성 추출", ["PCA", "주성분", "설명분산", "차원 축소"], "3차원 타원형 점군을 PC1·PC2로 낮추는 도식과 주성분별·누적 설명분산 그래프가 있다.", "PCA는 상관 구조를 반영해 분산을 가장 잘 설명하는 직교 축을 만들고 차원을 줄인다. 보통 누적 설명력 80~95%를 기준으로 개수를 정하지만 선형결합이라 해석성이 낮다."),
    33: curated("텍스트·이미지 전처리", ["Tokenization", "Vectorization", "BoW", "TF-IDF", "Embedding", "Data Augmentation"], "로봇 원본 사진을 회전·흐림·색상변환한 여러 증강 이미지로 확장하는 예가 있다.", "텍스트는 토큰화 후 BoW·TF-IDF 또는 문맥 임베딩으로 벡터화한다. 이미지는 resize, crop, blur, sharpening 등 증강으로 데이터 부족을 보완하고 일반화를 높인다."),
    34: curated("EDA·전처리·FE 요약", ["EDA", "Preprocessing", "Feature Split", "Feature Selection", "Feature Extraction"], "Wrap-up 제목 아래 목적과 적용 순서를 글머리표로 정리한다.", "EDA로 데이터를 이해하고 계획을 세운 뒤 정제, Feature Split, Feature Selection·Extraction 순으로 적용해 분석과 학습 성과를 높인다."),
    35: curated("DA Interview 섹션", ["DA Interview"], "DA Interview Question이라는 큰 제목의 구분 슬라이드이다.", "고객 이탈 데이터를 바탕으로 EDA·FE 판단을 묻는 면접 문제 섹션의 시작이다."),
    36: curated("고객 이탈 면접 문제", ["고객 이탈", "EDA", "Feature Engineering"], "10만 고객 데이터의 5개 샘플 행과 구매·인구통계·이탈여부 열이 큰 표로 제시된다.", "마지막 구매 후 180일 이상 구매가 없으면 이탈로 정의한 쇼핑몰 데이터를 사용해 고객 이탈 예측을 위한 EDA와 FE 과정을 설명하는 문제이다."),
    37: curated("면접 문제 EDA 답안", ["기초통계", "결측치", "이상치", "타깃분포", "도메인"], "상관행렬, 결측률 막대그래프, 금액 분포 그래프를 답안 목록 옆에 배치한다.", "기초 통계와 분포, 결측치, 이상치, 이탈 타깃 분포, 변수 관계, 도메인 특이사항을 순서대로 확인한다."),
    38: curated("면접 문제 이상치·결측치 처리", ["이상치", "결측치", "Imputation"], "샘플 표에서 나이 -5와 방문 580은 빨간 테두리, 쿠폰·구매단가 결측은 파란 테두리로 표시된다.", "음수 나이와 월 580회 방문은 오류 가능성을 검토해 대체·제외·상한 처리한다. 결측 원인을 파악하고 쿠폰사용률은 0, 구매단가는 관련 변수로 대체하거나 삭제하며 결측 자체의 의미도 본다."),
    39: curated("면접 문제 FE 답안", ["Target Leakage", "범주형 인코딩", "파생변수", "Scaling"], "마지막 구매 후 경과일 열을 빨간 테두리로 강조하고 범주별 인코딩·파생변수·스케일링 전략을 설명한다.", "타깃 정의에 직접 쓰인 마지막 구매 후 경과일은 제거한다. 이진·순서형·원핫 인코딩을 변수 성격에 맞게 쓰고 구매 신뢰도 등 파생변수를 만들며 큰 스케일 차이를 조정한다."),
    40: curated("Train-Test Contamination", ["Train-Test Contamination", "Data Leakage", "공정한 평가"], "A의 9:1 분할과 B의 9.5:0.5 분할에서 A test 고객 일부가 B train으로 이동하는 색상 블록 도식이 있다.", "동일 모집단을 서로 다르게 무작위 분할하면 A의 test 샘플이 B의 train에 포함될 수 있다. A test로 둘을 비교한 B의 성능은 데이터 오염 때문에 신뢰할 수 없다."),
    41: curated("클래스 불균형 면접 문제", ["Class Imbalance", "혼동행렬", "Accuracy", "Recall", "Precision", "F1"], "이탈·비이탈 2×2 혼동행렬과 88% 정확도 계산, 5% 대 95% 클래스 비율이 함께 제시된다.", "이탈 고객이 5%인 상황에서 88% 정확도만으로 모델을 신뢰할 수 없다. 전부 비이탈로 예측해도 95%가 될 수 있으므로 재현율·정밀도·F1 등을 함께 평가한다."),
    42: curated("EDA·FE 강의 마무리", ["EDA", "Feature Engineering"], "'감사합니다!'라는 큰 문구로 강의를 마무리한다.", "EDA와 특성공학 강의의 종료 페이지이다."),
}

CURATION["visualization"] = {
    1: curated("시각화 강의 표지", ["데이터 시각화"], "2026 Summer YBIGTA 시각화 강의 표지이며 발표자는 28기 남건우로 표시된다.", "2026 Summer YBIGTA 데이터 시각화 강의의 표지이다."),
    2: curated("시각화 강의 목차", ["Intro", "방법", "실습 및 사례", "정리 및 결론"], "Intro, 방법, 실습 및 사례, 정리 및 결론의 네 섹션이 번호와 함께 배치된다.", "강의는 시각화의 의미, 설계 방법, Plotly 실습 사례, 결론 순으로 구성된다."),
    3: curated("Intro 섹션", ["Intro"], "Intro라는 큰 제목만 배치된 구분 슬라이드이다.", "데이터 분석과 시각화의 정의 및 활용을 소개하는 섹션의 시작 페이지이다."),
    4: curated("데이터 분석과 시각화", ["Data", "Information", "Data Analytics", "의사결정"], "운영 환경에서 수집·가공·분석을 거쳐 Data가 Information과 Intelligence로 좁혀지는 깔때기형 도식이 있다.", "데이터는 그 자체로 정보가 아니며, 원자료를 이해하고 필요한 정보를 찾아 의사결정 근거로 만드는 데이터 분석 과정이 필요하다. 시각화는 이 과정을 빠르고 효과적으로 이해하게 돕는다."),
    5: curated("데이터 시각화의 정의", ["시각화", "데이터 시각화", "차트", "그래프", "맵"], "정의 문장 옆에 파이차트·선그래프·사용자 카드가 있는 대시보드 일러스트가 배치된다.", "데이터 시각화는 데이터를 쉽게 이해하도록 차트, 그래프, 지도 같은 시각 요소로 명확하고 효과적으로 표현하고 전달하는 과정이다."),
    6: curated("데이터 시각화의 이점", ["직관적 이해", "스토리텔링", "의사결정", "비정형 데이터"], "월별 방문자 수를 긴 문장으로 표현한 경우와 1~6월 막대그래프로 표현한 경우를 대비하며, 1월 12,453명에서 6월 17,900명으로 증가하는 흐름을 보여준다.", "시각화는 대용량 데이터의 특성을 짧고 빠르게 전달하고, 직관적 이해와 데이터 기반 의사결정·스토리텔링을 돕고, 비계량·비정형 정보도 도식화할 수 있다."),
    7: curated("분석 과정에서의 시각화", ["문제 정의", "데이터 수집", "데이터 가공", "데이터 분석", "결과 도출"], "문제 정의→수집→가공→분석→결과 도출의 5단계 흐름 아래 이상치 탐지와 매출 분석 사례의 적용 위치를 표시한다.", "시각화는 데이터 가공부터 분석과 결과 도출까지 사용된다. 강의는 수집 데이터 이상치 탐지와 커머스 매출 분석을 예로 든다."),
    8: curated("시각화 활용 사례", ["이상치 탐지", "대시보드", "매출 분석", "유입경로"], "왼쪽 원그래프에서 root_path의 미정의 값 0.8%를 빨간 상자로 강조하고, 오른쪽에는 여러 매출 지표를 담은 대시보드를 보여준다.", "시각화로 예상된 네 범주 외의 유입경로 0.8%를 발견해 개발 조치를 할 수 있고, 대시보드로 멤버등급별 매출 트렌드·프로모션·쿠폰 성과를 파악할 수 있다. 분석 근거를 강화하는 도구라는 점을 강조한다."),
    9: curated("시각화 역량의 활용처: 데이터 분석", ["Data Analytics", "공모전", "채용"], "데이터 활용·시각화 공모전 포스터와 토스 데이터 분석가 및 쿠팡 Business Analyst 채용공고를 나란히 제시하고 시각화·대시보드 역량 문구를 강조한다.", "시각화 역량은 분석 공모전뿐 아니라 데이터 분석가와 비즈니스 분석가 채용에서 인사이트 시각화와 BI 대시보드 경험으로 요구된다."),
    10: curated("시각화 역량의 활용처: 데이터 과학", ["Data Science", "논문 그래프", "BERT", "ViT"], "BERT의 사전학습 단계별 정확도 선그래프와 ViT 계열 모델의 계산량 대비 정확도 산점도 등 논문 Figure를 비교한다.", "데이터 과학에서는 모델의 학습 단계, 계산량, 성능 비교를 논문 그래프로 명료하게 전달하므로 시각화가 연구 결과 해석과 소통에 필요하다."),
    11: curated("시각화 역량의 활용처: 데이터 엔지니어링", ["Data Engineering", "ELK", "Grafana", "모니터링 대시보드"], "ELK의 로그 분석 대시보드와 Grafana의 CPU·메모리·디스크 모니터링 대시보드 화면을 나란히 보여준다.", "데이터 엔지니어링에서도 로그, 시스템 자원, 장애 징후를 대시보드로 관찰하므로 시각화가 운영 모니터링에 활용된다."),
    12: curated("방법 섹션", ["시각화 방법"], "방법이라는 큰 제목만 배치된 구분 슬라이드이다.", "목적과 데이터에 맞는 차트·색상·도구 선택 방법을 다루는 섹션의 시작이다."),
    13: curated("시각화 차트 종류", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Histogram", "Heatmap", "Treemap", "Violin Plot"], "막대·선·파이·도넛·산점도·버블·누적막대·영역·박스·히스토그램·히트맵·트리맵·게이지·바이올린·타임라인·워터폴·퍼널·레이더·점 도표 아이콘을 한눈에 모아 놓았다.", "데이터의 양, 분포, 비율, 관계, 시간 흐름 등 목적에 따라 다양한 차트 유형을 선택할 수 있음을 개괄한다."),
    14: curated("시각화 설계 절차", ["목적 설정", "데이터 파악", "차트 선택", "독자 중심"], "목적을 이해하기→데이터 파악하기→시각화 설계하기의 세 칸에 성별·연령별 페르소나 분석 예시를 연결한다.", "먼저 확인할 목표와 가설을 세우고 변수의 유형·분포·표본 수를 파악한 뒤 관계와 특성에 맞는 차트를 고른다. 결과를 볼 사람의 관점도 설계에 반영해야 한다."),
    15: curated("Matplotlib 구성 요소와 플롯 원칙", ["Matplotlib", "Figure", "Axes", "Legend", "Grid", "Label"], "Matplotlib Figure의 title, axis, tick, grid, line, marker, legend, spine 등 구성요소를 해부한 그림이 있다.", "배경과 그리드, 불필요한 범례·그림자 효과를 줄이고 직접 라벨링을 고려한다. 이중축은 관계가 명확할 때만 사용해 해석 혼란을 막는다."),
    16: curated("수량 시각화", ["Amounts", "Bar Plot", "Dot Plot", "Heatmap", "Stacked Bar"], "세로·가로 막대, 점, 그룹 막대, 누적 막대, 히트맵 예시를 작은 패널로 비교한다.", "명목형은 크기순, 순서형은 본래 순서로 정렬하고 긴 라벨에는 가로 막대를 쓴다. 그룹핑과 분리 플롯을 비교하고 전체가 중요할 때만 누적하며 dot plot과 heatmap도 고려한다."),
    17: curated("분포 시각화", ["Distribution", "Histogram", "Density Plot", "ECDF", "Boxplot", "Violin Plot"], "히스토그램·밀도·누적분포·Q-Q·박스·바이올린·strip·sina·겹친 밀도·ridgeline 등 분포 차트를 격자로 보여준다.", "스무딩은 표본이 충분할 때 쓰고 히스토그램 bin 폭과 밀도 bandwidth를 적절히 정한다. 왜곡을 줄이려면 ECDF, 심한 왜도에는 로그변환, 여러 분포 비교에는 boxplot·violin plot을 고려한다."),
    18: curated("비율 시각화", ["Proportions", "Pie Chart", "Grouped Bar", "Mosaic Plot", "Treemap"], "파이·막대·누적막대·누적밀도·모자이크·트리맵·parallel sets 예시를 격자로 비교한다.", "파이차트는 범주가 적고 비율 차이가 직관적일 때 유효하다. 범주가 많거나 비율이 비슷하면 피하고, 시간별 변화는 병렬 막대, 겹치는 범주는 mosaic plot이나 treemap 등을 고려한다."),
    19: curated("변수 관계 시각화", ["x-y Relationships", "Scatterplot", "Bubble Chart", "PCA", "t-SNE", "UMAP", "Smoothing", "Detrending"], "산점도·버블·paired scatter·slopegraph·density contour·2D/hex bin·correlogram·선그래프와 smoothing 예시가 있다.", "세 변수 이상은 크기나 색을 추가하고, 고차원 데이터는 PCA·t-SNE·UMAP으로 축소할 수 있다. 시계열은 선그래프를 쓰고 추세에는 smoothing, 장기 추세 제거에는 detrending을 고려한다."),
    20: curated("지도와 불확실성 시각화", ["Map", "Choropleth", "Cartogram", "Uncertainty", "Error Bar", "Confidence Band"], "지도·등치지역도·카토그램과 함께 error bar, confidence strip, eye plot, quantile dot plot, confidence band 등 불확실성 표현을 보여준다.", "공간 데이터에는 지도 계열을, 추정치의 불확실성에는 오차막대·신뢰띠·분위수 점도표 등을 사용한다. 추가 차트 선택 자료로 Fundamentals of Data Visualization과 Data Viz Catalogue를 안내한다."),
    21: curated("색상 척도 선택", ["Color Scale", "Qualitative", "Sequential", "Diverging", "ColorBrewer", "Viridis"], "범주형 정성 배합, 연속형 순차 배합, 기준점 양쪽을 표현하는 양방향 배합의 팔레트와 적용 차트를 비교한다.", "범주는 서로 구분되는 정성형 색, 크기·강도는 밝기가 순차적으로 변하는 색, 평균이나 0을 중심으로 대립하는 값은 양방향 색상척도를 사용한다."),
    22: curated("파이썬 시각화 라이브러리 비교", ["matplotlib", "seaborn", "plotly", "altair", "bokeh", "folium"], "여섯 라이브러리의 다운로드 규모, 장점, 단점, 비고를 표로 비교한다.", "matplotlib은 범용성과 커스터마이징, seaborn은 간결한 통계 그래프, plotly·bokeh는 인터랙티브 웹 시각화, altair는 선언형 문법, folium은 지도 시각화에 강점이 있다."),
    23: curated("시각화 소프트웨어 비교", ["Tableau", "Power BI", "Google Analytics", "FineReport", "D3.js"], "각 소프트웨어의 로고와 주요 특징을 표로 정리한다.", "Tableau는 대중적인 BI 도구, Power BI는 Microsoft 생태계 연동, Google Analytics는 웹·앱 트래픽, FineReport는 비즈니스 리포트, D3.js는 HTML·SVG·CSS 기반 맞춤 시각화에 쓰인다."),
    24: curated("시각화 검수 체크리스트", ["Content", "Color", "Labels", "Arrangement", "피드백"], "UCB Data Visualization Checklist를 내용·색상·라벨과 선·배치 영역으로 나누어 체크박스로 제시한다.", "시각화는 명료성, 독자 중심성, 스토리, 데이터·차트 적합성, 문서화, 의도적인 색, 핵심 패턴 강조, 제목·라벨 가독성, 공간 흐름과 비율, 방해요소 여부를 점검하고 다른 사람의 피드백을 받아야 한다."),
    25: curated("실습 및 사례 섹션", ["실습", "사례"], "실습 및 사례라는 큰 제목만 배치된 구분 슬라이드이다.", "Plotly와 가상 이커머스 로그를 이용해 시각화 스토리를 만드는 섹션의 시작이다."),
    26: curated("Plotly 개요와 구조", ["Plotly", "Figure", "Data", "Trace", "Layout", "Dash"], "Plotly 로고, 설치 명령, Figure·Data·Trace·Layout의 계층 설명이 배치된다.", "Plotly는 40개 이상의 차트를 제공하는 인터랙티브 파이썬 그래픽 라이브러리다. Figure는 data와 layout으로 구성되고, data는 개별 그래프 항목인 trace의 목록이며 Dash·Chart Studio와 확장할 수 있다."),
    27: curated("이커머스 매출 급증 시나리오", ["매출", "시나리오", "이상 징후"], "상승 막대 아이콘과 개구리 사진을 사용해 전월 대비 매출 300% 증가를 발견한 분석가 상황을 표현한다.", "데이터 이관 문제로 7월 분석을 못 한 M사가 8월 1일에 전월 대비 매출 300% 증가를 발견하고 원인을 추적하는 시나리오이다."),
    28: curated("이커머스 로그 데이터셋", ["ecommerce_log.csv", "user_Id", "product_Id", "traffic_source", "event_flag", "purchased"], "CSV 파일 아이콘 아래 date, user_Id, product_Id, gender, age_group, traffic_source, event_flag, purchased의 의미를 표로 설명한다.", "M 패션 이커머스의 7월 고객 행동 로그에는 날짜, 사용자·제품 ID, 성별·연령대, 유입경로, 이벤트 여부, 구매 여부가 포함된다."),
    29: curated("일별 방문수 분석", ["방문수", "방문자 수", "시계열", "이상치"], "고유 방문자 수와 총 방문 수의 두 선을 그린 그래프에서 7월 12일 고유 방문자 2,148명, 총 방문 6,442회의 급증을 툴팁으로 강조한다.", "7월 11일부터 방문 수가 급증한 패턴을 발견하고, 다음 분석 질문을 제품 판매량으로 좁힌다."),
    30: curated("일별 판매 Top3 분석", ["Top3 제품", "제품 26", "판매량", "누적 막대"], "날짜별 판매 상위 3개 제품 누적 막대그래프에서 제품 26이 422개 팔린 시점을 툴팁으로 강조한다.", "방문자 수가 증가한 약 4일 동안 제품 26의 판매량이 급증했음을 찾아 해당 제품의 조회와 판매를 더 자세히 본다."),
    31: curated("제품 26 조회·판매 분석", ["제품 26", "조회수", "판매량", "품절", "재고"], "왼쪽 일별 조회수에서 3,205회, 오른쪽 일별 판매량에서 422개가 정점이며 11~14일 이후 판매가 거의 사라지는 두 막대그래프를 비교한다.", "제품 26은 11일부터 조회와 판매가 폭증했지만 14일 재고가 소진되어 품절된 흐름으로 해석한다. 다음으로 광고 효과 여부를 확인한다."),
    32: curated("유입경로별 비율 분석", ["Traffic Source", "organic", "paid", "Stacked Bar"], "email·organic·paid·referral·social의 일별 100% 누적 막대에서 급증 기간의 organic 비중이 약 60%로 커진 구간을 검은 상자로 표시한다.", "급증 기간 유입은 광고 paid보다 직접검색 organic이 대부분이어서 광고가 원인이라는 가설을 약화시키고 외부 원인을 찾게 한다."),
    33: curated("정성 조사로 외부 요인 확인", ["정성 조사", "외부 요인", "도메인 지식", "2025-07-11"], "탑스타가 M사 신발을 애용한다는 가상 기사 문구와 운동화를 신은 상어 합성 이미지를 제시한다.", "정성 조사 결과 7월 11일 유명인의 제품 착용 보도가 있었음을 찾아, 시각화만으로 알 수 없던 매출 급증의 외부 원인을 설명한다."),
    34: curated("시각화 시나리오 흐름", ["스토리텔링", "방문자 수", "판매 Top3", "유입 경로", "정성 조사"], "방문자 수→판매 Top3→제품 26 판매→유입 경로→정성조사의 다섯 상자를 화살표로 연결한다.", "하나의 이상 현상에서 질문을 단계적으로 좁혀 정성 조사까지 이어지는 분석 스토리가 존재한다. 대시보드와 보고서는 이 흐름을 독자가 따라갈 수 있게 구성해야 한다."),
    35: curated("시각화 역량과 데이터 하이라키", ["데이터 하이라키", "대시보드", "Top-down", "Bottom-up", "스토리"], "매출 아래 제품·프로모션, 제품 아래 광고·가격·퀄리티가 연결된 계층도와 상하 방향 화살표를 보여준다.", "시각화 역량은 코드를 빨리 쓰는 능력보다 데이터의 계층 구조를 이해하고 top-down 또는 bottom-up 흐름으로 부가설명 없이도 이해되는 스토리 있는 대시보드를 만드는 능력이다."),
    36: curated("정리 및 결론 섹션", ["정리", "결론"], "정리 및 결론이라는 큰 제목만 배치된 구분 슬라이드이다.", "시각화의 의의와 실천 원칙을 요약하는 마지막 섹션의 시작이다."),
    37: curated("시각화의 의의와 과정", ["인사이트", "의사결정", "목적", "데이터", "차트 선택", "스토리"], "시각화의 의의와 과정을 두 묶음의 글머리표로 정리한다.", "시각화는 분석 결과를 제3자에게 효과적으로 전달하고 인사이트 기반 의사결정을 뒷받침한다. 목적과 의도, 필요한 데이터, 표현 도구·차트, 스토리 구성의 순서로 설계한다."),
    38: curated("시각화 실천 원칙", ["디자인", "AI 활용", "정성 조사", "도메인 지식", "한계"], "전하고 싶은 말을 긴 글머리표로 정리하며 시각화의 어려움, 디자인, AI 활용, 정답의 부재, 정성 조사 결합을 강조한다.", "몇 개의 그림만으로 목적과 결과를 전달해야 하므로 디자인과 청중의 톤앤매너가 중요하다. 코딩만이 역량은 아니며 AI를 활용할 수 있다. 시각화로 모든 원인을 알 수 없으므로 도메인 지식과 정성 조사를 결합해야 한다."),
    39: curated("시각화 강의 마무리", ["데이터 시각화"], "감사합니다라는 큰 문구로 강의를 마무리한다.", "데이터 시각화 강의의 종료 페이지이다."),
}

from scripts.build_cs_basics_evaluation_data import CURATION as CS_BASICS_CURATION
from scripts.build_git_evaluation_data import CURATION as GIT_CURATION
from scripts.build_python_environment_evaluation_data import CURATION as PYTHON_ENVIRONMENT_CURATION
from scripts.build_web_evaluation_data import CURATION as WEB_CURATION
from scripts.build_network_basics_evaluation_data import CURATION as NETWORK_BASICS_CURATION
from scripts.build_ml_evaluation_data import CURATION as MACHINE_LEARNING_CURATION
from scripts.build_dl_evaluation_data import CURATION as DEEP_LEARNING_CURATION
from scripts.build_cv_evaluation_data import CURATION as COMPUTER_VISION_CURATION
from scripts.build_nlp_evaluation_data import CURATION as NLP_CURATION
from scripts.build_docker_evaluation_data import CURATION as DOCKER_CURATION
from scripts.build_llm_evaluation_data import CURATION as LLM_CURATION
from scripts.build_aws_evaluation_data import CURATION as AWS_CURATION
from scripts.build_db_evaluation_data import CURATION as DB_CURATION
from scripts.build_ai_agent_evaluation_data import CURATION as AI_AGENT_CURATION
from scripts.build_rag_evaluation_data import CURATION as RAG_CURATION

CURATION["cs_basics"] = CS_BASICS_CURATION
CURATION["git"] = GIT_CURATION
CURATION["python_environment"] = PYTHON_ENVIRONMENT_CURATION
CURATION["web"] = WEB_CURATION
CURATION["network_basics"] = NETWORK_BASICS_CURATION
CURATION["machine_learning"] = MACHINE_LEARNING_CURATION
CURATION["deep_learning"] = DEEP_LEARNING_CURATION
CURATION["computer_vision"] = COMPUTER_VISION_CURATION
CURATION["nlp"] = NLP_CURATION
CURATION["docker"] = DOCKER_CURATION
CURATION["llm"] = LLM_CURATION
CURATION["aws"] = AWS_CURATION
CURATION["db"] = DB_CURATION
CURATION["ai_agent"] = AI_AGENT_CURATION
CURATION["rag"] = RAG_CURATION


def build(lecture_id: str) -> Path:
    if lecture_id not in CURATION:
        raise ValueError(f"수작업 구조화 정보가 없습니다: {lecture_id}")

    settings = Settings.from_env()
    settings.ensure_output_dirs()
    lecture = LECTURES[lecture_id]
    pdf_path = resolve_pdf_path(settings, lecture)
    loaded = load_pdf_pages(pdf_path, render_dpi=settings.page_render_dpi)
    annotations = CURATION[lecture_id]

    expected_pages = {page.page for page in loaded.pages}
    annotated_pages = set(annotations)
    if expected_pages != annotated_pages:
        raise ValueError(
            f"페이지 주석 범위가 다릅니다: missing={sorted(expected_pages - annotated_pages)}, "
            f"extra={sorted(annotated_pages - expected_pages)}"
        )

    chunks: list[Chunk] = []
    for page in loaded.pages:
        for chunk_number, item in enumerate(annotations[page.page], start=1):
            chunks.append(
                Chunk(
                    chunk_id=f"{lecture_id}_p{page.page}_{chunk_number:02d}",
                    lecture_id=lecture_id,
                    lecture_name=lecture.lecture_name,
                    page=page.page,
                    topic=str(item["topic"]),
                    concepts=[str(value) for value in item["concepts"]],
                    raw_text=page.text,
                    visual_description=str(item["visual_description"]),
                    content=str(item["content"]),
                )
            )

    document = LectureDocument(
        lecture_id=lecture_id,
        lecture_name=lecture.lecture_name,
        source_file=loaded.source_file,
        chunks=chunks,
    )
    output = settings.processed_dir / f"{lecture_id}.json"
    write_json(output, document.model_dump(mode="json"))
    if lecture_id == "basic_statistics":
        from scripts.build_basic_statistics_evaluation_data import apply_evaluation_data
    elif lecture_id == "crawling":
        from scripts.build_crawling_evaluation_data import apply_evaluation_data
    elif lecture_id == "eda_fe":
        from scripts.build_eda_fe_evaluation_data import apply_evaluation_data
    elif lecture_id == "visualization":
        from scripts.build_visualization_evaluation_data import apply_evaluation_data
    elif lecture_id == "cs_basics":
        from scripts.build_cs_basics_evaluation_data import apply_evaluation_data
    elif lecture_id == "git":
        from scripts.build_git_evaluation_data import apply_evaluation_data
    elif lecture_id == "python_environment":
        from scripts.build_python_environment_evaluation_data import apply_evaluation_data
    elif lecture_id == "web":
        from scripts.build_web_evaluation_data import apply_evaluation_data
    elif lecture_id == "network_basics":
        from scripts.build_network_basics_evaluation_data import apply_evaluation_data
    elif lecture_id == "machine_learning":
        from scripts.build_ml_evaluation_data import apply_evaluation_data
    elif lecture_id == "deep_learning":
        from scripts.build_dl_evaluation_data import apply_evaluation_data
    elif lecture_id == "computer_vision":
        from scripts.build_cv_evaluation_data import apply_evaluation_data
    elif lecture_id == "nlp":
        from scripts.build_nlp_evaluation_data import apply_evaluation_data
    elif lecture_id == "docker":
        from scripts.build_docker_evaluation_data import apply_evaluation_data
    elif lecture_id == "llm":
        from scripts.build_llm_evaluation_data import apply_evaluation_data
    elif lecture_id == "aws":
        from scripts.build_aws_evaluation_data import apply_evaluation_data
    elif lecture_id == "db":
        from scripts.build_db_evaluation_data import apply_evaluation_data
    elif lecture_id == "ai_agent":
        from scripts.build_ai_agent_evaluation_data import apply_evaluation_data
    elif lecture_id == "rag":
        from scripts.build_rag_evaluation_data import apply_evaluation_data
    else:
        apply_evaluation_data = None

    if apply_evaluation_data is not None:
        apply_evaluation_data(processed_path=output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="API 없이 사람이 검수한 강의안 구조화 JSON을 생성합니다."
    )
    parser.add_argument("lecture_id", choices=sorted(CURATION))
    args = parser.parse_args()
    output = build(args.lecture_id)
    print(output)


if __name__ == "__main__":
    main()
