from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "visualization.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "visualization.json"


def term(term_id: str, ko: str, en: str = "", *, abbreviations=None, aliases=None,
         symbols=None, not_equivalent_to=None) -> dict[str, Any]:
    return {"term_id": term_id, "canonical_ko": ko, "canonical_en": en,
            "abbreviations": abbreviations or [], "accepted_aliases": aliases or [],
            "symbols": symbols or [], "not_equivalent_to": not_equivalent_to or []}


TERMINOLOGY = [
    term("data_visualization", "데이터 시각화", "data visualization", aliases=["시각화"]),
    term("data_analytics", "데이터 분석", "data analytics"),
    term("insight", "인사이트", "insight", aliases=["통찰"]),
    term("decision_making", "의사결정", "decision making"),
    term("storytelling", "스토리텔링", "storytelling"),
    term("audience", "독자", "audience", aliases=["청중", "사용자"]),
    term("direct_label", "직접 라벨링", "direct labeling"),
    term("dual_axis", "이중축", "dual axis"),
    term("bar_chart", "막대그래프", "bar chart", aliases=["bar plot"]),
    term("stacked_bar", "누적 막대그래프", "stacked bar chart"),
    term("histogram", "히스토그램", "histogram"),
    term("density_plot", "밀도 그래프", "density plot", aliases=["KDE"]),
    term("bandwidth", "밴드위드", "bandwidth"),
    term("ecdf", "경험적 누적분포함수", "empirical cumulative distribution function", abbreviations=["ECDF"]),
    term("boxplot", "상자그림", "box plot", aliases=["boxplot"]),
    term("violin", "바이올린 그래프", "violin plot"),
    term("pie_chart", "파이차트", "pie chart"),
    term("mosaic", "모자이크 플롯", "mosaic plot"),
    term("treemap", "트리맵", "treemap"),
    term("scatterplot", "산점도", "scatter plot"),
    term("bubble_chart", "버블차트", "bubble chart"),
    term("pca", "주성분분석", "principal component analysis", abbreviations=["PCA"]),
    term("tsne", "t-SNE", "t-distributed stochastic neighbor embedding", abbreviations=["t-SNE"]),
    term("umap", "UMAP", "uniform manifold approximation and projection", abbreviations=["UMAP"]),
    term("line_chart", "선그래프", "line chart", aliases=["line graph"]),
    term("smoothing", "평활화", "smoothing"),
    term("detrending", "추세 제거", "detrending"),
    term("uncertainty", "불확실성", "uncertainty"),
    term("error_bar", "오차막대", "error bar"),
    term("confidence_band", "신뢰대", "confidence band", aliases=["신뢰띠"]),
    term("qualitative_scale", "정성형 색상척도", "qualitative color scale"),
    term("sequential_scale", "순차형 색상척도", "sequential color scale"),
    term("diverging_scale", "양방향 색상척도", "diverging color scale"),
    term("matplotlib", "Matplotlib", "Matplotlib"),
    term("seaborn", "Seaborn", "Seaborn"),
    term("plotly", "Plotly", "Plotly"),
    term("bokeh", "Bokeh", "Bokeh"),
    term("altair", "Altair", "Altair"),
    term("folium", "Folium", "Folium"),
    term("tableau", "Tableau", "Tableau"),
    term("power_bi", "Power BI", "Power BI"),
    term("d3", "D3.js", "D3.js"),
    term("figure", "Figure", "Figure"),
    term("trace", "Trace", "Trace"),
    term("layout", "Layout", "Layout"),
    term("dashboard", "대시보드", "dashboard"),
    term("hierarchy", "데이터 계층", "data hierarchy", aliases=["데이터 하이라키"]),
    term("causality", "인과관계", "causality", not_equivalent_to=["visual_pattern"]),
    term("visual_pattern", "시각적 패턴", "visual pattern", not_equivalent_to=["causality"]),
    term("qualitative_research", "정성 조사", "qualitative research"),
    term("domain_knowledge", "도메인 지식", "domain knowledge"),
]


def unit(unit_id: str, page: int, kind: str, source_type: str, excerpt: str,
         explanation: str, term_ids: list[str]) -> dict[str, Any]:
    return {"unit_id": unit_id, "page": page, "type": kind, "source_type": source_type,
            "source_excerpt": excerpt, "normalized_explanation": explanation,
            "source_status": "verified", "term_ids": term_ids}


