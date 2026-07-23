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
- (언어 "Java" 선택 시) "웹 스택은 무엇입니까?" → Spring MVC(서블릿, 기본) / WebFlux(리액티브). WebFlux 규칙은 현재 Java 전용이므로 Kotlin 선택 시 이 질문은 묻지 않고 MVC로 간주한다
- (웹 스택이 "Spring MVC"인 경우에만) "영속성 도구는 무엇입니까?" → JPA(ORM, 기본) / SQL-first(JdbcClient + jOOQ, ORM 미사용). WebFlux 선택 시 영속성은 R2DBC로 고정되므로 이 질문과 아래 JPA 세부 질문 2개를 묻지 않는다
- (영속성 도구 "JPA" 선택 시) "MongoDB도 함께 사용합니까?" → JPA만 사용(기본) / JPA + MongoDB 함께 사용
- (영속성 도구 "JPA" 선택 시) "Repository 조회 도구로 QueryDSL/jOOQ까지 쓸 계획이 있습니까?" → Specification까지만 사용(기본) / QueryDSL/jOOQ까지 쓸 계획 있음
- (웹 스택 "WebFlux" 선택 시) "리액티브 MongoDB도 함께 사용합니까?" → R2DBC만 사용(기본) / R2DBC + 리액티브 MongoDB 함께 사용
- "주 관계형 데이터베이스(RDB)는 무엇입니까?" → PostgreSQL(기본) / MySQL / MariaDB / 그 외 유명 DB(Oracle·SQL Server·SQLite 등, "Other"로 직접 입력). 옵션 설명에 PostgreSQL/MySQL이 가장 자주 사용되는 선택지임을 표기한다. 웹 스택과 무관하게 묻는다(WebFlux면 jOOQ 방언과 R2DBC 드라이버 선택의 기준이 된다).

(백엔드 스택 "NestJS" 선택 시)
- "영속성 도구는 무엇을 사용합니까?" → TypeORM / Prisma / 사용 안 함(SQL-first, Kysely)
- "입력 검증 도구는 무엇을 사용합니까?" → class-validator(기본) / Zod(nestjs-zod)
- RDB 질문은 하지 않는다 — `nestjs.md`에 DB 벤더 종속 내용이 없어 답변이 편집으로 이어지지 않는다.

(백엔드 스택 "FastAPI" 선택 시)
- "SQLAlchemy ORM을 사용합니까?" → ORM 사용(기본) / SQL-first(Core/async 드라이버만, ORM 미사용)
- "주 관계형 데이터베이스(RDB)는 무엇입니까?" → PostgreSQL(기본) / MySQL / MariaDB / 그 외 유명 DB(SQLite 등, "Other"로 직접 입력). 옵션 설명에 PostgreSQL/MySQL이 가장 자주 사용되는 선택지임을 표기한다.

(프론트엔드 "Vite" 선택 시)
- "라우팅 라이브러리는 무엇을 사용합니까?" → TanStack Router(기본 검토 대상) / React Router

(풀스택 + 백엔드 "NestJS" 선택 시)
- "프론트엔드 소스 루트 경로는 무엇입니까?" (예: `apps/web`, `frontend`, `web`) — 백엔드와 프론트엔드가 모두 TypeScript이므로 frontend rules의 glob 범위를 좁히는 데 사용한다 (2단계의 해당 편집 규칙 참조)

Next.js/Vue.js를 선택한 경우 프론트엔드 세부 질문은 없다.

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
- 선택한 언어 디렉토리의 `.claude/rules/backend/spring/{java|kotlin}/hexagonal/` 전체 (`spring/{java|kotlin}/layered/`, 아키텍처 공통인 `spring/{java|kotlin}/repository-tools.md`, `spring/api-dto.md`는 유지)
- Hexagonal 전담 에이전트 6개: `.claude/agents/spring-hexagonal-*.md`

