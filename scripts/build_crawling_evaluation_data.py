from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "crawling.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "crawling.json"


def term(term_id: str, ko: str, en: str = "", *, abbreviations=None, aliases=None,
         symbols=None, not_equivalent_to=None) -> dict[str, Any]:
    return {
        "term_id": term_id, "canonical_ko": ko, "canonical_en": en,
        "abbreviations": abbreviations or [], "accepted_aliases": aliases or [],
        "symbols": symbols or [], "not_equivalent_to": not_equivalent_to or [],
    }


TERMINOLOGY = [
    term("web_crawling", "웹 크롤링", "web crawling", aliases=["크롤링", "crawler"]),
    term("web_scraping", "웹 스크래핑", "web scraping", aliases=["스크래핑", "scraper"], not_equivalent_to=["web_crawling"]),
    term("html", "HTML", "HyperText Markup Language", abbreviations=["HTML"], aliases=["하이퍼텍스트 마크업 언어"]),
    term("markup_language", "마크업 언어", "markup language"),
    term("tag", "태그", "tag", symbols=["<tag>", "</tag>"]),
    term("attribute", "속성", "attribute", aliases=["HTML attribute"]),
    term("element", "엘리먼트", "element", aliases=["HTML element", "요소"]),
    term("doctype", "문서 형식 선언", "DOCTYPE", abbreviations=["DOCTYPE"], symbols=["<!DOCTYPE html>"]),
    term("http_request", "HTTP 요청", "HTTP request", abbreviations=["HTTP"]),
    term("get", "GET 요청", "GET request", abbreviations=["GET"]),
    term("post", "POST 요청", "POST request", abbreviations=["POST"]),
    term("status_code", "HTTP 상태 코드", "HTTP status code", aliases=["응답 코드"]),
    term("requests", "requests 라이브러리", "Python Requests", aliases=["requests"]),
    term("urllib", "urllib", "urllib"),
    term("beautifulsoup", "BeautifulSoup", "Beautiful Soup", abbreviations=["BS4"], aliases=["beautifulsoup4"]),
    term("parsing", "파싱", "parsing", aliases=["구문 분석"]),
    term("dom_tree", "분석 트리", "parse tree", aliases=["DOM 트리", "document tree"]),
    term("selenium", "Selenium", "Selenium", aliases=["셀레니움"]),
    term("dynamic_page", "동적 웹 페이지", "dynamic web page", aliases=["동적 페이지"]),
    term("robots_txt", "robots.txt", "robots.txt", aliases=["로봇 배제 표준"]),
    term("rate_limiting", "요청 간격 조절", "rate limiting", aliases=["속도 제한", "throttling"]),
    term("user_agent", "User-Agent", "User-Agent", aliases=["유저 에이전트"]),
    term("captcha", "CAPTCHA", "CAPTCHA", aliases=["캡차"]),
]


def unit(unit_id: str, kind: str, source_type: str, excerpt: str,
         explanation: str, term_ids: list[str]) -> dict[str, Any]:
    return {"unit_id": unit_id, "type": kind, "source_type": source_type,
            "source_excerpt": excerpt, "normalized_explanation": explanation,
            "source_status": "verified", "term_ids": term_ids}


