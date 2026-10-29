# Instrumentation Reference

Short, current-practice snippets. Package names and flags evolve; when a detail differs in the
user's version, keep the concepts (SDK init before app code, resource attributes, OTLP to a
Collector, log correlation) and check the language's OTel docs for the exact API.

## Common environment (all languages)

```bash
OTEL_SERVICE_NAME=checkout-api
OTEL_RESOURCE_ATTRIBUTES=service.version=1.42.0,deployment.environment.name=prod
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318   # 4317 for gRPC
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=1.0          # keep 1.0 when the Collector does tail sampling
OTEL_PROPAGATORS=tracecontext,baggage
```

Configure through environment variables rather than code where possible, so the same image runs
in every environment.

## Node.js (TypeScript)

```bash
npm i @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node \
      @opentelemetry/exporter-trace-otlp-http @opentelemetry/exporter-metrics-otlp-http
```

```ts
// instrumentation.ts — load before the app: node --import ./instrumentation.js app.js
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter(),
  metricReader: new PeriodicExportingMetricReader({ exporter: new OTLPMetricExporter() }),
  instrumentations: [getNodeAutoInstrumentations({
    '@opentelemetry/instrumentation-fs': { enabled: false }, // noisy
  })],
});
sdk.start();
process.on('SIGTERM', () => sdk.shutdown());
```

Manual span and log correlation (pino):

```ts
import { trace, SpanStatusCode } from '@opentelemetry/api';
const tracer = trace.getTracer('checkout');

await tracer.startActiveSpan('checkout.place_order', async (span) => {
  try {
    span.setAttribute('order.items_count', items.length);   // bounded, no PII
    return await placeOrder(items);
  } catch (err) {
    span.recordException(err as Error);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw err;
  } finally { span.end(); }
});
// @opentelemetry/instrumentation-pino (included in auto-instrumentations) injects trace_id/span_id.
```

Zero-code alternative: `node --require @opentelemetry/auto-instrumentations-node/register app.js`.

## Python

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install          # installs instrumentations for detected libraries
opentelemetry-instrument python -m app      # or: opentelemetry-instrument gunicorn app:app
```

With gunicorn/uvicorn pre-fork workers, initialize the SDK per worker (post-fork hook), not in
the master process.

```python
from opentelemetry import trace
tracer = trace.get_tracer("checkout")

with tracer.start_as_current_span("checkout.place_order") as span:
    span.set_attribute("order.items_count", len(items))
    place_order(items)
```

Log correlation: `OTEL_PYTHON_LOG_CORRELATION=true` adds `otelTraceID`/`otelSpanID` to stdlib
`logging` records; map them to `trace_id`/`span_id` in the JSON formatter (e.g.
`python-json-logger` or `structlog` processor reading `trace.get_current_span().get_span_context()`).

## Java / Spring Boot

Option A, zero-code Java agent (works for any JVM framework):

```bash
java -javaagent:/otel/opentelemetry-javaagent.jar -jar app.jar
```

Option B, Spring Boot starter (native-image friendly, configured in `application.yml`):

```xml
<dependency>
  <groupId>io.opentelemetry.instrumentation</groupId>
  <artifactId>opentelemetry-spring-boot-starter</artifactId>
</dependency>  <!-- version from the opentelemetry-instrumentation-bom -->
```

Spring Boot 3.x also ships Micrometer Tracing/Observation with an OTLP exporter; if the codebase
already uses Micrometer, keep it and export OTLP rather than mixing two tracing APIs.

```java
@WithSpan("checkout.place_order")
public Order placeOrder(@SpanAttribute("order.items_count") int count) { ... }
```

Log correlation: the agent injects `trace_id`/`span_id` into the Logback/Log4j2 MDC; reference
them in the JSON encoder (e.g. `logstash-logback-encoder` or Spring Boot structured logging
`logging.structured.format.console=ecs|logstash|gelf`).

## Go

```go
import (
  "go.opentelemetry.io/otel"
  "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
  "go.opentelemetry.io/otel/propagation"
  sdktrace "go.opentelemetry.io/otel/sdk/trace"
  "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func initTracing(ctx context.Context) (func(context.Context) error, error) {
  exp, err := otlptracehttp.New(ctx) // reads OTEL_EXPORTER_OTLP_* env
  if err != nil { return nil, err }
  tp := sdktrace.NewTracerProvider(sdktrace.WithBatcher(exp)) // resource from OTEL_* env
  otel.SetTracerProvider(tp)
  otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
    propagation.TraceContext{}, propagation.Baggage{}))
  return tp.Shutdown, nil
}

