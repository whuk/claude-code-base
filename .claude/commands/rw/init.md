---
description: "claude-code-base 템플릿을 실제 프로젝트 스택에 맞게 선별 적용하고, 해당하지 않는 rules/agents 파일을 정리한다."
argument-hint: "없음"
user-invocable: true
---

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
- (백엔드 포함 시) "백엔드 스택은 무엇입니까?" → Spring Boot(Java 또는 Kotlin) / NestJS(TypeScript) / FastAPI(Python)
- (프론트엔드 포함 시) "프론트엔드 프레임워크는?" → Next.js / Vite / Vue.js

**라운드 3 — 라운드 2 답변에 따라 해당하는 것만 묻는다**:

(백엔드 스택 "Spring Boot" 선택 시)
- "언어는 무엇입니까?" → Java(기본) / Kotlin
- "아키텍처 스타일은 무엇입니까?" → Layered(기본) / Hexagonal(Ports & Adapters)
- "MongoDB도 함께 사용합니까?" → JPA만 사용(기본) / JPA + MongoDB 함께 사용
- "Repository 조회 도구로 QueryDSL/jOOQ까지 쓸 계획이 있습니까?" → Specification까지만 사용(기본) / QueryDSL/jOOQ까지 쓸 계획 있음

(백엔드 스택 "NestJS" 선택 시)
- "ORM은 무엇을 사용합니까?" → TypeORM / Prisma
- "입력 검증 도구는 무엇을 사용합니까?" → class-validator(기본) / Zod(nestjs-zod)

(프론트엔드 "Vite" 선택 시)
- "라우팅 라이브러리는 무엇을 사용합니까?" → TanStack Router(기본 검토 대상) / React Router

FastAPI를 선택한 경우 백엔드 세부 질문은 없다(`fastapi.md`가 단일 경로만 정의한다). Next.js/Vue.js를 선택한 경우 프론트엔드 세부 질문은 없다.

## 2단계: 삭제/편집 대상 확정

답변에 따라 아래 규칙을 조합해 대상 목록을 만든다. 질문에서 선택되지 않은 조합을 추측해서 임의로 처리하지 않는다.

### 백엔드 미포함 시 — 삭제
- `.claude/rules/backend/` 전체
- 모든 백엔드 에이전트: `.claude/agents/spring-*.md`(spring-hexagonal-* 포함 14개), `.claude/agents/nestjs-*.md`(7개), `.claude/agents/fastapi-*.md`(7개)

### 백엔드 포함 + "Spring Boot" 선택 시 — 삭제
- `.claude/rules/backend/nestjs/`, `.claude/rules/backend/fastapi/` 전체 (`spring/`, `shared/`는 유지)
- `.claude/agents/nestjs-*.md`(7개), `.claude/agents/fastapi-*.md`(7개)

### 백엔드 스택 "Spring Boot" + 언어 "Java" 선택 시 — 삭제
- `.claude/rules/backend/spring/kotlin/` 전체 (`spring/java/`, `spring/api-dto.md`는 유지)

### 백엔드 스택 "Spring Boot" + 언어 "Kotlin" 선택 시 — 삭제
- `.claude/rules/backend/spring/java/` 전체 (`spring/kotlin/`, `spring/api-dto.md`는 유지)

### 백엔드 스택 "Spring Boot" + 아키텍처 스타일 "Layered" 선택 시 — 삭제
- 선택한 언어 디렉토리의 `.claude/rules/backend/spring/{java|kotlin}/hexagonal/` 전체 (`spring/{java|kotlin}/layered/`, `spring/api-dto.md`는 유지)
- Hexagonal 전담 에이전트 6개: `.claude/agents/spring-hexagonal-*.md`

### 백엔드 스택 "Spring Boot" + 아키텍처 스타일 "Hexagonal" 선택 시 — 삭제
- 선택한 언어 디렉토리의 `.claude/rules/backend/spring/{java|kotlin}/layered/` 전체 (`spring/{java|kotlin}/hexagonal/`, `spring/api-dto.md`는 유지)
- Layered 전제 에이전트 6개: `.claude/agents/spring-domain-designer.md`, `spring-tdd-implementer.md`, `spring-refactorer.md`, `spring-test-author.md`, `spring-code-reviewer.md`, `spring-debugger.md` (`spring-hexagonal-*` 6개와, 아키텍처 스타일과 무관한 `spring-style-checker`/`spring-openapi-spec-author`는 유지)

