---
name: java-spring-patterns
description: "Guides Java 17+ and Spring Boot 3.x/4.x work: architecture choice (layered, hexagonal, DDD, modular monolith, CQRS, events), idioms the JDK baseline allows (records, sealed types, pattern matching, virtual threads), Spring transactions, DI and errors, Testcontainers, ArchUnit, Micrometer. Use when building or reviewing Java/Spring Boot services."
allowed-tools: Read Write Edit Glob Grep
---

# Working on a Java / Spring Boot codebase

This file is a working method and an index. The detail lives in topic files next to it; read
only the ones the task needs, because each one is long enough to crowd out the code you are
looking at.

The method has four moves, in this order: **find out what the project is**, **match what is
already there**, **apply the topic file for the task**, and **review the result against the
failure modes that actually hurt Spring services**. Skipping the first move is the most common
way to give advice that does not compile or does not fit.

Not Java? Stop here. Node.js work belongs to `cardume-backend:nodejs-best-practices`, and
API contract questions that are language-neutral belong to `cardume-backend:api-patterns`.

## 1. Find out what the project is

Read the build file before suggesting any code. Advice for Java 21 is wrong on Java 17, and a
Boot 4 starter name is wrong on Boot 3.

- **JDK release:** `maven.compiler.release` / `<java.version>` in `pom.xml`, or the toolchain
  `languageVersion` in `build.gradle(.kts)`. Then check what that release allows in
  [capability-baseline.md](capability-baseline.md). Preview features need `--enable-preview`
  and are not a default.