### 백엔드 스택 "Spring Boot" + 아키텍처 스타일 "Hexagonal" 선택 시 — 삭제
- 선택한 언어 디렉토리의 `.claude/rules/backend/spring/{java|kotlin}/layered/` 전체 (`spring/{java|kotlin}/hexagonal/`, 아키텍처 공통인 `spring/{java|kotlin}/repository-tools.md`, `spring/api-dto.md`는 유지)
- Layered 전제 에이전트 6개: `.claude/agents/spring-domain-designer.md`, `spring-tdd-implementer.md`, `spring-refactorer.md`, `spring-test-author.md`, `spring-code-reviewer.md`, `spring-debugger.md` (`spring-hexagonal-*` 6개와, 아키텍처 스타일과 무관한 `spring-style-checker`/`spring-openapi-spec-author`는 유지)

### 백엔드 스택 "Spring Boot" + 언어 "Java" + 웹 스택 "Spring MVC" 선택 시 — 삭제
- `.claude/rules/backend/spring/java/webflux.md`, `.claude/rules/backend/spring/java/repository-r2dbc.md` (WebFlux 전용 규칙. 언어 "Kotlin" 선택 시에는 `spring/java/` 전체 삭제에 이미 포함되므로 별도 처리가 없다)

### 백엔드 스택 "Spring Boot" + 웹 스택 "WebFlux" 선택 시 — 삭제 + 편집
- 영속성 질문(JPA/SQL-first)을 묻지 않았으므로 JPA/SQL-first의 삭제·편집 케이스와 MongoDB(JPA용)/QueryDSL 편집 케이스는 적용하지 않는다.
- 선택한 아키텍처의 `.claude/rules/backend/spring/java/{layered|hexagonal}/repository.md`와 `.claude/rules/backend/spring/java/repository-tools.md`, `.claude/rules/backend/spring/java/repository-sql.md`를 삭제한다 (`repository-r2dbc.md`가 대체한다).
- Layered면 `spring/java/layered/domain.md`를 편집한다: 2번(인프라 비종속)의 `@Entity` 마커 허용·orm.xml 분리 문장을 순수 Domain 기준(영속성 애노테이션 전면 금지)으로 수정하고, 9번(JPA 영속성 매핑) 섹션을 삭제하며, 마지막 금지 패턴의 orm.xml 항목과 도입부의 SQL-first/WebFlux 안내 문장을 정리한다. 편집 후 번호와 문맥이 자연스럽게 이어지는지 다시 읽어 확인한다.
- Hexagonal이면 추가 편집이 없다 (`ports-and-adapters.md`·`hexagonal/domain.md`의 `{Domain}JpaEntity` 언급은 `repository-r2dbc.md` 2번의 대체 규정이 우선한다).
- `test.md`는 접두사 대체 목적으로는 편집하지 않는다 — base class 표의 `Jpa*` 접두사는 `webflux.md` 8번의 대체 규정(`R2dbc*` 접두사, WebTestClient)으로 갈음한다.
- (리액티브 MongoDB "R2DBC만 사용" 선택 시) `repository-r2dbc.md`에서 7번(리액티브 MongoDB 병용) 섹션과 8번(테스트)의 리액티브 MongoDB 문장을 제거한다. 편집 후 섹션 번호가 끊기지 않고 이어지도록 후속 섹션 번호를 당겨 정리한다. 또한 "JPA만" 케이스와 동일한 방식으로, 선택한 아키텍처의 `test.md`에서 MongoDB base class 행(`IntegrationTestBase`/`WebIntegrationTestBase`)과 MongoDB 통합 테스트 문단을 제거한다.
- `spring-*` 에이전트는 웹 스택(MVC/WebFlux)을 조건부로 함께 언급하므로 수정하지 않는다.

### 백엔드 스택 "Spring Boot" + 영속성 도구 "JPA" 선택 시 — 삭제
- 선택한 언어 디렉토리의 `.claude/rules/backend/spring/{java|kotlin}/repository-sql.md` (SQL-first 전용 규칙)