U = unit
UNITS = [
    U("viz_p4_u01", 4, "relation", "text_and_visual", "Data≠Information; Raw data를 이해하고 정보를 얻거나 합리적 근거로 의사결정하는 데 데이터 분석을 사용하며, 이 과정에서 시각화는 데이터를 빠르고 효과적으로 이해하게 돕는다.", "원자료는 분석을 거쳐 정보와 의사결정 근거가 되며 시각화가 이해를 돕는다.", ["data_analytics", "data_visualization", "decision_making"]),
    U("viz_p5_u01", 5, "definition", "text", "데이터를 쉽게 이해할 수 있도록 차트, 그래프, 맵과 같은 시각적 요소를 이용해 명확하고 효과적으로 표현하고 전달하는 과정", "데이터 시각화는 시각 요소로 데이터를 이해하기 쉽게 표현·전달한다.", ["data_visualization"]),
    U("viz_p6_u01", 6, "relation", "text_and_visual", "직관적인 데이터 이해; 대용량 데이터의 특성을 짧고 빠르게 전달; 데이터 기반 의사결정 및 스토리텔링", "시각화는 대용량 데이터를 빠르게 이해하고 의사결정과 스토리텔링을 돕는다.", ["data_visualization", "decision_making", "storytelling"]),
    U("viz_p8_u01", 8, "example", "text_and_visual", "예상하지 못한 유입경로 0.8%를 발견해 개발 조치; 대시보드로 멤버등급별 매출 트렌드·프로모션·쿠폰 성과 분석; 시각화는 데이터 가공부터 결과 도출까지 사용되며 분석 근거를 강화", "시각화는 이상과 패턴을 찾고 분석 방향과 근거를 제공한다.", ["data_visualization", "dashboard", "visual_pattern"]),
    U("viz_p14_u01", 14, "procedure", "text", "목적을 이해하기 → 데이터 파악하기 → 시각화 설계하기; 목표·가설/질문 설정, 변수·특성 파악, 관계·특성에 따른 차트 선택, 시각화를 볼 타인을 고려", "목표·데이터·독자를 먼저 정한 뒤 관계에 맞는 차트를 설계한다.", ["data_visualization", "audience"]),
    U("viz_p15_u01", 15, "warning", "text", "배경은 지양, 그리드는 최소화, 카테고리가 하나면 범례는 굳이 필요 없음, 범례 대신 직접 라벨링 고려, 이중축은 명확한 관계성이 있을 때만, 그림자 등 불필요한 그래픽 효과 지양", "불필요한 시각 요소를 줄이고 직접 라벨링을 고려하며 이중축을 제한적으로 사용한다.", ["direct_label", "dual_axis"]),
    U("viz_p16_u01", 16, "procedure", "text_and_visual", "명목형은 데이터 크기대로 정렬, 순서형은 순서 그대로 정렬, 라벨이 길면 horizontal bar plot, 스태킹은 total이 중요할 때만", "수량 비교는 범주 특성에 맞게 정렬하고 전체와 구성비가 중요할 때 누적 막대를 쓴다.", ["bar_chart", "stacked_bar"]),
    U("viz_p17_u01", 17, "procedure", "text", "Smoothing은 데이터 수가 충분할 때만; 히스토그램·밀도도표는 적절한 width; 왜곡이 싫으면 ECDF; Highly Skewed면 로그변환; 여러 분포는 boxplot·violin plot", "bin·bandwidth를 적절히 정하고 ECDF·로그변환·상자·바이올린 그래프를 분포 특성에 맞게 선택한다.", ["histogram", "density_plot", "bandwidth", "ecdf", "boxplot", "violin"]),
    U("viz_p18_u01", 18, "procedure", "text", "Pie Chart는 직관적 비율에 효과적; 카테고리가 많거나 비율이 비슷하면 지양; 시간별 분포 변화는 side-by-side bars; 범주가 겹치면 Mosaic Plot·Treemap", "파이차트는 범주가 적고 비율 차이가 명확할 때 쓰고, 아니면 막대·모자이크·트리맵을 고려한다.", ["pie_chart", "bar_chart", "mosaic", "treemap"]),
    U("viz_p19_u01", 19, "procedure", "text_and_visual", "변수가 3개 이상이면 버블차트·색 활용; 고차원이면 PCA·t-SNE·UMAP; 시계열은 Line graph; 추세는 smoothing; 장기 추세 제거는 detrending", "다변량·고차원·시계열 관계에 맞게 위치·크기·색·차원축소·선그래프를 사용한다.", ["scatterplot", "bubble_chart", "pca", "tsne", "umap", "line_chart", "smoothing", "detrending"]),
    U("viz_p20_u01", 20, "comparison", "visual", "x-y Relationships 차트 유형과 Uncertainty를 나타내는 error bars·confidence strips·quantile dot plot 등의 예시", "관계 유형에 맞는 차트를 고르고 추정치의 불확실성을 함께 표현한다.", ["uncertainty", "error_bar", "confidence_band"]),
    U("viz_p21_u01", 21, "comparison", "text_and_visual", "이산/범주형-정성형 배합, 연속형-순차형 배합, 대칭/대립형-양방향 배합", "서열 없는 범주는 정성형, 값 크기는 순차형, 중심값 양쪽의 대립은 양방향 색상척도로 표현한다.", ["qualitative_scale", "sequential_scale", "diverging_scale"]),
    U("viz_p22_u01", 22, "comparison", "visual", "Matplotlib·Seaborn·Plotly·Bokeh·Altair·Folium의 주요 용도와 특징을 비교한 표", "Python 시각화 도구는 범용 커스텀·통계 그래프·인터랙티브 웹·선언형 문법·지도 등 강점이 다르다.", ["matplotlib", "seaborn", "plotly", "bokeh", "altair", "folium"]),
    U("viz_p23_u01", 23, "comparison", "visual", "Tableau·Power BI·Google Analytics·FineReport·D3.js의 주요 용도와 특징을 비교한 표", "시각화 소프트웨어는 BI·Microsoft 연동·트래픽 분석·리포트·맞춤 웹 시각화 등 목적이 다르다.", ["tableau", "power_bi", "d3"]),
    U("viz_p24_u01", 24, "procedure", "text", "Content·Color·Arrangement·Labels & Lines 체크리스트: clear and concise, audience-centric, story, careful data selection, appropriate graph, documentation, intentional color, key pattern, intuitive spatial flow, accurate proportions, distraction-free, readable title and labels; 타인 피드백", "내용·독자·차트 적합성·색·라벨·배치·문서화를 점검하고 피드백으로 개선한다.", ["audience", "storytelling"]),
    U("viz_p26_u01", 26, "definition", "text_and_visual", "Plotly는 인터랙티브한 시각화가 가능한 Python 그래픽 라이브러리. Figure는 data와 layout을 입력받음; Data는 Trace의 리스트; Trace는 개별 그래프 항목; Layout은 레이아웃과 스타일", "Plotly Figure는 trace 목록인 data와 표현 설정인 layout으로 구성된다.", ["plotly", "figure", "trace", "layout"]),
    U("viz_p29_u01", 29, "example", "text_and_visual", "7월 11일부터 방문 수가 폭등한 패턴을 발견하고 제품 판매량으로 질문을 좁힘", "전체 방문 이상을 발견한 뒤 제품 지표로 질문을 좁힌다.", ["storytelling", "visual_pattern"]),
    U("viz_p30_u01", 30, "example", "text_and_visual", "방문자가 늘어난 동안 제품 26의 판매량이 급증해 제품 26의 조회·판매로 분석을 좁힘", "방문 이상과 특정 제품 판매의 동시 패턴을 보고 다음 질문을 정한다.", ["storytelling", "visual_pattern"]),
    U("viz_p31_u01", 31, "example", "text_and_visual", "제품 26은 11일부터 조회·판매가 급증한 뒤 14일 판매가 거의 사라진 패턴을 재고 소진·품절로 해석하고 광고 효과를 다음 가설로 확인", "강의 사례에서는 조회·판매 패턴을 재고 소진으로 해석했으나 이는 해당 사례의 가설이다.", ["storytelling", "visual_pattern"]),
    U("viz_p32_u01", 32, "example", "text_and_visual", "급증 기간의 유입은 paid보다 organic 비중이 크게 나타나 광고 원인 가설을 약화하고 외부 원인을 탐색", "유입 패턴으로 광고 가설을 재검토하지만 시각화만으로 인과를 확정하지 않는다.", ["storytelling", "visual_pattern", "causality"]),
    U("viz_p33_u01", 33, "example", "text_and_visual", "정성 조사에서 7월 11일 유명인의 제품 착용 보도라는 외부 정보를 확인", "시각화로 확인하기 어려운 외부 원인은 정성 조사와 도메인 정보로 확인한다.", ["qualitative_research", "domain_knowledge", "causality"]),
    U("viz_p34_u01", 34, "procedure", "text_and_visual", "방문자 수 → 판매 Top3 → 26번 제품 판매 → 유입 경로 → 정성조사로 이어지는 분석 STEP", "이상 발견부터 세부 지표·가설·추가 조사로 이어지는 스토리 흐름을 구성한다.", ["storytelling"]),
    U("viz_p35_u01", 35, "relation", "text_and_visual", "코드를 빠르게 작성하는 것보다 데이터에 대한 높은 이해를 바탕으로 스토리 있는 대시보드를 생성; 데이터 계층 구조와 top-down·bottom-up 분석", "시각화 역량은 데이터 계층을 이해하고 독자가 따라갈 수 있는 스토리 대시보드를 만드는 데 있다.", ["dashboard", "hierarchy", "storytelling"]),
    U("viz_p37_u01", 37, "procedure", "text", "시각화는 분석 결과를 제3자에게 효과적으로 나타내고 인사이트·의사결정을 뒷받침. 목적과 의도 → 필요한 데이터 → 라이브러리·툴·차트 선택 → 스토리 구성", "목적·데이터·표현·스토리를 연결해 분석 결과와 의사결정 근거를 전달한다.", ["data_visualization", "insight", "decision_making", "storytelling"]),
    U("viz_p38_u01", 38, "warning", "text", "시각화로 모든 결과를 확인하고 모든 문제의 원인을 파악할 수는 없음. 외부 요인이 변수가 될 수 있으며 시각화와 정성적 조사·도메인 지식을 결합", "시각 패턴만으로 모든 원인을 확정하지 말고 정성 조사와 도메인 지식을 결합한다.", ["qualitative_research", "domain_knowledge", "causality", "visual_pattern"]),
]


