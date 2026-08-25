# 2분 선택 주제 구술 평가 및 Rubric 기준서

> 상태: 현재 평가 구조 구현 완료. 이후 평가 데이터와 코드의 기준서로 사용한다.

## 1. 평가 목적

사용자는 강의 전체를 2분 안에 요약하지 않는다. 웹에서 다음 두 항목을 먼저 선택한
뒤, 선택한 범위에 관해 2분 동안 자유롭게 설명한다.

1. 강의안
2. 해당 강의의 상위 학습목표

평가는 선택한 상위 학습목표 아래의 하위 학습목표와 Claim만 대상으로 한다.
선택하지 않은 상위 학습목표는 불러오거나 채점하지 않는다.

점수는 해당 강의 전체 이해도가 아니라 **선택한 주제의 2분 복습 점수**다.

```text
선택 강의: 기초통계
선택 주제: 가설검정과 불확실성
평가 결과: 가설검정과 불확실성 복습 점수 82/100
```

## 2. 핵심 설계 원칙

- 발화 시간은 2분을 기준으로 하되 시간 자체에는 점수를 주지 않는다.
- 선택한 상위 학습목표 branch만 평가 모델에 전달한다.
- 키워드 출현이나 Embedding 유사도를 점수로 변환하지 않는다.
- 선택 분기의 Claim 수가 7~12개이므로 Embedding 후보 검색 없이 전체 Claim을 평가한다.
- 실제 점수 단위는 Segment가 아니라 Claim이다.
- Claim의 `evidence`가 가리키는 processed `chunk_id + unit_id`를 평가 시 직접 불러온다.
- LLM은 Claim 판정과 학생 발화 근거 추출을 담당한다.
- 점수 계산과 하위 학습목표 충족도 계산은 코드가 결정적으로 수행한다.
- 객관적으로 판정 가능한 관계는 별도 Relation이 아니라 Claim으로 포함한다.
- 전체 발표 흐름이나 추상적인 Relation Chain은 점수에서 제외하고 정성 피드백으로
  제공한다.
- 같은 설명을 Claim과 Relation에서 중복 채점하지 않는다.
- 점수는 비교적 후하게 설계하되, 키워드만 나열한 경우는 설명으로 인정하지 않는다.

## 3. 평가 계층

```text
Lecture
└── Top-level Objective (상위 학습목표)
    └── Sub-objective (하위 학습목표)
        └── Claim
```

### 3.1 상위 학습목표

강의당 3~4개를 권장한다.

- 범위가 좁은 강의: 3개
- 범위가 넓은 강의: 4개
- 최대 5개를 넘기지 않는다.
- 상위 목표 하나가 2분 안에 설명 가능한 범위인지 확인한다.
- UI에서 사용자가 의미를 이해하고 선택할 수 있는 제목과 설명을 제공한다.

기초통계 예시는 다음과 같다.

```text
기초통계
├── 확률·통계 기초
├── 가설검정과 불확실성
├── ANOVA와 대안
└── 회귀분석과 진단
```

### 3.2 하위 학습목표

상위 학습목표 하나당 기본 3개, 필요한 경우 4개를 권장한다.

- 기본값: 3개
- 허용 범위: 3~4개
- 최대: 4개
- 하위 목표 하나는 하나의 설명 가능한 질문에 대응해야 한다.
- 서로 중복되는 하위 목표를 만들지 않는다.

예시는 다음과 같다.

```text
가설검정과 불확실성
├── 가설검정의 논리와 절차
├── 1종·2종 오류와 검정력
├── p-value의 의미와 오해
└── 신뢰구간의 해석
```

### 3.3 Claim

하위 학습목표 하나당 2~3개를 권장한다.

- 상위 학습목표 전체 권장 Claim 수: 7~10개
- 상위 학습목표 전체 최대 Claim 수: 12개
- 하나의 Claim은 하나의 사실, 정의, 절차, 조건 또는 관계만 판정해야 한다.
- `그리고`, `또한`으로 서로 독립적인 정답을 한 Claim에 과도하게 묶지 않는다.
- 표현이 달라도 의미가 같으면 정답으로 인정할 수 있도록 작성한다.
- Claim 문장은 모범답안 문구가 아니라 판정 가능한 의미 단위여야 한다.

