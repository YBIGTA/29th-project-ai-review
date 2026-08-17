# AI 구술 복습 서비스 - RAG

강의안 PDF 4개를 페이지별로 구조화하고, Chunk를 Embedding하여 ChromaDB에서
검색할 수 있게 만드는 MVP 파이프라인입니다.

## 범위

- PDF 페이지별 텍스트 추출 및 전체 페이지 고해상도 PNG 렌더링
- 텍스트와 페이지 이미지를 함께 보는 OpenAI Vision Structured Output 구조화
- 페이지 캐시 및 재시도
- 강의별 핵심 개념 JSON 생성
- OpenAI Embedding 생성
- ChromaDB 영구 저장
- 전체 강의 또는 특정 강의 검색 CLI

STT, 프론트엔드, 로그인, 최종 평가 점수 산정은 포함하지 않습니다.

## 환경 설정

Python 3.11 이상을 권장합니다.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

준비된 `.env`의 `OPENAI_API_KEY`를 설정합니다. 파일이 없다면
`.env.example`을 복사해 만듭니다. API 키를 저장소에 커밋하지 마세요.

## PDF 위치

권장 위치는 `data/raw/`이지만, 현재 프로젝트와의 호환을 위해 `data/` 바로
아래의 기존 한글 PDF 파일도 자동으로 찾습니다. 원본 PDF는 수정하지 않습니다.

## 실행

먼저 PDF 텍스트 추출 상태를 확인합니다.

```bash
python scripts/inspect_pdfs.py
```

한 강의의 앞 페이지 하나로 API 연결을 점검합니다.

```bash
python scripts/process_one.py basic_statistics --max-pages 1 --skip-core-concepts --skip-index
```

한 강의를 전체 처리합니다.

```bash
python scripts/process_one.py basic_statistics
```

4개 강의를 모두 처리합니다.

```bash
python scripts/process_all.py
```

검색합니다.

```bash
python scripts/test_search.py "평균은 극단적으로 큰 값의 영향을 받을 수 있다"
python scripts/test_search.py "결측치와 이상치를 확인한다" --lecture-id eda_fe
```

`--force`를 주지 않으면 원문 해시와 모델이 같은 페이지 캐시를 재사용합니다.

모든 페이지는 텍스트 유무나 이미지 감지 결과와 관계없이 비전 분석을 거칩니다.
기본 렌더링은 160 DPI이고 `VISION_DETAIL=original`을 사용합니다. 이미지에서만
확인되는 표, 그래프, 수식, 다이어그램, 스크린샷의 정보는 각 Chunk의
`visual_description`과 `content`에 반영됩니다.

## 주요 출력

```text
data/processed/{lecture_id}.json
outputs/cache/{lecture_id}/page_XXX.json
outputs/core_concepts/{lecture_id}.json
outputs/logs/pipeline.log
vector_db/
```

## 테스트

```bash
pytest -q
```
