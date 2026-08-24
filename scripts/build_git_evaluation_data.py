from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "git.json"
RUBRIC_PATH = ROOT / "data" / "evaluation" / "rubrics" / "git.json"


def term(term_id: str, ko: str, en: str = "", *, abbreviations=None, aliases=None,
         symbols=None, not_equivalent_to=None) -> dict[str, Any]:
    return {"term_id": term_id, "canonical_ko": ko, "canonical_en": en,
            "abbreviations": abbreviations or [], "accepted_aliases": aliases or [],
            "symbols": symbols or [], "not_equivalent_to": not_equivalent_to or []}


TERMINOLOGY = [
    term("vcs", "버전 관리 시스템", "version control system", abbreviations=["VCS"]),
    term("local_vcs", "로컬 버전 관리", "local version control system"),
    term("centralized_vcs", "중앙집중식 버전 관리", "centralized version control system", abbreviations=["CVCS"]),
    term("distributed_vcs", "분산 버전 관리", "distributed version control system", abbreviations=["DVCS"]),
    term("git", "Git", "Git", aliases=["깃"]),
    term("github", "GitHub", "GitHub", aliases=["깃허브"], not_equivalent_to=["git"]),
    term("repository", "저장소", "repository", abbreviations=["repo"], aliases=["리포지토리"]),
    term("local_repository", "로컬 저장소", "local repository"),
    term("remote_repository", "원격 저장소", "remote repository"),
    term("working_directory", "작업 디렉터리", "working directory", aliases=["working tree", "워크트리"]),
    term("staging_area", "스테이징 영역", "staging area", aliases=["index", "인덱스"]),
    term("commit", "커밋", "commit"), term("branch", "브랜치", "branch"),
    term("main_branch", "메인 브랜치", "main branch", aliases=["main"]),
    term("remote", "리모트", "remote"), term("origin", "origin", "origin"),
    term("clone", "복제", "clone"), term("push", "푸시", "push"),
    term("pull", "풀", "pull"), term("fetch", "페치", "fetch"),
    term("merge", "병합", "merge"), term("merge_conflict", "병합 충돌", "merge conflict", aliases=["conflict"]),
    term("head", "HEAD", "HEAD"), term("common_ancestor", "공통 조상", "common ancestor", aliases=["merge base"]),
    term("fast_forward", "Fast-forward 병합", "fast-forward merge", abbreviations=["FF"]),
    term("rebase", "리베이스", "rebase"), term("squash_merge", "Squash 병합", "squash merge"),
    term("restore", "복원", "restore"), term("revert", "되돌림 커밋", "revert"),
    term("gitignore", ".gitignore", ".gitignore"), term("pull_request", "Pull Request", "pull request", abbreviations=["PR"]),
    term("code_review", "코드 리뷰", "code review"), term("ruleset", "브랜치 규칙", "branch ruleset"),
]


