# 작업 로그 — 2026-08-14

이 문서는 한 세션 동안 진행된 환경 구성, 실행 검증, 그리고 "한국어 용어 DB 2-pass" 기능의
도입/평가/롤백 과정을 시간 순으로 기록한다. 설계 배경 자체는 `IMPLEMENTATION_PLAN.md`를,
현재 사용법은 `README.md`를 참고한다. 이 문서는 "왜 지금 이 구조가 아닌지"를 설명하는
의사결정 기록이다.

## 1. 환경 구성

- JDK(Temurin 17)는 이미 설치돼 있었으나 `java` 명령이 인식되지 않았던 원인은 PATH 갱신을
  위해 터미널 재시작이 필요했던 것뿐이었다 (VSCode 재시작 후 정상 인식 확인).
- 프로젝트에는 `venv/`가 이미 있었지만 `faster-whisper`/`pymupdf` 등 핵심 의존성만 설치돼
  있었고, `sttcorrect`는 editable 모드로 설치돼 있었다. 이후 모든 실행은 anaconda 환경이
  아니라 `venv/Scripts/python.exe`로 통일했다.
- `requirements.txt`는 검토 결과 이미 파이프라인에 필요한 패키지를 빠짐없이 명시하고
  있었다 (JPype1/lxml/av 등은 konlpy/faster-whisper의 전이 의존성이라 별도 명시 불필요).

## 2. 실제 데이터로 파이프라인 첫 검증

`data/pdfs/DB.pdf` + `DB_test_normal.m4a`로 `run_pipeline` CLI를 end-to-end 실행해
정상 동작을 확인했다. 이 과정에서 `pdf_extract.py`가 deprecated된 `import fitz`를 쓰고
있는 것을 발견해 `import pymupdf`로 교체했다.

## 3. 한국어 용어 DB(2-pass) 기능 도입 — 배경과 실패

### 3.1 동기

STT가 한국어 단어를 잘못 알아듣는 경우(예: "무결성"→"물결성", "동시성"→"동실성")를
교정하기 위해, PDF에서 Okt로 한국어 고유명사를 뽑아 별도 DB로 만들고, 영어 용어 보정
전에 1차로 이 DB를 참고해 한국어 오인식을 고치는 2-pass 구조를 추가했다.

### 3.2 1차 구현 — LLM 기반 한국어 보정 (실패)

`llm/korean_correction.py`에 "용어 목록 참고해서 자연스럽게 고쳐라"는 열린 프롬프트로
LLM 보정을 구현했다. 실제 오디오로 테스트한 결과, LLM이 편집 거리와 무관하게 자기
도메인 지식으로 문장을 재구성해버렸다 — "데이터 인테그리티"(영어 용어의 한글 발음
전사)를 "데이터 무결성"으로 통째로 "번역"하며, 뒤이은 영어 용어 복원 pass가 필요로
하는 음차 흔적 자체를 지워버렸다. 그 결과 최종 출력에서 `Data Integrity`/
`Data Consistency` 같은 원래 목표였던 영어 용어 복원이 오히려 실패했다.

### 3.3 2차 구현 — 편집 거리 기반 결정적 매칭

LLM의 "의미 기반 재작성" 위험을 구조적으로 없애기 위해 `term_db/korean_correction.py`에
Levenshtein 편집 거리 기반 결정적 매칭으로 재작성했다 (LLM 미사용). 첫 버전은 실제
오디오로 테스트한 결과 **더 심각한 회귀**를 일으켰다 — "오늘은"→"오류은", "정리해"→
"관리해"처럼 완전히 정상적인 단어까지 대거 오염됐다. 원인은 두 가지였다:

1. 어절에 이미 정확히 일치하는 term이 있어도, 알고리즘이 그걸 무시하고 다른 term과의
   fuzzy 매칭을 계속 시도해 엉뚱한 term으로 덮어썼다.
2. `term_db_ko`는 PDF 전체에서 빈도 필터링 없이 뽑은 일반 명사 489개까지 포함하는데
   ("무결성"급 실제 오타 대상뿐 아니라 "하나"/"관리" 같은 흔한 2글자 단어도 섞여 있음),
   2글자 term에 편집 거리 1을 허용하면 절반이 다른 무관한 실제 단어("하다" vs "하나")
   까지 오염시켰다.

두 가지 안전장치(정확 일치 시 fuzzy 매칭 생략, 2글자 미만 term은 fuzzy 후보 제외)를
추가해 오염은 해결했지만, 그 대가로 애초 목표였던 "물결성"→"무결성" 케이스가 다시 안
잡히게 됐다 — Okt가 "무결성"을 "무결"(2글자)+"성"으로 쪼개 `term_db_ko`에 3글자
단일 토큰으로 들어가 있지 않았기 때문이다.

## 3.5 실제 강의 오디오(`DB_test_full.m4a`, 4분)로 STT 모델 크기 A/B 실측

한국어 일반 단어 오인식(`급여`→`그 별`, `동실성`→`동시성` 등)이 term_db 밖이라 LLM
보정으로 못 잡는 게 확인된 뒤, "STT 모델 자체를 키우면 해결되는지"를 실측했다.

**방법**: 동일 오디오/동일 term_db로 `small`(beam=2, 기존 기본값)과 `medium`(beam=5)
두 설정의 `transcript_raw`를 각각 뽑고, 이어서 동일한 `correct_with_llm`으로
`transcript_corrected`까지 생성해 최종본까지 비교했다. (스크립트는 세션 스크래치패드에
임시로 작성, 저장소에는 남기지 않음.)

**STT(raw) 단계 결과**: medium이 소요 시간 37초→134초(약 3.6배)를 대가로 명백히 더
정확했다. `그 별`→`급여`(원래 지적됐던 그 오류)를 포함해 `동실성`→`동시성`,
`TRANSECTION`→`Transaction`, `올TP`→`OLTP`, `다쳐온 분석`→`다차원 분석` 등 다수 개선.
반면 `포린키`→`Pull-in Key`, `유일성`→`유효성`, `DCL, TCL`→`DCL, DCL`(중복) 등 새 오류도
소수 발생 — net으로는 medium이 우세.

**최종 보정본까지 비교한 결과가 핵심 발견**: STT 단계의 장단점이 LLM 보정을 거치며
크게 재배열됐다.
- `유일성`→`유효성`, `그 별`→`급여`(medium만 해결)처럼 term_db 밖 일반 단어 오류는
  보정으로도 안 고쳐지거나(`유효성`) 원래부터 raw가 맞았을 때만(small의 `유일성`)
  최종본이 맞다 — 이건 예상대로.
- `포린키`(medium raw 오류)는 `Foreign Key`가 term_db에 있어서 최종본에서 정확히
  복원됨 — 파이프라인이 설계대로 작동하는 사례.
