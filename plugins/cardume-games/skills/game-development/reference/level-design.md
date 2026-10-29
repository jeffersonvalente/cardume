# Content and Level Design

## One lesson per level

Each level or scenario teaches exactly one thing: a new mechanic, a new interaction between two
known mechanics, or a new way to use one. Write that lesson as a single sentence before building.
If the sentence needs "and", split the level in two; players who fail a two-lesson level can't
tell which lesson they missed.

## One meaningful trap

Plant one trap or misdirection per level: the obvious approach that fails, the tempting pickup
that leads to a dead end, the enemy that looks like the threat but isn't. It should be fair (the
information to avoid it is visible) and it should teach, ideally reinforcing the level's lesson.
One trap creates an "aha"; several in one level create frustration.

## Difficulty ramps by combination

Raise difficulty by combining mechanics the player already knows, not by adding unexplained ones
or just inflating numbers (more HP, less time). A typical arc per mechanic: introduce it safely →
test it alone → combine it with an earlier mechanic → twist it. Interleave easier levels after
spikes so the curve is a sawtooth, not a wall.

## Data-driven content files

- Store levels as data (JSON, TOML, Godot Resources, ScriptableObjects), not code, so designers
  can edit them and tools can check them.
- Define a **JSON Schema** (or the engine's typed resource) for the format, versioned like saves.
- Ship a **validator CLI** that checks every level file: schema validity, references resolve (tile
  IDs, enemy types), the level is reachable (start connects to exit), and it only uses mechanics
  unlocked by that point in the progression. Run it in CI and in the editor's save hook.

```text
$ node tools/validate-levels.js levels/
levels/07-ice.json: ok
levels/08-ice-and-switches.json: error: uses mechanic "switch" first unlocked at level 09
```

## Reference solution per level

Store a reference solution next to each level: an input sequence or move list that completes it
using only the mechanics available at that level. It proves the level is solvable as designed and
catches accidental shortcuts or soft-locks when content or rules change.

- Run every reference solution headless in CI (this pairs with a deterministic sim: see
  `deterministic-simulation.md`); a level whose solution stops working is a broken level.
- Playtest each level against its reference: watch testers and note where they diverge from the
  intended path. If most players find a different solution, either the lesson is not landing or
  the level teaches something else, and the design sentence should change to match.
