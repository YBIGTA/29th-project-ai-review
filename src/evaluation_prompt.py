from __future__ import annotations

import json
from typing import Any

from src.evaluation_schemas import LectureRubric, TopLevelObjective
from src.schemas import TranscriptSegment


EVALUATION_SYSTEM_PROMPT = """당신은 강의자료 기반 구술 복습 평가자입니다.
선택된 상위 학습목표의 Claim만 판정하세요. 표현이 달라도 의미가 같으면 인정하되,
한국어·영어·약어·기호 또는 허용된 동의 표현 중 무엇을 사용해도 의미가 같으면
동일하게 인정하세요. 단순 키워드 나열은 이해로 인정하지 마세요. 강의자료 자체의
제외 주장은 정답으로 사용하지 마세요. 명시적인 오개념이나 해결되지 않은 모순이
있으면 맞는 부분만 골라서 판정하지 마세요. 모든 Claim을 빠짐없이 한 번씩 판정하고
제공된 구조로 반환하세요."""


def build_evaluation_prompt(
    *,
    rubric: LectureRubric,
    branch: TopLevelObjective,
    transcript: str,
    segments: list[TranscriptSegment],
    evidence_chunks: dict[str, dict[str, Any]],
    terminology: list[dict[str, Any]],
) -> str:
    selected_objective = {
        "objective_id": branch.objective_id,
        "title": branch.title,
        "selection_description": branch.selection_description,
        "sub_objectives": [
            {
                "sub_objective_id": sub.sub_objective_id,
                "title": sub.title,
                "summary": sub.summary,
                "claims": [
                    {
                        "claim_id": claim.claim_id,
                        "role": claim.role,
                        "category": claim.category,
                        "text": claim.text,
                        "evaluation_criteria": (
                            claim.evaluation_criteria.model_dump(mode="json")
                            if claim.evaluation_criteria is not None
                            else {
                                "required_elements": [claim.text],
                                "critical_errors": [],
                            }
                        ),
                        "term_ids": claim.term_ids,
                        "evidence_links": [
                            {
                                "chunk_id": evidence.chunk_id,
                                "unit_id": evidence.unit_id,
                            }
                            for evidence in claim.evidence
                        ],
                    }
                    for claim in sub.claims
                ],
            }
            for sub in branch.sub_objectives
        ],
    }
    selected_chunk_ids = set(evidence_chunks)
    payload = {
        "lecture_id": rubric.lecture_id,
        "lecture_name": rubric.lecture_name,
        "selected_objective": selected_objective,
        "excluded_source_claims": [
            item.model_dump(mode="json")
            for item in rubric.excluded_source_claims
            if item.chunk_id in selected_chunk_ids
        ],
        "transcript_full": transcript,
        "segments": [segment.model_dump(mode="json") for segment in segments],
        "terminology": terminology,
        "evidence_chunks": evidence_chunks,
    }
    rules = {
        "judgments": {
            "correct": "필수 의미가 정확하고 미해결 오개념·모순이 없다.",
            "mostly_correct": "필수 의미는 맞고 비핵심 생략·모호함만 있다. 명시적 오개념이나 미해결 모순에는 사용할 수 없다.",
            "partial": "필수 요소 일부만 맞거나 맞는 내용과 틀린 내용이 섞였지만 핵심 전체가 무너지지는 않았다.",
            "incorrect": "핵심 정의·조건·관계·방향을 반대로 설명하거나 critical error가 핵심 이해를 무너뜨린다.",
            "not_addressed": "segment와 전체 발화문 어디에도 의미 있는 설명이 없다.",
        },
        "conflict_status": {
            "none": "서로 충돌하는 설명이 없다.",
            "self_corrected": "앞선 오류를 명시적으로 인정하고 뒤에서 정확한 내용으로 정정했다.",
            "unresolved": "서로 충돌하는 설명이 있으나 명시적으로 해결하지 않았다.",
        },
        "required": [
            "선택 분기의 모든 claim_id를 정확히 한 번 판정한다.",
            "각 Claim마다 전체 발화문과 모든 segment를 확인하고, 맞는 부분만 선택해 오개념·충돌을 누락하지 않는다.",
            "evidence_spans를 만들기 전에 먼저 인용할 segment를 결정하고, 그 다음 해당 segment의 text에서 quote를 문자 그대로 복사한다.",
            "segment_id는 quote를 작성한 뒤 추측해서 붙이지 말고, quote가 실제로 포함된 segment의 ID만 사용한다.",
            "모든 segment의 text를 검색해도 quote가 정확히 포함되지 않으면 해당 evidence_span을 만들지 않는다.",
            "evidence_spans에는 판정에 실제 사용한 최소 비중복 근거를 기록한다.",
            "같은 의미를 반복한 segment는 가장 명확하고 완전한 quote 하나만 남긴다.",
            "서로 다른 필수 요소를 보완한 segment는 각각 supports로 남긴다.",
            "Claim과 충돌하는 발화는 contradicts로, 앞선 오류를 명시적으로 정정한 발화는 corrects로 남긴다.",
            "충돌이나 정정이 있으면 관련된 앞뒤 evidence span을 모두 남긴다.",
            "각 quote는 지정한 segment에 실제로 존재하는 하나의 연속 문자열을 글자·띄어쓰기·문장부호 그대로 복사한다.",
            "quote의 맞춤법, 띄어쓰기, 문장부호, 조사, 어미, 영문 표기를 교정하거나 요약하지 않는다.",
            "서로 다른 segment의 내용을 하나의 quote로 합치지 않는다.",
            "segment_id와 quote의 포함 관계를 출력 전에 다시 확인한다. 둘이 일치하지 않으면 segment_id를 바꾸거나 evidence_span을 생략한다.",
            "quote를 요약하거나 어미·문장부호를 바꾸거나 서로 떨어진 문장을 생략부호로 합치지 않는다.",
            "뒤에 올바른 문장이 나왔다는 이유만으로 정정으로 보지 않는다. '잘못 말했다', '정정하면', '아니고 정확히는'처럼 앞선 오류를 취소하는 맥락이 명확해야 self_corrected다.",
            "self_corrected는 최종 정정 내용의 완전성에 따라 correct, mostly_correct 또는 partial로 판정한다.",
            "unresolved 충돌은 핵심 전체가 무너지면 incorrect, 일부 정확한 이해가 남으면 partial로 판정한다.",
            "critical_errors에 해당하는 명시적 오개념이 있으면 mostly_correct로 판정하지 않는다.",
            "source_chunk_ids_used에는 해당 Claim evidence에 연결된 chunk만 기록한다.",
            "incorrect와 not_addressed를 구분한다.",
            "segment에서 못 찾으면 전체 발화문을 다시 확인한 뒤 not_addressed로 판정한다.",
            "terminology의 canonical_ko, canonical_en, abbreviations, accepted_aliases, symbols는 같은 개념의 표현으로 인정한다.",
            "not_equivalent_to에 연결된 개념은 서로 같은 뜻으로 인정하지 않는다.",
            "evidence_units의 normalized_explanation은 의미 판정에, source_excerpt는 강의안 근거 확인에 사용한다.",
            "점수는 계산하지 않는다.",
        ],
    }
    return (
        "다음 입력을 기준으로 Claim별 판정을 작성하세요.\n\n"
        f"판정 규칙:\n{json.dumps(rules, ensure_ascii=False, indent=2)}\n\n"
        f"평가 입력:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