- **medium 쪽에서만 최종본에 새로운 문제가 나타났다**: (1) raw에 있던 `Final, V2`
  언급이 correction 단계에서 통째로 사라짐(내용 누락), (2) `DCL, DCL`처럼 term_db에
  없는 약어(`DCL`/`TCL` 자체가 이번 term_db에 없음)가 겹치자 LLM이 참고할 힌트가 없어
  `TCL`이 최종본에서 완전히 증발함.
- **small 쪽에서는 별개로, 원문에 없는 이름(`김가나`/`이문자`)을 LLM이 자신 있게
  지어내는 hallucination이 발견됨** — 알아듣기 힘든 부분("GIMMA, BigWare, Student ID,
  Equal")을 자연스러운 문장으로 "복원"하려다 생긴 것으로 보임.

**판단**: 발견된 문제들은 모델 크기가 아니라 `correction.py`의 보정 프롬프트가
"생략 금지"를 명시하지 않은 것과 term_db의 커버리지 공백(`DCL`/`TCL` 누락)에서 기인한다.
모델을 키우면 얻는 이득(`급여` 등)보다 속도 비용(3.6배)과 위 구조적 리스크가 더 크다고
판단해, **`model_size`는 `small`로 유지하고 correction 프롬프트만 먼저 고치기로 결정**.

## 3.6 correction 프롬프트에 "생략/hallucination 금지" 지시 추가

`llm/correction.py`의 `PROMPT_TEMPLATE`에 다음 문장을 추가했다: "원문의 내용을 임의로
생략하거나 지어내지 마세요 — 알아듣기 어려운 부분이라도 반드시 원문 그대로 유지하고,
실제 원문에 없는 단어(예: 이름, 값)를 추측해서 채워 넣지 마세요." `Final, V2` 누락과
`김가나`/`이문자` hallucination 두 사례를 동시에 겨냥한 것이다. 기존 프롬프트 테스트
(`tests/test_correction_prompt.py`, 라인 prefix/substring 기반이라 문구 추가에 영향
없음) 포함 전체 테스트 40개 통과 확인. `DCL`/`TCL` term_db 공백 보강은 이번 세션에서는
손대지 않음 — 후속 과제로 남김 (아래 7절 참고).

### 3.4 최종 판단 — 2-pass 제거

1-pass(한국어 DB 없음)와 2-pass 결과를 diff로 직접 비교했다:

- 동일 입력으로 1-pass를 두 번 실행 → 완전히 동일한 출력 (LLM 논에서 발생하는 노이즈가
  아님을 확인).
- 1-pass vs 2-pass 최종 결과 차이는 단 두 곳. 하나는 한국어 pass가 직접 고친 것("동실성"
  →"동시성")이 유지된 것이었고, 나머지 하나("컨시스턴스"→"일관성")는 한국어 DB가 직접
  건드리지 않은 단어인데도 앞부분이 달라지며 최종 LLM이 문단을 다르게 "해석"해 생긴
  부수효과였다.
- 애초 목표였던 "물결성"→"무결성"은 한국어 pass가 못 잡았지만, **최종 영어 pass의 LLM이
  문맥("데이터 인테그리티, 즉 ...")만으로 스스로 고쳐서 1-pass/2-pass 결과가 동일했다.**

즉 한국어 pass가 실제로 기여하는 부분은 극히 좁고(Okt가 우연히 통째로 뽑아낸 단어의
1글자 오타), 그마저도 최종 LLM이 자체 문맥 추론으로 상당 부분 대신 처리하고 있었다.
반면 비용(오염 버그 위험, Okt 토큰화 불일치로 인한 커버리지 누락, 2-pass로 인한 API
호출/복잡도 증가)은 뚜렷했다. **비용 대비 이득이 낮다고 판단해 기능 전체를 롤백했다.**

## 4. 롤백 내역

다음을 모두 제거하고 1-pass 파이프라인으로 되돌렸다:

- `schema.py`의 `KoreanTermDB`, `transcript_korean_pass`, `korean_term_db_used`
- `pipeline.py`의 한국어 pass 분기 로직
- `cli/run_pipeline.py`의 `--term-db-ko`, `cli/build_term_db.py`의 `--out-ko`
- `term_db/builder.py`의 `build_korean_term_db`/`build_term_dbs`/
  `save_korean_term_db`/`load_korean_term_db`
- `term_db/korean_candidates.py`(Okt 명사 추출), `term_db/korean_correction.py`
  (편집 거리 매칭) 파일 자체
- `requirements.txt`의 `konlpy`, venv에서 `konlpy`/`JPype1`/`lxml` uninstall
  (더 이상 JDK/`JAVA_HOME` 불필요)
- 관련 테스트 파일(`test_korean_builder.py`, `test_korean_candidates.py`,
  `test_korean_correction.py`) 및 `test_pipeline_orchestration.py`/`test_schema.py`의
  한국어 관련 테스트
- `data/term_dbs/english/`, `data/term_dbs/korean/` 폴더 분리(중간에 도입했던 것)도
  단일 `data/term_dbs/`로 되돌림

영어 용어 DB의 collision 분류 시스템(`term_db/collision.py`, `TermEntry.korean_variants`
등 — PDF에 실제로 나타난 영어 용어의 한글 표기를 관찰해 조사/동음이의어 충돌을 판정하는
용도)은 이번 롤백과 무관한 별개 기능이라 그대로 유지했다.

## 5. 현재 상태

`DB_test_key_set.m4a`로 최종 재검증 완료 — 1-pass 파이프라인이 정상 동작하며,
`NOT NULL`/`UNIQUE`/`PRIMARY KEY`/`FOREIGN KEY`/`UPDATE ... SET` 등 collision 대상
용어가 `transcript_corrected`에 정확히 복원됨을 확인했다. 테스트 40개 전부 통과
(`JAVA_HOME` 불필요).

## 6. 향후 한국어 오타 교정을 다시 시도한다면

이번 시도에서 얻은 교훈:

- LLM에 "자연스럽게 고쳐라"는 열린 지시를 맡기면 편집 거리와 무관하게 의미 기반으로
  재작성해버릴 위험이 있다 — 결정적 매칭이 필요하다.
- 결정적 매칭이라도, 후보 term 목록이 PDF 전체에서 빈도 필터링 없이 뽑은 일반 명사라면
  (지금 489개처럼) 짧은 단어일수록 우연한 충돌 위험이 매우 크다.
- Okt의 명사 분리 방식이 "무결성"처럼 접미사가 붙은 합성명사를 쪼개버릴 수 있어, term
  목록 자체가 목표 단어를 온전히 담지 못할 수 있다.
- 재시도한다면 (a) term 목록을 "실제 STT 오타 후보"로 별도 큐레이션하거나, (b) 최종
  영어 pass의 LLM이 이미 상당 부분 자체적으로 처리하고 있다는 점을 먼저 감안해, 정말
  최종 pass가 놓치는 케이스가 무엇인지부터 데이터로 확인하고 시작하는 것이 좋다.

## 7. 후속 과제 (미착수)

- **`DCL`/`TCL` term_db 공백**: `data/term_dbs/db_course.json`에 두 약어가 모두 없다.
  `term_db/term_candidates.py`의 acronym 추출 정규식이 왜 이 둘을 놓쳤는지 확인하고
  PDF에 실제로 등장하는지부터 검증 필요.
- **3.5절에서 발견한 medium 모델 재평가**: correction 프롬프트의 "생략 금지" 수정과
  `DCL`/`TCL` 공백을 먼저 메운 뒤에 `model_size="medium"` 여부를 다시 실측하면, 이번에
  발견된 두 구조적 리스크(내용 누락, 힌트 부재로 인한 증발) 없이 순수하게 STT 정확도
  이득만 평가할 수 있을 것이다.
- **3.5/3.6절에서 함께 드러난 hallucination 완화 효과 검증**: 이번 세션에서 추가한
  "생략/hallucination 금지" 프롬프트 문구가 실제로 `Final, V2` 누락과 `김가나`/`이문자`
  같은 사례를 막는지, 같은 오디오로 재실행해 확인 필요 (이번 세션에서는 프롬프트만
  수정하고 재검증은 하지 않음).

---

# 작업 로그 — 2026-08-17

이 세션은 두 가지 작업을 진행했다: (1) 영어 전문용어 DB 재구조화, (2) `correction.py`의
LLM 2차 보정에 "영어 원어 복원" 기능 추가. 둘 다 실제 PDF/오디오로 실측하며 진행했고,
2번은 실측 중 실제 회귀(오답)를 발견해 프롬프트를 다시 다듬었다.

## 1. 영어 전문용어 DB 재구조화 — LLM 기반 발음 생성으로 교체

### 1.1 배경

`data/term_dbs/db_course.json` 점검 결과 대다수 entry의 `korean_variants`가 비어있었다.
원인은 발음 데이터를 PDF 본문에 우연히 등장하는 "영어(한글)"/"영어-한글" 병기 패턴
(`mapping_pairs.py`)에만 의존했기 때문이며, 이 병기가 없는 대다수 용어는 방치됐다.
게다가 이 병기 추출 정규식 자체가 실제 PDF 원문에서 오탐도 냈다: `"Row-oriented: 빠른
생성과..."` → `("oriented", "빠른")`, `"...전부 안 하거나 (All or Nothing)"` →
`("All or Nothing", "하거나")`.

대소문자만 다른 중복 entry(`Key`/`KEY`, `Row`/`row`, `DROP`/`drop` 등)도 다수 발견됐다
(`builder.py`가 term 문자열 완전 일치로만 병합했기 때문).

### 1.2 결정 — 하이브리드 방식 (정규식 추출 + LLM 발음 생성)

- **용어 선정은 기존 정규식 추출 그대로 유지**: PDF 원문에서 실제로 매치된 문자열만
  담으므로 grounded하고 hallucination 위험이 구조적으로 없다. 이 부분은 손대지 않음.
- **발음 생성만 LLM(Groq)에 위임**: PDF 원문 전체가 아니라 이미 grounded된 후보 용어
  리스트(실측 143개)만 한 번에 전달 — 입력 토큰이 작고(수백 토큰 수준), term DB 빌드는
  PDF당 1회성이라 비용 부담이 거의 없다 (llama-3.3-70b-versatile 기준).
- **grounding 안전장치**: LLM 응답에서 입력 목록에 없는 키(용어)는 전부 버린다 — LLM이
  목록 밖 용어를 지어내는 것을 원천 차단 (`term_db/pronunciation.py::generate_pronunciations`).
- **부수 효과**: `mapping_pairs.py`가 파이프라인에서 완전히 빠지면서, 그 모듈이 갖고
  있던 정규식 오탐 버그 자체가 구조적으로 무관해졌다. 사용처가 없어져 모듈과 테스트를
  삭제했다.

### 1.3 대소문자 dedup

`builder.py`에 `_fold_case_variants` 추가 — `term.lower()` 기준으로 대소문자만 다른
entry를 하나로 합친다. canonical 표기는 `acronym > alphanumeric > capitalized` 우선순위로
고르고(동순위면 알파벳순, dict/set 순회 순서 비의존적 결정론 보장), `korean_variants`는
순서 보존 + 중복 제거 union. LLM 호출 **전에** fold를 실행해 중복 용어에 대해 API를
두 번 호출하지 않도록 함.

### 1.4 버그 발견 및 수정 — grounding 체크의 대소문자 오탐

재빌드 후 135개 entry 중 `DROP` 하나만 발음이 비어있는 걸 발견. 실제 LLM 응답을
재현해 원인을 추적한 결과, LLM이 `"DROP"`을 `"DROp"`(대소문자 오타)으로 응답했는데
grounding 체크가 완전 일치만 인정해서 걸러진 것으로 확인됨 — 진짜 hallucination이
아니라 억울하게 버려진 케이스였다. `generate_pronunciations`를 대소문자 무시 매칭 +
입력의 canonical 표기로 반환하도록 수정 (진짜 목록 밖 용어를 걸러내는 효과는 유지).

### 1.5 실측 검증

`data/pdfs/DB.pdf` 재빌드: 143개 후보 → fold 후 135개 entry, 134개에 발음 생성 확인
(`UNIQUE`→"유니크", `Vector`→"벡터" 등). 전체 entry의 term이 정규식 후보 집합의
부분집합임을 재확인 (LLM이 목록 밖 용어를 지어내지 않았음 — grounding 최종 검증).
재빌드할 때마다 정확히 어떤 용어 몇 개가 누락되는지는 조금씩 달라짐(예: 두 번째
재빌드에서는 `WHEN`/`Google`/`Normalization`/`DynamoDB`/`ChromaDB`/`DDL` 6개 누락) —
`temperature=0.2`인 LLM 호출의 자연스러운 변동으로 판단, 재시도 로직은 추가하지 않음
(빠진 용어는 크래시 없이 그냥 seed/fallback 분류로 넘어감).

## 2. LLM 2차 보정 — 영어 원어 복원 추가

### 2.1 동기

`correct_with_llm`이 지금까지 한글 발음 오류만 고쳤고, 영어 용어로 복원할지는 LLM
판단에 완전히 맡겨져 비결정적이었다. WORK_LOG 3.5절 사례(`포린키`→`Foreign Key`)처럼
잘 되는 경우도 있었지만, 이번 세션 실측(`DB_test_normal.m4a`)에서는 `물결성`→`무결성`
처럼 한글로만 고쳐지고 영어로 전혀 안 바뀌는 경우도 확인됐다.

### 2.2 1차 시도 — "무조건 영어로 복원하라" (실패, 실제 회귀 발견)

`correction.py`의 `PROMPT_TEMPLATE`에 "term_db_used에 있는 용어는 반드시 영어 원어
표기로 복원하라"는 지시를 추가했다. `DB_test_normal.m4a`로 재검증한 결과 두 가지
부작용이 나타남:

1. **과교정**: `raw`에서 이미 정확했던 `"데이터베이스"`→`"DataBase"`,
   `"무결성"`→`"Integrity"`처럼 손댈 필요가 전혀 없는 정상 한국어까지 강제로 영어로
   치환해버림.
2. **용어 혼동 (실제 회귀)**: `"인테리티"`(Integrity의 오발음)가 `"Atomicity"`(완전히
   다른 ACID 속성, 원자성)로 잘못 치환됨 — term_db 목록 중 엉뚱한 걸 골라버린 명백한
   오답. 직전 버전(영어 복원 지시 없던 프롬프트)에서는 이 부분이 정확했으므로 순수
   회귀로 판단.

같은 지시로 `DB_test_hard.m4a`를 테스트했을 때는 위 문제가 재현되지 않고 오히려
`레디스`→`Redis`가 정상 복원됨 — 입력에 따라 비결정적으로 나타나는 문제로 확인됨.

### 2.3 2차 시도 — 조건부 복원 지시로 완화 (최종 채택)

프롬프트에 다음 조건을 추가: "원문에 이미 올바른 한국어 표현이 쓰인 경우는 절대
영어로 바꾸지 말고 그대로 둘 것", "발음이 여러 용어와 비슷해 보여도 실제로 들린
발음과 가장 가까운 것 하나만 고르고 다른 용어로 착각해서 바꾸지 말 것".

`DB_test_normal`/`DB_test_hard` 재검증 결과 과교정과 용어 혼동이 둘 다 사라짐. 다만
`"인테리티"`→`"Integrity"` 케이스는 이제 트리거되지 않고 한글 표기 교정
(`"인티그리티"`)에 그침 — 같은 `raw`+prompt로 `correct_with_llm`을 5회 반복 호출해
5회 모두 바이트 단위로 동일한 출력임을 확인, 이건 확률적 변동이 아니라 **결정론적
동작**이다.

### 2.4 최종 판단

안전(과교정/용어혼동 방지)과 영어 복원 커버리지 사이에 트레이드오프가 있음을 확인.
**안전 쪽을 우선해 조건부 지시를 최종 채택**했다 — 일부 애매한 오발음 케이스(예:
`인테리티`)에서 영어 복원이 트리거되지 않을 수 있지만, 명백한 케이스(`레디스`→`Redis`)는
여전히 잘 동작하고 오답(용어 혼동) 위험이 없는 쪽을 선택함.

## 3. 변경 파일

- 신규: `src/sttcorrect/term_db/pronunciation.py`, `tests/test_pronunciation.py`
- 수정: `src/sttcorrect/term_db/builder.py` (`_fold_case_variants`, LLM 연동),
  `tests/test_builder.py`
- 삭제: `src/sttcorrect/term_db/mapping_pairs.py`, `tests/test_mapping_pairs.py`
- 수정: `src/sttcorrect/llm/correction.py` (영어 복원 조건부 지시),
  `tests/test_correction_prompt.py`
- 수정: `README.md` (`GROQ_API_KEY`가 term DB 빌드 단계에도 필요함을 명시)
- 재생성: `data/term_dbs/db_course.json` (새 파이프라인으로 재빌드)

테스트 47개 전부 통과 (`pytest tests/ --ignore=tests/integration`).

## 4. 후속 과제 (미착수)

- `"인테리티"`류 애매한 오발음에서 영어 복원이 더 안정적으로 트리거되도록 프롬프트를
  추가로 다듬을지는 미결정 — 이번 세션에서는 안전 우선으로 현재 상태를 확정하고 보류함.
- `pronunciation.py`의 LLM 호출이 재빌드할 때마다 몇 개 용어를 랜덤하게 누락하는 현상
  관찰됨 — 재시도 로직 없이 fallback(seed/휴리스틱 분류)에 맡기는 현재 설계를 유지할지,
  누락된 용어만 추려 재요청하는 로직을 추가할지는 검토 필요.
- 영어 복원 기능을 다른 오디오 파일(`DB_test_full`, `DB_test_key_set`, `DB_test_pro`,
  `DB_test_Row`)로도 확장 검증하지 않음 — 이번 세션은 `DB_test_normal`/`DB_test_hard`
  2개 파일만 사용.

## 5. 2차 후보정 — "정리(organize)" 단계 추가 (완전히 별도 코드)

### 5.1 배경 및 요구사항

사용자가 "2차 후보정"의 의미를 명확히 정정함: 위 2절(영어 원어 복원)과는 다른 개념으로,
오디오 전사+1차 보정 결과(`transcript_corrected`)를 입력받아 LLM이 **맥락/내용 손실
없이** 구어체를 기술 문서처럼 정리해주는 단계다. 압축 요약이 아니다 — "핵심만 추리는
느낌보다는 구술기록을 기술 기록처럼 정리한다는 느낌"이라고 명시적으로 확인받음.

요구사항: 이 단계는 오디오 전사/1차 보정과 **완전히 분리된 코드**로 만들 것 — 별도
CLI, 별도 출력 파일. `run_pipeline`에 통합하지 않음.

### 5.2 설계

- `llm/organize.py` (신규): `build_organize_prompt`/`organize_transcript` —
  `correction.py`와 동일한 패턴(순수 함수 + `LLMClient` DI, `FakeLLMClient`로 테스트).
  "요약/생략 금지" 원칙을 프롬프트에 명시 (WORK_LOG 3.6절에서 검증된 문구 스타일 재사용).
- `schema.py`에 `OrganizedTranscript`(`session_id`/`topic`/`organized_text`) 추가 —
  기존 `TranscriptionResult`는 건드리지 않고 별도 파일에 저장.
- `cli/organize_transcript.py` (신규): `--result`로 `result.json`을 입력받아
  `organize_transcript()` 호출 후 `--out`에 별도 JSON으로 저장. `pipeline.py`/
  `cli/run_pipeline.py`/`llm/correction.py`는 전혀 수정하지 않음.

### 5.3 실측 검증

`result.json`(1854자, PRIMARY KEY/SQL/DDL/DML/DCL/TRANSACTION/ACID/OLTP/OLAP/RDBMS/
NoSQL/VectorDB까지 포함하는 긴 버전)으로 end-to-end 실행. 결과 `organized_text`(1808자)를
`transcript_corrected`와 문장 단위로 대조한 결과, 기술 내용 누락이나 새로 지어낸 내용
없이 "이제"/"그러니까"/"-는데요" 같은 구어체 필러만 제거되고 주제별로 문단이 자연스럽게
나뉜 것을 확인 — 설계 의도(압축 요약이 아닌 정리)대로 동작함.

### 5.4 변경 파일

- 신규: `src/sttcorrect/llm/organize.py`, `src/sttcorrect/cli/organize_transcript.py`,
  `tests/test_organize.py`
- 수정: `src/sttcorrect/schema.py` (`OrganizedTranscript` 추가), `tests/test_schema.py`
- 변경 없음: `pipeline.py`, `cli/run_pipeline.py`, `llm/correction.py`

테스트 51개 전부 통과 (`pytest tests/ --ignore=tests/integration`).

## 6. Whisper 모델 `small/beam2` → `medium/beam5` 전환, Groq 기본 모델 교체

사용자가 별도로 진행한 자체 평가(모델 크기 × `beam_size` 4가지 조합, `jiwer` CER +
키워드 recall/F1, 정성 루브릭 설계까지 포함한 본격적인 STT 비교)를 공유받아 검토함.
상세 비교 과정과 데이터는 `STT_MODEL_COMPARISON.md`에 별도 기록 — 여기서는 요지만 남긴다.

### 6.1 발견 — Groq 기본 LLM 모델 단종

비교를 재현하려던 중 `llm/groq_client.py`의 기본 모델 `llama-3.3-70b-versatile`이
Groq API에서 완전히 제거된 걸 발견함 (`404 model_not_found`). 이 세션 초반까지는
정상 동작했으므로 최근에 내려간 것으로 보임. 접근 가능한 대체 모델을 실제로 테스트
(`openai/gpt-oss-20b`는 응답이 빈 문자열, `qwen/qwen3.6-27b`는 `<think>` 사고 과정이
그대로 `content`에 새어나옴, `allam-2-7b`는 아랍어 특화라 엉뚱한 답, `groq/compound-mini`는
동작은 하나 에이전틱 모델이라 용도가 다름) 후 `openai/gpt-oss-120b`로 확정.
`groq_client.py` 기본값 교체 완료.

### 6.2 STT 비교 재현 및 결론

`DB_test_hard.m4a` 1건으로 이 레포의 실제 파이프라인(term DB 힌트 + LLM 보정 포함,
LLM은 위에서 교체한 `gpt-oss-120b`로 통제)에 재현: `medium/beam5` raw CER 9.57% vs
`small/beam2` corrected CER 23.83% — STT 자체 품질 차이가 보정으로 메울 수 있는 수준을
넘어섬. 사용자의 원 평가 결론(`medium/beam5` 최적)과 일치해 그대로 채택.

부수 발견: `medium/beam5`처럼 raw가 이미 정확한 경우, correction 프롬프트의 "명백히
틀린 발음은 영어로 복원" 규칙이 이미 맞는 한국어 표현(`데이터메이스`→정답은
`데이터베이스`)을 영어(`Database`)로 잘못 바꿔 오히려 CER을 소폭 악화시키는 사례
확인 — 지난 세션에 추가한 "이미 맞으면 건드리지 마라" 안전장치로도 못 막은
엣지케이스. 후속 과제로 남김.