U = unit
PAGE_DATA: dict[int, dict[str, Any]] = {
    1: {"page_role": "cover", "term_ids": [], "evidence_units": []},
    2: {"page_role": "table_of_contents", "term_ids": ["web_crawling"], "evidence_units": []},
    3: {"page_role": "section_divider", "term_ids": ["web_crawling"], "evidence_units": []},
    4: {"page_role": "core_content", "term_ids": ["web_crawling"], "evidence_units": [
        U("crawling_p4_u01", "relation", "text_and_visual", "원하는 정보들을 모두 찾기 위해서 일일이 검색하는 것은 너무 느림… 필요한 정보들을 자동으로 수집하는 방법: 크롤링", "대량의 웹 정보를 일일이 찾는 대신 필요한 정보를 자동 수집하기 위해 크롤링을 사용한다.", ["web_crawling"]),
    ]},
    5: {"page_role": "core_content", "term_ids": ["web_crawling"], "evidence_units": [
        U("crawling_p5_u01", "definition", "text", "웹상을 기어다니며 데이터를 긁어 모은다", "웹 크롤링은 웹을 돌아다니며 데이터를 수집하는 작업이다.", ["web_crawling"]),
        U("crawling_p5_u02", "relation", "text", "데이터가 없다! → 크롤링을 통해 웹에서 필요한 데이터를 수집한다", "분석에 필요한 데이터셋이 없을 때 웹을 수집처로 활용한다.", ["web_crawling"]),
    ]},
    6: {"page_role": "example", "term_ids": ["web_crawling"], "evidence_units": [
        U("crawling_p6_u01", "example", "visual", "Google에서 Naver·Daum 등 여러 웹 서비스로 이어지는 크롤링 흐름 도식", "크롤링은 여러 웹 페이지나 서비스를 돌아다니며 내용을 수집한다.", ["web_crawling"]),
    ]},
    7: {"page_role": "core_content", "term_ids": ["web_scraping"], "evidence_units": [
        U("crawling_p7_u01", "definition", "text_and_visual", "우리가 필요한 정보만 가져오는 것이 바로 스크래핑", "스크래핑은 원본 자료에서 필요한 정보만 선택해 추출한다.", ["web_scraping"]),
    ]},
    8: {"page_role": "core_content", "term_ids": ["web_crawling", "web_scraping"], "evidence_units": [
        U("crawling_p8_u01", "comparison", "text", "웹 크롤링: 웹 페이지 및 링크를 따라가며 콘텐츠를 자동 수집 / 웹 스크래핑: 여러 소스에서 필요한 정보만 추출", "크롤링은 폭넓은 탐색·수집, 스크래핑은 필요 정보의 선택적 추출에 초점을 둔다.", ["web_crawling", "web_scraping"]),
        U("crawling_p8_u02", "comparison", "text", "크롤링은 중복 제거 필수·서버 부하와 리소스가 큼 / 스크래핑은 적은 리소스로 원하는 정보 수집, 범위 제한", "폭넓은 크롤링은 중복·부하·자원 문제가 크고, 선택적 스크래핑은 자원을 줄이는 대신 범위가 제한된다.", ["web_crawling", "web_scraping"]),
        U("crawling_p8_u03", "warning", "text", "실질적으로는 용어를 많이 혼용, 하지만 원리 차이는 알 필요가 있다", "현업에서 용어가 혼용되더라도 개념적 차이를 구분한다.", ["web_crawling", "web_scraping"]),
    ]},
    9: {"page_role": "core_content", "term_ids": ["html", "markup_language", "tag"], "evidence_units": [
        U("crawling_p9_u01", "definition", "text", "HTML(HyperText Markup Language): 웹 페이지를 위한 마크업 언어", "HTML은 태그로 웹 문서의 구조를 표현하는 마크업 언어다.", ["html", "markup_language", "tag"]),
        U("crawling_p9_u02", "relation", "text", "웹 브라우저는 HTML로 정의된 콘텐츠를 시각적으로 렌더링", "브라우저는 HTML이 표현한 구조와 콘텐츠를 화면에 렌더링한다.", ["html"]),
    ]},
    10: {"page_role": "core_content", "term_ids": ["tag", "element"], "evidence_units": [
        U("crawling_p10_u01", "definition", "text_and_visual", "시작 태그 <태그이름>, 종료 태그 </태그이름>, 두 태그 사이에 내용", "일반적인 HTML 요소는 시작 태그와 종료 태그 사이에 내용을 둔다.", ["tag", "element"]),
    ]},
    11: {"page_role": "core_content", "term_ids": ["attribute", "element", "tag"], "evidence_units": [
        U("crawling_p11_u01", "definition", "text_and_visual", "<태그이름 속성이름=‘속성값’>; 엘리먼트에 추가적인 정보", "속성은 시작 태그에 이름과 값 형태로 적어 엘리먼트에 추가 정보를 제공한다.", ["attribute", "element", "tag"]),
    ]},
    12: {"page_role": "core_content", "term_ids": ["element", "tag", "attribute"], "evidence_units": [
        U("crawling_p12_u01", "definition", "text_and_visual", "엘리먼트: 스타트 태그부터 끝마침 태그까지를 모두 포함; HTML은 엘리먼트들의 집합", "HTML 엘리먼트는 시작 태그부터 종료 태그까지 속성과 내용을 포함한 전체 객체다.", ["element", "tag", "attribute"]),
    ]},
    13: {"page_role": "example", "term_ids": ["html", "doctype", "element", "tag"], "evidence_units": [
        U("crawling_p13_u01", "example", "text_and_visual", "!DOCTYPE는 문서종류의 정의; <html>은 웹페이지 전체, <body>는 보이는 내용, <h1>은 제목, <p>는 문단", "DOCTYPE은 문서 형식을 선언하고 html·body·h1·p 엘리먼트가 문서의 전체·가시 내용·제목·문단 구조를 만든다.", ["html", "doctype", "element", "tag"]),
    ]},
    14: {"page_role": "core_content", "term_ids": ["http_request", "get", "post", "status_code", "requests", "selenium"], "evidence_units": [
        U("crawling_p14_u01", "procedure", "text_and_visual", "GET 요청: 페이지 열람, 검색 등 읽기 작업; requests.get", "GET은 주로 읽기·조회에 사용하며 Python requests.get으로 보낼 수 있다.", ["get", "requests", "http_request"]),
        U("crawling_p14_u02", "comparison", "text", "POST 요청: 로그인, 데이터 제출 등 쓰기 작업; Selenium으로 주로 대응", "POST는 로그인·데이터 제출 같은 상호작용에 연결되며 강의에서는 Selenium 대응을 소개한다.", ["post", "selenium", "http_request"]),
        U("crawling_p14_u03", "interpretation", "text", "응답코드 200: 정상, 403/404: 차단·오류 체크 중요", "200은 정상 응답이고 403·40 접근 금지, 404는 요청 자원을 찾을 수 없음을 뜻하므로 상태 코드를 확인한다.", ["status_code"]),
    ]},
    15: {"page_role": "section_divider", "term_ids": [], "evidence_units": []},
    16: {"page_role": "core_content", "term_ids": ["beautifulsoup", "parsing", "dom_tree", "requests", "urllib", "dynamic_page"], "evidence_units": [
        U("crawling_p16_u01", "procedure", "text", "requests나 urllib을 이용해 html을 다운받고, BeautifulSoup으로 데이터를 추출", "requests·urllib로 HTML을 가져온 다음 BeautifulSoup으로 파싱하고 필요 요소를 추출한다.", ["requests", "urllib", "beautifulsoup", "parsing"]),
        U("crawling_p16_u02", "definition", "text", "HTML과 XML 문서를 parsing하기 위한 패키지; 분석 트리 생성", "BeautifulSoup은 HTML·XML을 탐색 가능한 트리로 파싱한다.", ["beautifulsoup", "parsing", "dom_tree"]),
        U("crawling_p16_u03", "comparison", "text", "장점: 간단한 코드, 빠른 속도 / 단점: 동적 페이지 크롤링이 까다로움", "BeautifulSoup 방식은 간단하고 빠르지만 자바스크립트 등으로 동적 생성되는 콘텐츠 처리에 제약이 있다.", ["beautifulsoup", "dynamic_page"]),
    ]},
    17: {"page_role": "core_content", "term_ids": ["selenium", "dynamic_page"], "evidence_units": [
        U("crawling_p17_u01", "definition", "text", "웹 브라우저를 이용하여 키보드와 마우스로 수행하는 동작을 자동화", "Selenium은 실제 브라우저의 키보드·마우스 상호작용을 자동화한다.", ["selenium"]),
        U("crawling_p17_u02", "procedure", "text", "버튼 클릭, 스크롤 등의 조작이 가능; 동적으로 활용하기 유리", "동적 콘텐츠나 버튼·스크롤 상호작용이 필요하면 Selenium이 유리하다.", ["selenium", "dynamic_page"]),
        U("crawling_p17_u03", "comparison", "text", "장점: 버튼 클릭, 스크롤 / 단점: 복잡한 코드, 느린 속도", "Selenium은 상호작용 범위가 넓지만 코드가 복잡하고 브라우저 구동 비용으로 느릴 수 있다.", ["selenium"]),
    ]},
    18: {"page_role": "core_content", "term_ids": ["robots_txt", "rate_limiting", "user_agent", "captcha"], "evidence_units": [
        U("crawling_p18_u01", "procedure", "text", "robots.txt 확인: 사이트가 크롤링을 허용하는지 여부를 명시", "수집 전 robots.txt를 확인해 자동 접근 허용 범위를 살핀다.", ["robots_txt"]),
        U("crawling_p18_u02", "warning", "text", "요청 간 시간 간격: time.sleep(1~3초) 권장; 너무 많은 페이지를 짧은 시간에 긁지 않기", "요청 간격을 두고 대량 요청을 자제해 사이트 부하를 줄인다.", ["rate_limiting"]),
        U("crawling_p18_u03", "warning", "text", "개인정보, 유료 서비스 크롤링 금지; 학습, 비영리 목적으로 제한적 사용 권장", "개인정보·유료 콘텐츠·약관·법적 제약을 확인하고 학습·비영리에서도 필요 범위만 수집한다.", []),
        U("crawling_p18_u04", "warning", "text", "User-Agent 설정도 필요 시 고려; CAPTCHA 같은 보안 기능이 있는 사이트는 피하는 것을 추천", "필요하면 User-Agent를 정상적으로 설정하고 CAPTCHA 등 접근 제한을 우회하려 하지 않는다.", ["user_agent", "captcha"]),
    ]},
    19: {"page_role": "section_divider", "term_ids": [], "evidence_units": []},
    20: {"page_role": "section_divider", "term_ids": [], "evidence_units": []},
    21: {"page_role": "closing", "term_ids": [], "evidence_units": []},
}


