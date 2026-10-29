# Game Feel

## Platformer controller tunables

Expose these as data and tune them in playtests. Starting values (pixel-art scale, 60 Hz):

| Tunable | Start | Notes |
|---------|-------|-------|
| Run acceleration / deceleration | reach top speed in ~0.1 s / stop in ~0.05 s | Faster stop feels more responsive |
| Air control | 60–80% of ground acceleration | Lower for weightier characters |
| Jump height & time to apex | derive gravity and jump velocity from these | Designers think in heights, not forces |
| Fall gravity multiplier | 1.5–2.5× | Snappier descent, less floaty |
| Jump cut multiplier | velocity × 0.4–0.5 on early release | Variable jump height |
| Coyote time | 80–120 ms | Jump allowed after leaving a ledge |
| Jump buffer | 100–150 ms | Jump pressed before landing still fires |
| Max fall speed | clamp | Keeps landings readable |
| Apex hang | reduce gravity near apex when holding jump | Optional, adds control |

Derive physics from design intent:

```text
gravity      = 2 * jumpHeight / timeToApex^2
jumpVelocity = gravity * timeToApex
```

Also consider corner correction (nudge the player around a ceiling edge they barely clip) and ledge forgiveness on landings.

## Input

- Action mapping layer: gameplay reads `jump`, never `Space` or `button 0`.
- Buffer presses with a timestamp; consume them when valid.
- Poll per frame, apply in fixed update; store "pressed this frame" flags until consumed.
- Dead zones for analog sticks; normalize diagonal movement.
- Touch: virtual stick or tap zones sized at least ~9–10 mm; consider auto-run designs instead of on-screen d-pads.

## Juice toolkit

| Technique | Use | Keep in check |
|-----------|-----|---------------|
| Easing | All UI and camera motion; ease-out for arrivals | Linear motion reads as mechanical |
| Squash & stretch | Jump takeoff, landing, impacts | Preserve approximate volume |
| Hit stop | Freeze 30–100 ms on heavy hits | Too long breaks rhythm |
| Screen shake | Explosions, heavy hits; trauma value decaying over time, noise-based offset | Always offer reduce/off |
| Particles | Dust on land/run, sparks on hit | Pool them; cap counts on mobile |
| Flash / tint | Damage feedback | Avoid rapid full-screen flashing (photosensitivity) |
| Audio | Every action has a sound; layer and pitch-vary | Limit concurrent voices |
| Camera | Look-ahead in move direction, smoothing, dead zone | Avoid motion sickness in 3D: limit FOV changes |
| Knockback | Communicates force | Don't take control away for long |

Add juice once mechanics are tuned; it can hide feel problems during iteration.

## Camera

2D: follow with smoothing and a dead zone, look-ahead in movement direction, clamp to level bounds, pixel-snap in pixel-art games. 3D: collision-aware third-person boom, avoid clipping into walls, separate look sensitivity for mouse and stick, invert options.
