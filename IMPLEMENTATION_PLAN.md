# STT & Audio Processing 파이프라인 — 구현 계획

> 이 문서는 `STT_Audio_Processing_개발명세.md`를 실제 코드로 옮기기 위한 상세 실행 계획이다.
> 이 저장소를 처음 여는 사람도 명세 + 이 문서 두 개만 보면 바로 PR1부터 착수할 수 있도록 작성했다.

## Context

명세 3.2절의 핵심 구조는 다음과 같다:

> "STT는 무조건 한국어로 전사 → PDF에서 뽑은 영어 용어 DB를 STT 힌트(initial_prompt/hotwords)와 LLM 보정 참고자료 두 군데에 각각 활용 → LLM이 문맥을 보고 한 번에 보정"

별도의 사전(dictionary) 기반 기계적 치환 단계는 **의도적으로 없다**. 명세 3.1절에서 fuzzy matching, stopword 리스트, `wordfreq` 필터링, `hangulize` 역음차 변환, TF-IDF 등 여러 대안이 검토 후 전부 기각되었고, 그 이유가 "PDF 표본 부족 상황에서는 통계적/사전적 방법으로 일반단어와 전문용어를 구분할 수 없다"는 결론이었다. 이 프로젝트의 모든 구현은 이 원칙을 재도입하지 않아야 한다 — 특히 용어 필터링에 빈도 기반 로직을 절대 넣지 않는다.

현재 저장소는 완전히 빈 상태이므로 프로젝트를 처음부터 구성한다.

**확정된 결정 사항**:
- LLM 보정 백엔드는 1차 초안에서 **Groq API + Llama3-8B**를 사용한다 (`llama3-8b-8192` 모델, OpenAI 호환 엔드포인트). 팀 내 추가 논의로 다른 백엔드로 바뀔 수 있으므로 `LLMClient` 인터페이스로 감싸 교체가 쉽도록 설계한다.
- 의존성 관리는 **pip + requirements.txt**를 사용한다 (Poetry/uv 아님).
- 명세의 "GPU 미사용, CPU만 사용" 제약은 STT(faster-whisper) 엔진에 대한 것이며, LLM 보정은 Groq API(외부 서버)를 호출하므로 이 제약과 무관하다.

---

## 프로젝트 구조

```
29th-project-ai-review/
├── STT_Audio_Processing_개발명세.md   # 원본 명세 (이미 존재)
├── IMPLEMENTATION_PLAN.md             # 이 문서
├── requirements.txt
├── .env.example                       # GROQ_API_KEY 등
├── .gitignore
├── README.md
├── config/
│   ├── stt_config.yaml                # SttConfig 기본값
│   └── seed_collision_terms.yaml      # 조사/동음이의어 curated 매핑 테이블
├── src/
│   └── sttcorrect/
│       ├── __init__.py
│       ├── config.py                   # yaml + .env 로더
│       ├── schema.py                   # TranscriptionResult, TermDBUsed, TermDB, TermEntry (pydantic)
│       ├── stt/
│       │   ├── __init__.py
│       │   └── whisper_backend.py      # WhisperSttBackend (faster-whisper 래퍼)
│       ├── term_db/
│       │   ├── __init__.py
│       │   ├── pdf_extract.py          # PDF 텍스트 추출 + 중복 라인 제거
│       │   ├── term_candidates.py      # 대문자/약어/영숫자혼합 후보 추출 (빈도 기반 필터 금지)
│       │   ├── mapping_pairs.py        # "RDBMS(알디비엠에스)" 류 한↔영 병기 추출
│       │   ├── transliterate.py        # 최소한의 fallback 음차 추정 (curated 테이블 우선)
│       │   ├── collision.py            # particle_collision / content_word_collision / safe 분류
│       │   ├── prompt_builder.py       # term_db -> (initial_prompt, hotwords)
│       │   └── builder.py              # PDF -> TermDB 전체 파이프라인
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py                 # LLMClient Protocol (call_llm(prompt) -> str)
│       │   ├── groq_client.py          # GroqLLMClient (llama3-8b-8192)
│       │   └── correction.py           # 프롬프트 빌더 (safe+content_word_collision 병합 vs particle_collision 분리)
│       ├── pipeline.py                 # 오케스트레이션: audio + term_db -> TranscriptionResult
│       └── cli/
│           ├── __init__.py
│           ├── build_term_db.py        # PDF -> term_db.json (1회성)
│           └── run_pipeline.py         # audio + term_db + topic + session_id -> result.json
├── data/
│   ├── term_dbs/                       # 코스별 생성 JSON (.gitkeep 외 gitignore)
│   └── samples/                        # 수동 테스트용 샘플 PDF/오디오 (gitignore)
├── scripts/
│   └── evaluate_corrections.py         # (PR8) 정답 대비 보정 정확도 실측용, pytest 아님
└── tests/
    ├── __init__.py
    ├── conftest.py                     # FakeSttBackend, FakeLLMClient, seed/TermDB fixture
    ├── test_schema.py
    ├── test_term_candidates.py
    ├── test_mapping_pairs.py
    ├── test_collision.py
    ├── test_prompt_builder.py
    ├── test_correction_prompt.py
    ├── test_pipeline_orchestration.py
    └── integration/                    # 기본 pytest 실행에서 제외 (실제 오디오/PDF/API 필요)
        ├── __init__.py
        ├── test_whisper_backend_smoke.py
        └── test_groq_client_smoke.py
```