CLAIM_LINKS = {
    "crawling.automation_need": (["crawling_p4_u01"], ["web_crawling"]),
    "crawling.data_acquisition": (["crawling_p5_u01", "crawling_p5_u02"], ["web_crawling"]),
    "crawling.multiple_services": (["crawling_p6_u01"], ["web_crawling"]),
    "crawling.link_traversal": (["crawling_p6_u01", "crawling_p8_u01"], ["web_crawling"]),
    "crawling.scraping_definition": (["crawling_p7_u01"], ["web_scraping"]),
    "crawling.scope_difference": (["crawling_p8_u01"], ["web_crawling", "web_scraping"]),
    "crawling.resource_difference": (["crawling_p8_u02"], ["web_crawling", "web_scraping"]),
    "crawling.terms_mixed": (["crawling_p8_u03"], ["web_crawling", "web_scraping"]),
    "crawling.html_role": (["crawling_p9_u01"], ["html", "markup_language", "tag"]),
    "crawling.browser_rendering": (["crawling_p9_u02"], ["html"]),
    "crawling.tag_pair": (["crawling_p10_u01"], ["tag", "element"]),
    "crawling.attribute": (["crawling_p11_u01"], ["attribute", "tag", "element"]),
    "crawling.element_hierarchy": (["crawling_p12_u01"], ["element", "tag", "attribute"]),
    "crawling.nested_tree": (["crawling_p12_u01", "crawling_p13_u01"], ["html", "element", "tag"]),
    "crawling.get_request": (["crawling_p14_u01"], ["get", "requests", "http_request"]),
    "crawling.post_request": (["crawling_p14_u02"], ["post", "selenium", "http_request"]),
    "crawling.status_codes": (["crawling_p14_u03"], ["status_code"]),
    "crawling.download_then_parse": (["crawling_p16_u01"], ["requests", "urllib", "beautifulsoup", "parsing"]),
    "crawling.bs_tree": (["crawling_p16_u02"], ["beautifulsoup", "parsing", "dom_tree"]),
    "crawling.bs_tradeoff": (["crawling_p16_u03"], ["beautifulsoup", "dynamic_page"]),
    "crawling.selenium_role": (["crawling_p17_u01"], ["selenium"]),
    "crawling.dynamic_pages": (["crawling_p17_u02"], ["selenium", "dynamic_page"]),
    "crawling.selenium_cost": (["crawling_p17_u03"], ["selenium"]),
    "crawling.robots": (["crawling_p18_u01"], ["robots_txt"]),
    "crawling.rate_limit": (["crawling_p18_u02"], ["rate_limiting"]),
    "crawling.legal_privacy": (["crawling_p18_u03"], []),
    "crawling.user_agent_captcha": (["crawling_p18_u04"], ["user_agent", "captcha"]),
}