PAGE_INFO: dict[int, tuple[str, list[str], str, str]] = {
    1: ("Git 강의 표지", ["Git"], "Git 강의의 표지이다.", "cover"),
    2: ("강의 목차", ["Git 기본 개념", "Git 명령", "협업"], "Git 기본 개념, 명령, 협업 순서로 구성된다.", "table_of_contents"),
    3: ("Git 기본 개념", ["Git"], "Git 기본 개념 섹션의 시작 페이지이다.", "section_divider"),
    4: ("버전 관리 시스템", ["VCS", "Local VCS", "CVCS", "DVCS"], "VCS는 코드 변경 이력을 관리하며 로컬·중앙집중식·분산 방식으로 발전했다.", "core_content"),
    5: ("Git을 쓰는 이유", ["변경 이력", "복구", "협업"], "Git은 변경 내역 보존, 코드 복구, 안전한 수정과 협업을 돕는다.", "core_content"),
    6: ("Git과 GitHub", ["Git", "GitHub", "로컬 저장소", "원격 저장소"], "Git은 버전 관리 도구이고 GitHub는 원격 저장소를 제공하는 서비스이며 둘은 push와 pull로 동기화한다.", "core_content"),
    7: ("Git 설치와 기본 설정", ["git config", "user.name", "user.email", "main"], "Git 설치를 확인하고 사용자 이름·이메일, 기본 브랜치와 편집기를 전역 설정한다.", "procedure"),
    8: ("Git diff 도구 설정", ["git config", "difftool", "VS Code"], "VS Code를 diff 도구로 설정하고 전역 설정 파일을 확인한다.", "procedure"),
    9: ("Git 데이터 흐름", ["Working Directory", "Staging Area", "Local Repository", "Remote Repository"], "수정은 작업 디렉터리에서 시작해 스테이징 영역을 거쳐 로컬 커밋이 되고 원격 저장소와 동기화된다.", "core_content"),
    10: ("Git 그래프", ["commit graph", "branch"], "커밋과 브랜치가 분기·병합되는 이력을 그래프로 보여준다.", "example"),
    11: ("Git 명령", ["Git command"], "Git 명령 섹션의 시작 페이지이다.", "section_divider"),
    12: ("Git 협업 시나리오", ["main", "clone", "branch", "merge"], "A가 main을 올리고 B가 clone한 뒤 별도 브랜치에서 작업해 main에 병합하는 흐름이다.", "core_content"),
    13: ("저장소 초기화", ["git init", "repository"], "git init은 기존 로컬 폴더를 Git 저장소로 만들고 추적을 시작한다.", "procedure"),
    14: ("스테이징과 커밋", ["git add", "git commit", "git status"], "git add로 변경을 스테이징하고 commit으로 로컬 이력에 남기며 status로 상태를 확인한다.", "procedure"),
    15: ("원격 연결과 최초 push", ["remote", "origin", "push", "upstream"], "원격 origin을 연결하고 로컬 main을 push하며 -u로 기본 추적 대상을 설정한다.", "procedure"),
    16: ("저장소 clone", ["git clone", "remote"], "git clone은 원격 저장소의 이력과 파일을 내려받고 원격 연결도 설정한다.", "procedure"),
    17: ("브랜치 생성", ["git switch", "branch"], "git switch -c로 기능 브랜치를 만들고 이동해 main과 분리된 작업 공간을 확보한다.", "procedure"),
    18: ("main 갱신", ["git switch", "git pull", "main"], "main으로 이동한 뒤 원격의 최신 main을 pull해 로컬을 갱신한다.", "procedure"),
    19: ("병합과 push", ["git merge", "git push"], "기능 브랜치를 main에 병합한 뒤 갱신된 main을 원격에 push한다.", "procedure"),
    20: ("충돌 해결", ["merge conflict", "git add", "git commit"], "충돌 구간을 사람이 수정하고 add와 commit으로 해결 결과를 확정한다.", "procedure"),
    21: ("충돌 표시 읽기", ["HEAD", "Current Change", "Incoming Change"], "Current Change는 현재 브랜치 HEAD, Incoming Change는 병합 대상 브랜치의 내용이다.", "core_content"),
    22: ("3-way merge", ["common ancestor", "HEAD", "fast-forward"], "3-way merge는 공통 조상과 양쪽 현재 상태를 비교하며, 현재 브랜치가 분기 전 상태면 fast-forward가 가능하다.", "core_content"),
    23: ("Rebase와 Squash 병합", ["rebase", "fast-forward", "squash"], "rebase는 브랜치 시작점을 최신 main 뒤로 옮기고, squash 병합은 여러 변경을 하나의 커밋으로 합친다.", "core_content"),
    24: ("브랜치 삭제", ["git branch -d", "git push --delete"], "작업이 끝난 로컬·원격 브랜치를 각각 삭제한다.", "procedure"),
    25: ("git restore", ["restore", "staging area", "working directory"], "restore --staged는 스테이징만 취소하고 restore 파일명은 작업 파일 변경 자체를 되돌린다.", "core_content"),
    26: ("git revert", ["revert", "commit"], "revert는 기존 커밋을 지우지 않고 반대 변경을 담은 새 커밋을 만든다.", "core_content"),
    27: ("Git 협업", ["collaboration"], "Git 협업 섹션의 시작 페이지이다.", "section_divider"),
    28: (".gitignore", [".gitignore", "secret", "cache", "pattern"], ".gitignore는 비밀정보·캐시·개인 설정 등 추적하지 않을 경로와 예외 패턴을 지정한다.", "core_content"),
    29: ("Pull Request 협업 예절", ["branch", "Pull Request", "code review", "commit convention"], "main 직접 push를 피하고 기능 브랜치와 PR·리뷰를 사용하며 의미 있는 브랜치명과 커밋 메시지를 작성한다.", "core_content"),
    30: ("리뷰 코멘트", ["code review", "comment"], "PR 작성자와 리뷰어가 필요한 코멘트를 주고받는다.", "example"),
    31: ("브랜치 ruleset", ["branch ruleset", "protection"], "브랜치 ruleset으로 main 변경에 리뷰·검사 같은 보호 규칙을 적용한다.", "core_content"),
    32: ("강의 마무리", ["Git"], "Git 강의의 종료 페이지이다.", "closing"),
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
    U("git_p4_u01", 4, "definition", "VCS = 코드 변경 이력 관리자", "VCS는 코드 변경 이력을 보존하고 관리한다.", ["vcs"]),
    U("git_p4_u02", 4, "comparison", "Local VCS / CVCS 중앙집중식 / DVCS 분산 버전관리 시스템", "버전 관리는 저장 위치와 복제 방식에 따라 로컬·중앙집중식·분산형으로 나뉜다.", ["local_vcs", "centralized_vcs", "distributed_vcs"]),
    U("git_p5_u01", 5, "interpretation", "파일 변경 내역 보존 및 관리 / 코드 복구 / 안전한 코드 수정 및 업데이트 / 협업", "Git은 이력·복구·안전한 변경·협업을 지원한다.", ["git", "vcs"]),
    U("git_p6_u01", 6, "comparison", "로컬 저장소: 내 컴퓨터 안 / 원격 저장소: GitHub 같은 서버 / Git ≠ GitHub", "Git과 GitHub, 로컬과 원격 저장소는 서로 다른 개념이다.", ["git", "github", "local_repository", "remote_repository"]),
    U("git_p7_u01", 7, "procedure", "git config --global user.name / user.email / init.defaultBranch main", "전역 설정은 커밋 작성자 정보와 기본 브랜치 같은 사용자 기본값을 정한다.", ["git", "main_branch"]),
    U("git_p9_u01", 9, "procedure", "Working Directory → Staging Area → Local Repository → Remote Repository", "변경은 작업·선별·로컬 기록·공유 단계를 이동한다.", ["working_directory", "staging_area", "local_repository", "remote_repository", "commit", "push"]),
    U("git_p12_u01", 12, "procedure", "main을 만들고 올린 뒤 clone해서 새로운 브랜치에서 작업한 후 main에 merge", "협업은 최신 저장소 복제, 분리된 브랜치 작업, 병합으로 진행한다.", ["main_branch", "clone", "branch", "merge"]),
    U("git_p13_u01", 13, "procedure", "git init: 로컬 폴더를 Git 저장소로 만들기", "init은 로컬 폴더에 Git 저장소를 초기화한다.", ["git", "repository"]),
    U("git_p14_u01", 14, "procedure", "git add: 커밋 대상으로 올리기 / git commit: 로컬 저장버전으로 남기기 / git status: 작업 상태 파악", "add·commit·status의 역할은 서로 다르다.", ["staging_area", "commit", "working_directory"]),
    U("git_p15_u01", 15, "procedure", "git remote add origin <URL> / git push -u origin main", "원격을 등록하고 최초 push에서 upstream을 설정한다.", ["remote", "origin", "push", "main_branch"]),
    U("git_p16_u01", 16, "procedure", "git clone <URL>: 저장소 통째로 다운로드 + 연결까지 자동 설정", "clone은 파일과 이력을 받고 원격 연결도 만든다.", ["clone", "repository", "remote"]),
    U("git_p17_u01", 17, "procedure", "git switch -c login: 브랜치 새로 만들고 이동", "기능 브랜치를 생성하고 그 브랜치로 이동한다.", ["branch", "main_branch"]),
    U("git_p18_u01", 18, "procedure", "git switch main / git pull origin main", "main으로 이동한 뒤 원격 최신 내용을 가져와 합친다.", ["main_branch", "pull", "origin"]),
    U("git_p19_u01", 19, "procedure", "git merge login / git push origin main", "기능을 main에 병합하고 원격에 공유한다.", ["merge", "push", "main_branch"]),
    U("git_p20_u01", 20, "procedure", "수동으로 수정하고 conflict 해결 후 git add, git commit", "충돌은 내용을 검토·수정하고 새 병합 커밋으로 확정한다.", ["merge_conflict", "commit", "staging_area"]),
    U("git_p21_u01", 21, "comparison", "Current Change (HEAD): 지금 브랜치 / Incoming Change: 합쳐오려는 브랜치", "충돌 표시는 현재 측과 들어오는 측을 구분한다.", ["head", "branch", "merge_conflict"]),
    U("git_p22_u01", 22, "relation", "공통 조상, main 현재 상태, 병합 대상 현재 상태를 참고 / fast-forward merge", "3-way merge는 세 상태를 비교하고 조건이 맞으면 fast-forward한다.", ["common_ancestor", "head", "merge", "fast_forward"]),
    U("git_p23_u01", 23, "comparison", "rebase: 브랜치 시작점을 main 끝으로 이동 / squash: 브랜치 커밋을 main의 새 커밋 하나로", "rebase와 squash는 이력을 정리하는 방식이 다르다.", ["rebase", "fast_forward", "squash_merge"]),
    U("git_p25_u01", 25, "comparison", "restore --staged: add만 취소 / restore 파일: 파일 수정 자체 취소", "restore 대상에 따라 스테이징 또는 작업 변경을 되돌린다.", ["restore", "staging_area", "working_directory"]),
    U("git_p26_u01", 26, "definition", "git revert <hash>: 그 커밋을 취소하는 새 커밋을 생성", "revert는 공개 이력을 보존하면서 반대 변경을 추가한다.", ["revert", "commit"]),
    U("git_p28_u01", 28, "definition", ".gitignore: Git이 추적하지 말아야 할 파일이나 폴더 목록", "비밀정보·생성물·개인 설정을 추적에서 제외한다.", ["gitignore"]),
    U("git_p28_u02", 28, "procedure", "filename / *.ext / prefix* / !filename / dirname/", "파일·확장자·접두어·예외·디렉터리 패턴을 지정한다.", ["gitignore"]),
    U("git_p29_u01", 29, "procedure", "main에 바로 push하지 않고 브랜치를 새로 파서 코드 리뷰어를 등록", "보호 브랜치에는 PR과 리뷰를 거쳐 변경을 통합한다.", ["main_branch", "branch", "pull_request", "code_review"]),
    U("git_p29_u02", 29, "interpretation", "브랜치 이름과 커밋 메시지는 동료들이 내용을 알 수 있게", "의도를 드러내는 이름과 메시지가 협업 이력을 이해하기 쉽게 한다.", ["branch", "commit"]),
    U("git_p30_u01", 30, "interpretation", "필요한 경우 코멘트를 남기고 리뷰어도 코멘트를 남긴다", "리뷰는 양방향 피드백 과정이다.", ["code_review", "pull_request"]),
    U("git_p31_u01", 31, "procedure", "Branch ruleset", "ruleset은 중요 브랜치에 병합 조건과 보호 규칙을 적용한다.", ["ruleset", "main_branch"], "visual"),
]


