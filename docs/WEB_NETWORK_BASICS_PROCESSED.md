# Web·네트워크 기초 평가 데이터 확장 결과

| 강의 | PDF 페이지 | 상위 목표 | Claim | 원자 Evidence | 용어 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Web | 29 | 3 | 22 | 20 | 42 |
| 네트워크 기초 | 28 | 4 | 31 | 18 | 49 |

두 강의 모두 PDF 원문과 핵심 도식을 대조해 processed `2.1.0`, Rubric `2.2.0`으로
구성했다. Web의 HTTP는 메시지·API 인터페이스 관점, 네트워크의 HTTP는
DNS·IP·TCP 뒤의 애플리케이션 교환 관점으로 평가 범위를 분리했다.

생성 결과:

- `data/processed/web.json`
- `data/evaluation/rubrics/web.json`
- `data/processed/network_basics.json`
- `data/evaluation/rubrics/network_basics.json`

재생성·검증:

```bash
python -m scripts.build_curated_json web
python -m scripts.build_curated_json network_basics
python scripts/validate_evaluation_data.py
python -m pytest -q
```
