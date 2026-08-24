# Rubric 강의 구조 및 근거 페이지 감사

> 열세 강의 PDF 537페이지를 시각 검토하고, processed JSON은 탐색 색인으로만 사용해
> 작성한 Rubric 범위 설계다. 표지·목차·구분·마무리 페이지는 평가 근거에서
> 제외하며, 실습·면접 페이지는 새로운 이론의 근거가 아니라 적용 사례로 사용한다.

## 기초통계 - 42페이지

### 1. 확률·통계 기초 (`stats.probability_foundations`)

- 확률변수와 기댓값·분산: p4
- 모집단·표본과 표본추출: p5
- 공분산·상관계수와 인과관계: p6
- 조건부확률·베이즈 정리·반복기댓값: p7

### 2. 가설검정과 불확실성 (`stats.hypothesis_uncertainty`)

- 가설검정의 논리와 절차: p9-10
- 1종·2종 오류와 trade-off: p11-13
- p-value의 정의와 오해: p14-16
- 신뢰구간의 해석과 주의점: p17-18

### 3. ANOVA와 대안 (`stats.anova_alternatives`)

- ANOVA의 목적과 F 통계량: p19-20
- 독립성·정규성·등분산성 점검: p21-23, p26
- Kruskal-Wallis와 Welch ANOVA: p24-27
- One-way·Two-way와 Tukey HSD: p28-30

### 4. 회귀분석과 진단 (`stats.regression_diagnostics`)

- 상관과 회귀의 차이 및 OLS: p32-34
- 선형회귀 가정과 잔차 진단: p35-36
- R²와 다중공선성: p37-39
- GLM과 로지스틱 회귀: p40-41

### 원문 주의사항

- p6의 “공분산이 0이면 독립”은 일반적으로 성립하지 않아 정답에서 제외한다.
- p21의 “정규성이 깨지면 F test 자체가 불가능”이라는 절대 표현은 정답에서
  제외한다.
- p15는 표본크기와 p-value의 관계를 말하지만 효과크기 자체를 직접 설명하지 않는다.
- p37은 높은 R²가 표본 밖 예측력을 보장하지 않는다고 설명하지만 인과성을 직접
  다루지 않는다.

## 크롤링 - 21페이지

### 1. 크롤링과 스크래핑 기초 (`crawl.foundations`)

- 크롤링의 필요성과 목적: p4-5
- 크롤링의 수집 흐름: p6
- 웹 스크래핑 및 크롤링과의 차이: p7-8

### 2. HTML과 웹 요청 (`crawl.html_requests`)

- HTML과 마크업 구조: p9
- 태그·속성·엘리먼트·문서 구조: p10-13
- GET·POST와 응답 코드: p14

### 3. 수집 도구와 책임 있는 크롤링 (`crawl.tools_responsibility`)

- BeautifulSoup의 역할과 한계: p16
- Selenium의 역할과 trade-off: p17
- robots.txt, 요청 간격, 법적·윤리적 주의: p18

### 원문 주의사항

- p8의 크롤링·스크래핑 구분은 강의가 “실질적으로 용어를 많이 혼용”한다고
  명시하므로 절대적인 용어 정의로 과도하게 채점하지 않는다.
- p14는 POST에 Selenium을 연결하지만 HTTP POST 자체와 브라우저 자동화는 동일한
  개념이 아니므로 “POST는 반드시 Selenium”을 정답으로 만들지 않는다.

## EDA·FE - 42페이지

### 1. EDA 과정과 데이터 이해 (`eda.workflow_types`)

- EDA·전처리·FE의 역할과 분석 프로세스: p4-6
- EDA 점검 순서: p8
- 데이터 형태와 변수 의미 확인: p9-10
- 변수 타입과 범주형 인코딩: p11-12

### 2. 데이터 품질과 클래스 불균형 (`eda.quality_imbalance`)

- 결측치 원인 확인과 처리: p13
- 이상치 탐지·처리와 데이터 누수 주의: p14-15
- 클래스 불균형의 평가 지표: p16
- 언더·오버샘플링과 불균형 학습: p17-18

### 3. 변수 관계와 전처리 (`eda.relationships_preprocessing`)

- 변수 분포·종속변수 관계와 다중공선성: p19-20
- 스케일링 필요성과 모델별 민감도: p21
- Standard·Min-Max·Robust Scaling: p22
- 병합과 그룹화: p23

### 4. 특성공학과 누수 방지 (`eda.feature_engineering`)

- 특성 선택과 특성 추출: p25-29
- 파생변수 생성: p30
- Data Leakage와 시점·fold 분리: p31
- PCA 및 텍스트·이미지 전처리: p32-33

