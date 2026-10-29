# Deterministic Simulation

A deterministic simulation produces the same outputs every time it is given the same starting
state, seed and inputs. That one property buys three things: **replays** (store the seed and the
input stream, not the frames), **rollback and lockstep netcode** (peers resimulate from inputs and
agree on the result), and **reproducible bugs** (a bug report becomes a seed plus an input file
that fails the same way on every machine).

## The contract

```text
simulate(state | scenario, seed, inputs[]) -> outputs (final state, events, score)
```

Treat the simulation as a pure function of those arguments. Rendering, audio, UI and networking
read its outputs; they never feed back into it except as recorded inputs.

## Rules for sim code

- **Seeded PRNG only.** Use a small explicit generator (PCG, xoshiro, mulberry32 in JS) owned by
  the sim state and seeded from the scenario. No `Math.random()`, `Random.Range` on a global
  instance, `randf()` without a dedicated `RandomNumberGenerator`, or OS randomness inside the sim.
  Give separate streams to systems that should not disturb each other (loot vs AI), so adding a
  particle effect does not change which item drops.
- **Fixed timestep.** Advance the sim in constant ticks (see `architecture.md`); never multiply by
  a frame `delta`. Count time in ticks, not seconds.
- **No wall clock and no IO.** No `Date.now()`, `performance.now()`, `Time.time`, file or network
  reads inside the sim. Anything external enters as a timestamped input.
- **Stable iteration order.** Iterate entities by ID or in insertion order, never over hash maps or
  sets whose order can vary between runs or runtimes.
- **Numerics.** Floating point is deterministic on the same build and platform; across platforms,
  compilers or engines it often is not. For cross-platform lockstep or rollback, use fixed-point or
  integer math in the sim, and keep engine physics out of it (most engine physics is not
  cross-platform deterministic).
- **Keep engine nodes out.** Put the sim in plain modules (pure data + functions) that the engine
  layer calls once per tick. This also makes it testable headless.

## Determinism tests

Run the same scenario twice with the same seed and inputs, hash the resulting state, and compare.

```ts
test("sim is deterministic", () => {
  const a = run(scenario, 1234, inputs);
  const b = run(scenario, 1234, inputs);
  expect(hash(a.state)).toBe(hash(b.state));
  expect(hash(run(scenario, 1235, inputs).state)).not.toBe(hash(a.state)); // seed actually matters
});
```

- Hash a canonical serialization (sorted keys, fixed float formatting), not object identity.
- Also hash per tick in a debug mode: the first tick where two runs diverge points at the bug.
- Keep a few **golden replays** (seed + inputs + expected final hash) in the repo and run them in
  CI; a changed hash after a refactor means behavior changed, intended or not.
- For netcode, run the same test across the platforms you ship on.
