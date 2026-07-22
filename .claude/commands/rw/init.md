# /rw:init — 템플릿 선별 초기화

claude-code-base 템플릿을 실제 프로젝트 스택에 맞게 선별 적용한다. 스택에 대해 질문한 뒤, 답변에 맞지 않는 `.claude/rules/`와 `.claude/agents/` 파일을 제거하거나 정리한다.

## 0단계: 안전 확인

1. `git remote -v`를 확인한다. 원격 저장소 이름에 `claude-code-base`가 포함돼 있으면 다음 메시지로 사용자에게 확인을 구한다(중단하지는 않되, 실수로 원본 템플릿에서 실행하는 상황을 막기 위함이다):
   > 이 저장소가 claude-code-base 템플릿 원본처럼 보입니다. 원본이 맞다면 실행을 중단해 주세요. 이 템플릿을 복사해서 만든 새 프로젝트라면 계속 진행해도 됩니다.
2. `.claude/rules/backend/`와 `.claude/rules/frontend/` 중 어느 것도 존재하지 않으면 다음 메시지를 출력하고 **중단**한다:
   > 이 저장소에는 claude-code-base 템플릿의 rules 디렉토리가 없습니다. 템플릿을 먼저 복사해 주세요.
3. `git status --short`로 커밋되지 않은 변경사항이 있으면 사용자에게 알리고, 먼저 커밋하거나 stash 할지 확인한다. 이번 작업의 삭제/편집 내역이 기존 변경사항과 섞이지 않도록 한다.

## 1단계: 스택 질문 (AskUserQuestion 사용, 여러 라운드로 진행)

**라운드 1 — 항상 묻는다**: "이 프로젝트는 어떤 영역을 사용합니까?"
- 백엔드만
- 프론트엔드만
- 풀스택 (백엔드 + 프론트엔드)

**라운드 2 — 라운드 1 답변에 따라 해당하는 것만 함께 묻는다**:
- (백엔드 포함 시) "백엔드 스택은 무엇입니까?" → Spring Boot(Java) / NestJS(TypeScript) / FastAPI(Python)
- (프론트엔드 포함 시) "프론트엔드 프레임워크는?" → Next.js / Vite

**라운드 3 — 백엔드 스택으로 "Spring Boot"를 선택한 경우에만 묻는다**:
- "MongoDB도 함께 사용합니까?" → JPA만 사용(기본) / JPA + MongoDB 함께 사용
- "Repository 조회 도구로 QueryDSL/jOOQ까지 쓸 계획이 있습니까?" → Specification까지만 사용(기본) / QueryDSL/jOOQ까지 쓸 계획 있음

NestJS/FastAPI를 선택한 경우 라운드 3은 건너뛴다(해당 세부 조정은 아직 규칙에 없다).

## 2단계: 삭제/편집 대상 확정

답변에 따라 아래 규칙을 조합해 대상 목록을 만든다. 질문에서 선택되지 않은 조합을 추측해서 임의로 처리하지 않는다.

### 백엔드 미포함 시 — 삭제
- `.claude/rules/backend/` 전체
- `.claude/agents/domain-designer.md`, `tdd-implementer.md`, `refactorer.md`, `test-author.md`, `code-reviewer.md`, `debugger.md`, `java-style-checker.md`, `openapi-spec-author.md`

### 백엔드 포함 + "Spring Boot" 선택 시 — 삭제
- `.claude/rules/backend/nestjs/`, `.claude/rules/backend/fastapi/` 전체 (`spring/`, `shared/`는 유지)

### 백엔드 포함 + "NestJS" 선택 시 — 삭제
- `.claude/rules/backend/spring/`, `.claude/rules/backend/fastapi/` 전체 (`nestjs/`, `shared/`는 유지)
- **에이전트는 삭제/수정하지 않는다.** 현재 `domain-designer`/`tdd-implementer`/`refactorer`/`test-author`/`code-reviewer`/`debugger`/`java-style-checker`/`openapi-spec-author` 8개는 전부 Spring 전용으로 작성돼 있어 NestJS 규칙을 참조하지 않는다. 3단계 보고 시 이 사실을 사용자에게 명시적으로 알린다: "이 에이전트들은 아직 Spring 전용입니다. NestJS 규칙 정리는 끝났지만, 이를 실제로 활용하는 전담 에이전트는 별도로 만들어야 합니다."

### 백엔드 포함 + "FastAPI" 선택 시 — 삭제
- `.claude/rules/backend/spring/`, `.claude/rules/backend/nestjs/` 전체 (`fastapi/`, `shared/`는 유지)
- NestJS와 동일한 이유로 **에이전트는 삭제/수정하지 않고**, 3단계 보고 시 같은 안내를 한다("FastAPI 규칙 정리는 끝났지만, 이를 활용하는 전담 에이전트는 별도로 만들어야 합니다").

### 프론트엔드 미포함 시 — 삭제
- `.claude/rules/frontend/` 전체
- `.claude/agents/frontend-*.md` (7개 전부: architect, code-reviewer, debugger, refactorer, style-checker, tdd-implementer, test-author)

### 프론트엔드 포함 + Next.js 선택 시 — 삭제
- `.claude/rules/frontend/vite.md`

### 프론트엔드 포함 + Vite 선택 시 — 삭제
- `.claude/rules/frontend/nextjs.md`

### 백엔드 스택 "Spring Boot" + "JPA만" 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/backend/spring/test.md`에서 MongoDB 관련 내용을 제거한다: base class 표에서 `IntegrationTestBase`(MongoDB Repository 통합), `WebIntegrationTestBase`(MongoDB Controller/Web) 행을 삭제하고, MongoDB 통합 테스트 관련 문단을 제거해 JPA 전용 안내만 남긴다.
- Edit 도구로 신중하게 처리하고, 편집 후 표/문단이 자연스럽게 이어지는지 다시 읽어 확인한다.

### 백엔드 스택 "Spring Boot" + "Specification까지만" 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/backend/spring/repository.md`에서 6번(QueryDSL 사용 규칙), 7.5번(jOOQ를 SQL 빌더로 사용) 섹션을 제거한다.
- 5번 "도구 선택 계층" 표와 8번 "Finder/Service 계층과의 통합" 다이어그램에 QueryDSL/jOOQ 관련 언급이 남아있으면 함께 정리해 본문과 표가 어긋나지 않도록 한다.

## 3단계: 확인 후 실행

1. 삭제/편집 대상 전체 목록을 사용자에게 보여주고 진행 여부를 확인받는다. NestJS/FastAPI를 선택한 경우 위 "에이전트는 삭제/수정하지 않는다" 안내도 함께 보여준다.
2. 확인되면 파일 삭제는 `git rm`으로, 내용 편집은 Edit로 수행한다.
3. 자동으로 커밋하지 않는다. 변경 결과를 요약해 보고하고, 사용자가 요청할 때만 커밋한다.

## 하지 말아야 할 것

- 사용자 확인 없이 바로 삭제/편집을 실행하지 않는다.
- 원본 템플릿 저장소에서 실행해 원본을 훼손하지 않는다(0단계 참조).
- 질문받지 않은 조합을 임의로 판단해서 처리하지 않는다.
- NestJS/FastAPI를 선택했다고 해서 Spring 전용 에이전트를 임의로 고치거나 이름을 바꾸지 않는다(별도 작업).
