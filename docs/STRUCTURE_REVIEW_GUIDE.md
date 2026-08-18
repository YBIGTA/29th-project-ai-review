# 강의안 구조화 결과 팀 검수 가이드

## 현재 상태

네 강의안의 모든 페이지를 페이지 단위 JSON으로 구조화했다. PDF에서 추출한 원문과 페이지 이미지를 함께 확인해 표, 차트, 수식, 코드, 화면 캡처처럼 텍스트 추출만으로 빠질 수 있는 정보도 설명에 반영했다.

이 결과에는 임베딩 벡터가 없고 ChromaDB에도 저장하지 않았다. OpenAI API도 호출하지 않았다. 팀 검수가 끝난 JSON을 이후 임베딩 입력으로 사용하는 단계이다.

| lecture_id | 원본 PDF | 구조화 JSON | 페이지/청크 수 |
|---|---|---|---:|
| `basic_statistics` | `data/기초통계.pdf` | `data/processed/basic_statistics.json` | 42 |
| `crawling` | `data/크롤링.pdf` | `data/processed/crawling.json` | 21 |
| `eda_fe` | `data/EDA&FE.pdf` | `data/processed/eda_fe.json` | 42 |
| `visualization` | `data/시각화.pdf` | `data/processed/visualization.json` | 39 |

총 144페이지이며 현재는 검수하기 쉽도록 한 페이지를 한 청크로 만들었다. 팀 검수 후 검색 품질을 위해 지나치게 긴 페이지를 여러 청크로 나누거나, 짧은 연속 페이지를 문맥 단위로 합칠 수 있다.

## JSON 필드 읽는 법

- `chunk_id`: 강의와 페이지를 식별하는 고유 ID
- `lecture_id`, `lecture_name`: 강의 식별자와 표시 이름
- `page`: 원본 PDF의 실제 페이지 번호
- `topic`: 해당 페이지의 대표 주제
- `concepts`: 검색과 중요 개념 분류에 쓸 핵심어
- `raw_text`: PDF에서 그대로 추출한 페이지 원문. 오탈자나 추출 순서 오류가 있을 수 있으므로 원본 보존용으로 사용한다.
- `visual_description`: 그림, 표, 그래프, 수식 배치, 코드 화면 등 시각 정보의 설명
- `content`: 원문과 시각 정보를 합쳐 검색·이해하기 쉽게 정리한 내용

## 권장 검수 방법

1. 한 명이 원본 PDF를 열고, 다른 한 명이 같은 강의 JSON의 `page`를 맞춰 본다.
2. `raw_text`에 중요한 문장·수식·코드가 누락되거나 심하게 깨졌는지 확인한다.
3. `visual_description`에 표의 비교 관계, 그래프의 방향·수치, 그림의 의미가 반영됐는지 확인한다.
4. `content`가 원문에 없는 결론을 새로 만들지 않았는지, 반대로 핵심을 빠뜨리지 않았는지 확인한다.
5. `topic`과 `concepts`가 이후 검색어로 쓰기에 구체적인지 확인한다.
6. 수정 의견은 아래 형식으로 기록하고, 합의된 내용만 구조화 스크립트에 반영한 뒤 JSON을 다시 생성한다.

```text
강의: visualization
페이지: 31
필드: visual_description
현재 내용: ...
수정 제안: ...
근거: 원본 그래프의 7월 12일 수치
검수자: ...
```

## 특히 확인할 항목

- 기초통계 6쪽: 원문은 공분산이 0이면 독립이라고 서술한다. 일반적으로 성립하지 않는 명제이므로 강의 의도와 표현을 확인해야 한다.
- EDA&FE 22쪽: 원문은 Min-Max Scaling이 이상치에 강건하다고 서술한다. 일반적인 특성과 반대이므로 강의 의도와 표현을 확인해야 한다.
- 그래프 수치, 수식 기호, 라이브러리·함수명, 코드 인자는 사람이 원본과 한 번 더 대조한다.
- 제목·목차·섹션 구분 페이지도 페이지 누락 방지를 위해 청크로 유지했다. 검색 대상에서 제외할지는 임베딩 직전에 결정한다.

## 수정 후 재생성

검수 반영은 `scripts/build_curated_json.py`의 해당 페이지 항목을 고친 뒤 실행한다.

```bash
.venv/bin/python scripts/build_curated_json.py basic_statistics
.venv/bin/python scripts/build_curated_json.py crawling
.venv/bin/python scripts/build_curated_json.py eda_fe
.venv/bin/python scripts/build_curated_json.py visualization
```

그다음 `pytest -q`로 페이지 누락, 스키마 오류, 원문 불일치 여부를 확인한다. 팀 검수가 끝나면 중요도 분류와 청킹 정책을 확정하고, 그 결과에만 임베딩을 생성해 ChromaDB에 넣는다.
