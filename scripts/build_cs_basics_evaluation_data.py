from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "cs_basics.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "cs_basics.json"


def term(term_id: str, ko: str, en: str = "", *, abbreviations=None, aliases=None,
         symbols=None, not_equivalent_to=None) -> dict[str, Any]:
    return {"term_id": term_id, "canonical_ko": ko, "canonical_en": en,
            "abbreviations": abbreviations or [], "accepted_aliases": aliases or [],
            "symbols": symbols or [], "not_equivalent_to": not_equivalent_to or []}


TERMINOLOGY = [
    term("computer_science", "컴퓨터 과학", "computer science", abbreviations=["CS"]),
    term("computation", "계산", "computation"),
    term("information", "정보", "information"),
    term("automation", "자동화", "automation"),
    term("algorithm", "알고리즘", "algorithm"),
    term("data_structure", "자료구조", "data structure"),
    term("computer_system", "컴퓨터 시스템", "computer system"),
    term("cpu", "중앙처리장치", "central processing unit", abbreviations=["CPU"]),
    term("gpu", "그래픽처리장치", "graphics processing unit", abbreviations=["GPU"]),
    term("ram", "주기억장치", "random access memory", abbreviations=["RAM"], aliases=["메모리"]),
    term("persistent_storage", "비휘발성 저장장치", "persistent storage", aliases=["영구 저장장치"]),
    term("ssd", "SSD", "solid-state drive", abbreviations=["SSD"]),
    term("hdd", "HDD", "hard disk drive", abbreviations=["HDD"]),
    term("source_code", "소스코드", "source code"),
    term("machine_code", "기계어", "machine code"),
    term("compiler", "컴파일러", "compiler", aliases=["컴파일"]),
    term("interpreter", "인터프리터", "interpreter", aliases=["인터프리트"]),
    term("operating_system", "운영체제", "operating system", abbreviations=["OS"]),
    term("scheduling", "스케줄링", "scheduling", aliases=["스케쥴링"]),
    term("memory_management", "메모리 관리", "memory management"),
    term("virtual_memory", "가상 메모리", "virtual memory"),
    term("system_call", "시스템 콜", "system call", abbreviations=["syscall"]),
    term("user_mode", "사용자 모드", "user mode"),
    term("kernel_mode", "커널 모드", "kernel mode"),
    term("linux", "Linux", "Linux", aliases=["리눅스"]),
    term("unix", "Unix", "Unix", aliases=["유닉스"]),
    term("linux_kernel", "Linux 커널", "Linux kernel"),
    term("distribution", "Linux 배포판", "Linux distribution", abbreviations=["distro"], aliases=["리눅스 디스트로"]),
    term("user_space", "사용자 영역", "user space"),
    term("everything_file", "모든 것은 파일", "everything is a file"),
    term("file_permission", "파일 권한", "file permission"),
    term("read_permission", "읽기 권한", "read permission", abbreviations=["r"]),
    term("write_permission", "쓰기 권한", "write permission", abbreviations=["w"]),
    term("execute_permission", "실행 권한", "execute permission", abbreviations=["x"]),
    term("virtualization", "가상화", "virtualization"),
    term("virtual_machine", "가상머신", "virtual machine", abbreviations=["VM"]),
    term("container", "컨테이너", "container"),
    term("docker", "Docker", "Docker", aliases=["도커"]),
    term("wsl", "Windows 리눅스 하위 시스템", "Windows Subsystem for Linux", abbreviations=["WSL", "WSL2"]),
    term("orbstack", "OrbStack", "OrbStack"),
    term("shell_script", "셸 스크립트", "shell script", aliases=["bash script", "배시 스크립트"]),
    term("chmod", "chmod", "change mode"),
]


