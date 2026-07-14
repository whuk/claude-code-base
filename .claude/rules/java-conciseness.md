# Java 간결성 규칙

순수 JDK 수단만으로 Java 코드의 장황함을 줄인다. 모든 계층(domain 패키지 포함)에 동일하게 적용 가능한 패턴만 채택하여 계층 간 스타일 이원화를 방지한다.

## 1. 핵심 원칙

- **이원화 금지**: domain 패키지에서 사용할 수 없는 수단(Spring `Assert`, Lombok 등)은 간결화 목적으로 도입하지 않는다. 이 규칙의 모든 패턴은 순수 JDK 문법이다.
- **점진 적용**: 신규 작성 코드와 수정 대상 코드에 적용한다. 동작 중인 기존 코드를 간결화 목적만으로 일괄 변환하지 않는다 (Tidy First — 해당 코드를 만질 때 구조적 변경 커밋으로 함께 정리한다).

## 2. Builder / 파라미터 객체 (텔레스코핑 오버로드 방지)

### 2.1. 전환 기준

다음 중 하나에 해당하면 오버로드 추가 대신 **Builder** 또는 **파라미터 객체**로 전환한다:

- 생성 메서드(생성자, 정적 팩토리)의 파라미터가 **5개 이상**
- 같은 이름의 오버로드가 **3개 이상**으로 늘어나는 시점
- 같은 타입의 파라미터가 3개 이상 연속되어 호출부에서 순서 실수를 컴파일러가 잡을 수 없는 경우

### 2.2. 작성 규칙

- Builder는 대상 클래스 내부의 `static class Builder`로 작성한다 (인프라 비종속 유지, 별도 파일 금지).
- 필수 필드는 `build()` 시점에 검증하거나 Builder 진입점 파라미터로 강제한다. 기존 생성자/팩토리의 불변식 검증을 그대로 유지한다.
- 영속 계층의 재구성 경로(`restore(...)`)처럼 파라미터가 많은 곳에 우선 적용한다.
- 이미 오버로드가 3개 이상인 메서드에 파라미터 추가가 필요해지면, 오버로드를 하나 더 만들지 말고 그 시점에 Builder로 전환한다 (구조적 변경 커밋 분리).

### 2.3. 예시

```java
// 금지: 오버로드 증식
public static Message restore(String id, String conversationId, ...);           // 파라미터 10개
public static Message restore(String id, String conversationId, ..., ...);      // 파라미터 13개
public static Message restore(String id, String conversationId, ..., ..., ...); // 파라미터 18개

// 권장: 단일 Builder
Message message = Message.restoreBuilder()
        .id(id)
        .conversationId(conversationId)
        .role(role)
        .status(status)
        .feedback(feedback)
        .createdAt(createdAt)
        .build();
```

## 3. Java 21 문법 활용

### 3.1. switch 패턴 매칭

- `if (x instanceof A a) ... else if (x instanceof B b) ...` 체인 대신 switch 패턴 매칭을 사용한다.
- `sealed` 타입과 조합하여 `default` 분기 없이 컴파일러의 exhaustiveness 검사를 받는다. sealed 타입에 구현이 추가되면 누락 분기가 컴파일 오류로 드러난다.

```java
// 권장
return switch (event) {
    case AgentEvent.Content c -> handleContent(c);
    case AgentEvent.UiControl u -> handleUiControl(u);
    case AgentEvent.Error e -> handleError(e);
};
```

### 3.2. record 패턴 (구조 분해)

- switch/instanceof에서 record 내부 값에 접근할 때 getter 체인보다 구조 분해가 명확하면 record 패턴을 사용한다.

```java
case AgentEvent.UiControl(var content) -> emit("ui_controller", content);
```

### 3.3. 텍스트 블록

- 3줄 이상의 문자열(테스트 JSON 픽스처, 인라인 SQL, 로그 템플릿 등)은 문자열 연결 대신 텍스트 블록(`"""`)을 사용한다.
- SQL 외부화 기준은 `repository.md` 7.3절(5줄 초과 시 파일 분리)을 그대로 따른다. 텍스트 블록은 외부화 기준 미만의 인라인 SQL에만 적용한다.

## 4. 지역변수 타입 추론 (`var`)

### 4.1. 허용

우변만 보고 타입이 명백한 경우에만 사용한다:

- 생성자 호출: `var parser = new SseLineParser();`
- 타입 이름이 드러나는 정적 팩토리: `var period = ValidityPeriod.of(start, end);`
- 명시적 캐스트, 리터럴

### 4.2. 금지

- 우변이 메서드 호출이라 타입이 드러나지 않는 경우: `var result = finder.search(query);` — 명시적 타입 선언
- 다이아몬드 연산자와 결합하여 타입 인자 정보가 사라지는 경우: `var list = new ArrayList<>();`
- 스트림 파이프라인의 중간 결과 등 추론 결과가 자명하지 않은 경우

## 5. 금지 패턴

- 간결화 목적으로 계층 이원화를 유발하는 의존성(Lombok, Spring `Assert`, Guava Preconditions 등)을 도입하지 않는다.
- 간결화(구조적 변경)와 동작 변경을 같은 커밋에 섞지 않는다.
- `Objects.requireNonNull` ↔ if-throw를 일괄 통일하지 않는다 (NPE/IAE 예외 계약이 달라 HTTP 응답이 변한다). 각 도메인의 기존 검증 스타일을 따른다.
- 이 규칙을 근거로 동작 중인 코드의 일괄 스타일 변환(빅뱅 리팩터링)을 수행하지 않는다.
