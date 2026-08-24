# Machine Learning·Deep Learning 평가 데이터 검수 기록

두 원본 PDF의 모든 페이지를 확인해 processed `2.1.0`, 용어 사전, atomic Evidence와
Rubric `2.2.0`을 작성했다. 표지·목차·구분·마무리 페이지는 검색용 설명만 유지하고
평가 Evidence에서는 제외했다.

| 강의 | 페이지 | 용어 | Evidence unit | 상위 목표 | Claim |
| --- | ---: | ---: | ---: | ---: | ---: |
| Machine Learning | 51 | 46 | 28 | 4 | 30 |
| Deep Learning | 54 | 59 | 33 | 4 | 36 |

## Machine Learning

- `ml.valid_experiment`: 유효한 문제 정의와 실험 설계 — 7 Claim
- `ml.model_selection`: 근거 기반 모델 선택 — 8 Claim
- `ml.model_specific_pipeline`: 모델별 전처리와 특성공학 — 8 Claim
- `ml.evaluation_improvement`: 평가·불균형 대응과 튜닝 — 7 Claim

PDF의 문제 정의, split·leakage·fold Pipeline, 모델 선택 기준, 모델별 전처리와
Feature Engineering, 불균형 대응, metric·OOF·tuning·early stopping을 원자 단위로
연결했다. 특정 모델이 언제나 최고라는 식으로 고정하지 않고 데이터 구조와 운영
제약에 근거한 선택을 평가한다.

## Deep Learning

- `dl.representation_networks`: 표현학습과 신경망 — 9 Claim
- `dl.loss_functions`: 손실 함수와 학습 목표 — 7 Claim
- `dl.optimization`: 신경망 최적화 — 10 Claim
- `dl.generalization_architectures`: 일반화와 MLP 이후 — 10 Claim

표현 학습·비선형성, 분류와 회귀 손실, 경사하강·역전파·optimizer, gradient 문제,
일반화 기법과 MLP 이후 아키텍처를 연결했다. 그림 위주인 회귀 손실·Dropout·Data
Augmentation 페이지는 `source_type=visual`로 표시해 텍스트에 없는 세부 공식을
추가하지 않았다.

### 원문 정규화 정책

- p17의 “hidden layer 2개 이상”은 보편적 DNN 경계가 아니라 강의 내 관습으로 보고
  핵심 Claim에서 제외했다.
- p29의 gradient 방향 문구는 수학적으로 gradient가 증가 방향이고 negative gradient가
  하강 방향임을 명확히 했다.
- p45 BatchNorm은 internal covariate shift를 단일한 확정 원인으로 채점하지 않고,
  mini-batch 통계 정규화와 학습 가능한 scale·shift 역할을 기준으로 삼았다.
- p46 early stopping은 validation으로 종료 시점을 정하고 test는 최종 평가에 보존하도록
  명확히 했다.

## 재생성·검증

```bash
python scripts/build_curated_json.py machine_learning
python scripts/build_curated_json.py deep_learning
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest
```

