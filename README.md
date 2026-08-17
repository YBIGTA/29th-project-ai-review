# 29th-project-ai-review

YBIGTA 신입기수 교육세션을 말로 복습하고, 전사 결과를 바탕으로 학습 내용을 평가하는 AI 구술 복습 서비스입니다.

현재 `dev`에는 다음 범위가 통합되어 있습니다.

- STT: M4A/WAV/WebM 오디오를 Faster-Whisper로 한국어 전사
- STT 후처리: Groq LLM을 사용한 전문용어 및 문맥 보정
- BE: STT 결과 JSON을 받는 FastAPI submit API
- 평가: 연결 확인을 위한 Mock 점수 및 피드백

RAG의 PDF 구조화, Embedding, ChromaDB 검색 파이프라인은 현재 `feat/rag-pipeline` 브랜치에서 개발 중입니다. STT 후처리 결과를 RAG 평가에 전달하는 형식과 충실성/연결성/포괄성 평가 방식은 아직 팀 합의가 필요한 상태입니다.

## 전체 흐름

```text
브라우저 오디오 녹음
    |
    v
STT-research: Faster-Whisper 전사
    |
    v
Groq LLM: 전문용어 및 문맥 보정
    |
    v
STT 결과 JSON
    |
    v
BE POST /api/reviews/submit
    |
    v
현재: Mock 평가 JSON
향후: RAG 기반 평가 JSON
    |
    v
FE 점수 및 피드백 표시
```

## 디렉터리 구조

```text
.
├── backend/
│   └── app/
│       ├── config.py          # CORS 등 BE 설정
│       ├── integrations.py    # 현재 Mock 평가, 향후 RAG adapter 위치
│       ├── main.py            # FastAPI 앱과 API route
│       ├── schemas.py         # STT 요청 및 평가 응답 Pydantic schema
│       ├── material_processing.py # 기존 자료 처리 adapter
│       └── storage.py          # 기존 로컬 저장 helper
├── src/
│   └── sttcorrect/
│       ├── cli/
│       │   ├── build_term_db.py # PDF 기반 전문용어 DB 생성
│       │   └── run_pipeline.py  # 오디오 전사 및 LLM 보정 실행
│       ├── stt/whisper_backend.py # Faster-Whisper wrapper
│       ├── llm/groq_client.py     # Groq LLM client
│       ├── term_db/                # PDF 용어 추출 및 분류
│       ├── pipeline.py             # STT -> 보정 orchestration
│       └── schema.py               # STT 결과 및 term DB schema
├── data/
│   ├── pdfs/                     # 로컬 테스트용 PDF, Git 제외
│   ├── term_dbs/                 # 생성된 용어 DB, Git 제외
│   └── voice/                    # 로컬 테스트용 오디오, Git 제외
├── results/                      # STT 결과 JSON, Git 제외
├── tests/                        # STT/BE 단위 테스트
├── .env.example                  # 환경변수 예시
└── requirements.txt
```

실제 PDF, 오디오, 결과 JSON, term DB는 저장소에 올리지 않습니다. `.gitignore`에 의해 `data/`, `results/`, `*.pdf`, `*.m4a`, `*.json`이 제외됩니다.

## 설치

macOS/Linux 기준입니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

STT 패키지를 `src` 경로에서 실행하려면 다음 중 하나를 사용합니다.

```bash
PYTHONPATH=src python -m sttcorrect.cli.run_pipeline --help
```

또는 프로젝트 설정에 따라 editable install을 사용할 수 있습니다.

```bash
pip install -e .
```

## 환경변수

`.env.example`을 복사해 `.env`를 만들고 API 키를 입력합니다.

```bash
cp .env.example .env
```

STT 보정에는 다음 값이 필요합니다.

```env
GROQ_API_KEY=...
GROQ_MODEL=openai/gpt-oss-120b
```

Groq 모델명은 계정에서 사용 가능한 모델이어야 합니다. API 키와 `.env`는 Git에 커밋하지 않습니다.

## STT 실행

### 전문용어 DB 생성

PDF에서 영어 전문용어, 약어, 한글 발음 정보를 추출합니다.

