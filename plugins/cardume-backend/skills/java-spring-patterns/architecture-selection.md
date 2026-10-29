# Choosing an Architecture Style

An architecture style is a bet about where change will come from. Layers bet that the
technology tiers change independently; hexagonal bets that the outside world (UI, database,
providers) changes more than the rules; DDD bets that the business model is the hard part;
modules bet that the system grows by features owned by different people; CQRS and event
sourcing bet that reading and history matter as much as writing; events bet that parts of the
system should not wait for each other.

Pick the style whose bet matches the forces you can see today, not the ones you imagine for
next year. Every style here costs indirection, and indirection only pays when the force it
answers is real.

## The forces to look for

Before reading the styles, gather evidence on these. Each one comes from the codebase, the
backlog or the team, not from preference.

- **Where the complexity is.** Mostly moving data between screens and tables, or rules that
  domain experts argue about (pricing, eligibility, scheduling, settlement)?
- **Who changes the code.** One team, or several teams that step on each other in the same
  packages and release train?
- **How the outside varies.** One controller and one database forever, or several entry points
  (REST, messages, batch, CLI) and swappable providers?
- **How reads and writes differ.** Same shape and volume, or dashboards and search that need
  data the write model does not keep?
- **What consistency the business needs.** Must everything be correct the instant a request
  returns, or can parts of the system catch up a moment later?
- **What history is worth.** Is "what was the state on 1 March, and why" a legal or business
  requirement, or is an audit table enough?

## Layered (feature-first)

**What it buys.** The shape every Spring developer can read on day one: controller, service,
repository. Fowler's
[PresentationDomainDataLayering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)
explains why the split still matters: presentation, domain logic and data access change for
different reasons. Grouping by feature first, then by layer inside the feature, keeps related
code together and leaves each feature ready to become a module later.

**What it costs.** Nothing stops the domain from leaking into services as procedural code over
anaemic entities, and nothing stops persistence types from reaching the controller. Over time
the "service" becomes the place where every rule lives, and it grows without a natural seam.

**You need it when** the work is CRUD-heavy, rules are simple validations, one team owns the
service, and speed of onboarding matters more than isolation. This is the right default for
most new Spring services.

**You don't when** rules are tested only by spinning up Spring and a database because they are
tangled with JPA, or when a single service class has passed a few dozen public methods. That is
the domain asking for its own model.

Spring shape: [mvc-layered.md](mvc-layered.md).

## Hexagonal (ports and adapters)

