# Contract: `decision_request` on the lab binding (spec 055)

The surface Experiments' harness builds against, in parallel with the
branch. Owner-confirmed at the 2026-09-20 clarify: pull method, seed
rendered without consuming, misuse always errors.

## Python

```python
line: str = env.decision_request(kitty_id)   # ParallelEnv; int id or "kitty_N"
request = json.loads(line)                    # the spec 053 wire document
```

Amended at review (2026-09-20): the method accepts the numeric id or the
`"kitty_N"` agent-name form; calls before the first `reset()` raise
`ValueError` ("reset first" — the window opens at reset, exactly as
promised below); a poisoned episode raises `RuntimeError`, matching
`step()`'s exception class for the same fault. Everything else stands.

- Callable after `reset()`/`step()` returns and before the next
  `step()` — the current decision window. Each call renders fresh; no
  caching, no staleness.
- Returns the exact line the served wire would POST for that kitty's
  decision this tick: `v`, `tick`, `kitty_id`, `me`, `world` (the fog
  view), `seed`, `config` — byte-equal, engine-serialized.
- The `seed` is the value the served request would carry, derived
  without touching the kitty's stream: calling this method never
  changes any trajectory, however often it is called, for any kitty.
- Errors (`ValueError`, message names the kitty and the reason):
  unknown kitty id; episode over (truncated or poisoned); no decision
  window. Never `None`, never placeholder or stale bytes.
- Works for every roster kitty regardless of seat (policy, scripted,
  external) — rendering an unasked kitty's request costs only the call.

## Rust (for completeness)

`Episode::decision_request(&self, kitty: KittyId) -> Result<String, EpisodeError-shaped error>`
with the same window and error semantics; `cloudkitty-py` wraps it
verbatim.

## Not in this contract

`VectorEnv` (out of scope, R4); any change to the wire, the envs'
existing methods, or `docs/plugins.md` beyond one pointer sentence.
