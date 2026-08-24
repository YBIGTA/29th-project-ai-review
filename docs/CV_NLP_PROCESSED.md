# Computer Vision·NLP 평가 데이터 검수 기록

두 원본 PDF의 전체 페이지를 시각·텍스트로 대조해 processed `2.1.0`, 한영 용어,
atomic Evidence와 Rubric `2.2.0`을 구성했다. 표지·목차·구분·마무리 페이지는 평가
Evidence에서 제외했다.

| 강의 | 페이지 | 용어 | Evidence unit | 상위 목표 | Claim |
| --- | ---: | ---: | ---: | ---: | ---: |
| Computer Vision | 42 | 57 | 31 | 4 | 33 |
| Natural Language Processing | 52 | 66 | 37 | 4 | 37 |

## Computer Vision

- `cv.visual_foundations`: 시각 과제와 고전 특징 추출
- `cv.cnn_representation`: CNN의 특징 학습
- `cv.downstream_tasks`: Vision Downstream Task
- `cv.transformer_foundation`: ViT와 Vision Foundation Model

CV task, filter·Harris·SIFT, CNN convolution·pooling·hierarchy, ResNet·YOLO·U-Net,
ViT·CLIP·DINO를 원자 근거에 연결했다.

### 원문 정규화

- Harris는 단순한 평균 제거·공분산 설명 대신 영상 gradient의 국소 second-moment
  matrix와 여러 방향 밝기 변화로 설명한다.
- CNN의 `translation invariance`를 모든 이동에 대한 완전 불변으로 단정하지 않고
  convolution의 equivariance와 pooling 등의 국소 강건성으로 구분한다.
- YOLO는 `region-free`라는 절대 분류보다 class와 bounding box를 직접 예측하는
  one-stage detector로 평가한다.
- ViT는 image inductive bias가 전혀 없다고 하지 않고 CNN보다 locality bias가 약한
  구조로 설명한다.

## Natural Language Processing

- `nlp.statistical_foundations`: 고전·통계 NLP와 단어 표현
- `nlp.word2vec_embeddings`: Word2Vec 단어 임베딩
- `nlp.sequence_models`: 언어 모델과 RNN 계열
- `nlp.attention_llm`: Seq2Seq·Transformer와 LLM

규칙·사전 기반 NLP, corpus·분포 가설·count representation, CBOW·Skip-gram,
RNN·LSTM·GRU, Seq2Seq·attention·Transformer와 LLM pretraining·fine-tuning을
연결했다.

### 원문 정규화

- p19의 `PKI`는 문맥과 수식상 `PMI`의 오타로 처리한다.
- TF-IDF는 단순 불용어 제거가 아니라 document frequency를 이용해 corpus 전반에
  흔한 단어의 가중치를 낮추는 방식으로 설명한다.
- Seq2Seq는 RNN과 대립하는 cell이 아니라 encoder-decoder architecture로 구분한다.
- LLM 모델을 encoder-only·decoder-only·encoder-decoder로 구분하고 특정 모델을
  모두 `sub task fine tuning` 결과로 고정하지 않는다.

## 재생성·검증

```bash
python scripts/build_curated_json.py computer_vision
python scripts/build_curated_json.py nlp
python scripts/validate_evaluation_data.py --write-schemas
python -m pytest
```