### 백엔드 스택 "Spring Boot" + 영속성 도구 "SQL-first" 선택 시 — 삭제 + 편집
- 선택한 언어·아키텍처의 `.claude/rules/backend/spring/{java|kotlin}/{layered|hexagonal}/repository.md`와 `.claude/rules/backend/spring/{java|kotlin}/repository-tools.md`를 삭제한다 (`repository-sql.md`가 대체한다).
- Layered면 `spring/{java|kotlin}/layered/domain.md`를 편집한다: 2번(인프라 비종속)의 `@Entity` 마커 허용·orm.xml 분리 문장을 순수 Domain 기준(영속성 애노테이션 전면 금지)으로 수정하고, 9번(JPA 영속성 매핑) 섹션을 삭제하며, 마지막 금지 패턴의 orm.xml 항목과 도입부의 SQL-first/WebFlux 안내 문장을 정리한다. 편집 후 번호와 문맥이 자연스럽게 이어지는지 다시 읽어 확인한다.
- Hexagonal이면 추가 편집이 없다 (`ports-and-adapters.md`의 `{Domain}JpaEntity` 언급은 `repository-sql.md` 2번의 대체 규정이 우선한다).
- MongoDB/QueryDSL 질문은 이 경우 묻지 않았으므로 해당 편집 케이스도 적용하지 않는다.
- `spring-*` 에이전트는 영속성 도구(JPA/SQL-first)를 조건부로 함께 언급하므로 수정하지 않는다.

### 백엔드 포함 + "NestJS" 선택 시 — 삭제
- `.claude/rules/backend/spring/`, `.claude/rules/backend/fastapi/` 전체 (`nestjs/`, `shared/`는 유지)
- `.claude/agents/spring-*.md`(spring-hexagonal-* 포함 14개), `.claude/agents/fastapi-*.md`(7개)

### 백엔드 포함 + "FastAPI" 선택 시 — 삭제
- `.claude/rules/backend/spring/`, `.claude/rules/backend/nestjs/` 전체 (`fastapi/`, `shared/`는 유지)
- `.claude/agents/spring-*.md`(spring-hexagonal-* 포함 14개), `.claude/agents/nestjs-*.md`(7개)

### 프론트엔드 미포함 시 — 삭제
- `.claude/rules/frontend/` 전체
- `.claude/agents/frontend-*.md` (frontend-vue-* 포함 13개 전부)

### 프론트엔드 포함 + Next.js 선택 시 — 삭제
- `.claude/rules/frontend/vite.md`, `.claude/rules/frontend/vue.md`
- Vue.js 전담 에이전트 6개: `.claude/agents/frontend-vue-*.md`

### 프론트엔드 포함 + Vite 선택 시 — 삭제
- `.claude/rules/frontend/nextjs.md`, `.claude/rules/frontend/vue.md`
- Vue.js 전담 에이전트 6개: `.claude/agents/frontend-vue-*.md`

### 프론트엔드 포함 + Vue.js 선택 시 — 삭제
- `.claude/rules/frontend/nextjs.md`, `.claude/rules/frontend/vite.md`
- React 계열 전제 에이전트 6개: `.claude/agents/frontend-architect.md`, `frontend-tdd-implementer.md`, `frontend-refactorer.md`, `frontend-test-author.md`, `frontend-code-reviewer.md`, `frontend-debugger.md` (`frontend-vue-*` 6개와, 프레임워크 무관인 `frontend-style-checker`는 유지)

