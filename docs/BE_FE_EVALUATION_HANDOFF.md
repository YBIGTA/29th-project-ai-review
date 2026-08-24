# 백엔드·프론트엔드 평가 파이프라인 인계서

> 대상: 백엔드·프론트엔드 담당자  
> 목적: 완성된 평가 엔진을 웹의 녹음·STT 흐름과 안정적으로 연결하고 결과 화면을 구현한다.  
> 평가 데이터 담당자는 이 문서를 넘긴 뒤 나머지 강의 데이터를 같은 스키마로 확장한다.

## 1. 현재 상태와 담당 경계

평가 방식과 공통 평가 코드는 구현을 완료했다. 평가기는 사용자가 선택한 강의와
상위 학습목표 하나만 불러와 2분 발화문을 Claim 단위로 판정하고, 코드가 100점 만점
점수를 계산한다.

```text
강의·상위 학습목표 선택
→ 120초 녹음
→ STT 전사
→ 전문용어 보정
→ 발화문 Segment 분리
→ 선택한 Rubric branch와 Evidence 로드
→ LLM의 Claim별 구조화 판정
→ 코드의 60 + 20 + 20 점수 계산
→ 웹 응답 변환
```

평가기는 Embedding, ChromaDB, 코사인 검색을 사용하지 않는다. 선택한 branch의
Claim과 Claim이 직접 연결한 `chunk_id + unit_id` Evidence를 사용한다.

### 평가 데이터 담당 영역

- `data/processed/*.json`
- `data/evaluation/rubrics/*.json`
- `data/term_dbs/*.json` 검수
- Claim·Evidence·용어·Gold 데이터 확장
- 평가 기준과 점수 로직

### 백엔드·프론트엔드 담당 영역

- 녹음 파일 업로드와 STT 작업 상태 관리
- 평가 API 호출과 오류 처리
- 강의·상위 학습목표 선택 UI
- 점수·누락·오개념·복습 제안 결과 UI
- 필요하면 평가 결과 저장 및 조회

강의별 판정 차이를 백엔드 조건문이나 프론트 코드로 구현하지 않는다. 개념별 기준은
Rubric의 Claim, `evaluation_criteria`, Evidence에 기록한다.

## 2. 평가 핵심 코드

| 파일 | 역할 |
| --- | --- |
| `src/evaluation.py` | Rubric 로드, 선택 branch 조회, Evidence 로드, 검증, 점수 계산 |
| `src/evaluation_schemas.py` | Rubric과 LLM 구조화 판정 스키마 |
| `src/evaluation_prompt.py` | Claim별 판정 프롬프트 구성 |
| `src/evaluation_api.py` | OpenAI 구조화 응답 호출과 검증 실패 시 교정 재요청 |
| `src/transcript.py` | 발화문을 의미 Segment로 분리 |
| `backend/app/integrations.py` | 평가 결과를 웹 응답 구조로 변환 |
| `scripts/evaluate_topic.py` | 서버 없이 평가기를 직접 실행하는 CLI |

평가 통합의 공식 진입점은 다음 함수다.

```python
from backend.app.integrations import evaluate_selected_topic

result = evaluate_selected_topic(
    transcript=corrected_transcript,
    lecture_id="basic_statistics",
    objective_id="stats.probability_foundations",
    settings=settings,
    client=openai_client,
)
```

백엔드는 내부 평가 모듈을 각각 호출하기보다 이 함수를 사용한다.

## 3. 데이터 준비 상태

| lecture_id | 표시 이름 | 현재 상태 |
| --- | --- | --- |
| `basic_statistics` | 기초통계 | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `crawling` | 크롤링 | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `eda_fe` | EDA/FE | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `visualization` | 시각화 | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `cs_basics` | CS기초 | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `git` | Git | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `python_environment` | Python/개발환경 | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `web` | Web | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `network_basics` | 네트워크 기초 | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `machine_learning` | Machine Learning | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `deep_learning` | Deep Learning | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `computer_vision` | Computer Vision | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `nlp` | Natural Language Processing | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `docker` | Docker | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `llm` | Large Language Models | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `aws` | AWS | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `db` | Database | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `ai_agent` | AI Agent | atomic Evidence·용어·세부 판정 기준 검수 완료 |
| `rag` | Retrieval-Augmented Generation | atomic Evidence·용어·세부 판정 기준 검수 완료 |