REQUIRED_ELEMENTS = {
    "crawling.automation_need": ["대량의 웹 정보를 일일이 찾는 비용", "필요 정보를 자동으로 수집하는 목적"],
    "crawling.data_acquisition": ["크롤링이 웹을 돌아다니며 데이터를 수집한다는 정의", "분석 데이터가 없을 때 웹에서 필요 데이터를 얻는 목적"],
    "crawling.multiple_services": ["여러 웹 페이지나 서비스를 돌아다닌다는 범위"],
    "crawling.link_traversal": ["페이지나 링크를 따라 폭넓게 수집하는 원리"],
    "crawling.scraping_definition": ["전체 원본에서 필요한 정보만 선택해 추출한다는 정의"],
    "crawling.scope_difference": ["크롤링의 폭넓은 자동 수집", "스크래핑의 필요 정보 선택 추출"],
    "crawling.resource_difference": ["크롤링의 중복·부하·자원 비용", "스크래핑의 적은 자원과 제한된 범위"],
    "crawling.terms_mixed": ["용어가 혼용되더라도 원리상 차이가 있다는 점"],
    "crawling.html_role": ["HTML이 웹 문서의 구조를 표현하는 마크업 언어라는 정의"],
    "crawling.browser_rendering": ["브라우저가 HTML 콘텐츠를 시각적으로 렌더링한다는 역할"],
    "crawling.tag_pair": ["시작 태그와 종료 태그", "두 태그 사이의 내용"],
    "crawling.attribute": ["시작 태그의 속성 이름·값 형태", "엘리먼트에 추가 정보를 제공한다는 역할"],
    "crawling.element_hierarchy": ["엘리먼트가 시작·종료 태그와 속성·내용을 포함한 전체 객체라는 정의"],
    "crawling.nested_tree": ["HTML 문서가 엘리먼트들로 구성된다는 점", "html·body·h1·p 등의 문서 구조 예시"],
    "crawling.get_request": ["GET이 페이지 열람·검색 등 읽기 요청이라는 점", "requests.get 사용"],
    "crawling.post_request": ["POST가 로그인·데이터 제출과 같은 요청에 연결된다는 점"],
    "crawling.status_codes": ["200은 정상", "403·40 접근 금지와 404는 자원을 찾을 수 없음을 확인해야 한다는 점"],
    "crawling.download_then_parse": ["requests·urllib로 HTML을 가져옴", "BeautifulSoup으로 파싱하고 필요 데이터를 추출함"],
    "crawling.bs_tree": ["BeautifulSoup이 HTML·XML을 탐색 가능한 분석 트리로 만든다는 역할"],
    "crawling.bs_tradeoff": ["간단하고 빠른 장점", "동적 페이지 처리의 제약"],
    "crawling.selenium_role": ["Selenium이 실제 브라우저의 키보드·마우스 동작을 자동화한다는 역할"],
    "crawling.dynamic_pages": ["동적 콘텐츠나 버튼 클릭·스크롤이 필요할 때 Selenium이 유리함"],
    "crawling.selenium_cost": ["복잡한 코드", "브라우저 구동으로 인한 느린 속도"],
    "crawling.robots": ["수집 전 robots.txt에서 허용 범위를 확인"],
    "crawling.rate_limit": ["요청 간격을 두고 짧은 시간의 대량 요청을 피함", "사이트 부하를 줄이는 목적"],
    "crawling.legal_privacy": ["개인정보·유료 서비스·법적 제약 확인", "학습·비영리라도 필요 범위로 제한"],
    "crawling.user_agent_captcha": ["필요 시 User-Agent 설정", "CAPTCHA 같은 보안 제한을 우회하지 않음"],
}


