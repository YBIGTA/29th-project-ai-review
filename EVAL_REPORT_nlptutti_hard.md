# `DB_test_hard.m4a` — Whisper 4개 조합 비교 (현재 코드, `Nlptutti` 기준)

기존에 진행하신 `small/beam2`, `small/beam5`, `medium/beam2`, `medium/beam5` 4개 조합
비교와 동일한 축으로, **현재 저장소 코드**(term_db 추출 버그 3건 수정 반영 +
Groq `openai/gpt-oss-120b` 보정)로 4개 조합을 전부 다시 돌려 `Nlptutti`
(`evaluate_keywords`, `get_cer`)로 측정했다. STT 힌트(`initial_prompt`/`hotwords`)와
LLM(`gpt-oss-120b`)·term_db는 4개 조합 모두 동일하게 고정하고 **Whisper `model_size`/
`beam_size`만 변수로** 뒀다.

## 비교 표

| 조합 | raw recall | corrected recall | corrected F1 | raw CER | corrected CER | STT 소요시간 |
| --- | --- | --- | --- | --- | --- | --- |
| `small / beam2` | 68.75% | 87.50% | 0.8235 | 24.04% | 8.70% | 12.7s |
| `small / beam5` | 87.50% | **100%** | **0.9412** | 21.48% | **8.44%** | 14.8s |
| `medium / beam2` | 81.25% | 87.50% | 0.9032 | 9.72% | 9.72% | 27.2s |
| `medium / beam5` | **93.75%** | **100%** | 0.8889 | **9.21%** | 12.02% | 32.6s |

## 해석 — raw와 corrected의 순위가 다른 이유

**raw(보정 전) 단계만 보면 예상대로 `medium/beam5`가 전 지표에서 1등**이다
(recall 93.75%, CER 9.21% 둘 다 최고) — 지금까지 이 세션에서 확인해온 "medium이
STT 자체 정확도는 확실히 낫다"는 결론과 일치한다.

그런데 **corrected(보정 후) 단계에서는 `small/beam5`가 오히려 `medium/beam5`를
앞선다** (F1 0.9412 vs 0.8889, CER 8.44% vs 12.02%). 원인을 텍스트로 직접 확인한 결과:

> `medium/beam5`의 corrected 텍스트에서 `"...최적화된 데이터베이스로..."`(정답,
> 한국어 유지)가 이번엔 `"...최적화된 Database로..."`(영어)로 잘못 복원됐다.

이건 새로운 버그가 아니라 **`STT_MODEL_COMPARISON.md`에 이미 기록해 둔, 같은
"이미 맞는 한국어 표현을 영어로 과잉 복원하는" 이슈가 이번엔 `medium/beam5` 쪽
호출에서 재현된 것**이다 (LLM 호출이 `temperature=0.2`라 매번 결과가 조금씩
달라질 수 있음 — 지난번엔 이 케이스가 안 걸렸었는데 이번엔 걸렸다). 즉
**"medium이 small보다 나쁘다"가 아니라, "correction 프롬프트의 잔여 결함이 어떤
조합에 걸리느냐"가 이번 measurement 순위를 뒤집은 것**으로 해석해야 한다.

## 소요 시간

`medium` 계열은 STT만 `small`의 약 2.2배 걸린다(27~33s vs 13~15s). 이번 오디오
(`DB_test_hard.m4a`, 짧은 클립)에선 정확도 이득이 확실했던 게 이전 세션 결론이었지만,
이번 측정에서는 correction 단계의 확률적 결함 때문에 그 이득이 최종 결과물에
그대로 드러나지 않았다.

## 종합 결론

1. **STT 자체 정확도(raw 기준)는 `medium/beam5` > `small/beam5` > `medium/beam2` >
   `small/beam2` 순** — 예상/기존 결론과 일치.
2. **최종 결과물(corrected 기준)은 이번 측정에서 `small/beam5`가 가장 좋았지만**,
   이는 correction 프롬프트의 잔여 과잉복원 버그가 우연히 `medium/beam5` 쪽에
   걸린 결과이지, `medium/beam5`의 STT 품질이 실제로 더 나쁘다는 뜻이 아니다.
3. **후속 과제**: "이미 맞는 한국어 표현(특히 `데이터베이스`)을 영어로 잘못
   복원"하는 correction 프롬프트의 잔여 결함이 이번까지 2회 재현됐다 — 이 세션
   범위에서 안전장치를 한 차례 개선했음에도 완전히는 안 잡히는 것으로 보이며,
   추가로 다듬을 가치가 있어 보인다.

## 참고

- 키워드 목록: 강의 전체 범위를 포괄하는 84개 중 이 오디오 참조문에 실제로 등장하는
  16개만 `Nlptutti`가 채택 (`RDBMS`, `NoSQL`, `Column`, `Transaction`, `OLTP`,
  `Scale Out` 등).
- 4개 조합 모두 같은 STT 힌트(`data/term_dbs/db_course.json` 기반)·같은 LLM
  (`openai/gpt-oss-120b`)로 통제, Whisper 설정만 변수로 뒀다.
- 결과 원본(raw/corrected 전문)은 스크래치패드에 임시 저장, 저장소에는 남기지 않음.
