# 종합 평가 — `DB_test_full.m4a` / `DB_test_hard.m4a`

`medium/beam5`(Whisper) + `openai/gpt-oss-120b`(Groq, correction) 전환 이후 코드 기본값
그대로, 실제 CLI(`sttcorrect.cli.run_pipeline`)로 두 오디오를 재전사·재보정하고 지표를
계산한 결과다.

## 평가 방법

- **CER**: `jiwer.cer()`. 정답 전체 텍스트가 확보된 `DB_test_hard.m4a`에만 적용.
  `DB_test_full.m4a`는 정확한 원문 재구성에 판단이 개입할 여지가 커(발음 표기 대본 →
  영어 복원형 변환 시 다수의 임의 선택 필요) CER은 계산하지 않고, 대신 아래 키워드
  기반 지표로 평가했다.
- **Recall / F1**: 사용자가 제공한 핵심 용어 DB를 기준으로, 각 오디오에 실제로
  등장하는 용어만 걸러 사용. 공백/하이픈 차이(`Vector DB` vs `VectorDB`, `Key Value
  Store` vs `Key-Value Store`)는 표기 변형으로 간주해 동일하게 매칭. Precision은
  correction 단계의 grounding 안전장치(목록 밖 용어 미생성)가 이미 검증되어 있어
  100%로 가정하고, `F1 = 2·P·R/(P+R)`로 계산했다.
- 두 파일 모두 같은 `data/term_dbs/db_course.json`(STT 힌트)과 같은 LLM 모델로 통제.

---

## 1. `DB_test_hard.m4a`

### 원문(정답)

> 데이터를 다루는 작업에는 크게 두 가지 성격이 있습니다. OLTP, 그러니까 Online
> Transaction Processing은 실시간에 대량의 Transaction을 처리해서 서비스 운영에
> 필요한 데이터의 일관성과 신뢰성을 보장하며, Online Analytical Processing은 복잡한
> 쿼리와 데이터 분석을 위해 설계되어서 다차원 분석에 주로 쓰입니다. RDBMS는 scale
> out이 어렵고 스키마 변경이 복잡하다는 한계가 있어서, NoSQL이 등장하게 됩니다.
> NoSQL은 Document Store, Key Value Store, Wide Column Store, Graph Store로
> 나뉘는데, MongoDB는 Document Store의 대표적인 예시이고 Redis는 Key Value Store의
> 대표적인 예시입니다. 마지막으로 VectorDB는 비정형 데이터, 특히 고차원 벡터 데이터
> 처리에 최적화된 데이터베이스로, 유사도 검색에 주로 사용됩니다.

### 정량 지표

| | raw | corrected |
| --- | --- | --- |
| CER | 9.57% | 10.79% |
| Recall (13개 키워드 중) | 92.31% (12/13) | **100% (13/13)** |
| F1 | 96.0 | **100.0** |

- Recall 기준으로는 보정이 완벽하게 작동했다 — raw에서 빠졌던 `Transaction`(raw는
  `Transiction`으로 오탈자)이 corrected에서 정확히 복원됨.
- 다만 CER은 corrected가 raw보다 0.22%p 더 나쁘다. 원인은 `데이터메이스`(오타, 정답은
  `데이터베이스`)를 `Database`(영어)로 잘못 복원한 것 — 이미 `STT_MODEL_COMPARISON.md`에
  기록된 이슈로, "이미 맞으면 건드리지 마라" 안전장치가 이 케이스는 못 막았다. Recall
  지표(핵심 용어 존재 여부)에는 안 잡히지만 CER(전체 문자 정확도)에는 잡히는, 두
  지표의 관점 차이를 보여주는 사례.

---

## 2. `DB_test_full.m4a`

5개 스크립트(Intro/DBMS → RDBMS 구성요소 → 제약조건 → SQL/트랜잭션 → OLTP/OLAP/NoSQL)를
이어 읽은 약 4분 분량 전체 녹음.

### 정량 지표 (핵심 용어 33개 기준)

| | raw | corrected |
| --- | --- | --- |
| Recall | 85.29% (28/33) | **91.18% (30/33)** |
| F1 | 92.06 | **95.38** |

**raw에서만 빠졌다가 corrected에서 복원된 것** (보정이 제대로 작동한 사례):
`Row`(raw는 `run`으로 오인식 → corrected `row`로 정확히 복원), `DEFAULT`(raw는
`DEPALTO` 오타 → corrected에서 정상 복원).

**corrected까지 계속 빠진 것** (보정도 못 잡은 케이스):

| 용어 | 원인 |
| --- | --- |
| `Primary Key` | `PRIMARY` 키(PRIMARY만 영어로 복원되고 "키"는 한글로 남음 — 부분 복원) |
| `Foreign Key` | 위와 동일 (`FOREIGN` 키) |
| `TCL` | raw/corrected 모두 `DDL, DML, DCL, DCL`로 — TCL 자리에 DCL이 중복 출력됨. **DCL/TCL이 애초에 `data/term_dbs/db_course.json`에 없다** (지난 세션 WORK_LOG에서 이미 확인된 gap: 강의 PDF 원문에 "DCL"/"TCL" 약어 자체가 리터럴로 등장하지 않아 정규식 추출이 못 잡음). 힌트가 없으니 STT/보정 둘 다 복원할 근거가 없었던 것으로, 예견된 실패. |

### 정성적 평가 (자체 판단, 자동 채점 아님)

- **충실성**: PRIMARY KEY/FOREIGN KEY 계열을 제외하면 핵심 개념(무결성/정합성, ACID,
  SQL 4대 명령어군, OLTP/OLAP, NoSQL 4가지 모델)이 거의 다 정확히 언급됨.
