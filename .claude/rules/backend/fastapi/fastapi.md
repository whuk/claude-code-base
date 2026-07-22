---
description: FastAPI 백엔드 고유 컨벤션 (backend/shared/architecture.md 전제, DDD 강제 수준은 완화)
globs: "**/routers/**,**/schemas/**,**/*_service.py,**/*_repository.py"
---

# FastAPI 규칙

`shared/architecture.md`의 공통 원칙을 전제로 하되, Python/FastAPI 생태계 관례에 맞게 무게를 덜어낸다. FastAPI는 가볍고 명시적인 스타일을 지향하므로, Aggregate Root·Specification 패턴 같은 Java 스타일 DDD 장치를 강제하지 않는다. **Rich Domain 원칙(`shared/architecture.md` 6번)은 권장이지 필수가 아니다** — 도메인 로직이 단순하면 트랜잭션 스크립트 스타일(라우터 → 서비스 함수 → ORM)도 허용한다.

## 1. 프로젝트 구조

- 기능(도메인) 단위로 패키지를 나눈다: `{feature}/router.py`, `{feature}/schemas.py`, `{feature}/service.py`, `{feature}/repository.py`, `{feature}/models.py`(ORM).
- 클래스 기반 Finder/Service 분리가 과할 정도로 단순한 기능이면, 모듈 레벨 함수로 조회/변경을 나눠도 된다. 다만 한 함수가 조회와 변경을 동시에 하지는 않는다(`shared/architecture.md` 7번).

## 2. Command/Query와 Pydantic

- Pydantic 모델이 Command/Query 객체이자 검증 계층을 겸한다. Java의 Bean Validation처럼 별도 애노테이션을 붙일 필요 없이, Pydantic 필드 타입과 `Field(...)` 제약(`min_length`, `pattern`, `gt` 등)이 곧 검증 규칙이다.
- **다중 진입점 방어가 사실상 기본 제공된다**: Pydantic 모델은 인스턴스화 시점에 항상 검증되므로(Pydantic v2 기준), Command 객체를 어느 경로(HTTP 라우터, 백그라운드 태스크, 메시지 컨슈머)로 생성하든 동일하게 검증된다. Java/NestJS처럼 별도 검증 트리거를 신경 쓸 필요가 없다.
- Router 입력 스키마(`schemas.py`)와 Service Command는 원칙적으로 분리하되, 단순 CRUD처럼 둘이 완전히 동일한 형태면 하나로 합쳐도 된다(`shared/architecture.md` 4번의 "연관 파라미터 그룹화" 취지를 해치지 않는 선에서 실용적으로 판단).

## 3. Domain과 ORM 매핑

- 도메인 로직이 단순하면 Pydantic 모델(또는 `dataclass`)에 메서드를 붙여 그대로 Domain으로 쓴다. 복잡한 불변 조건이 있는 경우에만 SQLAlchemy ORM 모델과 분리된 순수 Domain 클래스를 둔다.
- SQLAlchemy 사용 시 ORM 모델(`models.py`)과 Domain을 분리했다면, 변환 책임은 Repository가 전담한다. Domain이 SQLAlchemy `Mapped`/`Column`을 직접 참조하지 않는다.
- Value Object는 Pydantic `BaseModel`(`frozen=True`)이나 `dataclass(frozen=True)`로 표현한다.

## 4. Repository 도구 선택 (Escalation Ladder 적용)

- 단순 조회: SQLAlchemy ORM의 기본 쿼리(`select(Model).where(...)`).
- 동적 검색 조건 조합: 조건별 함수를 조합해 `select` 문에 `.where()`를 체이닝한다. 조건 조합 로직을 라우터/서비스가 아닌 Repository 모듈에 둔다.
- 복잡한 조인/N+1 방지: `selectinload`/`joinedload`를 명시적으로 사용한다. 관계 로딩과 페이지네이션을 동시에 쓸 때는 N+1이나 중복 로우에 주의한다.
- 대량 벌크/집계/네이티브 SQL: SQLAlchemy Core(`text()`, `insert().values(...)` 벌크)는 측정된 성능 문제가 있을 때만 사용한다.

## 5. 트랜잭션

- 세션(`AsyncSession`)은 요청 단위로 FastAPI 의존성 주입(`Depends`)을 통해 공급한다. Service 함수가 세션을 직접 생성하지 않는다.
- 쓰기 흐름은 세션 컨텍스트 안에서 커밋하고, 조회 전용 흐름은 커밋을 호출하지 않는다(읽기 전용 의도를 코드로 드러낸다).

## 6. API 스펙: code-first가 원칙이다

- FastAPI는 spec-first가 아니라 **code-first가 프레임워크의 정체성 자체**다. Pydantic 모델과 라우터 타입 힌트에서 OpenAPI 스펙(`/openapi.json`)이 자동 생성되는 것이 FastAPI를 쓰는 핵심 이유이므로, `spring/api-dto.md`처럼 yaml을 먼저 작성하고 코드를 생성하는 절차를 강제하지 않는다.
- 단일 소스 원칙(`shared/architecture.md`의 근본 취지: 프론트-백엔드 스펙 불일치 방지)은 방향을 바꿔서 달성한다: FastAPI가 자동 생성한 `/openapi.json`을 신뢰 가능한 단일 소스로 취급하고, 프론트엔드 타입 생성(`openapi-typescript` 등)이 이 산출물을 소비한다.
- Pydantic 모델에 `Field(description=...)`, `examples=...`를 채워서 생성된 스펙만으로 API 동작을 이해할 수 있게 한다(`spring/rest-api.md`의 예시 포함 원칙과 동일한 목표를 코드 쪽에서 달성).

## 7. 테스트

- `pytest` + `httpx.AsyncClient`(또는 `TestClient`)로 라우터를 테스트한다.
- 순수 도메인/서비스 로직은 FastAPI 앱을 띄우지 않고 함수/클래스 단위로 직접 테스트한다.
- `time.sleep`으로 순서를 보장하지 않는다. `pytest` fixture로 결정적 테스트 데이터를 만든다.
- DB가 필요한 테스트는 트랜잭션을 테스트마다 롤백하거나 격리된 스키마를 사용해 테스트 간 상태가 새지 않게 한다.

## 8. 금지 패턴

- Router 스키마를 검증 없이 그대로 ORM 모델에 매핑해 저장하지 않는다(Repository/Service를 거치지 않고 직접 커밋).
- 세션을 Service 함수 내부에서 직접 생성하지 않는다(`Depends`로 주입).
- 비즈니스 규칙 검증(형식이 아닌 규칙 위반)을 Pydantic validator에 넣지 않는다 — 형식 검증은 Pydantic, 비즈니스 검증은 Domain의 몫이다(`shared/architecture.md` 5번).