### 6.3 변경 파일

- 수정: `src/sttcorrect/llm/groq_client.py` (기본 모델 `openai/gpt-oss-120b`로 교체)
- 수정: `src/sttcorrect/stt/whisper_backend.py` (`SttConfig` 기본값
  `model_size="medium", beam_size=5`로 교체)
- 신규: `STT_MODEL_COMPARISON.md` (비교 데이터/방법/실제 전사 텍스트 전문 기록)

테스트 51개 전부 통과.

## 7. `EVAL_REPORT_full_hard.md`에서 드러난 term_db 추출 결함 3건 수정

`DB_test_full`/`DB_test_hard` 평가 중 `PRIMARY KEY`/`FOREIGN KEY`가 "PRIMARY 키"처럼
절반만 영어로 복원되고, `DCL`/`TCL`이 여전히 안 잡히는 걸 발견해 term_db 빌드
단계(`term_candidates.py`/`builder.py`) 자체를 고쳤다.

### 7.1 (근본 원인, 신규 발견) 정규식 단어 경계 버그

`config/seed_collision_terms.yaml`/기존 코드가 쓰던 `CAPITALIZED_RE`/`ACRONYM_RE`는
끝을 `\b`로 막았는데, 파이썬 `re`는 한글 음절도 `\w`로 취급한다. 그래서 `PRIMARY키`처럼
영어 뒤에 한글 조사가 공백 없이 바로 붙으면 "Y"와 "키" 사이에 `\b` 경계가 안 생겨
매치 자체가 실패했다 — **이건 이번에 추가한 기능이 아니라 처음부터 있던 결함**이다.

