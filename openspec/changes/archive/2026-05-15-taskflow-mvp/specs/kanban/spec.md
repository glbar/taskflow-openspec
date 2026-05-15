## ADDED Requirements

### Requirement: 태스크 목록 조회
`GET /teams/{id}/tasks`는 해당 팀의 태스크를 반환한다. 필터(전체/@me/미할당)와 정렬(최근 생성순 기본)을 지원한다.

- `filter=me`: `assignee_id = current_user_id`
- `filter=unassigned`: `assignee_id IS NULL`
- 기본(필터 없음): 팀 전체 태스크
- 정렬: `created_at DESC`

#### Scenario: 전체 태스크 조회
- **WHEN** 팀 멤버가 GET /teams/{id}/tasks 호출
- **THEN** HTTP 200, 해당 팀의 모든 태스크를 created_at DESC로 반환

#### Scenario: 내 태스크 필터
- **WHEN** GET /teams/{id}/tasks?filter=me 호출
- **THEN** HTTP 200, assignee_id = current_user_id인 태스크만 반환 (creator_id 기준 아님)

#### Scenario: 미할당 태스크 필터
- **WHEN** GET /teams/{id}/tasks?filter=unassigned 호출
- **THEN** HTTP 200, assignee_id IS NULL인 태스크만 반환

---

### Requirement: 태스크 생성
`POST /teams/{id}/tasks`로 태스크를 생성한다. 초기 상태는 항상 `TODO`이다. assignee_id는 nullable이다(미할당 가능).

- title: 1–100자, 필수
- assignee_id: FK→users, nullable
- creator_id: 현재 로그인 사용자 자동 설정
- 성공 응답: HTTP 201 + 생성된 태스크

#### Scenario: 담당자 지정 태스크 생성
- **WHEN** 팀 멤버가 title과 assignee_id로 POST /teams/{id}/tasks 호출
- **THEN** HTTP 201, status="TODO", creator_id=현재유저, assignee_id=지정유저

#### Scenario: 미할당 태스크 생성
- **WHEN** assignee_id 없이 POST /teams/{id}/tasks 호출
- **THEN** HTTP 201, assignee_id=null

#### Scenario: 제목 길이 초과
- **WHEN** 101자 이상 title로 POST /teams/{id}/tasks 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR" } }`

---

### Requirement: 태스크 상태 변경 (드래그)
`PATCH /tasks/{id}/status`는 태스크 상태를 변경한다. 허용 값: `TODO`, `DOING`, `DONE`. 팀 멤버라면 누구나 상태 변경 가능하다.

#### Scenario: 상태 변경 성공
- **WHEN** 팀 멤버가 PATCH /tasks/{id}/status { status: "DOING" } 호출
- **THEN** HTTP 200, tasks.status UPDATE, 업데이트된 태스크 반환

#### Scenario: 유효하지 않은 상태값
- **WHEN** status="IN_PROGRESS" 등 허용되지 않은 값으로 PATCH 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR" } }`

---

### Requirement: 태스크 제목·담당자 수정
`PUT /tasks/{id}`는 title과 assignee_id를 수정한다. 팀 멤버라면 누구나 수정 가능하다.

#### Scenario: 제목 수정
- **WHEN** 팀 멤버가 PUT /tasks/{id} { title: "새 제목" } 호출
- **THEN** HTTP 200, tasks.title UPDATE

#### Scenario: 담당자 변경
- **WHEN** PUT /tasks/{id} { assignee_id: 5 } 호출
- **THEN** HTTP 200, tasks.assignee_id UPDATE

#### Scenario: 담당자 미할당으로 변경
- **WHEN** PUT /tasks/{id} { assignee_id: null } 호출
- **THEN** HTTP 200, tasks.assignee_id = null

---

### Requirement: 태스크 단일 조회
`GET /tasks/{id}`는 태스크 상세 정보를 반환한다. 해당 팀 멤버만 접근 가능하다.

#### Scenario: 단일 태스크 조회
- **WHEN** 팀 멤버가 GET /tasks/{id} 호출
- **THEN** HTTP 200, `{ id, team_id, title, status, creator_id, assignee_id, created_at }` 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** GET /tasks/9999 호출
- **THEN** HTTP 404, `{ error: { code: "NOT_FOUND" } }`

---

### Requirement: 태스크 삭제 권한
`DELETE /tasks/{id}`는 creator(생성자) 또는 team owner만 가능하다. 그 외 멤버가 시도하면 403을 반환한다. 삭제 전 확인 다이얼로그를 클라이언트에서 표시한다.

#### Scenario: 생성자가 자신의 태스크 삭제
- **WHEN** creator_id = current_user_id인 사용자가 DELETE /tasks/{id} 호출
- **THEN** HTTP 200, tasks DELETE

#### Scenario: 팀 owner가 타인 태스크 삭제
- **WHEN** team owner가 타인이 만든 태스크에 DELETE /tasks/{id} 호출
- **THEN** HTTP 200, tasks DELETE

#### Scenario: 일반 멤버가 타인 태스크 삭제 시도
- **WHEN** creator도 아니고 owner도 아닌 멤버가 DELETE /tasks/{id} 호출
- **THEN** HTTP 403, `{ error: { code: "FORBIDDEN", message: "권한이 없습니다" } }`
