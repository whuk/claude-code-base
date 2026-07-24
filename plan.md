# 기능 개요

`/rw:init`이 현재 남기는 rules 파일의 **본문을 Edit로 수정**하는 12개 케이스를 없앤다. 대신 상호배타적 내용 갈래를 **미리 별도 파일로 분리**해두고, `/rw:init`은 확정된 스택에 맞지 않는 파일을 **삭제(또는 정규 이름으로 rename)만** 하도록 재설계한다. 값 치환/경로 주입처럼 분리로 풀 수 없는 케이스(RDB 방언·드라이버, 풀스택 glob)는 편집 자체를 제거하고 예시를 기본값으로 고정한 뒤 사용자에게 보고만 한다.

목표는 "존재하는 rules/agents 파일은 수정 없이 있는 그대로 내려주기"이며, `/rw:init`은 순수 선별(삭제) 스킬이 된다. worktree는 원래 사용하지 않으므로 대상 없음.

## 구현 목표

- `/rw:init`이 어떤 rules 파일의 **본문도 Edit하지 않는다** (rename·삭제만 허용).
- 현재 12개 편집 케이스 중 상호배타적 내용 갈래(A그룹)는 파일 분리로 해소한다.
- 값 치환/경로 주입 케이스(B그룹: jOOQ 방언, FastAPI 드라이버, 풀스택 glob)는 편집을 제거하고 예시를 PostgreSQL 등 기본값으로 고정한 뒤 보고만 한다.
- 분리로 생긴 파일 간 상호참조(`domain.md 9번` 등 파일명 참조)가 재구성 후에도 정확히 해소된다.
- 각 스택 조합에서 남는 파일 집합이 재구성 전과 동일한 규칙 내용을 커버한다(내용 누락·중복 없음).
- `CLAUDE.md` 1번의 rw:init 설명, agents 관련 안내가 새 동작과 일치한다.

## 설계

### 현재 편집 케이스 분류 (init.md 3단계)

**A그룹 — 파일 분리로 해소 (상호배타적 내용 갈래)**
1. Layered `domain.md`: JPA(orm.xml, 2·9번) ↔ 순수 Domain(SQL-first·R2DBC) — java+kotlin
2. `test.md`: JPA-only ↔ MongoDB 포함 — layered/hexagonal × java+kotlin
3. `repository.md`: Specification까지만 ↔ QueryDSL/jOOQ 포함 — layered/hexagonal × java+kotlin (`repository-tools.md`와 연동)
4. NestJS `nestjs.md`: 영속성(TypeORM/Prisma/SQL-first)
5. NestJS `nestjs.md`: 검증(class-validator/Zod)
6. FastAPI `fastapi.md`: 영속성(ORM/SQL-first)
7. Vite `vite.md`: 라우팅(TanStack/React Router)

**B그룹 — 편집 제거 + 보고만 (분리 불가: 값 치환·경로 주입)**
8. Spring jOOQ 방언(`SQLDialect.POSTGRES`→MYSQL 등)
9. FastAPI 드라이버(`asyncpg`→asyncmy 등)
10. 풀스택 NestJS frontend globs(`**/*.ts`→`apps/web/**/*.ts`)

### 분리 방식 원칙

- **정규 파일명 유지 + 변형 파일 공존**: 다른 rules/agents가 참조하는 파일명(`domain.md`, `repository.md`, `nestjs.md`, `fastapi.md`, `vite.md`, `test.md`)은 유지한다. 변형은 `-접미사` 파일로 둔다.
- **rw:init의 선택 동작**: 해당 스택에서 (a) 불필요한 변형 파일을 `git rm`, (b) 필요한 변형이 정규 이름이 아니면 `git mv`로 정규 이름에 맞춘다. **본문 Edit는 없다.** rename은 내용을 바꾸지 않으므로 "있는 그대로" 원칙에 부합한다.
- **중복 최소화**: 공통 섹션이 대부분이고 일부만 다른 파일(domain.md 등)은 통짜 복제 대신, 갈래가 갈리는 섹션만 별도 조각으로 빼는 것을 우선 검토한다. 조각화가 참조를 과도하게 늘리면 통짜 변형 2개 유지로 절충한다(설계 시 파일별로 판단).