실측(`data/pdfs/DB.pdf`): 이 패턴으로 한글이 바로 붙은 경우가 70건 있었고, 그중
`Rollback`/`RDB`/`Out`은 PDF 전체에서 단 한 번도 공백을 두고 등장하지 않아 지금까지
term_db에 완전히 빠져 있었다.

**수정**: 끝 경계를 `\b` 대신 `(?![A-Za-z0-9])`(그 뒤에 영문자/숫자가 더 안 옴)로
바꿔, 한글이 바로 붙어도 매치하면서 `PrimaryXyz` 같은 진짜 다른 단어는 안 잘리게 했다
(`CAPITALIZED_RE`/`ACRONYM_RE`/`ALNUM_MIXED_RE` 전부 적용).

### 7.2 복합어 추출 (`PRIMARY KEY`/`FOREIGN KEY`/`NOT NULL` 등)

기존 정규식은 공백에서 끊겨서 한 단어만 후보로 잡았다 — `PRIMARY`/`FOREIGN`/`KEY`가
term_db에 각각 따로 있었고, `KEY`가 `content_word_collision`(키=신장과 발음 충돌)이라
correction 프롬프트가 "신중히 판단"하도록 지시하는데, 이 신중함이 "PRIMARY 다음에
오는 키는 당연히 KEY"라는 명백한 문맥에서도 과하게 작동해 "PRIMARY 키"로만 절반
복원됐다.

