### Frontend

---

- **기술 스택**
    - `React` or `Next.js`, `Tailwind CSS`, `Shadcn UI` (컴포넌트 라이브러리), `react-webcam` / `MediaRecorder API`
- **주요 R&R**
    - **UI/UX 구현:** 회원가입/로그인 페이지, 토픽 및 PDF 업로드 UI, 구술 복습 실행 화면, 평가 리포트 대시보드
    - **미디어 제어:** 웹캠 스트리밍 및 마이크 녹음(WAV/WebM 추출) 기능 구현
    - **인터랙션:** 2~3분 카운트다운 타이머, [힌트 보기] 클릭 시 팝업 필요

### STT & Audio Processing

---

- **기술 스택**
    - `Python`, `Faster-Whisper` (아니면 `openai-whisper`), `pydub`, `ffmpeg` 등
- **주요 R&R**
    - **음성-텍스트 변환:** 오디오 파일(.wav, .mp3 등)을 입력받아 한국어/영어 텍스트 전사
        - 한영 혼용되는데, 이를 어떻게 잘 구분할 수 있을지 고민 필요
    - **음성 전처리:** 노이즈 제거 및 무음 구간 처리 등 필요.
    - **용어 보정:** 전문적인 용어들 (Convolution, ResNet 등) 오인식을 줄이기 위한 prompting 필요, 업로드된 학습 자료 바탕으로 미리 커스텀 필요

### RAG & LLM Setting

---

- **기술 스택**
    - `Python`, `LangChain` (or `LlamaIndex`), `ChromaDB` (Vector DB), `PyPDF`, `OpenAI API`
- **주요 R&R**
    - **문서 처리 & Vector DB:** 업로드된 PDF 강의 자료 텍스트 추출, Chunking 및 ChromaDB 저장
    - **힌트 추출 로직:** PDF 내 핵심 키워드/요약 문장을 추출, 핵심 내용 정도 구분 → 프론트엔드 힌트 단계별로 정리
    - **구술 평가 Prompting:** STT 전사 텍스트와 원본 PDF 내용을 비교, 이해도 점수(0~100점) 및 누락된 핵심 개념을 추출하는 프롬프트 작성. 단순 텍스트 일치도가 아니라 내용과 맥락 면에서 어느 정도의 이해도를 가지는지 판단해야 함!

### BE & Integration

---

- **추천 기술 스택**
    - `Python`, `FastAPI`, `PostgreSQL` (or `SQLite`), `SQLAlchemy` / `Pydantic`
- **주요 R&R**
    - **백엔드 API 개발:** RESTful API 엔드포인트 설계 및 DB 스키마 구축 (User, Topic, Review, Score)
    - **파이프라인 통합 (Glue Code):** FE에서 보낸 오디오/PDF를 받아서 STT 모듈과 RAG 모듈을 거쳐 최종 평가 JSON으로 반환하는 흐름 작성
    - **Mock API 작성:** FE 개발 촉진을 위한 가짜 응답(Mock Response) API 선제공
    - **PM 업무:** API Spec 문서화, WBS 일정 리딩, 8/18 중간발표 및 8/25 최종발표 총괄

- **1차 연동 API 계약**
    - `POST /api/materials/upload`: PDF를 업로드하고 `pdf_id`, `filename`, `status`를 반환
    - `GET /api/materials/{pdf_id}/status`: 업로드 응답의 `pdf_id`로 PDF 분석 상태 조회
    - `POST /api/reviews/submit`: `pdf_id`와 `audio_file`을 받아 Mock 평가 결과 반환
    - `filename`은 원본 PDF 파일명에서 확장자를 제거한 값이며, FE 화면의 드롭다운 표시명으로 사용
    - `pdf_id`는 서버 내부 식별자이며, 상태 조회와 리뷰 제출에 사용
    - FE 드롭다운은 `label=filename`, `value=pdf_id` 형태로 관리
