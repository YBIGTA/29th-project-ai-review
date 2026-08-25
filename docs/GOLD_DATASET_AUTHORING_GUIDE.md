# Gold 발화문 제작·검수 가이드

> 대상: Rubric 기반 2분 선택 주제 평가용 Gold를 만드는 팀원
>
> Gold는 현재 평가 AI가 내놓은 답이 아니라, **사람이 강의 근거와
> Rubric을 보고 검수한 기준 답안**이다.

## 1. 목적

Gold는 다음을 검증하는 데 사용한다.

- 완전히 올바른 발화문이 높은 점수를 받는가
- 표현이 달라도 같은 의미를 인정하는가
- 부분 이해와 누락을 지나치게 엄격하거나 후하게 판정하지 않는가
- 명시적 오개념을 `incorrect`로 잡는가
- 한국어·영어·약어·수식이 섞여도 같은 개념으로 인식하는가
- Claim 판정으로 계산한 60+20+20 점수가 교육적으로 납득 가능한가

Gold 제작 중에는 현재 평가기의 결과를 정답으로 사용하지 않는다.
팀원이 기대 판정을 확정한 뒤에만 평가기와 비교한다.

### 현재 제작 가능 범위

현재 `basic_statistics`, `crawling`, `eda_fe`, `visualization`, `cs_basics`,
`git`, `python_environment`, `web`, `network_basics`, `machine_learning`,
`deep_learning`, `computer_vision`, `nlp`, `docker`, `llm`, `aws`, `db`,
`ai_agent`, `rag`는 Rubric `2.2.0`의 모든 Claim에
`evaluation_criteria`와 원자 Evidence가 있어 최종 Gold 제작을 시작할 수 있다.

## 2. 현재 평가 구조

사용자는 강의안과 상위 학습목표 하나를 선택하고 약 2분 동안 자유롭게
설명한다.

```text
Lecture
└── Top-level objective (사용자가 선택)
    └── Sub-objective 3~4개
        └── Claim 2~3개
```

평가 AI는 선택 branch의 모든 Claim을 판정한다. Segment 개수, 키워드 개수,
Embedding 거리에 직접 점수를 주지 않는다.

| 판정 | 값 | Gold 판정 기준 |
| --- | ---: | --- |
| `correct` | 1.0 | `required_elements`가 충족되고 미해결 오개념·모순이 없다. |
| `mostly_correct` | 0.8 | 핵심은 정확하고 명시적 오개념 없이 비핵심 생략·모호함만 있다. |
| `partial` | 0.5 | 필수 요소 일부만 맞거나 맞는 내용과 틀린 내용이 섞였다. |
| `incorrect` | 0.0 | 핵심 정의·조건·관계·방향이 무너지거나 `critical_errors`가 핵심 이해를 무너뜨린다. |
| `not_addressed` | 0.0 | 판단할 설명이 없다. 용어만 나열한 경우도 포함한다. |

각 Claim의 `evaluation_criteria.required_elements`와 `critical_errors`를 먼저 읽고
판정한다. 올바른 설명과 틀린 설명을 동시에 했다면 다음처럼 판정한다.

- 틀린 문장이 발화문 안에서 해결되지 않았다면 `unresolved`다. 일부 정확한 이해가
  남으면 `partial`, 핵심 전체가 무너지면 `incorrect`로 판정한다.
- 뒤에 맞는 문장이 나왔다는 이유만으로 정정으로 보지 않는다. 앞선 오류를 취소하는
  표현이 명확하고 최종 설명이 정확할 때만 `self_corrected + correct`가 가능하다.
- 명시적 오개념이나 미해결 모순에는 `mostly_correct`를 사용하지 않는다.
- 판정자마다 이견이 있으면 임의로 확정하지 말고 `review_note`에 남긴다.

### 100점 계산

| 영역 | 배점 | 계산 방법 |
| --- | ---: | --- |
| Essential Claim 이해도 | 60 | 모든 `essential` Claim의 가중 평균 |
| Supporting Claim | 20 | 상위 N개 충족도와 실제 언급한 Supporting 정확도 중 낮은 비율 |
| 하위 학습목표 충족 | 20 | Essential 중심 충족도에 `incorrect`·미해결 충돌 상한 적용 |