### 적용 사례

- 고객 이탈 EDA·FE: p36-39
- Train-Test contamination: p40
- 클래스 불균형 평가: p41

### 원문 주의사항

- p22는 Min-Max Scaling이 이상치에 강건하다고 적지만 일반적으로 이상치에
  민감하므로 해당 표현은 정답에서 제외한다.
- p21의 “로지스틱 회귀에서는 성능의 변화 없음”은 규제·최적화·
  수치 안정성 등 조건을 빼놓은 절대적 표현이므로 정답에서 제외한다.
- p39의 “마지막 구매 후 경과일 제거”는 이탈 정의와 같은 정보를 사용한 이 사례의
  Target Leakage 맥락에 한정한다.

## 시각화 - 39페이지

### 1. 시각화의 목적과 역할 (`viz.purpose_role`)

- 데이터 분석과 시각화의 정의: p4-5
- 시각화의 이점과 분석 과정에서의 역할: p6-8
- 분석·과학·엔지니어링에서의 활용: p9-11

### 2. 목적별 차트와 시각 표현 선택 (`viz.chart_selection`)

- 목적·데이터·독자를 고려한 설계 절차: p13-15
- 수량·분포·비율 시각화: p16-18
- 변수 관계·시계열 시각화: p19
- 지도·불확실성 시각화: p20

### 3. 색상·도구·품질 검수 (`viz.color_tools_quality`)

- 정성·순차·양방향 색상척도: p21
- Python 라이브러리와 시각화 소프트웨어: p22-23
- 시각화 체크리스트와 피드백: p24

### 4. 분석 스토리와 전달 (`viz.storytelling`)

- Plotly Figure·Trace·Layout 구조: p26
- 질문을 좁혀 가는 이커머스 분석: p27-34
- 데이터 계층과 스토리 있는 대시보드: p35
- 목적·데이터·차트·스토리의 연결과 한계: p37-38

### 원문 주의사항

- p31의 “재고 소진”과 p32의 “광고 가설 약화”는 강의 사례 안의 해석이며 모든
  비슷한 그래프에 일반화하지 않는다.
- p33은 정성 조사로 외부 원인을 확인한 사례이므로 시각화만으로 인과를 확정했다고
  채점하지 않는다.

## CS기초 - 44페이지

### 1. CS의 범위와 프로그램 실행 (`cs.scope_execution`)

- Computer Science의 범위와 핵심 축: p4-8
- 강의에서 다루는 CS 실무 범위: p9-10
- 컴퓨터 구성요소와 CPU·GPU 차이: p12-15
- 소스 코드에서 CPU 실행까지의 흐름: p16

### 2. 운영체제의 자원 관리와 보호 (`cs.os_protection`)

- 운영체제가 필요한 이유와 핵심 역할: p17-18
- CPU 스케줄링과 time slicing: p19
- 가상 메모리와 프로세스 격리: p20
- user mode·kernel mode와 system call: p21

### 3. Linux의 구조와 파일 권한 (`cs.linux_model`)

- Linux를 서버에서 사용하는 이유: p22-23
- Unix·Linux·kernel·distribution의 관계: p24-25
- Everything is a File 철학: p26
- user·group·others와 read·write·execute 권한: p27, p40-41

### 4. 가상화와 Linux 실습 (`cs.virtualization_shell`)

- VM과 container의 차이: p28-29
- WSL1·WSL2 및 Docker·WSL2 역할 구분: p30-31
- macOS와 Linux의 차이 및 재현 가능한 개발 환경: p32
- Linux 기본 명령, 경로, shell script: p35-43

### 원문 주의사항

- p5의 `Imformation`, p9의 `Shell Scirpt` 등 명백한 철자 오류는 교정한 용어를
  사용하며 별도 개념으로 취급하지 않는다.
- p31의 Docker와 WSL2 비교는 서로 완전히 대체하는 도구라는 뜻이 아니라,
  애플리케이션 격리·배포와 Linux 개발 환경이라는 주된 역할 차이를 설명한다.
- p41의 `/etc/shadow` 권한 변경은 위험성을 보여 주는 반례다. 실제 권장 절차나
  올바른 운영 방법으로 채점하지 않는다.

## Git - 32페이지

### 1. Git과 버전 관리의 기초 (`git.foundations`)

- VCS의 목적과 Local·Centralized·Distributed 방식: p4-5
- Git과 GitHub, 로컬·원격 저장소 구분: p6
- 사용자·기본 브랜치 전역 설정: p7-8
- Working Directory·Staging·Local·Remote 흐름: p9-10

