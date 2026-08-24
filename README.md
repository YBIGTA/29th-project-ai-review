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

STT, 프론트엔드, 로그인, LLM 평가 API 호출은 포함하지 않습니다. 다만 평가 API가
반환한 의미 판정을 40·40·20점으로 계산하기 위한 rubric, 출력 스키마와 결정론적
점수 계산기는 `data/evaluation/`과 `src/evaluation.py`에 준비되어 있습니다.

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

### 이미 구조화된 JSON으로 ChromaDB 만들기

현재 저장된 구조화 JSON을 사용할 때는 `process_all.py`를 다시 실행하지 않습니다.
먼저 API를 호출하지 않는 dry-run으로 선별 결과를 확인합니다. 인자를 생략해도
dry-run이 기본값입니다.

```bash
python scripts/build_vector_db.py --dry-run
```

선별 기준은 `data/indexing/embedding_manifest.json`에 Chunk ID와 제외 이유를
명시했습니다. 원본 144개 Chunk는 그대로 보존하고 표지, 목차, 내용 없는 섹션
구분, 종료 페이지 27개만 인덱싱에서 제외하여 117개를 대상으로 사용합니다.

API 키와 모델 연결은 Chunk 하나로 확인할 수 있습니다. 이 명령은 임베딩 API를
한 번 호출하지만 ChromaDB에는 쓰지 않습니다.

```bash
python scripts/build_vector_db.py --smoke-test --lecture-id basic_statistics
```

확인이 끝난 뒤 선택된 Chunk 전체를 임베딩하고 ChromaDB에 저장합니다.

```bash
python scripts/build_vector_db.py --execute
이 단계도 내부적으로 Groq LLM을 호출하므로(아래 3번), `.env`의 `GROQ_API_KEY`와
네트워크 접근이 필요하다.

내부적으로 일어나는 일:

1. PyMuPDF로 PDF의 모든 페이지 텍스트를 추출하고, 슬라이드 헤더/푸터처럼 여러 페이지에
   반복되는 줄을 제거한다.
2. 대문자 단어/약어/영숫자 혼합 패턴으로 영어 전문용어 후보를 뽑는다
   (`RDBMS`, `DBMS`, `Key` 등). 대소문자만 다른 중복(`Key`/`KEY` 등)은 하나로 합친다.
3. 후보 용어 목록을 Groq LLM에 한 번에 전달해 각 용어의 한국어 발음을 생성한다
   (예: `RDBMS`→"알디비엠에스"). LLM이 목록에 없는 용어를 추가로 지어내면 무시한다.
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

한 강의만 구축하려면 `--lecture-id basic_statistics`처럼 제한할 수 있습니다.
`--execute`를 명시하지 않으면 API 호출과 DB 변경이 발생하지 않습니다. 실제 실행
기록은 `outputs/indexing/last_index_run.json`에 모델, 입력 해시, 벡터 차원과
Chunk 수를 남깁니다.

### PDF부터 다시 구조화하기

먼저 PDF 텍스트 추출 상태를 확인합니다.

```bash
python scripts/inspect_pdfs.py
```

한 강의의 앞 페이지 하나로 API 연결을 점검합니다.

```bash
python scripts/process_one.py basic_statistics --max-pages 1 --skip-core-concepts --skip-index
1. `term_db`에서 STT 힌트(`initial_prompt`, `hotwords`)를 만들어 `faster-whisper`에
   전달하고, 오디오를 한국어로 전사한다 (`transcript_raw`).
2. `term_db`를 `safe`/`content_word_collision`/`particle_collision` 3분류로 변환한다
   (`term_db_used`).
3. `transcript_raw`와 `term_db_used`를 Groq LLM에 보내 발음이 잘못 인식된 전문용어를
   문맥에 맞게 교정한다 — 명백히 잘못 전사된 용어는 영어 원어 표기로 복원하고
   (`포린키`→`Foreign Key`), 이미 올바른 한국어 표현은 건드리지 않는다
   (`transcript_corrected`).
4. 위 결과를 `TranscriptionResult` JSON으로 `--out` 경로에 저장한다.

`--term-db` 대신 `--pdf`를 주면 이 실행 시점에 즉석으로 용어 DB를 빌드한다 (매번 PDF를
다시 파싱하므로, 같은 PDF로 여러 오디오를 처리할 계획이라면 2단계에서 미리 만들어둔
`--term-db`를 재사용하는 쪽이 빠르다):

