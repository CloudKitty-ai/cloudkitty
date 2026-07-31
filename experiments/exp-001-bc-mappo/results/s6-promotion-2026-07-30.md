# Promoting arm2-g0p998-s6 into the served world — pre-soak probe + seating record (2026-07-30)

Owner call: s6 goes to the §9.1 deployment soak. Seat: **Miso** (kitty 1)
— the seat `kitty-eval`'s Mixed roster certified (subject at index 0),
so the soak matches the certification evidence as closely as the served
world allows. Selection: greedy (`sample = false`), the certified
condition.

## The one unmeasured interaction, closed before seating

Every certified run had either four s6 copies (AllSubject) or
all-`needs_driven` teammates (Mixed). The real served world has
**Biscuit on `playful`** — an interaction never evaluated. Closed with
the env chain (`forensics_replay.py --control`, which the forensics work
showed is tick-exact with the engine chain): s6 seated as Miso with the
as-configured roster vs the served world as it runs today, seeds 1–10,
20,000 ticks continuous, clock pinned (deploy semantics).

| | seated (s6 as Miso) | baseline (all scripted) |
|---|---|---|
| Paired Nash welfare Δ | **+0.0145 mean, +0.0120 min, 10/10 seeds** | — |
| Distress ticks, any kitty | **0** across all 200k ticks | 0 |
| Miso happiness | 93.5 | 90.3 |
| Biscuit (playful) | 79.0 | 77.4 |
| Pumpkin | 89.6 | 88.9 |
| Kittybear | 90.6 | 90.3 |

Every kitty is better off with s6 seated, including the playful
teammate it never trained or evaluated with. And the meow channel is
alive in deployment conditions: **0.101% of Miso's decisions** — 137
MeowPurr, 65 MeowWantDrink across 200k ticks.

## Config change (cloudkitty.toml, staged on this branch)

- `[[kitty]] id 1 (Miso): behavior = "policy:s6"`
- `[rl.policy.s6] artifact = "experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s6/arm2.ckpolicy"`
  (sha256 `8030b94d…`; the server validates schema + logs the hash at
  startup, spec 014 FR-016)

Validated without touching a running server: TOML parses; the eval
chain accepts the seated config (`kitty-eval --brain needs_driven
--config cloudkitty.toml` exit 0 — kitty behaviors are overridden by
the roster mode, so eval tooling is unaffected); the artifact itself
has passed `PolicyArtifact::load` validation in every certification.
**Startup validation (the `policy artifact validated` log line) is the
owner's step** — this session is not permitted to start/stop servers.

**Deployment caveat**: the artifact lives under `artifacts/` which is
gitignored (machine-local). If the served instance runs from this
checkout, the path resolves; if it deploys elsewhere, the artifact file
must travel with it (or be committed / given a durable home — owner's
call).

## Soak protocol (§9.1: one policy kitty in the served world, days)

- **Watch**: Miso's card + housemates in the client; the distress cue
  fires at 60 unresolved ticks (`[viewer] distress_patience_ticks`),
  well inside certification's 150-tick bound — any visible cue is
  already a signal worth logging.
- **Abort criteria** (revert the config commit + restart): any
  unresolved distress ≥ 150 ticks; Miso idling visibly (the F-010
  signature — not expected here, all slots are full); any kitty's
  happiness sagging below its baseline band above for a sustained
  stretch.
- **Success**: days at or above the probe's welfare band with zero
  aborts → exp-001's §9 decision rule 1 completes end-to-end.

## Regeneration

```
PY=experiments/exp-001-bc-mappo/trainer/.venv/bin/python
A=experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s6
for s in $(seq 1 10); do
  $PY experiments/exp-001-bc-mappo/trainer/forensics_replay.py \
      --policy $A/policy-final.pt --config cloudkitty.toml --seed $s \
      --ticks 20000 --horizon 20000 --pin-clock \
      --control kitty_2=playful,kitty_3=needs_driven,kitty_4=needs_driven
  # baseline arm: add kitty_1=needs_driven to --control
done
# Nash-of-happiness comparison from the saved presoak-*.npz (same
# formula both arms: exp(mean log happiness/100) averaged over ticks)
```