**수정**: `COMPOUND_RE`를 추가해 인접한 단어 1~2개를 이어 붙인 구간까지 후보로 잡음
(`\b(?:[A-Z][a-zA-Z]+|[A-Z]{2,})(?:[ \t]+...){1,2}(?![A-Za-z0-9])`). PDF 원문에 실제로
인접해서 등장하는 것만 grounded하게 잡는다.

버그 하나 도중에 발견: 처음엔 `\s+`로 단어 사이를 이었더니 PDF의 줄바꿈까지 넘어가서
`"Beyond RDBMS\n6.\nExample"`처럼 서로 무관한 슬라이드 항목이 하나로 묶였다 — `[ \t]+`로
줄바꿈을 제외해 해결. 또한 `COMPOUND_RE`가 `"The KEY"`처럼 관사+실제용어까지 잡아버려서
`filter_function_words`가 단일 단어 완전 일치만 걸러내던 걸 복합어의 구성 단어 중
하나라도 FUNCTION_WORDS면 전체를 제거하도록 확장했다.

`config/seed_collision_terms.yaml`의 `known_terms`에 `Primary Key`/`Foreign Key`
curated 규칙(`content_word_collision`)도 추가해 분류를 안정화했다.

### 7.3 DCL/TCL 파생 추출

지난 세션(6절 이전)에 이미 원인만 파악해두고 구현은 미뤘던 `extract_derived_acronyms`를
실제로 붙였다 — "Data Control Language"처럼 3단어 이상 Title-Case 구에서 이니셜을
모아 약어를 합성하고(→DCL), 이미 리터럴 약어로 존재하는 건(DDL/DML) 안 건드린다.
`_TITLE_PHRASE_RE`도 같은 줄바꿈 문제가 있어 `COMPOUND_RE`와 동일하게 `[ \t]+`로 수정.