### 2. 브랜치 작업과 이력 관리 (`git.workflow`)

- init·add·commit·status·remote·push·clone: p12-16
- 기능 브랜치 생성, main 갱신과 병합: p17-19
- 충돌 표시와 3-way·fast-forward merge: p20-22
- rebase·squash와 브랜치 삭제: p23-24
- restore와 revert의 차이: p25-26

### 3. Git 협업 규칙과 코드 리뷰 (`git.collaboration`)

- `.gitignore` 목적과 패턴: p28
- 기능 브랜치·Pull Request·명명 규칙: p29
- 리뷰 코멘트와 branch ruleset: p30-31

### 원문 주의사항

- p6의 `Git ≠ GitHub` 구분을 유지한다. 두 용어를 같은 제품으로 채점하지 않는다.
- p23의 `rebase`, `squash` 명령 예시에는 철자 오류가 일부 있으므로 평가 근거는
  동작 원리 중심으로 사용한다.
- `.gitignore`는 새 추적을 막는 규칙이지 이미 커밋된 비밀정보를 과거 이력에서
  자동 삭제하는 기능이 아니다.

## Python·개발환경 - 61페이지

### 1. Python 개발환경과 도구 선택 (`python.environment_tools`)

- 상황에 따른 개발환경 선택과 Colab trade-off: p4-5
- Conda·Miniconda·Anaconda 구분: p6-7
- VS Code의 기능과 Python Interpreter 선택: p8, p13-17
- Conda 기본 명령과 설치 참고: p18-20

### 2. 가상환경과 의존성 재현 (`python.virtual_environments`)

- 가상환경의 필요성과 정의: p22-23
- venv 생성·활성화·설치·requirements 재현: p24-29
- Conda 환경 생성·설치·내보내기·복제: p30-37
- venv와 Conda의 차이 및 선택: p32, p38

### 3. 읽기 좋은 Python 코드 (`python.code_quality`)

- 식별자·예약어·snake_case·CamelCase: p41-43
- PEP 8 들여쓰기: p44
- Typing의 목적과 컨테이너·Callable 예제: p45-48
- Docstring의 목적과 구성: p49-51

### 4. 클래스와 객체 지향 (`python.classes_oop`)

- 클래스·객체·속성·메서드의 역할: p52
- 클래스 속성과 인스턴스 속성: p53
- instance·class·static method 구분: p54-56
- OOP 정의, 4대 원칙과 상속·오버라이딩: p58-60

### 원문 주의사항

- p32의 Conda 설명은 장점을 강조한 비교다. Conda가 운영체제와 완전히 무관하거나
  모든 충돌을 자동으로 없앤다고 확대하지 않는다.
- p34처럼 Conda 환경에서 pip를 사용할 수 있지만 혼용 시 의존성 충돌 가능성이 있어
  Conda 패키지를 먼저 사용한다는 조건을 함께 평가한다.
- Python type hint는 기본적으로 런타임 타입을 강제하지 않는다. p45-48의 안정성
  설명을 “잘못된 타입을 실행 시 자동 차단한다”로 확대하지 않는다.
- p59의 캡슐화는 교육적 요약이다. Python의 접근 제한이 언어 수준에서 완전히
  강제된다는 뜻으로 채점하지 않는다.

## Web - 29페이지

### 1. URL과 HTTP 요청·응답 (`web.http_url`)

- 프론트엔드·백엔드와 Web 계층의 큰 그림: p2-4
- URL의 scheme·authority·path·query·fragment: p7
- HTTP 요청·응답 메시지 구조: p8
- HTTP 메서드와 상태 코드 범주: p9-10
- 브라우저·Form·JavaScript·cURL·requests·Postman 요청: p12

### 2. Web 프론트엔드 구조와 렌더링 (`web.frontend`)

- HTML 구조, CSS 표현, JavaScript 동작: p13-15
- SPA와 MPA 비교: p16
- CSR과 SSR 비교: p17
- 이벤트·서버 통신을 포함한 프론트엔드 역할: p18-19

### 3. 백엔드 API와 RESTful 설계 (`web.backend_api`)

- Response와 Endpoint 구성: p21
- Endpoint·HTTP method와 Router 연결: p22
- RESTful 자원·행위 표현과 제약: p23
- 백엔드 프레임워크와 아키텍처 패턴: p24-25
- 브라우저→서버→DB→응답 End-to-End: p26-28

### 원문 주의사항