CLAIM_UNITS = {
    "git.vcs_purpose": ["git_p4_u01", "git_p5_u01"], "git.vcs_types": ["git_p4_u02"],
    "git.git_github": ["git_p6_u01"], "git.local_remote": ["git_p6_u01"],
    "git.global_config": ["git_p7_u01"],
    "git.data_flow": ["git_p9_u01"], "git.staging_role": ["git_p9_u01", "git_p14_u01"],
    "git.add_commit_status": ["git_p14_u01"],
    "git.remote_push": ["git_p15_u01"], "git.clone": ["git_p16_u01"],
    "git.branch_work": ["git_p17_u01"], "git.update_main": ["git_p18_u01"],
    "git.collaboration_flow": ["git_p12_u01", "git_p17_u01", "git_p18_u01", "git_p19_u01"],
    "git.conflict_resolution": ["git_p20_u01", "git_p21_u01"],
    "git.three_way": ["git_p22_u01"], "git.fast_forward": ["git_p22_u01"],
    "git.rebase": ["git_p23_u01"],
    "git.restore": ["git_p25_u01"], "git.revert": ["git_p26_u01"],
    "git.ignore_purpose": ["git_p28_u01"], "git.ignore_patterns": ["git_p28_u02"],
    "git.pr_review": ["git_p29_u01", "git_p30_u01"], "git.naming": ["git_p29_u02"],
    "git.review_feedback": ["git_p30_u01"], "git.protected_main": ["git_p29_u01", "git_p31_u01"],
    "git.ruleset_checks": ["git_p31_u01"],
}


