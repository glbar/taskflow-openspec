## Context

TaskFlow MVP는 FastAPI(Python) 백엔드와 Vanilla JS + Tailwind CSS 프론트엔드로 구성된 풀스택 웹 앱이다. 로컬 개발에는 SQLite, 운영 배포에는 Vercel + Neon PostgreSQL을 사용한다. 코드베이스가 비어 있으며 이번 변경이 초기 구현이다.

## Goals / Non-Goals

**Goals:**
- Auth·팀·칸반·채팅·배포 5개 기능을 Day 2 안에 동작하는 상태로 완성
- 로컬 개발 → Vercel 운영 배포까지 단일 코드베이스로 처리
- 스펙 문서(프로그램정의 + 스토리보드)에 정의된 18개 API를 그대로 구현

**Non-Goals:**
- WebSocket 실시간 메시지, 이메일 인증, 파일 첨부, 전문 검색
- pytest/jest 자동화 테스트, Sentry 로그 수집
- JWT refresh token, 다중 팀 소속

## Decisions

### 1. 프론트엔드 구조: MPA (Multi-Page Application)

각 화면마다 독립 HTML 파일을 생성한다(`login.html`, `team.html`, `kanban.html`, `chat.html`).

**이유**: Vanilla JS 기반에서 SPA 라우터를 직접 구현하면 복잡도가 불필요하게 증가한다. MPA는 화면 전환이 페이지 이동이므로 학습 비용이 없다.

**대안**: index.html + JS 해시 라우팅 — 거부 이유: Vanilla JS에서 히스토리 API 관리가 번거롭고 Vercel 배포 시 리라이트 설정이 추가로 필요하다.

### 2. Tailwind CSS: CDN

`<script src="https://cdn.tailwindcss.com">` 한 줄로 사용한다.

**이유**: npm 빌드 과정 없이 즉시 사용 가능. Day 2 범위에서 빌드 파이프라인은 불필요하다.

**대안**: npm + PostCSS 빌드 — 거부 이유: 파일 크기 최적화가 MVP에서 우선순위가 아니다.

### 3. 백엔드 ORM: SQLAlchemy (동기)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
```

**이유**: FastAPI와 함께 async SQLAlchemy를 쓰면 설정이 복잡해진다(async session, await 체이닝). 동기 방식은 단순하며 SQLite↔Neon 전환도 `DATABASE_URL` 변경만으로 처리된다.

**대안**: async SQLAlchemy — 거부 이유: 학습 단계에서 async DB 패턴 추가는 오버엔지니어링.

### 4. JWT: python-jose + passlib[bcrypt]

```
python-jose[cryptography]  # JWT 발급·검증
passlib[bcrypt]            # 비밀번호 해시
```

**이유**: FastAPI 공식 문서에서 권장하는 조합. 두 라이브러리가 FastAPI 튜토리얼에 표준으로 등장해 참고 자료가 풍부하다.

### 5. Vercel Python 배포: mangum + api/ 폴더 구조

```
api/
  index.py      ← FastAPI app + mangum(app) handler
frontend/
  *.html
vercel.json     ← 라우팅: /api/* → api/index.py, /* → frontend/
requirements.txt
```

**이유**: Vercel Python Serverless Runtime은 WSGI/ASGI 앱을 `mangum`으로 래핑하여 Lambda 핸들러로 변환한다. 로컬은 `uvicorn api.index:app --reload`로 동일 앱을 실행한다.

### 6. 채팅 폴링 `since` 파라미터: ISO 타임스탬프 (URL 인코딩)

`GET /teams/{id}/messages?since=2026-05-13T14%3A27%3A00Z`

클라이언트에서 `encodeURIComponent(lastMessage.created_at)`으로 인코딩하여 전송한다. 서버는 `created_at > since` 조건으로 필터링한다.

**대안**: 메시지 ID 기반 — 검토했으나 스토리보드 명세(E.01)가 타임스탬프 기준으로 정의되어 있어 그대로 따른다.

### 7. DB 마이그레이션: SQLAlchemy `create_all` (앱 시작 시)

```python
Base.metadata.create_all(bind=engine)
```

**이유**: MVP 단계에서 Alembic 마이그레이션 스크립트 관리는 과도하다. 앱 시작 시 테이블이 없으면 생성한다.

**주의**: 운영 Neon에 처음 배포 시 테이블이 자동 생성된다. 스키마 변경 시 테이블 DROP 후 재생성 필요(데이터 손실).

## Risks / Trade-offs

| 리스크 | 완화 방법 |
|--------|---------|
| Vercel Python cold start (~1–3s) | 첫 요청 지연은 MVP에서 허용. 향후 Pro 플랜 warm-up 검토 |
| SQLite INTEGER vs PostgreSQL SERIAL 차이 | SQLAlchemy `Integer` + autoincrement=True로 양쪽 호환 |
| JWT localStorage 저장 (XSS 취약) | MVP 전제: 신뢰 환경(Chrome/Safari 최신). httpOnly cookie는 범위 외 |
| 1인 1팀 제약으로 팀 재합류 불가 | `DELETE /teams/{id}/leave` API 존재하나 UI 없음. 스토리보드 결정 #1 준수 |
| 타임스탬프 기반 폴링 중복/누락 | `since` 이후 메시지만 반환. 동시 메시지는 같은 초에 2건 발생 시 누락 가능 → 허용(MVP) |

## Migration Plan

1. 로컬 개발: `pip install -r requirements.txt` → `uvicorn api.index:app --reload`
2. Vercel 배포:
   - `vercel link` → 프로젝트 연결
   - Neon DB 생성 → `DATABASE_URL` 환경변수 설정
   - `vercel --prod` → 배포
3. 롤백: 이전 Vercel 배포로 즉시 롤백 가능 (Vercel 대시보드)

## Open Questions

- Tailwind CDN은 개발용으로 적합하나 운영에서 `console.warn`이 발생할 수 있음 — 무시 처리
- Neon free tier connection pool 제한(10개) — 동시 5명/팀 기준 충분