CRITICAL_ERRORS = {
    "crawling.scraping_definition": ["스크래핑을 링크를 따라 웹 전체를 폭넓게 탐색하는 것으로만 설명"],
    "crawling.scope_difference": ["크롤링과 스크래핑의 폭넓은 수집과 선택 추출 차이를 뒤바꿔 설명"],
    "crawling.html_role": ["HTML을 프로그래밍 로직을 수행하는 일반 프로그래밍 언어로 설명"],
    "crawling.tag_pair": ["종료 태그가 시작 태그와 동일하게 슬래시 없이 표현된다고 설명"],
    "crawling.attribute": ["속성이 태그 밖의 별도 엘리먼트라고 설명"],
    "crawling.get_request": ["GET을 로그인·데이터 제출 전용 쓰기 요청으로 설명"],
    "crawling.post_request": ["POST를 페이지 조회 전용이라고 설명"],
    "crawling.status_codes": ["403과 404를 모두 정상 응답으로 설명"],
    "crawling.bs_tradeoff": ["BeautifulSoup이 실제 브라우저 상호작용을 자동화한다고 설명"],
    "crawling.selenium_role": ["Selenium이 HTML 파싱만 수행하고 브라우저를 제어하지 않는다고 설명"],
    "crawling.robots": ["robots.txt 확인 없이 모든 경로를 자동 수집해도 된다고 설명"],
    "crawling.rate_limit": ["요청을 끊임없이 최대 속도로 보내는 것이 올바르다고 설명"],
    "crawling.legal_privacy": ["비영리·학습 목적이면 개인정보나 유료 콘텐츠도 무제한 수집해도 된다고 설명"],
    "crawling.user_agent_captcha": ["CAPTCHA나 보안 제한을 우회하는 방법을 권장"],
}


