# Phaser Snippets (TypeScript, web)

Targets Phaser 4 (4.0.0 stable April 2026; check npm for the current 4.x). The calls below (game config, Arcade physics, camera shake, tweens, groups, keyboard) have the same signatures in Phaser 3 and 4, so they work in both. Phaser 4's breaking changes are mostly in rendering: a new WebGL renderer, the Canvas renderer deprecated, FX and masks merged into filters, custom pipelines replaced by render nodes, and `roundPixels` defaulting to `false`. See the official v3→v4 migration guide in the Phaser repo (`changelog/v4/4.0/MIGRATION-GUIDE.md`). Use Vite or a similar bundler.

## Project structure

```text
src/
  main.ts            # Phaser.Game config
  scenes/            # Boot, Preload, Title, Game, UI (HUD as a parallel scene)
  entities/          # Player.ts, Enemy.ts
  systems/           # input.ts, audio.ts, save.ts
  data/              # tuning.json, levels/*.json (Tiled exports)
public/assets/       # atlases, audio
```

## Game config with fixed-step arcade physics

```ts
import * as Phaser from "phaser";   // works with the package's ESM build and its `export =` typings
import { GameScene } from "./scenes/GameScene";

new Phaser.Game({
  type: Phaser.AUTO,           // WebGL, falling back to the deprecated Canvas renderer
  width: 480,
  height: 270,
  pixelArt: true,
  roundPixels: true,           // v4 default is false; pixel art usually wants it on
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  physics: { default: "arcade", arcade: { gravity: { x: 0, y: 0 }, fps: 60, fixedStep: true } },
  scene: [GameScene],
});
```

Arcade physics then steps at a fixed 60 Hz independent of display refresh. For logic in `update(time, delta)`, scale by `delta / 1000` and clamp `delta`.

## Player with coyote time, jump buffer and variable jump

```ts
export const tuning = {
  speed: 160, accel: 1600, jumpHeight: 56, timeToApex: 0.34,
  fallGravityMult: 2, jumpCut: 0.45, coyoteMs: 100, bufferMs: 120,
};

export class Player extends Phaser.Physics.Arcade.Sprite {
  private gravity = (2 * tuning.jumpHeight) / tuning.timeToApex ** 2;
  private jumpVelocity = this.gravity * tuning.timeToApex;
  private coyote = 0;
  private buffer = 0;

  constructor(scene: Phaser.Scene, x: number, y: number, private keys: { left: Phaser.Input.Keyboard.Key; right: Phaser.Input.Keyboard.Key; jump: Phaser.Input.Keyboard.Key }) {
    super(scene, x, y, "player");
    scene.add.existing(this);
    scene.physics.add.existing(this);
  }

  step(deltaMs: number) {
    const dt = Math.min(deltaMs, 50) / 1000;
    const body = this.body as Phaser.Physics.Arcade.Body;
    const onFloor = body.blocked.down;

    this.coyote = onFloor ? tuning.coyoteMs : Math.max(this.coyote - deltaMs, 0);
    if (Phaser.Input.Keyboard.JustDown(this.keys.jump)) this.buffer = tuning.bufferMs;
    else this.buffer = Math.max(this.buffer - deltaMs, 0);

    let vy = body.velocity.y + this.gravity * (body.velocity.y > 0 ? tuning.fallGravityMult : 1) * dt;
    if (this.buffer > 0 && this.coyote > 0) { vy = -this.jumpVelocity; this.buffer = this.coyote = 0; }
    if (Phaser.Input.Keyboard.JustUp(this.keys.jump) && vy < 0) vy *= tuning.jumpCut;

    const dir = (this.keys.right.isDown ? 1 : 0) - (this.keys.left.isDown ? 1 : 0);
    const vx = Phaser.Math.Linear(body.velocity.x, dir * tuning.speed, Math.min(tuning.accel * dt / tuning.speed, 1));
    body.setVelocity(vx, vy);
  }
}
```

Keep tuning in a JSON or TS object so it can be tweaked live (a small debug panel such as lil-gui helps during playtests).

## Juice helpers

```ts
// screen shake and hit stop
this.cameras.main.shake(120, 0.004);
this.physics.world.pause();
this.time.delayedCall(60, () => this.physics.world.resume());

// squash on landing
this.tweens.add({ targets: player, scaleX: 1.2, scaleY: 0.8, duration: 60, yoyo: true, ease: "Quad.easeOut" });
```

## Pooling with groups

```ts
const bullets = this.physics.add.group({ classType: Bullet, maxSize: 64, runChildUpdate: true });
const b = bullets.get(x, y) as Bullet | null;   // reuses inactive members
b?.fire(dir);
// on hit or out of bounds: b.disableBody(true, true)
```

## Audio unlock and versioned save

```ts
// Phaser unlocks Web Audio on the first user gesture; wait for it before starting music
if (this.sound.locked) this.sound.once(Phaser.Sound.Events.UNLOCKED, () => this.sound.play("music"));
else this.sound.play("music");

const SAVE_KEY = "save";
const SAVE_VERSION = 2;
export function save(data: object) {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify({ version: SAVE_VERSION, ...data })); } catch { /* storage may be unavailable */ }
}
```

## Testing

Put rules (scoring, damage, state machines) in plain TS modules and unit-test them with Vitest; run headless browser smoke tests with Playwright that load the game, send inputs, and assert on a debug state exposed for tests.