### B그룹 처리 방식 (사용자 확정)

- 예시는 **PostgreSQL(jOOQ) / asyncpg(FastAPI)** 기준으로 고정하고 편집하지 않는다.
- `/rw:init`은 선택한 RDB를 **결과 보고에만** 표기하고, 방언 상수·드라이버는 사용자가 직접 교체하도록 안내한다. RDB 질문은 보고·컨텍스트 용도로 유지한다.
- 풀스택 NestJS glob은 `**/*.ts` 원본 그대로 두고, "frontend rules globs가 백엔드 TS에도 매칭될 수 있으니 필요 시 직접 좁히라"는 안내만 보고에 추가한다.

## 작업 계획

### Phase 1: B그룹 — 편집 제거 (RDB·glob)

- [x] init.md에서 "Spring Boot + RDB 선택 시 — 편집" 섹션을 **삭제 없는 보고 전용**으로 재작성하고, jOOQ 방언 치환 지시를 제거한다 → 검증: 해당 섹션에 `SQLDialect`/`git mv`/`Edit` 언급이 없고, 4단계·결과보고에 "방언 수동 교체 안내" 항목이 있음
- [x] init.md에서 "FastAPI + RDB 선택 시 — 편집" 섹션을 보고 전용으로 재작성하고 드라이버 치환 지시를 제거한다 → 검증: 해당 섹션에 `asyncpg`/드라이버 치환/Edit 언급이 없음
- [x] init.md에서 "풀스택 + 백엔드 NestJS 선택 시 — 편집(globs)" 섹션을 보고 전용 안내로 재작성한다 → 검증: globs 프리픽스 Edit 지시가 사라지고 안내 문구만 남음
- [x] 라운드 3의 RDB 질문 목적 설명을 "파일 편집 근거"에서 "보고·수동 교체 기준"으로 수정한다 → 검증: 질문 설명에 편집을 전제한 문구가 없음

### Phase 2: A그룹 분리 — Spring (domain / test / repository)

- [x] `spring/{java,kotlin}/layered/domain.md`의 순수 Domain 변형을 별도 파일(예: `domain-pure.md`)로 만든다. JPA용 `domain.md`는 현행 유지 → 검증: 두 파일이 각각 JPA(orm.xml 조항 포함)/순수(조항 없음)로 완결되게 읽힘. domain.md/domain-pure.md 도입부를 선택 동작(둘 중 하나만 남김)으로 갱신
- [x] `spring/{java,kotlin}/{layered,hexagonal}/test.md`에서 MongoDB 내용을 `test-mongodb.md`(추가분)로 분리하고, `test.md`는 JPA-only로 완결시킨다 → 검증: `test.md`에 MongoDB base class 행/문단이 없고(정밀 grep 통과), `test-mongodb.md`만으로 MongoDB 추가 규칙이 이해됨. test.md는 test-mongodb.md를 참조하지 않음(삭제 시 dangling 방지)
- [x] `spring/{java,kotlin}/{layered,hexagonal}/repository.md`를 Level 0~1로 완결시키고 상위 티어 컨텍스트는 `repository-tools.md`가 보유하게 한다 → 검증: repository.md는 `repository-tools.md`를 참조하지 않고(참조 방향 tools→repository 단방향), Level 2~3 표 행이 없음. 상위 도구 이름(QueryDSL/jOOQ)은 에스컬레이션 경로 안내로만 남기고 파일 참조는 두지 않음
- [x] 위 분리로 깨진 상호참조를 정적으로 갱신한다 → 검증: 남게 될 각 조합에서 참조 파일명이 실제 존재 파일과 일치. `repository-tools.md` 도입부(Level 2~3 정의), `repository-reactive-mongo.md` 4번(MongoDB base class → `test-mongodb.md`) 갱신. 기존부터 존재하던 `layer-communication-rules.md`의 `domain.md 9번` 참조는 이번 분할이 새로 깨뜨린 것이 아니므로 Phase 5에서 종합 점검

### Phase 3: A그룹 분리 — NestJS / FastAPI / Vite