PAGE_INFO: dict[int, tuple[str, list[str], str, str]] = {
    1: ("CS 기초 강의 표지", ["CS"], "CS 기초 강의 표지이다.", "cover"),
    2: ("강의 목차", ["CS", "컴퓨터 시스템", "실습"], "CS의 의미, 컴퓨터 시스템, Linux 실습 순으로 진행한다.", "table_of_contents"),
    3: ("CS란?", ["컴퓨터 과학"], "컴퓨터 과학의 의미와 범위를 소개하는 섹션이다.", "section_divider"),
    4: ("컴퓨터 과학의 정의", ["계산", "정보", "자동화", "컴퓨터 시스템"], "컴퓨터 과학은 계산·정보·자동화와 이를 수행하는 컴퓨터 및 계산 시스템을 연구한다.", "core_content"),
    5: ("CS의 세 축", ["계산", "정보", "자동화"], "계산은 문제를 단계와 연산으로 풀고, 정보는 컴퓨터가 처리할 형태로 표현하며, 자동화는 이 과정을 사람 개입 없이 수행하게 한다.", "core_content"),
    6: ("CS 이론 분야", ["계산 가능성", "알고리즘", "자료구조", "정보 이론", "하드웨어"], "계산 가능성, 효율적 풀이를 위한 알고리즘·자료구조, 정보 표현, 하드웨어 구현을 연결한다.", "core_content"),
    7: ("CS와 컴퓨터 시스템", ["컴퓨터 시스템", "알고리즘", "자료구조"], "이론적 계산과 정보 표현을 실제 컴퓨터 시스템으로 구현한다.", "core_content"),
    8: ("컴퓨터 시스템의 범위", ["아키텍처", "운영체제", "네트워크", "데이터베이스", "컴파일러"], "컴퓨터 시스템은 아키텍처, 운영체제, 네트워크, 데이터베이스, 컴파일러 등을 포함한다.", "core_content"),
    9: ("강의의 컴퓨터 시스템 범위", ["운영체제", "Linux", "가상화", "셸 스크립트"], "강의는 운영체제, Linux, 가상화, 셸 스크립트를 중심으로 다룬다.", "core_content"),
    10: ("AI 시대의 CS 기초", ["LLM", "시스템 구조"], "LLM이 코드를 작성해도 전반적인 시스템 구조를 이해해야 효율적으로 개발할 수 있다.", "core_content"),
    11: ("컴퓨터 시스템", ["컴퓨터 시스템"], "하드웨어부터 운영체제·Linux·가상화까지 다루는 섹션이다.", "section_divider"),
    12: ("하드웨어 구성 시작", ["하드웨어"], "컴퓨터 하드웨어 구성을 선택하는 상황을 소개한다.", "example"),
    13: ("PC 하드웨어 구성", ["CPU", "GPU", "RAM", "메인보드", "SSD"], "본체는 CPU·GPU·RAM·메인보드·저장장치·파워 등으로 구성되고 입출력 장치가 연결된다.", "core_content"),
    14: ("CPU·RAM·저장장치", ["CPU", "RAM", "SSD", "HDD", "휘발성"], "CPU는 연산, RAM은 빠르지만 휘발성인 작업 정보, SSD·HDD는 전원이 꺼져도 유지되는 저장을 담당한다.", "core_content"),
    15: ("CPU와 GPU", ["CPU", "GPU", "직렬 연산", "병렬 연산"], "CPU는 복잡한 제어 흐름과 순차 작업의 낮은 지연에, GPU는 단순한 연산을 대량 데이터에 병렬로 반복하는 작업에 강하다.", "core_content"),
    16: ("코드 실행 흐름", ["소스코드", "컴파일", "인터프리트", "기계어", "RAM", "CPU"], "소스코드는 컴파일 또는 인터프리트를 거쳐 기계어로 처리되고 RAM에 올라간 뒤 CPU가 연산한다.", "core_content"),
    17: ("운영체제의 필요성", ["운영체제", "하드웨어 관리", "보호"], "여러 프로그램의 우선순위와 자원을 관리하고 비정상 접근으로부터 시스템을 보호할 주체가 필요하다.", "core_content"),
    18: ("운영체제의 세 역할", ["스케줄링", "메모리 관리", "보호"], "운영체제는 프로그램 스케줄링, 메모리 분배, 하드웨어 접근 보호를 담당한다.", "core_content"),
    19: ("CPU 스케줄링", ["CPU", "스케줄링", "동시성"], "한 CPU 코어는 한 순간에 한 작업을 처리하며 OS가 짧은 시간 단위로 프로그램을 번갈아 실행해 동시적으로 보이게 한다.", "core_content"),
    20: ("메모리 관리", ["메모리 관리", "가상 메모리", "주소 변환"], "각 프로그램은 독립적 메모리를 쓰는 것처럼 보고 OS가 실제 메모리 주소를 관리한다.", "core_content"),
    21: ("시스템 콜과 보호", ["시스템 콜", "User mode", "Kernel mode", "보호"], "사용자 프로그램은 하드웨어에 직접 접근하지 않고 User mode에서 시스템 콜로 OS에 요청하면 Kernel mode에서 처리한다.", "core_content"),
    22: ("주요 운영체제", ["Windows", "macOS", "Linux"], "Windows, macOS, Linux를 주요 운영체제로 소개한다.", "supplementary_reference"),
    23: ("서버에서 Linux를 쓰는 이유", ["Linux", "GUI 오버헤드", "오픈소스", "안정성"], "Linux는 GUI 오버헤드를 줄일 수 있고 오픈소스이며 서버·임베디드·클라우드에서 검증된 안정성과 제어력을 갖는다.", "core_content"),
    24: ("Unix·Linux·배포판", ["Unix", "Linux 커널", "Linux 배포판", "User Space"], "Unix는 현대 운영체제의 뿐리이고 Linux는 Unix 철학을 따른 오픈소스 커널이며, 배포판은 커널과 User Space 패키지를 묶은다.", "core_content"),
    25: ("Unix 계보", ["Unix", "BSD", "Linux", "macOS"], "Unix에서 BSD·Linux 계열이 분기하는 계보를 도식으로 보여준다.", "example"),
    26: ("Everything is a File", ["Everything is a File", "regular file", "directory", "/proc"], "Unix/Linux에서 문서·디바이스·프로세스 정보·소켓을 파일 인터페이스로 다루며 open·read·write로 상호작용한다.", "core_content"),
    27: ("Linux 파일 권한", ["user", "group", "others", "read", "write", "execute"], "파일은 user·group·others 범주별로 r·w·x 권한을 가지며 이로써 OS의 보호 기능을 구현한다.", "core_content"),
    28: ("Linux 환경 선택", ["AWS", "dual boot", "VM", "WSL", "Docker"], "Windows에서 Linux를 쓰기 위해 AWS, 듀얼부팅, VM, WSL, Docker 등을 선택할 수 있다.", "core_content"),
    29: ("VM과 Container", ["VM", "Guest OS", "Container", "호스트 커널"], "VM은 독립 Guest OS와 커널을 올려 격리가 강하지만 무겁고, Container는 호스트 커널을 공유해 프로세스 수준으로 가밍고 빠르게 격리한다.", "core_content"),
    30: ("WSL1과 WSL2", ["WSL1", "WSL2", "syscall 번역", "Linux 커널"], "WSL1은 Linux 시스템 콜을 번역하고 WSL2는 경량 Linux 커널을 직접 실행한다.", "core_content"),
    31: ("WSL2와 Docker", ["WSL2", "Docker", "개발 환경", "배포"], "Docker는 애플리케이션 격리·배포, WSL2는 Windows에서 Linux 개발 환경 자체를 쓰는 데 초점이 있다.", "core_content"),
    32: ("macOS의 Linux 환경", ["macOS", "BSD", "Linux 커널", "Docker", "OrbStack"], "macOS와 Linux는 Unix 계열이지만 커널과 도구의 차이로 재현성 문제가 생길 수 있어 Docker나 OrbStack 환경을 고려한다.", "core_content"),
    33: ("Linux 사용자 참고", ["Ubuntu", "Arch Linux", "Kali Linux"], "Linux 배포판을 이미 쓰는 사용자를 위한 간단한 참고 페이지이다.", "supplementary_reference"),
    34: ("실습 섹션", ["Linux 실습"], "Linux 환경·하드웨어·파일·권한·셸 스크립트 실습 섹션이다.", "section_divider"),
    35: ("실습 환경", ["Ubuntu", "WSL2", "OrbStack"], "Windows는 WSL2, macOS는 OrbStack으로 Ubuntu 환경을 준비한다.", "procedure"),
    36: ("Windows·WSL2 실습 준비", ["Windows", "WSL2"], "Windows에서 WSL2를 준비하는 안내 자료를 제시한다.", "supplementary_reference"),
    37: ("macOS·OrbStack 실습 준비", ["macOS", "OrbStack"], "macOS에서 OrbStack으로 Linux 머신을 생성하는 화면을 보여준다.", "example"),
    38: ("시스템 정보 확인", ["lscpu", "free", "os-release", "uname"], "lscpu로 CPU, free -h로 메모리, /etc/os-release로 배포판, uname -a로 커널 정보를 확인한다.", "procedure"),
    39: ("파일시스템 기본 명령", ["ls", "cd", "pwd", "hidden file"], "ls로 파일을 보고 -a로 숨김 파일, -l로 권한을 확인하며 cd로 이동하고 pwd로 현재 경로를 본다.", "procedure"),
    40: ("권한 읽기 실습", ["/etc/shadow", "ls -l", "user", "group", "others"], "/etc/shadow의 -rw-r----- 표시를 user·group·others의 읽기·쓰기 권한으로 해석한다.", "example"),
    41: ("chmod 권한 변경 실습", ["chmod", "644", "/etc/shadow"], "chmod 644로 others에 읽기 권한을 부여하면 보호된 파일이 노출될 수 있음을 실습한다.", "example"),
    42: ("셸 스크립트 실행", ["shell script", "chmod", "executable"], "run.sh를 저장하고 chmod +x로 실행 권한을 준 뒤 ./run.sh로 실행한다.", "procedure"),
    43: ("입출력 자동화 셸 스크립트", ["bash", "for loop", "redirection", "basename"], "입력 파일을 반복하며 Python 프로그램에 리디렉션하고 결과를 출력 파일로 저장한다.", "example"),
    44: ("강의 마무리", ["CS 기초"], "CS 기초 강의의 종료 페이지이다.", "closing"),
}


