# Rate Limiting Principles

> Protect your API from abuse and overload.

## Why Rate Limit

```
Protect against:
├── Brute force attacks
├── Resource exhaustion
├── Cost overruns (if pay-per-use)
└── Unfair usage
```

## Strategy Selection

| Type | How | When |
|------|-----|------|
| **Token bucket** | Burst allowed, refills over time | Most APIs |
| **Sliding window** | Smooth distribution | Strict limits |
| **Fixed window** | Simple counters per window | Basic needs |

## Response Headers

Prefer the IETF HTTPAPI **`RateLimit-Policy`** / **`RateLimit`** fields
(draft-ietf-httpapi-ratelimit-headers — still an Internet-Draft, not an RFC; syntax
may change before publication, so pin to the draft revision you implement):

```http
RateLimit-Policy: "default";q=100;w=60
RateLimit: "default";r=42;t=18
```

- `q` = quota, `w` = window (s), `r` = remaining, `t` = seconds until reset.
- Exceeded → **429 Too Many Requests** + `Retry-After` (RFC 9110), body as
  RFC 9457 `application/problem+json`.
- Legacy `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` are
  non-standard vendor conventions — emit them only for backward compatibility with
  existing clients, not as the primary contract.
- Document limits in the OpenAPI description.
