# PR body draft: 043 — the `announce_here` knob

(Opening the PR is the owner's call. Body below.)

---

Spec 043: scripted cats can volunteer here-words, behind a knob that is
off — and byte-identical to today — until Experiments' here-word density
screen arms it.

## What

- `[behavior] announce_here` (u64, default 0/absent): the here-word
  announce period. Off = today's engine, byte-for-byte (stamp guard
  extended with the key; golden `7b361b2a…` green **unregenerated**;
  zero modified existing tests).
- Knob on: on a cat's phase ticks (`(tick + kitty_id) % period == 0`,
  the `critter_moves_this_tick` idiom) a message slot the want loop left
  Silent may carry one of the four Here\* kinds, chosen among the LEGAL
  kinds (unchanged `message_legal` law: adjacency, vocabulary flag,
  per-kind cooldown) by a stateless counter over the new
  `MessageKind::HERE_KINDS` order. No RNG, no new state, no wire/schema
  changes — a resumed run speaks identically to an unbroken one.
- Precedence (owner ruling 2026-08-23) holds by construction: the here
  path runs strictly after the want loop, and WaitForMe rides the
  message slot before `announce` is consulted at all — WaitForMe >
  want-word > here-word > Silent.

## ⚠ Deviation from the handoff — FLAG TO EXPERIMENTS (accepted 2026-08-30)

The handoff's literal selection `(tick + kitty_id) % n_legal` **aliases
against the phase gate**: on speaking ticks `tick + kitty_id` is a
multiple of the period, so the index only reaches multiples of
`gcd(period, n_legal)` — at period 4 with 2 or 4 legal words it is
pinned to index 0 (only `here_food` would ever be spoken). Implemented
instead: the speaking-tick counter
`((tick + kitty_id) / period) % n_legal`, which reduces to the handoff's
formula at period 1 (research D3; spec FR-006 as amended). Experiments
verified the algebra and amended the screen plan @ f0eaf84, noting kind
selection is a deterministic round-robin — per-kind corpus shares track
LEGALITY shares, not an independent draw. The cycling guard in
`behavior/mod.rs` reds under the literal formula (injection-proven).

## Gate zero — the screen's acceptance test, now in-tree

`tests/announce_here_gate_zero.rs`: same-seed lockstep worlds, defaults
vs defaults+knob. Per-tick **action projections** (id, pos, activity,
last_action — NOT the world fingerprint, which lawfully differs knob-on
via cooldowns/recent_meows) are equal; the armed run actually speaks
Here\* (445 emissions in 2,000 ticks at period 1); want/WaitForMe
streams are identical. This test is simultaneously the standing
no-scripted-here-listener guard: a future rung acting on heard Here\*
words reds it. Same file: the SC-003 density ladder (445/301/129 at
periods 1/4/16, strict) and SC-004 armed-run determinism.

If the projection assertion ever reds, the feature stops — report,
never weaken (handoff rule).

## Discipline

- Two commits: config surface inert, then the here path + instruments.
- Every new guard shown red first for its predicted reason —
  12 injection cycles recorded in `specs/043-announce-here/redden-list.md`
  (two pre-impl predictions corrected there, with the honest reds
  obtained by post-impl injections).
- Continuity: `specs/043-announce-here/continuity-baseline.md` — 725
  green at branch base, 737 green at head, stamp + golden unmoved at
  both commits.
- Docs: commented `announce_here` block in `cloudkitty.toml` (value NOT
  set — the served world launches knob-off), CHANGELOG Unreleased entry
  (no `[stamp]` marker — the stamp does not move).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_017Wov2on3vAYMEAYCCTWb9y