def curated_page(topic: str, concepts: list[str], content: str, role: str) -> list[dict[str, object]]:
    visual = content if role not in {"cover", "table_of_contents", "section_divider", "closing"} else f"{topic} 페이지이다."
    return [{"topic": topic, "concepts": concepts, "visual_description": visual, "content": content}]


CURATION = {page: curated_page(*info) for page, info in PAGE_INFO.items()}


def unit(unit_id: str, page: int, kind: str, excerpt: str, explanation: str,
         term_ids: list[str], source_type: str = "text") -> dict[str, Any]:
    return {"unit_id": unit_id, "page": page, "type": kind, "source_type": source_type,
            "source_excerpt": excerpt, "normalized_explanation": explanation,
            "source_status": "verified", "term_ids": term_ids}


U = unit
UNITS = [
    U("cs_p4_u01", 4, "definition", "컴퓨터 과학은 계산, 정보, 자동화와 이를 수행하는 컴퓨터 및 계산 시스템을 연구하는 학문이다.", "컴퓨터 과학은 계산·정보·자동화와 이를 구현하는 시스템을 연구한다.", ["computer_science", "computation", "information", "automation", "computer_system"]),
    U("cs_p5_u01", 5, "comparison", "계산: 문제를 단계로 쪼개어 연산으로 해결 / 정보: 컴퓨터가 이해·처리할 형태로 표현 / 자동화: 사람의 개입 없이 수행", "CS의 세 축은 문제 해결, 정보 표현, 자동 실행이다.", ["computation", "information", "automation"]),
    U("cs_p6_u01", 6, "relation", "계산 가능성 이론, 알고리즘·자료구조, 정보 이론, 하드웨어 이론", "계산 가능성부터 효율적 풀이·정보 표현·하드웨어 구현까지 연결된다.", ["computation", "algorithm", "data_structure", "information"]),
    U("cs_p8_u01", 8, "example", "컴퓨터 아키텍처, 운영체제, 네트워크, 데이터베이스, 컴파일러 등", "컴퓨터 시스템은 여러 시스템 분야를 포함한다.", ["computer_system", "operating_system", "compiler"]),
    U("cs_p9_u01", 9, "interpretation", "컴퓨터 시스템: 운영체제, Linux, 가상화, Shell Script", "강의는 OS·Linux·가상화·셸 스크립트를 핵심 시스템 범위로 다룬다.", ["computer_system", "operating_system", "linux", "virtualization", "shell_script"]),
    U("cs_p10_u01", 10, "interpretation", "코드를 짜는 행위 자체는 LLM이 해주니까, 전반적인 구조에 대한 이해가 있어야 더욱 효율적인 개발이 가능하다.", "AI가 코드를 작성해도 시스템 구조를 이해해야 실행·문제해결을 효율적으로 할 수 있다.", ["computer_system"]),
    U("cs_p13_u01", 13, "example", "본체: CPU, 그래픽카드, 램, 메인보드, 쿨러, 파워서플라이, SSD", "PC는 연산·메모리·저장·연결·전원 부품으로 구성된다.", ["cpu", "gpu", "ram", "ssd"]),
    U("cs_p14_u01", 14, "comparison", "CPU: 중앙 연산 장치 / RAM: CPU가 사용할 정보를 들고 있는 휘발성 저장 장치 / SSD·HDD: 전원이 꺼져도 정보를 들고 있는 영구 저장 장치", "CPU는 연산, RAM은 빠른 휘발성 작업 저장, SSD·HDD는 비휘발성 저장을 담당한다.", ["cpu", "ram", "persistent_storage", "ssd", "hdd"]),
    U("cs_p15_u01", 15, "comparison", "CPU는 직렬 연산이 강점 / GPU는 병렬 연산이 강점", "CPU는 복잡한 순차 제어, GPU는 대량의 단순 반복 연산에 강하다.", ["cpu", "gpu"]),
    U("cs_p16_u01", 16, "procedure", "소스코드 → (컴파일 / 인터프리트) → 기계어 → RAM에 올림 → CPU가 연산", "프로그램은 기계어로 변환·처리되어 메모리에 올라간 뒤 CPU가 실행한다.", ["source_code", "compiler", "interpreter", "machine_code", "ram", "cpu"]),
    U("cs_p17_u01", 17, "relation", "하드웨어를 직접 관리 및 통제하는 주체가 필요하다. 잘못된 접근 혹은 비정상적인 동작으로부터 시스템을 보호하기 위해서다.", "OS는 공유 하드웨어를 관리하고 비정상 접근을 보호한다.", ["operating_system"]),
    U("cs_p18_u01", 18, "definition", "운영체제의 역할: 스케줄링, 메모리 관리, 보호", "OS의 핵심 역할은 CPU 시간·메모리·하드웨어 접근 관리다.", ["operating_system", "scheduling", "memory_management"]),
    U("cs_p19_u01", 19, "procedure", "CPU 코어 하나는 한 순간에 한 가지 일만 처리. OS가 아주 짧은 시간 단위로 여러 프로그램을 번갈아 실행", "스케줄러가 실행 시간을 나눠 동시성을 제공한다.", ["cpu", "scheduling"]),
    U("cs_p20_u01", 20, "interpretation", "프로그램들이 각자 '나만 이 메모리를 쓰고 있다'고 착각하게 만듦. 실제로는 OS가 진짜 메모리 주소를 관리", "가상 메모리는 프로세스에 독립 주소 공간을 제공하고 OS가 실제 주소를 관리한다.", ["memory_management", "virtual_memory"]),
    U("cs_p21_u01", 21, "procedure", "유저 프로그램은 하드웨어에 직접적인 접근이 금지. 대신 OS에게 부탁(System Call). User mode와 Kernel mode가 분리", "특권 분리와 시스템 콜이 하드웨어 접근을 통제한다.", ["system_call", "user_mode", "kernel_mode", "operating_system"]),
    U("cs_p23_u01", 23, "comparison", "Linux 서버 사용 이유: GUI 오버헤드, 오픈소스, 안정성과 하드웨어 제어", "Linux는 자원 효율·자유도·안정성 때문에 서버에 널리 쓴다.", ["linux"]),
    U("cs_p24_u01", 24, "comparison", "Unix는 1970년대 서버용 OS의 뿐리. Linux는 1991년 Unix 철학을 따라 만든 오픈소스 커널. Linux Distribution은 커널 위에 User Space를 묶은 패키지", "Unix·Linux 커널·배포판은 역사와 구성 수준이 다른 개념이다.", ["unix", "linux_kernel", "distribution", "user_space"]),
    U("cs_p25_u01", 25, "example", "Unix에서 BSD와 Linux 계열이 분기되는 관계도", "macOS의 BSD 계열과 Linux 커널은 Unix 계열 철학을 공유하지만 동일한 커널은 아니다.", ["unix", "linux", "linux_kernel"] , "visual"),
    U("cs_p26_u01", 26, "definition", "Everything is a File: 문서뿐 아니라 디바이스, 프로세스 정보, 네트워크 소켓을 같은 개념으로 접근; open(), read(), write()", "Unix/Linux는 여러 커널 자원을 일관된 파일 인터페이스로 다룬다.", ["everything_file"]),
    U("cs_p26_u02", 26, "example", "Regular file, Directory file, /proc file", "일반 파일·디렉터리·커널 상태가 서로 다른 파일 형태로 노출된다.", ["everything_file"]),
    U("cs_p27_u01", 27, "procedure", "소유자(user) / 같은 그룹(group) / 그 외(others), 각 범주마다 r(read) / w(write) / x(execute) 권한", "Linux 권한은 주체 범주별로 읽기·쓰기·실행을 나눠 표현한다.", ["file_permission", "read_permission", "write_permission", "execute_permission"]),
    U("cs_p27_u02", 27, "interpretation", "-rwxr-xr-- 같은 표시는 차례대로 user, group, others의 r/w/x 권한", "ls -l 권한 문자열은 파일 형태 후 user·group·others의 rwx 세 묶음으로 읽는다.", ["file_permission", "read_permission", "write_permission", "execute_permission"]),
    U("cs_p28_u01", 28, "comparison", "Windows에서 Linux: AWS, Linux 직접 설치, 듀얼부팅, VM, WSL, Docker", "Linux 환경은 원격 머신·직접 설치·가상화·컨테이너 등으로 준비할 수 있다.", ["virtualization", "virtual_machine", "wsl", "docker"]),
    U("cs_p29_u01", 29, "comparison", "VM: 완전히 독립된 커널의 Guest OS, 완전 격리·무거움 / Container: 커널을 호스트와 공유, 프로세스 수준 격리, 가밍고 빠름", "VM은 커널까지 격리하고 컨테이너는 호스트 커널을 공유한다.", ["virtual_machine", "container"]),
    U("cs_p30_u01", 30, "comparison", "WSL1: syscall 번역 / WSL2: 경량 Linux 커널을 직접 실행", "WSL2는 시스템 콜 번역이 아니라 실제 Linux 커널을 사용한다.", ["wsl", "system_call", "linux_kernel"]),
    U("cs_p31_u01", 31, "comparison", "Docker: 애플리케이션 격리/배포 중심 / WSL2: 개발 환경 자체를 Linux로 쓰는 워크스테이션", "Docker와 WSL2는 목적이 다르다.", ["docker", "wsl"]),
    U("cs_p32_u01", 32, "warning", "macOS와 Linux는 같은 Unix 기반이지만 BSD / Linux Kernel의 차이가 있어 셸스크립트에 예상치 못한 오류가 발생할 수 있다. Docker·OrbStack 고려", "Unix 계열이라도 커널·도구 차이로 재현성 문제가 생길 수 있다.", ["unix", "linux_kernel", "docker", "orbstack", "shell_script"]),
    U("cs_p38_u01", 38, "procedure", "CPU: lscpu / 메모리: free -h / 배포판: cat /etc/os-release / 커널: uname -a", "Linux 명령으로 하드웨어·배포판·커널 정보를 확인한다.", ["cpu", "ram", "distribution", "linux_kernel"]),
    U("cs_p39_u01", 39, "procedure", "ls, ls -a, ls -l, cd, cd .., pwd", "ls는 파일 목록, cd는 이동, pwd는 현재 경로 확인에 쓴다.", ["file_permission"]),
    U("cs_p40_u01", 40, "example", "/etc/shadow의 -rw-r-----: user는 r+w, group은 r, others는 권한 없음", "보호된 파일의 권한 표시를 주체별로 읽는다.", ["file_permission", "read_permission", "write_permission"]),
    U("cs_p41_u01", 41, "warning", "sudo chmod 644 /etc/shadow: others에도 읽기 권한 추가 후 다른 사용자로 cat /etc/shadow", "잘못된 chmod는 민감한 파일을 다른 사용자에게 노출할 수 있다.", ["chmod", "file_permission", "read_permission"]),
    U("cs_p42_u01", 42, "procedure", "chmod +x ./run.sh → ./run.sh", "셸 스크립트에 실행 권한을 준 뒤 경로로 실행한다.", ["shell_script", "chmod", "execute_permission"]),
    U("cs_p43_u01", 43, "procedure", "for file_path in inputs/*; do ... python3 test.py < $file_path > outputs/${file_name}.output; done", "반복문과 입출력 리디렉션으로 여러 테스트 케이스를 자동 실행한다.", ["shell_script"]),
]


