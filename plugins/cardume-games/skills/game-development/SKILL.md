---
name: game-development
description: "Game development principles across engines: engine selection, game loop and architecture, input, physics, game feel, UI, audio, saves, performance, mobile, multiplayer, testing, accessibility and shipping. Use when building, structuring, tuning or debugging a 2D/3D game in Godot, Unity, Unreal, Phaser, Three.js, Bevy or similar."
allowed-tools: Read Glob Grep
---

# Game Development

Principles that hold across engines, with engine-specific code in `reference/`. Prefer the concepts here over exact API names: engine APIs shift between versions, the patterns don't.

## Reference files

| File | Read when |
|------|-----------|
| `reference/engine-selection.md` | Choosing an engine or justifying the current one |
| `reference/architecture.md` | Game loop, scenes/states, ECS vs scene tree, events, data-driven design, saves |
| `reference/game-feel.md` | Input handling, platformer controls, juice, camera |
| `reference/performance-and-platforms.md` | Frame budget, profiling per engine, mobile, shipping |
| `reference/multiplayer.md` | Any networked play |
| `reference/deterministic-simulation.md` | Seeded RNG, pure sim functions, replays, rollback, determinism tests |
| `reference/level-design.md` | Level/scenario design, difficulty ramps, level files with schema, validator and reference solutions |
| `reference/snippets-godot.md` | GDScript examples (Godot 4) |
| `reference/snippets-unity.md` | C# examples (Unity) |
| `reference/snippets-phaser.md` | TypeScript examples (Phaser 4 web; the shown calls also work in Phaser 3) |

## Start with the core loop

Prototype the one action the player repeats (jump, shoot, match, steer) with placeholder shapes before menus, saves, progression or art. Fun is found by playing, not by planning, and polishing a loop that isn't fun wastes the most time of any mistake in game development.

A useful order: core loop → playtest → iterate on tunables → content → polish/juice → performance pass → ship. Keep a build playable at every step so feedback stays possible.

## Engine selection (summary)

| Engine | Pick it when | Watch out for |
|--------|--------------|---------------|
| Godot 4 | 2D or mid-scope 3D, small team, open source, fast iteration | Console export goes through third parties; smaller asset store |
| Unity | Mobile, cross-platform, large ecosystem, C# team | Licensing terms change; review them before committing |
| Unreal 5 | High-fidelity 3D, large teams, AAA pipelines | Heavy builds and hardware; overkill for small 2D games |
| Phaser | 2D browser games with a full framework (scenes, physics, input) | 2D only; you own the build tooling |
| PixiJS | 2D web rendering when you want your own game structure | Renderer only: no physics or scene system |
| Three.js / Babylon.js | 3D in the browser (Babylon is more batteries-included) | Web GPU/memory limits, asset size, mobile browsers |
| Bevy | Rust team, ECS-first, code-driven | Young ecosystem, API churn between releases, no full editor |
| LÖVE | Small 2D games and jams in Lua | Minimal tooling; build your own structure |
| Defold | Small, fast 2D for mobile and web | Smaller community; Lua |
| raylib | Learning, tiny games, C/C++ control | You build almost everything yourself |

If a project already uses an engine, stay with it; a mid-project switch costs more than any feature gain. Full matrix with reasons: `reference/engine-selection.md`.

## Core architecture

- **Game loop:** run simulation on a fixed timestep (for example 60 Hz) with an accumulator, render every frame, and interpolate rendering between the last two simulation states. Frame-rate-dependent logic behaves differently on fast and slow machines and blocks replays and netcode. When an engine gives you a variable `delta`, multiply movement by it, and use the engine's physics tick for physics.
- **Scenes and states:** model screens (title, gameplay, pause, game over) and entity behavior (idle, run, jump, attack) as explicit state machines. Ad-hoc boolean flags (`isJumping && !isAttacking`) multiply into bugs.
- **ECS vs scene tree/OOP:** use the engine's native model (Godot nodes, Unity GameObjects/components, Bevy ECS). Reach for a data-oriented ECS when you have thousands of similar entities; otherwise composition of small components is clearer. Avoid deep inheritance trees either way.
- **Event bus / signals:** decouple systems (UI, audio, achievements) from gameplay by emitting events like `player_died` rather than calling across systems directly. Keep it to cross-cutting concerns; overuse makes control flow hard to trace.
- **Data-driven design:** stats, waves, levels and tuning live in Godot Resources, Unity ScriptableObjects, or JSON/TOML, so they change without code edits and can be tweaked during playtests.

## Input

- Map physical inputs to **actions** (`jump`, `move_left`) and read actions in gameplay code; this enables rebinding, gamepads and touch with one code path.
- **Buffer inputs** briefly (about 100–150 ms) so a jump pressed just before landing still fires.
- **Coyote time** (about 80–120 ms) lets the player jump just after leaving a ledge; it reads as fairness, not cheating.
- **Variable jump height:** cut upward velocity when the button is released early. Pair with stronger gravity while falling for a snappier arc.
- Read input in the frame update, consume it in the fixed update, so short presses aren't lost between ticks.

