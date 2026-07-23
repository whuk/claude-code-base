---
description: JPA Repository 동적 검색 조건 처리 및 쿼리 작성 규칙 (Specification/QueryDSL/JdbcClient, Kotlin)
globs: "**/*Repository*.kt,**/*Specifications.kt,**/*SqlBuilder.kt"
---

# Repository 계층 규칙

JPA Repository 작성 시 동적 검색 조건 처리 방식과 쿼리 작성 규칙을 정의한다. Level 2~3 도구(QueryDSL, JdbcClient + jOOQ)의 사용 상세 규칙은 `repository-tools.md`가 정의한다.

이 프로젝트가 Hexagonal(Ports & Adapters)을 채택했다면 이 파일은 적용 대상이 아니다. Repository가 Domain 클래스를 직접 다루는지(Layered) Port 뒤의 Adapter가 별도 JpaEntity를 다루는지(Hexagonal)가 핵심 차이다 (`hexagonal/repository.md` 참조). 마찬가지로 이 프로젝트가 Java를 채택했다면 이 파일은 적용 대상이 아니다. Java와 Kotlin 규칙 파일을 한 프로젝트에서 동시에 쓰지 않으므로, 실제로 채택하지 않은 언어의 규칙 파일도 프로젝트에서 제외한다 (`java/layered/repository.md` 참조). 또한 이 프로젝트가 SQL-first(ORM 미사용)를 채택했다면 이 파일은 적용 대상이 아니다. ORM과 SQL-first 영속성 규칙을 한 프로젝트에서 동시에 쓰지 않으므로, 실제로 채택하지 않은 영속성 도구의 규칙 파일도 프로젝트에서 제외한다 (`repository-sql.md` 참조).

## 1. 핵심 원칙

- 검색(조회) 조건이 동적으로 조합되는 경우, `@Query` 어노테이션을 사용하지 않고 **JPA Specification**을 사용한다.
- Repository 인터페이스는 `JpaSpecificationExecutor<T>`를 함께 상속하여 Specification 기반 조회를 지원한다.

## 2. Specification 사용 규칙

- 검색 조건별로 개별 Specification 함수를 작성하고, `and()`, `or()` 등으로 조합하여 사용한다.
- Specification 함수는 도메인별 전용 object에 그룹화한다 (예: `OrderSpecifications`, `UserSpecifications`).
- null이거나 빈 값인 조건은 무시하도록 처리하여, 조건의 유무에 따라 동적으로 쿼리가 구성되도록 한다.

## 3. @Query 허용 범위

- Specification으로 표현하기 어려운 **집계(aggregation)**, **서브쿼리**, **네이티브 쿼리** 등 특수한 경우에만 예외적으로 `@Query`를 허용한다.
- Spring Data JPA의 메서드 이름 기반 쿼리 파생(Query Derivation)은 단순 조회(단일 조건, 2개 이하 조건)에 한해 허용한다.

## 4. 도구 선택 계층 (Escalation Ladder)

항상 최하위 충분한 단계에서 시작한다. 상위 단계로 올라가려면 구체적인 근거가 필요하다.

| Level | 도구 | 사용 조건 |
|-------|------|-----------|
| 0 | Query Derivation | 정적 조건 2개 이하의 단순 조회 |
| 1 | JPA Specification | 동적 검색 조건 조합 (기본값, 섹션 1~3) |
| 2 | QueryDSL | N+1 fetch join + 페이지네이션, 3개 이상 엔티티 조인, 타입 안전 DTO 프로젝션, 복잡한 서브쿼리 |
| 3 | JdbcClient + jOOQ | 대량 벌크 처리, 리포팅/집계(GROUP BY, 윈도우 함수, CTE), 측정된 JPA 성능 병목, JPQL/QueryDSL로 표현 불가한 네이티브 SQL 기능 |

- Level 2는 Specification으로 표현이 어렵거나 N+1 문제가 발생하는 경우에 사용한다.
- Level 3은 **측정된 성능 문제**가 있을 때만 사용한다. 선제적 사용을 금지한다.
- 동일 도메인에서 여러 Level을 혼용할 수 있다. 쿼리별로 적절한 Level을 선택한다.
- Level 2~3 도구의 사용 상세 규칙(의존성, 클래스 구조, DTO 프로젝션, N+1 방지 도구, SQL 관리, 테스트)은 `repository-tools.md`를 따른다.

## 5. Finder/Service 계층과의 통합

`service-layer.md`의 Finder/Service 분리 규칙에 따라 다음과 같이 통합한다.

```
Finder/Service
    |
    +---> {Domain}Repository (JPA — Specification + QueryDSL)
    |         |
    |         +---> {Domain}RepositoryCustom → {Domain}RepositoryImpl
    |
    +---> {Domain}JdbcRepository (성능 최적화 쿼리)
              |
              +---> {Domain}SqlBuilder (jOOQ, 선택)
```

- **Finder** (조회 전용): 모든 티어의 Repository를 사용할 수 있다. 내부적으로 어떤 티어가 사용되는지 알 필요 없다.
- **Service** (상태 변경): 주로 JPA `{Domain}Repository`를 사용한다. JdbcClient는 벌크 작업 등 예외적 경우에만 허용하며, 도메인 검증 우회를 명시적으로 문서화한다.
- **의존 방향**: Finder/Service → Repository/JdbcRepository. 역방향 의존을 금지한다. SqlBuilder는 JdbcRepository의 내부 의존성이며, Finder/Service에서 직접 사용하지 않는다.

## 6. 금지 패턴

- 동적 검색 조건을 `@Query` 어노테이션의 JPQL/HQL 문자열로 직접 작성하지 않는다.
- 검색 조건 분기를 위해 여러 개의 `@Query` 메서드를 나열하지 않는다.
- Specification object 내부에 비즈니스 로직을 포함하지 않는다. 순수한 조건 조립만 담당한다.
- 측정된 근거 없이 선제적으로 상위 단계 도구(QueryDSL, JdbcClient + jOOQ)를 사용하지 않는다 (도구별 금지 패턴은 `repository-tools.md` 4번 참조).
