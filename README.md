# sttcorrect

강의 음성(한국어, CS 전문용어 혼재)을 `faster-whisper`로 한국어 전사한 뒤, 강의 PDF에서 추출한
영어 전문용어 DB를 STT 힌트(`initial_prompt`/`hotwords`)와 LLM 문맥 보정 참고자료로 활용해
최종 텍스트를 보정하는 파이프라인이다. 설계 배경과 근거는 `IMPLEMENTATION_PLAN.md`를 참고한다.

## 사전 준비물

- Python 3.10 이상
- [Groq](https://console.groq.com/) API 키 (LLM 문맥 보정 호출용)
- 강의 PDF 1개 이상, 그 강의를 녹음한 오디오 파일 1개 이상 (wav/m4a 등 `faster-whisper`가
  디코딩 가능한 포맷이면 된다 — 내부적으로 PyAV/ffmpeg를 거치므로 wav로 직접 변환할
  필요는 없다)

PDF는 `data/pdfs/`, 오디오는 `data/voice/`에 모아 관리한다 (두 폴더 모두 git에
추적되지만, 안의 실제 파일은 `.gitignore`로 제외된다 — 저작권 있는 강의자료/녹음을
커밋하지 않기 위함).

## 설치

```powershell
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell (macOS/Linux는 source venv/bin/activate)
pip install -r requirements.txt
pip install -e .            # src/sttcorrect 패키지를 편집 가능 모드로 설치 (CLI/테스트 import용)
Copy-Item .env.example .env # 생성된 .env 파일에 GROQ_API_KEY=... 를 채워넣는다
```

## 사용법 — 처음부터 끝까지 실행하는 절차

파이프라인은 **"PDF → 용어 DB 빌드"(1회, 재사용 가능)** 와 **"오디오 → 전사+보정"(강의마다
반복)** 두 단계로 나뉜다. 아래는 실제로 실행하는 순서다.

### 1단계 — 강의 자료 준비 (PDF + 오디오)

강의자료 PDF는 `data/pdfs/`에, 녹음 오디오는 `data/voice/`에 넣는다.

```powershell
Copy-Item ~\Downloads\lecture.pdf data\pdfs\lecture.pdf
Copy-Item ~\Downloads\lecture.m4a data\voice\lecture.m4a
```

### 2단계 — PDF에서 용어 DB 생성 (`build_term_db`)

```powershell
python -m sttcorrect.cli.build_term_db `
  --pdf data/pdfs/lecture.pdf `
  --topic DB `
  --out data/term_dbs/db_course.json
```

내부적으로 일어나는 일:

1. PyMuPDF로 PDF의 모든 페이지 텍스트를 추출하고, 슬라이드 헤더/푸터처럼 여러 페이지에
   반복되는 줄을 제거한다.
2. 대문자 단어/약어/영숫자 혼합 패턴으로 영어 전문용어 후보를 뽑는다
   (`RDBMS`, `DBMS`, `Key` 등).
3. `RDBMS(알디비엠에스)`처럼 본문에 병기된 한글 발음이 있으면 함께 추출해 각 용어에
   붙인다.
4. `config/seed_collision_terms.yaml`의 curated 규칙으로 각 용어를 `safe` /
   `content_word_collision`(예: `Key`→"키") / `particle_collision`(예: `Row`→"로우")
   3가지로 분류한다.
5. 결과를 `--out` 경로에 JSON으로 저장한다.

한 과목의 PDF를 학기 동안 여러 개(주차별) 처리해 하나의 누적 term DB로 합치려면 `--merge`
플래그를 주고 매번 같은 `--out` 경로를 지정한다:

```powershell
# 1주차 — 파일이 아직 없으므로 --merge를 줘도 새로 생성될 뿐이다
python -m sttcorrect.cli.build_term_db --pdf data/pdfs/db_week1.pdf --topic DB `
  --out data/term_dbs/db_course.json --merge

# 2주차 이후 — 동일 --out에 --merge를 주면 기존 term DB와 병합해 누적한다
python -m sttcorrect.cli.build_term_db --pdf data/pdfs/db_week2.pdf --topic DB `
  --out data/term_dbs/db_course.json --merge
```

`--merge` 없이 실행하면 기존과 동일하게 `--out`을 덮어쓴다.

### 3단계 — 오디오 전사 + 보정 (`run_pipeline`)

```powershell
python -m sttcorrect.cli.run_pipeline `
  --audio data/voice/lecture.m4a `
  --term-db data/term_dbs/db_course.json `
  --topic DB `
  --session-id abc123 `
  --out result.json
```

내부적으로 일어나는 일:

1. `term_db`에서 STT 힌트(`initial_prompt`, `hotwords`)를 만들어 `faster-whisper`에
   전달하고, 오디오를 한국어로 전사한다 (`transcript_raw`).
2. `term_db`를 `safe`/`content_word_collision`/`particle_collision` 3분류로 변환한다
   (`term_db_used`).
3. `transcript_raw`와 `term_db_used`를 Groq LLM에 보내 발음이 잘못 인식된 전문용어를
   문맥에 맞게 교정한다 (`transcript_corrected`).
4. 위 결과를 `TranscriptionResult` JSON으로 `--out` 경로에 저장한다.

`--term-db` 대신 `--pdf`를 주면 이 실행 시점에 즉석으로 용어 DB를 빌드한다 (매번 PDF를
다시 파싱하므로, 같은 PDF로 여러 오디오를 처리할 계획이라면 2단계에서 미리 만들어둔
`--term-db`를 재사용하는 쪽이 빠르다):

```powershell
python -m sttcorrect.cli.run_pipeline `
  --audio data/voice/lecture.m4a --pdf data/pdfs/lecture.pdf --topic DB `
  --session-id abc123 --out result.json
```

### 4단계 — 결과 확인

`--out`으로 저장된 JSON은 다음 구조다:

```json
{
  "session_id": "abc123",
  "topic": "DB",
  "transcript_raw": "STT가 전사한 원본 텍스트",
  "transcript_corrected": "LLM이 전문용어를 교정한 최종 텍스트",
  "term_db_used": {
    "safe": ["..."],
    "content_word_collision": ["..."],
    "particle_collision": ["..."]
  }
}
```

`transcript_corrected`가 최종 결과물이고, `term_db_used`는 이번 보정에 실제로 참고된
용어 목록이라 결과가 이상할 때 원인 추적(어떤 용어가 힌트로 안 들어갔는지 등)에 쓴다.

## 테스트

```bash
pytest tests/ --ignore=tests/integration
```

`tests/integration/`은 실제 오디오/모델이 필요한 스모크 테스트로, 기본 실행에서는 제외된다.
