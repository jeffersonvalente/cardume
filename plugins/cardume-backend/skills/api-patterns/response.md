# Response Format Principles

> Consistency is key - choose a format and stick to it.

## Common Patterns

```
Choose one:
├── Envelope pattern ({ data, meta })
├── Direct data (just return the resource)
└── HAL/JSON:API (hypermedia)
```

## Error Response: RFC 9457 Problem Details

Use **RFC 9457** (Problem Details for HTTP APIs, obsoletes RFC 7807) with media type
`application/problem+json` instead of inventing an error envelope.

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Request validation failed",
  "status": 422,
  "detail": "2 fields are invalid",
  "instance": "/orders/req-7f3a",
  "errors": [
    { "pointer": "#/email", "detail": "must be a valid email" }
  ],
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

```
Rules:
├── type      → stable URI per problem kind (documented; "about:blank" if none)
├── title     → short, human-readable, same for every occurrence of the type
├── status    → mirrors the HTTP status code
├── detail    → occurrence-specific, safe to show
├── instance  → identifies this occurrence
├── Extension members (errors[], traceId, ...) for field errors / support
└── NEVER stack traces, SQL, internal hostnames (security!)
```

Frameworks with built-in support: Spring (`ProblemDetail`), ASP.NET Core
(`ProblemDetails`), FastAPI/Express via middleware.

## Pagination Types

| Type | Best For | Trade-offs |
|------|----------|------------|
| **Offset** | Simple, jumpable | Performance on large datasets |
| **Cursor** | Large datasets | Can't jump to page |
| **Keyset** | Performance critical | Requires sortable key |

### Selection Questions

1. How large is the dataset?
2. Do users need to jump to specific pages?
3. Is data frequently changing?
