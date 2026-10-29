# Testing Spring Boot Services

Everything in this file applies to Spring Boot 3.1+ unless a line says "Boot 4". The Boot 3 → 4
migration section is at the end; read it whenever the project is on, or moving to, Boot 4.x.
General test strategy lives in `cardume-qa:testing-patterns`.

## Choose the smallest test that proves the behaviour

| What you are checking | Test type |
|-----------------------|-----------|
| Domain rules, value-object invariants | Plain JUnit, no Spring |
| Controller mapping, validation, status codes, ProblemDetail bodies | `@WebMvcTest` slice + `MockMvc` (or `RestTestClient` on Boot 4) |
| Repository queries, mappings, locking | `@DataJpaTest` / `@JdbcTest` against a real database container |
| A whole use case with transactions, rollback, concurrency | `@SpringBootTest` + Testcontainers |
| Module boundaries and module-level behaviour | `ApplicationModules.verify()`, `@ApplicationModuleTest` |
| Layering and dependency rules | ArchUnit |

Slices load only the relevant part of the context, so they start fast and fail precisely
([Spring Boot: testing](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html)).

## Real infrastructure with Testcontainers

Use the production database engine in tests; H2 hides dialect, locking and constraint
differences. `@ServiceConnection` (Boot 3.1+) derives connection properties from the container,
so no `@DynamicPropertySource` boilerplate is needed
([Spring Boot: Testcontainers](https://docs.spring.io/spring-boot/reference/testing/testcontainers.html)).

```java
@SpringBootTest
@Testcontainers
class StockTransferIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer postgres = new PostgreSQLContainer("postgres:17-alpine");
    // Testcontainers 1.x: org.testcontainers.containers.PostgreSQLContainer<?> (generic)
    // Testcontainers 2.x: org.testcontainers.postgresql.PostgreSQLContainer

    @Autowired StockTransferService transfers;
    @Autowired StockLevelRepository stock;

    @Test
    void failedTransferLeavesBothWarehousesUnchanged() {
        var command = new MoveStock(WAREHOUSE_A, WAREHOUSE_B, "SKU-1", 1_000);   // more than A holds

        assertThatThrownBy(() -> transfers.move(command)).isInstanceOf(InsufficientStock.class);

        assertThat(stock.quantity(WAREHOUSE_A, "SKU-1")).isEqualTo(10);
        assertThat(stock.quantity(WAREHOUSE_B, "SKU-1")).isZero();
    }
}
```

Tips:

- Write a test for the **failure path** of every multi-write use case: it is the test that
  catches a missing or bypassed `@Transactional`.
- For lost-update checks, run two transfers concurrently (for example with an
  `ExecutorService` and a `CountDownLatch`) and assert the final totals.
- Do not annotate such integration tests with `@Transactional`: the test transaction would
  wrap the service's own and hide commit-time behaviour (and after-commit listeners).
- Reuse containers across test classes with a shared base class or a `@TestConfiguration`
  declaring the container as a `@ServiceConnection` bean; Boot's development-time
  `SpringApplication.from(...).with(...)` can reuse the same configuration for local runs.

## Architecture tests with ArchUnit

ArchUnit rules are plain tests over bytecode
([ArchUnit user guide](https://www.archunit.org/userguide/html/000_Index.html)). Keep them in the
test suite so every build checks them. Examples: [mvc-layered.md](mvc-layered.md#enforce-it-with-archunit),
[hexagonal.md](hexagonal.md#enforce-it-with-archunit). Useful general rules:

```java
@ArchTest
static final ArchRule noFieldInjection = noFields()
        .should().beAnnotatedWith(Autowired.class)
        .because("use constructor injection");

@ArchTest
static final ArchRule controllersDoNotTouchRepositories = noClasses()
        .that().areAnnotatedWith(RestController.class)
        .should().dependOnClassesThat()
        .areAssignableTo(org.springframework.data.repository.Repository.class);
```

When introducing rules into an existing codebase, `FreezingArchRule` records current violations
and fails only on new ones.

## Spring Modulith tests

- `ApplicationModules.of(App.class).verify()` in a unit test.
- `@ApplicationModuleTest` boots a single module; `BootstrapMode.DIRECT_DEPENDENCIES` adds its
  neighbours.
- `Scenario` / `PublishedEvents` assert that a use case published the expected events
  ([Spring Modulith: testing](https://docs.spring.io/spring-modulith/reference/testing.html)).

## Mocks

- Prefer real collaborators or hand-written fakes for your own ports; mock only at the edges
  you do not control.
- In unit tests, use Mockito directly with `@ExtendWith(MockitoExtension.class)`.
- In Spring tests, replace a bean with `@MockitoBean` / `@MockitoSpyBean` (Spring Framework
  6.2+). `@MockBean`/`@SpyBean` were deprecated in Boot 3.4 and removed in Boot 4.

## Boot 3 → 4 test migration

Source: [Spring Boot 4.0 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)
and [release notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes).
Check them for the exact patch version in use.

1. **Mock beans.** Replace `@MockBean` / `@SpyBean` with `@MockitoBean` / `@MockitoSpyBean`.
   The new annotations work on **test-class fields**, not inside `@Configuration` classes;
   declare shared mocks on the test class (for example `@MockitoBean(types = …)`).
2. **Mockito listener.** `MockitoTestExecutionListener` is gone. If `@Mock` / `@Captor` fields
   stop being initialised, add `@ExtendWith(MockitoExtension.class)`.
3. **Test starters per technology.** Test support is split into
   `spring-boot-starter-<technology>-test` starters (for example the web MVC, data JPA or
   security test starters); each brings `spring-boot-starter-test`. Declare the ones for the
   technologies you test.
4. **MockMvc.** `@SpringBootTest` no longer configures `MockMvc` by itself; add
   `@AutoConfigureMockMvc`.
5. **HTTP clients in tests.** `@SpringBootTest` no longer provides `TestRestTemplate`. Prefer
   the new `RestTestClient` (`@AutoConfigureRestTestClient`); if you keep
   `TestRestTemplate`, add `@AutoConfigureTestRestTemplate` and its dependency, and update its
   import to the new package.
6. **Moved imports.** Slice annotations moved into technology-specific modules (for example
   `@WebMvcTest` now lives under `org.springframework.boot.webmvc.test.autoconfigure`). Let the
   IDE re-resolve imports after adding the right test starter rather than guessing packages.
7. **Testcontainers 2.0.** Boot 4 manages Testcontainers 2.x: module artifacts gained a
   `testcontainers-` prefix (`org.testcontainers:testcontainers-postgresql`), container classes
   moved to per-module packages (`org.testcontainers.postgresql.PostgreSQLContainer`), and JUnit 4
   support was removed. Update coordinates and imports together.