백·프론트 통합 개발은 기초통계로 진행할 수 있다. 나머지 강의는 데이터 담당자가
완료 사실을 공유한 뒤 최종 평가 테스트 대상으로 사용한다.

## 4. 강의와 상위 학습목표 ID

`topic`, `lecture_id`, `objective_id`는 표시 문자열이 아니라 아래 값을 정확히 사용한다.

| topic | lecture_id | objective_id | 표시 제목 |
| --- | --- | --- | --- |
| 기초통계 | `basic_statistics` | `stats.probability_foundations` | 확률·통계의 기초 |
| 기초통계 | `basic_statistics` | `stats.hypothesis_uncertainty` | 가설검정과 불확실성 |
| 기초통계 | `basic_statistics` | `stats.anova_alternatives` | ANOVA와 가정 위반 대안 |
| 기초통계 | `basic_statistics` | `stats.regression_diagnostics` | 회귀분석과 진단 |
| 크롤링 | `crawling` | `crawl.foundations` | 크롤링의 목적과 범위 |
| 크롤링 | `crawling` | `crawl.html_requests` | HTML 구조와 HTTP 요청 |
| 크롤링 | `crawling` | `crawl.tools_responsibility` | 도구 선택과 책임 있는 수집 |
| EDA/FE | `eda_fe` | `eda.workflow_types` | 분석 흐름과 데이터 이해 |
| EDA/FE | `eda_fe` | `eda.quality_imbalance` | 데이터 품질과 클래스 불균형 |
| EDA/FE | `eda_fe` | `eda.relationships_preprocessing` | 변수 관계와 전처리 |
| EDA/FE | `eda_fe` | `eda.feature_engineering` | 특성공학과 누수 방지 |
| 시각화 | `visualization` | `viz.purpose_role` | 시각화의 목적과 설계 |
| 시각화 | `visualization` | `viz.chart_selection` | 데이터 관계에 맞는 차트 선택 |
| 시각화 | `visualization` | `viz.color_tools_quality` | 색상·도구 선택과 품질 검수 |
| 시각화 | `visualization` | `viz.storytelling` | 분석 스토리텔링 |
| CS기초 | `cs_basics` | `cs.scope_execution` | CS의 범위와 프로그램 실행 |
| CS기초 | `cs_basics` | `cs.os_protection` | 운영체제의 자원 관리와 보호 |
| CS기초 | `cs_basics` | `cs.linux_model` | Linux의 구조와 파일 권한 |
| CS기초 | `cs_basics` | `cs.virtualization_shell` | 가상화와 Linux 실습 |
| Git | `git` | `git.foundations` | Git과 버전 관리의 기초 |
| Git | `git` | `git.workflow` | 브랜치 작업과 이력 관리 |
| Git | `git` | `git.collaboration` | Git 협업 규칙과 코드 리뷰 |
| Python/개발환경 | `python_environment` | `python.environment_tools` | Python 개발환경과 도구 선택 |
| Python/개발환경 | `python_environment` | `python.virtual_environments` | 가상환경과 의존성 재현 |
| Python/개발환경 | `python_environment` | `python.code_quality` | 읽기 좋은 Python 코드 |
| Python/개발환경 | `python_environment` | `python.classes_oop` | 클래스와 객체 지향 |
| Web | `web` | `web.http_url` | URL과 HTTP 요청·응답 |
| Web | `web` | `web.frontend` | Web 프론트엔드 구조와 렌더링 |
| Web | `web` | `web.backend_api` | 백엔드 API와 RESTful 설계 |
| 네트워크 기초 | `network_basics` | `network.foundations` | 네트워크와 패킷 통신 |
| 네트워크 기초 | `network_basics` | `network.ip_transport` | IP·NAT와 전송 프로토콜 |
| 네트워크 기초 | `network_basics` | `network.dns_http` | DNS에서 HTTP 응답까지 |
| 네트워크 기초 | `network_basics` | `network.security` | 네트워크 암호화와 HTTPS |
| Machine Learning | `machine_learning` | `ml.valid_experiment` | 유효한 문제 정의와 실험 설계 |
| Machine Learning | `machine_learning` | `ml.model_selection` | 근거 기반 모델 선택 |
| Machine Learning | `machine_learning` | `ml.model_specific_pipeline` | 모델별 전처리와 특성공학 |
| Machine Learning | `machine_learning` | `ml.evaluation_improvement` | 평가·불균형 대응과 튜닝 |
| Deep Learning | `deep_learning` | `dl.representation_networks` | 표현학습과 신경망 |
| Deep Learning | `deep_learning` | `dl.loss_functions` | 손실 함수와 학습 목표 |
| Deep Learning | `deep_learning` | `dl.optimization` | 신경망 최적화 |
| Deep Learning | `deep_learning` | `dl.generalization_architectures` | 일반화와 MLP 이후 |
| Computer Vision | `computer_vision` | `cv.visual_foundations` | 시각 과제와 고전 특징 추출 |
| Computer Vision | `computer_vision` | `cv.cnn_representation` | CNN의 특징 학습 |
| Computer Vision | `computer_vision` | `cv.downstream_tasks` | Vision Downstream Task |
| Computer Vision | `computer_vision` | `cv.transformer_foundation` | ViT와 Vision Foundation Model |
| Natural Language Processing | `nlp` | `nlp.statistical_foundations` | 고전·통계 NLP와 단어 표현 |
| Natural Language Processing | `nlp` | `nlp.word2vec_embeddings` | Word2Vec 단어 임베딩 |
| Natural Language Processing | `nlp` | `nlp.sequence_models` | 언어 모델과 RNN 계열 |
| Natural Language Processing | `nlp` | `nlp.attention_llm` | Seq2Seq·Transformer와 LLM |
| Docker | `docker` | `docker.foundations` | 컨테이너화와 Docker 객체 |
| Docker | `docker` | `docker.image_build` | Dockerfile과 Image Build |
| Docker | `docker` | `docker.container_operations` | Container 운영과 데이터 영속성 |
| Docker | `docker` | `docker.compose_networking` | Network와 Docker Compose |
| Large Language Models | `llm` | `llm.architecture_models` | Transformer·BERT·GPT 구조 |
| Large Language Models | `llm` | `llm.scaling_alignment` | Scaling·ICL과 Alignment |
| Large Language Models | `llm` | `llm.reasoning_preference` | Reasoning과 Preference 학습 |
| Large Language Models | `llm` | `llm.extensions` | LLM 확장 주제 |
| AWS | `aws` | `aws.cloud_foundations` | 클라우드 컴퓨팅과 서비스 모델 |
| AWS | `aws` | `aws.services_compute` | AWS 서비스와 EC2 운영 |
| AWS | `aws` | `aws.network_security_deployment` | 네트워크·보안·배포 |
| Database | `db` | `db.foundations_rdbms` | DB·DBMS와 관계형 모델 |
| Database | `db` | `db.normalization_transactions` | 정규화와 트랜잭션 |
| Database | `db` | `db.sql_queries` | SQL 정의·조작·조회 |
| Database | `db` | `db.systems_selection` | OLTP·OLAP와 DB 선택 |
| AI Agent | `ai_agent` | `agent.core_components` | Agent 핵심 구성요소 |
| AI Agent | `ai_agent` | `agent.frameworks` | Agent Framework와 Workflow |
| AI Agent | `ai_agent` | `agent.protocols_tactics` | Protocol과 Engineering Tactic |
| AI Agent | `ai_agent` | `agent.design_harness` | Agent 설계와 Harness Engineering |
| Retrieval-Augmented Generation | `rag` | `rag.foundations_architecture` | RAG 목적과 전체 구조 |
| Retrieval-Augmented Generation | `rag` | `rag.embeddings_vector_search` | 임베딩과 벡터 검색 |
| Retrieval-Augmented Generation | `rag` | `rag.advanced_retrieval` | 고급 Retrieval 전략 |
| Retrieval-Augmented Generation | `rag` | `rag.chunking_contextual` | Chunking과 Contextual Retrieval |

