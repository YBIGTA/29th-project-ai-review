# Git·Python 개발환경 평가 데이터 확장 결과

## 완료 범위

두 강의 모두 PDF 전체 페이지를 기준으로 processed와 Rubric을 구성했다. 이미지로
들어간 터미널 명령과 Python 코드 페이지는 렌더링 결과를 직접 확인해 Evidence에
반영했다.

| 강의 | PDF 페이지 | 상위 목표 | Claim | 원자 Evidence | 용어 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Git | 32 | 3 | 26 | 26 | 33 |
| Python/개발환경 | 61 | 4 | 37 | 36 | 51 |

생성 결과:

- `data/processed/git.json`
- `data/evaluation/rubrics/git.json`
- `data/processed/python_environment.json`
- `data/evaluation/rubrics/python_environment.json`

## 구성 원칙

- 표지·목차·구분·마무리 페이지는 구조에 보존하되 Evidence에서 제외한다.
- 명령어 암기보다 각 명령이 Working Directory·Staging·Repository 또는 가상환경
  상태를 어떻게 바꾸는지를 평가한다.
- Git·GitHub, restore·revert, venv·Conda처럼 혼동하기 쉬운 개념은 비교 Claim과
  `critical_errors`를 둔다.
- 한국어·영어·명령어·약어 표현은 processed의 `terminology`로 연결한다.
- 모든 Claim은 검수된 `chunk_id + unit_id` 원자 Evidence와 직접 연결한다.

## 재생성 및 검증

```bash
python -m scripts.build_curated_json git
python -m scripts.build_curated_json python_environment
python scripts/validate_evaluation_data.py
python -m pytest -q
```

지속할 변경은 생성된 JSON을 직접 고치지 말고 각 build script에 반영한다.