```bash
PYTHONPATH=src python -m sttcorrect.cli.build_term_db \
  --pdf data/pdfs/DB.pdf \
  --topic DB \
  --out data/term_dbs/db_course.json
```

### 전사 및 2차 보정

```bash
PYTHONPATH=src python -m sttcorrect.cli.run_pipeline \
  --audio data/voice/DB_test_hard.m4a \
  --term-db data/term_dbs/db_course.json \
  --topic DB \
  --session-id test-medium-beam2 \
  --model-size medium \
  --beam-size 2 \
  --out results/test-medium-beam2.json
```

파이프라인은 다음 순서로 실행됩니다.

1. term DB에서 `initial_prompt`와 `hotwords`를 생성합니다.
2. Faster-Whisper로 오디오를 전사해 `transcript_raw`를 생성합니다.
3. Groq LLM에 전사 결과와 term DB를 전달합니다.
4. 전문용어, 띄어쓰기, 문장부호 등을 보정해 `transcript_corrected`를 생성합니다.
5. 최종 결과를 JSON으로 저장합니다.

`medium-beam2`를 사용하려면 반드시 `--model-size medium --beam-size 2`를 지정합니다. M4A는 Faster-Whisper가 지원하는 코덱이라면 별도 WAV 변환 없이 사용할 수 있습니다.

## STT 결과 JSON

```json
{
  "session_id": "test-medium-beam2",
  "topic": "DB",
  "transcript_raw": "Whisper 원본 전사 결과",
  "transcript_corrected": "Groq 보정 결과",
  "term_db_used": {
    "safe": ["RDBMS", "MongoDB"],
    "content_word_collision": ["Key"],
    "particle_collision": ["Row"]
  }
}
```

FE/BE 통합 시 평가 입력으로 사용할 텍스트는 `transcript_corrected`입니다. `transcript_raw`는 원본 비교와 오류 분석을 위해 보존합니다.

## BE 실행

```bash
uvicorn backend.app.main:app --reload
```

서버 확인:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

`/health`의 정상 응답:

```json
{
  "status": "ok"
}
```

## BE API 계약

### `POST /api/reviews/submit`

STT 결과 JSON 전체를 Request body로 받습니다. 현재는 `transcript_corrected`를 Mock 평가에 전달합니다.

Request:

```json
{
  "session_id": "test-medium-beam2",
  "topic": "DB",
  "transcript_raw": "원본 전사 결과",
  "transcript_corrected": "보정된 전사 결과",
  "term_db_used": {
    "safe": [],
    "content_word_collision": [],
    "particle_collision": []
  }
}
```

Response:

```json
{
  "review_id": "review-abc123",
  "session_id": "test-medium-beam2",
  "score": 78,
  "transcript": "원본 전사 결과",
  "corrected_transcript": "보정된 전사 결과",
  "feedback": {
    "summary": "Mock 평가가 정상적으로 생성되었습니다.",
    "strengths": ["핵심 주제를 언급했습니다."],
    "missing_points": ["세부 근거와 예시가 아직 반영되지 않았습니다."],
    "suggestions": ["핵심 개념 사이의 관계를 한 문장씩 설명해 보세요."]
  },
  "status": "mock"
}
```

정상 처리 상태 코드는 `201 Created`입니다. `status`가 `mock`이면 아직 실제 RAG 평가가 연결되지 않은 상태입니다.

### Swagger에서 확인

1. 서버를 실행합니다.
2. `http://127.0.0.1:8000/docs`에 접속합니다.
3. `POST /api/reviews/submit`의 `Try it out`을 클릭합니다.
4. `results/test-medium-beam2.json`의 전체 내용을 Request body에 붙여넣습니다.
5. `Execute`를 클릭하고 `201` 응답과 `status: "mock"`을 확인합니다.

macOS에서는 JSON 파일을 클립보드에 복사할 수 있습니다.

```bash
pbcopy < results/test-medium-beam2.json
```

## RAG 통합 예정 범위

`feat/rag-pipeline`에는 다음 PDF 기반 파이프라인이 구현되어 있습니다.

```text
PDF 페이지 텍스트 추출 + 이미지 렌더링
-> Vision 기반 페이지 구조화
-> Chunk JSON 생성
-> 핵심 개념 JSON 생성
-> OpenAI Embedding
-> ChromaDB 저장 및 검색
```

