# Modular Monolith with Spring Modulith

One deployable, several modules with verified boundaries. Reference:
[Spring Modulith documentation](https://docs.spring.io/spring-modulith/reference/).
Public example: [spring-petclinic-modulith](https://github.com/spring-petclinic/spring-petclinic-modulith).

## Setup

Import the Spring Modulith BOM and add the starters you need. Pick the Modulith generation that
matches the Boot generation (1.x lines target Boot 3.x — use at least Boot 3.2; 2.x targets
Boot 4.x); check the
[project README](https://github.com/spring-projects/spring-modulith)
for the exact pair.

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>org.springframework.modulith</groupId>
      <artifactId>spring-modulith-bom</artifactId>
      <version>${spring-modulith.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<dependency>
  <groupId>org.springframework.modulith</groupId>
  <artifactId>spring-modulith-starter-core</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.modulith</groupId>
  <artifactId>spring-modulith-starter-test</artifactId>
  <scope>test</scope>
</dependency>
```

## Module conventions

From the [fundamentals chapter](https://docs.spring.io/spring-modulith/reference/fundamentals.html):

- Each **direct sub-package** of the package holding `@SpringBootApplication` is a module.
- A module's **base package is its API**. Sub-packages (`booking.internal`, `booking.persistence`)
  are internal; other modules must not reference them, even when the types are public. The
  compiler cannot stop that — verification does.
- Expose extra packages deliberately with `@NamedInterface` on their `package-info.java`
  (for example an `spi` or `events` package).
- Restrict who a module may depend on with `@ApplicationModule(allowedDependencies = …)` on the
  module's `package-info.java`. `"membership :: events"` allows only that named interface.

```java
// booking/package-info.java
@org.springframework.modulith.ApplicationModule(
    displayName = "Desk booking",
    allowedDependencies = { "membership :: events" })
package com.example.cowork.booking;
```

- `Type.OPEN` modules exist for migrating legacy code; treat them as temporary.

## How modules talk

1. **Events first.** Publish a domain event (`ApplicationEventPublisher` or Spring Data
   aggregate events) and let other modules react with `@ApplicationModuleListener`, which is
   asynchronous, runs in its own transaction and fires after the publisher commits
   ([events chapter](https://docs.spring.io/spring-modulith/reference/events.html)). The
   publisher does not know its consumers, and a failing listener does not roll back the
   publisher.
2. **API calls when the caller needs an answer now**, through the other module's base package
   (a `MembershipApi` interface), never its repositories or entities.

### Event Publication Registry (transactional outbox)

Add one of `spring-modulith-starter-jpa`, `spring-modulith-starter-jdbc` or
`spring-modulith-starter-mongodb`. Spring Modulith then records each event/listener pair in the
same transaction as the business change and marks it completed when the listener succeeds — an
outbox with at-least-once delivery. Make listeners idempotent.

Operational settings worth knowing:

- `spring.modulith.events.republish-outstanding-events-on-restart=true` re-sends incomplete
  publications at startup (use with care in multi-instance deployments).
- `spring.modulith.events.completion-mode` = `UPDATE` (default, keep rows), `DELETE` or
  `ARCHIVE`.
- Purge old completed entries with `CompletedEventPublications`, and resubmit stuck ones with
  `IncompleteEventPublications` (from `spring-modulith-events-api`), for example from a
  scheduled job.
- With JDBC, `spring.modulith.events.jdbc.schema-initialization.enabled=true` creates the
  table; in production prefer a Flyway/Liquibase migration.

### Externalising events

Annotate an event type with `@Externalized("target::key")` and add the matching
`spring-modulith-events-kafka` (or AMQP, JMS, SQS, SNS…) artifact to forward it to a broker after
commit, through the same registry. This is also the first step when a module is being prepared
for extraction.

## Persistence per module

- Each module owns its tables. Options, in increasing isolation: a shared schema with
  table-name prefixes, one schema per module, or a separate database (rarely needed inside a
  monolith).
- Keep each module's migrations in its own location or prefix so ownership is obvious, and
  check whether your Modulith version offers per-module Flyway support before building your
  own.
- Never join across modules' tables. If a module needs another module's data, it calls the API
  or keeps its own projection fed by events.

## Verification and tests

```java
class ModularityTest {

    static final ApplicationModules modules = ApplicationModules.of(CoworkApplication.class);

    @Test
    void verifiesModuleStructure() {
        modules.verify();   // fails on cycles and access to internal types
    }

    @Test
    void writesDocumentation() {
        new Documenter(modules).writeDocumentation();   // PlantUML/C4 diagrams + module canvases
    }
}
```

- Run `verify()` in CI on every build.
- `@ApplicationModuleTest` bootstraps one module (optionally with its dependencies) for an
  integration test; `Scenario` helps assert published events
  ([testing chapter](https://docs.spring.io/spring-modulith/reference/testing.html)).
- Details and Boot 4 test notes: [testing.md](testing.md).

## Runtime insight

`spring-modulith-actuator` exposes the module structure at `/actuator/modulith`;
`spring-modulith-observability-core` adds Micrometer spans and metrics for inter-module calls.
`spring-modulith-starter-insight` bundles both
([production-ready features](https://docs.spring.io/spring-modulith/reference/production-ready.html)).

## Inside a module

Pick the structure per module. A module with real rules can be hexagonal or DDD-shaped
internally; a reference-data module can be a single package of controller, service and
repository. Do not force hexagonal layering on trivial modules — the boundary at the module level
already gives most of the isolation.

## When to extract a module

Extract into a separate service only when a concrete signal appears:

- it must scale independently or has very different resource needs;
- a separate team owns it and needs its own release cadence;
- it needs a different technology, runtime or compliance zone;
- its events are already externalised and consumers no longer call its API synchronously.

Until then, the monolith keeps refactoring cheap and transactions local.
