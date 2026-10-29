# Capability Baseline

Use this file to decide whether an idiom is available to the project. Find the project's JDK
release first (see SKILL.md), then use only features at or below that release.

## How to read it

- **Final in** is the first JDK release where the feature is a standard, permanent part of the
  language or platform. Code written against an LTS baseline (17, 21, 25) can use everything
  final at or before that release.
- **Preview** features exist earlier but only compile and run with `--enable-preview`, and may
  change between releases. Do not standardise them in production code; mention them only as
  "available later" or behind an explicit team decision.
- LTS releases: 17 (2021), 21 (2023), 25 (GA 2025-09-16, see the
  [JDK 25 project page](https://openjdk.org/projects/jdk/25/)). Non-LTS releases (22–24, 26…)
  are fine when the team upgrades every six months.

## Language and platform features

| Feature | Final in | Source | Notes |
|---------|----------|--------|-------|
| Text blocks | 15 | [JEP 378](https://openjdk.org/jeps/378) | Available on any 17+ baseline |
| Pattern matching for `instanceof` | 16 | [JEP 394](https://openjdk.org/jeps/394) | |
| Records | 16 | [JEP 395](https://openjdk.org/jeps/395) | Usable on a 17 baseline |
| Sealed classes and interfaces | 17 | [JEP 409](https://openjdk.org/jeps/409) | |
| Record patterns | 21 | [JEP 440](https://openjdk.org/jeps/440) | Deconstruct records in `instanceof`/`switch` |
| Pattern matching for `switch` | 21 | [JEP 441](https://openjdk.org/jeps/441) | Exhaustive over sealed types; `case null` opt-in |
| Virtual threads | 21 | [JEP 444](https://openjdk.org/jeps/444) | Throughput for blocking I/O |
| Sequenced collections | 21 | [JEP 431](https://openjdk.org/jeps/431) | `getFirst()`, `reversed()` … |
| Unnamed variables and patterns (`_`) | 22 | [JEP 456](https://openjdk.org/jeps/456) | |
| Stream gatherers | 24 | [JEP 485](https://openjdk.org/jeps/485) | Custom intermediate stream operations |
| `synchronized` without pinning virtual threads | 24 | [JEP 491](https://openjdk.org/jeps/491) | Removes most carrier pinning |
| Scoped values | 25 | [JEP 506](https://openjdk.org/jeps/506) | Alternative to `ThreadLocal` for virtual threads |
| Flexible constructor bodies | 25 | [JEP 513](https://openjdk.org/jeps/513) | Validate arguments before `super(...)` |
| Compact source files / instance `main` | 25 | [JEP 512](https://openjdk.org/jeps/512) | Scripts and teaching; rarely in services |

Structured concurrency was still a preview API in JDK 25
([JEP 505](https://openjdk.org/jeps/505)); check the release notes of the project's JDK before
recommending it.

For releases after this table, read the JDK's release notes and the JEP index
(<https://openjdk.org/jeps/0>) rather than assuming the list is complete.

## What changes with the baseline

| Baseline | Practical consequence |
|----------|-----------------------|
| 17 | Records, sealed types, text blocks, `instanceof` patterns. Use `if`/`instanceof` chains or the visitor pattern instead of pattern `switch`. No virtual threads. |
| 21 | Adds exhaustive pattern `switch`, record patterns, virtual threads. Avoid `synchronized` around blocking calls on virtual threads (pinning). |
| 24 | `synchronized` no longer pins in the common cases, so lock choice is again about semantics, not carrier threads. |
| 25+ | Scoped values and flexible constructor bodies are final; prefer scoped values over `ThreadLocal` for per-request context on virtual threads. |

## Framework baseline

| Spring Boot | Spring Framework | Minimum Java | Notes |
|-------------|------------------|--------------|-------|
| 3.x | 6.x | 17 | Jakarta EE namespace (`jakarta.*`). Virtual-thread support from 3.2 with Java 21. |
| 4.x | 7.x | 17 | GA 2025-11-20; first-class support for Java 25; modularised auto-configuration and test starters. |

Sources: [Spring Boot 4.0 release notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes),
[Spring Boot 4.0 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide),
[Spring Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html).

The conventions in this skill (constructor injection, `@Transactional` services, ProblemDetail,
Testcontainers with `@ServiceConnection`, Micrometer Observation, Spring Modulith) carry over from
3.x to 4.x. What moves in 4.x is mostly packaging: starters, test annotations and some property
names — see [testing.md](testing.md) and [observability.md](observability.md). Always confirm
the exact Boot version before giving dependency coordinates or property names.