팀원은 총점을 보고 Claim 판정을 역산하지 않는다. **Claim별 기대 판정을
먼저 확정**하고 점수는 그 판정으로부터 계산한다.

`70점 대본`, `50점 대본`처럼 총점부터 지정해 만드는 방식은 사용하지 않는다.
case는 `정답`, `누락`, `단일 오개념`, `미해결 충돌`, `명시적 정정`처럼 발화의
조건으로 설계하고, 기대 점수는 사람이 확정한 Claim 판정을 점수 코드에 넣어 계산한다.

## 3. 팀원과 제작 AI에게 주는 파일

강의 하나를 담당하는 팀원에게 다음을 준다.

1. **원본 강의 PDF**: 최종 정답의 1차 근거
2. `data/evaluation/rubrics/<lecture_id>.json`: 학습목표, Claim, Evidence
3. `data/processed/<lecture_id>.json`: Evidence unit과 한국어·영어·약어 대응
4. `docs/2MIN_TOPIC_RUBRIC_SPEC.md`: 2분 평가와 60+20+20 설계
5. 본 문서 `docs/GOLD_DATASET_AUTHORING_GUIDE.md`

PDF와 processed·Rubric이 다르면 팀원이 임의로 고치지 말고 차이를 기록한다.
최종 판단은 PDF 원문 대조 후 확정한다.
Rubric Claim에 `evaluation_criteria`가 없다면 최종 Gold 제작을 멈추고 Rubric 확장
대상으로 보고한다.

### 제작 AI에게 주지 말아야 할 것

- 현재 평가기가 낸 Claim 판정과 총점
- `outputs/`에 있는 평가 결과
- 특정 점수가 나오도록 유도하는 지시

이를 먼저 주면 AI가 현재 평가기의 판단을 복제해 Gold의 독립성이
사라진다.

## 4. 필수 산출물

하나의 Gold case는 **순수 발화문**과 **사람 기대 판정표** 두 자료로
구성한다.

### 4.1 순수 발화문 `.txt`

- 사용자가 말한 내용만 넣는다.
- 제목, Claim ID, 오류 설명, 기대 점수, Markdown 표시를 넣지 않는다.
- 문서체보다 실제 학습자가 말할 법한 자연스러운 구어체를 쓴다.
- 문자 수만으로 2분을 판정하지 말고 최소 한 번 직접 읽으며 측정한다.
- 권장 실독 시간은 약 105~120초다. 약간의 멈춤과 더듬음을 고려한다.

파일명:

```text
<objective_id>__<case_id>.txt
```

예:

```text
stats.probability_foundations__correct_full_01.txt
stats.probability_foundations__misconception_variance_01.txt
```

### 4.2 사람 기대 판정표

발화문과 별도로 다음을 작성한다.

````markdown
# Gold annotation

- case_id: stats.probability_foundations__misconception_variance_01
- lecture_id: basic_statistics
- objective_id: stats.probability_foundations
- case_type: single_misconception
- measured_seconds: 114
- author: 작성자
- reviewer: 검수자
- split: undecided

| claim_id | expected_judgment | expected_conflict_status | reason | source_page |
| --- | --- | --- | --- | ---: |
| stats.random_variable | correct | none | 핵심 정의가 맞다. | 4 |
| stats.expectation_variance | partial | unresolved | 맞는 설명과 틀린 설명이 해결되지 않은 채 섞였다. | 4 |
| stats.sample_population | not_addressed | none | 모집단과 표본을 설명하지 않았다. | 5 |

## Expected evidence spans

```json
{
  "claim_id": "stats.expectation_variance",
  "evidence_spans": [
    {
      "segment_id": "seg_02",
      "quote": "분산은 평균 주변의 퍼짐입니다.",
      "relation": "supports"
    },
    {
      "segment_id": "seg_05",
      "quote": "분산이 클수록 평균 주변에 더 안정적으로 모입니다.",
      "relation": "contradicts"
    }
  ]
}
```

## Intended error

- 의도한 오개념: 분산이 클수록 안정적이라고 해석
- 영향받아야 하는 Claim: stats.expectation_variance
- 의도하지 않은 추가 오류: 없음