좋지 않은 예시는 다음과 같다.

```text
확률변수는 표본공간을 수치에 대응시키며 기댓값은 확률가중평균이고
분산과 표준편차는 평균 주변의 퍼짐을 나타낸다.
```

이 문장은 확률변수, 기댓값, 분산, 표준편차의 네 판단을 하나로 묶으므로 분리한다.

```text
- 확률변수는 표본공간의 결과를 실수에 대응시키는 함수다.
- 기댓값은 가능한 값의 확률가중평균이다.
- 분산은 기댓값 주변의 퍼짐을 제곱편차로 나타낸다.
- 표준편차는 분산의 제곱근이다.
```

## 4. Claim의 두 가지 분류 축

Claim에는 `role`과 `category`를 각각 기록한다. 두 필드는 역할이 다르다.

```text
role
→ 어느 점수 영역에 반영할지 결정

category
→ 어떤 종류의 이해를 판정하고 피드백할지 결정
```

### 4.1 Claim role

#### `essential`

해당 하위 학습목표를 이해했다면 반드시 설명해야 하는 핵심 내용이다.

- 하위 학습목표마다 기본 1개를 둔다.
- `essential` Claim은 핵심 Claim 이해도 60점에 반영한다.
- 2개 이상 필요하다면 하위 학습목표가 너무 넓지 않은지 먼저 검토한다.

#### `supporting`

핵심 설명을 보완하는 상세 해석, 적용 조건, 비교, 관계 또는 예시다.

- 하위 학습목표마다 1~2개를 권장한다.
- 모든 `supporting` Claim을 말하도록 요구하지 않는다.
- 선택된 상위 목표의 `supporting_claim_slots`만큼 잘 설명한 Claim을 반영한다.
- 보조·심화 Claim 20점에 반영한다.

### 4.2 Claim category

카테고리는 고정 배점 영역이 아니며, Claim 판정 기준과 피드백 분류에 사용한다.
모든 하위 학습목표에 세 카테고리가 전부 존재할 필요는 없다.

#### `core_understanding`

정의, 기본 사실, 핵심 의미와 올바른 해석이다.

```text
p-value는 귀무가설이 참이라는 조건에서 관측 결과 이상의 극단적인 결과가
나올 확률이다.
```

#### `explanation_application`

작동 원리, 절차, 적용 조건, 가정, 대안 선택이다.

```text
등분산성이 성립하지 않으면 Welch ANOVA를 대안으로 고려한다.
```

#### `connection_comparison`

개념 간 차이, 방향 관계, 원인·결과, trade-off다.

```text
기각 기준을 엄격하게 하면 1종 오류는 줄지만 2종 오류는 증가할 수 있다.
```

단순히 두 개념을 함께 언급한 것은 `connection_comparison` Claim을 설명한 것으로
인정하지 않는다.

## 5. 100점 점수 체계

선택한 상위 학습목표 하나의 점수는 다음과 같이 계산한다.

| 평가 영역 | 배점 | 데이터 |
| --- | ---: | --- |
| 핵심 Claim 이해도 | 60 | `role=essential` Claim |
| 보조·심화 Claim | 20 | `role=supporting` Claim |
| 하위 학습목표 충족 | 20 | Claim 판정에서 결정적으로 산출 |
| 합계 | 100 | |

Claim 카테고리별로 고정 점수를 배정하지 않는다. 강의와 선택 주제마다 정의, 절차,
적용, 관계의 분포가 다르기 때문이다.

### 5.1 Claim 판정값

| 판정 | 계산값 | 기준 |
| --- | ---: | --- |
| `correct` | 1.00 | 필수 의미가 정확하고 미해결 오개념·모순이 없다. |
| `mostly_correct` | 0.80 | 필수 의미는 맞고 비핵심 생략·모호함만 있다. 명시적 오개념이나 미해결 모순에는 사용하지 않는다. |
| `partial` | 0.50 | 필수 요소 일부만 맞거나 맞는 내용과 틀린 내용이 섞였지만 핵심 전체가 무너지지는 않았다. |
| `incorrect` | 0.00 | 핵심 의미, 조건 또는 관계 방향이 틀리다. |
| `not_addressed` | 0.00 | 해당 내용을 판단할 만한 설명이 없다. |

