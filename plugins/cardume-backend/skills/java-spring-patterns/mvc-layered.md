# Layered (MVC) Services

The classic Spring shape: web layer → service layer → persistence layer. It is the right
default for CRUD-heavy services, admin back-offices and small APIs, because every Spring
developer can read it immediately.

## Layout

Group by feature first, then by layer inside the feature, so related code stays together and a
feature can later become a module ([Fowler, PresentationDomainDataLayering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)).

```text
com.example.rooms
├── RoomsApplication.java
├── booking
│   ├── web          BookingController, request/response records
│   ├── service      BookingService (@Service, @Transactional use cases)
│   └── persistence  BookingEntity, BookingRepository (Spring Data)
└── catalog
    ├── web
    ├── service
    └── persistence
```

For a very small service, a flat `web` / `service` / `persistence` split is acceptable.

## Rules

- **Dependencies point downward only:** web → service → persistence. Persistence never calls a
  service; services never depend on controllers or web types.
- **Controllers stay thin:** validate the request record, call one service method, map the
  result to a response record and status.
- **Services own transactions and rules.** One public method per use case, annotated
  `@Transactional` ([spring-conventions.md](spring-conventions.md#transactions)).
- **Entities do not leave the service layer** through the API: map to response records, so the
  database schema is not your public contract and lazy-loading surprises stay inside the
  transaction.
- Errors map to `ProblemDetail` in one `@RestControllerAdvice`.

## Enforce it with ArchUnit

Run layer rules as ordinary tests so violations fail the build
([ArchUnit user guide: layer checks](https://www.archunit.org/userguide/html/000_Index.html#_layer_checks)).

```java
@AnalyzeClasses(packages = "com.example.rooms")
class LayeringTest {

    @ArchTest
    static final ArchRule layers = layeredArchitecture()
            .consideringOnlyDependenciesInLayers()
            .layer("Web").definedBy("..web..")
            .layer("Service").definedBy("..service..")
            .layer("Persistence").definedBy("..persistence..")
            .whereLayer("Web").mayNotBeAccessedByAnyLayer()
            .whereLayer("Service").mayOnlyBeAccessedByLayers("Web")
            .whereLayer("Persistence").mayOnlyBeAccessedByLayers("Service");
}
```

## When not to use it

- The domain has rich rules that should be tested without Spring or a database → consider
  [hexagonal](hexagonal.md).
- Several teams own different parts → define contexts and modules first
  ([modular-monolith.md](modular-monolith.md)).
- Services grow into "god services" with dozens of methods: that is the signal that the
  feature needs its own domain model, not more layers.
