## ADDED Requirements

### Requirement: 채팅 메시지 조회 (폴링)
`GET /teams/{id}/messages`는 팀 채팅 메시지를 반환한다. `since` 파라미터(ISO 타임스탬프, URL 인코딩)를 사용하여 증분 폴링을 지원한다.

- `since` 없음: 최근 50개 반환 (첫 진입)
- `since=<ISO>`: 해당 시각 이후 메시지만 반환 (5초 폴링)
- 정렬: `created_at ASC`
- 응답: `[{ id, user_id, user_email, content, created_at }]`

#### Scenario: 첫 진입 조회
- **WHEN** since 파라미터 없이 GET /teams/{id}/messages 호출
- **THEN** HTTP 200, 최근 50개 메시지를 created_at ASC로 반환

#### Scenario: 증분 폴링
- **WHEN** since=2026-05-13T14%3A27%3A00Z 로 GET /teams/{id}/messages 호출
- **THEN** HTTP 200, created_at > since인 메시지만 반환 (없으면 빈 배열 [])

#### Scenario: 메시지 없는 팀
- **WHEN** 메시지가 0건인 팀에서 GET /teams/{id}/messages 호출
- **THEN** HTTP 200, 빈 배열 [] 반환

---

### Requirement: 채팅 메시지 전송
`POST /teams/{id}/messages`로 메시지를 전송한다. 메시지 길이는 1–1000자이다. 클라이언트와 서버 양쪽에서 검증한다.

#### Scenario: 정상 메시지 전송
- **WHEN** 팀 멤버가 1000자 이내 content로 POST /teams/{id}/messages 호출
- **THEN** HTTP 201, messages INSERT, `{ id, user_id, user_email, content, created_at }` 반환

#### Scenario: 1000자 초과 메시지
- **WHEN** 1001자 이상 content로 POST /teams/{id}/messages 호출
- **THEN** HTTP 400, `{ error: { code: "TOO_LONG", message: "메시지는 1000자 이내로 입력하세요", limit: 1000, actual: <실제길이> } }`

#### Scenario: 빈 메시지
- **WHEN** 빈 문자열 또는 공백만으로 POST /teams/{id}/messages 호출
- **THEN** HTTP 400, `{ error: { code: "VALIDATION_ERROR" } }`

---

### Requirement: 채팅 메시지 삭제
`DELETE /messages/{id}`는 본인 메시지만 삭제할 수 있다. team owner도 타인 메시지를 삭제할 수 없다. 삭제 확인 다이얼로그 없이 즉시 삭제한다(클라이언트 호버 메뉴).

#### Scenario: 본인 메시지 삭제
- **WHEN** 메시지 작성자가 DELETE /messages/{id} 호출
- **THEN** HTTP 200, messages DELETE

#### Scenario: 타인 메시지 삭제 시도
- **WHEN** 메시지 작성자가 아닌 사용자(owner 포함)가 DELETE /messages/{id} 호출
- **THEN** HTTP 403, `{ error: { code: "NOT_OWNER", message: "본인의 메시지만 삭제할 수 있습니다" } }`

---

### Requirement: 폴링 신뢰성
클라이언트는 5초 간격으로 폴링하며, 네트워크 오류 시 exponential backoff(5s→10s→20s→40s→최대 60s)로 재시도한다. 재연결 시 `since` 파라미터로 누락 메시지를 일괄 수신한다.

#### Scenario: 폴링 성공 후 메시지 누락 없음
- **WHEN** POST /messages로 성공(201)한 메시지가 있음
- **THEN** 이후 GET /messages (since= 포함)에서 반드시 해당 메시지가 포함됨

#### Scenario: 네트워크 오류 후 재연결
- **WHEN** 폴링 실패 후 재연결 성공
- **THEN** since= 파라미터로 끊긴 동안 발생한 메시지를 모두 수신
