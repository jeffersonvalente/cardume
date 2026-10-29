# Multiplayer Basics

## Should you build it?

Networking typically doubles or triples scope: server hosting and cost, cheating, matchmaking, reconnection, testing with latency, and a player base big enough to find matches. Alternatives that capture much of the social value:

- Local/couch co-op or split screen.
- Asynchronous play: ghosts, shared leaderboards, daily seeds, level sharing.
- Turn-based over a simple HTTP API (far easier than real-time).

Build real-time multiplayer when it is the core of the game, and decide before writing gameplay code: retrofitting networking into a single-player codebase usually means a rewrite.

## Topologies

| Model | Notes |
|-------|-------|
| Authoritative dedicated server | Server owns state; best cheat resistance; hosting cost |
| Listen server / host-client | One player hosts; cheap; host advantage and host migration issues |
| Peer-to-peer lockstep | All peers simulate from inputs; needs determinism; good for RTS |
| Rollback (GGPO-style) | Predict remote inputs, rewind and resimulate on correction; fighting games |

## Authoritative server essentials

- Clients send **inputs** (with sequence numbers), never positions or results.
- Server simulates at a fixed tick (20–60 Hz) and broadcasts snapshots or deltas.
- **Client-side prediction:** the local player applies its own inputs immediately.
- **Server reconciliation:** when a snapshot arrives, reset to the server state for the acknowledged input and re-apply unacknowledged inputs.
- **Entity interpolation:** render remote entities ~100 ms in the past, blending between received snapshots.
- **Lag compensation:** the server rewinds hitboxes to the shooter's view time when validating hits; cap the rewind window.
- Validate everything server-side (speed, cooldowns, inventory).

## Practicalities

- Use the engine's networking layer where it fits (Godot high-level multiplayer, Unity Netcode for GameObjects or community libraries, Unreal replication) before writing your own.
- Transport: UDP-based (ENet, QUIC, WebRTC data channels) for real-time; WebSocket for browser games accepting TCP head-of-line blocking. **WebTransport** (HTTP/3 over QUIC, unreliable datagrams plus independent streams) is the client-server option for browsers without WebRTC's signaling; it is reported as available in all major current browsers since Safari 26.4 (2026), but implementations still differ, so check caniuse and keep a WebSocket fallback.
- Rollback: use an existing library rather than writing your own (GGPO, open source C++; GGRS, its Rust reimplementation, used by `bevy_ggrs`). Both require a deterministic simulation (`deterministic-simulation.md`).
- Test with simulated latency, jitter and packet loss from the start.
- Accounts, persistence, matchmaking and purchase validation belong in a backend service (involve backend-specialist).