### 백엔드 스택 "Spring Boot" + "JPA만" 선택 시 — 편집 (파일 삭제 아님)
- 언어·아키텍처 스타일 답변에 따라 `.claude/rules/backend/spring/{java|kotlin}/layered/test.md` 또는 `.claude/rules/backend/spring/{java|kotlin}/hexagonal/test.md`에서 MongoDB 관련 내용을 제거한다: base class 표에서 `IntegrationTestBase`(MongoDB Repository/Persistence Adapter 통합), `WebIntegrationTestBase`(MongoDB Controller/Web Adapter) 행을 삭제하고, MongoDB 통합 테스트 관련 문단을 제거해 JPA 전용 안내만 남긴다.
- Edit 도구로 신중하게 처리하고, 편집 후 표/문단이 자연스럽게 이어지는지 다시 읽어 확인한다.
- **`spring-*` 에이전트는 수정하지 않는다.** `spring-test-author`/`spring-hexagonal-test-author`의 base class 표에는 MongoDB 행이 남는다. 3단계 보고 시 이 사실을 사용자에게 알린다.

### 백엔드 스택 "Spring Boot" + "Specification까지만" 선택 시 — 삭제 + 편집
- 선택한 언어 디렉토리의 `.claude/rules/backend/spring/{java|kotlin}/repository-tools.md`(QueryDSL/JdbcClient/jOOQ 상세 규칙)를 삭제한다.
- 언어·아키텍처 답변에 해당하는 `repository.md`에서 "도구 선택 계층" 표의 Level 2~3 행과 `repository-tools.md` 참조 문구, "Finder/Service 계층과의 통합" 다이어그램·금지 패턴의 QueryDSL/JdbcClient/jOOQ 언급을 정리해 본문과 표가 어긋나지 않도록 한다.
- 언어·아키텍처 답변에 해당하는 `test.md`에서도 삭제된 `repository-tools.md`에 대한 참조가 남지 않게 정리한다: Layered면 `layered/test.md` 2.1절의 jOOQ SqlBuilder 문단과 5번(N+1 쿼리 카운트 검증)의 QueryDSL 언급, Hexagonal이면 `hexagonal/test.md` 5번의 `repository-tools.md` 참조 문구를 제거·조정한다. 편집 후 문단이 자연스럽게 이어지는지 다시 읽어 확인한다.
- **`spring-*` 에이전트는 수정하지 않는다.** 일부 에이전트(`spring-domain-designer` 등)는 QueryDSL/JdbcClient 티어를 계속 언급한다. 3단계 보고 시 이 사실을 사용자에게 알린다.

### 백엔드 스택 "Spring Boot" + RDB 선택 시 — 편집 (파일 삭제 아님)
- PostgreSQL 선택 시: 편집하지 않는다 (규칙의 jOOQ 방언 예시가 이미 PostgreSQL 기준이다).
- MySQL/MariaDB 선택 시: 앞선 케이스들의 삭제 처리 후 **남아 있는** 파일에 한해, 선택한 언어 디렉토리에서 jOOQ 방언 예시를 치환한다 — `repository-sql.md` 3번과 `repository-tools.md` 2.5절의 `SQLDialect.POSTGRES`(설명 문장과 `JooqConfig` 코드 예시), `layered/test.md` 2.1절의 프로덕션 방언 예시 `POSTGRES`, (WebFlux 프로젝트) `repository-r2dbc.md` 4번의 `SQLDialect.POSTGRES`를 선택한 DB의 방언 상수(`SQLDialect.MYSQL`/`SQLDialect.MARIADB`)로 바꾼다.
- 그 외 DB를 직접 입력받은 경우: jOOQ 오픈소스 방언이 존재하면(예: SQLite → `SQLDialect.SQLITE`) 동일하게 치환하고, 상용 에디션 방언이 필요한 DB(Oracle, SQL Server 등)면 치환하지 않고 3단계 보고에서 "jOOQ 방언 예시는 PostgreSQL 기준으로 남아 있으며, 선택한 DB는 jOOQ 상용 에디션 방언이 필요하다"고 안내한다.
- 편집 후 파일 내 방언 언급이 일관되게 읽히는지 다시 확인한다.
- `spring-*` 에이전트는 DB 벤더를 언급하지 않으므로 수정 대상이 없다.

