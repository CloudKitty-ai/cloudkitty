# Deploying CloudKitty

How to run the sanctuary on a real server. One binary serves everything —
the simulation, the read-only API, the WebSocket, and the viewer itself —
so deployment is: build it, keep it on loopback, and put a TLS reverse
proxy in front. This doc records the recommended shape (Caddy + systemd)
and the reasoning, drawn from the 2026-07-22 security assessment.

## The shape

```
browser ── https ──> Caddy ── http (loopback) ──> cloudkitty-server :8090
                                                        │
                                                  snapshot.json
```

The server deliberately speaks plain HTTP with no auth: every endpoint is
read-only (viewers watch the world, they never touch it — Article V), so
the proxy's job is TLS, compression, and being the only thing reachable
from outside. Keep `bind` on loopback so the binary itself never is:

```toml
[world]
bind = "127.0.0.1:8090"   # the default; the proxy is the public face
```

## Build and run

```bash
cargo build --release
./target/release/cloudkitty-server
```

Run it from the repository root: the viewer is served from `./client`,
and the world saves to `snapshot.json` in the working directory (both
paths are configurable — `--client` and `--snapshot` / the
`[persistence]` block). Started from anywhere else, the server falls back
to the workspace copy of the viewer and says so in the log.

The world saves itself every `save_every_ticks` ticks and again on
graceful shutdown, atomically (temp file + rename), so a crash mid-write
can cost at most one save interval — never the world.

## Caddy

The whole recommended Caddyfile:

```caddyfile
cloudkitty.example.com {
	encode zstd gzip
	reverse_proxy 127.0.0.1:8090
	header {
		X-Content-Type-Options nosniff
		X-Frame-Options DENY
		Referrer-Policy no-referrer
	}
}
```

Why each line earns its place:

- **Caddy itself** brings automatic HTTPS, HTTP/2, and transparent
  WebSocket proxying — `/ws` needs no special stanza.
- **`encode zstd gzip`** is the biggest practical win. The per-tick world
  JSON is highly repetitive and compresses dramatically, which blunts the
  bandwidth cost of many viewers.
- **The three headers** are the standard hardening set the app does not
  send itself. Do **not** add a `Cache-Control` override: the server
  sends `no-cache` on static files deliberately, so browsers revalidate
  the viewer instead of serving a stale one for hours after a deploy.
- **Rate limiting** is absent because stock Caddy has none. The server
  already serializes the world once per tick no matter how many viewers
  share it (PR #29), which removes the cheap CPU-amplification vector; if
  connection-level limits ever become necessary, that is the
  `mholt/caddy-ratelimit` plugin via an `xcaddy` build.

## systemd

```ini
[Unit]
Description=CloudKitty — a cute, safe sandbox where kitties frolic
After=network.target

[Service]
WorkingDirectory=/opt/cloudkitty
ExecStart=/opt/cloudkitty/target/release/cloudkitty-server
Restart=on-failure

# The server takes its final world save on SIGINT (Ctrl-C); systemd's
# default SIGTERM would skip it. Periodic saves bound the loss either
# way, but there is no reason to lose even one interval on purpose.
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
```

The `KillSignal` line is the one non-obvious part: graceful shutdown —
"letting the kitties settle", final save included — listens for SIGINT
only.

## Updating

```bash
git pull
cargo build --release
sudo systemctl restart cloudkitty
```

Two things to know before restarting into new code or config:

- **Snapshots are guarded by a config fingerprint.** If the config
  changed shape (world size, roster, …), the server refuses to resume the
  old world rather than silently discarding it, and the error says what
  to do: change the config back, point `--snapshot` elsewhere, or start
  over with `--fresh`.
- **`--fresh` never loses a world by accident**: the old save is moved
  aside to `snapshot.json.<timestamp>.bak` first (pass `--no-backup` to
  skip that).

## What is public, on purpose

Worth knowing when you point the internet at it:

- **Everything in `client/` is served.** Any file dropped in that
  directory becomes public. The snapshot lives outside it, so world saves
  are never downloadable.
- **`GET /config` returns the full simulation config**, including the
  world seed, the snapshot path, and the bind address. With the seed and
  a snapshot the world's future is predictable — CloudKitty is a
  deterministic fishbowl, and this is the fishbowl glass. The `[rl.*]`
  blocks (policy artifact paths) are *not* served.
- **CORS is permissive**: any website can read the API from a visitor's
  browser. For public read-only data this is a choice, not an oversight.
- **There are no accounts and no rate limits** in the app itself. The
  worst realistic outcome of hostile traffic is a degraded viewer, never
  a compromised world — but if a deployment ever needs limits, they
  belong in the proxy (see the Caddy note above).
