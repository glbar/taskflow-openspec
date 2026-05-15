## ADDED Requirements

### Requirement: 회원가입
사용자는 이메일과 비밀번호로 계정을 생성할 수 있다. 시스템은 `POST /auth/signup`을 통해 계정을 생성하고 JWT를 즉시 반환한다. 비밀번호는 bcrypt로 해시하여 저장한다. 이메일 인증은 없다(즉시 활성화).

- 이메일: 유효한 형식, UNIQUE 제약
- 비밀번호: 8자 이상
- 성공 응답: HTTP 201 + `{ token, user: { id, email, team_id } }`
- 실패 응답 표준: `{ error: { code, message } }`

#### Scenario: 정상 회원가입
- **WHEN** 유효한 이메일과 8자 이상 비밀번호로 POST /auth/signup 호출
- **THEN** HTTP 201, JWT 토큰 반환, users 테이블에 INSERT, team_id=null

#### Scenario: 이메일 중복
- **WHEN** 이미 가입된 이메일로 POST /auth/signup 호출
- **THEN** HTTP 409, `{ error: { code: "EMAIL_TAKEN", message: "이미 가입된 이메일입니다" } }`

#### Scenario: 이메일 형식 오류
- **WHEN** 유효하지 않은 이메일 형식(예: "user@invalid")으로 POST /auth/signup 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR" } }`

#### Scenario: 비밀번호 8자 미만
- **WHEN** 7자 이하 비밀번호로 POST /auth/signup 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR" } }`

---

### Requirement: 로그인
사용자는 이메일과 비밀번호로 로그인하여 JWT를 발급받는다. `POST /auth/login`은 검증 성공 시 HTTP 200 + JWT(만료 24h) + 사용자 정보를 반환한다. 클라이언트는 토큰을 `localStorage`에 저장하고, `team_id` 값에 따라 화면을 분기한다 (null → 팀 선택 화면, 값 있음 → 칸반 화면).

#### Scenario: 정상 로그인
- **WHEN** 등록된 이메일과 올바른 비밀번호로 POST /auth/login 호출
- **THEN** HTTP 200, `{ token: "eyJ...", user: { id, email, team_id } }` 반환

#### Scenario: team_id null인 사용자 로그인
- **WHEN** 팀에 소속되지 않은 사용자가 로그인
- **THEN** 응답 user.team_id = null, 클라이언트는 팀 선택 화면으로 이동

#### Scenario: 자격증명 오류
- **WHEN** 존재하지 않는 이메일 또는 틀린 비밀번호로 POST /auth/login 호출
- **THEN** HTTP 401, `{ error: { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 일치하지 않습니다" } }` (이메일 존재 여부 노출 금지)

---

### Requirement: 로그아웃
로그아웃은 stateless로 처리한다. `POST /auth/logout`은 서버에서 블랙리스트를 관리하지 않고 HTTP 200만 반환한다. 실제 토큰 폐기는 클라이언트(`localStorage.removeItem('token')`)에서 처리한다.

#### Scenario: 정상 로그아웃
- **WHEN** 유효한 JWT로 POST /auth/logout 호출
- **THEN** HTTP 200 `{}` 반환, 서버 상태 변경 없음

#### Scenario: 클라이언트 토큰 삭제
- **WHEN** 로그아웃 요청 완료
- **THEN** 클라이언트가 localStorage에서 토큰 삭제 후 /login으로 redirect

---

### Requirement: 현재 사용자 조회
`GET /auth/me`는 JWT에서 사용자 정보를 추출하여 반환한다. 페이지 진입 시 토큰 유효성 확인에 사용된다.

#### Scenario: 유효한 토큰으로 조회
- **WHEN** 유효한 JWT로 GET /auth/me 호출
- **THEN** HTTP 200, `{ id, email, team_id }` 반환

#### Scenario: 토큰 만료
- **WHEN** 만료된 JWT로 API 호출
- **THEN** HTTP 401, `{ error: { code: "TOKEN_EXPIRED", message: "인증이 만료되었습니다" } }`, 클라이언트는 localStorage 삭제 후 /login redirect

---

### Requirement: JWT 보호 미들웨어
`/teams/*`, `/tasks/*`, `/messages/*` 경로는 모두 유효한 JWT가 필요하다. Authorization 헤더가 없거나 토큰이 유효하지 않으면 HTTP 401을 반환한다.

#### Scenario: 인증 없이 보호 경로 접근
- **WHEN** Authorization 헤더 없이 GET /teams/{id}/tasks 호출
- **THEN** HTTP 401, `{ error: { code: "TOKEN_EXPIRED" } }`
