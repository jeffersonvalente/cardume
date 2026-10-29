# Modern Java Idioms (language only)

Plain JDK guidance — nothing here depends on Spring. Check the project's baseline in
[capability-baseline.md](capability-baseline.md) before using a feature.

## Records for values

A record is a transparent carrier for immutable data: the compiler derives the constructor,
accessors, `equals`, `hashCode` and `toString` from the components
([JEP 395](https://openjdk.org/jeps/395)). Use one for value objects, DTOs, commands, events
and query results.

Put invariants in the **compact constructor**, so an invalid instance can never exist:

```java
public record Money(BigDecimal amount, Currency currency) {
    public Money {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(currency, "currency");
        if (amount.scale() > currency.getDefaultFractionDigits()) {
            throw new IllegalArgumentException("too many decimal places for " + currency);
        }
    }

    public Money plus(Money other) {
        requireSameCurrency(other);
        return new Money(amount.add(other.amount), currency);
    }

    private void requireSameCurrency(Money other) {
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException("currency mismatch");
        }
    }
}
```

Things to keep in mind:

- Records are shallowly immutable. Copy mutable components (`List.copyOf(items)`) in the compact
  constructor.
- A record is a poor JPA entity (entities need a no-arg constructor and mutable state for
  dirty checking). Use records around entities, not as entities; JPA `@Embeddable` records are
  supported by Hibernate 6.2+.
- Prefer records over Lombok `@Value`/`@Data` when the type is pure data — one less annotation
  processor and the intent is visible in the language.

## Sealed types for closed hierarchies

`sealed ... permits` lists every allowed subtype ([JEP 409](https://openjdk.org/jeps/409)).
Use it when the set of cases is part of the domain: payment outcomes, commands, domain events.

```java
public sealed interface ReservationResult
        permits ReservationResult.Confirmed, ReservationResult.Waitlisted, ReservationResult.Rejected {

    record Confirmed(ReservationId id) implements ReservationResult {}
    record Waitlisted(int position) implements ReservationResult {}
    record Rejected(String reason) implements ReservationResult {}
}
```

Subtypes must be `final`, `sealed` or `non-sealed`, and live in the same module (or package,
outside a named module).

## Pattern matching in `switch` (21+)

With [JEP 441](https://openjdk.org/jeps/441) and record patterns
([JEP 440](https://openjdk.org/jeps/440)), a `switch` over a sealed type is checked for
exhaustiveness: no `default` branch is needed, and adding a new permitted subtype becomes a
compile error everywhere a case is missing — which is the point.

```java
String describe(ReservationResult result) {
    return switch (result) {
        case Confirmed(ReservationId id) -> "Confirmed as " + id.value();
        case Waitlisted(int position) when position <= 3 -> "Almost there: #" + position;
        case Waitlisted(int position) -> "Waitlisted at #" + position;
        case Rejected(String reason) -> "Rejected: " + reason;
    };
}
```

Rules worth stating in reviews:

- **Null handling is opt-in.** A pattern `switch` throws `NullPointerException` for a `null`
  selector unless a `case null` (or `case null, default`) is present. Decide explicitly.
- Avoid a `default` branch on sealed hierarchies: it silences the exhaustiveness check you
  wanted.
- Guards (`when`) are evaluated in order; put the more specific case first.
- On a **17 baseline** pattern `switch` was preview only. Do not standardise preview features on
  17; use `instanceof` patterns or polymorphism instead.
- From 22, unnamed patterns (`case Rejected _`) skip components you do not use
  ([JEP 456](https://openjdk.org/jeps/456)).

## Text blocks

Multi-line string literals ([JEP 378](https://openjdk.org/jeps/378)) for SQL, JSON fixtures and
templates. Indentation is stripped relative to the closing delimiter; use `\` at line end to
join lines and `formatted(...)` for values. Never build SQL with `formatted` — bind parameters.

## Virtual threads (21+)

Virtual threads are cheap JDK-managed threads mounted on a small pool of carrier threads
([JEP 444](https://openjdk.org/jeps/444)). The JEP is explicit that they "are not faster
threads"; they "exist to provide scale (higher throughput), not speed (lower latency)".

Use them for:

- Request-per-thread servers and code that spends most of its time waiting on I/O (JDBC, HTTP
  calls, file access).
- Fan-out of blocking calls, one virtual thread per task:

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    Future<Quote> a = executor.submit(() -> supplierA.quote(sku));
    Future<Quote> b = executor.submit(() -> supplierB.quote(sku));
    return cheaper(a.get(), b.get());
}
```

Rules:

- **Do not pool them.** Create one per task. A pool exists to limit or reuse expensive threads;
  virtual threads are neither.
- **Limit concurrency with a `Semaphore`**, not a fixed-size pool, when a downstream (database
  connections, a rate-limited API) cannot take unlimited parallel calls. The JDBC connection pool
  remains the real ceiling for database work.
- **CPU-bound work gains nothing.** Keep using a bounded platform-thread pool or parallel
  streams for computation.
- **Pinning (21–23):** a virtual thread blocking inside `synchronized` (or a native frame) keeps
  its carrier thread busy. Replace `synchronized` that guards blocking I/O with
  `ReentrantLock`. Diagnose with the `jdk.VirtualThreadPinned` JFR event.
- **Java 24+:** [JEP 491](https://openjdk.org/jeps/491) lets virtual threads release the carrier
  while blocked in `synchronized`, so the rewrite above is mostly unnecessary. Native frames
  still pin.
- **`ThreadLocal`:** works, but millions of threads multiply its memory. Prefer passing context
  explicitly, or scoped values on Java 25+ ([JEP 506](https://openjdk.org/jeps/506)).

Spring's switch for virtual threads is in [spring-conventions.md](spring-conventions.md#virtual-threads).

## Smaller idioms

- `Optional` is a return type for "may be absent". Do not use it for fields or parameters, and
  avoid bare `get()`: use `orElseThrow(() -> new SomethingNotFound(id))`.
- `List.of`, `Map.of`, `List.copyOf` create unmodifiable collections; return them from APIs.
- Sequenced collections (21+): `list.getFirst()`, `list.reversed()` instead of index arithmetic.
- `var` for local variables when the right-hand side states the type; not for public API.
- Money: `BigDecimal` built from a `String` or `BigDecimal.valueOf(long, scale)`, never
  `new BigDecimal(double)`; compare with `compareTo`, because `equals` also compares scale.