CRITICAL_ERRORS = {
    "git.git_github": ["Git과 GitHub가 완전히 동일한 프로그램이라고 설명"],
    "git.data_flow": ["commit이 원격 저장소에 자동으로 업로드된다고 설명", "git add가 원격 저장소에 변경을 전송한다고 설명"],
    "git.add_commit_status": ["git add가 커밋을 생성하거나 push까지 수행한다고 설명"],
    "git.clone": ["clone이 현재 로컬 변경을 원격에 업로드하는 명령이라고 설명"],
    "git.update_main": ["pull이 로컬 변경을 원격에 업로드하는 명령이라고 설명"],
    "git.conflict_resolution": ["충돌 표시 중 한쪽을 무조건 선택하면 검토 없이 항상 올바르게 해결된다고 설명"],
    "git.fast_forward": ["모든 merge가 항상 fast-forward라고 설명"],
    "git.rebase": ["공유된 main에서 rebase를 해도 이력이 절대 바뀌지 않는다고 설명"],
    "git.restore": ["restore --staged가 작업 파일의 수정까지 삭제한다고 설명"],
    "git.revert": ["revert가 기존 커밋을 이력에서 삭제한다고 설명"],
    "git.ignore_purpose": ["이미 추적 중인 비밀정보가 .gitignore에 추가되는 즉시 과거 이력에서도 삭제된다고 설명"],
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
        objective("git.foundations", "Git과 버전 관리의 기초", "VCS의 목적, Git·GitHub와 네 저장 영역의 관계를 설명한다.", [
            sub("git.foundation.vcs", "버전 관리의 목적", "VCS의 필요성과 유형을 설명한다.", [
                claim("git.vcs_purpose", "essential", "VCS는 코드 변경 이력을 보존·관리하여 복구, 안전한 수정과 협업을 돕는다.", category="core_understanding"),
                claim("git.vcs_types", "supporting", "버전 관리는 저장 위치와 복제 방식에 따라 Local VCS, 중앙집중식 CVCS, 분산형 DVCS로 구분된다.", category="connection_comparison"),
            ]),
            sub("git.foundation.platform", "Git·GitHub와 저장소", "도구와 호스팅 서비스, 로컬과 원격을 구분한다.", [
                claim("git.git_github", "essential", "Git은 분산 버전 관리 도구이고 GitHub는 Git 원격 저장소와 협업 기능을 제공하는 서비스로 서로 동일하지 않다.", category="core_understanding"),
                claim("git.local_remote", "supporting", "로컬 저장소는 내 컴퓨터의 커밋 이력이고 원격 저장소는 GitHub 같은 공유 서버의 이력이며 push·pull로 동기화한다."),
            ]),
            sub("git.foundation.flow", "Git 데이터 흐름", "작업 변경이 네 영역을 이동하는 과정을 설명한다.", [
                claim("git.data_flow", "essential", "파일 수정은 Working Directory에서 시작해 git add로 Staging Area에 선별되고 commit으로 Local Repository에 기록된 뒤 push로 Remote Repository에 공유된다.", category="core_understanding"),
                claim("git.staging_role", "supporting", "Staging Area는 다음 커밋에 포함할 변경만 고르는 중간 영역이며 git status로 수정·스테이징 상태를 확인한다."),
                claim("git.global_config", "supporting", "git config --global의 user.name·user.email은 커밋 작성자 정보를, init.defaultBranch는 새 저장소의 기본 브랜치명을 설정한다."),
            ]),
        ]),
        objective("git.workflow", "브랜치 작업과 이력 관리", "저장소 시작부터 브랜치 병합·충돌·복구까지 설명한다.", [
            sub("git.workflow.start", "저장소 시작과 원격 연결", "init·clone·remote·push의 역할을 구분한다.", [
                claim("git.add_commit_status", "essential", "git add는 변경을 스테이징하고 commit은 스테이징된 변경을 로컬 이력에 남기며 status는 현재 상태를 보여준다.", category="core_understanding"),
                claim("git.remote_push", "supporting", "git remote add origin은 원격 주소를 등록하고 git push -u origin main은 main을 올리면서 기본 추적 대상을 설정한다."),
                claim("git.clone", "supporting", "git clone은 원격 저장소의 파일과 커밋 이력을 내려받고 원격 연결도 자동 설정한다."),
            ]),
            sub("git.workflow.branch", "브랜치 협업 흐름", "기능 브랜치에서 작업하고 최신 main에 통합한다.", [
                claim("git.branch_work", "essential", "git switch -c로 main과 분리된 기능 브랜치를 만들고 이동해 안전하게 작업한다.", category="core_understanding"),
                claim("git.update_main", "supporting", "병합 전 main으로 이동해 pull로 원격의 최신 main을 로컬에 반영한다."),
                claim("git.collaboration_flow", "supporting", "협업의 기본 흐름은 clone·기능 브랜치 작업·최신 main 반영·검토 후 병합·push다.", category="connection_comparison"),
            ]),
            sub("git.workflow.merge", "병합과 충돌", "3-way merge와 충돌 해결을 설명한다.", [
                claim("git.conflict_resolution", "essential", "병합 충돌은 Current와 Incoming 내용을 맥락에 맞게 수동 수정한 뒤 add와 commit으로 해결 결과를 확정한다.", category="core_understanding"),
                claim("git.three_way", "supporting", "3-way merge는 공통 조상, 현재 브랜치, 병합 대상 브랜치의 세 상태를 비교한다."),
                claim("git.fast_forward", "supporting", "현재 브랜치가 분기 이후 새 커밋이 없으면 포인터만 앞으로 옮기는 fast-forward 병합이 가능하다."),
            ]),
            sub("git.workflow.history", "이력 정리와 복구", "rebase·squash·restore·revert의 차이를 설명한다.", [
                claim("git.rebase", "essential", "rebase는 기능 브랜치의 시작점을 최신 main 뒤로 옮기도록 커밋을 다시 적용해 선형 이력을 만든다.", category="core_understanding"),
                claim("git.restore", "supporting", "git restore --staged는 스테이징만 취소하고 git restore 파일명은 작업 파일 변경을 되돌린다."),
                claim("git.revert", "supporting", "git revert는 기존 커밋을 삭제하지 않고 그 효과를 취소하는 새 커밋을 만든다."),
            ]),
        ]),
        objective("git.collaboration", "Git 협업 규칙과 코드 리뷰", ".gitignore, PR, 리뷰와 보호 브랜치 운영을 설명한다.", [
            sub("git.collab.ignore", ".gitignore", "추적 제외 목적과 패턴을 설명한다.", [
                claim("git.ignore_purpose", "essential", ".gitignore는 API key 같은 비밀정보, 캐시·로그·OS 임시 파일과 개인 설정을 새로 추적하지 않도록 지정한다.", category="core_understanding"),
                claim("git.ignore_patterns", "supporting", "파일명, *.확장자, prefix*, 디렉터리/ 패턴으로 제외하고 !파일명으로 특정 예외를 다시 포함할 수 있다."),
            ]),
            sub("git.collab.pr", "Pull Request와 리뷰", "브랜치 기반 변경 제안과 피드백을 설명한다.", [
                claim("git.pr_review", "essential", "main에 직접 push하기보다 기능 브랜치에서 Pull Request를 만들고 리뷰어와 코멘트를 주고받은 뒤 병합한다.", category="core_understanding"),
                claim("git.naming", "supporting", "브랜치명과 커밋 메시지는 변경 목적을 동료가 바로 이해할 수 있도록 명확하게 작성한다."),
                claim("git.review_feedback", "supporting", "코드 리뷰는 작성자와 리뷰어가 필요한 코멘트를 주고받아 변경의 문제와 개선점을 확인하는 과정이다."),
            ]),
            sub("git.collab.protection", "보호 브랜치", "main의 품질과 안정성을 보호한다.", [
                claim("git.protected_main", "essential", "main 브랜치 ruleset은 승인된 리뷰나 검사 통과 같은 조건을 요구해 무검토 직접 변경을 막는다.", category="core_understanding"),
                claim("git.ruleset_checks", "supporting", "브랜치 ruleset으로 PR 승인, 상태 검사 같은 병합 조건을 중앙에서 일관되게 적용할 수 있다."),
            ]),
        ]),
    ]
    return {"schema_version": "2.2.0", "lecture_id": "git", "lecture_name": "Git",
            "assessment": {"mode": "selected_topic_recall", "target_seconds": 120, "max_seconds": 120,
                           "score_policy": {"essential_points": 60, "supporting_points": 20, "coverage_points": 20}},
            "top_level_objectives": objectives, "excluded_source_claims": []}


