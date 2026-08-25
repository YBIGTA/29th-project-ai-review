from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "python_environment.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "python_environment.json"


def term(term_id: str, ko: str, en: str = "", *, abbreviations=None, aliases=None,
         symbols=None, not_equivalent_to=None) -> dict[str, Any]:
    return {"term_id": term_id, "canonical_ko": ko, "canonical_en": en,
            "abbreviations": abbreviations or [], "accepted_aliases": aliases or [],
            "symbols": symbols or [], "not_equivalent_to": not_equivalent_to or []}


TERMINOLOGY = [
    term("development_environment", "개발환경", "development environment"),
    term("colab", "Google Colab", "Google Colaboratory", aliases=["코랩"]),
    term("vscode", "Visual Studio Code", "Visual Studio Code", abbreviations=["VS Code"], aliases=["비주얼 스튜디오 코드", "브이에스코드"]),
    term("python_interpreter", "Python 인터프리터", "Python interpreter"),
    term("conda", "Conda", "Conda", aliases=["콘다"]),
    term("miniconda", "Miniconda", "Miniconda", aliases=["미니콘다"]),
    term("anaconda", "Anaconda", "Anaconda", aliases=["아나콘다"]),
    term("package_manager", "패키지 관리자", "package manager"),
    term("dependency", "의존성", "dependency", aliases=["dependency management", "디펜던시"]),
    term("virtual_environment", "가상환경", "virtual environment", abbreviations=["venv env"], aliases=["virtual env"]),
    term("venv", "venv", "venv", aliases=["파이썬 venv"]),
    term("activation", "활성화", "activation", aliases=["activate"]),
    term("deactivation", "비활성화", "deactivation", aliases=["deactivate"]),
    term("pip", "pip", "pip"), term("requirements", "requirements.txt", "requirements.txt"),
    term("pip_freeze", "pip freeze", "pip freeze"), term("environment_yml", "environment.yml", "environment.yml", aliases=["environment.yaml"]),
    term("conda_env", "Conda 환경", "Conda environment"),
    term("package_conflict", "패키지 충돌", "package conflict", aliases=["의존성 충돌"]),
    term("reproducibility", "재현성", "reproducibility", aliases=["환경 재현"]),
    term("pep8", "PEP 8", "PEP 8", aliases=["파이썬 스타일 가이드"]),
    term("identifier", "식별자", "identifier"), term("keyword", "예약어", "keyword", aliases=["키워드"]),
    term("snake_case", "스네이크 케이스", "snake_case"), term("camel_case", "카멜 케이스", "CamelCase", aliases=["PascalCase"]),
    term("indentation", "들여쓰기", "indentation"),
    term("dynamic_typing", "동적 타이핑", "dynamic typing", aliases=["동적 타입"]),
    term("type_hint", "타입 힌트", "type hint", aliases=["typing", "type annotation", "타입 어노테이션"]),
    term("callable", "Callable", "Callable"), term("typeddict", "TypedDict", "TypedDict"),
    term("docstring", "독스트링", "docstring", aliases=["문서 문자열"]),
    term("class", "클래스", "class"), term("object", "객체", "object"), term("instance", "인스턴스", "instance"),
    term("attribute", "속성", "attribute"), term("class_attribute", "클래스 속성", "class attribute"),
    term("instance_attribute", "인스턴스 속성", "instance attribute"), term("constructor", "생성자", "constructor", aliases=["__init__"]),
    term("method", "메서드", "method"), term("instance_method", "인스턴스 메서드", "instance method"),
    term("class_method", "클래스 메서드", "class method", aliases=["classmethod"]),
    term("static_method", "정적 메서드", "static method", aliases=["staticmethod"]),
    term("self", "self", "self"), term("cls", "cls", "cls"),
    term("oop", "객체 지향 프로그래밍", "object-oriented programming", abbreviations=["OOP"]),
    term("encapsulation", "캡슐화", "encapsulation"), term("inheritance", "상속", "inheritance"),
    term("polymorphism", "다형성", "polymorphism"), term("abstraction", "추상화", "abstraction"),
    term("override", "오버라이딩", "method overriding", aliases=["override"]), term("super", "super", "super"),
]


