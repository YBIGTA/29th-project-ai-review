# 백엔드 로컬 실행 요청

로그인 및 사용자 프로필 메뉴를 함께 확인하기 위해 아래 작업을 부탁드립니다.

## 요청 사항

1. 프로젝트 루트 `.env`에 로컬 PostgreSQL 연결 주소를 설정해 주세요.

```env
DATABASE_URL=로컬_PostgreSQL_접속주소
GOOGLE_CLIENT_ID=Google_Client_ID
GOOGLE_CLIENT_SECRET=Google_Client_Secret
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
AUTH_COOKIE_SECURE=false
```

2. 프로젝트 루트에서 DB 마이그레이션을 실행해 주세요.

```powershell
alembic upgrade head
```

3. 백엔드 서버를 실행해 주세요.

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

4. 아래 주소가 정상 응답하는지 확인해 주세요.

```text
http://127.0.0.1:8000/health
```

정상 응답 예시:

```json
{"status":"ok"}
```

5. 프론트에서 연결할 백엔드 주소와 실행 결과를 공유해 주세요.

- 기본 백엔드 주소: `http://localhost:8000`
- 프론트 주소: `http://localhost:3000`
- Google OAuth redirect URI: `http://localhost:3000/auth/google/callback`

> 실제 Client ID, Client Secret, DATABASE_URL 값은 이 문서나 GitHub에 기록하지 말고 개인 채널로 전달해 주세요.
