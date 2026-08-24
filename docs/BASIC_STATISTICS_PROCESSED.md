# 기초통계 processed 검수 결과

## 적용 범위

현재 검수 완료 범위는 `data/기초통계.pdf` 42쪽이다. 크롤링, EDA·FE, 시각화는 같은 구조로 확장할 예정이다.

## 데이터 구조

`data/processed/basic_statistics.json`은 다음 정보를 가진다.

- `schema_version`: `2.1.0`
- `terminology`: 한국어·영어·약어·허용 별칭·기호·혼동 금지 개념
- `page_role`: 표지, 목차, 구분, 핵심 본문, 예제, 참고자료, 마무리 구분
- `raw_text`: PDF에서 추출한 원문을 그대로 보존
- `content`: 해당 슬라이드의 검수된 전체 설명
- `evidence_units`: 정의·공식·관계·절차·주의사항을 Claim 단위로 분리한 근거
- `source_issues`: 원문의 오탈자·잘못된 주장·과도한 단정을 기록하고 평가 정책을 명시

기초통계에는 69개 용어 항목, 75개 evidence unit, 9개 source issue가 있다. 표지·목차·섹션 구분·마무리는 평가 evidence로 사용하지 않는다.

## Rubric 연결

`data/evaluation/rubrics/basic_statistics.json`의 각 Claim은 다음 방식으로 연결된다.

```text
claim_id
  -> term_ids
  -> evidence.page
  -> evidence.chunk_id
  -> evidence.unit_id
```

평가 프롬프트에는 선택된 상위 학습목표의 Claim, 그 Claim이 실제로 참조하는 atomic evidence, 관련 용어만 들어간다. 같은 페이지의 무관한 설명, `raw_text`, `source_issues`는 평가 컨텍스트에 섞이지 않는다.

## 원문 오류 처리

대표적으로 다음 내용을 평가 정답에서 제외했다.

- 6쪽: 공분산이 0이면 항상 독립이라는 주장
- 21쪽: 정규성이 깨지면 F 검정 자체가 불가능하다는 절대적 표현
- 25쪽: 글자와 공식이 훼손된 Kruskal-Wallis 참고 이미지
- 38쪽: VIF 임계값을 보편적인 절대 기준처럼 제시한 표현

오탈자나 표현상 주의가 필요한 내용은 `warn`, 정답으로 쓰면 안 되는 내용은 `exclude`로 구분한다.

## 재생성과 검증

기초통계 curated JSON을 다시 생성하면 검수된 atomic evidence 구조가 자동 적용된다.

```bash
python -m scripts.build_curated_json basic_statistics
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest
```

`data/evaluation/gold/basic_statistics_bilingual_cases.json`은 한국어·영어·혼합 표현과 대표 오개념에 대한 실제 LLM 회귀 테스트 입력이다. 현재 자동 테스트는 데이터 연결과 프롬프트 컨텍스트를 검증하며, 이 gold의 실제 LLM 판정률 측정은 API 호출 테스트 단계에서 수행한다.
