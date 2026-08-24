# 기여 가이드 (Contributing Guide)

## 1. 브랜치 전략 (Branch Strategy)

```
main  ───────────────────────────────────────────● [8/16 중간 Freeze] ───● [8/24 최종 Freeze]
       \                                        /                            /
dev     ●────●─────────●─────────●─────────────●────────────────────────────●
         \    \         \         \
feat/     ●───●(FE)      ●─────────●(STT)
```

### **`main` (Production / Presentation)**
- 시연 및 발표용으로 검증된 최종 코드만 관리
- **절대 직접 `push` 금지!**
- Code Freeze 시점(8/16, 8/24)에 `dev` 브랜치에서 PR을 통해 merge

### **`dev` (Integration / Staging) — Default Branch**
- 각 파트의 작업물을 모으는 **통합 테스트 브랜치**
- 모든 기능 개발 완료 후 `dev` 브랜치를 타겟으로 PR 생성
- 항상 안정적인 상태 유지

### **`feat/{파트}-{기능명}` (Working Branch)**
- 팀원 각자가 개별 기능을 개발하는 **작업 전용 브랜치**
- 항상 `dev` 브랜치에서 분기(`checkout`)하여 생성

---

## 2. 파트별 브랜치 네이밍 규칙

`feat/{파트}-{작업내용}` 형식으로 작성

### 예시

**Frontend**
- UI 레이아웃, 웹캠/마이크 녹음 및 힌트 모달 컴포넌트
  - `feat/fe-ui-components`
  - `feat/fe-webcam-recorder`

**STT & Audio**
- Faster-Whisper 로컬 파이프라인, 기술 용어 보정
  - `feat/stt-faster-whisper`
  - `feat/stt-prompt-tuning`

**Rubric & LLM**
- PDF Evidence 검수, Rubric, LLM 평가 프롬프트
  - `feat/rubric-evidence`
  - `feat/rag-eval-prompt`

**BE & PM**
- FastAPI 세팅, Mock API, AI 파이프라인 연결 Glue Code
  - `feat/be-mock-api`
  - `feat/be-pipeline-glue`

---

## 3. Commit 메시지 컨벤션

- `feat` : 새로운 기능 추가
- `fix` : 버그 수정
- `docs` : 문서 수정 (README, 주석, API Spec 등)
- `style` : 코드 포맷팅, 세미콜론 누락 등 (코드 로직 변경 없음)
- `refactor` : 코드 리팩토링 (기능 추가나 버그 수정이 아닌 구조 개선)
- `chore` : 빌드 업무 수정, 패키지 매니저 설정, `.gitignore` 수정 등

### 예시

```bash
git commit -m "feat: Faster-Whisper initial_prompt 용어 보정 추가"
git commit -m "fix: 오디오 바이너리 WAV 변환 인코딩 버그 수정"
git commit -m "docs: API Spec JSON 규격 업데이트"
git commit -m "chore: .gitignore에 오디오 테스트 파일 제외 경로 추가"
```

---

## 4. 작업 흐름 (Workflow)

### Step 1: 작업 시작 전에 미리 브랜치 생성

```bash
# 최신 dev 브랜치 상태 반영
git checkout dev
git pull origin dev

# 본인 파트의 작업 브랜치 생성 및 이동
git checkout -b feat/be-mock-api
```

### Step 2: 작업 진행 중에는

```bash
git add .
git commit -m "feat: mock api 추가 완료"
git push origin feat/be-mock-api
```

일반적으로 여러 번의 커밋을 만들어 진행상황을 기록합니다.

### Step 3: 작업 완료 후에는

1. **GitHub에서 PR 생성**
   - `base: dev` ← `compare: feat/{본인 브랜치}` 설정 확인
   - PR 제목: 작업 내용 한 문장 요약
   - PR 설명: 작업 내용 3줄 요약 작성

2. **예시 PR**
   ```
   Title: feat: FE 프로토타입 - Next.js 앱 및 녹음 UI 구현
   
   Description:
   - Next.js 16 + TypeScript + Tailwind 기반 앱 초기화
   - 주제 선택, 카메라/마이크 권한 처리
   - 음성 녹음 3초 카운트다운, 평가 결과 UI
   ```

3. **팀이 함께 리뷰 및 파이프라인 확인 후 `dev`로 머지**
   - 코드 리뷰: 팀원이 검토하고 댓글로 피드백
   - CI/CD 확인: 테스트가 통과하는지 확인
   - Merge: 조건이 만족되면 머지 버튼 클릭

---

## 5. Code Freeze 일정

### 8/16 (금) — 중간 발표 Code Freeze
- `dev` 브랜치의 상태를 `main` 브랜치로 merge
- 중간 발표에 최종 검증된 코드 배포

### 8/24 (토) — 최종 발표 Code Freeze
- 최종 기능이 모두 완성된 후 `main`으로 merge
- 최종 발표 및 시연용 버전

---

## 6. 주의사항

1. **`dev`와 `main`에는 직접 push 금지**
   - 항상 `feat/` 브랜치에서 작업 후 PR을 통해 merge

2. **PR 생성 전에 최신 `dev` 상태 반영**
   ```bash
   git fetch origin
   git rebase origin/dev
   git push -f origin feat/your-branch
   ```

3. **커밋 메시지는 명확하고 간결하게**
   - 팀이 히스토리를 이해하기 쉽도록

4. **Code Freeze 기간에는 `main`으로의 merge 만 진행**
   - 긴급 버그 수정은 별도 PR로 빠르게 처리

---

## 7. 도움이 필요할 때

- 브랜치 전략 관련 질문: README 또는 팀 리더에게 문의
- 머지 컨플릭트: 팀과 함께 해결
- 실수로 `main`에 push했다면: 즉시 팀에 보고