평가 데이터에는 위 강의와 목표가 모두 준비돼 있지만 현재
`frontend/fe/components/ReviewApp.tsx`와 `backend/app/main.py`의 topic 목록은
기초통계·크롤링·EDA/FE·시각화까지만 등록돼 있다. 백·프론트 담당자는 위 표를 기준으로
새 강의 표시명, `lecture_id`, `objective_id`를 등록해야 웹에서 선택할 수 있다. 평가 데이터
확장 작업에서는 역할 경계에 따라 이 두 파일을 수정하지 않았다.

장기적으로 하드코딩을 제거하려면 백엔드가 Rubric에서 강의·상위목표 목록을 읽어 주는
조회 API를 추가할 수 있다. 현재 필수 작업은 아니다.

## 5. 환경 변수와 실행

프로젝트 루트 `.env`:

```dotenv
OPENAI_API_KEY=...
LLM_MODEL=gpt-5.6-luna
GROQ_API_KEY=...
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

프론트 `frontend/fe/.env.local`:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

`NEXT_PUBLIC_API_BASE_URL`을 비워 두면 프론트의 `/api/reviews/submit` Mock route가
사용될 수 있고 `/api/stt/transcribe`는 Next 앱에 구현돼 있지 않아 실패할 수 있다.
실제 통합 테스트에서는 반드시 FastAPI 주소를 지정한다.

백엔드 실행:

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```