---

## 모듈별 핵심 설계

### `schema.py` — 출력 계약

```python
from typing import Literal
from pydantic import BaseModel, Field

class TermDBUsed(BaseModel):
    safe: list[str] = Field(default_factory=list)
    content_word_collision: list[str] = Field(default_factory=list)
    particle_collision: list[str] = Field(default_factory=list)

class TranscriptionResult(BaseModel):
    session_id: str
    topic: str
    transcript_raw: str
    transcript_corrected: str
    term_db_used: TermDBUsed
    # .model_dump_json(ensure_ascii=False, indent=2) 로 명세 8절 JSON과 정확히 일치해야 함

class TermEntry(BaseModel):
    term: str                                              # 예: "RDBMS"
    korean_variants: list[str] = Field(default_factory=list)  # 예: ["알디비엠에스"]
    collision_label: Literal["safe", "content_word_collision", "particle_collision"]
    source: Literal["capitalized", "acronym", "alphanumeric", "mapping_pair"]

class TermDB(BaseModel):
    """빌드 단계의 rich 표현. 최종 출력에 들어가는 flat한 TermDBUsed와는 다른 표현이므로 섞지 말 것."""
    course_id: str | None = None
    topic: str | None = None
    entries: list[TermEntry]

    def to_term_db_used(self) -> TermDBUsed:
        """entries를 collision_label별로 묶어 순서 보존 + 중복 제거한 문자열 리스트로 변환"""
```

**주의**: `TermDB`(rich, 빌드 시점)와 `TermDBUsed`(flat, 출력 시점)는 반드시 별도 모델로 유지한다. LLM 프롬프트에서는 3분류를 2분류(안전/위험)로 합치지만, 최종 JSON에는 원래 3분류가 그대로 남아야 하기 때문 (7.2절 vs 8절 스키마 차이).

### `stt/whisper_backend.py`

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SttConfig:
    model_size: str = "small"
    device: str = "cpu"
    compute_type: str = "int8"
    cpu_threads: int = 4
    language: str = "ko"
    vad_filter: bool = True
    condition_on_previous_text: bool = False
    beam_size: int = 2

class WhisperSttBackend:
    def __init__(self, config: SttConfig | None = None) -> None:
        self._config = config or SttConfig()
        self._model = None  # lazy load — 생성/임포트 시점에 모델 로드 금지

    def _load_model(self):
        from faster_whisper import WhisperModel
        if self._model is None:
            self._model = WhisperModel(
                self._config.model_size,
                device=self._config.device,
                compute_type=self._config.compute_type,
                cpu_threads=self._config.cpu_threads,
            )
        return self._model

    def transcribe(
        self,
        wav_path: str | Path,
        initial_prompt: str | None = None,
        hotwords: str | None = None,
    ) -> str:
        """명세 5절의 파라미터 그대로 model.transcribe 호출, segment.text를 이어붙여 반환"""
        model = self._load_model()
        segments, _info = model.transcribe(
            str(wav_path),
            language=self._config.language,
            vad_filter=self._config.vad_filter,
            initial_prompt=initial_prompt,
            hotwords=hotwords,
            condition_on_previous_text=self._config.condition_on_previous_text,
            beam_size=self._config.beam_size,
        )
        return " ".join(seg.text.strip() for seg in segments)
