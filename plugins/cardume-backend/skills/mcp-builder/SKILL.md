---
name: mcp-builder
description: "Principles for building MCP (Model Context Protocol) servers: tool design, resource and prompt patterns, input schemas, error handling, and security. Use when creating or reviewing an MCP server or its tool definitions."
allowed-tools: Read Write Edit Glob Grep
---

# MCP Builder

> Principles for building MCP servers against the current spec.
> Spec baseline: **MCP 2026-07-28** (previous: 2025-11-25). Always confirm the latest
> revision at <https://modelcontextprotocol.io/specification/latest> and its changelog
> before relying on version-specific details.

Deep dives: [references/protocol-and-transports.md](references/protocol-and-transports.md)
(stateless model, transports, version negotiation, migration) and
[references/authorization-and-security.md](references/authorization-and-security.md)
(OAuth 2.1, protected resource metadata, client registration, threats).

---

## 1. What MCP Is

MCP is an open JSON-RPC 2.0 protocol that lets AI applications (hosts/clients) use
capabilities exposed by **servers**.

| Primitive | Controlled by | Purpose |
|-----------|---------------|---------|
| **Tools** | Model | Functions the model can invoke (side effects allowed) |
| **Resources** | Application | Context data addressed by URI (files, records, docs) |
| **Prompts** | User | Reusable, parameterized prompt templates / workflows |

Client-side features a server can ask for: **elicitation** (ask the user for input).
Roots, Sampling and Logging are **deprecated** in 2026-07-28 — do not build new
dependencies on them (pass paths as tool params; call LLM APIs directly; log to
`stderr` or OpenTelemetry).

### What changed in 2026-07-28 (high impact)

| Change | Consequence for servers |
|--------|-------------------------|
| Protocol is **stateless**: no `initialize` handshake, no `Mcp-Session-Id` | Each request carries protocol version + client capabilities in `_meta`; never keep per-connection state |
| `server/discover` RPC (MUST implement) | Advertise supported versions, capabilities, identity |
| Multi Round-Trip Requests (MRTR) | Need user input mid-call? Return `resultType: "input_required"` with `inputRequests`; client retries with `inputResponses` |
| `subscriptions/listen` replaces GET stream + `resources/subscribe` | Change notifications only on opted-in listen streams |
| Tasks moved to an extension (`io.modelcontextprotocol/tasks`) | Long-running work = opt-in extension |
| Client ID Metadata Documents preferred; DCR deprecated | See auth reference |

SDKs may lag the spec — check your SDK's release notes for which protocol versions it
implements, and support older clients via `server/discover`/version negotiation.

---

## 2. Server Architecture

### Transports (standard)

| Transport | Use |
|-----------|-----|
| **stdio** | Local server launched as a subprocess by the client; JSON-RPC over stdin/stdout. Logs go to **stderr** only |
| **Streamable HTTP** | Remote server; single MCP endpoint accepting POST, response as JSON or an SSE stream |

- HTTP+SSE (the old two-endpoint transport) is **deprecated** since 2025-03-26 —
  migrate to Streamable HTTP. "SSE" now only means the response-streaming mode
  *inside* Streamable HTTP.
- WebSocket is **not** a standard MCP transport (custom transports are allowed but
  not interoperable).

### Statelessness rules

