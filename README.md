# claude-code-base

Claude Code용 프로젝트 규칙(`rules`)과 서브에이전트(`agents`), 커스텀 커맨드(`commands`)를 갖춘 베이스 템플릿입니다. Kent Beck의 TDD와 Tidy First 원칙을 기반으로, 백엔드(Spring Boot/NestJS/FastAPI)와 프론트엔드(TypeScript/Next.js/Vite/Vue.js) 개발 워크플로우를 다룹니다.

## 사용 방법

1. 이 저장소를 템플릿으로 새 프로젝트를 만듭니다 (GitHub의 "Use this template" 또는 clone).
2. 새 프로젝트를 Claude Code로 엽니다.
3. **가장 먼저 `/rw:init`을 실행합니다.** 실제 프로젝트 스택(백엔드/프론트엔드/풀스택, 백엔드 스택 종류, Spring이면 언어(Java/Kotlin)·아키텍처 스타일(Layered/Hexagonal)·웹 스택(MVC/WebFlux — Java 한정, WebFlux면 영속성은 R2DBC로 고정)·영속성 도구(JPA/SQL-first)·MongoDB 사용 여부·QueryDSL/jOOQ 계획·주 RDB(PostgreSQL/MySQL 등), NestJS면 영속성 도구(TypeORM/Prisma/SQL-first)와 검증 도구(class-validator/Zod), FastAPI면 SQLAlchemy ORM 사용 여부와 주 RDB, 프론트엔드면 Next.js/Vite/Vue.js와 Vite의 라우팅 라이브러리)을 확정한 뒤, 해당하지 않는 `.claude/rules/`와 `.claude/agents/` 파일을 정리해줍니다. 기존 코드가 있는 프로젝트면 빌드 파일·의존성·디렉토리 구조를 스캔해 스택을 자동 감지하고(감지 근거는 실행 전 확인 단계에 표시), 빈 프로젝트거나 감지하지 못한 항목만 질문합니다. 그대로 다 복사해서 쓰면 안 쓰는 규칙/에이전트까지 매 세션 로드되어 불필요하게 토큰을 소모합니다.

## 구성

```
.claude/
├── CLAUDE.md              # 전체 개발 방법론 (TDD, Tidy First, 일반 행동 규칙)
├── rules/
│   ├── backend/
│   │   ├── shared/          # 스택 공통 아키텍처 원칙 (CQRS-lite, 계층 의존 방향, DDD 전술 패턴)과 REST API 규약 (rest-api.md)
│   │   ├── spring/          # Spring Boot 구현 규칙 (api-dto.md는 공통, java/·kotlin/으로 언어 분리 후 각 언어 아래 layered/·hexagonal/로 아키텍처 스타일 분리. 각 언어 레벨의 repository-tools.md(JPA용 QueryDSL/JdbcClient/jOOQ 상세)와 repository-sql.md(SQL-first, ORM 미사용)는 아키텍처 공통이며 영속성 도구 선택에 따라 둘 중 하나만 유지. java/의 webflux.md·repository-r2dbc.md는 WebFlux(리액티브, Java 전용) 선택 시에만 유지하며 이 경우 JPA/SQL-first 영속성 규칙을 대체, repository-reactive-mongo.md는 WebFlux + 리액티브 MongoDB 병용 시에만 유지)
│   │   ├── nestjs/          # NestJS 구현 규칙
│   │   └── fastapi/         # FastAPI 구현 규칙
│   └── frontend/           # TypeScript/Next.js/Vite/Vue.js 규칙 (typescript.md는 공통. nextjs.md/vite.md/vue.md 중 선택한 프레임워크만 유지. vite-routing-reactrouter.md·vite-routing-tanstack.md는 Vite 전용 라우팅 규칙으로, Vite 선택 시 라우팅 라이브러리에 맞는 하나만 유지하고 Next.js/Vue.js 선택 시 둘 다 삭제)
├── agents/                 # 워크플로우별 서브에이전트, 스택별로 분리 (spring-*/nestjs-*/fastapi-*/frontend-*). Spring은 Layered 전제인 spring-*와 Hexagonal 전담인 spring-hexagonal-*을 아키텍처 스타일별로, 프론트엔드는 React 계열(Next.js/Vite) 전제인 frontend-*와 Vue.js 전담인 frontend-vue-*를 프레임워크별로 제공
└── commands/rw/             # 커스텀 슬래시 커맨드 (init, git, plan, prd, tdd)
```

## 계획 기반 작업 흐름 (plan.md)

1. **`/rw:plan:plan <PRD 파일 경로 또는 기능 설명>`** — 프로젝트 루트에 `plan.md`를 생성합니다. 기능 개요, 구현 목표, 설계, Phase별 테스트 체크리스트로 구성됩니다. `plan.md`가 이미 있으면 실행되지 않고 먼저 `plan_move`로 아카이빙하라고 안내합니다.
2. **`/rw:tdd:go`** — `plan.md`에서 체크 안 된 테스트를 하나 찾아 Red(실패 확인) → Green(최소 구현) 순으로 구현하고, 통과하면 해당 항목에 체크합니다. 모든 테스트가 끝날 때까지 반복 실행합니다.
3. **`/rw:plan:plan_move`** — 완료된(또는 중단된) `plan.md`를 요약 키워드가 담긴 파일명(`plan_yyyyMMdd_요약키워드.md`)으로 `plans/` 디렉토리에 아카이빙합니다. 이후 `/rw:plan:plan`으로 새 계획을 시작할 수 있습니다.

## 다른 도구로 이식

Codex CLI, Gemini CLI 등 다른 코딩 에이전트로 옮기는 방법은 아직 정리되지 않았습니다. 두 도구 모두 서브에이전트/커맨드 개념은 있지만 형식이 다르고(Gemini CLI는 Claude Code와 형식이 유사해 이식이 비교적 쉬움, Codex CLI는 TOML 재작성이 필요), `globs`/`alwaysApply` 기반 조건부 규칙 로딩은 두 도구 모두 네이티브로 지원하지 않습니다.
