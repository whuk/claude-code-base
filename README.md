# claude-code-base

Claude Code용 프로젝트 규칙(`rules`), 서브에이전트(`agents`), 커스텀 커맨드(`commands`)를 갖춘 베이스 템플릿입니다.
Kent Beck의 TDD와 Tidy First 원칙을 기반으로, 백엔드(Spring Boot / NestJS / FastAPI)와 프론트엔드(Next.js / Vite / Vue.js) 개발 워크플로우를 다룹니다.

## 사용 방법

1. 이 저장소를 템플릿으로 새 프로젝트를 만듭니다 (GitHub의 "Use this template" 또는 clone).
2. 새 프로젝트를 Claude Code로 엽니다.
3. **가장 먼저 `/rw:init`을 실행합니다.**

`/rw:init`은 실제 프로젝트 스택(영역, 백엔드 스택, 언어, 아키텍처 스타일, 영속성 도구, 프론트엔드 프레임워크 등)을
확정한 뒤, 해당하지 않는 `.claude/rules/`와 `.claude/agents/` 파일을 정리합니다.

- 기존 코드가 있으면 빌드 파일·의존성·디렉토리 구조를 스캔해 스택을 자동 감지하고, 감지하지 못한 항목만 질문합니다.
- 감지 근거는 실행 전 확인 단계에 표시됩니다.
- **건너뛰고 전부 복사해 쓰면, 사용하지 않는 규칙과 에이전트까지 매 세션 로드되어 토큰을 낭비합니다.**

스택별 선택지와 삭제·rename 규칙의 상세는 `.claude/commands/rw/init.md`에 있습니다.

### 이미 초기화한 프로젝트를 템플릿 업데이트와 동기화하기

템플릿의 선별 규칙이 갱신되면, 구버전으로 초기화한 프로젝트에는 이제 불필요해진 규칙 파일이 남아 매 세션 로드될 수 있습니다.
`/rw:init` 재실행은 이미 삭제된 파일을 다시 지우려다 실패할 수 있으므로, 남은 파일을 수동으로 제거하는 편이 깔끔합니다.

```bash
# 예: Next.js/Vue.js 프로젝트에 남은 Vite 전용 라우팅 규칙 제거 (커밋 전이면 rm)
git rm .claude/rules/frontend/vite-routing-reactrouter.md \
       .claude/rules/frontend/vite-routing-tanstack.md
```

## 구성

```
.claude/
├── CLAUDE.md              # 개발 방법론 (TDD, Tidy First, 일반 행동 규칙)
├── STYLE_GUIDE.md         # .claude 문서 작성 포맷
├── rules/
│   ├── code-review.md     # 스택 무관 코드 리뷰 기준
│   ├── backend/
│   │   ├── shared/        # 공통 아키텍처 원칙, REST API 규약
│   │   ├── spring/        # Spring Boot
│   │   ├── nestjs/        # NestJS
│   │   └── fastapi/       # FastAPI
│   └── frontend/          # TypeScript 공통 + Next.js / Vite / Vue.js
├── agents/                # 워크플로우별 서브에이전트 (스택별 분리)
└── commands/rw/           # 커스텀 슬래시 커맨드 (init, git, plan, prd, tdd)
```

`/rw:init`이 선택에 따라 남기는 규칙 파일:

| 선택 축 | 남는 것 |
|---|---|
| Spring 언어 · 아키텍처 | `spring/java/` 또는 `spring/kotlin/` → 그 아래 `layered/` 또는 `hexagonal/` |
| 영속성 도구 | JPA면 `repository-tools.md`, SQL-first면 `repository-sql.md` (둘 중 하나) |
| 웹 스택 (Java 한정) | WebFlux면 `webflux.md`·`repository-r2dbc.md`가 JPA/SQL-first 규칙을 대체 |
| 프론트엔드 | `nextjs.md` / `vite.md` / `vue.md` 중 하나 (Vite면 라우팅 규칙도 하나만) |
| 스택 무관 | `code-review.md`와 `code-reviewer` 에이전트는 항상 유지 |

에이전트도 같은 축으로 나뉩니다 — Spring은 Layered용 `spring-*`와 Hexagonal용 `spring-hexagonal-*`,
프론트엔드는 React 계열(Next.js/Vite)용 `frontend-*`와 Vue.js용 `frontend-vue-*`를 제공합니다.

## 계획 기반 작업 흐름 (plan.md)

| 커맨드 | 역할 |
|---|---|
| `/rw:plan:plan <PRD 경로 또는 기능 설명>` | 프로젝트 루트에 `plan.md` 생성 (기능 개요, 구현 목표, 설계, Phase별 테스트 체크리스트) |
| `/rw:tdd:go` | `plan.md`의 미완료 테스트를 하나씩 Red → Green으로 구현하고 체크 |
| `/rw:plan:plan_move` | 완료·중단된 `plan.md`를 `plans/plan_yyyyMMdd_요약키워드.md`로 아카이빙 |

`plan.md`가 이미 있으면 `/rw:plan:plan`은 실행되지 않고, 먼저 `plan_move`로 아카이빙하라고 안내합니다.

## PR 리뷰 흐름

1. **`/rw:git:commit-and-push`** — 커밋과 push까지만 수행합니다. PR 생성은 `/commit-commands:commit-push-pr` 또는 `gh pr create`를 사용합니다.
2. **`/rw:git:pr-review [PR번호]`** — `code-reviewer` 에이전트(+ 저장소에 남아 있는 스택 전담 리뷰어)가 변경분을 리뷰하고, 심각도 등급(Blocker/Major/Minor/Nit)이 붙은 결과를 PR 코멘트로 남깁니다. 기준은 `rules/code-review.md`입니다.
3. **사람이 리뷰 결과를 확인하고 머지 여부를 판단합니다.** Blocker/Major가 있으면 수정한 뒤 2번을 다시 실행합니다.
4. **`/rw:git:squash-merge-pull [PR번호]`** — squash merge 후 로컬 기본 브랜치를 동기화합니다.

> 커맨드는 일반 코멘트만 남기고 PR의 리뷰 상태를 바꾸지 않으며(`--approve`/`--request-changes` 미실행), 발견한 문제를 대신 수정하지도 않습니다.
> 별도 리뷰어가 있으면 Approve까지 받고, 작성자 혼자인 저장소는 GitHub가 자기 PR 승인을 허용하지 않으므로 코멘트 확인이 그 절차를 갈음합니다.

## 다른 도구로 이식

Codex CLI, Gemini CLI 등 다른 코딩 에이전트로 옮기는 방법은 아직 정리되지 않았습니다.

- **Gemini CLI** — 형식이 Claude Code와 유사해 이식이 비교적 쉽습니다.
- **Codex CLI** — TOML로 재작성이 필요합니다.
- 두 도구 모두 `globs`/`alwaysApply` 기반 조건부 규칙 로딩을 네이티브로 지원하지 않습니다.
