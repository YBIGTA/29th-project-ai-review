# STT 모델 비교 — `small/beam2`(현재 기본값) vs `medium/beam5`

이 문서는 사용자가 별도로 진행한 자체 평가(모델 크기 × `beam_size` 4가지 조합 + GPT-4o
계열, `jiwer` CER + 키워드 recall/F1, 루브릭 설계)를 이어받아, 이 레포의 실제 파이프라인
(term DB 기반 STT 힌트 + LLM 보정 포함)으로 `DB_test_hard.m4a` 1개 파일에 대해 재현
검증한 결과다. 원 평가는 `medium/beam5`를 최적으로 꼽았고, 이 문서는 그 결론을 이
레포 코드로 다시 확인한다.

## 진행 중 발견한 이슈 — 기본 LLM 모델 단종

비교를 진행하던 중 `llm/groq_client.py`의 기본 모델 `llama-3.3-70b-versatile`이 Groq
API에서 완전히 제거된 것을 발견했다 (`404 model_not_found`). 이 세션 초반까지는 정상
동작했으므로 최근에 Groq 쪽에서 모델을 내린 것으로 보인다. 이 문제는 STT 비교와 무관하게
파이프라인 전체를 막고 있어 먼저 해결했다.

Groq에 현재 이 API 키로 접근 가능한 모델 목록을 조회하고, 이 프로젝트의 단일턴 한국어
텍스트 교정 작업에 실제로 쓸 수 있는지 직접 테스트했다:

| 모델 | 테스트 결과 |
| --- | --- |
| `openai/gpt-oss-120b` | 정상 동작 — 채택 |
| `openai/gpt-oss-20b` | 응답 `content`가 빈 문자열로 옴 (reasoning에 토큰 소진, 최종 답 없음) |
| `qwen/qwen3.6-27b` | 최종 답 없이 `<think>...</think>` 사고 과정 원문이 그대로 `content`에 출력됨 — `groq_client.py`가 `content`를 그대로 `transcript_corrected`로 쓰기 때문에 파이프라인이 깨짐 |
| `groq/compound-mini` | 정상 동작하지만 에이전틱(도구 호출) 모델이라 용도가 다르고, 답변도 다소 어색("데이터 무결성, 즉 데이터 무결성" 중복) |
| `allam-2-7b` | 아랍어 특화 모델 — 한국어 질문에 엉뚱하게 답함 |

**조치**: `src/sttcorrect/llm/groq_client.py`의 기본 `model`을 `openai/gpt-oss-120b`로
변경함. 아래 비교는 모두 이 모델로 통제해 진행했다 (STT 설정만 변수로 남기기 위함).

## 비교 방법

- 오디오: `data/voice/DB_test_hard.m4a`
- STT 힌트: 현재 `data/term_dbs/db_course.json` 기반 `initial_prompt`/`hotwords` 동일 사용
- 보정(LLM): 두 설정 모두 동일하게 `openai/gpt-oss-120b`로 `correct_with_llm` 실행 —
  이전 세션에 확정한 "이미 맞으면 건드리지 말 것 + 헷갈리면 다른 용어로 착각하지 말 것"
  조건부 영어 복원 프롬프트 그대로 사용
- 채점: `jiwer.cer()`, 정답 텍스트는 사용자가 직접 제공한 스크립트 사용
- `small/beam2`의 raw 전사는 이전 세션(같은 term DB·설정)에 이미 확보해 둔 결과를
  재사용하고, `medium/beam5`만 이번에 새로 전사 실행

## 정답 텍스트

