## Why

소규모 팀(3–5인)이 업무 진행 상황을 칸반 보드와 실시간 채팅으로 한 화면에서 추적할 수 있는 MVP 웹 애플리케이션이 필요하다. 기존에 산재된 도구(메신저 + 스프레드시트) 대신 초대코드 기반 팀 합류, 드래그 칸반, 5초 폴링 채팅을 하나의 URL로 제공한다.

## What Changes

- **인증**: 이메일/비밀번호 회원가입·로그인, JWT 발급(24h), bcrypt 해시 저장
- **팀**: 팀 생성 + 초대코드 자동 발급, 코드로 합류, 멤버 목록 조회, 팀 탈퇴
- **칸반**: TODO/DOING/DONE 3컬럼 태스크 보드, 드래그로 상태 이동, assignee 지정
- **채팅**: 팀 단위 메시지 송수신, 5초 폴링(`since=` 증분), 1000자 제한
- **배포**: 로컬 FastAPI + SQLite → Vercel(FE+BE) + Neon PostgreSQL 원클릭 배포

**Out of Scope**: 알림(이메일/SMS/푸시), 파일 첨부, 전문 검색, 권한 세분화(팀 admin/member 구분만), 다국어, WebSocket, 자동화 테스트

## Capabilities

### New Capabilities

- `user-auth`: 회원가입·로그인·JWT 발급·로그아웃(stateless)·현재 사용자 조회
- `team-management`: 팀 생성·초대코드 발급·코드 합류·멤버 목록·팀 탈퇴·팀 정보 조회
- `kanban`: 태스크 CRUD, TODO/DOING/DONE 상태 전환(드래그), assignee 지정·필터
- `chat`: 팀 채팅 송수신·5초 폴링·메시지 삭제(본인만)
- `deployment`: 로컬 SQLite ↔ 운영 Neon 환경 분리, Vercel FE+BE 배포

### Modified Capabilities

## Impact

- **새 파일**: FastAPI 백엔드(`api/`), Vanilla JS + Tailwind 프론트(`frontend/`), DB 마이그레이션
- **API**: 18개 엔드포인트 (Auth 4 + Team 5 + Task 6 + Chat 3)
- **DB**: 4테이블 — `users`, `teams`, `tasks`, `messages`
- **환경변수**: `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`
- **외부 의존**: Vercel(배포), Neon(운영 DB), bcrypt, python-jose(또는 PyJWT)
