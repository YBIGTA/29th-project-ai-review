# AI Agent·RAG 평가 데이터 확장 기록

## 완료 범위

두 PDF의 모든 페이지를 원본 text와 slide image로 대조해 다음 산출물을 만들었다.

| 강의 | 페이지 | 상위 목표 | Claim | 주요 근거 페이지 |
|---|---:|---:|---:|---|
| AI Agent | 53 | 4 | 34 | p9-18, p21-30, p32-40, p43-52 |
| Retrieval-Augmented Generation | 35 | 4 | 35 | p5-12, p14-23, p25, p27-34 |

- `data/processed/ai_agent.json`, `data/processed/rag.json`: schema 2.1, 전체 페이지
  원문, 검수 content, 한·영 용어·약어, atomic Evidence, source issue
- `data/evaluation/rubrics/ai_agent.json`, `data/evaluation/rubrics/rag.json`: schema 2.2,
  120초 선택 목표 평가, Claim별 Evidence·용어·critical error
- `scripts/build_ai_agent_evaluation_data.py`, `scripts/build_rag_evaluation_data.py`: 동일 결과 재생성

표지·목차·섹션 구분·마무리 페이지는 `page_role`로 분리해 평가 Evidence로 사용하지
않는다. Workflow, graph, retrieval architecture처럼 text extraction만으로 관계가 손실될
수 있는 정보는 slide image를 함께 확인했다.

## AI Agent 목표

1. `agent.core_components`: ReAct·Function Calling·MCP, memory, structured output
2. `agent.frameworks`: LangChain·LCEL·LangGraph, ADK·CrewAI·n8n과 선택 기준
3. `agent.protocols_tactics`: agent protocol, triage·handoff, scaling·persona·prompt structure
4. `agent.design_harness`: workflow plan, prompt·context·harness, invariant·verification·human role

정답 기준에서는 LangGraph를 DAG로 한정하는 설명, LangChain·LangGraph를 single-agent
전용으로 보는 설명, 특정 framework의 보편적 우월성, persona·autoscaling 효과의 무조건적
보장을 제외하거나 교정했다. Function calling은 model의 호출 제안과 orchestrator의 실제
실행을 구분하고, MCP도 permission·security·context 관리가 필요한 protocol로 설명한다.

## RAG 목표

1. `rag.foundations_architecture`: LLM 한계, RAG 정의, indexing·query 흐름, sparse·dense retrieval
2. `rag.embeddings_vector_search`: similarity metric, representation·contrastive learning,
   vector DB·HNSW·PQ와 embedding 평가
3. `rag.advanced_retrieval`: Basic RAG failure, Graph·Hybrid RAG, corrective feedback loop
4. `rag.chunking_contextual`: semantic chunking·overlap, contextual prepending,
   hybrid search·rank fusion·reranking

정답 기준에서는 Euclidean distance가 고차원에서 언제나 사용 불가라는 표현, HNSW의
strict `O(log N)`·exact accuracy 보장, 모든 language model의 자동 sentence embedding,
Graph query의 exact entity 문자열 필수 조건을 일반화하지 않는다. p29의 출처 없는 성능
수치는 제외하고, p30의 `Self-RAG`는 슬라이드가 설명한 corrective/self-reflective feedback
pattern 범위로 한정했다.

## 재생성과 검증

```bash
python scripts/build_curated_json.py ai_agent
python scripts/build_curated_json.py rag
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest -q
```

현재 전체 검증 결과는 `110 passed, 1 skipped`다.

백엔드와 프론트엔드 코드는 이번 확장에서 수정하지 않았다.
