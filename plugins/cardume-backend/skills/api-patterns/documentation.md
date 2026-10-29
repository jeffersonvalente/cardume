# API Documentation Principles

> Good docs = happy developers = API adoption.

## OpenAPI Essentials

- Target **OpenAPI 3.1** (full JSON Schema 2020-12 alignment, webhooks) or
  **3.2** (released Sept 2025: hierarchical tags, `QUERY` method, streaming media
  types such as SSE/JSON Lines, OAuth 2.0 device flow). Check your tooling supports
  3.2 before adopting it. "Swagger" is the tooling brand; 2.0 is legacy.

```
Include:
├── All endpoints with examples
├── Request/response schemas
├── Authentication requirements (securitySchemes)
├── Error responses as application/problem+json (RFC 9457)
├── Idempotency-Key header on retryable unsafe operations
└── Rate limiting info (RateLimit / RateLimit-Policy, 429 + Retry-After)
```

## Good Documentation Has

```
Essentials:
├── Quick start / Getting started
├── Authentication guide
├── Complete API reference
├── Error handling guide
├── Code examples (multiple languages)
└── Changelog
```