현재 `dev`의 BE는 RAG 구현 세부사항을 알지 않고 STT 결과 JSON을 받습니다. RAG 통합 시 BE 내부의 Mock adapter를 실제 평가 함수로 교체하는 것을 목표로 합니다.

아직 합의가 필요한 항목:

- STT 보정 결과를 RAG 평가용으로 추가 가공할지 여부
- `lecture_id`와 `topic`의 매핑 방식
- 핵심 개념별 충실성 평가 기준
- 개념 간 연결성 평가 기준
- 전체 주제 포괄성 평가 기준
- 점수 및 피드백 JSON 최종 형식

RAG evaluator가 확정되면 다음과 같은 경계로 연결할 수 있습니다.

```python
evaluation = evaluate_speech(
    transcript=request.transcript_corrected,
    topic=request.topic,
    term_db_used=request.term_db_used,
)
```

FE는 RAG 내부 구현을 직접 호출하지 않고, BE가 반환하는 평가 JSON만 표시합니다.

## 테스트

BE/STT 단위 테스트:

```bash
pytest -q tests/test_api.py
```

STT 관련 테스트까지 포함한 테스트:

```bash
PYTHONPATH=src pytest -q
```

실제 Whisper/Groq/API 호출은 비용과 실행 시간이 발생할 수 있으므로, 일반 단위 테스트와 분리해 수동으로 실행합니다.

## FE 전달사항

FE는 다음 순서로 구현하면 됩니다.

1. 사용자가 세션 또는 주제를 선택합니다.
2. 브라우저 마이크 권한을 요청합니다.
3. `MediaRecorder`로 녹음을 시작하고, 사용자가 녹음을 종료하면 오디오 Blob을 생성합니다.
4. 녹음된 오디오 파일을 STT 실행 계층에 전달합니다.
5. STT 실행 결과 JSON을 받습니다.
6. 결과 JSON 전체를 `POST /api/reviews/submit`으로 전송합니다.
7. BE 응답의 `score`, `corrected_transcript`, `feedback`을 화면에 표시합니다.
8. `status: "mock"`인 동안에는 실제 평가가 아닌 임시 결과임을 구분합니다.

### 브라우저 녹음 포맷

브라우저의 `MediaRecorder`가 생성하는 포맷은 브라우저마다 다를 수 있습니다. 일반적으로 Chrome 계열은 `audio/webm;codecs=opus`를 우선 사용하고, Safari는 M4A/MP4 계열 지원 여부를 확인해야 합니다.

FE는 녹음 시작 전에 지원 포맷을 확인하는 것이 좋습니다.

```javascript
const mimeTypes = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
];

const mimeType = mimeTypes.find((type) => MediaRecorder.isTypeSupported(type));
if (!mimeType) {
  throw new Error("지원되는 녹음 포맷이 없습니다.");
}

const recorder = new MediaRecorder(stream, { mimeType });
```

녹음이 끝나면 `Blob`을 파일로 감싸 STT 계층에 전달합니다. 파일 확장자는 실제 MIME 타입과 일치시켜야 합니다. 현재 BE의 로컬 오디오 업로드 검증은 WAV, WebM, M4A를 지원하지만, 현재 `dev`의 submit API는 STT 결과 JSON을 받으므로 오디오 파일을 직접 `POST /api/reviews/submit`에 보내는 구조는 아닙니다.

브라우저 녹음의 권장 흐름은 다음과 같습니다.

```text
MediaRecorder
-> audio Blob
-> STT 실행 계층
-> transcript JSON
-> POST /api/reviews/submit
```

FE에서 함께 구현해야 할 상태:

- 마이크 권한 요청 중
- 녹음 중
- 녹음 완료 및 업로드 중
- STT 처리 중
- 평가 요청 중
- 평가 완료
- 권한 거부/녹음 실패/API 실패

현재 FE가 알아야 할 API는 `POST /api/reviews/submit`이며, PDF 업로드 API는 현재 개발 범위에 포함하지 않습니다. 강의자료는 사전에 RAG에 구축하는 방향입니다.
