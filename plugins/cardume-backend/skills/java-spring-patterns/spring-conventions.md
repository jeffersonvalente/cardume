# Spring Conventions

Framework guidance for Spring Boot 3.x and 4.x. Language idioms are in
[java-language.md](java-language.md).

## Dependency injection

Use constructor injection with `final` fields
([Spring Framework: dependency injection](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)).
With a single constructor, no `@Autowired` is needed.

```java
@Service
class StockTransferService {
    private final StockLevelRepository stock;
    private final Clock clock;

    StockTransferService(StockLevelRepository stock, Clock clock) {
        this.stock = stock;
        this.clock = clock;
    }
}
```

Why: dependencies are visible in the signature, the object is complete after construction,
fields can be `final`, and a unit test can call `new` without a container.

A constructor with many parameters is a design signal, not an injection problem: the class
probably has more than one responsibility. Split it rather than switching to field injection.

## Transactions

Declarative transactions work through a proxy around the bean
([Spring Framework: declarative transactions](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)).
Put `@Transactional` on the **service method that represents one use case**, so every write in
that use case commits or rolls back together.

Pitfalls the reference docs call out, and that reviews should check:

- **Self-invocation bypasses the proxy.** Calling a `@Transactional` method from another method
  of the same class does not start a transaction. Move it to another bean or annotate the
  caller.
- **Rollback rules.** By default only unchecked exceptions (`RuntimeException`, `Error`) roll
  back. A checked exception commits unless you set `rollbackFor`.
- **Controllers are the wrong place.** A controller that calls `save` twice runs two separate
  transactions (or none), so a failure between them leaves partial data.
- **Validate before mutating.** Do all checks (existence, limits, permissions) before the first
  change, so a rejected request never touches state even before rollback matters.
- `@Transactional(readOnly = true)` on query methods lets the JPA provider skip dirty checking.
- Keep remote calls (HTTP, broker sends) out of the transaction: they hold locks and
  connections, and they cannot be rolled back. Use events or an outbox ([eda.md](eda.md)).

## Concurrency and locking

Read-modify-write on shared rows loses updates under concurrency unless something serialises it
([Spring Data JPA: locking](https://docs.spring.io/spring-data/jpa/reference/jpa/locking.html)).

- **Optimistic** (default choice): add a `@Version` field to the entity. A concurrent change
  makes the second commit fail with `ObjectOptimisticLockingFailureException`; retry the use
  case or return `409 Conflict`.
- **Pessimistic**: `@Lock(LockModeType.PESSIMISTIC_WRITE)` on a repository finder issues
  `SELECT … FOR UPDATE`. When one transaction locks several rows, always lock them in the
  same order (for example ascending id) so two opposite requests cannot deadlock.
- A single conditional `UPDATE … WHERE quantity >= :n` is often the simplest correct option for
  counters and balances.

```java
@Transactional
public TransferReceipt move(MoveStock command) {
    if (command.from().equals(command.to())) {
        throw new InvalidTransfer("source and target must differ");
    }
    // lock in a stable order to avoid deadlocks between opposite transfers
    var ids = Stream.of(command.from(), command.to()).sorted().toList();
    Map<WarehouseId, StockLevel> locked = stock.lockAll(ids, command.sku());

    StockLevel source = locked.get(command.from());
    StockLevel target = locked.get(command.to());
    source.remove(command.quantity());   // throws InsufficientStock before anything is written
    target.add(command.quantity());
    return new TransferReceipt(command.sku(), command.quantity(), clock.instant());
}
```

Dirty checking flushes both changes at commit; an exception anywhere rolls both back.

## Money and numbers

`double` and `float` cannot represent most decimal fractions exactly. For money use
`BigDecimal` with an explicit scale and `RoundingMode`, or a `long` count of minor units, and
wrap it in a value object ([java-language.md](java-language.md#records-for-values)). Map it to a
`NUMERIC(p,s)` / `DECIMAL` column, not a floating-point column.

## Web layer: input, output and errors

- Accept a request **record** annotated with Jakarta Bean Validation and mark the parameter
  `@Valid @RequestBody`
  ([Spring Framework: validation](https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html)).
  State-changing calls take a body, not query parameters.

  ```java
  record MoveStockRequest(
          @NotNull UUID from,
          @NotNull UUID to,
          @NotBlank String sku,
          @Positive int quantity) {}
  ```

- Return a response record and the right status: `201 Created` with `Location` for creation,
  `200` with a body, `204` when there is nothing to return.
- Keep the controller thin: map the request to a command, call one service method, map the
  result. Business rules live in the service or domain.

### Error responses with ProblemDetail

Spring Framework 6+ supports RFC 9457 problem details through `ProblemDetail`,
`ErrorResponse` and `ResponseEntityExceptionHandler`
([Spring Framework: error responses](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html),
[RFC 9457](https://www.rfc-editor.org/rfc/rfc9457)).

```java
@RestControllerAdvice
class ApiErrors extends ResponseEntityExceptionHandler {

    @ExceptionHandler(NotFound.class)
    ProblemDetail notFound(NotFound ex) {
        var problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setType(URI.create("https://errors.example.com/not-found"));
        return problem;
    }

    @ExceptionHandler(InsufficientStock.class)
    ProblemDetail insufficient(InsufficientStock ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage());
    }
}
```

- Extending `ResponseEntityExceptionHandler` makes Spring MVC's own exceptions (validation,
  unsupported media type…) use the same format. Alternatively set
  `spring.mvc.problemdetails.enabled=true`.
- Domain exceptions should not know HTTP; the advice translates them.
- Never leak stack traces or SQL in `detail`.

## Configuration

- Bind settings to a `@ConfigurationProperties` **record** with validation, rather than many
  `@Value` fields
  ([Spring Boot: type-safe configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html#features.external-config.typesafe-configuration-properties)).
- Inject a `Clock` instead of calling `Instant.now()`, so time is testable.
- Secrets come from the environment or a secret manager, never from committed files.

## Virtual threads

On Java 21+ with Spring Boot 3.2+, set:

```properties
spring.threads.virtual.enabled=true
```

Boot then runs request handling (Tomcat/Jetty), `@Async`, scheduling and several integrations on
virtual threads
([Spring Boot: virtual threads](https://docs.spring.io/spring-boot/reference/features/spring-application.html#features.spring-application.virtual-threads)).
Notes:

- The JDBC pool size still bounds database concurrency; virtual threads do not make the
  database faster.
- Because virtual threads are daemon threads, an application whose only work is scheduled tasks
  may exit; Boot provides `spring.main.keep-alive=true` for that case.
- Review `synchronized` blocks around I/O on Java 21–23 (see
  [java-language.md](java-language.md#virtual-threads-21)).

## HTTP clients

- `RestClient` (Framework 6.1+) is the synchronous fluent client; prefer it over
  `RestTemplate` for new code. Pair it with virtual threads instead of going reactive just for
  concurrency.
- Declarative HTTP interfaces (`@HttpExchange`) give a typed client from an interface.
- Always set connect and read timeouts.
