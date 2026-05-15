## ADDED Requirements

### Requirement: 팀 생성
인증된 사용자는 `POST /teams`로 팀을 생성한다. 서버는 초대코드(`AAAA-9999` 형식)를 자동 생성하고, 생성자를 owner로 지정하며, `users.team_id`를 해당 팀 ID로 업데이트한다. 팀 이름은 1–30자이다.

- 성공 응답: HTTP 201 + `{ id, name, invite_code, owner_id, created_at }`
- 이미 팀에 소속된 사용자는 새 팀을 만들 수 없다 (1인 1팀 제약)

#### Scenario: 정상 팀 생성
- **WHEN** 팀 미소속 사용자가 유효한 팀명으로 POST /teams 호출
- **THEN** HTTP 201, teams INSERT, users.team_id UPDATE, invite_code 자동 생성(예: "FRNT-2026")

#### Scenario: 초대코드 형식 검증
- **WHEN** 팀이 생성됨
- **THEN** invite_code가 `^[A-Z]{4}-[0-9]{4}$` 정규식을 만족함

#### Scenario: 팀명 길이 초과
- **WHEN** 31자 이상의 팀명으로 POST /teams 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR" } }`

---

### Requirement: 초대코드로 팀 합류
미소속 사용자는 `POST /teams/join`에 초대코드를 전달하여 팀에 합류한다. 성공 시 `users.team_id`가 해당 팀 ID로 업데이트된다.

- 초대코드 형식: `^[A-Z]{4}-[0-9]{4}$` (클라이언트·서버 양쪽 검증)

#### Scenario: 정상 합류
- **WHEN** 유효한 초대코드로 POST /teams/join 호출
- **THEN** HTTP 200, users.team_id UPDATE, `{ team: { id, name, member_count }, redirect: "/teams/{id}" }` 반환

#### Scenario: 초대코드 형식 오류
- **WHEN** 소문자 또는 하이픈 없는 코드로 POST /teams/join 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR", message: "형식이 올바르지 않습니다" } }`

#### Scenario: 존재하지 않는 초대코드
- **WHEN** 형식은 맞지만 DB에 없는 코드로 POST /teams/join 호출
- **THEN** HTTP 404, `{ error: { code: "NOT_FOUND", message: "해당 초대코드를 찾을 수 없습니다" } }`

#### Scenario: 이미 팀 소속 사용자
- **WHEN** 이미 team_id가 있는 사용자가 POST /teams/join 호출
- **THEN** HTTP 409, `{ error: { code: "ALREADY_IN_TEAM", message: "이미 다른 팀에 소속되어 있습니다" } }`

---

### Requirement: 팀 정보 조회
`GET /teams/{id}`는 팀 정보를 반환한다. 해당 팀의 멤버만 접근 가능하다. 비멤버는 403을 반환한다.

#### Scenario: 멤버가 팀 정보 조회
- **WHEN** 해당 팀 멤버가 GET /teams/{id} 호출
- **THEN** HTTP 200, `{ id, name, invite_code, owner_id, created_at }` 반환

#### Scenario: 비멤버 접근
- **WHEN** 다른 팀 사용자가 GET /teams/{id} 호출
- **THEN** HTTP 403, `{ error: { code: "FORBIDDEN", message: "이 팀의 멤버가 아닙니다" } }`

---

### Requirement: 팀 멤버 목록 조회
`GET /teams/{id}/members`는 해당 팀의 멤버 목록을 반환한다. owner는 `is_owner: true`로 구분된다. 해당 팀 멤버만 접근 가능하다.

#### Scenario: 멤버 목록 조회
- **WHEN** 팀 멤버가 GET /teams/{id}/members 호출
- **THEN** HTTP 200, `[{ id, email, is_owner, team_joined_at }]` 반환, owner가 목록 상단

---

### Requirement: 팀 탈퇴
`DELETE /teams/{id}/leave`로 팀에서 탈퇴한다. 탈퇴 후 `users.team_id`는 null이 된다. owner가 탈퇴하면 팀이 삭제되지 않고 owner_id만 유지된다(Day 2 범위 외: owner 이전).

#### Scenario: 일반 멤버 탈퇴
- **WHEN** 팀 멤버가 DELETE /teams/{id}/leave 호출
- **THEN** HTTP 200, users.team_id = null로 UPDATE

#### Scenario: 탈퇴 후 팀 재합류
- **WHEN** 탈퇴 후 다른 초대코드로 POST /teams/join 호출
- **THEN** 정상 합류 처리 (team_id가 null이므로 ALREADY_IN_TEAM 발생 안 함)

---

### Requirement: 팀 미소속 사용자 차단
`users.team_id = null`인 사용자가 `/teams/*` 또는 `/tasks/*`, `/messages/*`에 접근하면 팀 선택 화면으로 redirect된다. 서버는 403을 반환한다.

#### Scenario: 미소속 사용자 칸반 접근
- **WHEN** team_id=null인 사용자가 GET /teams/{id}/tasks 호출
- **THEN** HTTP 403, `{ error: { code: "FORBIDDEN" } }`
