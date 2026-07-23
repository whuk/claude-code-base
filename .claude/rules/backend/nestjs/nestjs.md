---
description: NestJS 백엔드 고유 컨벤션 (backend/shared/architecture.md 전제)
globs: "**/*.controller.ts,**/*.service.ts,**/*.module.ts,**/*.entity.ts,**/*.repository.ts"
---

# NestJS 규칙

`shared/architecture.md`의 공통 원칙과 `shared/rest-api.md`의 REST 설계 규약(URI, 상태 코드, 페이지네이션, 에러 형식)을 전제로, NestJS 고유 구현 방법만 다룬다. NestJS는 애초에 Angular/Spring 스타일 구조(데코레이터, DI, 모듈)에서 설계됐기 때문에, Java/Spring 규칙(`spring/`)과 사상을 거의 그대로 공유한다.

이 프로젝트가 Spring Boot나 FastAPI를 채택했다면 이 파일은 적용 대상이 아니다. 백엔드 스택(Spring/NestJS/FastAPI)은 한 프로젝트에서 하나만 사용하므로, 실제로 채택하지 않은 스택의 규칙 파일은 프로젝트에서 제외한다 (`spring/`, `fastapi.md` 참조).

## 1. 모듈/계층 구조

- 기능 단위로 `Module`을 나눈다. 하나의 `Module`이 관련된 `Controller`, `Service`(Finder/Write), `Repository` 프로바이더를 묶는다.
- 계층 순서(`shared/architecture.md` 3번): `Controller` → `Service` → `Repository` → `Domain`. `Controller`가 `Repository`나 `Domain`을 직접 참조하지 않는다.
- `Domain`(순수 비즈니스 로직 클래스)은 `@Injectable()`, `@Entity()` 외의 프레임워크 데코레이터에 의존하지 않는다.

## 2. Finder/Service 분리

- 조회 전용 `{Domain}Finder`(`@Injectable()`)와 상태 변경 전용 `{Domain}Service`(`@Injectable()`)를 별도 프로바이더로 분리한다.
- Service가 조회가 필요하면 같은 모듈의 Finder를 생성자 주입받아 사용할 수 있다.

## 3. Command/Query와 검증

- Controller의 입력 DTO와 Service의 Command/Query는 별도 클래스로 분리한다(Web DTO를 Service로 그대로 넘기지 않는다, `shared/architecture.md` 1-2번).
- 검증은 `class-validator` 데코레이터(`@IsString()`, `@IsEmail()`, `@ValidateNested()` 등)를 기본으로 한다. Zod 스키마 기반 검증(`nestjs-zod`)도 허용하되 한 프로젝트 내에서는 하나로 통일한다.
- **다중 진입점 방어**(`shared/architecture.md` 5번): Command/Query 클래스에도 Controller DTO와 동일한 검증 데코레이터를 붙인다. Service 메서드 진입점에서 `ValidationPipe`를 명시적으로 적용하거나, Command 생성 시점에 `class-validator`의 `validateOrReject()`를 직접 호출해 HTTP 경로를 거치지 않는 호출(메시지 컨슈머, 배치, 다른 서비스의 직접 호출)도 방어한다.
- 연관 파라미터 4개 이상은 Value Object(별도 클래스 또는 중첩 DTO)로 그룹화한다(`shared/architecture.md` 4번).

## 4. 영속성 (ORM별 Domain 매핑)

- **TypeORM 사용 시**: Domain 클래스가 엔티티 역할을 겸한다. 데코레이터 대신 `EntitySchema`(TypeORM의 코드-외부 매핑 정의)를 사용해 컬럼/관계 매핑을 Domain 클래스 밖으로 분리한다. 이는 Spring 규칙의 `orm.xml`(`spring/domain.md` 9번)과 동일한 철학이다.
- **Prisma 사용 시**: Prisma는 Domain 클래스를 직접 엔티티로 매핑할 수 없다(schema.prisma에서 타입이 생성되는 구조). 이 경우 Prisma가 생성한 타입과 Domain 객체 간 변환은 Repository 구현체가 전담한다. Domain 클래스가 Prisma 타입을 직접 참조하지 않는다.
- Value Object는 (TypeORM) `EntitySchema`의 embedded 매핑 또는 (Prisma) Repository의 변환 로직에서 처리한다.

## 5. Repository 도구 선택 (Escalation Ladder 적용)

