# Domain-Driven Design in Java and Spring

Primary reference: Eric Evans, [DDD Reference](https://www.domainlanguage.com/ddd/reference/).
Public example: [ddd-by-examples/library](https://github.com/ddd-by-examples/library).

DDD is worth its cost when the business rules are the hard part. Do the strategic work first;
tactical patterns without boundaries produce a large, tangled model with DDD vocabulary.

## Strategic design first

- **Ubiquitous language.** Use the domain experts' words in code: class, method and event names
  match how the business talks (`Membership.suspend()`, not `MemberService.updateStatus(3)`).
  When a word means different things to different groups, that is a context boundary.
- **Bounded contexts.** Each context owns its model and its language. "Customer" in billing
  (payment method, invoices) is not the same model as "Customer" in support (tickets, SLA).
- **Context map.** Record how contexts relate (shared kernel, customer/supplier, conformist,
  anticorruption layer, open host service / published language). The map decides integration
  style: a downstream context protecting itself from a messy upstream gets an
  anticorruption layer that translates.

Example for a co-working space: contexts `membership`, `booking` and `billing`. Booking needs to
know whether a member may book; it asks membership's published API or reacts to its events,
and keeps its own small view of what it needs.

## Tactical building blocks mapped to Java

| Building block | Java / Spring expression |
|----------------|--------------------------|
| Value object | `record` with invariants in the compact constructor (`DeskId`, `TimeSlot`, `Money`) |
| Entity | Class with identity and behaviour methods; no public setters |
| Aggregate | One root entity guarding invariants for a cluster; load and save it as a unit; reference other aggregates by id |
| Domain event | `record` implementing a context's `sealed interface` of events (`BookingConfirmed`, `BookingCancelled`) |
| Repository | Interface in the domain, expressed in domain terms; implemented by an adapter using Spring Data |
| Domain service | Stateless class for a rule that spans aggregates and belongs to none |
| Application service | Use-case orchestration and transaction boundary; no business rules of its own |

```java
public sealed interface BookingEvent permits BookingConfirmed, BookingCancelled {
    BookingId bookingId();
}

public record BookingConfirmed(BookingId bookingId, DeskId desk, TimeSlot slot) implements BookingEvent {}
public record BookingCancelled(BookingId bookingId, String reason) implements BookingEvent {}
```

```java
// domain
public interface Bookings {
    Optional<Booking> byId(BookingId id);
    boolean overlaps(DeskId desk, TimeSlot slot);
    void save(Booking booking);
}

// adapter
@Repository
class JpaBookings implements Bookings {
    private final BookingJpaRepository jpa;   // Spring Data interface on BookingEntity
    // map entity <-> domain object here
}
```

Aggregate guidelines:

- Keep aggregates small; one transaction modifies one aggregate. Changes to other aggregates
  happen through domain events and eventual consistency.
- Enforce invariants inside the aggregate's methods, not in services
  (`booking.cancel(reason, clock)` refuses to cancel a past booking).
- Collect domain events in the aggregate and publish them after saving. With Spring Data,
  `@DomainEvents` / `AbstractAggregateRoot` publish them on `save`
  ([Spring Data: domain events](https://docs.spring.io/spring-data/commons/reference/repositories/core-domain-events.html)).

## Package structure that "screams" the domain

Top-level packages are contexts, not technical layers:

```text
com.example.cowork
├── membership   (API: MembershipApi, events)
├── booking      (API: BookingApi; internal: domain, application, persistence)
└── billing      (API: …)
```

With Spring Modulith, each direct sub-package of the application's root package is a module,
so contexts become verifiable modules for free — see [modular-monolith.md](modular-monolith.md).

## When not to use it

- No domain expert and no complex rules: tactical DDD on CRUD produces anaemic objects behind
  extra interfaces. Use [layered](mvc-layered.md).
- Do not adopt event sourcing or CQRS just because the code is "DDD"; they are separate
  decisions ([cqrs-event-sourcing.md](cqrs-event-sourcing.md)).
