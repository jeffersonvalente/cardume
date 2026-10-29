# Event-Driven Architecture with Spring

## Name the pattern

"Event-driven" means several different things. Fowler's
[What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html)
separates four patterns; always say which one a design uses:

| Pattern | What the event carries | Consequence |
|---------|------------------------|-------------|
| Event notification | "Something happened" plus an id | Consumers call back for details; low coupling to data shape, more traffic |
| Event-carried state transfer | The data consumers need | Consumers keep local copies and work when the source is down; data is duplicated and eventually consistent |
| Event sourcing | Every state change, as the system of record | See [cqrs-event-sourcing.md](cqrs-event-sourcing.md) |
| CQRS | Often events feed the read model | See [cqrs-event-sourcing.md](cqrs-event-sourcing.md) |

Fowler also notes that the flow becomes harder to see: nothing in the publisher's code shows
what happens next. Compensate with tracing ([observability.md](observability.md)) and
generated module documentation.

## Inside one application: Spring events

Publish with `ApplicationEventPublisher` (or aggregate events via Spring Data) and listen with
`@EventListener` or `@TransactionalEventListener`
([Spring Framework: transaction-bound events](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)).

- `@EventListener` runs synchronously, inside the publisher's transaction. A failure rolls the
  publisher back too.
- `@TransactionalEventListener` binds the listener to a transaction phase:
  `AFTER_COMMIT` (default), `AFTER_ROLLBACK`, `AFTER_COMPLETION` or `BEFORE_COMMIT`. Use
  `AFTER_COMMIT` for side effects that must only happen when data is really saved.
- **Pitfall:** if the event is published when **no transaction is active**, a
  `@TransactionalEventListener` is silently not invoked — unless you set
  `fallbackExecution = true`. Check that the publishing method really is transactional (and
  not suffering self-invocation, see [spring-conventions.md](spring-conventions.md#transactions)).
- Code in an `AFTER_COMMIT` listener runs after the commit; if it must write to the database,
  give it its own transaction (`Propagation.REQUIRES_NEW`).
- An in-memory event is lost if the process dies between commit and listener execution. When
  that matters, use the registry below.

## Between modules: Spring Modulith outbox

`@ApplicationModuleListener` plus the Event Publication Registry stores each publication in the
business transaction and completes it after the listener succeeds — a transactional outbox with
at-least-once delivery
([Spring Modulith events](https://docs.spring.io/spring-modulith/reference/events.html)).
Setup and operations: [modular-monolith.md](modular-monolith.md#event-publication-registry-transactional-outbox).

## Between services: a broker

- **Never send to the broker inside the business transaction.** If the commit fails after the
  send, consumers see an event for data that does not exist; if the send fails after the
  commit, the event is lost. Write the event in the same transaction (outbox) and relay it.
  Spring Modulith's `@Externalized` events do exactly this for Kafka, AMQP, JMS and others.
- For direct Kafka work, use [Spring for Apache Kafka](https://docs.spring.io/spring-kafka/reference/):
  `KafkaTemplate` to send, `@KafkaListener` to consume, `DefaultErrorHandler` with a
  dead-letter topic for poison messages.
- Consumers must be **idempotent** (at-least-once delivery means duplicates): store processed
  event ids or make the handler's effect naturally idempotent.
- Treat event payloads as a public contract: version them, add fields compatibly, and document
  them (AsyncAPI is the usual format).
- Choose a partition key that preserves the order you need (usually the aggregate id).

## Event design

- Name events in the past tense, in the domain's language (`DeskReleased`, not
  `DeskUpdateEvent`).
- Model a context's events as records implementing a sealed interface, so consumers can switch
  exhaustively ([java-language.md](java-language.md#pattern-matching-in-switch-21)).
- Include an event id, the aggregate id, and the time it happened; add a schema version once the
  event crosses a process boundary.