CLAIM_UNITS = {
    "cs.definition": ["cs_p4_u01"], "cs.three_pillars": ["cs_p5_u01"], "cs.theory_fields": ["cs_p6_u01"],
    "cs.system_scope": ["cs_p8_u01", "cs_p9_u01"], "cs.ai_structure": ["cs_p10_u01"],
    "cs.storage_roles": ["cs_p14_u01"], "cs.cpu_gpu": ["cs_p15_u01"], "cs.pc_components": ["cs_p13_u01"],
    "cs.execution_pipeline": ["cs_p16_u01"], "cs.machine_execution": ["cs_p16_u01"],
    "cs.os_need": ["cs_p17_u01", "cs_p18_u01"], "cs.time_sharing": ["cs_p19_u01"],
    "cs.virtual_memory": ["cs_p20_u01"], "cs.address_management": ["cs_p20_u01"],
    "cs.system_call": ["cs_p21_u01"], "cs.mode_separation": ["cs_p21_u01"], "cs.protection_goal": ["cs_p17_u01", "cs_p21_u01"],
    "cs.linux_server": ["cs_p23_u01"], "cs.opensource_control": ["cs_p23_u01"], "cs.linux_stability": ["cs_p23_u01"],
    "cs.unix_linux": ["cs_p24_u01"], "cs.distro": ["cs_p24_u01"], "cs.kernel_difference": ["cs_p25_u01"],
    "cs.everything_file": ["cs_p26_u01"], "cs.file_examples": ["cs_p26_u02"], "cs.permission_model": ["cs_p27_u01"], "cs.permission_string": ["cs_p27_u02"],
    "cs.vm_container": ["cs_p29_u01"], "cs.vm_isolation": ["cs_p29_u01"], "cs.container_efficiency": ["cs_p29_u01"],
    "cs.wsl_versions": ["cs_p30_u01"], "cs.wsl_docker": ["cs_p31_u01"], "cs.macos_reproducibility": ["cs_p32_u01"],
    "cs.inspect_system": ["cs_p38_u01"], "cs.navigate_files": ["cs_p39_u01"], "cs.read_permissions": ["cs_p40_u01"],
    "cs.chmod_risk": ["cs_p41_u01"], "cs.run_script": ["cs_p42_u01"], "cs.batch_script": ["cs_p43_u01"],
}