`incorrect`와 `not_addressed`는 계산값은 같지만 피드백 의미가 다르다.

- `incorrect`: 설명했으나 틀렸으므로 교정 피드백을 제공한다.
- `not_addressed`: 이번 복습에서 다루지 않았음을 알려준다.

용어만 언급한 경우 Claim을 설명한 것으로 인정하지 않으며 `not_addressed`로 둔다.

### 5.2 핵심 Claim 이해도 60점

선택한 상위 학습목표 아래의 모든 `essential` Claim을 사용한다.

```text
essential_score =
60 × Σ(claim.weight × judgment_value)
     ───────────────────────────────
              Σ(claim.weight)
```

초기 Rubric에서는 `essential` Claim의 `weight`를 기본 1.0으로 두고, 교육적으로
분명한 이유가 있을 때만 조정한다. 가중치 차이는 과도하게 벌리지 않는다.

### 5.3 보조·심화 Claim 20점

모든 `supporting` Claim을 요구하지 않는다. 선택형 충족도와 실제로 언급한 내용의
정확도를 함께 반영한다.

```text
top_n_ratio = 상위 N개 supporting Claim 판정값의 평균
addressed_accuracy = not_addressed를 제외한 supporting Claim 판정값의 평균

supporting_score = 20 × min(top_n_ratio, addressed_accuracy)

N = supporting_claim_slots
```

설명한 supporting Claim이 N개보다 적으면 상위 N개에 포함된 `not_addressed`는
0점으로 계산한다. 반면 말하지 않은 선택형 Claim은 `addressed_accuracy`에서는
제외한다. 따라서 선택하지 않은 세부 내용은 벌하지 않되, 실제로 말한 오개념은
상위 N개 밖이라고 해서 사라지지 않는다. 초기 기본값은 다음과 같다.

- 전체 Claim 7~8개: `supporting_claim_slots = 2`
- 전체 Claim 9~12개: `supporting_claim_slots = 3`

Supporting Claim은 선택형이므로 개별 `weight`를 사용하지 않는 것을 기본으로 한다.

### 5.4 하위 학습목표 충족 20점

LLM이 Objective를 별도로 `complete` 또는 `partial`로 판정하지 않는다. 각 하위
학습목표의 Claim 결과로 충족 비율을 계산한다.

하위 학습목표마다 기본 1개의 `essential` Claim을 두고 다음 규칙을 사용한다.

| 상태 | 충족 비율 |
| --- | ---: |
| Essential이 `correct` | 1.00 |
| Essential이 `mostly_correct` | 0.90 |
| Essential이 `partial` | 0.70 |
| Essential은 0점이지만 Supporting 하나 이상이 `partial` 이상 | 0.50 |
| 키워드만 언급하거나 모든 Claim이 `incorrect`/`not_addressed` | 0.00 |

하위 학습목표 수가 `M`일 때 각 목표의 기본 배점은 `20 / M`이다.

하위 목표 안의 판정이 서로 충돌하면 다음 상한을 적용한다.

- `incorrect` Claim이 하나 이상 있으면 해당 하위 목표 충족 비율은 최대 0.70
- `conflict_status=unresolved`가 하나 이상 있으면 최대 0.85
- `self_corrected`는 충돌 상한을 적용하지 않는다.

```text
coverage_score =
Σ((20 / 하위 학습목표 수) × 각 하위 학습목표 충족 비율)
```

### 5.5 최종 점수

```text
total_score = essential_score + supporting_score + coverage_score
```

각 영역은 소수 둘째 자리에서 반올림하여 한 자리까지 표시하고, 내부 계산에는
반올림 전 값을 사용한다.

## 6. LLM 판정과 점수 계산의 분리

LLM은 점수를 직접 계산하지 않는다. 각 Claim에 대해 다음만 반환한다.