프론트 의존성 설치 및 실행:

```bash
cd frontend/fe
npm install
npm run dev
```

헬스 체크:

```bash
curl http://localhost:8000/health
```

정상 응답:

```json
{"status":"ok"}
```

## 6. API 호출 순서

### 6.1 녹음 업로드

`POST /api/stt/transcribe`  
Content-Type: `multipart/form-data`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `session_id` | string | 프론트가 생성한 세션 ID |
| `topic` | string | 검수 완료 강의 표시명 중 하나. 현재 `기초통계`, `크롤링`, `EDA/FE`, `시각화`, `CS기초`, `Git`, `Python/개발환경`, `Web`, `네트워크 기초`, `Machine Learning`, `Deep Learning`, `Computer Vision`, `Natural Language Processing`, `Docker`, `Large Language Models`, `AWS`, `Database`, `AI Agent`, `Retrieval-Augmented Generation` |
| `audio_file` | file | WAV, WebM 또는 M4A |

성공 상태 코드는 `202 Accepted`다.

```json
{
  "job_id": "job-12자리ID",
  "session_id": "session-001",
  "topic": "기초통계",
  "status": "transcribing"
}
```

허용 확장자는 `.wav`, `.webm`, `.m4a`이며 MIME type도 함께 검증한다. 지원하지 않는
파일은 `415`, 알 수 없는 topic은 `400`을 반환한다.

### 6.2 STT 상태 Polling

`GET /api/stt/transcribe/{job_id}`

상태 전이는 다음과 같다.

```text
transcribing → correcting → corrected
                       └──→ failed
```

응답 예시:

```json
{
  "job_id": "job-12자리ID",
  "session_id": "session-001",
  "topic": "기초통계",
  "status": "corrected",
  "transcript_raw": "조건부 확률은...",
  "transcript_corrected": "조건부확률은...",
  "error": null
}
```

- `transcribing`, `correcting`: Polling 계속
- `corrected`: 평가 요청 가능
- `failed`: Polling 중단 후 `error` 표시
- 존재하지 않는 `job_id`: `404`

현재 프론트는 약 800ms 간격으로 Polling한다.

### 6.3 평가 요청

`POST /api/reviews/submit`  
Content-Type: `application/json`

```json
{
  "job_id": "job-12자리ID",
  "session_id": "session-001",
  "topic": "기초통계",
  "lecture_id": "basic_statistics",
  "objective_id": "stats.probability_foundations",
  "transcript_raw": "STT 원문",
  "transcript_corrected": "용어 보정문",
  "term_db_used": {
    "safe": [],
    "content_word_collision": [],
    "particle_collision": []
  }
}
```

평가는 `transcript_corrected`를 사용한다. `transcript_raw`는 결과 화면과 추적을 위해
그대로 돌려준다.

현재 백엔드 스키마에서는 `term_db_used`가 필수지만 평가 점수에는 사용하지 않는다.
STT 상태 응답이 이 값을 제공하지 않으므로 프론트는 현재처럼 빈 배열 구조를 보내도
된다. 백엔드 담당자가 계약을 단순화한다면 이 필드를 optional로 바꿀 수 있다.

`topic`과 `lecture_id`가 맞지 않으면 `400`, 평가 데이터·OpenAI 호출·검증 실패는
현재 `502`로 반환한다. Pydantic 입력 검증 실패는 `422`다.