- **Spring Boot generation:** the parent POM or the `org.springframework.boot` plugin version.
  3.x and 4.x share the conventions here but differ in starters, test annotations and some
  property names; [capability-baseline.md](capability-baseline.md#framework-baseline) has the
  table.
- **Persistence and messaging:** Spring Data JPA, JDBC, R2DBC; Kafka, Rabbit, none. The answer
  changes how transactions, locking and events are written.
- **Existing shape:** look at the top-level packages under the `@SpringBootApplication` class.
  Feature packages with `web`/`service`/`persistence` inside are layered; `port`/`adapter`
  packages are hexagonal; a `package-info.java` with `@ApplicationModule` or a
  `spring-modulith` dependency means a modular monolith.
- **Existing tests:** Testcontainers, ArchUnit or `ApplicationModules.verify()` tests are rules
  the team already decided to enforce. Keep them green.

When the prompt gives a code snippet with no build file (a review question, say), take the
versions it states and say which assumptions you made.

## 2. Match what is already there

Consistency is worth more than local perfection. A hexagonal use case dropped into a layered
codebase is harder to maintain than one more well-written `@Service`.

- Follow the existing package style, naming, mapping approach and error format.
- When the existing style itself causes the bug (field injection, logic in controllers,
  `double` balances), fix it in the code you touch and say why. Do not rewrite unrelated
  modules in the same change.
- Changing the architecture style is a decision, not a refactor. Use
  [architecture-selection.md](architecture-selection.md) to argue it, and record it with
  `cardume-core:adr` if the team agrees.

## 3. Apply the topic file for the task

Pick by what the task touches. Several can apply; read them one at a time as the work reaches
them.

**Language and platform**
- Is this idiom available here? → [capability-baseline.md](capability-baseline.md)
- Records, sealed types, pattern matching, text blocks, virtual threads, plain-JDK idioms →
  [java-language.md](java-language.md)

**Framework**
- Dependency injection, `@Transactional` boundaries, locking, money types, request/response
  records, Bean Validation, ProblemDetail errors, configuration, HTTP clients →
  [spring-conventions.md](spring-conventions.md)

**Architecture** — start with [architecture-selection.md](architecture-selection.md) when the
style is not yet decided, then go to the style itself:
- Feature-first web/service/persistence layers → [mvc-layered.md](mvc-layered.md)
- Ports and adapters, framework-free core → [hexagonal.md](hexagonal.md)
- Bounded contexts, aggregates, value objects → [ddd.md](ddd.md)
- One deployable with verified module boundaries → [modular-monolith.md](modular-monolith.md)
- Separate read models, event-sourced aggregates, Axon →
  [cqrs-event-sourcing.md](cqrs-event-sourcing.md)
- Spring application events, transactional listeners, outbox, Kafka →
  [eda.md](eda.md)

**Proof and operations**
- Test slices, Testcontainers, ArchUnit, Modulith tests, Boot 3 → 4 test migration →
  [testing.md](testing.md)
- Micrometer observations, metrics cardinality, tracing, logs →
  [observability.md](observability.md)

Related skills, when the question leaves Java:
`cardume-backend:api-patterns` (resource design, status codes, versioning),
`cardume-core:database-design` (schema, indexes, migrations),
`cardume-core:clean-code` (naming and function shape in any language),
`cardume-qa:testing-patterns` (test strategy across the stack).

## 4. Review against what actually breaks

Most production incidents in Spring services come from a short list of causes, and almost all
of them are visible in one controller-plus-service pair. Walk the request from the edge to the
database and back, and answer each question below. When the answer is "no", the finding goes
in the review with the fix and the reason.

**At the edge.** Does a state-changing endpoint take a request body as a `record` with Bean
Validation (`@Valid @RequestBody`), rather than loose query parameters? Is the controller thin:
map the request to a command, call one service method, map the result to a response record
with the right status? See [spring-conventions.md](spring-conventions.md#web-layer-input-output-and-errors).

**Wiring.** Are collaborators injected through the constructor into `final` fields? Field
injection hides dependencies and forces a Spring context into every unit test, which is why
"hard to test" usually points here.

**The unit of work.** Is there exactly one `@Transactional` boundary per use case, on a
service method, wrapping *every* write of that use case? Two `save` calls in a controller run
as separate transactions, so an exception between them leaves the first write committed. That
is the classic "debited but not credited" bug. Watch for self-invocation, which bypasses the
proxy, and for checked exceptions, which do not roll back by default.

**Order of operations.** Are all checks (existence, limits, permissions, invariants) done
before the first mutation? Rolling back is the safety net, not the plan; a rejected request
should never touch state.

**Concurrency.** Is any read-modify-write on a shared row (balances, stock, counters)
protected? Use optimistic locking with `@Version` and return `409` or retry, or take
pessimistic locks in a stable order (for example ascending id) so opposite operations cannot
deadlock, or use one conditional `UPDATE`. Without one of these, two concurrent requests lose
an update even inside a transaction.

**Numbers.** Is money a `BigDecimal` with explicit scale and rounding, or a `long` of minor
units, wrapped in a value object and stored as `NUMERIC`? `double` cannot represent most
decimal amounts, and the error compounds.

**Absence and failure.** Is `Optional.get()` replaced by `orElseThrow` with a domain
exception (`AccountNotFound`)? Are domain exceptions translated to RFC 9457 `ProblemDetail`
responses in one `@RestControllerAdvice` (404 for unknown resources, 422 for rule violations,
409 for conflicts), with no stack traces or SQL leaking out? `RuntimeException("limit")`
becomes a 500 with no useful body.

**Side effects.** Are HTTP calls and broker sends kept out of the transaction and triggered
after commit (`@TransactionalEventListener`, Modulith event publication registry, outbox)?
See [eda.md](eda.md).

**Proof.** Is there a test that would have caught the bug? For transactional and locking
bugs that means a `@SpringBootTest` with Testcontainers on the real database engine: force a
failure mid-use-case and assert nothing was written; run two transfers concurrently and assert
the totals. H2 hides locking and dialect behaviour. See [testing.md](testing.md).

**Idioms.** Does the code use what the baseline allows and avoid what it does not (no pattern
`switch` on 17, no `synchronized` around blocking I/O on 21–23 virtual threads)? See
[java-language.md](java-language.md).

### Writing the review

Lead with the defect that loses data or money, then the ones that make the service wrong
under load, then structure and style. For each finding give the line, what goes wrong in
production, and the fix. Close with a corrected version of the code when it fits in the
reply: a request record, a controller that delegates, a transactional service that validates
first and locks consistently, the exception advice, and the test that proves the rollback.

## Sources

Topic files cite their own primary sources. The ones this guide leans on directly:
[Spring Framework: declarative transactions](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html),
[Spring Framework: dependency injection](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html),
[Spring Data JPA: locking](https://docs.spring.io/spring-data/jpa/reference/jpa/locking.html),
[Spring Framework: error responses](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html),
[RFC 9457](https://www.rfc-editor.org/rfc/rfc9457),
[Spring Boot: Testcontainers](https://docs.spring.io/spring-boot/reference/testing/testcontainers.html),
[Spring Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html).