- 단순 조회(정적 조건 1-2개): TypeORM `Repository.find()`/Prisma `findMany()` 기본 메서드.
- 동적 검색 조건 조합: TypeORM `QueryBuilder` 또는 Prisma의 동적 `where` 객체 조합. 조건별 빌더 함수를 도메인 전용 모듈에 그룹화한다(Spring의 Specification 패턴과 동일한 사상).
- 복잡한 조인/N+1 방지: TypeORM `relations`/`leftJoinAndSelect`, Prisma `include`. 페이지네이션과 fetch join(관계 포함 로딩)을 동시에 쓰지 않는다(인메모리 페이지네이션 경고).
- 대량 벌크/집계/네이티브 SQL: 원시 쿼리(`query()`, Prisma `$queryRaw`)는 측정된 성능 문제가 있을 때만 예외적으로 허용한다.

## 6. 트랜잭션

- Service의 쓰기 메서드는 트랜잭션 경계로 감싼다. TypeORM은 `DataSource.transaction()` 또는 `QueryRunner`, Prisma는 `$transaction()`을 사용한다.
- Finder(조회 전용)는 트랜잭션 경계를 명시적으로 열지 않는다.
- 클래스 전체에 선언적으로 트랜잭션을 적용하는 Spring 방식과 달리 NestJS는 메서드 단위로 트랜잭션을 명시해야 하므로, 트랜잭션이 필요한 메서드를 주석이 아니라 헬퍼 함수/데코레이터로 일관되게 표시한다.

## 7. API 스펙

- 가능하면 `openapi.yaml`을 먼저 정의하고 코드/DTO를 생성하는 spec-first를 유지한다(`shared/architecture.md`의 단일 소스 원칙과 `spring/api-dto.md`의 사상을 그대로 따른다). 스펙 작성 규약(스키마 명명, `$ref`, `operationId`, 제약조건 명시)은 `shared/rest-api.md` 8번을 따른다.
- 이 codegen 경로(예: openapi-generator의 TypeScript/NestJS 대상 템플릿)가 팀 환경에서 검증되지 않았다면, `@nestjs/swagger` 데코레이터 기반 code-first로 시작하는 것을 예외적으로 허용한다. 이 경우 CI에서 생성된 OpenAPI 문서를 아티팩트로 남겨 프론트엔드와의 계약이 암묵적으로 깨지지 않는지 추적한다.

## 8. 테스트

- 단위 테스트: Jest. `@nestjs/testing`의 `Test.createTestingModule()`로 필요한 프로바이더만 로드한다(전체 애플리케이션 컨텍스트를 올리지 않는다).
- Service/Finder 단위 테스트에서 Repository 등 하위 의존성은 custom provider(`{ provide: OrderRepository, useValue: mock }`)로 대체한다. 실제 DB 접근 없이 오케스트레이션 로직만 검증하고, 실제 영속성 동작(매핑, 쿼리 조합)은 통합 테스트에서 검증한다.
- 통합/E2E 테스트: Supertest로 HTTP 요청을 검증한다.
- `Thread.sleep` 상당의 시간 기반 동기화(임의 `setTimeout` 대기)를 사용하지 않는다. 결정적 데이터는 Fixture/Factory로 생성한다.

## 9. 에러 응답 (RFC 9457)

- 에러 응답은 `shared/rest-api.md` 4번의 Problem Details 형식을 따른다. 전역 Exception Filter(`APP_FILTER`로 등록)에서 매핑하고, Controller에서 에러 응답 객체를 직접 조립하지 않는다.
- `ValidationPipe` 검증 실패(`BadRequestException`)는 400 + Problem Details로 변환하고, 필드별 오류를 `errors` 배열로 포함한다. Service 진입점 검증(3번 다중 진입점 방어)에서 발생한 검증 예외도 같은 필터에서 400으로 매핑한다.
- 도메인 예외(비즈니스 규칙 위반)는 공통 도메인 예외 클래스를 기준으로 같은 필터에서 422 Problem Details로 매핑한다. Domain/Service 계층에서 `HttpException` 계열(NestJS 웹 계층 타입)을 직접 던지지 않는다 — 안쪽 계층이 바깥 계층 타입을 참조하는 역방향 의존이다(`shared/architecture.md` 3번).

## 10. 금지 패턴

- Controller DTO를 Service 메서드 파라미터로 그대로 사용하지 않는다.
- Domain 클래스에 TypeORM 컬럼 데코레이터(`@Column`, `@OneToMany` 등)를 직접 붙이지 않는다(`EntitySchema` 사용).
- Finder 프로바이더에 상태 변경 메서드를 포함하지 않는다.
- 동적 검색 조건을 원시 SQL/QueryBuilder 문자열로 나열하지 않는다(5번 기준 도구 사용).
- Domain/Service 계층에서 `HttpException` 계열을 직접 던지지 않는다(9번).