## 7. 평가 응답 계약

성공 상태 코드는 `201 Created`, `status`는 `evaluated`다.

```json
{
  "review_id": "review-12자리ID",
  "session_id": "session-001",
  "lecture_id": "basic_statistics",
  "objective_id": "stats.probability_foundations",
  "score": 73.25,
  "transcript": "STT 원문",
  "corrected_transcript": "용어 보정문",
  "quantitative": {
    "scores": {
      "essential": {
        "score": 45.0,
        "max_score": 60,
        "rubric_level": 3,
        "reason": "하위 목표별 essential Claim의 정확도를 반영했습니다."
      },
      "supporting": {
        "score": 12.0,
        "max_score": 20,
        "rubric_level": 2,
        "reason": "Supporting Claim 설명 정확도를 반영했습니다."
      },
      "coverage": {
        "score": 16.25,
        "max_score": 20,
        "rubric_level": 3,
        "reason": "하위 학습목표의 충족 범위를 반영했습니다."
      }
    },
    "total": {
      "score": 73.25,
      "max_score": 100,
      "rubric_level": 3,
      "reason": "Rubric의 60+20+20 규칙으로 계산했습니다."
    },
    "sub_objective_coverage": [
      {
        "sub_objective_id": "stats.probability.random_variable",
        "ratio": 0.85,
        "base_ratio": 1.0,
        "coverage_cap": 0.85,
        "cap_reasons": ["하위 목표 안에 해결되지 않은 충돌이 있음"]
      }
    ]
  },
  "qualitative": {
    "strengths": ["정확하거나 대체로 정확하게 설명한 Claim 문장"],
    "missing_claims": ["발화에서 다루지 않은 Claim 문장"],
    "incorrect_claims": ["잘못 설명한 Claim 문장 — 판정 이유"],
    "review_suggestions": ["다음 복습 제안"]
  },
  "status": "evaluated"
}
```

`score`와 `quantitative.total.score`는 같은 값이다. 화면에서는 다음 세 영역을
60/20/20으로 표시한다.

| 키 | 표시명 | 만점 |
| --- | --- | ---: |
| `essential` | 핵심 이해도 | 60 |
| `supporting` | 보조·심화 설명 | 20 |
| `coverage` | 하위 목표 충족도 | 20 |

`rubric_level`은 0~4의 화면용 단계다. 최종 점수 계산의 입력이 아니다.

## 8. Claim 상세 결과에 관한 주의

평가 내부 결과에는 다음 정보가 존재한다.

- Claim별 `correct`, `mostly_correct`, `partial`, `incorrect`, `not_addressed`
- `conflict_status`: `none`, `self_corrected`, `unresolved`
- 학생 발화의 정확한 `evidence_spans`
- `supports`, `contradicts`, `corrects` 관계
- Claim별 판정 이유

현재 공개 API 응답은 이 데이터를 요약해 `strengths`, `missing_claims`,
`incorrect_claims`, `review_suggestions`만 반환한다. 프론트에서 Claim별 원문 인용과
세부 판정 화면이 필요하다면 백엔드 응답 스키마에 상세 필드를 추가해야 한다.

이 경우 평가 로직을 다시 구현하지 말고 `backend/app/integrations.py`에서 이미 생성된
assessment를 응답 형태로 노출한다. 필드명과 UI 범위는 백·프론트가 함께 확정한다.

## 9. 백엔드 통합 시 확인할 사항

1. `backend/app/integrations.py`의 `evaluate_selected_topic()`을 평가 진입점으로 사용한다.
2. `OPENAI_API_KEY`, `LLM_MODEL`, `GROQ_API_KEY` 누락을 시작 시 또는 요청 시 명확히 알린다.
3. 평가 요청 타임아웃을 짧게 잡지 않는다. LLM 판정과 검증 교정 재요청이 발생할 수 있다.
4. 현재 STT 작업 상태는 프로세스 메모리에 있으므로 서버 재시작 시 사라진다.
5. 업로드 음성은 `backend/data/audio/`에 저장되며 현재 자동 삭제 정책이 없다.
6. 평가 결과는 현재 DB에 영구 저장하지 않는다.
7. 배포 환경에서 여러 worker를 사용하면 메모리 기반 job 상태가 worker 사이에 공유되지 않는다.
8. 운영 수준에서는 작업 상태 저장소, 오디오 보존·삭제 정책, 결과 저장 방식을 별도로 정한다.
9. 평가 실패 시 내부 API 키나 전체 프롬프트를 사용자 오류 화면에 그대로 노출하지 않는다.

