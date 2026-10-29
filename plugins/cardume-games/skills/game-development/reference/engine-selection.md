# Engine Selection

Pick by target platform first, team skills second, genre third. An engine the team already knows usually beats a "better" one they don't.

## Questions to answer first

1. Which platforms must ship (web, iOS/Android, desktop, consoles)? Console support narrows choices most.
2. 2D, 3D, or 2.5D? How high is the visual fidelity bar?
3. What languages does the team know (C#, GDScript/Python-like, C++, TypeScript, Rust, Lua)?
4. Is an editor required for designers and artists, or is a code-first workflow acceptable?
5. Licensing and revenue terms acceptable for the project's business model?
6. How long is the project: jam, months, years?

## Matrix

| Engine | Strengths | Weaknesses | Typical fit |
|--------|-----------|------------|-------------|
| **Godot 4** | Free and open source (MIT), light editor, excellent 2D, node/scene composition, GDScript iteration speed, C# option | Console ports via third-party publishers; 3D ecosystem smaller than Unity/Unreal; Godot 4 C# projects cannot export to the web yet (check the current export docs) | Indie 2D, stylized 3D, jams, teams that value openness |
| **Unity** | Huge ecosystem and asset store, strong mobile and cross-platform reach, C#, mature tooling | Licensing/terms have changed before; large projects need discipline; editor weight | Mobile, mid-size 3D, cross-platform commercial games |
| **Unreal Engine 5** | Top-tier rendering (Nanite, Lumen), Blueprints plus C++, robust networking framework | Heavy hardware and build times, steep C++ curve, large binaries | High-fidelity 3D, shooters, large teams |
| **Phaser** | Complete 2D web framework: scenes, arcade/matter physics, input, loader, tweens | 2D only; performance bounded by browser; you set up bundling | Browser 2D games, ads/playables, educational games |
| **PixiJS** | Very fast 2D WebGL/WebGPU renderer, flexible | No physics, scenes or game loop policy; you assemble the engine | Custom web engines, UI-heavy 2D, visual toys |
| **Three.js** | De facto 3D library for the web, large community | Library, not engine: no editor, physics or scene management by default | Web 3D experiences, small 3D games with custom structure |
| **Babylon.js** | More complete web 3D engine: physics plugins, GUI, inspector, editor tooling | Larger bundle; smaller community than Three.js | Web 3D games wanting batteries included |
| **Bevy** | Rust, ECS-native, high performance, code-first, open source | Frequent breaking changes, no mature editor, smaller ecosystem | Rust teams, simulation-heavy games, systems-minded developers |
| **LÖVE** | Simple Lua framework, quick to learn, great for jams | No editor, minimal built-ins, mobile/web support less polished | Small 2D games, prototypes, learning |
| **Defold** | Small runtime, strong mobile and web export, free | Lua, smaller community, opinionated message-passing model | Lightweight mobile/web 2D |
| **raylib** | Tiny C library, many bindings, no dependencies | Everything beyond basics is yours to build | Learning, tools, very small games |

## Quick picks

- Browser 2D game, TypeScript team → Phaser (or PixiJS if you want full control).
- Browser 3D → Three.js for flexibility, Babylon.js for completeness.
- 2D indie for desktop and Switch-class consoles → Godot (plan the porting route) or Unity.
- Mobile-first commercial game → Unity or Defold; Godot is viable for 2D.
- Photoreal 3D → Unreal 5.
- Rust team or ECS-heavy simulation → Bevy.
- Game jam → whatever the team already knows best.

## Red flags

- Choosing an engine for a feature the game doesn't need yet.
- Writing a custom engine when the goal is shipping a game.
- Ignoring console requirements until late: certification and porting shape architecture.
