# AWS / Docker 사전 세팅

이 문서는 RAG 내부 구현이 바뀌기 전에 백엔드 배포 껍데기를 미리 준비하기 위한 절차입니다.

## 로컬 Docker 확인

1. 환경변수 파일을 만듭니다.

```bash
cp .env.docker.example .env.docker
```

2. `.env.docker`에 실제 키를 채웁니다. `OPENAI_API_KEY`, `GROQ_API_KEY`, Google OAuth 값은 GitHub에 올리지 않습니다.

3. 컨테이너를 실행합니다.

```bash
docker compose up --build
```

4. 헬스체크를 확인합니다.

```bash
curl http://localhost:8000/health
```

성공 기준은 `{"status":"ok"}` 응답입니다.

## AWS EC2 준비

권장 최소 구성:

- Ubuntu 22.04 또는 24.04 EC2
- Docker Engine과 Docker Compose plugin 설치
- 보안 그룹 inbound: `22`는 본인 IP만, `8000`은 테스트용으로만 허용
- 운영 시에는 `8000` 직접 공개 대신 Nginx 또는 ALB 뒤에 둡니다.
- EBS 용량은 Whisper 모델, Docker image, vector DB를 고려해 최소 30GB 이상 권장

EC2에서 실행 순서:

```bash
git clone <repo-url>
cd 29th-project-ai-review
cp .env.docker.example .env.docker
vi .env.docker
docker compose up -d --build
docker compose logs -f api
curl http://localhost:8000/health
```

## 배포 시 확인할 것

- `alembic upgrade head`가 API 컨테이너 시작 로그에서 성공하는지 확인합니다.
- `backend_data`, `postgres_data` Docker volume이 생성되는지 확인합니다.
- `vector_db`는 저장소의 `./vector_db` 디렉터리를 컨테이너의 `/app/vector_db`에 연결합니다.
- 팀원이 RAG 코드를 바꾼 뒤에는 이미지를 다시 빌드합니다.

```bash
docker compose up -d --build api
docker compose logs -f api
```

## 나중에 바뀔 가능성이 높은 부분

- RAG가 Chroma 로컬 파일 대신 외부 Vector DB를 쓰면 `vector_db` volume과 `VECTOR_DB_PATH` 설정은 제거하거나 바뀔 수 있습니다.
- GPU EC2를 쓰면 Dockerfile의 Whisper 실행 환경을 CUDA 기반 이미지로 바꿔야 합니다.
- 프론트 배포 주소가 정해지면 `ALLOWED_ORIGINS`에 실제 도메인을 추가해야 합니다.
