---
name: preview
description: "Manages the local development preview server via cardume-auto-preview: start, stop, restart, status, or health check, with port-conflict handling."
disable-model-invocation: true
argument-hint: "[start|stop|status] [port]"
compatibility: "Claude Code with the Cardume plugins (uses cardume-* commands, subagents or plugin paths); the guidance itself is portable."
---

# /cardume-core:preview - Preview Management

$ARGUMENTS

---

## Task

Manage preview server: start, stop, status check.

### Commands

```
/cardume-core:preview           - Show current status
/cardume-core:preview start     - Start server
/cardume-core:preview stop      - Stop server
/cardume-core:preview restart   - Restart
/cardume-core:preview check     - Health check
```

---

## Usage Examples

### Start Server
```
/cardume-core:preview start

Response:
🚀 Starting preview...
   Port: 3000
   Type: Next.js

✅ Preview ready!
   URL: http://localhost:3000
```

### Status Check
```
/cardume-core:preview

Response:
=== Preview Status ===

🌐 URL: http://localhost:3000
📁 Project: C:/projects/my-app
🏷️ Type: nextjs
💚 Health: OK
```

### Port Conflict
```
/cardume-core:preview start

Response:
⚠️ Port 3000 is in use.

Options:
1. Start on port 3001
2. Close app on 3000
3. Specify different port

Which one? (default: 1)
```

---

## Technical

Preview is managed by the `cardume-auto-preview` command:

```bash
cardume-auto-preview start [port]
cardume-auto-preview stop
cardume-auto-preview status
```