## Review note

- 이견 또는 Rubric 공백이 있으면 기록
````

각 `evidence_spans[].quote`는 지정 Segment에 실제로 있는 **하나의 연속된 문구를
글자 그대로 복사**한다. 같은 의미 반복은 가장 명확한 하나만, 서로 다른 보완
정보와 충돌·정정은 각각 남긴다. 요약, 문장 수정, 떨어진 문구의 결합을 하지 않는다.
`not_addressed`는 빈 배열로 둔다.

Segment ID는 평가 AI 결과에서 가져오지 않는다. 순수 발화문을 확정한 뒤 다음 명령으로
동일한 결정적 Segmenter만 실행한다.

```bash
python scripts/segment_transcript.py \
  --transcript-file data/evaluation/gold/transcripts/<lecture_id>/<case_id>.txt \
  --output data/evaluation/gold/annotations/<case_id>__segments.json
```

이 명령은 OpenAI API를 호출하거나 Claim을 판정하지 않는다. 출력된 `seg_01`,
`seg_02` 등을 사람 기대 판정표의 `evidence_spans`에 사용한다. 발화문을 수정하면
Segment도 다시 생성하고 Quote를 다시 확인한다.

## 5. 상위 학습목표별 case 구성

완전 정답만으로는 평가기의 문제를 찾을 수 없다. 상위 학습목표 하나당
우선 8개를 다음처럼 만든다.

| 유형 | 개수 | 목적 |
| --- | ---: | --- |
| 완전 정답 | 1 | 모든 하위 목표를 정확히 설명 |
| 자연스런 경미한 누락 | 1 | 핵심은 맞지만 상세 일부가 빠진 발화 |
| Essential 하나 누락 | 1 | `not_addressed`와 Coverage 감점 확인 |
| 하위 목표 부분 커버 | 1 | `partial`과 `mostly_correct` 경계 확인 |
| 단일 오개념 | 1 | 핵심 오류 탐지 |
| 미해결 충돌 | 1 | 같은 Claim의 맞는 설명과 틀린 설명을 모두 잡는지 확인 |
| 명시적 자기 정정 | 1 | 앞선 오류와 최종 정정을 함께 보고 판정하는지 확인 |
| 영어·약어·반복·비순차 표현 | 1 | 표현 및 Segment 순서 변화의 견고성 확인 |

시간이 허락하면 다음도 추가한다.

- 핵심어만 나열하고 설명하지 않는 대본
- 예시는 맞지만 정의를 잘못 일반화한 대본
- 두 개 이상의 서로 다른 오개념을 포함한 대본
- STT 표기 변형을 포함한 대본
- Claim 경계가 애매한 경계 case

## 6. 발화문 제작 규칙

### 정답 case

- 선택된 상위 목표의 모든 하위 목표를 다룬다.
- 각 Essential Claim은 키워드가 아니라 의미가 드러나게 설명한다.
- Supporting Claim은 최소 `supporting_claim_slots`만큼 정확히 포함한다.
- Rubric 문장을 그대로 이어 붙이지 말고 자연스럽게 바꿔 말한다.
- 강의 범위 밖의 고급 지식을 과도하게 추가하지 않는다.

### 오류·누락 case

- 의도한 오류의 위치와 영향받는 Claim을 먼저 정한다.
- 오류를 돋보이게 표시하지 말고 올바른 설명 사이에 자연스럽게 넣는다.
- `single_misconception`에는 의도하지 않은 다른 오류를 넣지 않는다.
- 언급하지 않은 것은 `not_addressed`이지 `incorrect`가 아니다.
- 미해결 충돌 case에는 같은 Claim에 대한 `supports`와 `contradicts` 발화를 모두
  포함하고, 어느 쪽이 최종 입장인지 명시적으로 해결하지 않는다.
- 자기 정정 case에는 앞선 오류, 오류를 취소하는 명시적 표현, 정확한 최종 설명을
  모두 포함한다. 단순히 뒤에서 다른 말을 덧붙이는 것은 자기 정정 case가 아니다.
- PDF에 잘못된 설명이 있어도 그것을 정답으로 쓰지 않는다. Rubric의
  `excluded_source_claims`와 source issue를 확인한다.