def apply_evaluation_data(processed_path: Path = PROCESSED_PATH,
                          rubric_path: Path = RUBRIC_PATH) -> None:
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id") != "crawling":
        raise ValueError("크롤링 processed 파일이 아닙니다.")
    pages = {chunk["page"]: chunk for chunk in payload["chunks"]}
    if set(pages) != set(PAGE_DATA):
        raise ValueError("크롤링 PDF의 1~21쪽이 모두 존재해야 합니다.")
    payload["schema_version"] = "2.1.0"
    payload["terminology"] = TERMINOLOGY
    for page, metadata in PAGE_DATA.items():
        pages[page].update(metadata)
        pages[page].setdefault("source_issues", [])
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    unit_lookup = {u["unit_id"]: (chunk, u) for chunk in payload["chunks"] for u in chunk["evidence_units"]}
    rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    rubric["schema_version"] = "2.2.0"
    claims = {claim["claim_id"]: claim for obj in rubric["top_level_objectives"]
              for sub in obj["sub_objectives"] for claim in sub["claims"]}
    if set(claims) != set(CLAIM_LINKS) or set(claims) != set(REQUIRED_ELEMENTS):
        raise ValueError("크롤링 claim·evidence·판정 기준 목록이 일치하지 않습니다.")
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
    rubric["excluded_source_claims"] = []
    rubric_path.write_text(json.dumps(rubric, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    apply_evaluation_data()
    print(f"updated: {PROCESSED_PATH.relative_to(ROOT)}")
    print(f"updated: {RUBRIC_PATH.relative_to(ROOT)}")