CLAIM_UNITS = {
    "viz.definition": ["viz_p5_u01"], "viz.data_to_information": ["viz_p4_u01"], "viz.benefits": ["viz_p6_u01"],
    "viz.analysis_evidence": ["viz_p8_u01"], "viz.analysis_role": ["viz_p8_u01"],
    "viz.set_goal": ["viz_p14_u01"], "viz.inspect_data": ["viz_p14_u01"], "viz.audience": ["viz_p14_u01"],
    "viz.reduce_clutter": ["viz_p15_u01"], "viz.direct_label": ["viz_p15_u01"], "viz.dual_axis": ["viz_p15_u01"],
    "viz.amount_order": ["viz_p16_u01"], "viz.stacked_condition": ["viz_p16_u01"],
    "viz.histogram_bandwidth": ["viz_p17_u01"], "viz.distribution_alternatives": ["viz_p17_u01"],
    "viz.pie_condition": ["viz_p18_u01"], "viz.avoid_pie": ["viz_p18_u01"], "viz.proportion_alternatives": ["viz_p18_u01"],
    "viz.multivariate": ["viz_p19_u01"], "viz.dimension_reduction": ["viz_p19_u01"], "viz.time_series": ["viz_p19_u01"], "viz.map_uncertainty": ["viz_p20_u01"],
    "viz.qualitative": ["viz_p21_u01"], "viz.sequential": ["viz_p21_u01"], "viz.diverging": ["viz_p21_u01"],
    "viz.python_tools": ["viz_p22_u01"], "viz.software_tools": ["viz_p23_u01"], "viz.plotly_structure": ["viz_p26_u01"],
    "viz.content_fit": ["viz_p24_u01"], "viz.labels_colors": ["viz_p24_u01"], "viz.arrangement_feedback": ["viz_p24_u01"],
    "viz.question_narrowing": ["viz_p29_u01", "viz_p30_u01", "viz_p31_u01", "viz_p32_u01"],
    "viz.evidence_to_question": ["viz_p29_u01", "viz_p30_u01", "viz_p31_u01", "viz_p32_u01"],
    "viz.case_not_general_rule": ["viz_p31_u01", "viz_p32_u01", "viz_p33_u01"],
    "viz.qualitative_research": ["viz_p33_u01", "viz_p38_u01"], "viz.not_causality_alone": ["viz_p32_u01", "viz_p33_u01", "viz_p38_u01"],
    "viz.story_flow": ["viz_p34_u01", "viz_p35_u01"], "viz.end_to_end": ["viz_p37_u01"], "viz.actionable_conclusion": ["viz_p35_u01", "viz_p37_u01"],
}