def apply_evaluation_data(processed_path: Path = PROCESSED_PATH,
                          rubric_path: Path = RUBRIC_PATH) -> None:
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    if payload.get("lecture_id") != "git":
        raise ValueError("Git processed 파일이 아닙니다.")
    pages = {chunk["page"]: chunk for chunk in payload["chunks"]}
    if set(pages) != set(range(1, 33)):
        raise ValueError("Git PDF의 1~32쪽이 모두 존재해야 합니다.")
    payload["schema_version"] = "2.1.0"
    payload["terminology"] = TERMINOLOGY
    valid_roles = {"cover", "table_of_contents", "section_divider", "core_content", "example", "supplementary_reference", "closing"}
    for number, (_, _, _, role) in PAGE_INFO.items():
        pages[number]["page_role"] = role if role in valid_roles else "core_content"
        pages[number]["term_ids"] = []
        pages[number]["evidence_units"] = []
        pages[number]["source_issues"] = []
    unit_lookup: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for item in UNITS:
        item = dict(item)
        page_number = item.pop("page")
        pages[page_number]["term_ids"] = list(dict.fromkeys([*pages[page_number]["term_ids"], *item["term_ids"]]))
        pages[page_number]["evidence_units"].append(item)
        unit_lookup[item["unit_id"]] = (pages[page_number], item)
    processed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rubric = build_rubric()
    claims = {c["claim_id"]: c for obj in rubric["top_level_objectives"] for sub_item in obj["sub_objectives"] for c in sub_item["claims"]}
    if set(claims) != set(CLAIM_UNITS):
        raise ValueError("Git Claim과 Evidence 연결표가 일치하지 않습니다.")
    for claim_id, unit_ids in CLAIM_UNITS.items():
        target = claims[claim_id]
        term_ids: list[str] = []
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