- SPA·MPA 및 CSR·SSR은 서로 완전히 배타적인 제품 분류가 아니라 페이지 구성·렌더링
  전략이다. 모든 SPA가 한 렌더링 방식만 쓴다고 확대하지 않는다.
- p23의 REST 여섯 제약을 모두 암기했는지보다 자원은 URI, 행위는 HTTP method로
  분리하고 무상태 인터페이스를 지향한다는 핵심을 평가한다.

## 네트워크 기초 - 28페이지

### 1. 네트워크와 패킷 통신 (`network.foundations`)

- host·network device·link·message: p4
- LAN과 WAN의 범위·관리 주체: p5
- 패킷 교환과 router·switch: p6
- 네트워크 참조 모델의 계층화: p7

### 2. IP·NAT와 전송 프로토콜 (`network.ip_transport`)

- protocol, IP와 ARP의 역할: p9
- IPv4·IPv6, IP address와 port: p10
- private·public IP와 NAT: p11-12
- Port Forwarding: p13
- TCP와 UDP의 연결·신뢰성·속도 비교: p14

### 3. DNS에서 HTTP 응답까지 (`network.dns_http`)

- Domain Name과 DNS 이름 해석: p18
- TCP 위 HTTP Request·Response: p19
- DNS→IP·port→TCP→HTTP→response 흐름: p20
- 다중 IP의 load balancing·장애 대비 사례: p27

### 4. 네트워크 암호화와 HTTPS (`network.security`)

- 대칭키의 성능과 키 공유 문제: p22
- 공개키·개인키와 session key 혼합: p23
- CA 인증서와 디지털 서명: p24
- TLS와 HTTPS: p25

### 원문 주의사항

- p9의 ARP는 IP와 MAC 대응이며 DNS의 domain→IP 변환과 구분한다.
- p14의 TCP·UDP 표는 일반적인 trade-off다. UDP가 항상 애플리케이션 수준의 신뢰성을
  구현할 수 없다는 절대 명제로 확대하지 않는다.
- p24의 “개인키로 메시지를 암호화하고 공개키로 복호화” 표현은 교육적 단순화다.
  디지털 서명은 일반적으로 메시지 해시에 서명하고 공개키로 출처·무결성을 검증하는
  용도로 평가하며 기밀성 암호화와 혼동하지 않는다.

## Machine Learning - 51페이지

### 1. 유효한 문제 정의와 실험 설계 (`ml.valid_experiment`)

- 프로젝트 전체 의사결정 흐름과 문제 활용: p4-9
- Train·Validation·Test 역할과 CV: p12
- random·stratified·group·time split: p13
- 전처리 누수와 fold 내부 Pipeline: p14-16

### 2. 근거 기반 모델 선택 (`ml.model_selection`)

- 가설 기반 후보 비교와 선택 제약: p18-21
- baseline·선형·로지스틱 회귀: p22
- tree·random forest·boosting: p23-25
- XGBoost·LightGBM·CatBoost와 조건부 후보: p26-27

### 3. 모델별 전처리와 특성공학 (`ml.model_specific_pipeline`)

- 모델별 scaling·결측치·이상치 처리: p29-32
- 선형·트리 모델의 Feature Engineering 차이: p33-38
- 범주형 encoding과 target leakage: p39-41

### 4. 평가·불균형 대응과 튜닝 (`ml.evaluation_improvement`)

- 불균형 대응 순서와 training-fold sampling: p42-43
- 오류 비용 기반 metric과 fold 변동성: p45-46
- OOF prediction과 오류 분석: p47
- tuning·탐색·early stopping: p48-50

### 원문 주의사항

- 층화는 클래스 비율을 맞추지만 같은 개체 반복이나 미래 정보 누수를 해결하지 않는다.
- SMOTE를 기본 해법으로 고정하지 않고 실제 오류 비용·지표·가중치·threshold를 먼저
  검토한다.
- Early stopping과 hyperparameter tuning은 잘못된 validation 설계나 data quality를
  고치는 수단으로 평가하지 않는다.

## Deep Learning - 54페이지

### 1. 표현학습과 신경망 (`dl.representation_networks`)

- 딥러닝·representation·end-to-end 학습: p4-9
- 뉴런 계산과 신경망 계열: p10-13
- activation·ReLU와 비선형성: p14-16

### 2. 손실 함수와 학습 목표 (`dl.loss_functions`)

- Loss의 역할: p21-22
- Cross Entropy, likelihood와 NLL: p23-25
- 회귀 손실의 과제 구분: p26

### 3. 신경망 최적화 (`dl.optimization`)