### 7.4 (부수 발견) LLM 발음 생성이 term_db 확대로 인해 통째로 깨짐

위 수정들로 term_db가 135→186개로 늘자, 재빌드 결과 **186개 전부** `korean_variants`가
비어있는 걸 발견했다. 원인 추적:

- `finish_reason: "length"` — 응답이 중간에 잘림. `usage.completion_tokens: 3072`
  중 `reasoning_tokens: 1812`(59%)를 눈에 안 보이는 사고 과정에 먼저 쓰는 걸 확인
  (`openai/gpt-oss-120b`는 추론 모델). 큰 용어 목록을 한 번에 요청하면 실제 JSON
  본문 쓸 토큰이 부족해진다.
- `reasoning_effort: "low"`로 줄여보려 했으나 **요청을 아예 거부**하는 이상 동작 확인
  (`"I'm sorry, but I can't comply with that request."`) — 채택 안 함.
- `max_tokens`를 명시적으로 8000까지 올려 단일 호출로 해결하려 했으나, 이 계정(무료
  티어로 추정 — `service tier "on_demand"`, 헤더 `x-ratelimit-limit-tokens: 8000`)의
  분당 토큰 한도(TPM) 자체가 8000이라 단일 요청으로도 초과해 413 에러.

**최종 해법**: `pronunciation.py`의 `generate_pronunciations`를 40개씩 청크로 나눠
여러 번 호출하도록 수정 (실측: 40개는 매번 완결된 JSON으로 끝남). 청크를 연속
호출하면 분당 토큰 한도(8000 TPM)를 넘어 429가 날 수 있어서, `GroqLLMClient.call_llm`에
`Retry-After` 헤더 기반(없으면 지수 백오프) 재시도 로직도 추가했다. `max_tokens`도
`GroqLLMClient` 생성자에 명시적으로 노출해 기본 4096으로 설정 — 추론 모델의 토큰
truncation을 correction/organize 등 다른 호출에서도 예방한다.

### 7.5 재검증 결과

`DB.pdf` 재빌드: 186개 전체 발음 생성 성공(청크+재시도 적용 후 0개 누락).
`DB_test_full.m4a` 재실행 — recall 91.18%→**97.06%**, F1 95.38→**98.51**.
`Primary Key`/`Foreign Key`는 정확히 복원됨. `TCL`만 여전히 안 잡히는데, 이제
원인이 바뀌었다: term_db엔 정상 등록됐지만 **raw STT 단계부터 "티씨엘"과 "디씨엘"의
발음이 비슷해 둘 다 DCL로 인식**됨 — term_db 공백이라는 구조적 문제는 해결됐고,
남은 건 순수 음향 인식의 한계라 이번 세션 범위 밖으로 남겨둔다. 상세 데이터는
`EVAL_REPORT_full_hard.md` 3절 참고.

### 7.6 변경 파일

- 수정: `src/sttcorrect/term_db/term_candidates.py` (`\b`→`(?![A-Za-z0-9])` 경계 수정,
  `COMPOUND_RE`, `extract_derived_acronyms` 추가, `filter_function_words` 복합어 대응)
- 수정: `src/sttcorrect/term_db/builder.py` (`_source_for_candidate`에 compound 판정,
  derived_acronym 주입, `_SOURCE_PRIORITY` 확장)
- 수정: `src/sttcorrect/term_db/pronunciation.py` (40개 청크 배치 처리)
- 수정: `src/sttcorrect/llm/groq_client.py` (`max_tokens` 명시, 429 재시도)
- 수정: `src/sttcorrect/schema.py` (`source` Literal에 `compound`/`derived_acronym` 추가)
- 수정: `config/seed_collision_terms.yaml` (`Primary Key`/`Foreign Key` curated 규칙)
- 수정: `tests/test_term_candidates.py`, `tests/test_builder.py`, `tests/test_pronunciation.py`
- 수정: `EVAL_REPORT_full_hard.md` (재검증 결과 반영)
- 재생성: `data/term_dbs/db_course.json` (186개, 전체 발음 생성 완료)

테스트 64개 전부 통과.

---

# 작업 로그 — 2026-08-18

## 1. Whisper STT "번역 드리프트" 현상 발견 — 원인 조사, 미해결로 기록