P: dict[int, tuple[str, list[str], str, str]] = {
    1:("Python·개발환경 강의 표지",["Python","개발환경"],"Python과 개발환경 강의의 표지이다.","cover"),
    2:("강의 목차",["Environment","Virtual Environment","Python Guidelines"],"개발환경, 가상환경, Python 가이드 순으로 구성된다.","table_of_contents"),
    3:("개발환경",["Environment"],"개발환경 섹션의 시작 페이지이다.","section_divider"),
    4:("개발환경 선택",["개발환경","trade-off"],"Python 개발환경에는 하나의 정답이 없으며 상황에 따라 장단점이 다르다.","core_content"),
    5:("Google Colab",["Google Colab","클라우드 환경"],"Colab은 계정만 있으면 준비가 쉽지만 파일 기반 프로그램 개발에는 유연성이 부족할 수 있다.","core_content"),
    6:("Anaconda 환경",["Anaconda","로컬 개발","팀 프로젝트"],"Anaconda는 로컬 파일 관리와 팀의 공통 개발환경 구성에 유용하다.","core_content"),
    7:("Conda·Miniconda·Anaconda",["Conda","Miniconda","Anaconda","의존성"],"Conda는 패키지·환경 관리 엔진, Miniconda는 최소 구성, Anaconda는 데이터 과학 패키지를 포함한 배포판이다.","core_content"),
    8:("VS Code",["VS Code","터미널","Git","Python extension","debugging"],"VS Code는 편집·실행·디버깅과 터미널, Git, 확장을 통합한다.","core_content"),
    9:("Anaconda 다운로드",["Anaconda","설치"],"Anaconda 사이트에서 운영체제에 맞는 설치 파일을 찾는 절차이다.","procedure"),
    10:("운영체제별 Anaconda",["Anaconda","OS"],"사용 중인 운영체제에 맞는 Anaconda 설치 파일을 선택한다.","procedure"),
    11:("Anaconda 설치",["Anaconda","recommended"],"권장 설정을 중심으로 Anaconda 설치를 진행한다.","procedure"),
    12:("Anaconda 설치 옵션",["PATH","default Python","cache"],"바로가기, PATH, 기본 Python 등록, 캐시 정리 설치 옵션의 의미를 설명한다.","supplementary_reference"),
    13:("VS Code 다운로드",["VS Code","OS"],"운영체제에 맞는 VS Code를 다운로드한다.","procedure"),
    14:("VS Code 설치 옵션",["VS Code","code command","file association"],"컨텍스트 메뉴, .py 연결, 터미널 code 명령 옵션을 설정한다.","procedure"),
    15:("Python 확장 설치",["VS Code","Python extension"],"VS Code에서 Python 확장을 설치한다.","procedure"),
    16:("Python 인터프리터 선택",["Python interpreter","Command Palette"],"Python: Select Interpreter로 실행에 사용할 Python 환경을 선택한다.","procedure"),
    17:("Anaconda base 선택",["Anaconda","base","interpreter"],"Anaconda가 설치한 base Python을 VS Code 인터프리터로 선택하는 예다.","example"),
    18:("Conda 기본 명령",["conda","activate","env list","create"],"Conda 버전·환경 목록을 확인하고 Python 버전을 지정해 환경을 생성·활성화한다.","procedure"),
    19:("Anaconda 명령어 표",["conda env","export","environment.yml"],"Conda 환경의 생성·삭제·활성화·복제·내보내기·재생성을 위한 명령을 정리한다.","supplementary_reference"),
    20:("macOS 설치 가이드",["macOS","Anaconda","VS Code"],"macOS용 외부 설치 가이드 링크를 제공한다.","supplementary_reference"),
    21:("가상환경",["Virtual Environment"],"가상환경 섹션의 시작 페이지이다.","section_divider"),
    22:("가상환경의 필요성",["패키지 버전","의존성 충돌","재현성"],"프로젝트별 패키지 버전 충돌과 팀·시간 간 실행 차이를 막기 위해 독립 환경이 필요하다.","core_content"),
    23:("가상환경 정의",["virtual environment","독립성"],"가상환경은 독립적인 프로젝트를 위한 개별 실행 공간이다.","core_content"),
    24:("venv 정의와 명령",["venv","activate"],"venv는 Python 표준 가상환경 도구이며 환경 생성과 운영체제별 활성화 명령을 제공한다.","core_content"),
    25:("venv 생성 위치",["venv","project directory"],"명령을 실행한 디렉터리에 venv 폴더가 생성되며 프로젝트별로 둘 수 있다.","example"),
    26:("venv 활성화와 설치",["activate","pip","package"],"venv를 활성화한 뒤 pip로 필요한 패키지를 환경 안에 설치한다.","procedure"),
    27:("requirements.txt 생성",["pip freeze","requirements.txt","deactivate"],"pip freeze로 설치 목록을 requirements.txt에 저장하고 deactivate로 환경을 빠져나온다.","procedure"),
    28:("requirements.txt 재현",["pip install -r","requirements.txt"],"새 venv에서 requirements.txt를 이용해 동일한 패키지 목록을 설치한다.","procedure"),
    29:("venv 특징",["venv","격리","requirements.txt"],"venv는 가볍고 Python 프로젝트별 의존성을 격리하며 requirements로 패키지 목록을 공유한다.","core_content"),
    30:("Conda 환경 생성",["Conda","create","activate","deactivate"],"Conda는 Python 버전을 지정해 환경을 만들고 활성화·비활성화·삭제할 수 있다.","core_content"),
    31:("Conda 환경 생성 실습",["conda create","Python version"],"이름과 Python 버전을 지정해 Conda 환경을 생성한다.","example"),
    32:("venv와 Conda 구성 차이",["venv","Conda","system dependency"],"venv는 최소 Python 환경이고 Conda는 더 포괄적인 패키지와 시스템 의존성을 관리할 수 있다.","core_content"),
    33:("Conda 환경과 패키지",["conda env list","conda install"],"환경 목록을 확인하고 활성화한 Conda 환경에 패키지를 설치한다.","procedure"),
    34:("Conda 안의 pip",["conda install","pip install","conflict"],"Conda 환경에서 pip도 쓸 수 있지만 충돌을 줄이려면 Conda 패키지를 우선한다.","core_content"),
    35:("Conda 환경 내보내기",["conda env export","environment.yml","remove"],"환경을 YAML로 내보내고 비활성화·삭제하는 흐름이다.","procedure"),
    36:("Conda 환경 재생성",["environment.yml","conda env create"],"environment.yml로 다른 이름의 동일 환경을 재생성한다.","procedure"),
    37:("Conda 특징",["platform independence","dependency","environment.yml"],"Conda는 다양한 언어·복잡한 의존성을 관리하고 YAML로 환경을 복제한다.","core_content"),
    38:("venv와 Conda 비교",["venv","Conda","use case"],"venv는 가벼운 Python 전용 프로젝트에, Conda는 데이터 과학과 복잡한 다언어 환경에 적합하다.","core_content"),
    39:("Python Guidelines",["Python Guidelines"],"Python 가이드 섹션의 시작 페이지이다.","section_divider"),
    40:("좋은 Python 코드",["readability","maintainability"],"간단한 문법을 넘어 읽기 쉽고 유지보수하기 좋은 Python 코드를 고민한다.","core_content"),
    41:("식별자 명명 규칙",["identifier","keyword"],"식별자는 예약어를 피하고 숫자·공백·특수문자 규칙을 지키며 의미 있는 이름을 사용한다.","core_content"),
    42:("Python 예약어",["keyword","keyword.kwlist"],"Python이 문법 용도로 예약한 keyword는 식별자로 사용할 수 없다.","core_content"),
    43:("Snake case와 Camel case",["snake_case","CamelCase"],"단어 경계를 밑줄 또는 대문자로 표현해 의미 있는 식별자를 만든다.","core_content"),
    44:("PEP 8 들여쓰기",["PEP 8","indentation","spaces"],"PEP 8은 Python 들여쓰기에 스페이스 4칸을 권장한다.","core_content"),
    45:("Typing의 목적",["dynamic typing","type hint","readability"],"타입 힌트는 동적 Python 코드의 자료형 의도를 표시해 안정성과 가독성을 높인다.","core_content"),
    46:("Typing의 이점",["parameter","return type","IDE"],"매개변수와 반환형을 표시하면 IDE와 협업자가 함수 계약을 쉽게 이해한다.","core_content"),
    47:("Typing 예제",["List","Tuple","Dict","TypedDict","Any"],"컨테이너와 구조화된 딕셔너리의 타입을 구체적으로 표현한다.","example"),
    48:("Callable 타입",["Callable","function type"],"함수를 인자로 받을 때 Callable로 인자와 반환 타입을 표현한다.","example"),
    49:("Docstring 소개",["docstring","documentation"],"함수·클래스·모듈을 코드 내부에서 문서화하는 Docstring을 소개한다.","core_content"),
    50:("Docstring의 기능",["docstring","__doc__","IDE hover"],"Docstring은 입출력과 역할을 설명하며 __doc__ 조회와 IDE hover 문서에 쓰인다.","core_content"),
    51:("Docstring 템플릿",["Args","Returns","Attributes","Methods"],"함수와 클래스 Docstring에 설명, 인자, 반환, 속성, 메서드를 구조화하는 템플릿이다.","example"),
    52:("클래스의 역할",["class","object","attribute","method"],"클래스는 객체의 속성과 동작을 묶는 설계도이며 재사용·유지보수를 돕는다.","core_content"),
    53:("클래스·인스턴스 속성",["class attribute","instance attribute","__init__"],"클래스 속성은 모든 인스턴스가 공유하고 인스턴스 속성은 객체별 상태를 저장한다.","core_content"),
    54:("세 가지 메서드",["instance method","class method","static method","self","cls"],"인스턴스·클래스·정적 메서드는 받는 참조와 사용하는 상태가 다르다.","core_content"),
    55:("클래스 구성 예제",["class","__init__","classmethod","staticmethod"],"YbigtaMember 예제로 속성, 생성자와 세 종류 메서드를 연결한다.","example"),
    56:("클래스 호출 예제",["instance","method call"],"인스턴스를 만들고 인스턴스·클래스·정적 메서드 결과를 확인한다.","example"),
    57:("Python 학습 자료",["official docs","Real Python","fact check"],"공식 문서와 튜토리얼을 사용하고 비공식 자료는 사실 검증한다.","supplementary_reference"),
    58:("객체 지향 프로그래밍",["OOP","object","reuse","maintainability"],"OOP는 객체의 속성과 행동으로 프로그램을 설계해 재사용성·확장성·유지보수성을 높인다.","core_content"),
    59:("OOP 4대 원칙",["encapsulation","inheritance","polymorphism","abstraction"],"캡슐화·상속·다형성·추상화의 의미를 정리한다.","core_content"),
    60:("상속과 오버라이딩 예제",["inheritance","super","override"],"자식 클래스가 부모를 상속하고 super로 초기화하며 메서드를 오버라이딩한다.","example"),
    61:("강의 마무리",["Python"],"Python·개발환경 강의의 종료 페이지이다.","closing"),
}