- [x] `nestjs.md`의 영속성 섹션(4·5·6·10번 해당 부분)을 `nestjs-persistence-{typeorm,prisma,sqlfirst}.md`로 분리하고 `nestjs.md`는 영속성-무관 핵심으로 완결시킨다 → 검증: 각 영속성 파일 단독으로 해당 도구 경로가 완결되고, `nestjs.md`에 특정 ORM 종속 문장이 없음
- [x] `nestjs.md`의 검증 섹션(3번)을 `nestjs-validation-{classvalidator,zod}.md`로 분리한다 → 검증: 두 파일이 각각 완결되고 `nestjs.md`에 검증 도구 선택 잔여물이 없음
- [x] `fastapi.md`의 영속성 갈래(ORM/SQL-first)를 `fastapi-persistence-{orm,sqlfirst}.md`로 분리한다 → 검증: 각 파일 단독 완결, `fastapi.md`에 미선택 경로 문장 없음
- [x] `vite.md`의 라우팅 섹션(3번)을 `vite-routing-{tanstack,reactrouter}.md`로 분리한다 → 검증: 두 파일 각각 완결, `vite.md`에 미선택 라이브러리 문장 없음
- [x] 각 분리 파일에 올바른 frontmatter(글로벌 glob/description)를 부여해 템플릿 상태에서 의도대로 로드되게 한다 → 검증: 분리 파일 frontmatter가 원본 파일 규약과 일치

### Phase 4: init.md 3단계 재작성 (편집 → 삭제/rename)

- [x] "Spring WebFlux/SQL-first + Layered domain 편집" 케이스를 `domain.md` 삭제 + `domain-pure.md`→`domain.md` rename으로 교체한다 → 검증: 해당 섹션에 domain.md 본문 Edit 지시가 없음
- [x] "JPA만 / MongoDB" 케이스를 `test-mongodb.md` 유지/삭제 선택으로 교체한다 (편집 제거) → 검증: test.md Edit 지시 없음
- [x] "Specification까지만" 케이스를 `repository-tools.md` 삭제만으로 교체한다 (repository.md·test.md 편집 제거) → 검증: repository.md/test.md Edit 지시 없음
- [x] NestJS 영속성·검증 케이스를 해당 분리 파일 선택 삭제로 교체한다 → 검증: nestjs.md Edit 지시 없음
- [x] FastAPI 영속성 케이스를 분리 파일 선택 삭제로 교체한다 → 검증: fastapi.md Edit 지시 없음
- [x] Vite 라우팅 케이스를 분리 파일 선택 삭제로 교체한다 → 검증: vite.md Edit 지시 없음
- [x] init.md 전체에서 `Edit`로 rules 본문을 수정하라는 지시가 하나도 없음을 확인한다 → 검증: 문서 내 "편집 (파일 삭제 아님)"/"삭제 + 편집" 표현이 남지 않고, 4단계 실행 지시가 `git rm`/`git mv`만 사용

### Phase 5: 문서 동기화 및 조합 검증

- [ ] `CLAUDE.md` 1번의 rw:init 설명에서 편집을 전제한 문구(RDB가 편집으로 이어진다는 취지 등)를 새 동작에 맞게 수정한다 → 검증: 설명이 "선별 삭제 + 분리 파일 선택 + RDB 보고" 동작과 일치
- [ ] init.md 4단계/결과 보고를 갱신한다: rename 수행 명시, RDB 수동 교체 안내, 풀스택 glob 안내, 분리 파일 목록 반영 → 검증: 보고 항목이 새 처리와 일치
- [ ] 대표 스택 조합(Java/Layered/SQL-first, Java/WebFlux, Kotlin/Hexagonal/JPA+Mongo, NestJS/Prisma/Zod, FastAPI/SQL-first, Vite/React Router)별로 남는 파일 집합을 손으로 시뮬레이션해 내용 누락·잔여 참조가 없는지 점검한다 → 검증: 각 조합에서 남는 파일만으로 규칙이 완결되고 죽은 참조가 없음
- [ ] agents 파일은 이번 작업에서 수정하지 않음을 재확인하고, 기존 "에이전트 미수정 안내"(NestJS+Zod 등)가 여전히 유효한지 확인한다 → 검증: agents/ 변경 0건, 관련 안내 문구 유지
