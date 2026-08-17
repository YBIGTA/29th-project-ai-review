# 29th-project-ai-review

YBIGTA 교육 세션을 사용자가 말로 복습하고, 전사 결과를 RAG 모델 바탕으로 평가하는 AI 구술 복습 서비스입니다.

- FE 브라우저에서 음성 녹음
- BE에서 Faster-Whisper `medium`, `beam_size=2`로 STT 수행
- Groq LLM을 이용한 전문용어 및 문맥 보정
- 보정된 STT JSON을 평가 API로 전달

PDF 업로드는 현재 사용하지 않습니다. 세션 자료와 용어 DB는 사전에 준비되어 있다는 전제입니다.

## 전체 흐름

```text
FE 브라우저 음성 녹음
  -> POST /api/stt/transcribe
  -> BE 오디오 로컬 저장
  -> Faster-Whisper medium, beam=2 전사
  -> Groq LLM 2차 보정
  -> transcript_raw / transcript_corrected 반환
  -> POST /api/reviews/submit
  -> Mock 평가 JSON 반환
  -> FE에서 전사문, 점수, 피드백 표시
```

## 디렉터리 구조

```text
.
├── backend/
│   ├── app/
│   │   ├── config.py              # 환경변수 및 CORS 설정
│   │   ├── integrations.py        # 현재 Mock 평가 adapter
│   │   ├── main.py                # FastAPI 앱 및 API route
│   │   ├── material_processing.py # 기존 자료 처리 helper
│   │   ├── schemas.py             # Request/Response Pydantic schema
│   │   └── storage.py             # 오디오 로컬 저장 helper
│   └── data/audio/                # 요청 오디오 임시 저장 위치
├── frontend/fe/
│   ├── app/                       # Next.js 진입점 및 전역 스타일
│   ├── components/ReviewApp.tsx   # 녹음, API 호출, 결과 표시 UI
│   ├── lib/api.ts                 # BE API client와 TypeScript 타입
│   ├── package.json               # FE 의존성과 실행 명령어
│   ├── package-lock.json          # npm 의존성 버전 고정
│   └── tsconfig.json              # TypeScript 설정
├── src/sttcorrect/
│   ├── cli/                       # term DB 생성 및 로컬 pipeline CLI
│   ├── llm/groq_client.py         # Groq API client
│   ├── stt/whisper_backend.py     # Faster-Whisper wrapper
│   ├── term_db/                   # 용어 추출 및 prompt 생성
│   ├── pipeline.py                # STT -> LLM 보정 orchestration
│   └── schema.py                  # STT 결과 및 term DB schema
├── data/                          # PDF, term DB, 테스트 음성; Git 제외
├── results/                       # STT 결과 JSON; Git 제외
├── tests/                         # BE/STT 단위 테스트
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```


## 기술 스택

| 영역 | 기술 | 역할 |
|---|---|---|
| FE | Next.js, React, TypeScript | 녹음, API 호출, 결과 화면 |
| 음성 입력 | MediaRecorder API | WebM 오디오 생성 |
| BE | FastAPI, Uvicorn, Pydantic | API, 파일 저장, schema 검증 |
| STT | Faster-Whisper | 한국어/영어 음성 전사 |
| 보정 | Groq API | 전문용어, 띄어쓰기, 문장부호 보정 |
| 평가 | Mock adapter | RAG 연결 전 통합 검증 |

## 설치

프로젝트 루트에서 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

FE 의존성:

```bash
cd frontend/fe
npm install
cd ../..
```

## 환경변수

```bash
cp .env.example .env
```

루트 `.env`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

`frontend/fe/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

환경변경 후에는 해당 서버를 재시작합니다. `.env`와 `.env.local`은 커밋하지 않습니다.

## 용어 DB 준비

BE STT API는 `data/term_dbs/db_course.json`을 읽습니다. 파일이 없으면 로컬 PDF를 준비한 뒤 생성합니다.

```bash
PYTHONPATH=src python -m sttcorrect.cli.build_term_db \
  --pdf data/pdfs/DB.pdf \
  --topic DB \
  --out data/term_dbs/db_course.json