def curated_page(topic: str, concepts: list[str], content: str, role: str) -> list[dict[str, object]]:
    visual = content if role not in {"cover", "table_of_contents", "section_divider", "closing"} else f"{topic} 페이지이다."
    return [{"topic": topic, "concepts": concepts, "visual_description": visual, "content": content}]


CURATION = {page: curated_page(*info) for page, info in P.items()}


def unit(uid: str, page: int, kind: str, excerpt: str, explanation: str,
         terms: list[str], source_type: str = "text") -> dict[str, Any]:
    return {"unit_id": uid, "page": page, "type": kind, "source_type": source_type,
            "source_excerpt": excerpt, "normalized_explanation": explanation,
            "source_status": "verified", "term_ids": terms}


U = unit
UNITS = [
    U("py_p4_u01",4,"interpretation","정답은 없지만 상황에 따라 장단점이 있다","개발환경은 목적과 제약에 맞춰 선택한다.",["development_environment"]),
    U("py_p5_u01",5,"comparison","구글 계정만 있으면 준비할 게 없다 / 코드 파일을 다루기엔 유연성이 아쉽다","Colab은 접근이 쉽지만 본격적인 파일 기반 개발에는 제약이 있다.",["colab","development_environment"]),
    U("py_p6_u01",6,"interpretation","아나콘다: 로컬에서 파일 관리에 유용 / 팀프로젝트에도 공통의 환경을 조성","로컬 프로젝트와 팀 환경 구성에 Anaconda를 활용할 수 있다.",["anaconda","development_environment","reproducibility"]),
    U("py_p7_u01",7,"comparison","Conda 핵심 엔진 / Miniconda 최소 버전 / Anaconda 데이터 사이언스 패키지 사전 탑재","Conda·Miniconda·Anaconda는 엔진과 배포 범위가 다르다.",["conda","miniconda","anaconda","package_manager","dependency"]),
    U("py_p8_u01",8,"interpretation","터미널 내장, Git 내장, Python extension, 코드 작성·실행·디버깅","VS Code는 개발 작업을 통합한다.",["vscode","python_interpreter"]),
    U("py_p16_u01",16,"procedure","Python: Select Interpreter","VS Code에서 실행할 Python 환경을 선택한다.",["vscode","python_interpreter"]),
    U("py_p22_u01",22,"relation","프로젝트마다 필요한 패키지 버전이 다름 / 팀원 환경 차이 / 업데이트 후 오류","격리는 버전 충돌과 재현성 문제를 줄인다.",["virtual_environment","dependency","package_conflict","reproducibility"]),
    U("py_p23_u01",23,"definition","독립적인 프로젝트를 위한 개별적인 공간","가상환경은 프로젝트별 독립 실행 공간이다.",["virtual_environment"]),
    U("py_p24_u01",24,"definition","Venv는 Python을 위한 가상 환경 생성 도구이며 표준 라이브러리에 포함","venv는 Python 표준 가상환경 도구다.",["venv","virtual_environment"]),
    U("py_p24_u02",24,"procedure","python3 -m venv 환경이름 / source 환경이름/bin/activate / 환경이름\\Scripts\\activate","venv는 생성 후 운영체제에 맞는 스크립트로 활성화한다.",["venv","activation"]),
    U("py_p26_u01",26,"procedure","source ybigta/bin/activate / pip install numpy / pip install pandas","활성화된 venv 안에 pip로 패키지를 설치한다.",["venv","activation","pip"]),
    U("py_p27_u01",27,"procedure","pip freeze > requirements.txt / deactivate","설치 목록을 파일로 기록하고 환경을 비활성화한다.",["pip_freeze","requirements","deactivation"]),
    U("py_p28_u01",28,"procedure","pip install -r requirements.txt","새 환경에 기록된 패키지 목록을 설치한다.",["pip","requirements","reproducibility"]),
    U("py_p29_u01",29,"comparison","경량성과 편리성 / 프로젝트별 독립성 / 시스템 Python 보호 / 패키지 버전 관리","venv는 가볍고 Python 의존성을 프로젝트별로 격리한다.",["venv","virtual_environment","requirements"]),
    U("py_p30_u01",30,"definition","Conda는 오픈소스 패키지 관리 시스템이자 환경 관리 시스템","Conda는 환경과 패키지를 함께 관리한다.",["conda","conda_env","package_manager"]),
    U("py_p30_u02",30,"procedure","conda create --name 환경 python=버전 / conda activate / conda deactivate","Conda 환경을 생성·활성화·비활성화한다.",["conda","activation","deactivation"]),
    U("py_p32_u01",32,"comparison","venv는 최소한 구성 / conda는 필요한 모든 패키지를 포함하며 운영체제와 독립적이고 포괄적","venv와 Conda는 관리 범위와 무게가 다르다.",["venv","conda","dependency"]),
    U("py_p34_u01",34,"interpretation","Conda 환경에서도 pip 설치 가능하지만 종속성 충돌 가능성 / conda 패키지를 먼저 설치","Conda와 pip를 섞을 때는 충돌을 줄이는 설치 순서를 고려한다.",["conda","pip","package_conflict"]),
    U("py_p35_u01",35,"procedure","conda env export > environment.yml / conda deactivate / conda env remove","Conda 환경을 YAML로 내보내고 제거할 수 있다.",["conda","environment_yml","deactivation"]),
    U("py_p36_u01",36,"procedure","conda env create -n 새환경 -f environment.yml","YAML로 환경을 재생성한다.",["conda","environment_yml","reproducibility"]),
    U("py_p38_u01",38,"comparison","Conda: 다양한 언어·복잡한 의존성 / Venv: 파이썬 전용·경량","프로젝트 복잡도와 언어 범위에 따라 도구를 선택한다.",["conda","venv","dependency"]),
    U("py_p41_u01",41,"procedure","Keyword 사용 불가 / 특수 문자는 언더바만 / 숫자로 시작하지 않음 / 공백 불가 / 가급적 의미 있는 이름","Python 식별자는 문법 규칙과 의미 있는 명명을 지켜야 한다.",["identifier","keyword"]),
    U("py_p43_u01",43,"comparison","Snake case는 단어 사이에 언더바 / Camel case는 단어 첫 글자를 대문자","단어 경계 표기 방식이 다르다.",["snake_case","camel_case","identifier"]),
    U("py_p44_u01",44,"procedure","Python은 스페이스 4개를 들여쓰기에 권장하며 이는 PEP 8 스타일 가이드 때문","Python 들여쓰기는 PEP 8의 4칸 권장을 따른다.",["pep8","indentation"]),
    U("py_p45_u01",45,"definition","typing이란 변수와 함수의 자료형을 명시해 코드의 안정성과 가독성을 높이는 방법","타입 힌트는 자료형 의도를 문서화한다.",["dynamic_typing","type_hint"]),
    U("py_p46_u01",46,"interpretation","파라미터로 어떤 값이 들어와야 하는지 명시하고 리턴값 형태 표시 / IDE hover","타입 힌트는 함수 계약을 도구와 독자에게 보여준다.",["type_hint"]),
    U("py_p47_u01",47,"example","List, Tuple, Dict, Any와 TypedDict로 타입 지정","컨테이너와 딕셔너리 구조를 타입으로 표현할 수 있다.",["type_hint","typeddict"] ,"visual"),
    U("py_p48_u01",48,"example","Callable[[str, int], float] / Callable[..., float]","Callable은 함수 인자와 반환 형식을 표현한다.",["type_hint","callable"],"visual"),
    U("py_p50_u01",50,"definition","Docstring은 함수·클래스·모듈의 입출력 형태 등을 코드 내부에 문서화 / __doc__ 조회 / IDE hover","Docstring은 실행 코드 가까이에서 객체 사용법을 문서화한다.",["docstring"]),
    U("py_p51_u01",51,"procedure","Args, Returns / Attributes, Methods","Docstring은 역할과 인자·반환·속성·메서드를 구조화한다.",["docstring"],"visual"),
    U("py_p52_u01",52,"definition","클래스는 객체를 생성하기 위한 설계도 / 속성에 데이터 저장, 메서드로 동작 정의","클래스는 상태와 행동을 묶어 객체를 만든다.",["class","object","attribute","method"]),
    U("py_p53_u01",53,"comparison","class attribute: 모든 인스턴스가 같은 값 공유 / instance attribute: 인스턴스별 고유 값","클래스 속성과 인스턴스 속성의 공유 범위가 다르다.",["class_attribute","instance_attribute","instance","constructor"]),
    U("py_p54_u01",54,"comparison","self는 현재 인스턴스 / cls는 현재 클래스 / static method는 self나 cls 없음","세 메서드는 접근하는 상태와 첫 인자가 다르다.",["instance_method","class_method","static_method","self","cls"]),
    U("py_p58_u01",58,"definition","객체가 지정된 속성과 행동을 가지도록 설계하는 프로그래밍 패러다임 / 재사용성·확장성·유지보수성","OOP는 객체 중심으로 상태와 행동을 구조화한다.",["oop","object","attribute"]),
    U("py_p59_u01",59,"definition","캡슐화 / 상속 / 다형성 / 추상화","OOP의 네 원칙은 정보 은닉, 확장, 동일 인터페이스의 다양한 동작, 구현 은닉이다.",["encapsulation","inheritance","polymorphism","abstraction"]),
    U("py_p60_u01",60,"example","부모 클래스를 상속 / super()로 부모 속성 초기화 / introduce 메서드 오버라이딩","자식 클래스는 부모 동작을 재사용·확장하고 재정의할 수 있다.",["inheritance","super","override"],"visual"),
]