### 백엔드 포함 + "NestJS" 선택 시 — 삭제
- `.claude/rules/backend/spring/`, `.claude/rules/backend/fastapi/` 전체 (`nestjs/`, `shared/`는 유지)
- `.claude/agents/spring-*.md`(spring-hexagonal-* 포함 14개), `.claude/agents/fastapi-*.md`(7개)

### 백엔드 포함 + "FastAPI" 선택 시 — 삭제
- `.claude/rules/backend/spring/`, `.claude/rules/backend/nestjs/` 전체 (`fastapi/`, `shared/`는 유지)
- `.claude/agents/spring-*.md`(spring-hexagonal-* 포함 14개), `.claude/agents/nestjs-*.md`(7개)

### 프론트엔드 미포함 시 — 삭제
- `.claude/rules/frontend/` 전체
- `.claude/agents/frontend-*.md` (7개 전부: architect, code-reviewer, debugger, refactorer, style-checker, tdd-implementer, test-author)

### 프론트엔드 포함 + Next.js 선택 시 — 삭제
- `.claude/rules/frontend/vite.md`, `.claude/rules/frontend/vue.md`

### 프론트엔드 포함 + Vite 선택 시 — 삭제
- `.claude/rules/frontend/nextjs.md`, `.claude/rules/frontend/vue.md`

### 프론트엔드 포함 + Vue.js 선택 시 — 삭제
- `.claude/rules/frontend/nextjs.md`, `.claude/rules/frontend/vite.md`
- **`frontend-*` 에이전트는 삭제/수정하지 않는다.** `frontend-architect`/`frontend-tdd-implementer`/`frontend-code-reviewer`/`frontend-debugger`는 현재 Next.js/Vite(React 계열) 전제로 작성돼 있어 Vue.js 규칙(Composition API, Pinia, Vue Router 등)을 참조하지 않는다. 3단계 보고 시 이 사실을 사용자에게 명시적으로 알린다: "frontend 에이전트들은 아직 Next.js/Vite 전용입니다. Vue.js 규칙 정리는 끝났지만, 이를 실제로 활용하는 전담 에이전트는 별도로 만들어야 합니다."

### 백엔드 스택 "Spring Boot" + "JPA만" 선택 시 — 편집 (파일 삭제 아님)
- 언어·아키텍처 스타일 답변에 따라 `.claude/rules/backend/spring/{java|kotlin}/layered/test.md` 또는 `.claude/rules/backend/spring/{java|kotlin}/hexagonal/test.md`에서 MongoDB 관련 내용을 제거한다: base class 표에서 `IntegrationTestBase`(MongoDB Repository/Persistence Adapter 통합), `WebIntegrationTestBase`(MongoDB Controller/Web Adapter) 행을 삭제하고, MongoDB 통합 테스트 관련 문단을 제거해 JPA 전용 안내만 남긴다.
- Edit 도구로 신중하게 처리하고, 편집 후 표/문단이 자연스럽게 이어지는지 다시 읽어 확인한다.

### 백엔드 스택 "Spring Boot" + "Specification까지만" 선택 시 — 편집 (파일 삭제 아님)
- 언어·아키텍처 스타일 답변에 따라 `.claude/rules/backend/spring/{java|kotlin}/layered/repository.md` 또는 `.claude/rules/backend/spring/{java|kotlin}/hexagonal/repository.md`에서 QueryDSL 사용 규칙, jOOQ를 SQL 빌더로 사용하는 섹션을 제거한다.
- "도구 선택 계층" 표와 "Finder/Service 계층과의 통합" 다이어그램에 QueryDSL/jOOQ 관련 언급이 남아있으면 함께 정리해 본문과 표가 어긋나지 않도록 한다.