평가 데이터 파일과 평가 점수 로직은 데이터 담당자와 합의 없이 백엔드에서 수정하지 않는다.

## 10. 프론트엔드 통합 시 확인할 사항

1. 녹음 전에 강의와 상위 학습목표를 모두 선택하게 한다.
2. 녹음 시간은 120초를 기준으로 한다.
3. 녹음 종료 후 `transcribing`, `correcting`, `evaluating` 상태를 구분해 보여준다.
4. `corrected`가 된 뒤에만 `/api/reviews/submit`을 호출한다.
5. 평가 중 중복 제출을 막는다.
6. 결과 화면에 총점뿐 아니라 60/20/20 세부 점수와 이유를 표시한다.
7. 누락과 오개념을 서로 다른 영역으로 표시한다.
8. 실패 시 STT 실패와 평가 실패를 구분해 안내한다.
9. 실제 FastAPI 연결 시 `NEXT_PUBLIC_API_BASE_URL`을 반드시 확인한다.
10. Object URL과 MediaStream track을 종료해 브라우저 리소스를 정리한다.

현재 `frontend/fe/app/api/reviews/submit/route.ts`는 Mock 응답이다. 실제 통합 환경에서는
`NEXT_PUBLIC_API_BASE_URL`을 설정해 FastAPI로 요청하거나, Next route를 FastAPI proxy로
명확하게 바꾼다. Mock 결과를 실제 평가 결과로 오인하지 않는다.

## 11. 로컬 통합 점검 순서

1. `GET /health`가 `200`인지 확인
2. 기초통계와 상위 목표 하나 선택
3. WebM 녹음 업로드 후 `202`와 `job_id` 확인
4. Polling에서 `transcribing → correcting → corrected` 확인
5. raw·corrected transcript가 모두 비어 있지 않은지 확인
6. 평가 제출 후 `201`, `status=evaluated` 확인
7. 총점이 0~100이고 세 영역 만점이 60·20·20인지 확인
8. 결과 화면에 누락·오개념·복습 제안 표시
9. 잘못된 파일 형식, topic 불일치, 없는 objective ID 오류 처리 확인
10. 새로고침·서버 재시작 시 현재 메모리 상태 동작 확인

백엔드 단위 테스트:

```bash
python -m pytest tests/test_api.py -q
```

전체 Python 검증:

```bash
python scripts/validate_evaluation_data.py
python -m pytest -q
```

프론트 검증:

```bash
cd frontend/fe
npm run lint
npm run build
```

## 12. 변경 협업 규칙

데이터 담당자가 확장하면서 일반적으로 바꾸는 것은 processed, Rubric, 용어 DB,
Gold와 강의별 생성 스크립트다. 공통 API 필드와 평가 엔진은 그대로 유지한다.

다음 변경은 백·프론트에도 공유한다.

- `lecture_id`, `objective_id`, 표시 제목 변경
- 응답 필드 추가·삭제·이름 변경
- STT 상태 문자열 변경
- 120초 녹음 정책 변경
- 점수 영역이나 만점 변경
- Claim 상세 결과의 API 노출 결정

반대로 레이아웃, 상태 저장소, 오디오 저장 정책, 배포 CORS, API proxy와 같은 변경은
평가 데이터와 독립적으로 백·프론트가 진행할 수 있다.

## 13. 현재 완료 기준

다음은 이미 검증된 상태다.

- 선택한 상위 목표 branch만 평가
- Claim과 atomic Evidence 직접 연결
- 한국어·영어·약어·기호 동의 표현 전달
- 명시적 오개념과 미해결 충돌 판정
- 자기 정정 판정
- 정확한 복수 Evidence Quote 검증
- LLM 출력 검증 실패 시 한 번 교정 재요청
- Essential 60 + Supporting 20 + Coverage 20 결정적 계산
- Python 전체 테스트 110개 통과, 1개 제외

백·프론트 팀은 위 평가 로직을 재작성할 필요 없이 API 연결, 상태 관리, 결과 표현과
운영 안정성에 집중하면 된다.