- 판정값
- 충돌 상태(`none`, `self_corrected`, `unresolved`)
- 최소 비중복 학생 발화 근거 목록
- 사용한 강의안 chunk ID
- 판정 이유

예시는 다음과 같다.

```json
{
  "claim_id": "stats.p_value_definition",
  "judgment": "correct",
  "source_chunk_ids_used": ["basic_statistics_p14_01"],
  "conflict_status": "none",
  "evidence_spans": [
    {
      "segment_id": "segment_3",
      "quote": "귀무가설이 참일 때 지금보다 극단적인 데이터가 나올 확률",
      "relation": "supports"
    }
  ],
  "rationale": "귀무가설 조건과 극단성의 의미를 정확히 설명했다."
}
```

`evidence_spans`는 다음 규칙을 따른다.

- 같은 의미의 반복은 가장 명확한 Quote 하나만 남긴다.
- 서로 다른 필수 요소를 보완하면 비중복 Quote를 각각 남긴다.
- 충돌과 명시적 정정은 관련된 앞뒤 Quote를 모두 남긴다.
- `supports`, `contradicts`, `corrects`로 Claim과의 관계를 표시한다.
- Quote를 요약하거나 합성하지 않고 지정 Segment의 연속 원문을 그대로 사용한다.

코드는 다음을 검증하고 점수를 계산한다.

- 선택한 상위 학습목표의 모든 Claim ID가 정확히 한 번 존재하는가
- 알 수 없는 Claim ID가 추가되지 않았는가
- 각 `evidence_spans[].segment_id`가 실제 Segment ID인가
- `source_chunk_ids_used`가 해당 Claim의 `evidence` 안에 존재하는가
- 각 Quote가 실제 지정 Segment 안에 연속 원문으로 존재하는가
- `self_corrected`에 `contradicts`와 `corrects` 근거가 모두 있는가
- `unresolved`에 `supports`와 `contradicts` 근거가 모두 있는가
- `not_addressed`일 때 발화 근거가 비어 있는가
- 상세 `score_breakdown`에 Essential 기여점수, Supporting 선택·언급 정확도,
  Coverage 기본값·상한 근거가 기록되는가

## 7. 평가 실행 흐름

```text
1. 사용자가 강의안 선택
2. 사용자가 상위 학습목표 선택
3. Backend가 해당 상위 학습목표 branch만 로드
4. 2분 STT 발화문을 의미 Segment로 분리
5. 선택 branch의 Claim 7~12개 전체를 평가 대상으로 구성
6. 각 Claim의 evidence.chunk_id와 unit_id를 따라 atomic evidence를 직접 로드
7. Segment·Claim·Evidence 평가 packet 구성
8. LLM이 Claim 판정과 학생 발화 근거를 반환
9. 코드가 출력 구조·출처 연결·Segment 원문 Quote를 검증
10. 검증 실패 시 오류와 기존 JSON을 전달해 전체 판정을 한 번 자동 교정
11. 재검증까지 통과한 결과만 60 + 20 + 20 점수를 계산
12. 누락, 오개념, 잘한 점, 복습 제안을 생성
```

자동 교정은 정확 Quote 검증을 완화하지 않는다. 한 번의 교정 후에도 실패하면 점수를
만들지 않고 마지막 LLM 응답을 `.invalid.json`으로 보존한다. 네트워크·구조화 파싱
재시도와 판정 내용 검증 재시도는 서로 별도로 관리한다.

Segment와 Claim은 일대일 관계가 아니다.

```text
하나의 Segment → 여러 Claim
여러 Segment → 하나의 Claim
```

Embedding 후보 검색은 사용하지 않는다. LLM은 선택 branch의 모든 Claim을 Segment와
다대다로 비교하고, Segment에서 근거를 찾지 못하면 전체 발화문을 다시 확인한 뒤
`not_addressed`를 확정한다.

## 8. Evidence 사용 원칙

Rubric의 `evidence`는 출처 메타데이터에 그치지 않고 평가 시 해당 evidence unit을 직접
불러오는 연결 정보다.

