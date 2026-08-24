# Docker·LLM 평가 데이터 검수 기록

두 원본 PDF의 전체 페이지를 시각·텍스트로 대조해 processed `2.1.0`, 한영 용어,
atomic Evidence와 Rubric `2.2.0`을 구성했다. 표지·목차·구분·마무리 페이지는 평가
Evidence에서 제외했다.

| 강의 | 페이지 | 용어 | Evidence unit | 상위 목표 | Claim |
| --- | ---: | ---: | ---: | ---: | ---: |
| Docker | 36 | 47 | 16 | 4 | 28 |
| Large Language Models | 73 | 58 | 39 | 4 | 33 |

## Docker

- `docker.foundations`: 컨테이너화와 Docker 객체
- `docker.image_build`: Dockerfile과 Image Build
- `docker.container_operations`: Container 운영과 데이터 영속성
- `docker.compose_networking`: Network와 Docker Compose

Dockerfile→image→container, client-daemon-registry 구조, instruction·layer·cache,
run·lifecycle·volume, bridge DNS와 Compose를 원자 근거에 연결했다.

### 원문 정규화

- p19는 container를 단순 restart하면 writable layer가 초기화된다는 설명을 제외했다.
  제거·재생성에 대비한 영속 데이터는 volume 또는 bind mount에 둔다.
- p32의 Compose를 Dockerfile의 변형이라고 한 표현을 제외했다. Compose는
  `compose.yaml`로 multi-container service를 구성·실행하는 별도 도구다.
- p34의 `depends_on`은 dependency order를 표현하지만 application readiness는
  healthcheck 조건 등을 함께 고려해야 한다.
- `docker compose down -v`는 volume data까지 삭제할 수 있는 명령으로 평가한다.

## Large Language Models

- `llm.architecture_models`: Transformer·BERT·GPT 구조
- `llm.scaling_alignment`: Scaling·ICL과 Alignment
- `llm.reasoning_preference`: Reasoning과 Preference 학습
- `llm.extensions`: LLM 확장 주제

Self-attention, BERT MLM·NSP, GPT next-token pretraining, scaling·ICL, IFT·RLHF,
CoT·tool use, reward model·DPO·RLVR·GRPO, diffusion LM·hallucination·RAG·VLA를
연결했다.

### 원문 정규화

- p12의 “기존 사전학습 모델은 모두 단방향”은 대표적인 기존 LM objective 다수로
  범위를 제한했다.
- p27 scaling은 scale의 지수 증가가 모든 성능의 선형 증가를 보장한다는 설명 대신
  parameter·data·compute와 loss 사이의 경험적 power-law 경향으로 평가한다.
- p29의 GPT-4 parameter 수, p57의 외부 일화, p58의 비공개 model 규모·시점 의존
  성능 평가는 정답 근거에서 제외했다.
- p37 IFT는 instruction-following behavior 조정이 주목적이지만 knowledge에 어떤
  영향도 없다고 절대화하지 않는다.
- p33의 benchmark 결과는 해당 TriviaQA setting의 사례이며 모든 task의 보편적
  우위로 일반화하지 않는다.

## 재생성·검증

```bash
python scripts/build_curated_json.py docker
python scripts/build_curated_json.py llm
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest
```
