# 시각화·CS기초 평가 데이터 확장 결과

## 완료 범위

두 강의 모두 PDF 원본의 전체 페이지를 기준으로 processed와 Rubric을 완성했다.
표지·목차·구분·마무리 페이지는 구조에는 남기되 평가 Evidence에서는 제외했다.

| 강의 | PDF 페이지 | 상위 목표 | Claim | 원자 Evidence | 용어 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 시각화 | 39 | 4 | 39 | 25 | 51 |
| CS기초 | 44 | 4 | 39 | 33 | 42 |

생성 결과:

- `data/processed/visualization.json`
- `data/evaluation/rubrics/visualization.json`
- `data/processed/cs_basics.json`
- `data/evaluation/rubrics/cs_basics.json`

## 구성 원칙

- `raw_text`는 PDF에서 다시 추출한 페이지 원문을 그대로 보존한다.
- `content`는 원문에 없는 내용을 보충하지 않고, 정의·조건·관계·주의점을 평가에
  필요한 수준으로 보존한다.
- 한국어·영어·약어는 `terminology`의 canonical term과 alias로 연결한다.
- Claim은 `chunk_id + unit_id`로 원자 Evidence에 직접 연결한다.
- 각 Claim에 `required_elements`, `partial_conditions`, `critical_errors`를 둔다.
- 사례에서만 성립하는 해석은 일반 이론처럼 확장하지 않는다.

## 재생성 및 검증

```bash
python -m scripts.build_curated_json visualization
python -m scripts.build_curated_json cs_basics
python scripts/validate_evaluation_data.py
python -m pytest -q
```

원본 PDF나 생성 규칙을 수정했을 때만 위 명령으로 재생성한다. 수동으로 JSON만
수정하면 다음 재생성에서 덮어써지므로, 지속할 변경은 각 build script에 반영한다.
