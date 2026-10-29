---
type: llm
focus: last_message
weight: 2
---

PASS if it identifies: unhandled async rejections in Express 4 (no try/catch or error middleware) and the null `user` crash; synchronous blocking calls (readFileSync, pbkdf2Sync, large JSON.parse) stalling the event loop, with fixes (async APIs, streaming, worker threads/queue for CPU work); `forEach(async ...)` firing un-awaited inserts so errors are lost and the response is sent before work finishes (use for...of, Promise.all with limits, or a batch insert in a transaction); path traversal via `'/data/' + req.body.file`; trusting userId from the body instead of the authenticated session; and missing input validation/body size limits.
FAIL if it misses either the path traversal or the forEach(async) problem.