### 백엔드 스택 "NestJS" + ORM 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/backend/nestjs/nestjs.md`에서 선택하지 않은 ORM 관련 내용을 제거한다: 4번(영속성)의 해당 ORM 항목, 5번(Repository 도구)·6번(트랜잭션)·10번(금지 패턴)의 해당 ORM 도구 언급.
- Prisma를 선택한 경우 금지 패턴의 TypeORM 컬럼 데코레이터 항목(`EntitySchema` 사용)도 함께 제거한다.
- 편집 후 각 섹션이 선택한 ORM 단일 경로로 자연스럽게 읽히는지 다시 읽어 확인한다.
- `nestjs-*` 에이전트는 두 ORM을 조건부로 함께 언급하므로 수정하지 않는다.

### 백엔드 스택 "NestJS" + 검증 도구 선택 시 — 편집 (파일 삭제 아님)
- class-validator 선택 시: `nestjs.md` 3번에서 Zod 허용 문장("Zod 스키마 기반 검증(`nestjs-zod`)도 허용하되 ... 통일한다")을 제거한다.
- Zod 선택 시: `nestjs.md` 3번을 `nestjs-zod` 기준으로 조정한다 — class-validator 기본 문장을 Zod 스키마 기반 검증으로 바꾸고, 다중 진입점 방어 항목의 `validateOrReject()` 언급을 Command 생성 시점의 Zod 스키마 `parse()` 호출로 대체한다.
- **Zod 선택 시 `nestjs-*` 에이전트는 수정하지 않는다.** `nestjs-tdd-implementer`/`nestjs-code-reviewer`/`nestjs-domain-designer`는 class-validator 전제로 작성돼 있다. 3단계 보고 시 이 사실을 사용자에게 명시적으로 알린다: "nestjs 에이전트들은 class-validator 전제입니다. Zod 기준으로 활용하려면 에이전트를 별도로 조정해야 합니다."

### 프론트엔드 "Vite" + 라우팅 라이브러리 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/frontend/vite.md` 3번(라우팅)에서 선택하지 않은 라이브러리 항목을 제거하고, 선택한 라이브러리를 확정 문장으로 바꾼다. "둘 중 하나를 프로젝트 시작 시점에 고정한다" 문장은 선택이 끝났으므로 제거한다.
- 5번(금지 패턴)의 "라우팅 라이브러리를 프로젝트 중간에 이유 없이 교체하지 않는다"는 그대로 둔다.

## 3단계: 확인 후 실행

1. 삭제/편집 대상 전체 목록을 사용자에게 보여주고 진행 여부를 확인받는다. Vue.js를 선택한 경우 "`frontend-*` 에이전트는 삭제/수정하지 않는다" 안내를, NestJS + Zod를 선택한 경우 "nestjs 에이전트들은 class-validator 전제" 안내를 함께 보여준다.
2. 확인되면 파일 삭제는 `git rm`으로, 내용 편집은 Edit로 수행한다.
3. 자동으로 커밋하지 않는다. 사용자가 요청할 때만 커밋한다.

## 결과 보고

- 선택된 스택 조합 요약 (영역, 백엔드 스택·언어·아키텍처, 프론트엔드 프레임워크 등)
- 삭제한 파일/디렉토리 목록과 편집한 파일 목록
- 해당 시 에이전트 안내문 (Hexagonal의 `spring-*`, Vue.js의 `frontend-*`, NestJS+Zod의 `nestjs-*` 안내)
- 커밋하지 않았음을 명시하고, 커밋을 원하면 요청하도록 안내

## 하지 말아야 할 것

- 사용자 확인 없이 바로 삭제/편집을 실행하지 않는다.
- 원본 템플릿 저장소에서 실행해 원본을 훼손하지 않는다(0단계 참조).
- 질문받지 않은 조합을 임의로 판단해서 처리하지 않는다.
- Vue.js를 선택했다고 해서 Next.js/Vite 전제로 작성된 `frontend-*` 에이전트를 임의로 고치거나 이름을 바꾸지 않는다(별도 작업).
- Zod를 선택했다고 해서 class-validator 전제로 작성된 `nestjs-*` 에이전트를 임의로 고치지 않는다(별도 작업).