```powershell
python -m sttcorrect.cli.run_pipeline `
  --audio data/voice/lecture.m4a --pdf data/pdfs/lecture.pdf --topic DB `
  --session-id abc123 --out result.json
```

한 강의를 전체 처리합니다.

```bash
python scripts/process_one.py basic_statistics
```

4개 강의를 모두 처리합니다.

```bash
python scripts/process_all.py
```

위 `process_one.py`와 `process_all.py`는 PDF 로드, 페이지 이미지 분석, 구조화 JSON
생성, 핵심 개념 생성과 인덱싱을 묶은 전체 파이프라인입니다. 기존 구조화 JSON으로
임베딩만 할 때는 사용하지 마세요.

검색합니다.

```bash
python scripts/test_search.py "평균은 극단적으로 큰 값의 영향을 받을 수 있다"
python scripts/test_search.py "결측치와 이상치를 확인한다" --lecture-id eda_fe
```

2~3분 STT 답변은 한 벡터로 평균내지 않고 의미 단위로 나누어 검색합니다.

```bash
python scripts/test_long_answer_search.py \
  --file ../기초통계_대본.txt \
  --lecture-id basic_statistics \
  --segment-only

python scripts/test_long_answer_search.py \
  --file ../기초통계_대본.txt \
  --lecture-id basic_statistics \
  --top-k-per-segment 5 \
  --max-evidence 12
```

분할은 문단, 문장부호와 `다음으로`, `반면`, `마지막으로` 같은 주제 전환 표현을
사용하므로 별도 LLM 호출이 없습니다. 모든 의미 단위는 한 번의 Embedding 배치로
처리하고, 구간별 검색 결과는 중복 Chunk를 제거하면서 각 구간의 근거가 골고루
남도록 합칩니다. `--show-segment-hits`를 추가하면 구간별 원본 순위도 확인할 수
있습니다. `--segment-only`는 API를 호출하지 않고 분할 결과만 보여줍니다. 거리
기준은 교정 사례를 충분히 모으기 전까지 기본적으로 강제하지 않으며, 필요하면
`--max-distance 0.55`처럼 실험할 수 있습니다.

검색이 검증되면 평가 LLM에 보낼 입력을 준비합니다. 이 단계는 의미 구간 임베딩과
ChromaDB 검색까지만 수행하며, 평가 LLM 자체는 아직 호출하지 않습니다.

```bash
python scripts/prepare_evaluation_input.py \
  --file ../기초통계_대본.txt \
  --lecture-id basic_statistics \
  --profile 2min
```

`--profile 2min`은 중간발표용, `--profile 3min`은 실제 서비스용입니다. 결과는
기본적으로 `outputs/evaluation_inputs/{lecture_id}_{profile}.json`에 저장됩니다.
이 파일에는 원문 STT, 의미 구간, 최종 검색 근거, 전체 강의 Rubric, 활성 프로필,
판정 규칙과 `EvaluationAssessment` 출력 스키마가 포함됩니다. API 키는 저장하지
않습니다.

준비된 입력을 평가 LLM에 보내 구조화 판정 JSON을 생성합니다.

```bash
python scripts/evaluate_prepared_input.py \
  --input outputs/evaluation_inputs/basic_statistics_2min.json
```

이 명령은 준비 파일에 기록된 모델로 OpenAI Responses API를 한 번 호출합니다.
결과는 `outputs/evaluations/basic_statistics_2min_assessment.json`에 저장되며, Rubric의
모든 주장·학습목표·관계·관계 체인 ID가 정확히 한 번씩 반환되지 않으면 저장하지
않습니다.

구조화 판정 결과를 40·40·20 기준으로 계산합니다. 이 단계는 로컬 계산이며 API를
호출하지 않습니다.

```bash
python scripts/score_evaluation_result.py \
  --assessment outputs/evaluations/basic_statistics_2min_assessment.json \
  --lecture-id basic_statistics \
  --profile 2min
```

점수는 기본적으로 `outputs/scores/{assessment_file_stem}_score.json`에 저장됩니다.

`--force`를 주지 않으면 원문 해시와 모델이 같은 페이지 캐시를 재사용합니다.