CRITICAL_ERRORS = {
    "cs.storage_roles": ["RAM이 전원이 꺼져도 영구적으로 데이터를 보존한다고 설명", "SSD·HDD를 휘발성 저장장치로 설명"],
    "cs.cpu_gpu": ["CPU와 GPU의 직렬·병렬 연산 강점을 서로 뒤바꿔 설명"],
    "cs.execution_pipeline": ["소스코드가 메모리와 기계어 처리 없이 CPU에서 그대로 실행된다고 설명"],
    "cs.time_sharing": ["한 CPU 코어가 같은 순간에 무제한한 명령을 물리적으로 동시 실행한다고 설명"],
    "cs.virtual_memory": ["각 프로세스가 다른 프로세스와 실제 메모리 주소를 무조건 그대로 공유한다고 설명"],
    "cs.system_call": ["일반 사용자 프로그램이 하드웨어를 제약 없이 직접 제어한다고 설명"],
    "cs.unix_linux": ["Unix·Linux 커널·Linux 배포판을 모두 동일한 개념으로 설명"],
    "cs.permission_model": ["r·w·x가 각각 user·group·others 자체를 뜻한다고 설명"],
    "cs.vm_container": ["컨테이너가 항상 독립 Guest OS 커널을 포함한다고 설명", "VM이 호스트 커널을 그대로 공유하는 프로세스 수준 격리라고 설명"],
    "cs.wsl_versions": ["WSL1이 실제 Linux 커널을 직접 실행하고 WSL2가 syscall만 번역한다고 뒤바꿔 설명"],
    "cs.chmod_risk": ["민감한 파일을 chmod 644로 바꾸어도 다른 사용자의 읽기 권한은 생기지 않는다고 설명"],
}