### 백엔드 스택 "NestJS" + 영속성 도구(TypeORM/Prisma) 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/backend/nestjs/nestjs.md`에서 선택하지 않은 영속성 도구 관련 내용을 제거한다: 4번(영속성)의 다른 ORM 항목과 SQL-first(Kysely) 항목, 5번(Repository 도구)·6번(트랜잭션)·10번(금지 패턴)의 해당 도구 언급.
- Prisma를 선택한 경우 금지 패턴의 TypeORM 컬럼 데코레이터 항목(`EntitySchema` 사용)도 함께 제거한다.
- 편집 후 각 섹션이 선택한 도구 단일 경로로 자연스럽게 읽히는지 다시 읽어 확인한다.
- `nestjs-*` 에이전트는 영속성 도구를 조건부로 함께 언급하므로 수정하지 않는다.

### 백엔드 스택 "NestJS" + 영속성 도구 "사용 안 함(SQL-first)" 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/backend/nestjs/nestjs.md`에서 TypeORM/Prisma 관련 내용을 제거하고 SQL-first(Kysely) 경로만 남긴다: 4번(영속성)의 두 ORM 항목과 embedded 매핑 언급, 5번·6번의 ORM 도구 언급, 10번 금지 패턴의 TypeORM 컬럼 데코레이터 항목.
- 편집 후 각 섹션이 Kysely 단일 경로로 자연스럽게 읽히는지 다시 읽어 확인한다.
- `nestjs-*` 에이전트는 영속성 도구를 조건부로 함께 언급하므로 수정하지 않는다.

### 백엔드 스택 "FastAPI" + ORM 사용 여부 선택 시 — 편집 (파일 삭제 아님)
- ORM 사용 선택 시: `.claude/rules/backend/fastapi/fastapi.md`에서 SQL-first 관련 내용을 제거한다 — 1번의 `models.py` 괄호 단서, 3번의 SQL-first 항목과 도구 고정 문장, 4번·5번·10번의 SQL-first/커넥션 언급.
- SQL-first 선택 시: 반대로 ORM 경로를 제거한다 — 1번의 `models.py` 항목, 3번의 ORM 항목, 4번의 ORM 표현(`selectinload` 등), 5번의 `AsyncSession` 언급을 `AsyncConnection` 기준으로 정리.
- 편집 후 각 섹션이 선택한 경로 하나로 자연스럽게 읽히는지 다시 읽어 확인한다.
- `fastapi-*` 에이전트는 영속성 방식을 조건부로 함께 언급하므로 수정하지 않는다.

### 백엔드 스택 "FastAPI" + RDB 선택 시 — 편집 (파일 삭제 아님)
- PostgreSQL 선택 시: 편집하지 않는다 (`fastapi.md`의 드라이버 예시가 이미 PostgreSQL 기준이다).
- 그 외 선택 시: `.claude/rules/backend/fastapi/fastapi.md`의 드라이버 예시를 선택한 DB 기준으로 치환한다 — 3번의 async 드라이버 예시(`asyncpg`), 9번의 동기 드라이버 예시(`psycopg2`)와 async 드라이버 예시(`asyncpg, aiosqlite 등`)를 해당 DB의 드라이버로 바꾼다 (MySQL/MariaDB: async는 `asyncmy` 또는 `aiomysql`, 동기는 `PyMySQL`; SQLite: async는 `aiosqlite`, 동기는 표준 `sqlite3`).
- ORM 사용 여부 케이스(위)의 편집으로 이미 제거된 문장은 대상이 아니다. 남아 있는 문장에 대해서만 적용한다.
- 편집 후 문장이 자연스럽게 읽히는지 다시 확인한다.
- `fastapi-*` 에이전트는 DB 벤더를 언급하지 않으므로 수정 대상이 없다.

