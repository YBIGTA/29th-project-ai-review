# 크롤링·EDA/FE 평가 데이터 확장 결과

## 완료 범위

| 강의 | PDF 페이지 | 상위 목표 | Claim | 상태 |
| --- | ---: | ---: | ---: | --- |
| 크롤링 | 21 | 3 | 27 | processed `2.1.0`, Rubric `2.2.0` |
| EDA/FE | 42 | 4 | 38 | processed `2.1.0`, Rubric `2.2.0` |

두 강의 모두 PDF 전체 페이지를 확인했고, 표지·목차·구분·마무리
페이지는 평가 Evidence에서 제외했다. Claim은 `chunk_id + unit_id`로
검수된 원자 Evidence와 연결되며, 모든 Claim에 다음이 있다.

- 한국어·영어·약어·별칭을 연결하는 `term_ids`
- `evaluation_criteria.required_elements`
- 명시적 오개념을 잡는 `critical_errors`
- PDF 원문을 보존한 `source_excerpt`

## 원문 주의사항

EDA/FE p21의 “로지스틱 회귀에서는 성능 변화 없음”과 p22의
“Min-Max Scaling은 이상치에 강건”은 절대화되었거나 틀린
표현이다. `source_issues` 및 Rubric `excluded_source_claims`에 기록하고
평가 정답 근거에서 제외했다.

크롤링 p8의 크롤링·스크래핑 비교는 강의가 용어의 실무적
혼용을 명시하므로, 용어 하나만을 엄격하게 채점하지 않고 폭넓은
수집과 선택적 추출의 원리 차이를 판정한다.

## 재생성·검증

```bash
python -m scripts.build_curated_json crawling
python -m scripts.build_curated_json eda_fe
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest -q
```

`build_curated_json`은 기본 페이지 JSON을 생성한 뒤 강의별 확장 스크립트를
자동으로 적용하므로, 재생성 후에도 용어·Evidence·Rubric 기준이
유지된다.