## Physics and collision

- Use **collision layers/masks** so bullets don't test against other bullets and pickups only test against the player; it is cheaper and avoids accidental interactions.
- Enable **continuous collision detection** only on small, fast objects that tunnel through walls; it costs more than discrete checks.
- Don't move static bodies every frame; use kinematic/animatable bodies for moving platforms, because engines rebuild static structures when they move.
- Many platformers use kinematic character controllers instead of full rigidbody physics, because precise, predictable movement feels better than simulated forces.

## Game feel ("juice")

Every player action deserves feedback within a frame or two: sound, animation, particles, a small camera response. Tools, roughly in order of payoff: easing curves instead of linear motion, squash and stretch, hit stop (freeze 30–100 ms on impact), screen shake (short, decaying, with an option to reduce or disable), particles, and layered audio. Add juice after the mechanic works; it hides problems during tuning. Details: `reference/game-feel.md`.

## UI and HUD

Keep the HUD minimal and readable at the smallest target resolution. Anchor UI to screen edges and safe areas rather than absolute positions. Separate UI from gameplay state: the HUD listens to events or reads a model; gameplay never reaches into UI nodes. Pause and settings menus must be reachable by keyboard, gamepad and touch.

## Audio

Route sounds through buses (master, music, SFX, voice, UI) with separate volume sliders. Randomize pitch slightly on repeated SFX to avoid fatigue. Limit concurrent instances of the same sound. On web, start audio only after a user gesture, because browsers block autoplay.

## Save systems

Store a **version number** in every save and write migrations from old versions; unversioned saves can't evolve. Serialize data, not engine objects. Write to a temp file and rename for atomic saves, so a crash mid-write doesn't corrupt progress. Keep settings separate from progress. See `reference/architecture.md`.

## Assets

Pack 2D sprites into **texture atlases** to cut draw calls. Use power-of-two or engine-recommended compressed texture formats per platform. Keep source files (Aseprite, Blender, audio projects) in version control with LFS, and generate exported assets through a repeatable pipeline. Record the license of every third-party asset.

## Performance

- Budget: **16.6 ms per frame at 60 FPS, 8.3 ms at 120 FPS**, shared by gameplay, physics, rendering and the engine itself.
- **Profile first** on the weakest target device (Godot profiler, Unity Profiler/Frame Debugger, Unreal Insights, browser Performance panel).
- Common wins: object pooling for frequently spawned objects, fewer draw calls via batching/atlases/instancing, avoiding per-frame allocations (GC spikes cause stutter in C#, JS and GDScript), spatial partitioning for many collision checks, LOD and culling in 3D.
- Details per engine: `reference/performance-and-platforms.md`.

## Mobile

Design for touch from the start: large touch targets, virtual controls only when needed, gestures that don't fight the OS. Handle many aspect ratios with a base resolution plus expand/letterbox rules and safe areas around notches. Cap frame rate (30 or 60) where the game allows, to save battery and heat. Pause on focus loss and save state on backgrounding.

## Multiplayer

Ask whether the game needs it; networking multiplies scope, testing and server cost. If it does: an **authoritative server** owns game state; clients send inputs, not results. Use **client-side prediction** with **server reconciliation** for the local player, **interpolation** for remote entities, and **lag compensation** for hit detection. Local/couch co-op or asynchronous play (ghosts, leaderboards) often deliver the social value at a fraction of the cost. See `reference/multiplayer.md`.

## Testing

- Unit-test pure rules (damage, inventory, scoring, state machines) separated from engine nodes.
- Make the simulation **deterministic** (fixed timestep, seeded RNG, no wall-clock reads in logic) so a recorded input stream replays identically; replays turn rare bugs into reproducible ones. See `reference/deterministic-simulation.md`.
- Run **automated playtests**: scripted or bot inputs that run a level headless and assert on outcomes (no crash, level completable, no soft-lock).
- Feel still needs human playtests; write down what testers should watch for.

## Accessibility

Offer remappable controls, subtitles with size and background options, colorblind-safe palettes (never encode meaning in color alone), options to reduce screen shake and flashing, adjustable difficulty or assist modes, and hold/toggle choices for held inputs. These cost little when planned early and are expensive to retrofit.

## Shipping

Automate per-platform builds (CI export from the engine's CLI). Strip debug tools from release builds. Meet store requirements: icons, age rating, privacy labels, platform guidelines on purchases and loot boxes, Google Play's target API level, and Steam's AI-content disclosure. Brazil's ECA Digital (Lei 15.211/2025, in force since March 2026) bans loot boxes in games aimed at or likely to be accessed by minors. Details: `reference/performance-and-platforms.md`. Add crash reporting. Collect analytics only with informed consent and in line with regional privacy law. Keep build numbers traceable to commits.

## Safety and IP

Use placeholder or original assets, or properly licensed packs. Don't reproduce copyrighted art, music, characters or a commercial game's name and branding; drawing on a mechanic is fine, a look-alike is not.