### 백엔드 스택 "NestJS" + 검증 도구 선택 시 — 편집 (파일 삭제 아님)
- class-validator 선택 시: `nestjs.md` 3번에서 Zod 허용 문장("Zod 스키마 기반 검증(`nestjs-zod`)도 허용하되 ... 통일한다")을 제거한다.
- Zod 선택 시: `nestjs.md` 3번을 `nestjs-zod` 기준으로 조정한다 — class-validator 기본 문장을 Zod 스키마 기반 검증으로 바꾸고, 다중 진입점 방어 항목의 `validateOrReject()` 언급을 Command 생성 시점의 Zod 스키마 `parse()` 호출로 대체한다.
- **Zod 선택 시 `nestjs-*` 에이전트는 수정하지 않는다.** `nestjs-tdd-implementer`/`nestjs-code-reviewer`/`nestjs-domain-designer`는 class-validator 전제로 작성돼 있다. 3단계 보고 시 이 사실을 사용자에게 명시적으로 알린다: "nestjs 에이전트들은 class-validator 전제입니다. Zod 기준으로 활용하려면 에이전트를 별도로 조정해야 합니다."

### 풀스택 + 백엔드 "NestJS" 선택 시 — 편집 (파일 삭제 아님)
- 백엔드와 프론트엔드가 모두 TypeScript이므로 `frontend/typescript.md`의 globs(`**/*.ts`)가 백엔드 소스에도 매칭된다. 1단계 라운드 3에서 답변받은 프론트엔드 소스 루트 경로를 `frontend/*.md`의 globs에 프리픽스로 적용한다 (예: `**/*.ts` → `apps/web/**/*.ts`, `**/*.tsx` → `apps/web/**/*.tsx`).
- 편집 후 globs가 실제 프론트엔드 파일 경로와 매칭되는지 경로 예시로 확인한다.

### 프론트엔드 "Vite" + 라우팅 라이브러리 선택 시 — 편집 (파일 삭제 아님)
- `.claude/rules/frontend/vite.md` 3번(라우팅)에서 선택하지 않은 라이브러리 항목을 제거하고, 선택한 라이브러리를 확정 문장으로 바꾼다. "둘 중 하나를 프로젝트 시작 시점에 고정한다" 문장은 선택이 끝났으므로 제거한다.
- 5번(금지 패턴)의 "라우팅 라이브러리를 프로젝트 중간에 이유 없이 교체하지 않는다"는 그대로 둔다.

## 3단계: 확인 후 실행

1. 삭제/편집 대상 전체 목록을 사용자에게 보여주고 진행 여부를 확인받는다. NestJS + Zod를 선택한 경우 "nestjs 에이전트들은 class-validator 전제" 안내를 함께 보여준다.
2. 확인되면 파일 삭제는 `git rm`으로, 내용 편집은 Edit로 수행한다.
3. 자동으로 커밋하지 않는다. 사용자가 요청할 때만 커밋한다.

## 결과 보고

- 선택된 스택 조합 요약 (영역, 백엔드 스택·언어·아키텍처·주 RDB, 프론트엔드 프레임워크 등)
- 삭제한 파일/디렉토리 목록과 편집한 파일 목록
- 해당 시 에이전트 안내문 (NestJS+Zod, JPA만, Specification까지만 선택 시의 에이전트 미수정 안내)
- 해당 시 RDB 안내문 (jOOQ 상용 에디션 방언이 필요한 DB를 선택한 경우)
- 커밋하지 않았음을 명시하고, 커밋을 원하면 요청하도록 안내

## 하지 말아야 할 것

- 사용자 확인 없이 바로 삭제/편집을 실행하지 않는다.
- 원본 템플릿 저장소에서 실행해 원본을 훼손하지 않는다(0단계 참조).
- 질문받지 않은 조합을 임의로 판단해서 처리하지 않는다.
- rules를 편집했더라도 전제가 다른 에이전트(`nestjs-*`의 class-validator 전제, `spring-*`의 MongoDB/QueryDSL 언급 등)를 임의로 고치지 않는다(별도 작업). 3단계 보고에서 안내만 한다.
