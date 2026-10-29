# Architecture

## Fixed timestep with interpolation

Run simulation at a constant rate; render as fast as the display allows; blend between simulation states for smooth visuals.

```text
const DT = 1 / 60
accumulator = 0
previous = current = initialState

each frame:
    frameTime = min(now - last, 0.25)   # clamp to avoid the spiral of death after a stall
    accumulator += frameTime
    while accumulator >= DT:
        previous = current
        current = simulate(current, DT, inputs)
        accumulator -= DT
    alpha = accumulator / DT
    render(lerp(previous, current, alpha))
```

Why: identical results at 30, 60 or 144 FPS; deterministic replays; prerequisite for rollback or lockstep netcode. Engines provide this already (Godot `_physics_process`, Unity `FixedUpdate`, Unreal substepping, Phaser/Matter fixed-step options); use the engine's version and enable physics interpolation where offered rather than writing your own.

If you stay with variable delta (common for simple web games), multiply every velocity and timer by `delta`, and clamp `delta` so a tab switch doesn't teleport objects.

## Scene and state management

- **Game-level states:** Boot → Title → Playing ⇄ Paused → GameOver. One place owns transitions; scenes don't load each other ad hoc.
- **Entity states:** a finite state machine per actor (Idle, Run, Jump, Fall, Attack, Hurt). Each state handles `enter`, `exit`, `update`, `handle_input`. Hierarchical FSMs or behavior trees for complex AI.
- **Persistent services** (audio, save, settings, input remap) live outside scenes: Godot autoloads, Unity bootstrap scene or DontDestroyOnLoad objects, Phaser global plugins or registry. Keep the list short; global singletons tend to absorb unrelated logic.

## ECS vs scene tree / OOP

| Model | Good for | Costs |
|-------|----------|-------|
| Scene tree / component composition (Godot, Unity GameObjects) | Most games; editor-friendly; intuitive hierarchy | Per-object overhead with thousands of entities |
| Data-oriented ECS (Bevy, Unity DOTS/Entities, flecs, bitecs) | Thousands of similar entities, simulations, cache-friendly processing | Steeper learning curve; harder editor workflows |

Rule: use the engine's native model; adopt ECS for a hot subsystem (bullets, crowds) only when profiling demands it.

## Event bus and signals

Emit domain events (`enemy_killed(enemy, by)`, `coin_collected(value)`) that UI, audio, achievements and analytics subscribe to. Benefits: gameplay doesn't know the HUD exists; features can be added without touching core code. Limits: avoid event chains that trigger other events several levels deep, and disconnect listeners when objects are freed to prevent leaks and calls on dead objects.

## Data-driven design

- Godot: custom `Resource` classes (`.tres`) for enemy stats, weapons, levels.
- Unity: `ScriptableObject` assets for definitions; keep runtime state out of them, since edits in play mode can persist in the editor.
- Web/others: JSON or TOML loaded at boot, validated against a schema.

Separate **definitions** (immutable, shared: "Goblin has 10 HP") from **instances** (mutable: "this goblin has 3 HP").

## Save systems

```json
{ "version": 3, "savedAt": "2026-01-01T12:00:00Z", "player": { "level": 4, "hp": 20 }, "flags": ["met_merchant"] }
```

- Include `version`; on load, run migrations `v1→v2→v3` in order.
- Serialize plain data (IDs, numbers, strings); never serialize engine objects or references directly.
- Atomic write: write `save.tmp`, flush, then rename over `save.json`. Keep one backup.
- Separate files for settings vs progress vs cloud-sync metadata.
- Validate on load; on failure, fall back to backup and tell the player rather than crashing.
- Platform paths: Godot `user://`, Unity `Application.persistentDataPath`, web `localStorage`/IndexedDB (size limits apply).
