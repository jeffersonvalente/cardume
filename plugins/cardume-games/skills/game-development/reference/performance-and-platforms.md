# Performance and Platforms

## Frame budget

| Target | Budget per frame |
|--------|------------------|
| 30 FPS | 33.3 ms |
| 60 FPS | 16.6 ms |
| 90 FPS (VR minimum) | 11.1 ms |
| 120 FPS | 8.3 ms |

Leave headroom (~20%) for spikes and the OS. Measure on the weakest target device, in a release build.

## Profiling per engine

| Engine | Tools |
|--------|-------|
| Godot | Debugger → Profiler, Monitors, Visual Profiler; `--print-fps`; Video RAM tab |
| Unity | Profiler (CPU, GPU, memory, GC Alloc column), Frame Debugger, Memory Profiler, Profile Analyzer |
| Unreal | Unreal Insights, `stat unit`, `stat gpu`, GPU Visualizer |
| Web (Phaser/Pixi/Three/Babylon) | Browser Performance panel, memory snapshots, Spector.js for WebGL, Babylon Inspector, `renderer.info` in Three.js |
| Bevy | `tracing` with Tracy, diagnostics plugins |

Decide CPU-bound vs GPU-bound first (does lowering resolution help? then GPU-bound).

## Common fixes

- **Object pooling:** pre-allocate bullets, particles, enemies, damage numbers; deactivate instead of destroying.
- **Allocation in the hot loop:** reuse vectors/arrays, avoid closures and string building per frame, cache component lookups. GC pauses cause visible hitches in C#, JS and GDScript.
- **Draw calls:** texture atlases, sprite batching, GPU instancing for repeated meshes, fewer materials, static batching.
- **Overdraw:** large transparent sprites and particles are expensive on mobile GPUs.
- **Physics:** collision layers, simpler colliders, fewer active bodies, sleeping, spatial partitioning (grids, quadtrees) for custom checks.
- **3D:** LOD, frustum and occlusion culling, baked lighting where possible, texture compression.
- **Loading:** stream or async-load assets; avoid loading on the main thread mid-gameplay.
- **Web:** compress assets, lazy-load levels, watch bundle size and memory on mobile browsers, handle WebGL context loss.

## Mobile specifics

- **Resolution and aspect:** design at a base resolution; choose expand (show more world) or letterbox; respect safe areas around notches and gesture bars; test 16:9 through ~20:9 and tablets at 4:3.
- **Battery and thermals:** cap frame rate where gameplay allows, lower update rates on menus, pause when backgrounded. Sustained thermal throttling halves performance on many phones.
- **Touch:** large targets, no hover-dependent UI, multi-touch handling, avoid gestures that conflict with system edge swipes.
- **Lifecycle:** save on pause/background; handle audio interruptions (calls); resume gracefully.
- **Size:** store download limits and user patience; split optional content into on-demand downloads.

## Shipping checklist

- Reproducible CI builds via the engine CLI (Godot `--headless --export-release`, Unity `-batchmode -executeMethod`, Unreal `RunUAT BuildCookRun`, web bundler build).
- Release builds without debug overlays, cheats or verbose logging.
- Version numbers traceable to commits; symbol files kept for crash reports.
- Store assets: icons, screenshots, trailer, descriptions, age rating questionnaire, privacy labels.
- Platform rules: in-app purchase policies, loot box odds disclosure where required, children's privacy rules if relevant.
- **Brazil, ECA Digital (Lei 15.211/2025, in force since 17 March 2026):** art. 20 bans loot boxes in electronic games aimed at, or likely to be accessed by, children and adolescents, judged by the game's age rating (classificação indicativa). The law also covers games run from abroad that reach Brazilian minors; check the implementing decrees and get legal advice before shipping paid random rewards to Brazil. Source: <https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15211.htm>.
- **Google Play target API:** from 31 August 2026, new apps and updates must target Android 16 (API 36) or higher (Wear OS, Automotive, TV and XR have lower floors; extensions to 1 November 2026 on request). Check <https://developer.android.com/google/play/requirements/target-sdk> for the current rule; engine versions must support the required SDK.
- **Steam AI disclosure:** the Steamworks Content Survey asks you to disclose AI-generated content that ships in the game or that players consume (art, audio, text, localization), and to describe guardrails for content generated live at runtime; AI tools used only for development efficiency are out of scope. Check the current survey wording on partner.steamgames.com before submitting.
- Analytics and crash reporting with an explicit consent prompt where law requires; collect the minimum data needed.
- Console certification requirements (suspend/resume, save handling, user switching) planned early when consoles are a target.
