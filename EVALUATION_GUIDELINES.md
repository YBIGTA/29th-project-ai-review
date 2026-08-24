# Rubric 평가 가이드

## 평가 범위

사용자가 선택한 `lecture_id + objective_id` 조합만 평가합니다. 강의 전체나 다른
상위 학습목표의 누락은 감점하지 않습니다. 발화 제한은 120초이며 시간 자체에는
점수를 주지 않습니다.

## 입력

- STT 원문과 보정문
- 의미 단위 Segment
- 선택한 상위 학습목표의 하위 목표와 Claim 전체
- 각 Claim에 직접 연결된 processed Evidence
- 선택 Claim과 연결된 한국어·영어·약어·기호 용어 정보
- 강의안 오류를 기록한 `excluded_source_claims`

임베딩 검색과 코사인 거리는 사용하지 않습니다.

## Claim 판정

| 판정 | 기준 | 값 |
|---|---|---:|
| `correct` | 필수 의미가 정확하고 미해결 오개념·모순이 없음 | 1.0 |
| `mostly_correct` | 필수 의미는 맞고 비핵심 생략·모호함만 있음 | 0.8 |
| `partial` | 필수 요소 일부만 맞거나 맞는 내용과 틀린 내용이 섞임 | 0.5 |
| `incorrect` | 핵심 정의·조건·관계·방향이 무너짐 | 0.0 |
| `not_addressed` | 전체 발화에도 의미 있는 설명이 없음 | 0.0 |

표현이 달라도 의미가 같으면 인정합니다. 단순 키워드 나열은 설명으로 인정하지
않습니다. `incorrect`와 `not_addressed`를 반드시 구분합니다. 명시적 오개념이나
미해결 충돌에는 `mostly_correct`를 사용하지 않습니다. 앞선 오류를 분명히 취소하고
올바르게 다시 설명한 경우만 `self_corrected`로 인정합니다.

## 점수

- Essential 60점: 모든 하위 목표의 essential Claim 가중 평균
- Supporting 20점: N개 최고 판정 평균과 실제 언급한 supporting 정확도 중 낮은 값
- Coverage 20점: 하위 목표별 essential 판정과 supporting 보완 규칙. `incorrect`와
  미해결 충돌이 있는 하위 목표에는 각각 상한 적용

LLM은 점수를 만들지 않습니다. `src/evaluation.py`가 구조화 판정을 검증한 뒤
결정적으로 계산합니다.

## Evidence 원칙

- 기초통계 processed schema 2.1.0은 Claim의 `chunk_id + unit_id`로 atomic evidence만 조회합니다.
- 다른 강의는 schema 2.1.0 확장 전까지 기존 chunk 단위 조회를 유지합니다.
- 판정에 사용한 chunk만 `source_chunk_ids_used`에 기록합니다.
- `source_excerpt`는 PDF에서 직접 확인한 텍스트·공식·시각 정보여야 하며,
  `normalized_explanation`과 분리합니다.
- 원문에 없는 외부 지식을 정답 기준으로 추가하지 않습니다.
- 강의안 자체의 오류는 `excluded_source_claims`에 기록하고 정답으로 쓰지 않습니다.
- 같은 의미 반복은 대표 Quote 하나만 남기고, 서로 보완하거나 충돌·정정하는
  내용은 여러 `evidence_spans`로 보존합니다.
- 각 Quote는 지정 Segment에서 가져온 연속 원문이어야 하며 `supports`,
  `contradicts`, `corrects` 관계를 표시합니다.

## 결과

- 60+20+20 세부 점수와 총점
- 하위 목표별 충족 비율
- 정확하게 설명한 Claim
- 누락한 Claim
- 잘못 설명한 Claim과 이유
- 다음 복습 제안

모든 Claim 판정에는 `source_chunk_ids_used`, `conflict_status`, `evidence_spans`,
판정 이유가 포함되어야 합니다. 코드는 Claim·출처·Segment·정확 Quote를 검증하고,
실패하면 오류를 반영한 전체 JSON을 한 번 재요청합니다. 재검증도 실패하면 채점하지
않고 마지막 응답을 `.invalid.json`으로 보존합니다.