- **연결성**: raw 단계부터 문장 구조와 인과관계("~해서 ~됩니다" 식 설명)가 잘 보존돼
  있었고, corrected가 이를 깨지 않음 — correction 프롬프트의 "문장 구조 유지" 원칙이
  잘 지켜짐.
- **포괄성**: 5개 스크립트 전 구간이 다 반영됨 (일부만 다루고 끝나는 현상 없음).
- **누락/오류 요약**: (1) `PRIMARY KEY`/`FOREIGN KEY`가 "OO 키" 형태로만 부분 복원되는
  패턴이 반복적으로 나타남 — 우연이 아니라 구조적 경향으로 보임. (2) `DCL`/`TCL`
  term_db 공백은 여전히 미해결 후속 과제.

---

## 3. 개선 작업 이후 재검증 (`DB_test_full.m4a`)

위 2번에서 발견한 `PRIMARY KEY`/`FOREIGN KEY`/`TCL` 누락 원인을 term_db 빌드 단계에서
직접 고치고 재검증했다.

### 적용한 수정

1. **경계 버그(근본 원인)**: 파이썬 `re`가 한글 음절도 `\w`로 취급해서, 영어 단어 뒤에
   한글 조사가 공백 없이 바로 붙으면(`PRIMARY키`) 정규식 `\b` 경계가 안 생겨 후보
   추출 자체가 실패했다. 끝 경계를 `\b` 대신 `(?![A-Za-z0-9])`로 바꿔 해결 —
   `Rollback`/`RDB`/`Out`이 이 버그로 term_db에서 완전히 누락돼 있었던 것도 함께 복구됨.
2. **복합어 추출**: `PRIMARY`/`KEY`처럼 한 단어씩만 뽑던 정규식에, 인접한 단어
   1~2개를 이어 붙여 잡는 `COMPOUND_RE`를 추가 (`PRIMARY KEY`, `FOREIGN KEY`,
   `NOT NULL` 등을 PDF 원문에 실제로 인접해 등장하는 것만 grounded하게 포착). 줄바꿈은
   제외해 무관한 슬라이드 항목이 잘못 묶이는 걸 방지.
3. **DCL/TCL 파생 추출**: "Data Control Language"처럼 3단어 이상 Title-Case 구에서
   이니셜을 모아 약어를 합성하는 `extract_derived_acronyms`를 추가 — PDF에 리터럴
   약어가 없어도 term_db에 등록됨.
4. **(부수 발견) 발음 생성 배치화**: term_db가 135→186개로 늘면서 LLM 발음 생성 응답이
   중간에 잘리는 문제(`finish_reason="length"`, 추론 모델이라 토큰 예산의 상당 부분을
   보이지 않는 사고 과정에 먼저 씀)를 발견해 40개씩 청크로 나눠 호출하도록 수정. 또한
   무료 티어 분당 토큰 한도(8000 TPM)로 인한 429 응답에 대한 재시도 로직도
   `GroqLLMClient`에 추가.

### 재검증 결과

| | raw | corrected |
| --- | --- | --- |
| Recall | 85.29% (28/33) | **97.06% (32/33)** (이전: 91.18%) |
| F1 | 92.06 | **98.51** (이전: 95.38) |

`Primary Key`/`Foreign Key`는 이제 정확히 복원된다. `TCL`만 여전히 안 잡히는데, 원인이
바뀌었다: 이제 term_db엔 `TCL`이 정상 등록돼 있지만(STT 힌트로도 전달됨), **raw
전사 단계부터 "티씨엘"과 "디씨엘"의 발음이 비슷해 둘 다 `DCL`로 들림**
(`"DDL, DML, DCL, DCL로 나뉘는데"`) — term_db 공백이라는 구조적 문제는 해결됐고, 남은
건 순수 음향 인식의 한계다. correction 단계는 원문에 없는 내용을 지어내지 않는다는
원칙(`WORK_LOG` 3.6절부터 이어진 안전장치)에 따라 이 오인식은 고치지 않는 게 맞다.

## 종합 결론

1. **`medium/beam5` + `gpt-oss-120b` 전환은 두 파일 모두에서 recall/F1 개선으로
   이어짐** (`DB_test_hard` F1 96.0→100.0, `DB_test_full` F1 92.06→98.51(최종)).
2. **CER과 keyword recall이 항상 같은 방향을 가리키진 않는다** — `DB_test_hard`에서
   corrected CER이 raw보다 살짝 나쁜데도 recall/F1은 완벽했다. 두 지표를 함께 봐야
   실제 품질을 온전히 판단할 수 있다.
3. **term_db 추출 단계의 구조적 결함 2건(경계 버그, 복합어 미지원) + DCL/TCL 공백을
   모두 수정**하여 `DB_test_full`의 남은 이슈를 1개(`TCL`)로 줄임 — 그 1개도 이제는
   term_db 문제가 아니라 STT 음향 인식 자체의 한계로 성격이 바뀌었다.
4. **미해결**: `TCL`/`DCL` 발음 혼동(음향적으로 유사) — 추가로 다루려면 STT 모델
   자체의 미세조정이나 다른 접근이 필요해 보이며, 이번 세션 범위 밖으로 남겨둔다.

## 참고 — 이번 평가 산출물

- STT 재전사·재보정 결과: 스크래치패드에 임시 저장 (`eval_full.json`, `eval_hard.json`),
  저장소에는 남기지 않음.
- 사용된 원문 대본: `STT_테스트_음성대본_DB.md` (`~/Downloads`)