CLAIM_UNITS = {
 "py.env_choice":["py_p4_u01","py_p5_u01"], "py.colab_tradeoff":["py_p5_u01"], "py.anaconda_team":["py_p6_u01"],
 "py.conda_family":["py_p7_u01"], "py.miniconda_anaconda":["py_p7_u01"],
 "py.vscode_role":["py_p8_u01"], "py.interpreter_select":["py_p16_u01"],
 "py.venv_need":["py_p22_u01"], "py.venv_definition":["py_p23_u01","py_p24_u01"], "py.venv_create_activate":["py_p24_u02"],
 "py.venv_install":["py_p26_u01"], "py.requirements_export":["py_p27_u01"], "py.requirements_restore":["py_p28_u01"], "py.venv_features":["py_p29_u01"],
 "py.conda_definition":["py_p30_u01"], "py.conda_lifecycle":["py_p30_u02","py_p35_u01"], "py.venv_conda":["py_p32_u01","py_p38_u01"],
 "py.conda_pip":["py_p34_u01"], "py.conda_export":["py_p35_u01","py_p36_u01"],
 "py.naming_rules":["py_p41_u01"], "py.naming_styles":["py_p43_u01"], "py.pep8_indent":["py_p44_u01"],
 "py.typing_purpose":["py_p45_u01"], "py.typing_contract":["py_p46_u01"], "py.typing_structures":["py_p47_u01"], "py.callable":["py_p48_u01"],
 "py.docstring_purpose":["py_p50_u01"], "py.docstring_structure":["py_p51_u01"],
 "py.class_role":["py_p52_u01"], "py.class_instance_attr":["py_p53_u01"], "py.constructor":["py_p53_u01"],
 "py.method_types":["py_p54_u01"], "py.instance_method":["py_p54_u01"], "py.class_static_method":["py_p54_u01"],
 "py.oop_definition":["py_p58_u01"], "py.oop_principles":["py_p59_u01"], "py.inheritance_override":["py_p60_u01"],
}


