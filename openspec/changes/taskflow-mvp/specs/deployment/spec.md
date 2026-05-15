## ADDED Requirements

### Requirement: 로컬 개발 환경
로컬에서는 FastAPI + SQLite로 개발한다. `uvicorn api.index:app --reload`로 서버를 실행하고, 프론트엔드는 정적 파일로 직접 열거나 `python -m http.server`로 서빙한다.

- 환경변수: `.env` 파일에 `DATABASE_URL=sqlite:///./taskflow.db`, `JWT_SECRET_KEY=<개발용 키>`
- DB 초기화: 앱 시작 시 `Base.metadata.create_all(bind=engine)` 자동 실행

#### Scenario: 로컬 서버 시작
- **WHEN** `uvicorn api.index:app --reload` 실행
- **THEN** FastAPI 앱이 포트 8000에서 시작되고 SQLite DB 파일이 자동 생성됨

#### Scenario: 환경변수 누락
- **WHEN** JWT_SECRET_KEY 환경변수 없이 앱 시작
- **THEN** 앱이 시작 시 오류를 발생시키고 종료됨

---

### Requirement: 운영 배포 (Vercel + Neon)
운영 환경은 Vercel(FE+BE)과 Neon PostgreSQL을 사용한다. `main` 브랜치 push 시 자동 배포된다.

- 백엔드: `api/index.py`에 FastAPI 앱 + `mangum(app)` handler
- 프론트: `frontend/` 폴더의 정적 HTML 파일
- DB: Neon Pooled Connection, `DATABASE_URL` 환경변수로 자동 주입
- 배포 후 테이블 자동 생성 (`create_all`)

#### Scenario: Vercel 배포 성공
- **WHEN** git push origin main
- **THEN** Vercel이 자동으로 빌드·배포하고 운영 URL에서 앱이 접근 가능

#### Scenario: DB 연결 전환
- **WHEN** DATABASE_URL이 `postgres://...neon.tech`로 설정됨
- **THEN** SQLAlchemy가 PostgreSQL 방언으로 자동 전환되고 로컬 코드 변경 불필요

---

### Requirement: 환경 분리
로컬과 운영이 `DATABASE_URL` 환경변수 하나로만 분리된다.

- 로컬: `DATABASE_URL=sqlite:///./taskflow.db`
- 운영: `DATABASE_URL=postgresql+psycopg2://...neon.tech/neondb?sslmode=require`
- CORS: `CORS_ORIGINS` 환경변수로 허용 도메인 명시 (로컬: `http://localhost:*`, 운영: `https://*.vercel.app`)

#### Scenario: CORS 설정
- **WHEN** Vercel 배포 URL에서 프론트엔드가 API 호출
- **THEN** CORS 허용 도메인에 포함되어 요청 성공

#### Scenario: 로컬 CORS
- **WHEN** localhost:5500에서 localhost:8000 API 호출
- **THEN** CORS 허용으로 요청 성공