def claim(claim_id: str, role: str, text: str, *, category: str = "explanation_application") -> dict[str, Any]:
    return {"claim_id": claim_id, "role": role, "category": category, "text": text,
            "weight": 1.0, "evidence": [], "term_ids": [],
            "evaluation_criteria": {"required_elements": [text], "critical_errors": CRITICAL_ERRORS.get(claim_id, [])}}


def sub(sub_id: str, title: str, summary: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    return {"sub_objective_id": sub_id, "title": title, "summary": summary, "claims": claims}


def objective(obj_id: str, title: str, description: str, subs: list[dict[str, Any]]) -> dict[str, Any]:
    count = sum(len(item["claims"]) for item in subs)
    return {"objective_id": obj_id, "title": title, "selection_description": description,
            "supporting_claim_slots": 2 if count <= 8 else 3, "sub_objectives": subs}


def build_rubric() -> dict[str, Any]:
    objectives = [
        objective("cs.scope_execution", "CS의 범위와 프로그램 실행", "CS의 의미, 하드웨어 역할과 코드 실행 흐름을 설명한다.", [
            sub("cs.scope.meaning", "CS의 의미", "계산·정보·자동화와 주요 이론 분야를 연결한다.", [
                claim("cs.definition", "essential", "컴퓨터 과학은 계산·정보·자동화와 이를 수행하는 컴퓨터 및 계산 시스템을 연구한다.", category="core_understanding"),
                claim("cs.three_pillars", "supporting", "계산은 문제를 단계와 연산으로 풀고, 정보는 처리 가능한 형태로 표현하며, 자동화는 이를 사람 개입 없이 수행하게 한다."),
                claim("cs.theory_fields", "supporting", "계산 가능성, 알고리즘·자료구조, 정보 이론과 실제 시스템 구현은 CS의 연결된 주제다.", category="connection_comparison"),
            ]),
            sub("cs.scope.relevance", "시스템 범위와 필요성", "시스템 분야와 AI 시대의 구조 이해 필요성을 설명한다.", [
                claim("cs.system_scope", "essential", "컴퓨터 시스템은 아키텍처·운영체제·네트워크·데이터베이스·컴파일러 등을 포함하며 강의는 OS·Linux·가상화·셸을 다룬다.", category="core_understanding"),
                claim("cs.ai_structure", "supporting", "LLM이 코드를 작성해도 전반적인 시스템 구조를 이해해야 효율적인 개발과 문제 해결이 가능하다."),
            ]),
            sub("cs.scope.hardware", "하드웨어 역할", "CPU·GPU·RAM·저장장치의 역할을 비교한다.", [
                claim("cs.storage_roles", "essential", "CPU는 연산, RAM은 빠른 휘발성 작업 저장, SSD·HDD는 비휘발성 영구 저장을 담당한다.", category="core_understanding"),
                claim("cs.cpu_gpu", "supporting", "CPU는 복잡한 제어 흐름과 순차 작업, GPU는 단순한 연산을 대량 데이터에 병렬로 반복하는 작업에 강하다.", category="connection_comparison"),
                claim("cs.pc_components", "supporting", "PC 본체는 CPU·GPU·RAM·메인보드·저장장치·전원·쿨링 부품으로 구성된다."),
            ]),
            sub("cs.scope.execution", "프로그램 실행", "소스코드가 CPU에서 실행되는 흐름을 설명한다.", [
                claim("cs.execution_pipeline", "essential", "소스코드는 컴파일 또는 인터프리트를 거쳐 기계어로 처리되고 RAM에 올라간 뒤 CPU가 연산한다.", category="core_understanding"),
                claim("cs.machine_execution", "supporting", "CPU는 사람이 작성한 소스코드 문자열을 그대로 읽는 것이 아니라 메모리에 적재된 기계어 명령을 실행한다."),
            ]),
        ]),
        objective("cs.os_protection", "운영체제의 자원 관리와 보호", "OS의 스케줄링·메모리 관리·보호 원리를 설명한다.", [
            sub("cs.os.scheduling", "스케줄링", "CPU 시간을 나눠 동시성을 만드는 원리를 설명한다.", [
                claim("cs.os_need", "essential", "운영체제는 여러 프로그램이 공유하는 하드웨어를 관리하고 잘못된 접근으로부터 시스템을 보호한다.", category="core_understanding"),
                claim("cs.time_sharing", "supporting", "한 CPU 코어는 한 순간에 한 작업을 처리하고 OS가 짧은 시간 단위로 프로그램을 번갈아 실행해 동시적으로 보이게 한다."),
            ]),
            sub("cs.os.memory", "메모리 관리", "가상 메모리와 실제 주소 관리를 설명한다.", [
                claim("cs.virtual_memory", "essential", "가상 메모리는 각 프로그램이 독립된 메모리를 쓰는 것처럼 보이게 하고 OS가 실제 메모리 주소를 관리한다.", category="core_understanding"),
                claim("cs.address_management", "supporting", "프로세스가 보는 가상 주소와 실제 물리 메모리 주소의 연결은 OS가 관리한다."),
            ]),
            sub("cs.os.protection", "특권 분리와 보호", "User·Kernel mode와 시스템 콜을 연결한다.", [
                claim("cs.system_call", "essential", "사용자 프로그램은 하드웨어에 직접 접근하지 않고 시스템 콜로 OS에 요청한다.", category="core_understanding"),
                claim("cs.mode_separation", "supporting", "요청하는 User mode와 특권 작업을 실제 처리하는 Kernel mode를 분리해 시스템을 보호한다."),
                claim("cs.protection_goal", "supporting", "하드웨어·다른 프로그램의 메모리·디스크에 대한 무제한 접근을 막는 것이 OS 보호의 목적이다."),
            ]),
        ]),
        objective("cs.linux_model", "Linux의 구조와 파일 권한", "Linux 서버, Unix·커널·배포판, 파일 철학과 권한을 설명한다.", [
            sub("cs.linux.server", "Linux 서버", "서버에서 Linux를 쓰는 이유를 설명한다.", [
                claim("cs.linux_server", "essential", "Linux는 GUI 오버헤드를 줄일 수 있고 오픈소스이며 안정성과 하드웨어 제어력 때문에 서버에 널리 쓴다.", category="core_understanding"),
                claim("cs.opensource_control", "supporting", "Linux는 소스코드가 공개되어 커스텀하기 좋고 라이선스 비용 부담을 줄일 수 있다."),
                claim("cs.linux_stability", "supporting", "Linux는 서버·임베디드·클라우드·슈퍼컴퓨터 환경에서 오랫동안 사용되며 안정성을 검증받았다."),
            ]),
            sub("cs.linux.structure", "Unix·커널·배포판", "서로 다른 수준의 Linux 개념을 구분한다.", [
                claim("cs.unix_linux", "essential", "Unix는 운영체제 계보의 뿐리이고 Linux는 Unix 철학을 따른 오픈소스 커널이다.", category="core_understanding"),
                claim("cs.distro", "supporting", "Linux 배포판은 Linux 커널과 User Space 도구·패키지를 묶어 사용 가능한 OS 환경으로 제공한다."),
                claim("cs.kernel_difference", "supporting", "macOS의 BSD 계열과 Linux는 Unix 계열 철학을 공유하지만 서로 다른 커널과 도구 환경을 가진다.", category="connection_comparison"),
            ]),
            sub("cs.linux.files", "파일 철학과 권한", "Everything is a File과 rwx 권한을 연결한다.", [
                claim("cs.everything_file", "essential", "Unix/Linux의 Everything is a File 철학은 문서·디바이스·프로세스 정보·소켓을 open·read·write와 같은 일관된 파일 인터페이스로 다룬다.", category="core_understanding"),
                claim("cs.file_examples", "supporting", "Linux에서 일반 파일, 디렉터리, /proc의 커널 상태 정보는 서로 다른 파일 형태로 노출된다."),
                claim("cs.permission_model", "supporting", "Linux 파일은 user·group·others 범주별로 r·w·x 읽기·쓰기·실행 권한을 따로 가진다."),
                claim("cs.permission_string", "supporting", "-rwxr-xr-- 같은 ls -l 표시는 파일 형태 후 user·group·others의 rwx 세 묶음으로 읽는다."),
            ]),
        ]),
        objective("cs.virtualization_shell", "가상화와 Linux 실습", "VM·Container·WSL을 비교하고 Linux 명령·권한·셸 자동화를 설명한다.", [
            sub("cs.virtualization.models", "VM과 Container", "커널 공유와 격리 비용을 비교한다.", [
                claim("cs.vm_container", "essential", "VM은 독립 Guest OS와 커널을 올리고 Container는 호스트 커널을 공유해 프로세스 수준으로 격리한다.", category="core_understanding"),
                claim("cs.vm_isolation", "supporting", "VM은 커널까지 분리해 격리가 강하지만 Guest OS 자원 비용으로 무겁다."),
                claim("cs.container_efficiency", "supporting", "Container는 호스트 커널을 공유하여 VM보다 가밍고 빠르지만 격리 범위가 다르다."),
            ]),
            sub("cs.virtualization.environment", "WSL·Docker·macOS", "개발 환경 목적과 재현성을 고려한다.", [
                claim("cs.wsl_versions", "essential", "WSL1은 Linux 시스템 콜을 번역하고 WSL2는 경량 Linux 커널을 직접 실행한다.", category="core_understanding"),
                claim("cs.wsl_docker", "supporting", "Docker는 애플리케이션 격리·배포, WSL2는 Windows에서 Linux 개발 환경 자체를 쓰는 데 초점이 있다.", category="connection_comparison"),
                claim("cs.macos_reproducibility", "supporting", "macOS와 Linux는 Unix 계열이지만 커널·도구 차이로 셸 스크립트 재현성 문제가 생길 수 있어 Docker·OrbStack을 고려한다."),
            ]),
            sub("cs.practice.inspect", "시스템과 파일 확인", "시스템 정보와 파일 경로·권한을 확인한다.", [
                claim("cs.inspect_system", "essential", "lscpu로 CPU, free -h로 메모리, /etc/os-release로 배포판, uname -a로 커널 정보를 확인한다.", category="core_understanding"),
                claim("cs.navigate_files", "supporting", "ls·ls -a·ls -l로 파일·숨김 파일·권한을 확인하고 cd로 이동하며 pwd로 현재 경로를 본다."),
                claim("cs.read_permissions", "supporting", "/etc/shadow의 -rw-r----- 표시는 user에게 읽기·쓰기, group에게 읽기, others에게 아무 권한도 없음을 뜻한다."),
            ]),
            sub("cs.practice.shell", "권한과 셸 자동화", "chmod와 셸 스크립트 실행을 설명한다.", [
                claim("cs.chmod_risk", "essential", "chmod 644로 /etc/shadow에 others 읽기 권한을 주면 민감한 정보가 다른 사용자에게 노출될 수 있다.", category="core_understanding"),
                claim("cs.run_script", "supporting", "셸 스크립트는 chmod +x로 실행 권한을 부여한 뒤 ./run.sh와 같이 경로로 실행할 수 있다."),
                claim("cs.batch_script", "supporting", "셸 스크립트는 for 반복문과 입출력 리디렉션을 사용해 여러 입력을 프로그램에 넘기고 결과를 파일로 자동 저장할 수 있다."),
            ]),
        ]),
    ]
    return {"schema_version": "2.2.0", "lecture_id": "cs_basics", "lecture_name": "CS 기초",
            "assessment": {"mode": "selected_topic_recall", "target_seconds": 120, "max_seconds": 120,
                           "score_policy": {"essential_points": 60, "supporting_points": 20, "coverage_points": 20}},
            "top_level_objectives": objectives, "excluded_source_claims": []}


def apply_evaluation_data(processed_path: Path = PROCESSED_PATH,
                          rubric_path: Path = RUBRIC_PATH) -> None:
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id") != "cs_basics":
        raise ValueError("CS 기초 processed 파일이 아닙니다.")
    pages = {chunk["page"]: chunk for chunk in payload["chunks"]}
    if set(pages) != set(range(1, 45)):
        raise ValueError("CS 기초 PDF의 1~44쪽이 모두 존재해야 합니다.")
    payload["schema_version"] = "2.1.0"
    payload["terminology"] = TERMINOLOGY
    for number, (_, _, _, role) in PAGE_INFO.items():
        pages[number]["page_role"] = role if role in {"cover", "table_of_contents", "section_divider", "core_content", "example", "supplementary_reference", "closing"} else "core_content"
        pages[number]["term_ids"] = []
        pages[number]["evidence_units"] = []
        pages[number]["source_issues"] = []
    unit_lookup: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for item in UNITS:
        item = dict(item); page_number = item.pop("page")
        pages[page_number]["term_ids"] = list(dict.fromkeys([*pages[page_number]["term_ids"], *item["term_ids"]]))
        pages[page_number]["evidence_units"].append(item)
        unit_lookup[item["unit_id"]] = (pages[page_number], item)
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rubric = build_rubric()
    claims = {c["claim_id"]: c for obj in rubric["top_level_objectives"] for sub_item in obj["sub_objectives"] for c in sub_item["claims"]}
    if set(claims) != set(CLAIM_UNITS):
        raise ValueError("CS 기초 Claim과 Evidence 연결표가 일치하지 않습니다.")
    for claim_id, unit_ids in CLAIM_UNITS.items():
        target = claims[claim_id]; term_ids: list[str] = []
        for unit_id in unit_ids:
            chunk, source = unit_lookup[unit_id]
            term_ids.extend(source["term_ids"])
            target["evidence"].append({"page": chunk["page"], "chunk_id": chunk["chunk_id"], "unit_id": unit_id,
                                       "source_excerpt": source["source_excerpt"], "source_status": "verified", "review_note": ""})
        target["term_ids"] = list(dict.fromkeys(term_ids))
    rubric_path.parent.mkdir(parents=True, exist_ok=True)
    rubric_path.write_text(json.dumps(rubric, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    apply_evaluation_data()
    print(f"updated: {PROCESSED_PATH.relative_to(ROOT)}")
    print(f"updated: {RUBRIC_PATH.relative_to(ROOT)}")