CRITICAL_ERRORS = {
 "py.conda_family":["Conda·Miniconda·Anaconda를 모두 완전히 동일한 설치 패키지라고 설명"],
 "py.venv_need":["가상환경이 서로 다른 프로젝트의 패키지를 하나의 전역 공간에 합치는 도구라고 설명"],
 "py.venv_create_activate":["activate 명령이 가상환경을 새로 생성한다고 설명"],
 "py.requirements_export":["pip freeze가 패키지 자체를 requirements.txt 안에 복사한다고 설명"],
 "py.requirements_restore":["requirements.txt만 존재하면 설치 명령 없이 패키지가 자동 설치된다고 설명"],
 "py.venv_conda":["venv가 Python 외 시스템 패키지까지 Conda와 동일하게 관리한다고 단정"],
 "py.conda_pip":["Conda 환경에서 pip와 conda를 어떤 순서로 섞어도 의존성 충돌 가능성이 전혀 없다고 설명"],
 "py.typing_purpose":["Python 타입 힌트가 기본적으로 런타임 타입을 강제하고 오류를 자동 차단한다고 설명"],
 "py.class_instance_attr":["인스턴스 속성이 모든 인스턴스에 항상 하나의 값으로 공유된다고 설명"],
 "py.method_types":["정적 메서드가 자동으로 현재 인스턴스 self를 받는다고 설명"],
 "py.oop_principles":["상속·캡슐화·다형성·추상화의 의미를 서로 뒤바꿔 핵심 관계를 무너뜨림"],
}


