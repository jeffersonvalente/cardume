---
type: llm
focus: last_message
weight: 2
---

PASS if it identifies: missing transaction boundary (debit saved before the limit check/credit, so partial writes) and moves logic into a @Service method annotated @Transactional; `double` for money (use BigDecimal or minor units); validation before mutation; concurrency/lost updates (optimistic locking with @Version or pessimistic lock with consistent lock ordering); field injection replaced by constructor injection; `.get()` on Optional replaced by a domain exception mapped to 404/422 (e.g. @ControllerAdvice/ProblemDetail); a request DTO (record) with Bean Validation instead of query params, and a proper response/status. It should mention testing (e.g. Testcontainers integration test for the rollback case).
FAIL if it misses the transactional/partial-write bug or keeps double for money.