```text
Claim
→ evidence.chunk_id
→ evidence.unit_id
→ processed JSON에서 해당 atomic evidence 직접 로드
→ Claim 평가 packet에 포함
```

`data/processed/*.json`의 `content`는 페이지 이해를 돕는 가공 자료이며 단독 정답
원문으로 간주하지 않는다. 핵심 Claim을 작성할 때 다음 자료를 함께 검수한다.

1. 원본 PDF 페이지
2. `raw_text`
3. `visual_description`
4. `content`

기초통계는 검수된 `evidence_units`를 사용한다. 원문에 없는
보충 설명이나 강의안 오류에 대한 검수 의견은 `source_excerpt`에 섞지 않고 별도
`source_issues`와 `source_status`로 구분한다. 다른 강의는 확장 전까지 기존 chunk
단위 초안 형식을 유지한다.

## 9. Rubric JSON 구조

다음은 구조를 설명하기 위한 축약 예시다. 실제 평가는
`data/evaluation/rubrics/*.json`의 검수된 데이터를 사용한다.

```json
{
  "schema_version": "2.0.0",
  "lecture_id": "basic_statistics",
  "lecture_name": "기초통계",
  "assessment": {
    "mode": "selected_topic_recall",
    "target_seconds": 120,
    "max_seconds": 120,
    "score_policy": {
      "essential_points": 60,
      "supporting_points": 20,
      "coverage_points": 20
    }
  },
  "top_level_objectives": [
    {
      "objective_id": "stats.hypothesis_and_uncertainty",
      "title": "가설검정과 불확실성",
      "selection_description": "가설검정 절차, 오류, p-value와 신뢰구간을 복습합니다.",
      "supporting_claim_slots": 3,
      "sub_objectives": [
        {
          "sub_objective_id": "stats.hypothesis_workflow",
          "title": "가설검정의 논리와 절차",
          "summary": "가설 설정부터 p-value를 통한 판단까지 설명한다.",
          "claims": [
            {
              "claim_id": "stats.hypothesis_steps",
              "role": "essential",
              "category": "explanation_application",
              "text": "가설검정은 귀무·대립가설 설정, 유의수준 선택, 검정통계량과 p-value 계산, 귀무가설 판단 순서로 진행한다.",
              "weight": 1.0,
              "evidence": [
                {
                  "page": 9,
                  "chunk_id": "basic_statistics_p9_01",
                  "unit_id": "basic_statistics_p9_u01",
                  "source_excerpt": "Step1. 귀무 대립가설 세우기 ... Step5. 귀무가설에 대한 판단",
                  "source_status": "verified",
                  "review_note": ""
                }
              ],
              "evaluation_criteria": {
                "required_elements": ["귀무·대립가설 설정부터 판단까지의 검정 절차"],
                "critical_errors": ["기각하지 못한 것을 귀무가설이 참이라고 증명한 것으로 해석"]
              }
            },
            {
              "claim_id": "stats.test_selection",
              "role": "supporting",
              "category": "explanation_application",
              "text": "자료 특성과 검정 가정에 따라 적절한 검정법을 선택한다.",
              "weight": 1.0,
              "evidence": [
                {
                  "page": 9,
                  "chunk_id": "basic_statistics_p9_01",
                  "source_excerpt": "자료 유형과 정규성에 따른 검정법 선택 도식",
                  "source_status": "verified",
                  "review_note": "슬라이드 시각 정보에서 확인"
                }
              ],
              "evaluation_criteria": {
                "required_elements": ["자료 특성과 검정 가정에 따른 검정법 선택"],
                "critical_errors": []
              }
            }
          ]
        }
      ]
    }
  ],
  "excluded_source_claims": [
    {
      "page": 6,
      "chunk_id": "basic_statistics_p6_01",
      "source_text": "공분산이 0이면 두 확률변수는 항상 독립이다.",
      "reason": "일반적으로 성립하지 않아 정답 기준에서 제외한다."
    }
  ]
}
```

## 10. JSON 필드 정의

### Lecture