// Server and client
http.Handle("/orders", otelhttp.NewHandler(ordersHandler, "orders"))
client := http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}
```

Go has no runtime auto-instrumentation in-process; use contrib wrappers (`otelhttp`,
`otelgrpc`, `otelsql`) or eBPF-based zero-code instrumentation. Log correlation with `log/slog`:
use the `otelslog` bridge, or a handler that adds `trace_id`/`span_id` from
`trace.SpanContextFromContext(ctx)`.

## Propagation across queues

Inject context into message headers on publish and extract on consume:

```ts
import { context, propagation } from '@opentelemetry/api';
const headers: Record<string, string> = {};
propagation.inject(context.active(), headers);     // producer: send headers with the message
const parent = propagation.extract(context.active(), msg.headers); // consumer
```

For batch consumers, start a new trace per batch and add span links to each message's context.

## Collector (gateway) baseline

```yaml
receivers:
  otlp:
    protocols: { grpc: { endpoint: 0.0.0.0:4317 }, http: { endpoint: 0.0.0.0:4318 } }

processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 20 }
  k8sattributes: {}
  resourcedetection: { detectors: [env, system] }
  attributes/redact:
    actions:
      - { key: http.request.header.authorization, action: delete }
      - { key: user.email, action: delete }
  transform/redact:
    error_mode: ignore
    log_statements:     # context inferred from the path prefix (log.*)
      - replace_pattern(log.body, "\\b\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}\\b", "***CPF***")
  tail_sampling:
    decision_wait: 10s
    policies:
      - { name: errors, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: slow, type: latency, latency: { threshold_ms: 1000 } }
      - { name: baseline, type: probabilistic, probabilistic: { sampling_percentage: 5 } }
  batch: {}

connectors:
  spanmetrics: {}          # alpha; RED metrics from 100% of spans, before sampling
                           # emits traces.span.metrics.calls / .duration (ms); exemplars off by default
  forward: {}              # hands unsampled traces to the sampling pipeline

exporters:
  otlphttp/backend: { endpoint: https://otlp.backend.internal }   # the user's own backend

service:
  pipelines:
    traces/in:      { receivers: [otlp], processors: [memory_limiter, k8sattributes, resourcedetection, attributes/redact], exporters: [spanmetrics, forward] }
    traces/sampled: { receivers: [forward], processors: [tail_sampling, batch], exporters: [otlphttp/backend] }
    metrics:        { receivers: [otlp, spanmetrics], processors: [memory_limiter, batch], exporters: [otlphttp/backend] }
    logs:           { receivers: [otlp], processors: [memory_limiter, transform/redact, batch], exporters: [otlphttp/backend] }
```

With more than one gateway replica, put a tier of Collectors with the `loadbalancing` exporter
(routing by trace ID) in front, so every span of a trace reaches the same tail-sampling
instance. Keep `memory_limiter` first; batch after any sampling or filtering.

**Batching.** The `batch` processor README still says to place it after `memory_limiter` and any
sampling processors, as above. Exporters can also batch themselves through `sending_queue`
(`sending_queue: { batch: {} }`, off by default) and persist the queue across restarts with
`sending_queue.storage: file_storage/<name>` plus the `file_storage` extension. Either works;
exporter-side batching with a persistent queue avoids losing data held in an in-memory batch
on restart. Check the current Collector release notes for which the project recommends, and
avoid batching twice without reason.

**Redaction options.** `transform` (OTTL) handles pattern rewrites like the one above. The
contrib `redaction` processor is an allowlist alternative: `allowed_keys` (fails closed: an
empty list removes all attributes), `blocked_values` regexes masked with asterisks,
`blocked_key_patterns`, optional `hash_function` (HMAC variants for low-entropy data), and a
`summary` audit level. Its stability is per signal (traces beta, logs/metrics alpha at the time
of writing); check its README before relying on it in production.