### Rubric 공백을 발견한 경우

중요한 오개념이 현재 Rubric의 어떤 Claim과도 대응하지 않을 수 있다. 이때
가장 비슷한 Claim에 억지로 붙이지 말고 다음처럼 보고한다.

```text
rubric_gap: true
gap_description: 이 오개념을 직접 판정할 Claim이 없음
suggested_claim_or_rule: 검수자 제안
```

이는 실패한 Gold가 아니라 Rubric 개선을 위한 중요한 발견이다.

## 7. AI 활용 절차

AI는 초안 작성과 누락 검사에 활용할 수 있지만 최종 Gold 판정자가 될 수는
없다.

1. 작성 AI에게 PDF, Rubric, processed, case 지시를 준다.
2. AI가 발화문과 Claim별 기대 판정 초안을 만든다.
3. 작성자가 PDF Evidence와 대조해 사실 관계를 검수한다.
4. 가능하면 별도 세션의 검수 AI 또는 다른 팀원이 독립적으로 판정한다.
5. 두 판정이 다르면 근거 페이지와 Claim을 보고 합의한다.
6. 발화문을 직접 읽어 시간을 측정하고 `.txt`와 판정표를 분리해 제출한다.
7. 이 단계 후에만 현재 평가기를 실행해 Gold와 비교한다.

## 8. 복사해 사용할 AI 프롬프트

### 8.1 발화문·기대 판정 초안 생성

```text
너는 2분 구술 복습 평가의 Gold 데이터 초안 작성자다.
정답의 1차 근거는 첨부한 강의 PDF이며, Rubric의 선택된
objective branch와 processed evidence unit을 판정 단위로 사용한다.

[작업 대상]
- lecture_id: {LECTURE_ID}
- objective_id: {OBJECTIVE_ID}
- case_id: {CASE_ID}
- case_type: {CASE_TYPE}
- 의도한 누락/오개념: {INTENDED_CONDITION}

[발화문 작성 규칙]
1. 실제 학습자가 설명하는 자연스러운 구어체로 작성한다.
2. 약 2분 발화를 목표로 하되 불필요한 문장으로 길이를 늘리지 않는다.
3. Rubric 문장을 그대로 나열하지 말고 의미를 자연스럽게 바꿔 설명한다.
4. 지정된 누락/오개념만 의도적으로 반영하고 추가 오류를 만들지 않는다.
5. 혼합 표현 case가 아니면 억지로 영어를 추가하지 않는다.
6. PDF와 Rubric이 충돌하거나 오개념이 어떤 Claim에도 매핑되지 않으면
   임의로 해결하지 말고 별도로 표시한다.
7. 특정 총점을 목표로 문장이나 오류 수를 조절하지 않는다.
8. Claim에 evaluation_criteria가 없으면 임의의 판정 기준을 만들지 말고 작업을 중단해 보고한다.

[기대 판정 규칙]
- 선택 branch의 모든 Claim을 한 번씩 판정한다.
- 판정값은 correct, mostly_correct, partial, incorrect, not_addressed 중 하나다.
- 용어만 언급했으면 not_addressed로 판정한다.
- 명시적 오개념이나 미해결 충돌이 있으면 mostly_correct를 사용하지 않는다.
- 맞는 요소와 틀린 요소가 섞였지만 핵심 전체가 무너지지 않았으면 partial로 판정한다.
- 핵심 정의·조건·방향 전체를 반대로 설명했으면 incorrect로 판정한다.
- self_corrected는 앞선 오류를 명시적으로 취소하고 최종 설명을 바로잡은 경우에만 사용한다.
- unresolved에는 supports와 contradicts 근거를 모두 남긴다.
- self_corrected에는 contradicts와 corrects 근거를 모두 남긴다.
- evidence span의 quote는 지정 Segment의 하나의 연속 구간을 글자 그대로 복사한다.
- 같은 의미 반복은 대표 Quote 하나만 남기고, 보완·충돌·정정은 비중복 Quote를 각각 남긴다.
- conflict_status는 none, self_corrected, unresolved 중 하나로 판정한다.
- 점수를 먼저 정한 뒤 판정을 맞추지 않는다.

[출력]
A. 순수 발화문
B. Claim별 expected_judgment 표
C. 의도한 오류/누락과 영향받는 Claim
D. PDF 근거 페이지
E. Rubric gap 또는 추가 인간 검수가 필요한 점

현재 평가 AI의 출력을 참고하지 말고 제공된 강의 근거로만 초안을 만들어라.
```