모든 페이지는 텍스트 유무나 이미지 감지 결과와 관계없이 비전 분석을 거칩니다.
기본 렌더링은 160 DPI이고 `VISION_DETAIL=original`을 사용합니다. 이미지에서만
확인되는 표, 그래프, 수식, 다이어그램, 스크린샷의 정보는 각 Chunk의
`visual_description`과 `content`에 반영됩니다.

## 주요 출력

```text
data/processed/{lecture_id}.json
data/indexing/embedding_manifest.json
outputs/cache/{lecture_id}/page_XXX.json
outputs/core_concepts/{lecture_id}.json
outputs/logs/pipeline.log
outputs/indexing/last_index_run.json
vector_db/
```

### 5단계 — (선택) 2차 후보정: 구어체를 기술 문서처럼 정리 (`organize_transcript`)

3단계까지의 `transcript_corrected`는 여전히 강의를 그대로 받아적은 **구어체**다
("그러니까", "이제", 말버릇, 반복 등이 남아있음). 이 단계는 `result.json`을 입력으로
받아 내용은 하나도 잃지 않은 채 문어체 기술 문서/강의 노트 형태로 다시 정리한다.

이 단계는 오디오 전사·1차 보정(1~4단계)과 **완전히 독립적인 코드**로 분리되어 있다 —
`run_pipeline`을 전혀 거치지 않고, 이미 저장된 `result.json`만 있으면 나중에 언제든
따로 실행할 수 있다.

```powershell
python -m sttcorrect.cli.organize_transcript `
  --result result.json `
  --out notes.json
```

내부적으로 일어나는 일:

1. `--result` 경로에서 `TranscriptionResult`(`result.json`)를 읽어 `transcript_corrected`를
   꺼낸다.
2. 이 텍스트를 Groq LLM에 보내 구어체 필러만 제거하고, 내용/맥락은 그대로 보존한 채
   문단 단위로 정리된 문어체로 다시 쓰게 한다 (요약이 아니다 — 개념이나 설명을
   생략/압축하지 않는다).
3. 결과를 `OrganizedTranscript` JSON으로 `--out` 경로에 저장한다:

```json
{
  "session_id": "abc123",
  "topic": "DB",
  "organized_text": "정리된 문어체 텍스트 (문단 구분 포함)"
}
```

`--out`으로 지정한 파일은 `result.json`과 별개의 파일이며, `result.json` 자체는
수정되지 않는다.

## 알려진 제한사항

- **Whisper 번역 드리프트**: 영어 전문용어가 밀집된 구간에서 드물게 `transcript_raw`가
  한국어가 아니라 완전한 영어 문장으로 전사되는 경우가 있다 (Whisper 계열 모델이
  "전사"/"번역"을 함께 학습해 생기는 알려진 결함 패턴). `transcript_raw`/
  `transcript_corrected`를 검토할 때 이런 구간이 있는지 확인하는 것을 권장한다.
  상세 조사 내용은 `WORK_LOG.md` 2026-08-18 세션 1절 참고.
- **Correction 단계의 잔여 과잉복원**: 드물게 이미 올바른 한국어 표현(예: "데이터베이스")이
  영어 표기("Database")로 잘못 바뀌는 경우가 있다. `term_db_used`의 용어 목록/분류를
  참고해 원인을 추적할 수 있다. 상세 내용은 `STT_MODEL_COMPARISON.md`, `WORK_LOG.md`
  참고.

## 테스트

```bash
pytest -q
```

## 평가 기준 데이터 검증

평가 기준은 키워드 출현 횟수가 아니라 학습목표, 의미 단위 주장, 개념 관계를
사용합니다. 모든 근거 페이지와 Chunk 참조를 검사하려면 다음을 실행합니다.

```bash
python scripts/validate_evaluation_data.py
```

공통 채점 정책은 `data/evaluation/scoring_policy.json`, 강의별 기준은
`data/evaluation/rubrics/`, 대표 교정 사례는
`data/evaluation/calibration_cases.jsonl`에 있습니다.

자유 복습 평가 범위는 `data/evaluation/profiles/`에서 선택합니다.

- `*_free_recall_3min.json`: 실제 서비스용 최대 3분 표준 프로필
- `*_free_recall_demo_2min.json`: 중간발표용 최대 2분 데모 프로필

두 프로필 모두 40·40·20점 체계를 사용하며, 2분 프로필은 강의 영역을 없애는
대신 각 영역에서 기대하는 설명 수만 줄입니다. 발화 시간 자체에는 점수를 주지
않습니다.