CRITICAL_ERRORS = {
    "viz.data_to_information": ["원자료 그 자체가 항상 의미 있는 정보와 의사결정 근거를 자동으로 제공한다고 설명"],
    "viz.set_goal": ["시각화의 목표·질문은 차트를 다 그린 후에만 정해도 된다고 설명"],
    "viz.dual_axis": ["이중축은 어떤 두 지표를 임의로 겹쳐도 관계를 정확히 보장한다고 설명"],
    "viz.histogram_bandwidth": ["bin 폭과 bandwidth를 어떻게 정해도 분포 모양은 절대 바뀌지 않는다고 설명"],
    "viz.avoid_pie": ["범주가 많고 비율이 비슷할수록 파이차트가 비교에 더 적합하다고 설명"],
    "viz.qualitative": ["서열 없는 범주에 밝기가 단조롭게 증가하는 순차형 척도만 써야 한다고 설명"],
    "viz.sequential": ["값의 크기나 강도 표현에 서열 없는 임의의 정성형 색만 쓰는 것이 적합하다고 설명"],
    "viz.diverging": ["중심값 양쪽의 대립을 하나의 단조 순차형 색만으로 표현해야 한다고 설명"],
    "viz.plotly_structure": ["Plotly Figure의 data가 스타일 설정이고 layout이 trace 목록이라고 뒤바꿔 설명"],
    "viz.case_not_general_rule": ["해당 이커머스 사례의 재고·광고·유명인 패턴을 모든 비슷한 그래프의 일반 원인으로 확정"],
    "viz.not_causality_alone": ["시각적 패턴만으로 외부 원인과 인과관계를 확정할 수 있다고 설명"],
    "viz.qualitative_research": ["시각화에 나타나지 않은 외부 요인은 추가 조사 없이도 자동으로 확정된다고 설명"],
}