def claim(cid: str, role: str, text: str, *, category: str = "explanation_application") -> dict[str, Any]:
    return {"claim_id":cid,"role":role,"category":category,"text":text,"weight":1.0,"evidence":[],"term_ids":[],
            "evaluation_criteria":{"required_elements":[text],"critical_errors":CRITICAL_ERRORS.get(cid,[])}}


def sub(sid: str, title: str, summary: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    return {"sub_objective_id":sid,"title":title,"summary":summary,"claims":claims}


def objective(oid: str, title: str, desc: str, subs: list[dict[str, Any]]) -> dict[str, Any]:
    count=sum(len(s["claims"]) for s in subs)
    return {"objective_id":oid,"title":title,"selection_description":desc,"supporting_claim_slots":2 if count<=8 else 3,"sub_objectives":subs}


def build_rubric() -> dict[str, Any]:
    objs=[
      objective("python.environment_tools","Python 개발환경과 도구 선택","Colab·Conda 계열·VS Code의 역할과 선택 기준을 설명한다.",[
       sub("python.env.choice","환경 선택 기준","개발 목적에 따른 환경 trade-off를 설명한다.",[
        claim("py.env_choice","essential","Python 개발환경에는 하나의 정답이 없으며 접근성, 파일 관리, 협업과 프로젝트 규모에 맞춰 선택한다.",category="core_understanding"),
        claim("py.colab_tradeoff","supporting","Google Colab은 계정만 있으면 빠르게 시작할 수 있지만 로컬 파일 기반 프로그램 개발에는 유연성이 부족할 수 있다."),
        claim("py.anaconda_team","supporting","Anaconda 같은 로컬 환경은 파일 기반 개발과 팀 프로젝트의 공통 환경 구성에 활용할 수 있다."),]),
       sub("python.env.conda_family","Conda 계열 도구","Conda·Miniconda·Anaconda를 구분한다.",[
        claim("py.conda_family","essential","Conda는 패키지·환경 관리 엔진, Miniconda는 Conda와 Python 중심 최소 배포판, Anaconda는 데이터 과학 패키지를 미리 포함한 배포판이다.",category="core_understanding"),
        claim("py.miniconda_anaconda","supporting","Miniconda는 필요한 패키지만 선택하는 가벼운 설치에, Anaconda는 데이터 과학 도구를 바로 쓰는 큰 배포에 적합하다.",category="connection_comparison"),]),
       sub("python.env.ide","VS Code와 인터프리터","IDE 기능과 실행 환경 선택을 설명한다.",[
        claim("py.vscode_role","essential","VS Code는 코드 편집·실행·디버깅, 터미널, Git과 Python 확장을 통합한 개발 도구다.",category="core_understanding"),
        claim("py.interpreter_select","supporting","Python: Select Interpreter로 현재 프로젝트가 실행과 디버깅에 사용할 Python·가상환경을 명시적으로 선택한다."),]),
      ]),
      objective("python.virtual_environments","가상환경과 의존성 재현","venv·Conda의 격리, 패키지 기록과 환경 복제를 설명한다.",[
       sub("python.venv.motivation","가상환경의 필요성","프로젝트 격리와 재현성을 설명한다.",[
        claim("py.venv_need","essential","가상환경은 프로젝트마다 다른 Python·패키지 버전을 격리해 충돌을 줄이고 팀원과 미래의 실행 재현성을 높인다.",category="core_understanding"),
        claim("py.venv_definition","supporting","가상환경은 시스템·다른 프로젝트와 분리된 Python 실행 및 패키지 공간이며 venv는 Python 표준 도구다."),
        claim("py.venv_features","supporting","venv는 가볍고 Python 전용이며 시스템 Python을 건드리지 않고 프로젝트별 의존성을 관리한다."),]),
       sub("python.venv.workflow","venv 사용 흐름","생성·활성화·설치·공유를 연결한다.",[
        claim("py.venv_create_activate","essential","python -m venv로 환경을 생성하고 운영체제에 맞는 activate 스크립트를 실행해 활성화한다.",category="core_understanding"),
        claim("py.venv_install","supporting","활성화한 환경에서 pip로 설치하면 패키지가 해당 환경에 격리된다."),
        claim("py.requirements_export","supporting","pip freeze는 현재 설치된 패키지와 버전 목록을 requirements.txt에 기록하며 deactivate는 환경을 비활성화한다."),
        claim("py.requirements_restore","supporting","새 가상환경에서 pip install -r requirements.txt를 실행해 기록된 의존성을 설치한다."),
        ]),
       sub("python.conda.workflow","Conda 환경 관리","Conda 환경의 생명주기와 복제를 설명한다.",[
        claim("py.conda_definition","essential","Conda는 Python뿐 아니라 여러 언어의 패키지와 가상환경, 복잡한 의존성을 함께 관리한다.",category="core_understanding"),
        claim("py.conda_lifecycle","supporting","Conda 환경은 이름과 Python 버전을 지정해 만들고 activate·deactivate하며 필요하면 remove로 삭제한다."),
        claim("py.conda_export","supporting","conda env export로 environment.yml을 만들고 conda env create -f로 환경을 재생성한다."),]),
       sub("python.env.compare","venv와 Conda 선택","범위와 충돌 가능성을 비교한다.",[
        claim("py.venv_conda","essential","venv는 가벼운 Python 전용 프로젝트에, Conda는 복잡한 데이터 과학·다언어·시스템 의존성 관리에 더 적합하다.",category="connection_comparison"),
        claim("py.conda_pip","supporting","Conda 환경에서도 pip를 쓸 수 있지만 충돌을 줄이려면 Conda 패키지를 우선하고 없는 패키지만 pip로 보완한다."),]),
      ]),
      objective("python.code_quality","읽기 좋은 Python 코드","명명·PEP 8·Typing·Docstring으로 코드 계약을 전달한다.",[
       sub("python.quality.naming","명명과 스타일","식별자 규칙과 일관된 표기를 설명한다.",[
        claim("py.naming_rules","essential","Python 식별자는 예약어를 피하고 숫자로 시작하거나 공백을 포함할 수 없으며 언더바 외 특수문자를 피하고 의미 있는 이름을 사용한다.",category="core_understanding"),
        claim("py.naming_styles","supporting","snake_case는 단어 사이를 언더바로 나누고 CamelCase는 단어 첫 글자를 대문자로 표시한다."),
        claim("py.pep8_indent","supporting","PEP 8은 Python 들여쓰기에 스페이스 4칸을 권장하며 프로젝트 전체에서 일관되게 적용한다."),]),
       sub("python.quality.typing","타입 힌트","동적 언어에서 함수 계약을 표현한다.",[
        claim("py.typing_purpose","essential","타입 힌트는 변수·매개변수·반환형의 의도를 표시해 가독성, IDE 지원과 정적 검사 가능성을 높이지만 기본적으로 런타임 강제는 아니다.",category="core_understanding"),
        claim("py.typing_contract","supporting","함수의 매개변수와 반환 타입을 함께 표시하면 호출자가 함수 계약을 빠르게 이해할 수 있다."),
        claim("py.typing_structures","supporting","List·Tuple·Dict와 TypedDict로 컨테이너 원소와 딕셔너리 구조를 구체적으로 표현할 수 있다."),
        claim("py.callable","supporting","Callable은 함수 자체를 인자로 받을 때 그 함수의 인자 타입과 반환 타입을 표현한다."),]),
       sub("python.quality.docs","Docstring","코드 내부 문서화의 내용과 효과를 설명한다.",[
        claim("py.docstring_purpose","essential","Docstring은 함수·클래스·모듈의 역할과 입출력을 코드 내부에 기록하며 __doc__과 IDE hover에서 확인할 수 있다.",category="core_understanding"),
        claim("py.docstring_structure","supporting","함수 Docstring은 설명·Args·Returns를, 클래스 Docstring은 Attributes·Methods 등을 구조화해 기록할 수 있다."),]),
      ]),
      objective("python.classes_oop","클래스와 객체 지향","클래스의 상태·메서드와 OOP 원칙 및 상속을 설명한다.",[
       sub("python.class.basics","클래스와 속성","클래스·객체·인스턴스와 속성 범위를 설명한다.",[
        claim("py.class_role","essential","클래스는 관련 데이터인 속성과 동작인 메서드를 묶어 객체를 생성하는 설계도다.",category="core_understanding"),
        claim("py.class_instance_attr","supporting","클래스 속성은 모든 인스턴스가 공유하고 인스턴스 속성은 각 객체의 고유 상태를 저장한다."),
        claim("py.constructor","supporting","__init__ 생성자는 인스턴스가 만들어질 때 self에 객체별 초기 상태를 설정한다."),]),
       sub("python.class.methods","메서드 종류","self·cls와 상태 접근 범위를 구분한다.",[
        claim("py.method_types","essential","인스턴스 메서드는 self, 클래스 메서드는 cls를 받고 정적 메서드는 self·cls를 자동으로 받지 않는다.",category="core_understanding"),
        claim("py.instance_method","supporting","인스턴스 메서드는 self를 통해 현재 객체의 인스턴스 속성에 접근하거나 변경한다."),
        claim("py.class_static_method","supporting","클래스 메서드는 cls로 클래스 상태를 다루고 정적 메서드는 클래스와 관련 있지만 인스턴스·클래스 상태가 필요 없는 기능에 사용한다."),]),
       sub("python.oop.principles","OOP 원칙","객체 중심 설계와 네 원칙을 설명한다.",[
        claim("py.oop_definition","essential","객체 지향은 객체의 상태와 행동으로 프로그램을 구성해 재사용성·확장성·유지보수성을 높이는 패러다임이다.",category="core_understanding"),
        claim("py.oop_principles","supporting","캡슐화는 내부 상태 은닉, 상속은 기존 클래스 확장, 다형성은 같은 인터페이스의 다른 동작, 추상화는 구현을 감추고 필요한 인터페이스를 제공하는 원칙이다."),
        claim("py.inheritance_override","supporting","자식 클래스는 부모를 상속해 super로 초기화·동작을 재사용하고 메서드 오버라이딩으로 동작을 확장하거나 바꿀 수 있다."),]),
      ]),
    ]
    return {"schema_version":"2.2.0","lecture_id":"python_environment","lecture_name":"Python / 개발환경",
            "assessment":{"mode":"selected_topic_recall","target_seconds":120,"max_seconds":120,"score_policy":{"essential_points":60,"supporting_points":20,"coverage_points":20}},
            "top_level_objectives":objs,"excluded_source_claims":[]}


def apply_evaluation_data(processed_path: Path = PROCESSED_PATH, rubric_path: Path = RUBRIC_PATH) -> None:
    payload=json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id")!="python_environment": raise ValueError("Python 개발환경 processed 파일이 아닙니다.")
    pages={c["page"]:c for c in payload["chunks"]}
    if set(pages)!=set(range(1,62)): raise ValueError("Python 개발환경 PDF의 1~61쪽이 모두 존재해야 합니다.")
    payload["schema_version"]="2.1.0"; payload["terminology"]=TERMINOLOGY
    valid={"cover","table_of_contents","section_divider","core_content","example","supplementary_reference","closing"}
    for num,(_,_,_,role) in P.items():
        pages[num]["page_role"]=role if role in valid else "core_content"; pages[num]["term_ids"]=[]; pages[num]["evidence_units"]=[]; pages[num]["source_issues"]=[]
    lookup={}
    for raw in UNITS:
        item=dict(raw); num=item.pop("page"); pages[num]["term_ids"]=list(dict.fromkeys([*pages[num]["term_ids"],*item["term_ids"]])); pages[num]["evidence_units"].append(item); lookup[item["unit_id"]]=(pages[num],item)
    processed_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    rubric=build_rubric(); claims={c["claim_id"]:c for o in rubric["top_level_objectives"] for s in o["sub_objectives"] for c in s["claims"]}
    if set(claims)!=set(CLAIM_UNITS): raise ValueError("Python 개발환경 Claim과 Evidence 연결표가 일치하지 않습니다.")
    for cid,uids in CLAIM_UNITS.items():
        target=claims[cid]; tids=[]
        for uid in uids:
            chunk,source=lookup[uid]; tids.extend(source["term_ids"]); target["evidence"].append({"page":chunk["page"],"chunk_id":chunk["chunk_id"],"unit_id":uid,"source_excerpt":source["source_excerpt"],"source_status":"verified","review_note":""})
        target["term_ids"]=list(dict.fromkeys(tids))
    rubric_path.parent.mkdir(parents=True,exist_ok=True); rubric_path.write_text(json.dumps(rubric,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    apply_evaluation_data(); print(f"updated: {PROCESSED_PATH.relative_to(ROOT)}"); print(f"updated: {RUBRIC_PATH.relative_to(ROOT)}")