- 경사하강과 backpropagation: p28-32
- learning rate와 optimizer 변형: p33-38
- vanishing·exploding gradient와 완화법: p39-40

### 4. 일반화와 MLP 이후 (`dl.generalization_architectures`)

- 일반화·과적합·regularization: p42-43
- weight decay·BatchNorm·early stopping·dropout·augmentation: p44-48
- MLP의 구조적 한계와 생성 모델 계열: p51-53

### 원문 주의사항

- p17의 hidden layer 개수는 DNN의 보편적인 절대 경계로 채점하지 않는다.
- p29의 gradient는 증가 방향이며 경사하강은 negative gradient 방향으로 이동한다.
- p45의 internal covariate shift 설명은 확정적 단일 원인으로 사용하지 않고 BatchNorm
  연산과 학습 가능한 affine transformation을 중심으로 평가한다.
- p46의 학습 종료 선택은 validation으로 수행하고 test는 최종 평가에 보존한다.

## Computer Vision - 42페이지

### 1. 시각 과제와 고전 특징 추출 (`cv.visual_foundations`)

- CV 정의, 2D·3D task와 좋은 feature: p4-7
- filter와 Harris corner detector: p9-12
- SIFT의 scale·rotation 강건 descriptor: p13
- grouping·segmentation·SVM: p14-18

### 2. CNN의 특징 학습 (`cv.cnn_representation`)

- CNN feature 학습과 전체 흐름: p20
- locality·translation 관련 inductive bias: p21
- convolution, padding·stride와 pooling: p22-23
- receptive field와 hierarchical feature: p24, p26

### 3. Vision Downstream Task (`cv.downstream_tasks`)

- ResNet residual connection: p27-28
- R-CNN 계열과 YOLO object detection: p29-30
- U-Net encoder-decoder segmentation: p31

### 4. ViT와 Vision Foundation Model (`cv.transformer_foundation`)

- patch·position embedding·CLS token과 encoder: p33-36
- CLIP image-text embedding과 zero-shot: p38-39
- DINO label-free self-distillation과 attention map: p40-41

### 원문 주의사항

- p11 Harris 설명은 gradient second-moment matrix를 기준으로 정규화한다.
- p21의 translation invariance를 모든 이동에 대한 완전 불변으로 확대하지 않는다.
- p29의 YOLO는 class와 box를 직접 예측하는 one-stage detector로 설명한다.
- p36의 ViT가 image inductive bias가 전혀 없다는 절대 표현은 사용하지 않는다.

## Natural Language Processing - 52페이지

### 1. 고전·통계 NLP와 단어 표현 (`nlp.statistical_foundations`)

- NLP 정의와 방법론 발전: p8-9
- rule·dictionary 방식과 한계: p11-14
- corpus·distributional hypothesis·cosine similarity: p15-18
- BoW·TF-IDF·co-occurrence·PMI·PPMI·sparse vector: p17-20

### 2. Word2Vec 단어 임베딩 (`nlp.word2vec_embeddings`)

- neural prediction과 dense embedding: p22
- CBOW 목표·학습·weight embedding: p23-25
- Skip-gram과 embedding 활용: p26-27

### 3. 언어 모델과 RNN 계열 (`nlp.sequence_models`)

- language model과 recurrent hidden state: p29-30
- one-to-many·many-to-one·many-to-many task: p31-33
- gradient 문제와 LSTM·GRU gate: p34-35

### 4. Seq2Seq·Transformer와 LLM (`nlp.attention_llm`)

- encoder-decoder Seq2Seq와 가변 길이 생성: p37-39
- positional encoding, QKV attention과 Transformer: p40-44
- LLM architecture, tokenizer, pretraining·fine-tuning: p46-49

### 원문 주의사항

- p19의 `PKI`는 `PMI` 오타로 교정한다.
- p17 TF-IDF는 corpus 전체 document frequency를 반영하는 방식으로 평가한다.
- p37 Seq2Seq는 RNN과 대립하는 cell이 아니라 encoder-decoder architecture다.
- p47의 모델 예시를 모두 subtask fine-tuning 결과로 고정하지 않는다.

## 공통 검수 결론

- processed의 page, chunk ID, topic은 페이지 탐색에 충분했다.
- 핵심 시각 정보는 PDF 원본을 기준으로 재확인했다.
- processed `content`는 대체로 강의 구조를 반영하지만 일부 외부 해석 또는 과도한
  일반화가 있어 평가 핵심 페이지부터 수정한다.
- Rubric의 `source_excerpt`는 processed content 복사가 아니라 PDF 원문과 시각
  정보를 확인한 검수 근거로 작성한다.