### 8.2 독립 검수용 프롬프트

```text
너는 Gold 데이터의 독립 검수자다. 작성 AI의 판정을 자동으로
동의하지 말고, PDF, Rubric, processed evidence와 발화문을 직접 대조하라.

1. 선택 branch의 모든 Claim이 판정표에 정확히 한 번씩 있는지 확인한다.
2. 각 expected_judgment를 독립적으로 재판정한다.
3. 각 evidence span의 quote가 지정 Segment의 연속된 원문인지 확인한다.
4. 명시적 정정과 미해결 충돌이 올바르게 구분됐는지 확인한다.
5. 의도하지 않은 추가 오류, 숨은 모순, 과도한 외부 지식을 찾는다.
6. 중요한 오개념이 Claim과 매핑되지 않으면 rubric_gap으로 보고한다.
7. 총점을 추측해 판정을 바꾸지 않는다.

출력:
- Claim별 독립 판정
- 작성자 판정과의 불일치
- 각 불일치의 PDF/Rubric 근거
- 추가 오류 및 Rubric gap
- 실독 시간 검사가 필요한지
```

## 9. 인간 검수 체크리스트

- [ ] `lecture_id`와 `objective_id`가 올바르다.
- [ ] 선택 범위 밖의 내용이 과도하게 섞이지 않았다.
- [ ] branch의 모든 Claim이 판정표에 한 번씩 있다.
- [ ] 판정이 PDF·Evidence와 일치한다.
- [ ] `incorrect`와 `not_addressed`를 구분했다.
- [ ] 의도한 오류 외의 숨은 오류가 없다.
- [ ] Claim별 `required_elements`와 `critical_errors`를 확인했다.
- [ ] 미해결 충돌에는 supports·contradicts가, 자기 정정에는 contradicts·corrects가 모두 있다.
- [ ] 정답 case에 최소 `supporting_claim_slots`만큼 Supporting Claim이 포함됐다.
- [ ] 한국어·영어 대응이 의미적으로 올바르다.
- [ ] 인용문이 순수 발화문의 연속된 원문이다.
- [ ] `.txt`에 정답 표시·Claim ID·설명이 섞이지 않았다.
- [ ] 실제 실독 시간을 확인했다.
- [ ] 작성자 외 1명 이상이 최종 판정을 검수했다.

## 10. Calibration과 Holdout

완성된 Gold는 평가기를 실행하기 **전에** 나눈다.

- **Calibration set 약 70%**: Rubric·프롬프트·점수식 보정에 사용
- **Holdout set 약 30%**: 보정 중에 결과를 보지 않고 마지막에 한 번 검증

각 상위 목표의 정답·누락·오개념·혼합 표현 case가 두 set에 고르게
들어가야 한다. Holdout 결과를 보고 기준을 수정했다면 그 set은 더 이상
Holdout이 아니다.

## 11. 프로젝트에서 평가하기

순수 발화문 `.txt`는 JSON으로 변환할 필요 없이 바로 평가할 수 있다.

```bash
python scripts/evaluate_topic.py \
  --lecture <lecture_id> \
  --objective <objective_id> \
  --transcript-file <transcript.txt> \
  --output outputs/<case_id>_result.json
```

평가 후에는 총점만 보지 말고 다음 순서로 비교한다.

1. Gold의 Claim별 `expected_judgment`
2. 평가 AI의 Claim별 `judgment`
3. 불일치 Claim의 `evidence_spans`, `conflict_status`, `rationale`
4. Essential 60, Supporting 20, Coverage 20의 세부 점수
5. Rubric 공백, 프롬프트 문제, 점수식 문제, Gold 오류 중 어디에 해당하는지

특정 대본 하나의 점수를 맞추기 위해 기준을 바꾸지 말고, Calibration set
전체의 Claim 판정 일치도와 오개념 탐지가 개선되는지 확인한다.