ROLES = {1: "cover", 2: "table_of_contents", 3: "section_divider", 12: "section_divider",
         13: "supplementary_reference", 25: "section_divider", 27: "example", 28: "example",
         29: "example", 30: "example", 31: "example", 32: "example", 33: "example",
         34: "example", 35: "example", 36: "section_divider", 39: "closing"}


def apply_evaluation_data(processed_path: Path = PROCESSED_PATH,
                          rubric_path: Path = RUBRIC_PATH) -> None:
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id") != "visualization":
        raise ValueError("시각화 processed 파일이 아닙니다.")
    pages = {chunk["page"]: chunk for chunk in payload["chunks"]}
    if set(pages) != set(range(1, 40)):
        raise ValueError("시각화 PDF의 1~39쪽이 모두 존재해야 합니다.")
    payload["schema_version"] = "2.1.0"
    payload["terminology"] = TERMINOLOGY
    for page_number, chunk in pages.items():
        chunk["page_role"] = ROLES.get(page_number, "core_content")
        chunk["term_ids"] = []
        chunk["evidence_units"] = []
        chunk.setdefault("source_issues", [])
    unit_lookup: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for item in UNITS:
        item = dict(item); page_number = item.pop("page")
        pages[page_number]["term_ids"] = list(dict.fromkeys([*pages[page_number]["term_ids"], *item["term_ids"]]))
        pages[page_number]["evidence_units"].append(item)
        unit_lookup[item["unit_id"]] = (pages[page_number], item)
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    rubric["schema_version"] = "2.2.0"
    claims = {c["claim_id"]: c for obj in rubric["top_level_objectives"] for sub in obj["sub_objectives"] for c in sub["claims"]}
    if set(claims) != set(CLAIM_UNITS):
        raise ValueError("시각화 Claim과 Evidence 연결표가 일치하지 않습니다.")
    for claim_id, unit_ids in CLAIM_UNITS.items():
        target = claims[claim_id]; target["evidence"] = []; term_ids: list[str] = []
        for unit_id in unit_ids:
            chunk, source = unit_lookup[unit_id]
            term_ids.extend(source["term_ids"])
            target["evidence"].append({"page": chunk["page"], "chunk_id": chunk["chunk_id"], "unit_id": unit_id,
                                       "source_excerpt": source["source_excerpt"], "source_status": "verified", "review_note": ""})
        target["term_ids"] = list(dict.fromkeys(term_ids))
        target["evaluation_criteria"] = {"required_elements": [target["text"]],
                                         "critical_errors": CRITICAL_ERRORS.get(claim_id, [])}
    rubric_path.write_text(json.dumps(rubric, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    apply_evaluation_data()
    print(f"updated: {PROCESSED_PATH.relative_to(ROOT)}")
    print(f"updated: {RUBRIC_PATH.relative_to(ROOT)}")