- No protocol session: `tools/list`, `resources/list`, `prompts/list` must not vary
  per connection (they MAY vary by the caller's authorization).
- Need state across calls (cart, browser context, transaction)? Return an explicit,
  opaque, high-entropy **handle** from a "create" tool and accept it as an argument.
  Bind it server-side to the authenticated user; possession of a handle is never
  authentication. Document its lifetime in the tool description.
- Horizontal scaling is straightforward: any replica can serve any request.

### Project layout (TypeScript example)

```
my-mcp-server/
├── src/
│   ├── index.ts        # server + transport wiring
│   ├── tools/          # one module per tool (schema + handler)
│   └── resources/
├── test/
├── package.json
└── tsconfig.json
```

---

## 3. Tool Design

### Definition fields

| Field | Notes |
|-------|-------|
| `name` | 1–128 chars, `[A-Za-z0-9_.-]`, unique per server, action-oriented (`create_issue`) |
| `title` | Optional human-friendly display name |
| `description` | What it does, when to use it, side effects, limits — the model reads this |
| `inputSchema` | JSON Schema (2020-12 default); `type: object`; describe every property; mark `required`; no-arg tools: `{ "type": "object", "additionalProperties": false }` |
| `outputSchema` | Optional JSON Schema for `structuredContent`; if present, results MUST conform |
| `annotations` | Behavior hints (below) |
| `icons` | Optional UI icons |

### Results

- `content`: unstructured blocks — `text`, `image`, `audio` (base64 + `mimeType`),
  `resource_link`, embedded `resource`.
- `structuredContent`: any JSON value matching `outputSchema`. For backwards
  compatibility also return the serialized JSON in a text block.
- Errors the model can fix (bad date, not found, upstream API failure) → a normal
  result with `isError: true` and an actionable message. Malformed requests / unknown
  tool → JSON-RPC protocol error.

### Annotations (hints, not guarantees)

| Hint | Meaning |
|------|---------|
| `readOnlyHint` | Does not modify its environment |
| `destructiveHint` | May perform destructive updates (meaningful when not read-only) |
| `idempotentHint` | Repeating the call with same args has no extra effect |
| `openWorldHint` | Interacts with external entities (web, third-party APIs) |

Clients MUST treat annotations as untrusted unless the server is trusted — never rely
on them as a security control.

### Design principles

| Principle | Practice |
|-----------|----------|
| Task-shaped, not API-shaped | Prefer `schedule_meeting` over thin wrappers of every endpoint |
| Few, focused tools | Large tool lists cost context and confuse selection |
| Bounded output | Paginate, truncate, offer `limit`/filters; return IDs + summaries |
| Deterministic order | Return `tools/list` in stable order (cache-friendly) |
| No secrets in args | Never mark sensitive params with `x-mcp-header` (headers are visible to proxies) |

---

## 4. Resources

| Pattern | Example |
|---------|---------|
| Direct resource | `docs://readme`, `file:///project/README.md` |
| Resource template (RFC 6570) | `users://{userId}/profile` |

- `resources/list`, `resources/templates/list`, `resources/read`; results carry
  `ttlMs` + `cacheScope` caching hints in 2026-07-28.
- Use `mimeType`; text vs base64 `blob`. Annotations: `audience`, `priority`,
  `lastModified`.
- Unknown resource → JSON-RPC `-32602` (Invalid Params) in 2026-07-28.
- Change notifications are delivered via `subscriptions/listen`.

## 5. Prompts

- `prompts/list` + `prompts/get` with typed `arguments`; return a list of messages.
- Use for user-invoked workflows (slash commands), not for hidden instructions.

## 6. Elicitation

- Ask the user for missing input mid-operation. In 2026-07-28 this is an MRTR
  `inputRequests` entry (`method: "elicitation/create"`), answered on the client's retry.
- **Form mode**: flat JSON Schema of primitives; for non-sensitive data only.
- **URL mode**: send the user to a URL (OAuth to a third party, payment, API-key entry)
  — sensitive data never passes through the MCP client.
- Handle `accept` / `decline` / `cancel`; carry your own correlation data in
  `requestState`.

---

## 7. Authorization (HTTP transports)

- Optional, but if a remote server is protected: it acts as an **OAuth 2.1 resource
  server**.
- MUST publish **Protected Resource Metadata** (RFC 9728,
  `/.well-known/oauth-protected-resource`) and return `401` with
  `WWW-Authenticate: Bearer resource_metadata="…", scope="…"`.
- Validate every token: issuer, expiry, and **audience = this server** (RFC 8707
  resource indicators). Insufficient scope → `403` + `error="insufficient_scope"`.
- Clients register via **Client ID Metadata Documents** (preferred), pre-registration,
  or Dynamic Client Registration (deprecated, back-compat only).
- **stdio servers do not use this flow** — read credentials from the environment.

Details: [references/authorization-and-security.md](references/authorization-and-security.md).

---

## 8. Security Checklist

- [ ] **No token passthrough**: never accept tokens not issued for this server, never
      forward the client's token downstream — obtain separate upstream credentials
- [ ] Least privilege: minimal scopes, minimal upstream API permissions, read-only by default
- [ ] Validate every input against the schema *and* business rules (paths, URLs, SQL, shell)
- [ ] Sanitize outputs; treat upstream data as untrusted (prompt injection via tool results)
- [ ] Rate-limit tool calls; enforce timeouts and output size limits
- [ ] Secrets from env/secret manager; never logged or returned
- [ ] Local HTTP servers: bind to `127.0.0.1`, validate `Origin` (DNS rebinding), require auth
- [ ] Human-in-the-loop for destructive tools (set `destructiveHint`, clear descriptions)
- [ ] Audit log of tool invocations (no secrets/PII)

---

## 9. Official SDKs

Tier 1: TypeScript (`@modelcontextprotocol/sdk`), Python (`mcp`, includes FastMCP-style
server API), C#, Go, Rust, Ruby. Tier 2: Java. Tier 3: Swift, PHP, Kotlin.
List and tiers: <https://modelcontextprotocol.io/docs/sdk>. Prefer an official SDK over
hand-rolled JSON-RPC.

## 10. Configuration (stdio clients)

| Field | Purpose |
|-------|---------|
| `command` | Executable to run |
| `args` | Command arguments |
| `env` | Environment variables (credentials for stdio servers) |

Remote servers are configured by URL (Streamable HTTP endpoint); the client handles OAuth.

---

## 11. Testing

| Layer | How |
|-------|-----|
| Unit | Tool handlers as plain functions; schema validation of inputs/outputs |
| Protocol | SDK in-memory/client transport: list → call → assert `structuredContent` |
| Interactive | **MCP Inspector**: `npx @modelcontextprotocol/inspector <command>` (stdio) or point it at the HTTP URL |
| Auth | 401 + `WWW-Authenticate`, wrong-audience token rejected, 403 on missing scope |
| Model-level | Evaluate with realistic prompts that the model picks the right tool with right args |

---

## 12. Best Practices Checklist

- [ ] Targets a named spec revision; `server/discover` advertises supported versions
- [ ] stdio or Streamable HTTP only (no legacy HTTP+SSE, no WebSocket)
- [ ] No per-connection state; explicit handles for cross-call state
- [ ] Clear names, rich descriptions, complete `inputSchema`
- [ ] `outputSchema` + `structuredContent` for machine-readable results
- [ ] Accurate annotations
- [ ] `isError: true` with actionable messages for recoverable failures
- [ ] Authorization per spec for remote servers; no token passthrough
- [ ] Tested in MCP Inspector and with an automated client

---

> **Remember:** the model only knows what your names, descriptions and schemas tell it.
> Keep tools few, focused, safe by default, and stateless.
