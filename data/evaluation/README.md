# Rubric 평가 데이터

이 디렉터리는 2분 선택 주제 평가에 필요한 최종 데이터만 보관합니다.

## 파일

- `rubrics/*.json`: 네 강의의 상위 목표·하위 목표·Claim·Evidence
- `rubric.schema.json`: Rubric JSON Schema
- `topic_assessment.schema.json`: LLM 판정 출력 JSON Schema
- `../processed/processed.schema.json`: processed JSON Schema
- `gold/*_assessment.json`: 사람이 검수한 Claim 판정 예시
- `gold/*_score.json`: 코드로 재현해야 하는 기대 점수

## 원칙

- 선택한 상위 학습목표 분기만 평가합니다.
- Rubric과 processed 데이터는 임베딩하지 않습니다.
- 기초통계 Claim Evidence는 `chunk_id + unit_id`로 atomic evidence를 직접 조회합니다.
- 기초통계 Claim의 `term_ids`는 한국어·영어·약어·기호를 같은 개념으로 연결합니다.
- LLM은 Claim별 판정, 충돌 상태, 최소 비중복 원문 근거를 반환합니다.
- 같은 의미 반복은 대표 Quote 하나만, 보완·충돌·정정은 Segment별 Quote로 보존합니다.
- 점수는 코드가 60+20+20으로 계산하며 실제로 언급한 Supporting 오답을 버리지 않습니다.
- 결과의 `score_breakdown`은 Claim별 기여점수와 Supporting·Coverage 계산 근거를 보여줍니다.
- 출력 검증 실패 시 오류를 반영한 전체 판정을 한 번 재요청하며, 재검증을 통과한 결과만 채점합니다.
- 자동 교정 후에도 실패하면 점수를 만들지 않고 마지막 응답을 `.invalid.json`으로 보존합니다.
- 명확한 관계·비교는 `category=connection_comparison` Claim으로 평가합니다.
- 별도 Relation, Relation Chain, 2분·3분 Profile은 사용하지 않습니다.

## 검증

```bash
python scripts/validate_evaluation_data.py
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest tests/test_evaluation.py -q
```

기초통계의 상세 구조와 재생성 방법은 `docs/BASIC_STATISTICS_PROCESSED.md`를
참고합니다. Evidence를 변경할 때는 원본 PDF, processed JSON, Rubric을 함께 검수해야 합니다.

팀원이 AI를 활용해 Gold 발화문과 사람 기준의 기대 판정을 만들 때는
`docs/GOLD_DATASET_AUTHORING_GUIDE.md`를 따릅니다. 현재 평가기의 출력을 보기 전에
Gold 판정을 확정하고 Calibration/Holdout을 분리해야 합니다.
