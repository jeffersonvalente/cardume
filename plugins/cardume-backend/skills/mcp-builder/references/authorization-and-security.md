# MCP Authorization and Security (spec 2026-07-28)

Sources: <https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization>,
<https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices>.

## Scope of the authorization spec

- Authorization is **optional**. When used over HTTP it SHOULD follow the spec.
- **stdio servers SHOULD NOT** use it — take credentials from the environment.
- Built on: OAuth 2.1 (IETF draft), RFC 6750 bearer tokens, RFC 8414 AS metadata,
  RFC 9728 Protected Resource Metadata, RFC 8707 resource indicators, RFC 9207 issuer
  identification, OAuth Client ID Metadata Documents (IETF draft), OIDC Discovery.

## Roles

| Role | Responsibility |
|------|----------------|
| MCP server | OAuth 2.1 **resource server**: validates tokens, publishes PRM |
| MCP client | OAuth 2.1 client: discovery, PKCE, `resource` parameter |
| Authorization server | Issues tokens (can be your IdP; separate from the MCP server is fine) |

## Server obligations

1. Publish **Protected Resource Metadata** (RFC 9728), e.g.
   `https://mcp.example.com/.well-known/oauth-protected-resource`, listing
   `authorization_servers` and a minimal `scopes_supported`.
2. Unauthenticated request → `401` with
   `WWW-Authenticate: Bearer resource_metadata="<PRM URL>", scope="files:read"`.
3. Validate every token per OAuth 2.1 §5.2: signature/introspection, expiry, issuer,
   and **audience = this server's canonical URI** (RFC 8707). Invalid/expired → `401`.
4. Insufficient scope → `403` with `error="insufficient_scope"`, the full set of
   scopes needed for the operation, and `resource_metadata`.
5. Tokens only in the `Authorization: Bearer` header, never in query strings.
6. **MUST NOT accept or transit any other tokens** (no token passthrough).

## Client registration (priority)

1. **Client ID Metadata Documents (CIMD)** — the `client_id` is an HTTPS URL that
   serves the client's metadata JSON. Preferred (SHOULD).
2. Pre-registered client ID.
3. **Dynamic Client Registration (RFC 7591)** — deprecated in 2026-07-28; kept only for
   authorization servers without CIMD support.

Clients must also send PKCE, the `resource` parameter on authorization and token
requests, and validate `iss` (RFC 9207) before redeeming codes.

## Calling upstream APIs from a server

- Never forward the MCP client's token to a downstream API. Obtain upstream
  credentials separately (service account, token exchange, or a per-user upstream
  OAuth flow via **URL-mode elicitation**).
- Proxy servers using a static upstream client ID MUST implement per-client consent to
  avoid the confused deputy problem (exact redirect URI matching, single-use `state`,
  `__Host-` signed consent cookies).

## Threats and mitigations

| Threat | Mitigation |
|--------|-----------|
| Token passthrough / wrong audience | Audience validation; separate upstream credentials |
| Confused deputy (OAuth proxy) | Per-client consent before upstream authorization |
| State handle hijacking | Random, expiring handles bound to the authenticated user |
| SSRF (clients fetching metadata; AS fetching CIMD) | HTTPS only, block private/link-local ranges, egress proxy |
| Local server compromise | Prefer stdio for local; if HTTP, bind 127.0.0.1, require auth, validate `Origin` |
| Prompt injection via tool output | Treat upstream content as untrusted; label/sanitize; keep human approval for destructive tools |
| Over-broad scopes | Minimal initial scopes; step-up via targeted `WWW-Authenticate` challenges |
| Excess privilege upstream | Least-privilege service accounts, read-only by default |

## Test cases

- No token → 401 with `resource_metadata`
- Token for another audience → 401
- Valid token, missing scope → 403 `insufficient_scope`
- Expired token → 401
- Handle owned by another user → tool error, no data leak
- Invalid `Origin` on Streamable HTTP → 403
