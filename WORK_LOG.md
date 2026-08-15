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
