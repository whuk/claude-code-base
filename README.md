# claude-code-base

Claude Code용 프로젝트 규칙(`rules`)과 서브에이전트(`agents`), 커스텀 커맨드(`commands`)를 갖춘 베이스 템플릿입니다. Kent Beck의 TDD와 Tidy First 원칙을 기반으로, 백엔드(Spring Boot/NestJS/FastAPI)와 프론트엔드(TypeScript/Next.js/Vite) 개발 워크플로우를 다룹니다.

## 사용 방법

1. 이 저장소를 템플릿으로 새 프로젝트를 만듭니다 (GitHub의 "Use this template" 또는 clone).
2. 새 프로젝트를 Claude Code로 엽니다.
3. **가장 먼저 `/rw:init`을 실행합니다.** 실제 프로젝트 스택(백엔드/프론트엔드/풀스택, 백엔드 스택 종류, Next.js/Vite, MongoDB 사용 여부, QueryDSL/jOOQ 계획)에 대해 질문한 뒤, 해당하지 않는 `.claude/rules/`와 `.claude/agents/` 파일을 정리해줍니다. 그대로 다 복사해서 쓰면 안 쓰는 규칙/에이전트까지 매 세션 로드되어 불필요하게 토큰을 소모합니다.

## 구성

```
.claude/
├── CLAUDE.md              # 전체 개발 방법론 (TDD, Tidy First, 일반 행동 규칙)
├── rules/
│   ├── backend/
│   │   ├── shared/          # 스택 공통 아키텍처 원칙 (CQRS-lite, 계층 의존 방향, DDD 전술 패턴)
│   │   ├── spring/          # Java/Spring Boot 구현 규칙 (api-dto.md, rest-api.md는 공통, layered/·hexagonal/로 아키텍처 스타일 분리)
│   │   ├── nestjs/          # NestJS 구현 규칙
│   │   └── fastapi/         # FastAPI 구현 규칙
│   └── frontend/           # TypeScript/Next.js/Vite 규칙
├── agents/                 # 워크플로우별 서브에이전트, 스택별로 분리 (spring-*/nestjs-*/fastapi-*/frontend-*). spring-*는 Layered 아키텍처 전제이며 Hexagonal 전담 에이전트는 아직 없음
└── commands/rw/             # 커스텀 슬래시 커맨드 (init, git, plan, prd, tdd)
```

## 다른 도구로 이식

Codex CLI, Gemini CLI 등 다른 코딩 에이전트로 옮기는 방법은 아직 정리되지 않았습니다. 두 도구 모두 서브에이전트/커맨드 개념은 있지만 형식이 다르고(Gemini CLI는 Claude Code와 형식이 유사해 이식이 비교적 쉬움, Codex CLI는 TOML 재작성이 필요), `globs`/`alwaysApply` 기반 조건부 규칙 로딩은 두 도구 모두 네이티브로 지원하지 않습니다.