`result_full.json`(`DB_test_full.m4a`)의 SQL 예제 구간에서 `transcript_raw`가 한국어가
아니라 완전히 유창한 영어 산문("If you have to set several values at the same time...
SQL is a language used to build, manage, and utilize DBMS data...")으로 통째로 전사된
사례를 발견했다. `transcript_corrected`도 바이트 단위로 동일해 correction 단계가 아니라
Whisper STT 단계 자체의 문제임을 확인했다.

### 1.1 원인 조사

`faster_whisper.WhisperModel.transcribe()`의 파라미터 기본값을 `inspect.signature()`로
직접 확인: `task="transcribe"`(이미 정상), `condition_on_previous_text`(프로젝트가 이미
`False`로 명시적 오버라이드)를 빼면 `compression_ratio_threshold`/`log_prob_threshold`/
`no_speech_threshold`/`temperature` fallback list 모두 라이브러리 기본값 그대로였다 —
설정 실수는 아니었다. 결과물이 문법적으로 유창한 영어라 위 임계값 기반 재시도
안전장치에도 안 걸리는 것으로 추정된다 (Whisper 계열이 "전사"/"번역"을 함께 학습해
영어 전문용어 밀도가 높은 구간에서 스스로 번역 모드로 새는, 커뮤니티에 보고된 알려진
결함 패턴과 일치).

### 1.2 실측 — `small/beam2`, `medium/beam2`는 재현 안 됨

같은 `DB_test_full.m4a`를 `small/beam2`, `medium/beam2`로 재전사한 결과, **두 설정 모두
이 구간이 정상적으로 한국어로 전사됐다** (영어 용어만 문장에 섞인 정상 패턴). 드리프트는
기존에 저장돼 있던 `medium/beam5` 결과에서만 나타났다. `small`/`medium` 두 모델 크기
모두 안전했고 `beam_size=5`일 때만 걸렸다는 점에서, **모델 크기가 아니라 `beam_size`가
방아쇠일 가능성**을 시사한다 — 다만 세그먼트 1건짜리 관찰이라 표본이 작고, 인과관계를
확정할 근거는 아니다.

### 1.3 검토했으나 미착수로 남긴 대응 방안

- 세그먼트 단위 감지(Whisper의 VAD 세그먼트별 라틴 문자 비율 + 최소 길이로 의심 구간
  판별) + 의심 구간만 다른 파라미터로 재전사하는 방안을 설계까지 논의했으나, 오디오
  슬라이싱 인프라가 이 프로젝트에 전혀 없어(타임스탬프 기반 오디오 자르기 필요) 실제
  구현은 하지 않았다.
- STT 디코딩이 사실상 결정론적(`temperature=0.0` 우선)이라, 파라미터를 안 바꾸고
  단순 재시도만 하는 방식은 효과가 없을 것으로 판단해 배제했다.
- **후속 과제로 남김** — 실제 코드 변경 없이 원인 조사와 대응 방안 검토까지만 진행.

## 2. `correct_with_llm` 청크 분할 추가 — 추론 모델 토큰 truncation 버그 수정

### 2.1 발견 경위

1절 조사 과정에서 `DB_test_full.m4a`(4분 분량)를 `small/beam2`, `medium/beam2`로 재전사
후 `correct_with_llm`으로 재보정했더니, `small/beam2`는 `corrected`가 완전히 빈 문자열,
`medium/beam2`는 한 문단만 쓰다가 중간에 끊겼다. 7.4절에서 발음 생성에 겪었던 것과 같은
클래스의 문제로 의심하고 직접 검증했다.

### 2.2 원인 정량 확인

`small/beam2`의 raw 전사본(1828자)으로 만든 실제 correction 프롬프트를 Groq API에
직접 호출해 `usage`를 확인: `completion_tokens: 4026`(`max_tokens=4096`에 거의 근접)
중 `reasoning_tokens: 3179`(**전체 예산의 79%**)를 눈에 안 보이는 사고 과정에 먼저
쓰고, 실제 보이는 출력은 847토큰(1929자)만 남았다. 짧은 오디오(`DB_test_hard`)로
테스트할 땐 필요한 출력 길이 자체가 짧아 이 문제가 안 드러났지만, 4분 분량 전체
강의처럼 출력이 길어야 하는 경우 이 좁은 여유가 종종 넘쳐(`temperature=0.2`라 사고
과정 길이도 호출마다 변동) 응답이 잘리거나 빈 문자열로 돌아오는 것으로 확인됐다.

### 2.3 해결 — 문장 단위 청크 분할 + 빈 응답 안전장치

`correction.py`에 `pronunciation.py`(7.4절)와 같은 이유·같은 해법으로 청크 분할을
추가했다. 다만 입력이 "용어 목록"이 아니라 "긴 텍스트"라 분할 방식이 다르다:
문장 경계(`.`/`!`/`?`)에서만 나눠 600자 기준으로 청크를 묶는 `_split_into_chunks`를
추가했다(문장 하나가 600자를 넘어도 강제로 자르지 않음 — 내용 보존 우선).

추가로, 실측에서 관찰된 "특정 청크만 빈 문자열로 실패"하는 경우를 위한 안전장치를
새로 넣었다: 청크 하나의 보정 응답이 비어 있으면 그 청크는 보정 없이 **원문 그대로**
결과에 포함시킨다 — 보정 실패가 곧 내용 유실로 이어지지 않도록 했다.

### 2.4 검증

- 유닛 테스트 2개 추가(`test_correct_with_llm_splits_long_transcript_into_sentence_chunks`,
  `test_correct_with_llm_falls_back_to_original_chunk_when_response_is_empty`) — 전체
  66개 테스트 통과.
- 이전에 빈 문자열이 나왔던 실제 입력(1828자)을 수정된 코드로 다시 돌려 완결된
  보정 텍스트(1923자, 내용 누락 없음)가 나오는 것을 실제 Groq API로 재확인.

### 2.5 변경 파일

- 수정: `src/sttcorrect/llm/correction.py` (`_split_into_chunks`, 청크 단위 `correct_with_llm`)
- 수정: `tests/test_correction_prompt.py`

## 3. Groq 비추론(non-reasoning) 대체 모델 탐색 — 채택 가능한 대안 없음으로 결론

2절 문제를 모델 교체로 우회할 수 있는지 확인하기 위해 현재 Groq 무료 티어에 활성화된
모델 목록(`GET /openai/v1/models`)을 조회하고, 후보 3개를 실제 호출로 검증했다:

- `qwen/qwen3.6-27b`: 여전히 추론 모델 — `<think>...</think>` 사고 과정이 숨겨지지
  않고 응답 본문에 그대로 노출되어, 오히려 `gpt-oss` 계열보다 더 안 좋음.
- `allam-2-7b`: 사고 과정 없이 바로 답변하지만, 7B로 작아서인지 교정 대신 영어로
  번역해버리는 등 품질이 불안정.
- `groq/compound-mini`: 사고 과정 없지만 마크다운 제목/설명을 자동으로 붙여
  "교정된 텍스트만 출력"이라는 요구사항과 안 맞고, 웹검색/코드실행이 딸린 에이전틱
  모델이라 이 단순 교정 작업엔 과함.

**결론**: 예전에 쓰던 `llama-3.3-70b-versatile` 같은 깔끔한 비추론 대체재가 지금
목록엔 없다. 모델 교체 대신 2절의 청크 분할 방식을 채택.

## 4. `DB_test_hard.m4a` 3-way 재검증 (`small/beam5` / `medium/beam2` / `medium/beam5`)

2절 수정 반영 후 현재 코드 기준으로 재검증했다.

### 4.1 평가 스크립트 자체의 버그 발견 — 정답 텍스트 대소문자 오타

1차 채점에서 `medium/beam5`가 raw CER은 최고인데 corrected F1(0.9375)만 다른 두
조합(0.9677)보다 낮게 나와 원인을 nlptutti 키워드별 breakdown으로 추적했다. 원인은
평가 스크립트 자체의 정답 텍스트에 `"scale out"`을 소문자로 써놓고 키워드 목록엔
`"Scale Out"`(대문자)으로 등록해 생긴 대소문자 불일치였다 — `medium/beam5`만 이
용어를 정확히 영어로 복원했는데, 오히려 그 정확함이 대소문자 불일치로 인해 거짓
양성(false positive)으로 잘못 채점된 것이었다. 정답 텍스트 오타를 수정하고 재채점.

### 4.2 최종 결과

| 조합 | raw CER | corrected CER | raw recall | corrected recall | raw F1 | corrected F1 |
| --- | --- | --- | --- | --- | --- | --- |
| `small/beam5` | 21.48% | 13.81% | 81.25% | 93.75% | 0.8667 | 0.9375 |
| `medium/beam2` | 9.72% | 6.91% | 75.00% | 93.75% | 0.8276 | 0.9375 |
| `medium/beam5` | **8.70%** | **5.12%** | **93.75%** | **100%** | **0.9375** | **0.9697** |

`medium/beam5`가 raw·corrected, CER·recall·F1 전 지표에서 1위 — 이번 재검증에서는
6절에서 관찰됐던 "보정 후 과잉복원으로 순위가 역전되는" 현상도 재현되지 않았다.
**현재 기본값(`medium/beam5`) 유지가 맞다는 결론을 재확인.**

## 5. `config/seed_collision_terms.yaml` 대규모 확장 — 파이프라인 호환성 검증

사용자가 이 파일을 다른 과목(CS기초/Git/Web/크롤링/기초통계/EDA_FE/시각화/DL/ML/NLP/
CV/LLM/Docker/AWS/RAG/AI_Agent) PDF까지 포괄하도록 `known_terms`를 67개 항목으로 크게
확장했다. 파이프라인과 실제로 잘 맞물리는지, 성능 향상이 있는지 검증을 요청받았다.

### 5.1 구조적 호환성 — 문제 없음

`load_collision_seed()`로 정상 로드 확인, `label` 값 오타 없음(`content_word_collision`
19건/`particle_collision` 48건, 스키마 `Literal`과 전부 일치). 기존 `db_course.json`
(186개 entry)을 새 seed로 재분류해도 딱 2개(`DataBase`, `DA`)만 라벨이 바뀌고 나머지
184개는 그대로 — 회귀 없음. 전체 테스트 66개 통과.

### 5.2 중요 발견 — `known_terms`의 `korean`/`korean_variants` 필드는 실제로 안 쓰임

코드 추적 결과 `classify_term()`(`collision.py`)이 `known["label"]`만 읽고
`known["korean"]`/`known["korean_variants"]`는 완전히 무시하는 것을 확인했다.
STT 힌트(`build_stt_hints`)의 발음 데이터는 오직 `generate_pronunciations`(LLM)가
생성한 값만 쓴다 — 즉 `known_terms`에 정성 들여 적어둔 발음/근거 주석은 현재 코드에서는
사람이 읽는 문서 역할만 하고, 실제 동작에는 `label` 하나만 영향을 준다.

### 5.3 `content_word_collision`과 `safe`는 현재 완전히 동일하게 취급됨

`correction.py`의 `safe_terms = term_db_used.safe + term_db_used.content_word_collision`
(두 라벨이 같은 버킷으로 합쳐짐) + `prompt_builder.py`의 `build_stt_hints`는 애초에
`collision_label`을 아예 안 봄 — 이 두 가지를 근거로, **`content_word_collision`
라벨은 `safe`와 기능적으로 완전히 동일**하다는 걸 코드로 확인했다. 새로 추가된
`Database: {label: content_word_collision}` 항목은 이 때문에 (기존부터 반복 관찰된
"데이터베이스"→"Database" 과잉복원 이슈를 겨냥한 것이었다면) **아무 동작 변화도
일으키지 않는 no-op**이다 — 그 캐치를 받으려면 `particle_collision`으로 등록해야
correction 프롬프트가 "신중히 판단하세요" 목록(`risky_terms`)에 넣는다.

### 5.4 성능 향상 검증 결과 — 이번 테스트 데이터로는 확인 불가

- `DataBase` 라벨 변경은 5.3절 이유로 실측을 돌려도 애초에 차이가 날 수 없음(구조적으로
  no-op).
- `DA`(`particle_collision`로 변경, 실제 동작 차이 있음)는 DB 강의 오디오에서 "DA"가
  실제로 오인식/혼동되는 사례를 관찰한 적이 없어 트리거될 상황 자체가 이 오디오엔
  없는 것으로 보임.
- 나머지 63개 항목은 DB 과목이 아닌 다른 과목 대상이라, 이 프로젝트엔 해당 과목의
  오디오/PDF 테스트 데이터가 없어 성능 검증 자체가 불가능함.

**결론**: 구조적으로는 안전하게 붙지만, 지금 갖고 있는 테스트 데이터 기준으로는
유의미한 성능 향상을 확인할 수 없다. `Database`를 `particle_collision`으로 바꾸면
실제 효과가 생길 수 있는데, 이번 세션에서는 적용하지 않고 다음 후속 과제로 남긴다.

## 6. 변경 파일 요약 (이번 세션)

- 수정: `src/sttcorrect/llm/correction.py`, `tests/test_correction_prompt.py`
- 변경 없음(검증만 진행): `src/sttcorrect/stt/whisper_backend.py`,
  `config/seed_collision_terms.yaml`(사용자가 별도로 확장, 이번 세션에서 검증만 수행)

테스트 66개 전부 통과.

## 7. 후속 과제 (미착수)

- **Whisper 번역 드리프트**: 1절에서 발견한, 영어 전문용어 밀도가 높은 구간이 통째로
  영어로 전사되는 현상. `beam_size=5`가 방아쇠일 가능성이 있으나 표본 1건뿐이라
  검증 필요. 세그먼트 단위 감지+재시도 방안은 설계만 하고 미구현(오디오 슬라이싱
  인프라 부재).
- **`seed_collision_terms.yaml`의 `Database` 항목**: 라벨을 `content_word_collision`→
  `particle_collision`으로 바꾸면 correction 프롬프트에서 실제로 "신중히 판단" 캐치를
  받게 되어, 반복 관찰된 과잉복원 이슈 완화에 기여할 가능성이 있음 — 미적용 상태.
- **`known_terms`의 `korean`/`korean_variants` 데드 필드**: 앞으로 curated 발음을
  실제 STT 힌트에 반영하고 싶다면(LLM 생성 발음보다 신뢰도 높은 수동 값 우선 사용),
  `builder.py`/`collision.py`에 이 필드를 실제로 읽어 `TermEntry.korean_variants`에
  주입하는 로직을 추가해야 함 — 현재는 완전히 미사용.
- **다른 과목(Git/Web/통계/DL/ML/NLP/CV/LLM/Docker/AWS/RAG/Agent) `seed_collision_terms.yaml`
  항목 63개**: 실제 성능 검증을 하려면 해당 과목의 PDF+오디오 테스트 데이터가 필요.