| 필드 | 의미 |
| --- | --- |
| `schema_version` | 데이터 스키마 버전 |
| `lecture_id` | 강의 고유 ID |
| `lecture_name` | UI 표시 강의명 |
| `assessment` | 2분 평가 모드와 공통 배점 |
| `top_level_objectives` | UI에서 선택할 상위 학습목표 목록 |
| `excluded_source_claims` | 원문에 있지만 자동 정답으로 사용하지 않을 내용 |

### Top-level Objective

| 필드 | 의미 |
| --- | --- |
| `objective_id` | 상위 학습목표 ID |
| `title` | UI 선택 제목 |
| `selection_description` | 사용자가 2분 동안 설명할 범위 안내 |
| `supporting_claim_slots` | 20점에 반영할 Supporting Claim 수 |
| `sub_objectives` | 평가할 하위 학습목표 |

### Sub-objective

| 필드 | 의미 |
| --- | --- |
| `sub_objective_id` | 하위 학습목표 ID |
| `title` | 결과 화면과 피드백에 사용할 제목 |
| `summary` | 기대하는 설명 범위 |
| `claims` | 해당 목표의 원자적 평가 Claim |

### Claim

| 필드 | 의미 |
| --- | --- |
| `claim_id` | Claim 고유 ID |
| `role` | `essential` 또는 `supporting` |
| `category` | 세 Claim 카테고리 중 하나 |
| `text` | 의미 비교에 사용할 기준 주장 |
| `term_ids` | 한글·영어·약어·기호를 연결하는 용어 ID |
| `weight` | Essential Claim 사이의 제한적 중요도 조정 |
| `evidence` | 출처 chunk와 검수된 근거 |
| `evaluation_criteria` | 필수 의미 요소와 핵심 오개념 기준 |

### Evidence

| 필드 | 의미 |
| --- | --- |
| `page` | 원본 PDF 페이지 |
| `chunk_id` | processed chunk ID |
| `unit_id` | processed atomic evidence ID |
| `source_excerpt` | 원문과 시각 정보를 검수해 확정한 근거 요약 |
| `source_status` | `verified`, `needs_review`, `source_error` |
| `review_note` | 시각 정보, 원문 오류 등 검수 메모 |

## 11. Rubric 작성 및 검수 규칙

### 계층 검수

- 강의당 상위 학습목표는 3~4개를 우선한다.
- 상위 목표당 하위 학습목표는 3개를 기본으로 하고 최대 4개로 제한한다.
- 상위 목표 전체 Claim은 7~12개로 구성한다.
- 각 하위 목표에는 기본 1개의 Essential Claim이 있어야 한다.
- Supporting Claim은 선택적으로 설명할 가치가 있는 내용만 둔다.

### Claim 검수

- 한 Claim에서 독립적인 판단을 둘 이상 요구하지 않는다.
- Claim text만 읽어도 맞고 틀림을 판정할 수 있어야 한다.
- 관계 Claim은 관계의 대상, 방향 또는 비교 기준이 명확해야 한다.
- 모호한 선행 관계나 발표 흐름은 점수 Claim으로 만들지 않는다.
- 같은 내용을 서로 다른 Claim에서 중복 채점하지 않는다.
- 강의안에 없는 외부 지식을 자동 정답 기준으로 추가하지 않는다.

### Evidence 검수

- 모든 Claim은 한 개 이상의 Evidence를 가져야 한다.
- 모든 Evidence의 page, chunk ID, unit ID는 실제 processed JSON과 일치해야 한다.
- 핵심 Claim은 원본 PDF 페이지까지 직접 확인한다.
- `content`의 요약이나 재해석만 보고 Claim을 작성하지 않는다.
- 그림과 표에 근거할 경우 `review_note`에 시각 정보임을 기록한다.
- 강의안 오류는 몰래 수정하지 말고 `source_status`와
  `excluded_source_claims`에 기록한다.

## 12. 정성 피드백

점수와 별도로 다음을 제공한다.

- 정확하게 설명한 핵심 내용
- 일부만 설명한 내용
- 잘못 설명한 내용과 대표 오개념
- 선택 주제 안에서 다루지 않은 하위 학습목표
- 개념을 더 자연스럽게 연결하는 방법
- 다음 복습에서 우선 확인할 Claim

