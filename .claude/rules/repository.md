# Repository 계층 규칙

JPA Repository 작성 시 동적 검색 조건 처리 방식과 쿼리 작성 규칙을 정의한다.

## 1. 핵심 원칙

- 검색(조회) 조건이 동적으로 조합되는 경우, `@Query` 어노테이션을 사용하지 않고 **JPA Specification**을 사용한다.
- Repository 인터페이스는 `JpaSpecificationExecutor<T>`를 함께 상속하여 Specification 기반 조회를 지원한다.

## 2. Specification 사용 규칙

- 검색 조건별로 개별 Specification 메서드를 작성하고, `and()`, `or()` 등으로 조합하여 사용한다.
- Specification 메서드는 도메인별 전용 클래스에 `static` 메서드로 그룹화한다 (예: `OrderSpecifications`, `UserSpecifications`).
- null이거나 빈 값인 조건은 무시하도록 처리하여, 조건의 유무에 따라 동적으로 쿼리가 구성되도록 한다.

## 3. @Query 허용 범위

- Specification으로 표현하기 어려운 **집계(aggregation)**, **서브쿼리**, **네이티브 쿼리** 등 특수한 경우에만 예외적으로 `@Query`를 허용한다.
- Spring Data JPA의 메서드 이름 기반 쿼리 파생(Query Derivation)은 단순 조회(단일 조건, 2개 이하 조건)에 한해 허용한다.

## 4. 금지 패턴

- 동적 검색 조건을 `@Query` 어노테이션의 JPQL/HQL 문자열로 직접 작성하지 않는다.
- 검색 조건 분기를 위해 여러 개의 `@Query` 메서드를 나열하지 않는다.
- Specification 클래스 내부에 비즈니스 로직을 포함하지 않는다. 순수한 조건 조립만 담당한다.