> 데이터를 다루는 작업에는 크게 두 가지 성격이 있습니다. OLTP, 그러니까 Online
> Transaction Processing은 실시간에 대량의 Transaction을 처리해서 서비스 운영에
> 필요한 데이터의 일관성과 신뢰성을 보장하며, Online Analytical Processing은 복잡한
> 쿼리와 데이터 분석을 위해 설계되어서 다차원 분석에 주로 쓰입니다. RDBMS는 scale
> out이 어렵고 스키마 변경이 복잡하다는 한계가 있어서, NoSQL이 등장하게 됩니다.
> NoSQL은 Document Store, Key Value Store, Wide Column Store, Graph Store로
> 나뉘는데, MongoDB는 Document Store의 대표적인 예시이고 Redis는 Key Value Store의
> 대표적인 예시입니다. 마지막으로 VectorDB는 비정형 데이터, 특히 고차원 벡터 데이터
> 처리에 최적화된 데이터베이스로, 유사도 검색에 주로 사용됩니다.

## 결과 — CER (jiwer, 정답 텍스트 기준)

| 설정 | raw CER | corrected CER |
| --- | --- | --- |
| `small, beam2` (현재 기본값) | 37.27% | 23.83% |
| `medium, beam5` | **9.57%** | 10.79% |

- `medium/beam5`의 raw(보정 전) 결과가 `small/beam2`의 corrected(보정 후) 결과보다도
  훨씬 정확하다 (9.57% vs 23.83%) — STT 자체 품질 차이가 보정으로 메울 수 있는 수준을
  넘어선다.
- `medium/beam5`는 raw가 이미 매우 정확해서, 이번 실행에서는 LLM 보정이 오히려 아주
  살짝 CER을 악화시켰다 (9.57%→10.79%). 원인은 아래 "발견한 이슈" 참고.

## 소요 시간

| 설정 | 소요 시간 |
| --- | --- |
| `medium, beam5` (이번 세션 실측, `DB_test_hard.m4a` 1건) | 41.46초 |
| `medium, beam5` (사용자 자체 벤치마크, 파일 2건 평균) | 47.31초 |
| `small, beam2` (사용자 자체 벤치마크, 파일 2건 평균, 참고용 — 이번 세션에서 재측정하지 않음) | 11.64초 |

## 발견한 이슈 — correction 단계의 잔여 과교정 사례

`medium/beam5`의 raw 전사는 `"...최적화된 데이터메이스로..."`(오타)였다. 정답은
`"...최적화된 데이터베이스로..."`(한국어 유지)인데, LLM 보정이 이를 `"...최적화된
Database로..."`(영어)로 바꿔버렸다. `Database`류 표기가 term DB에 있어서 "명백히
틀린 발음은 영어로 복원하라"는 규칙이 여기서도 발동한 것으로 보인다 — 지난 세션에
다듬은 안전장치("이미 맞으면 건드리지 마라")로도 못 막은 엣지케이스다. 이번 비교에서
`medium/beam5`의 corrected CER이 raw보다 살짝 높게 나온 주 원인이 이것이다. 파급은
작지만(단어 1개), 프롬프트를 더 다듬을 여지가 남아있다는 신호로 기록해 둔다.

## 실제 전사 텍스트

**`medium, beam5` raw**
> 데이터를 다루는 작업에는 크게 두 가지 성격이 있습니다. OLTP, 그러니까 Online
> Transiction Processing은 실시간의 대량의 트랜지션을 처리해서 서비스 운영에 필요한
> 데이터의 일건성과 신뢰성을 보장하고요. OLAP, Online Analytical Processing은 복잡한
> 커리와 데이터 분석을 위해 설계되어서 다 차원 분석에 주로 쓰입니다. RDBMS는 Scale
> Out이 어렵고 Schema 변경이 복잡하다는 한계가 있어서 NoSQL이 등장하게 됩니다 NoSQL은
> Document Store, Key Value Store, Wide Column Store, Graph Store로 나뉘는데
> MongoDB는 Document Store의 대표적인 예시이고 Redis는 Key Value Store의 대표적인
> 예시입니다 VectorDB는 비정형 데이터, 특히 고차원 데이터 처리에 최적화된
> 데이터메이스로 유사도 검색에 주로 사용됩니다.