전체 발표 순서, 자연스러운 전환, Relation Chain은 점수로 사용하지 않고 정성
피드백에만 사용한다.

## 13. 현재 평가 구조

| 이전 구조 | 현재 구조 |
| --- | --- |
| 강의 Rubric 전체 평가 | 선택한 상위 학습목표 branch만 평가 |
| 평면적인 `learning_objectives` | 상위 목표 → 하위 목표 → Claim 계층 |
| `essential: bool` | `role: essential/supporting` |
| Claim 카테고리 없음 | 세 가지 `category` 추가 |
| Relation/Chain 별도 점수 | 명확한 Relation은 Supporting Claim, Chain은 피드백 |
| Evidence는 출처 ID만 기록 | Evidence chunk 직접 로드 및 사용 기록 |
| Objective를 LLM이 별도 판정 | Claim 결과로 하위 목표 충족도 계산 |
| 40/40/20 | 60/20/20 |
| 2분/3분 자유회상 Profile | 2분 선택 주제 평가 |

이전 Rubric, 2분·3분 Profile, 별도 scoring policy, Relation·Chain 평가기와
ChromaDB 검색 파이프라인은 제거했다. 현재 기준 파일은 다음과 같다.

- `data/evaluation/rubrics/*.json`
- `src/evaluation_schemas.py`
- `src/evaluation_prompt.py`
- `src/evaluation_api.py`
- `src/evaluation.py`
- Backend와 Frontend의 강의·상위 학습목표 선택 입력
- `tests/test_evaluation.py`

## 14. 최종 검수 체크리스트

- [x] 강의별 상위 학습목표 3~4개 확정
- [x] 상위 목표별 하위 학습목표 3~4개 확정
- [x] 하위 목표별 Essential Claim 1개 확정
- [x] Supporting Claim을 포함해 상위 목표 전체 7~12개로 조정
- [x] 각 Claim role과 category 검수
- [ ] 각 Claim의 원본 PDF, raw text, visual, content 대조
- [ ] Evidence의 `source_excerpt`와 `source_status` 확정
- [x] 상위 목표별 `supporting_claim_slots` 2 또는 3 확정
- [x] 강의별로 난이도와 범위가 지나치게 다르지 않은지 비교
- [x] 점수 계산 코드와 테스트 작성
- [ ] 사람 평가자용 Claim 판정 지침 작성
- [ ] 상위 목표별 Calibration과 Holdout Gold 작성

## 15. Gold 평가 원칙

- Gold는 강의 전체가 아니라 `lecture_id + objective_id` 조합별로 만든다.
- 실제 2분 분량에 가까운 발표문을 사용한다.
- 우수, 양호, 부분 설명, 키워드 나열, 오개념 포함, 주제 이탈 사례를 포함한다.
- 모든 Claim을 `correct`, `mostly_correct`, `partial`, `incorrect`,
  `not_addressed` 중 하나로 판정한다.
- 모든 판정에 학생 Segment와 Evidence chunk 연결을 기록한다.
- 두 명이 독립적으로 판정한 뒤 불일치를 합의한다.
- Calibration 데이터로 프롬프트를 조정하고 Holdout 데이터로 최종 성능을 확인한다.

## 16. 이 설계가 해결하는 문제

- 2분 안에 강의 전체를 설명해야 했던 비현실적인 평가 범위를 제거한다.
- 사용자가 선택한 주제만 평가하므로 누락에 대한 과도한 감점을 줄인다.
- Claim 카테고리별 고정 배점 때문에 생기는 강의별 불균형을 제거한다.
- 명확한 Relation은 Claim으로 보존하고 추상적인 Chain 점수는 제거한다.
- Claim, 학생 Segment, 강의 Evidence의 연결을 결과에서 추적할 수 있다.
- LLM의 주관적인 Objective 판정 대신 코드가 Claim 결과로 점수를 계산한다.
- 최종 점수의 각 감점 이유를 하위 학습목표와 Claim 수준에서 설명할 수 있다.
