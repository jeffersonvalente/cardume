# MCP Protocol and Transports (spec 2026-07-28)

Sources: <https://modelcontextprotocol.io/specification/2026-07-28/changelog>,
`basic/transports/stdio`, `basic/transports/streamable-http`, `server/tools`.
Re-check the changelog when a newer revision is published.

## Stateless request model

- No `initialize` / `notifications/initialized` handshake and no protocol session.
- Every request carries in `params._meta`:
  - `io.modelcontextprotocol/protocolVersion` (required)
  - `io.modelcontextprotocol/clientCapabilities` (required)
  - `io.modelcontextprotocol/clientInfo` (SHOULD)
- Servers SHOULD return `io.modelcontextprotocol/serverInfo` in each result's `_meta`.
- Unsupported version → `UnsupportedProtocolVersionError` (code `-32022`) listing
  supported versions.
- `server/discover` (servers MUST implement): advertises supported versions,
  capabilities and identity; clients use it as an up-front probe and as the
  backwards-compatibility probe on stdio.
- Every result has `resultType`: `"complete"` or `"input_required"`.
- Removed: `ping`, `logging/setLevel`, `notifications/roots/list_changed`. Log level is
  per request via `io.modelcontextprotocol/logLevel` in `_meta`.

## Multi Round-Trip Requests (MRTR)

Servers no longer send their own requests to clients. When a call needs more input
(elicitation, and the deprecated sampling/roots), the server returns:

```json
{ "resultType": "input_required",
  "inputRequests": { "login": { "method": "elicitation/create", "params": { "mode": "form", "message": "…", "requestedSchema": { "type": "object", "properties": { "name": { "type": "string" } } } } } },
  "requestState": "opaque-server-state" }
```

The client retries the original request (new JSON-RPC `id`) with `inputResponses`
and the echoed `requestState`. Keep `requestState` opaque and integrity-protected
(sign/encrypt it) because it round-trips through the client.

## Change notifications

`subscriptions/listen` opens one long-lived stream; the client opts in to
`toolsListChanged`, `promptsListChanged`, `resourcesListChanged`,
`resourceSubscriptions`. Progress and log notifications stay on the response stream of
the request they belong to. List results carry `ttlMs` + `cacheScope`
(`public`/`private`) caching hints.

## stdio

- Client launches the server as a subprocess; newline-delimited JSON-RPC on
  stdin/stdout, no embedded newlines.
- **Never write anything but MCP messages to stdout** (a stray `console.log`/`print`
  corrupts the stream). Logs go to stderr.
- Cancellation: `notifications/cancelled`. Shutdown: client closes stdin; server
  should exit on EOF.
- Credentials come from the environment, not OAuth.

## Streamable HTTP

- One MCP endpoint (e.g. `https://example.com/mcp`) accepting **POST**; each JSON-RPC
  message is its own POST.
- Client `Accept` lists `application/json` and `text/event-stream`; server answers a
  request with one JSON object or an SSE stream scoped to that request.
- Required request headers: `MCP-Protocol-Version` (must match `_meta`),
  `Mcp-Method`, and `Mcp-Name` for `tools/call`, `resources/read`, `prompts/get`.
  Header/body mismatch → `400` + `HeaderMismatch` (`-32020`).
- Optional `x-mcp-header` on tool params mirrors values to `Mcp-Param-{Name}` for
  routing — never on secrets.
- Closing the response stream = cancellation. No `Last-Event-ID` resumability.
- Security: validate `Origin` (403 if invalid) against DNS rebinding; bind local
  servers to `127.0.0.1`; authenticate connections.
- Send `X-Accel-Buffering: no` on SSE responses behind nginx-style proxies.

### Back-compat with 2025-03-26 … 2025-11-25 clients

Those versions used `initialize`, `Mcp-Session-Id`, a GET stream and resumable SSE.
A 2026-07-28-only server should answer GET/DELETE with `405`, ignore
`Mcp-Session-Id` and `Last-Event-ID`. To serve both eras, implement the older
revision's behavior alongside (most SDKs handle negotiation for you).

### Deprecated / non-standard

| Item | Status |
|------|--------|
| HTTP+SSE (2024-11-05, separate SSE + POST endpoints) | Deprecated; migrate to Streamable HTTP |
| WebSocket | Not a standard transport (custom transports allowed, not interoperable) |
| Roots, Sampling, Logging features | Deprecated in 2026-07-28 |
| Tasks | Moved to the `io.modelcontextprotocol/tasks` extension |

## Error codes

- JSON-RPC standard codes (`-32602` invalid params, also used for unknown resource).
- `-32000`..`-32019` implementation-defined; `-32020`..`-32099` reserved for MCP.
- Tool business errors are **results** with `isError: true`, not JSON-RPC errors.

## Migration checklist (from 2025-xx servers)

- [ ] Remove session-keyed state; introduce explicit handles where needed
- [ ] Implement `server/discover`
- [ ] Replace server-initiated `elicitation/create`/`sampling/createMessage` with MRTR
- [ ] Replace `resources/subscribe` / GET stream with `subscriptions/listen`
- [ ] Add `resultType` and caching hints (usually handled by the SDK)
- [ ] Drop dependence on Roots/Sampling/Logging