```

모델 lazy load가 중요한 이유: 테스트나 다른 모듈이 이 파일을 import할 때마다 수백MB 모델이 로드되는 것을 막기 위함.

### `term_db/pdf_extract.py`

```python
from pathlib import Path

def extract_page_texts(pdf_path: str | Path) -> list[str]:
    """PyMuPDF(fitz)로 페이지별 page.get_text() 추출. 이미지 전용 페이지는 빈 문자열 반환
    (OCR은 명세상 범위 밖)"""

def dedup_lines(pages: list[str], repeat_threshold: float = 0.3) -> list[str]:
    """정규화한 라인이 전체 페이지의 repeat_threshold 비율 이상 반복되면(슬라이드 헤더/푸터/
    강의 제목 등) 첫 등장만 남기고 제거"""

def extract_and_dedup(pdf_path: str | Path) -> str:
    """extract_page_texts + dedup_lines 결과를 하나의 텍스트로 합침"""
```

### `term_db/term_candidates.py`

```python
import re

CAPITALIZED_RE = re.compile(r"\b[A-Z][a-zA-Z]+\b")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")
ALNUM_MIXED_RE = re.compile(r"\b[A-Za-z]+\d[A-Za-z0-9]*\b")  # 예: Neo4j, MySQL8

# 문법적 기능어(관사/전치사 등)만 걸러내는 닫힌 집합. 빈도/wordfreq 기반 필터가 아님에 주의.
FUNCTION_WORDS = {"The", "A", "An", "Of", "In", "On", "At", "And", "Or", "For", "To", "Is", "Are", "With", "By", "As"}

def extract_candidate_terms(text: str) -> set[str]:
    """3개 정규식의 합집합. 빈도/wordfreq/TF-IDF 필터링을 절대 추가하지 않는다
    (명세 3.1절에서 Transaction/Trigger/Primary 같은 핵심 용어가 걸러지는 문제로 기각됨)"""

def filter_function_words(candidates: set[str]) -> set[str]:
    """FUNCTION_WORDS(관사/전치사 등 닫힌 집합)만 제거. 도메인 일반단어까지 거르려던
    '하드코딩 stopword 리스트' 접근(기각됨)과는 다르다는 점을 테스트로 명시할 것"""
```

**필수 회귀 테스트**: `extract_candidate_terms`/`filter_function_words` 결과에 `Transaction`, `Trigger`, `Primary`가 살아남는지 확인 — 이 프로젝트에서 빈도 기반 필터링이 왜 금지되는지를 코드 차원에서 증명하는 테스트.

### `term_db/mapping_pairs.py`

```python
import re

_PAREN_EN_KO = re.compile(r"([A-Za-z][A-Za-z0-9]+)\s*\(([가-힣]+)\)")       # "RDBMS(알디비엠에스)"
_PAREN_KO_EN = re.compile(r"([가-힣]+)\s*\(([A-Za-z][A-Za-z0-9 ]+)\)")      # "관계형 데이터베이스(RDBMS)"
_DASH_EN_KO = re.compile(r"([A-Za-z][A-Za-z0-9]+)\s*[-–:]\s*([가-힣]+)")

def extract_mapping_pairs(text: str) -> list[tuple[str, str]]:
    """PDF 텍스트에서 영-한 병기 패턴을 찾아 (영어용어, 한글표기) 쌍 목록으로 반환.
    이후 TermEntry.korean_variants에 병합됨"""
```

### `term_db/transliterate.py`

```python
def guess_korean_transliteration(term: str) -> str | None:
    """아주 제한적인 규칙 기반 fallback 음차 추정. hangulize는 영어 역방향을 지원하지 않아
    기각되었고, 범용 음차기를 새로 만드는 것도 1차 범위 밖이므로, 짧은 단어 몇 개의 규칙만
    다룬다. collision.classify_term에서 curated 테이블/실제 관찰값을 모두 확인한 뒤
    최후 fallback으로만 사용. 매칭 실패 시 None → 호출측은 기본값 'safe' 처리"""
```

### `config/seed_collision_terms.yaml`

```yaml
particles: ["로", "가", "는", "은", "을", "를", "의", "에", "이"]
content_word_homophones: ["키", "셋", "원"]
known_terms:   # 수동 curated 테이블 — 항상 최우선
  Row: {korean: "로우", label: particle_collision}
  Key: {korean: "키", label: content_word_collision}
  Set: {korean: "셋", label: content_word_collision}
  One: {korean: "원", label: content_word_collision}
