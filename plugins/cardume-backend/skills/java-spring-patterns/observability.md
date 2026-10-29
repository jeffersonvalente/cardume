# Observability with Micrometer

Spring Boot instruments applications through Micrometer. The **Observation API** is the single
instrumentation point: one observation produces a timer (metrics), a span (traces) and log
correlation, depending on which handlers are registered
([Micrometer Observation](https://docs.micrometer.io/micrometer/reference/observation.html),
[Spring Boot: observability](https://docs.spring.io/spring-boot/reference/actuator/observability.html)).

Platform-wide concerns (collectors, backends, SLOs, alerting) belong to the platform skills; this
file covers the application side.

## Instrument with observations

Spring MVC, WebFlux, `RestClient`, `WebClient`, JDBC (with the relevant module), Kafka and
others are already observed. Add observations for business operations that matter:

```java
@Service
class CheckoutService {
    private final ObservationRegistry registry;

    CheckoutService(ObservationRegistry registry) { this.registry = registry; }

    Receipt checkout(Cart cart) {
        return Observation.createNotStarted("shop.checkout", registry)
                .lowCardinalityKeyValue("payment.method", cart.paymentMethod().name())
                .highCardinalityKeyValue("cart.id", cart.id().toString())
                .observe(() -> doCheckout(cart));
    }
}
```

Or annotate the method with `@Observed(name = "shop.checkout")`. Annotations need AOP: add the
AspectJ starter (`spring-boot-starter-aop` on Boot 3, renamed `spring-boot-starter-aspectj` on
Boot 4) and set `management.observations.annotations.enabled=true` (Boot 3.2+), which
registers the `ObservedAspect`. Self-invocation bypasses the aspect, as with transactions.

## Cardinality

- **Low-cardinality** keys become metric tags and span attributes. Use only bounded values:
  method, outcome, status class, region.
- **High-cardinality** keys go to spans only. Ids, emails, URLs with ids, free text and user
  names must **never** be metric tags: every distinct value creates a new time series and can
  overwhelm the metrics backend.
- Never put personal data in either; spans are often retained and widely visible.

## Filter noise

Drop observations you do not want — typically actuator and health-check traffic — with an
`ObservationPredicate` bean:

```java
@Bean
ObservationPredicate skipActuator() {
    return (name, context) -> !(context instanceof ServerRequestObservationContext server
            && server.getCarrier().getRequestURI().startsWith("/actuator"));
}
```

Sampling: Boot samples 10% of traces by default (`management.tracing.sampling.probability`);
raise it in non-production environments.

## Exporting telemetry

- **Boot 3.x:** add Micrometer Tracing with a bridge (`micrometer-tracing-bridge-otel` or
  `-brave`) plus an exporter, and a Micrometer registry for metrics (`micrometer-registry-otlp`,
  `-prometheus`, …).
- **Boot 4.x:** `spring-boot-starter-opentelemetry` brings what is needed to export **metrics
  and traces over OTLP** and auto-configures the OpenTelemetry SDK. OTLP trace export is
  configured under `management.opentelemetry.tracing.export.otlp.*`
  ([Spring Boot 4.0 tracing](https://docs.spring.io/spring-boot/4.0/reference/actuator/tracing.html)).
- **Boot 4 property rename:** `management.tracing.enabled` became
  `management.tracing.export.enabled`, and per-exporter switches follow the
  `management.tracing.export.<name>.enabled` pattern
  ([Boot 4.0 release notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)).
  Update configuration files and environment variables when migrating.

## Logs

- Boot adds trace and span ids to log lines when tracing is active (see
  `logging.pattern.correlation`), so logs and traces join up.
- Structured logging (`logging.structured.format.console=ecs` or `logstash`, Boot 3.4+) makes
  logs machine-readable without custom encoders.
- Log business identifiers deliberately at INFO; never log secrets, tokens or full payloads with
  personal data.

## Checklist

- Business-critical use cases have an observation with a stable, dotted name.
- No unbounded values in low-cardinality keys.
- Actuator noise filtered; sampling set per environment.
- Exporter configuration matches the Boot generation (3.x vs 4.x property names).
- `/actuator` exposure limited to what operations needs (`health`, `info`, `prometheus`/metrics).
