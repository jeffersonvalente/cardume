# Hexagonal Architecture (Ports and Adapters)

Alistair Cockburn's stated intent is to "allow an application to equally be driven by users,
programs, automated test or batch scripts, and to be developed and tested in isolation from its
eventual run-time devices and databases"
([Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)).

## The core idea: inside versus outside

The hexagon is not about six sides or layers. The only distinction that matters is
**inside** (the application and its domain) versus **outside** (everything it talks to).
The inside defines interfaces — **ports** — in its own terms; the outside provides
**adapters** that translate between a technology and a port.

- **Driving (primary) side:** actors that start an interaction — HTTP controllers, message
  listeners, schedulers, tests. Their adapters call an inbound port (a use-case interface).
- **Driven (secondary) side:** things the application uses — database, broker, payment
  provider, clock. The application calls an outbound port; an adapter implements it.

The asymmetry matters: driving adapters *depend on* the inside and call it; driven adapters
*implement* interfaces the inside owns. Either way, source dependencies point inward.

## Layout example

```text
com.example.parcels
├── application
│   ├── port
│   │   ├── in    TrackParcel, RegisterParcel           (use-case interfaces)
│   │   └── out   ParcelStore, CarrierGateway           (what the core needs)
│   └── service   RegisterParcelService implements RegisterParcel
├── domain        Parcel, TrackingNumber, ParcelStatus  (plain Java)
├── adapter
│   ├── in
│   │   ├── web        ParcelController
│   │   └── messaging  CarrierEventListener
│   └── out
│       ├── persistence  JpaParcelStore implements ParcelStore (+ entities, mappers)
│       └── carrier      HttpCarrierGateway implements CarrierGateway
└── config        wiring of application services as beans
```

The public example [thombergs/buckpal](https://github.com/thombergs/buckpal) follows the same
split and is a useful reference.

## A framework-free core

- `domain` and `application` import no Spring, JPA, Jackson or Jakarta Persistence types. That
  keeps them testable with plain JUnit and makes framework upgrades an adapter concern.
- JPA entities live in the persistence adapter and are mapped to domain objects. Mapping costs
  code; it buys a domain model shaped by rules instead of by tables.
- Transactions are an application concern but `@Transactional` is a Spring annotation. Two
  common choices: annotate the application service and accept that single dependency, or keep
  the service plain and wrap it in a transactional decorator in `config`. Pick one and state
  it.

## Wiring adapters with DI

Register plain application services as beans in a configuration class, so the core does not need
`@Service`:

```java
@Configuration
class ParcelWiring {

    @Bean
    RegisterParcel registerParcel(ParcelStore store, CarrierGateway carrier, Clock clock) {
        return new RegisterParcelService(store, carrier, clock);
    }
}
```

Adapters are ordinary Spring components (`@RestController`, `@Repository`, `@Component`)
implementing the outbound port interfaces; Spring injects whichever implementation is present,
and tests can pass an in-memory fake instead.

## Enforce it with ArchUnit

```java
@AnalyzeClasses(packages = "com.example.parcels")
class HexagonTest {

    @ArchTest
    static final ArchRule coreIsFrameworkFree = noClasses()
            .that().resideInAnyPackage("..domain..", "..application..")
            .should().dependOnClassesThat()
            .resideInAnyPackage("org.springframework..", "jakarta.persistence..", "com.fasterxml.jackson..");

    @ArchTest
    static final ArchRule coreDoesNotSeeAdapters = noClasses()
            .that().resideInAnyPackage("..domain..", "..application..")
            .should().dependOnClassesThat().resideInAPackage("..adapter..");
}
```

If you accept `@Transactional` in application services, exclude
`org.springframework.transaction..` from the first rule explicitly rather than weakening it.
ArchUnit also ships `onionArchitecture()` for this shape
([ArchUnit user guide](https://www.archunit.org/userguide/html/000_Index.html#_onion_architecture)).

## When not to use it

- CRUD services whose "domain" is the table: ports and mappers add ceremony without isolation
  value. Use [layered](mvc-layered.md).
- Modules inside a modular monolith that are trivial: give hexagonal structure only to the
  modules whose rules justify it.
- When nobody will ever drive the core from anything but one controller and one database, be
  honest that the benefit is testability alone — sometimes still worth it, sometimes not.
