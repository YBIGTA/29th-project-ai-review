# 29th Project AI Review

강의와 상위 학습목표를 선택한 뒤 2분 동안 설명하면, Rubric의 Claim을 기준으로
평가하는 구술 복습 서비스입니다.

## 평가 흐름

```text
강의 선택 → 상위 학습목표 선택 → 120초 녹음 → STT·용어 보정
→ 선택 분기의 Claim 7~12개 로드
→ Rubric에 기록된 chunk_id로 processed 근거 직접 조회
→ LLM의 Claim별 구조화 판정
→ 코드의 60+20+20 점수 계산
```

Rubric과 processed 문서는 임베딩하지 않습니다. ChromaDB나 코사인 검색도 평가에
사용하지 않습니다. LLM은 판정만 담당하며 최종 점수는 코드가 계산합니다.

## 설치

Python 3.11 이상을 권장합니다.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

두 번째 명령은 `src/sttcorrect` 로컬 패키지를 editable 모드로 설치합니다. 이
단계까지 완료해야 테스트와 CLI에서 `sttcorrect`를 정상적으로 import할 수 있습니다.

`.env`에 필요한 API 키를 설정합니다. API 키는 커밋하지 않습니다.

```dotenv
OPENAI_API_KEY=...
LLM_MODEL=gpt-5.6-luna
```

## 핵심 데이터

- `data/*.pdf`: 원본 강의안
- `data/processed/*.json`: 페이지별 원문·시각정보·검수 요약 (기초통계는 atomic evidence·이중언어 용어 포함)
- `data/evaluation/rubrics/*.json`: 강의별 Rubric
- `data/evaluation/gold/*_assessment.json`: 사람이 검수한 Gold 판정 예시
- `data/evaluation/gold/*_score.json`: 코드로 재현하는 Gold 점수 예시
- `data/term_dbs/*.json`: STT 전문용어 보정 데이터

## 핵심 코드

- `src/evaluation_schemas.py`: Rubric과 LLM 판정 스키마
- `src/evaluation.py`: 선택 분기·근거 조회·검증·점수 계산
- `src/evaluation_prompt.py`: Claim 평가 프롬프트
- `src/evaluation_api.py`: OpenAI 구조화 응답 호출
- `src/transcript.py`: STT 발화문 의미 구간 분리
- `backend/app/integrations.py`: STT 결과와 Rubric 평가 연결
- `frontend/fe/components/ReviewApp.tsx`: 강의·상위목표 선택 및 결과 화면

## 데이터 검증

Rubric 구조, Claim 개수, Evidence chunk·페이지·source excerpt 연결을 확인합니다.

```bash
python scripts/validate_evaluation_data.py
```

JSON Schema도 다시 출력하려면 다음과 같이 실행합니다.

```bash
python scripts/validate_evaluation_data.py --write-schemas
```

## 테스트

```bash
python -m pytest -q
```

프론트엔드는 별도로 검사합니다.

```bash
cd frontend/fe
npm run lint
npm run build
```

## 실행

백엔드:

```bash
uvicorn backend.app.main:app --reload
```

프론트엔드:

```bash
cd frontend/fe
npm run dev
```

## 평가 점수

- Essential Claim 이해도: 60점
- Supporting Claim 설명: 20점
- 하위 학습목표 충족도: 20점

판정값은 `correct`, `mostly_correct`, `partial`, `incorrect`,
`not_addressed` 다섯 단계입니다. 선택하지 않은 상위 학습목표는 불러오거나
채점하지 않습니다.

자세한 기준은 `docs/2MIN_TOPIC_RUBRIC_SPEC.md`를 참고하세요.