```

### `term_db/collision.py`

```python
from typing import Literal
from pydantic import BaseModel

class CollisionSeed(BaseModel):
    particles: list[str]
    content_word_homophones: list[str]
    known_terms: dict[str, dict]

def load_collision_seed(path: str = "config/seed_collision_terms.yaml") -> CollisionSeed: ...

def classify_term(
    term: str,
    seed: CollisionSeed,
    korean_variants: list[str] | None = None,
) -> Literal["safe", "content_word_collision", "particle_collision"]:
    """우선순위 (신뢰도 높은 순):
    1. seed.known_terms[term.lower()] — 수동 curated 테이블, 최우선
    2. korean_variants(PDF 실제 관찰값)가 seed.particles / seed.content_word_homophones에 걸리는지
    3. guess_korean_transliteration(term) fallback, 동일하게 멤버십 체크
    4. 기본값 'safe'
    """

def classify_terms(entries: list["TermEntry"], seed: CollisionSeed) -> list["TermEntry"]:
    """각 entry에 classify_term 적용 후 반환"""
```

이 우선순위 로직(curated > 관찰 > 추정 > 기본safe)이 이 프로젝트에서 **가장 중요한 비즈니스 로직**이며 가장 두껍게 테스트되어야 한다.

### `term_db/prompt_builder.py`

```python
def build_stt_hints(term_db: "TermDB", max_terms: int = 100) -> tuple[str, str]:
    """(initial_prompt, hotwords) 반환.
    initial_prompt: 짧은 한국어 프레이밍 문장 + 쉼표로 이은 용어 목록
    hotwords: 쉼표/공백으로 이은 용어 원문
    collision_label과 무관하게 전체 용어 사용 (음향 힌트 단계에서는 위험도 구분 무의미).
    max_terms로 길이 제한 (향후 절차 3번: 실측 후 튜닝)"""
```

### `term_db/builder.py`

```python
def build_term_db(
    pdf_path: str,
    topic: str | None = None,
    seed_path: str = "config/seed_collision_terms.yaml",
) -> "TermDB":
    """1. text = extract_and_dedup(pdf_path)
       2. candidates = filter_function_words(extract_candidate_terms(text))
       3. pairs = extract_mapping_pairs(text)
       4. candidates + pairs를 TermEntry 목록으로 병합 (korean_variants 부착)
       5. seed = load_collision_seed(seed_path); classify_terms(entries, seed)
       6. TermDB(topic=topic, entries=entries) 반환"""

def save_term_db(term_db: "TermDB", out_path: str) -> None: ...
def load_term_db(path: str) -> "TermDB": ...
```

### `llm/base.py`

```python
from typing import Protocol

class LLMClient(Protocol):
    def call_llm(self, prompt: str) -> str: ...
```

구조적 타이핑(Protocol)만 사용 — ABC 계층 없이 "인터페이스만 맞으면 교체 가능"이라는 명세 요구사항 그대로 최소하게 구현.

### `llm/groq_client.py`

```python
import os
import requests