**What it buys.** Alistair Cockburn's
[Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) aims to let an
application be driven equally by users, programs, tests or batch scripts, and to be developed
and tested in isolation from its runtime devices and databases. The core owns interfaces
(ports) in its own vocabulary; adapters translate HTTP, JPA, Kafka or a payment provider to
those ports. The rules become plain Java you can test in milliseconds, and replacing a provider
touches one adapter. [thombergs/buckpal](https://github.com/thombergs/buckpal) is a worked
Spring example.

**What it costs.** Mapping. Every boundary crossing needs a translation (request → command,
domain → entity, entity → domain), and for a CRUD service those mappers outnumber the rules.
Teams also over-apply it, creating a port per repository method.

**You need it when** the same use cases are triggered from more than one place, an external
dependency is volatile or will be replaced, or the rules are valuable enough that you want them
free of framework annotations and fast to test.

**You don't when** the core is a thin pass-through to tables. Then the only benefit is
testability, and Spring's test slices already give most of it cheaply.

Spring shape: [hexagonal.md](hexagonal.md).

## Domain-Driven Design

**What it buys.** DDD is less a structure than a way of finding the right boundaries and the
right words. Evans' [DDD Reference](https://www.domainlanguage.com/ddd/reference/) puts the
strategic tools first: a ubiquitous language shared with domain experts, bounded contexts that
each own one consistent model (Fowler,
[BoundedContext](https://martinfowler.com/bliki/BoundedContext.html)), and a context map of how
they relate. Tactical patterns (aggregates, value objects, domain events) then keep invariants
inside small consistency boundaries.
[ddd-by-examples/library](https://github.com/ddd-by-examples/library) shows it in Spring.

**What it costs.** Time with domain experts, and a model that must keep evolving. Tactical
patterns without the strategic work give you DDD vocabulary over the same tangle, plus extra
interfaces.

**You need it when** the business rules are the reason the software exists, the same word
means different things to different departments, and you have access to people who can explain
the domain.

**You don't when** nobody can explain the rules beyond "save this form", or the rules live in a
third-party product you only integrate with. Fowler's
[AnemicDomainModel](https://martinfowler.com/bliki/AnemicDomainModel.html) warns against
domain objects without behaviour; the opposite mistake is building aggregates for data that has
no invariants.

Spring shape: [ddd.md](ddd.md). DDD fits inside either a layered or a hexagonal module; it
decides the boundaries and the model, not the package layering.

## Modular monolith

**What it buys.** One deployable, one database transaction when you need it, and boundaries
that are verified rather than hoped for. The
[Spring Modulith reference](https://docs.spring.io/spring-modulith/reference/fundamentals.html)
treats each direct sub-package of the application's main package as an application module; its
nested packages are internal by default, other modules may only use its top-level API, and
`ApplicationModules.verify()` fails the build on cycles or access to another module's internals.
Modules talk through Spring application events, with an event publication registry that makes
delivery survive crashes
([Spring Modulith: events](https://docs.spring.io/spring-modulith/reference/events.html)).
Fowler's [MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html) argues for this
path: boundaries are hard to guess up front and cheap to move inside one codebase.

**What it costs.** Discipline at the module API, and accepting eventual consistency between
modules that talk by events. A shared database invites joins across module tables; keep tables
owned by one module.

**You need it when** the system has several business capabilities, more than one team or
sub-team, and someone has started saying "microservices" mostly to get boundaries. Modules give
the boundaries without the network.

**You don't when** the service is small and does one thing. A single module is just a package.

Spring shape: [modular-monolith.md](modular-monolith.md), including the concrete signals that
justify extracting a module into its own service.

## CQRS and event sourcing

**What it buys.** CQRS separates the model that changes state from the models that answer
questions, so each can have the shape and storage that suits it. Event sourcing stores every
change as an event and derives state from them, giving a complete, replayable history and the
ability to build new read models from the past. Axon
([AxonIQ docs](https://docs.axoniq.io/)) packages both for Spring.

**What it costs.** Fowler is explicit that for most systems
[CQRS](https://martinfowler.com/bliki/CQRS.html) adds risky complexity and should be confined to
the bounded context that needs it. [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
adds event versioning, replay that must not re-trigger external effects, and read models that
lag behind writes.

**You need it when** reads and writes really diverge (heavy search or reporting next to a
transactional core), when history is a requirement and not a nice-to-have, or when temporal
questions ("what did we know then?") come from the business. Even then, start with
query-side projections over the same database before separate stores.

**You don't when** reads mirror writes, users expect to read their own write immediately, or
"we might need history someday" is the only argument. Domain events plus an audit table answer
that for a fraction of the cost.

Spring shape: [cqrs-event-sourcing.md](cqrs-event-sourcing.md).

## Event-driven

**What it buys.** Producers stop knowing their consumers, slow work leaves the request path,
and parts of the system keep working when others are down. Fowler's
[What do you mean by "Event-Driven"?](https://martinfowler.com/articles/201701-event-driven.html)
separates four things under the label: event notification, event-carried state transfer, event
sourcing and CQRS. Say which one you mean; they have different costs.

**What it costs.** The flow disappears from the code: nothing in the publisher shows what
happens next. You need tracing, idempotent consumers, a decision about ordering and
duplicates, and an outbox (or Modulith's publication registry) so an event is published if and
only if the transaction committed.

**You need it when** a side effect must not block or fail the main operation (emails,
projections, notifications), several independent reactions follow one fact, or another
module or service needs to know without being called.

**You don't when** the caller needs the result to continue, or when the "event" is really a
command to one specific receiver. A direct method call inside a transaction is simpler and
easier to reason about.

Spring shape: [eda.md](eda.md), from in-process `@TransactionalEventListener` to Kafka.

## How the styles combine

These are not rival options on one axis. Modular monolith is about *deployment and team
boundaries*; layered and hexagonal are about *how one module is organised inside*; DDD is about
*where the boundaries go and what the model says*; CQRS, event sourcing and events are about
*how data and decisions flow*. A realistic system mixes them per module.

A co-working booking platform, for example, might be a modular monolith with three modules.
`membership` is plain layered CRUD. `booking`, where the overlap and cancellation rules live, is
hexagonal with a DDD aggregate per desk-day. `billing` reacts to booking events through the
Modulith publication registry and keeps a lightweight CQRS projection for invoices. No module
pays for a style it does not need.

When the evidence is mixed, choose the simpler style and keep the door open: feature-first
packages can become modules, a service with a clear use-case method can gain ports later, and
domain events published today can feed a read model tomorrow. Moving the other way, removing
ports, events or event-sourced history, is much harder.

## Write the decision down

A style choice is expensive to reverse and someone will ask why. Record it with
`cardume-core:adr`, naming the forces you observed above, the styles you rejected and the
signal that would make you revisit the choice. Enforce what you chose with ArchUnit or
`ApplicationModules.verify()` so the decision survives the next deadline
([testing.md](testing.md)).
