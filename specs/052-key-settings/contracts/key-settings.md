# Contract: key settings (spec 052)

Three readers, one value. The value is built at boot (before the listener binds) and never changes for the life of the process.

## 1. `GET /settings` — JSON (default)

`200 OK`, `application/json`. Read-only; no other method, no body, no query.

```json
{
  "engine_defaults_sha256": "3f9a…e1",
  "entries": [
    { "group": "world",    "key": "width",  "value": 20, "source": "toml" },
    { "group": "world",    "key": "height", "value": 20, "source": "toml" },
    { "group": "world",    "key": "seed",   "value": 20260814, "source": "toml" },
    { "group": "kitty",    "key": "1", "value": { "name": "Miso", "behavior": "needs_driven" }, "source": "toml" },
    { "group": "kitty",    "key": "2", "value": { "name": "Biscuit", "behavior": "policy:e006a-L-04-s3" }, "source": "toml" },
    { "group": "vision",   "key": "radius", "value": 5, "source": "toml" },
    { "group": "vision",   "key": "memory_timeout_ticks", "value": 0, "source": "toml" },
    { "group": "meow",     "key": "relief_memory_margin", "value": 0, "default": "unbounded", "source": "toml" },
    { "group": "actions",  "key": "groom_cuddle_relief", "value": 15.0, "default": 15.0, "source": "toml" },
    { "group": "behavior", "key": "announce_here", "value": 0, "default": 0, "source": "default" },
    { "group": "behavior", "key": "contagion_aware_ladder", "value": false, "default": false, "source": "default" },
    { "group": "behavior", "key": "reply_intensity_floor", "value": "none", "default": "none", "source": "default" },
    { "group": "water",    "key": "bath_gain", "value": 3.5, "default": 3.5, "source": "toml" },
    { "group": "water",    "key": "bath_gain_ceiling", "value": 60.0, "default": 60.0, "source": "toml" },
    { "group": "water",    "key": "contagion_factor", "value": 0.0, "default": 0.0, "source": "default" },
    { "group": "water",    "key": "contagion_membership", "value": "option_a", "default": "option_a", "source": "default" },
    { "group": "watchdog", "key": "threshold", "value": 150, "default": 150, "source": "toml" },
    { "group": "watchdog", "key": "remind_every", "value": 150, "default": 150, "source": "toml" }
  ]
}
```

Rules: `entries` is ordered (display order); every listed key is present on every config; `default` is omitted for `world.*`, `kitty.*` and `vision.*` (required sections under the 3.0 rule — there is no default to fall back on); f32 dials print as written (`0.2`, not the f64 expansion); an Option key absent from the config carries its sentinel string (`"unbounded"`, `"none"`) in both `value` and `default`; `source` is decided by presence in the loaded file, so a key written at its default reads `"toml"`. (Values above are illustrative, not the served toml's.)

## 2. `GET /settings` — text (`Accept: text/plain`, and not `application/json`; a browser's `application/json, text/plain, */*` stays JSON)

`200 OK`, `text/plain; charset=utf-8`. Exactly the boot block: one line per entry, header first, trailing newline.

```text
engine_defaults_sha256 = 3f9a…e1
world.width = 20 [toml]
world.height = 20 [toml]
world.seed = 20260814 [toml]
kitty.1 = Miso needs_driven [toml]
kitty.2 = Biscuit policy:e006a-L-04-s3 [toml]
vision.radius = 5 [toml]
vision.memory_timeout_ticks = 0 [toml]
meow.relief_memory_margin = 0 (default: unbounded) [toml]
actions.groom_cuddle_relief = 15 (default: 15) [toml]
behavior.announce_here = 0 (default: 0) [default]
behavior.contagion_aware_ladder = false (default: false) [default]
behavior.reply_intensity_floor = none (default: none) [default]
water.bath_gain = 3.5 (default: 3.5) [toml]
water.bath_gain_ceiling = 60 (default: 60) [toml]
water.contagion_factor = 0 (default: 0) [default]
water.contagion_membership = option_a (default: option_a) [default]
watchdog.threshold = 150 (default: 150) [toml]
watchdog.remind_every = 150 (default: 150) [toml]
```

Line grammar: `<group>.<key> = <value>[ (default: <default>)] [<source>]`. Strings print bare; numbers print as `serde_json` prints them, so the example above is illustrative (a float default may render `15.0`); the test compares the endpoint text to `render_text()`, not to a hand-written string.

## 3. The boot log

One `info` event, message `key settings\n<the text block above>`, emitted by `KeySettings::announce()` — the same renderer as §2, pinned by a log-capture test (FR-012) — emitted after the config is validated and the registry checked, after the existing watchdog "standing by" line, and before the simulation task is spawned. The existing wet-fur / contagion / vision / ladder lines are unchanged.

## 4. `docs/deploy/update.sh` — the closing section

On the server-restart path, after `wait_healthy` succeeds, after the `deployed <rev>` line and the backup prune, the script fetches `http://$UPSTREAM/settings` with `Accept: text/plain` and:

| result | prints | exit |
|---|---|---|
| 200, non-empty body | `==> key settings` then the body verbatim | 0 |
| 404 | `!! this binary does not serve /settings (predates spec 052?)` | 2 |
| 200 empty, or any other status | `!! /settings answered <code> with an unusable body` | 2 |
| curl failed to connect / timed out, three tries two seconds apart | `!! the server stopped answering after the health check` | 2 |
| the section could not be written to stdout | `!! could not print the key settings section` | 2 |

Exit **2**, not 1: the rollback branch exits 1, and a wrapper reading `$?` must never take "deployed but unverified" for "rolled back". No rollback in any of these failures; the world is serving. The client-only path (`--client-only`) is unchanged.

## 5. What this contract does not touch

`GET /config` (byte-identical on the same config), `engine_defaults_sha256`, every other endpoint, the websocket, the snapshot.