```

생성된 term DB는 PDF와 API key에 의존하므로 Git에 올리지 않습니다.

## 서버 실행

BE는 프로젝트 루트에서 실행합니다.

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

FE는 별도 터미널에서 실행합니다.

```bash
cd frontend/fe
npm run dev
```

브라우저에서 `http://localhost:3000`을 엽니다.

## API 계약

### `POST /api/stt/transcribe`

`multipart/form-data`로 다음 필드를 받습니다.

```text
session_id: string
topic: string (기본값 DB)
audio_file: .wav, .webm, .m4a
```

처리 순서는 오디오 저장, Faster-Whisper `medium`/`beam_size=2` 전사, Groq 보정입니다.

```json
{
  "session_id": "demo-session",
  "topic": "DB",
  "transcript_raw": "원본 전사 결과",
  "transcript_corrected": "보정된 전사 결과",
  "term_db_used": {
    "safe": ["RDBMS"],
    "content_word_collision": [],
    "particle_collision": []
  }
}
```

### `POST /api/reviews/submit`

STT 결과 JSON을 Request body로 받습니다. 현재 평가 부분은 Mock입니다.

```json
{
  "session_id": "demo-session",
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

응답은 원본/보정 전사와 함께 다음 평가 구조를 포함합니다.

```json
{
  "review_id": "review-abc123",
  "session_id": "demo-session",
  "score": 75,
  "transcript": "원본 전사 결과",
  "corrected_transcript": "보정된 전사 결과",
  "quantitative": {
    "concept_recall": 0.72,
    "concept_precision": 0.84,
    "concept_f1": 0.77,
    "scores": {
      "accuracy": {"score": 32, "max_score": 40, "rubric_level": 3, "reason": "..."},
      "coverage": {"score": 29, "max_score": 40, "rubric_level": 3, "reason": "..."},
      "structural_understanding": {"score": 14, "max_score": 20, "rubric_level": 3, "reason": "..."}
    },
    "total": {"score": 75, "max_score": 100, "rubric_level": 3, "reason": "..."}
  },
  "qualitative": {
    "missing_concepts": ["세부 근거와 예시"],
    "incorrect_concepts": [],
    "misconnected_concepts": [],
    "review_suggestions": ["핵심 개념 사이의 관계를 설명해 보세요."]
  },
  "status": "mock"
}
```

점수 배점은 정확도 40점, 충족도 40점, 구조적 이해도 20점입니다. `201 Created`와 `status: "mock"`이면 현재 Mock 평가까지 정상 처리된 것입니다.

## 로컬 통합 테스트

1. BE를 실행하고 `/health`에서 `{"status":"ok"}`를 확인합니다.
2. FE를 실행해 `http://localhost:3000`에 접속합니다.
3. 브라우저에서 녹음을 시작하고 종료합니다.
4. 전사 원문과 보정문이 FE에 표시되는지 확인합니다.
5. 점수와 정성 피드백이 표시되는지 확인합니다.

Swagger에서 직접 테스트하려면 `http://127.0.0.1:8000/docs`에서 `POST /api/stt/transcribe`를 먼저 실행하고, 반환된 JSON을 `POST /api/reviews/submit`의 Request body에 넣습니다.

## 테스트 및 정적 검증

프로젝트 루트:

```bash
source .venv/bin/activate
pytest -q
python -m compileall -q backend src
```

FE:

```bash
cd frontend/fe
npm run lint
npx tsc --noEmit
```

단위 테스트와 정적 검증은 외부 API 및 Whisper 모델 호출까지 보장하지 않습니다. 실제 통합 검증은 BE와 FE를 실행한 뒤 별도로 진행합니다.

## 향후 RAG 통합

현재 `backend/app/integrations.py`의 Mock 평가를 실제 RAG 평가 adapter로 교체합니다.

```text
사전 구축된 세션 자료
  -> 텍스트/이미지 처리
  -> 개념 및 평가 기준 구조화
  -> 임베딩 및 벡터 저장
  -> transcript_corrected 평가
  -> 정량 점수 및 정성 피드백 반환
```

통합 전 확정할 항목은 다음과 같습니다.

- `topic`과 RAG 자료의 매핑 방식
- RAG 평가 함수의 입력 형식
- 정확도, 충족도, 구조적 이해도의 세부 루브릭
- `quantitative`와 `qualitative` 응답의 최종 형식
- STT 보정 결과의 추가 후처리 여부