class GroqLLMClient:
    """Groq의 OpenAI 호환 chat/completions 엔드포인트(https://api.groq.com/openai/v1)를
    requests로 호출. 팀 통합 LLM으로 교체 시 base_url/model/인증 방식만 바꾸면 되도록
    LLMClient 인터페이스만 구현."""

    def __init__(self, api_key: str | None = None, model: str = "llama3-8b-8192", timeout: float = 60.0) -> None:
        self._api_key = api_key or os.environ["GROQ_API_KEY"]
        self._model = model
        self._timeout = timeout
        self._base_url = "https://api.groq.com/openai/v1"

    def call_llm(self, prompt: str) -> str:
        resp = requests.post(
            f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
```

API 키는 `.env`의 `GROQ_API_KEY`에서만 로드하고 코드에 하드코딩하지 않는다.

### `llm/correction.py`

```python
PROMPT_TEMPLATE = """다음은 한국어 STT로 전사된 텍스트입니다. 아래 용어 목록을 참고해
발음이 잘못 인식된 부분을 자연스럽게 교정하세요. 문장 구조는 바꾸지 마세요.

일반 용어: {safe_terms}
※ 아래 단어는 한국어 문법요소/일상어와 발음이 겹칠 수 있어 문맥을 보고 신중히 판단하세요: {risky_terms}

원본 전사: {transcript}
교정된 텍스트만 출력하세요."""

def build_correction_prompt(transcript: str, term_db_used: "TermDBUsed") -> str:
    """명세 7.2절의 정확한 병합 규칙 구현:
    safe_terms = term_db_used.safe + term_db_used.content_word_collision
    risky_terms = term_db_used.particle_collision (이것만 분리)
    3분류 TermDBUsed -> 프롬프트 상 2분류로 축약"""
    safe_terms = term_db_used.safe + term_db_used.content_word_collision
    risky_terms = term_db_used.particle_collision
    return PROMPT_TEMPLATE.format(
        safe_terms=", ".join(safe_terms),
        risky_terms=", ".join(risky_terms),
        transcript=transcript,
    )

def correct_with_llm(transcript: str, term_db_used: "TermDBUsed", llm: "LLMClient") -> str:
    """build_correction_prompt 후 llm.call_llm 호출. llm은 DI로 주입 —
    파이프라인/테스트가 실제 백엔드 없이 Fake를 넣을 수 있게 함"""
    return llm.call_llm(build_correction_prompt(transcript, term_db_used))
```

### `pipeline.py`

```python
def run_pipeline(
    audio_path: str,
    term_db: "TermDB",
    session_id: str,
    topic: str,
    stt: "WhisperSttBackend | None" = None,
    llm: "LLMClient | None" = None,
) -> "TranscriptionResult":
    """1. initial_prompt, hotwords = build_stt_hints(term_db)
       2. stt = stt or WhisperSttBackend()
       3. transcript_raw = stt.transcribe(audio_path, initial_prompt, hotwords)
       4. term_db_used = term_db.to_term_db_used()
       5. llm = llm or GroqLLMClient()
       6. transcript_corrected = correct_with_llm(transcript_raw, term_db_used, llm)
       7. TranscriptionResult(session_id, topic, transcript_raw, transcript_corrected, term_db_used) 반환"""
```

`stt`/`llm` 옵션 주입 지점이 테스트 가능성의 핵심 — 프로덕션 코드는 기본값(실제 백엔드)을 쓰고, 테스트는 Fake를 주입한다.

### CLI

```
python -m sttcorrect.cli.build_term_db --pdf lecture.pdf --topic DB --out data/term_dbs/db_course.json
python -m sttcorrect.cli.run_pipeline --audio lec.wav --term-db data/term_dbs/db_course.json --topic DB --session-id abc123 --out result.json
```

`run_pipeline`은 `--term-db <json>`(권장, 재사용 가능) 또는 `--pdf <path>`(즉석 빌드) 중 하나를 받는다.

---

## 테스트 전략

**실제 모델/오디오/API 없이 바로 단위 테스트 가능** (`pytest tests/ --ignore=tests/integration`):

| 파일 | 검증 내용 |
|---|---|
| `test_term_candidates.py` | 정규식 후보 추출, `Transaction`/`Trigger`/`Primary` 생존 확인(회귀 가드) |
| `test_mapping_pairs.py` | 괄호/대시 병기 패턴 추출 (합성 텍스트 기준) |
| `test_collision.py` | 최우선순위 로직(curated > 관찰 > 추정 > 기본safe) 전 경로 커버 — **가장 중요한 테스트 파일** |
| `test_prompt_builder.py` | `build_stt_hints` 포맷/`max_terms` 절단 |
| `test_correction_prompt.py` | safe+content_word_collision 병합, particle_collision 분리, 빈 risky_terms 엣지케이스 |
| `test_schema.py` | `TranscriptionResult`가 명세 8절 JSON과 정확히 일치, `to_term_db_used()` 순서/중복제거 |
| `test_pipeline_orchestration.py` | `FakeSttBackend`/`FakeLLMClient`로 배선만 검증 (실제 추론 없음) |

**실제 오디오/PDF/Groq API 키 필요** (기본 pytest 실행에서 제외, `tests/integration/`):
- `test_whisper_backend_smoke.py` — 실제 wav 처리 시간 측정 (향후 절차 2번 근거 데이터)
- `test_groq_client_smoke.py` — 실제 Groq 호출, `GROQ_API_KEY` 없으면 skip

**pytest가 아닌 별도 스크립트로 관리**:
- `scripts/evaluate_corrections.py` — "Row/DB/Table"류 치명적 오류 빈도 측정(향후 절차 4번). 품질 실험이지 pass/fail 단위 테스트가 아니므로 분리.
- `content_word_collision`/`particle_collision` 매핑의 타 과목(CV, 통계) 일반화 검증(향후 절차 6번)은 README에 수동 체크리스트로 문서화.

---

## 의존성 (`requirements.txt`)

```
faster-whisper>=1.2.1,<2   # hotwords 파라미터는 1.2.1부터 지원
pymupdf>=1.24                # PDF 텍스트 추출 (C-core라 대용량에 강함, page.get_text()로 충분;
                              #   pdfplumber는 표 추출 특화라 이 용도엔 불필요)
pydantic>=2
pyyaml>=6
requests>=2.31               # Groq OpenAI 호환 엔드포인트 호출
python-dotenv>=1

# dev/test
pytest>=8
pytest-mock>=3
```

`ctranslate2`는 faster-whisper 종속으로 함께 설치되므로 직접 pin할 필요 없음(특정 CPU wheel 이슈 있을 때만 예외).

---

## 빌드 순서 (PR 단위)

1. **PR1 — 스캐폴딩 + 스키마**: `requirements.txt`, 패키지 골격, `schema.py` + `test_schema.py`. 무거운 의존성 없이 CI green.
2. **PR2 — PDF 텍스트 + 후보 추출**: `pdf_extract.py`, `term_candidates.py`, `mapping_pairs.py` + 테스트. 순수 텍스트 처리, 빈도 필터 없음을 테스트로 못박기.
3. **PR3 — 충돌 분류기**: `config/seed_collision_terms.yaml`, `collision.py`, `transliterate.py` + `test_collision.py`. 명세의 핵심 차별화 로직, 컨텍스트 신선할 때 먼저 처리.
4. **PR4 — 용어 DB 빌더 + STT 힌트 + CLI**: `builder.py`, `prompt_builder.py`, `cli/build_term_db.py`. 첫 실행 가능한 산출물: `PDF -> term_db.json`.
5. **PR5 — Whisper 래퍼**: `stt/whisper_backend.py` + 수동 스모크 테스트(샘플 wav, 기본 pytest 제외).
6. **PR6 — LLM 보정**: `llm/base.py`, `llm/groq_client.py`, `llm/correction.py` + Fake 기반 테스트.
7. **PR7 — 전체 파이프라인**: `pipeline.py`, `cli/run_pipeline.py`, `test_pipeline_orchestration.py`. 향후 절차 1번(오디오+PDF → 최종 JSON 실제 실행 파이프라인) 완성.
8. **PR8 (stretch)**: `tests/integration/`, `scripts/evaluate_corrections.py` 스켈레톤, README에 향후 절차 2/3/4/6번 수동 검증 체크리스트 문서화.

이 구조가 남겨두는 확장 지점: `LLMClient` 교체 = 향후 절차 5번(팀 통합 LLM으로 전환); `TermDB`가 코스별 JSON으로 영속화되어 재사용 가능 = 향후 절차 6번(타 과목 검증); `beam_size`/`max_terms`/hotwords가 모두 `SttConfig`/CLI 플래그로 외부화 = 향후 절차 2·3번 실측 튜닝; `schema.py`가 독립적이고 안정적 = 향후 절차 7번(RAG/평가 팀 핸드오프).

---

## 검증 방법

- PR1~7 각 단계마다 `pytest tests/ --ignore=tests/integration` 실행해 회귀 없는지 확인
- PR4 완료 시점: 실제 샘플 PDF로 `build_term_db` CLI 실행 → `term_db.json`의 3분류가 명세 4.2절 표 예시(`Row`→particle_collision, `Key`/`Set`→content_word_collision)와 일치하는지 수동 확인
- PR7 완료 시점: 샘플 오디오 + 위 term_db.json으로 `run_pipeline` CLI를 end-to-end 실행, 출력 JSON이 명세 8절 스키마와 정확히 일치하는지 확인 (`GROQ_API_KEY` 환경변수 필요)
- 이후 향후 절차 2~4(모델 크기/빔사이즈 튜닝, Row/DB/Table류 오류 빈도가 최종 채점 정확도에 미치는 영향)는 코드 완성 후 실측 기반으로 별도 진행
