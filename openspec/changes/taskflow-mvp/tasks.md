## 1. 프로젝트 초기 설정

- [ ] 1.1 디렉토리 구조 생성: `api/`, `frontend/`, `openspec/` 폴더
- [ ] 1.2 `requirements.txt` 작성 (fastapi, uvicorn, sqlalchemy, python-jose[cryptography], passlib[bcrypt], mangum, psycopg2-binary, python-dotenv)
- [ ] 1.3 `.env` 파일 생성 (DATABASE_URL, JWT_SECRET_KEY, CORS_ORIGINS)
- [ ] 1.4 `.gitignore` 작성 (.env, *.db, __pycache__, .vercel)
- [ ] 1.5 `vercel.json` 작성 (라우팅: /api/* → api/index.py, /* → frontend/)

## 2. DB 모델

- [ ] 2.1 `api/database.py` — SQLAlchemy engine, Session, Base 설정 (DATABASE_URL 환경변수 읽기)
- [ ] 2.2 `api/models.py` — User 모델 (id, email, password_hash, team_id FK, created_at)
- [ ] 2.3 `api/models.py` — Team 모델 (id, name, invite_code UNIQUE, owner_id FK, created_at)
- [ ] 2.4 `api/models.py` — Task 모델 (id, team_id FK, title, status, creator_id FK, assignee_id FK nullable, created_at)
- [ ] 2.5 `api/models.py` — Message 모델 (id, team_id FK, user_id FK, content, created_at)
- [ ] 2.6 인덱스 추가: tasks(team_id, created_at), messages(team_id, created_at), teams(invite_code)
- [ ] 2.7 `api/index.py` — FastAPI 앱 생성, startup 이벤트에서 `create_all` 실행, mangum 핸들러 등록

## 3. 공통 유틸리티

- [ ] 3.1 `api/auth.py` — JWT 발급 함수 (create_access_token, 만료 24h)
- [ ] 3.2 `api/auth.py` — JWT 검증 의존성 (get_current_user: Authorization 헤더 파싱, 401 반환)
- [ ] 3.3 `api/auth.py` — 팀 멤버십 검증 의존성 (get_current_team_member: team_id 확인, 403 반환)
- [ ] 3.4 `api/schemas.py` — Pydantic 스키마 (UserCreate, UserLogin, TeamCreate, TaskCreate, TaskStatusUpdate, MessageCreate 등)
- [ ] 3.5 `api/index.py` — 에러 응답 표준화: `{ error: { code, message } }` 형태의 HTTPException handler
- [ ] 3.6 `api/index.py` — CORS 미들웨어 설정 (CORS_ORIGINS 환경변수)

## 4. 인증 API

- [ ] 4.1 `POST /auth/signup` — 이메일 형식·중복 검증, bcrypt 해시, users INSERT, JWT 반환 (201)
- [ ] 4.2 `POST /auth/login` — bcrypt 검증, JWT 반환, user.team_id 포함 (200)
- [ ] 4.3 `POST /auth/logout` — 200 반환 (stateless)
- [ ] 4.4 `GET /auth/me` — JWT에서 현재 사용자 정보 반환

## 5. 팀 API

- [ ] 5.1 `POST /teams` — 팀명 검증, invite_code 생성 (`[A-Z]{4}-[0-9]{4}`), teams INSERT, users.team_id UPDATE (201)
- [ ] 5.2 `POST /teams/join` — invite_code 형식·존재 검증, 이미 소속 409 처리, users.team_id UPDATE (200)
- [ ] 5.3 `GET /teams/{id}` — 팀 정보 반환 (멤버만 접근, 비멤버 403)
- [ ] 5.4 `GET /teams/{id}/members` — 멤버 목록 반환 (is_owner 포함)
- [ ] 5.5 `DELETE /teams/{id}/leave` — users.team_id = null UPDATE (200)

## 6. 칸반 API

- [ ] 6.1 `GET /teams/{id}/tasks` — 태스크 목록 반환 (filter=me/unassigned, created_at DESC 정렬)
- [ ] 6.2 `POST /teams/{id}/tasks` — 태스크 생성 (title 검증, assignee_id nullable, status=TODO, 201)
- [ ] 6.3 `GET /tasks/{id}` — 태스크 단일 조회
- [ ] 6.4 `PUT /tasks/{id}` — title·assignee_id 수정
- [ ] 6.5 `PATCH /tasks/{id}/status` — status 변경 (TODO/DOING/DONE 검증)
- [ ] 6.6 `DELETE /tasks/{id}` — creator 또는 team owner만 삭제 가능 (그 외 403)

## 7. 채팅 API

- [ ] 7.1 `GET /teams/{id}/messages` — since 파라미터 지원 (없으면 최근 50개, 있으면 증분), created_at ASC
- [ ] 7.2 `POST /teams/{id}/messages` — content 길이 검증 (1–1000자), messages INSERT (201)
- [ ] 7.3 `DELETE /messages/{id}` — 본인 메시지만 삭제 (그 외 403 NOT_OWNER)

## 8. 프론트엔드 공통

- [ ] 8.1 `frontend/common.js` — fetch 래퍼 (Authorization 헤더 자동 첨부, 401 catch → /login redirect)
- [ ] 8.2 `frontend/common.js` — localStorage JWT 관리 함수 (getToken, setToken, removeToken)
- [ ] 8.3 `frontend/common.js` — 에러 토스트 표시 함수
- [ ] 8.4 `frontend/common.js` — 페이지 진입 시 토큰 없으면 /login redirect 함수

## 9. 로그인·회원가입 화면

- [ ] 9.1 `frontend/login.html` — 로그인 폼 (이메일, 비밀번호, 로그인 버튼, 회원가입 링크), Tailwind 스타일
- [ ] 9.2 `frontend/login.html` — POST /auth/login 연동, 성공 시 team_id 기반 화면 분기
- [ ] 9.3 `frontend/signup.html` — 회원가입 폼 (이메일, 비밀번호 8자+), Tailwind 스타일
- [ ] 9.4 `frontend/signup.html` — POST /auth/signup 연동, 클라이언트 validation, 에러 메시지 표시

## 10. 팀 선택 화면

- [ ] 10.1 `frontend/team.html` — 팀 만들기 폼 + 초대코드 합류 폼, Tailwind 스타일
- [ ] 10.2 `frontend/team.html` — POST /teams 연동, 성공 시 초대코드 표시 모달
- [ ] 10.3 `frontend/team.html` — POST /teams/join 연동, invite_code 형식 클라이언트 검증, 에러 처리

## 11. 칸반 화면

- [ ] 11.1 `frontend/kanban.html` — 3컬럼(TODO/DOING/DONE) 레이아웃, 헤더(팀명·탭·로그아웃), Tailwind 스타일
- [ ] 11.2 `frontend/kanban.html` — GET /teams/{id}/tasks 연동, 카드 렌더링 (제목, #id, @assignee)
- [ ] 11.3 `frontend/kanban.html` — 필터 버튼(전체/@me/미할당) 구현
- [ ] 11.4 `frontend/kanban.html` — + 버튼 클릭 시 인라인 입력 폼, Enter → POST /tasks, Esc → 취소
- [ ] 11.5 `frontend/kanban.html` — HTML5 drag & drop: dragstart, dragover, drop → PATCH /tasks/{id}/status
- [ ] 11.6 `frontend/kanban.html` — 카드 클릭 시 모달(상태 변경·제목 수정·담당자 변경·삭제), PUT/PATCH/DELETE 연동
- [ ] 11.7 `frontend/kanban.html` — empty state 표시 (카드 0개일 때)

## 12. 채팅 화면

- [ ] 12.1 `frontend/chat.html` — 메시지 목록(말풍선), 입력창(1000자 카운터), Tailwind 스타일
- [ ] 12.2 `frontend/chat.html` — GET /teams/{id}/messages 첫 로드 (최근 50개)
- [ ] 12.3 `frontend/chat.html` — setInterval 5초 폴링 (since= 파라미터, 새 메시지만 append)
- [ ] 12.4 `frontend/chat.html` — POST /teams/{id}/messages 연동, Enter 전송, 1000자 초과 시 버튼 disable
- [ ] 12.5 `frontend/chat.html` — 본인 메시지 호버 시 🗑 아이콘, DELETE /messages/{id} 연동
- [ ] 12.6 `frontend/chat.html` — empty state, 폴링 실패 시 연결 끊김 표시 + exponential backoff 재시도

## 13. 반응형 UI (모바일)

- [ ] 13.1 칸반: `md:` breakpoint 기준 3컬럼(PC) / 탭 스와이프(모바일) 전환
- [ ] 13.2 모바일 칸반: 카드 길게 누르기 → 상태 변경 메뉴(드래그 대체)
- [ ] 13.3 모바일 채팅: visualViewport API로 키보드 올라올 때 메시지 영역 축소
- [ ] 13.4 모바일 헤더: 햄버거 메뉴(☰) → 슬라이드 패널(칸반/채팅/멤버/로그아웃)

## 14. 팀 멤버 화면

- [ ] 14.1 `frontend/members.html` (또는 사이드 패널) — GET /teams/{id}/members 연동, owner(★) 구분 표시

## 15. Vercel 배포

- [ ] 15.1 GitHub 저장소 생성 및 초기 push
- [ ] 15.2 Vercel 프로젝트 연결 (`vercel link`)
- [ ] 15.3 Neon DB 생성, DATABASE_URL·JWT_SECRET_KEY·CORS_ORIGINS 환경변수 설정
- [ ] 15.4 첫 배포 (`vercel --prod`) 및 동작 확인 (회원가입 → 팀 생성 → 칸반 → 채팅)
