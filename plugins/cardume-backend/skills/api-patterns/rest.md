# REST Principles

> Resource-based API design - nouns not verbs.

## Resource Naming Rules

```
Principles:
├── Use NOUNS, not verbs (resources, not actions)
├── Use PLURAL forms (/users not /user)
├── Use lowercase with hyphens (/user-profiles)
├── Nest for relationships (/users/123/posts)
└── Keep shallow (max 3 levels deep)
```

## HTTP Method Selection

| Method | Purpose | Idempotent? | Body? |
|--------|---------|-------------|-------|
| **GET** | Read resource(s) | Yes | No |
| **POST** | Create new resource | No | Yes |
| **PUT** | Replace entire resource | Yes | Yes |
| **PATCH** | Partial update | No | Yes |
| **DELETE** | Remove resource | Yes | No |

## Status Code Selection

| Situation | Code | Why |
|-----------|------|-----|
| Success (read) | 200 | Standard success |
| Created | 201 | New resource created |
| No content | 204 | Success, nothing to return |
| Bad request | 400 | Malformed request |
| Unauthorized | 401 | Missing/invalid auth |
| Forbidden | 403 | Valid auth, no permission |
| Not found | 404 | Resource doesn't exist |
| Conflict | 409 | State conflict (duplicate) |
| Validation error | 422 | Valid syntax, invalid data |
| Rate limited | 429 | Too many requests |
| Server error | 500 | Our fault |

> 422 is "Unprocessable Content" in RFC 9110. Error bodies: RFC 9457
> `application/problem+json` (see `response.md`).

## Idempotency Keys (safe retries of unsafe methods)

POST and PATCH are not idempotent; a network timeout leaves the client unsure whether
the operation happened. Accept an **`Idempotency-Key`** request header
(draft-ietf-httpapi-idempotency-key-header — an active IETF Internet-Draft, not yet
an RFC; widely used in practice, e.g. payment APIs):

```http
POST /payments
Idempotency-Key: "8e03978e-40d5-43e8-bc93-6894a57f9324"
```

```
Server rules:
├── Client generates a unique key (UUID) per logical operation
├── Key required but missing → 400 (problem+json)
├── Store key + request fingerprint + response for a bounded TTL (e.g. 24h)
├── Same key + same payload → replay the stored response
├── Same key + different payload → 422 (problem+json)
├── Same key while first request still in flight → 409 Conflict
└── Document which endpoints require/accept the header and the key TTL
```