**`medium, beam5` corrected**
> 데이터를 다루는 작업에는 크게 두 가지 성격이 있습니다. OLTP, 그러니까 Online
> Transaction Processing은 실시간의 대량의 트랜지션을 처리해서 서비스 운영에 필요한
> 데이터의 일건성과 신뢰성을 보장하고요. OLAP, Online Analytical Processing은 복잡한
> 커리와 데이터 분석을 위해 설계되어서 다 차원 분석에 주로 쓰입니다. RDBMS는 Scale
> Out이 어렵고 Schema 변경이 복잡하다는 한계가 있어서 NoSQL이 등장하게 됩니다 NoSQL은
> Document Store, Key Value Store, Wide Column Store, Graph Store로 나뉘는데
> MongoDB는 Document Store의 대표적인 예시이고 Redis는 Key Value Store의 대표적인
> 예시입니다 VectorDB는 비정형 데이터, 특히 고차원 데이터 처리에 최적화된 Database로
> 유사도 검색에 주로 사용됩니다.

**`small, beam2` raw**
> 데이터를 다루는 작업에는 크게 두 가지 성격이 있습니다. OLTP, 그러니까 온라인
> 트랜젝션 프로세싱은 실시간의 대량의 트랜젝션을 처리해서 서비스 운영에 필요한
> 데이터의 일괄성과 실례성을 보장하고요. OLAP, 온라인, 엔얼리티컬 프로세싱은 옥잡한
> 커리와 데이터 분석을 위해 설계되어서 다쳐온 분석의 주로 쓰입니다. RDBMS는 스케일
> 아웃이 어렵고, 스키마변경이 복잡하다는 한계가 있어서 NoSQL이 등장하게 됩니다.
> NoSQL은 다큐먼트 스토어, 키벨류 스토어, 와이드 컬럼 스토어, 그래프 스토어로는
> 아니는데, MongoDB는 다큐먼트 스토어의 대표적인 예시이고, 레디스는 키벨류 스토어의
> 대표적인 예시입니다. 마지막으로 VectorDB는 비정형 데이터, 특히 고창원 Vector 데이터
> 처리에 최적화된 데이터메이스로 유사도 검색에 주로 사용됩니다.

**`small, beam2` corrected**
> 데이터를 다루는 작업에는 크게 두 가지 성격이 있습니다. OLTP, 그러니까 Online
> Transaction Processing은 실시간의 대량의 Transaction을 처리해서 서비스 운영에
> 필요한 데이터의 일괄성과 Consistency를 보장하고요. OLAP, Online Analytical
> Processing은 옥잡한 Query와 데이터 분석을 위해 설계되어서 다쳐온 분석의 주로
> 쓰입니다. RDBMS는 Scale 아웃이 어렵고, 스키마변경이 복잡하다는 한계가 있어서
> NoSQL이 등장하게 됩니다. NoSQL은 다큐먼트 스토어, Key-Value 스토어, Wide 컬럼
> 스토어, 그래프 스토어로는 아니는데, MongoDB는 다큐먼트 스토어의 대표적인 예시이고,
> Redis는 Key-Value 스토어의 대표적인 예시입니다. 마지막으로 VectorDB는 비정형
> 데이터, 특히 고창원 Vector 데이터 처리에 최적화된 Database로 유사도 검색에 주로
> 사용됩니다.

## 결론 및 적용 사항

- `medium/beam5`로 전환하는 방향은 이 레포의 실제 파이프라인으로도 재현 확인됨 —
  사용자의 원 평가 결론과 일치.
- **적용 완료**: `src/sttcorrect/llm/groq_client.py` 기본 모델을
  `llama-3.3-70b-versatile` → `openai/gpt-oss-120b`로 교체 (단종된 모델 대응, 별도
  이슈였지만 이번 비교의 전제조건이라 함께 처리함).
- **적용 완료**: `src/sttcorrect/stt/whisper_backend.py`의 `SttConfig` 기본값을
  `model_size="small", beam_size=2` → `model_size="medium", beam_size=5`로 변경.
- 후속 과제: correction 프롬프트의 "이미 맞으면 건드리지 마라" 안전장치가 여전히
  일부 케이스(`데이터메이스`→`Database`)에서 뚫리는 것을 확인 — 추가 튜닝 여지 있음.
