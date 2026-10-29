# CQRS and Event Sourcing

## Choosing the level

| Situation | Use | Why |
|-----------|-----|-----|
| CRUD screens, reads mirror writes | Plain CRUD: an ordinary layered or hexagonal service | Nothing to separate; extra models only add code |
| Heavy reporting or search beside a transactional core | Lightweight CQRS: query projections, same database | Read shapes diverge from the aggregate, storage does not |
| Read load far beyond write load, different storage needs | CQRS with a separate read store fed by events | Reads scale and evolve on their own |
| Regulatory history, temporal queries, replayable projections | Event sourcing (with CQRS), in that one bounded context | History itself is the requirement |
| "We might need history later" | Domain events plus an audit table now; revisit later | Keeps the option open without the cost |

Both patterns cost more than they look. Fowler's [CQRS](https://martinfowler.com/bliki/CQRS.html)
note warns that for most systems it adds risky complexity and should be confined to specific
bounded contexts, never the whole system. His
[Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) article shows the same for
the log: external systems, code changes and event schema changes all need deliberate handling
during replay.

So when someone asks for "CQRS" or "event sourcing", check the need before picking a row:

- Do reads and writes really differ in shape, volume or scaling?
- Is a complete, replayable history a business requirement (regulation, audit, temporal
  questions like "what did we know on 1 March?"), or is an audit log table enough?
- Can the users tolerate read models that lag behind writes?

If the answers are "no", recommend the simpler design and say why.

## Lightweight CQRS (no event sourcing)

Most of the benefit comes from separating the **models**, not the infrastructure:

- **Commands** go through the domain model (aggregates, invariants, transactions).
- **Queries** bypass the domain model and read purpose-built projections: a JPA/JDBC query
  returning records, a database view, or Spring Data interface/record projections.
- Both can share one database. Start there; split storage only when load requires it.

```java
// write side
@Transactional
public void reschedule(RescheduleBooking cmd) {
    Booking booking = bookings.byId(cmd.bookingId()).orElseThrow(() -> new BookingNotFound(cmd.bookingId()));
    booking.reschedule(cmd.newSlot(), clock);
    bookings.save(booking);
}

// read side: no aggregate, just the data the screen needs
public record DeskOccupancyRow(String deskCode, LocalDate day, int bookedHours) {}

@Query("""
       select new com.example.cowork.booking.query.DeskOccupancyRow(d.code, b.day, sum(b.hours))
       from BookingEntity b join b.desk d
       where b.day between :from and :to
       group by d.code, b.day
       """)
List<DeskOccupancyRow> occupancy(LocalDate from, LocalDate to);
```

When the read side moves to its own store, feed it from domain events
([eda.md](eda.md)) and make the projection rebuildable.

## Event sourcing

State is stored as the sequence of events that produced it; current state is a fold over
those events ([Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)). Event sourcing
implies CQRS (the event log is not queryable in useful ways); CQRS does not imply event sourcing.

What it buys:

- **Complete rebuild**: projections can be dropped and recomputed from the log.
- **Temporal queries**: reconstruct state at any past point.
- **Replay**: re-run events to fix a bug in a projection or to feed a new consumer.
- **Snapshots** are an optimisation, a cache of folded state, never the source of truth.

What it costs:

- Events are a permanent public schema: plan versioning (upcasters) from day one.
- Side effects (emails, payments) must not repeat during replay.
- Querying requires projections; there is no "just select from the table".
- Team learning curve and specialised tooling.

### Tooling on the JVM

[Axon Framework](https://docs.axoniq.io/) is the established option: aggregates handle commands
and apply events, event processors build projections, and Axon Server (or a JPA/JDBC event store)
stores events. It plugs into Spring Boot through its starter; check the Axon documentation for
the release that supports the project's Boot generation before adding it.

Alternatives exist (EventStoreDB clients, hand-rolled stores on PostgreSQL). Hand-rolled is
reasonable for one small aggregate type; beyond that, a framework pays for itself.
