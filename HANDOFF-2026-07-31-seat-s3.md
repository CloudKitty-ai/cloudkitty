# Handover: Experiments → Product — seat s3 as Kittybear (2026-07-31)

The owner has adopted the pair-screen recommendation: the served world
gets its second policy kitty — **s3 drives Kittybear** (Seating B).
Evidence: [pair-screen-2026-07-31.md](experiments/exp-001-bc-mappo/results/pair-screen-2026-07-31.md)
(both seatings passed; B recommended per the pre-registered rule) on
top of [recert-2026-07-31.md](experiments/exp-001-bc-mappo/results/recert-2026-07-31.md)
(s3 certified clean on the current engine + 24×24: +0.0427 AllSubject,
all gates zero). Everything below is small, and none of it touches the
engine.

## The change (Product)

1. **Byte-identical artifact move** (the policies/ rule — copy, never
   re-export):
   `experiments/exp-001-bc-mappo/artifacts/arm2-g0p998-s3/arm2.ckpolicy`
   → `policies/s3.ckpolicy`. Committed bytes MUST hash
   `bbaf5f8bbfc312447046aae326eaff23cee9454a6d143cb472adbade9187aad2`.
2. **README row** (`policies/README.md`), same shape as s6's:
   filename → that sha256 → provenance "exp-001 arm2, γ = 0.998,
   seed 3 (BC → MAPPO); drives Kittybear (`policy:s3`), greedy
   selection" → certification `recert-2026-07-31.md` (certify clean)
   + `pair-screen-2026-07-31.md` (seating screen, Seating B).
3. **`cloudkitty.toml`**:
   - Kittybear (`[[kitty]]` id 4): `behavior = "needs_driven"` →
     `behavior = "policy:s3"`, with a one-line comment citing the
     pair-screen (mirror Miso's seating comment style).
   - New block, mirroring s6's exactly (greedy = default, matching
     the certified condition):
     ```toml
     [rl.policy.s3]
     artifact = "policies/s3.ckpolicy"
     ```
   - Do NOT touch Miso/s6, Biscuit, or Pumpkin. Biscuit stays
     `playful` (owner constraint: the meow instigator keeps its
     script).

## Deploy (owner, after the merge)

One server restart. **No `--fresh`** — geometry is unchanged; the
snapshot is compatible. This restart also picks up s6's
`policies/s6.ckpolicy` path row from PR #86 (the pending bookkeeping
restart — one restart covers both). Startup verification: the log
should show two `policy artifact validated` lines whose hashes match
the two README rows.

## Why these exact shapes (don't re-derive)

- **Seat = Kittybear, not Pumpkin**: pre-registered decision rule
  (prereg deviation 2026-07-31e) — B held the higher Nash delta;
  descriptively it also retires the world's loudest scripted meower
  and s3 uses the channel more from that seat.
- **Greedy selection**: s3's certification ran greedy; the seating
  must match the certified condition (same rule as s6).
- **Expect a chattier, quieter-scripted world**: s3 emits FollowMe
  meows beside s6 (F-012 — latent channel use, unmasked by policy
  company; ~7–16 per 20k ticks). This is measured, expected behavior,
  not an anomaly. Watch criteria for the new seating: distress cues
  (none in 20/20 screen runs), happiness bands (Miso ~94.9, Biscuit
  ~80.4, Pumpkin ~90.3, Kittybear ~94.6). Abort = revert the seating
  commit + restart (Kittybear falls back to needs_driven).

## Carried asks (non-blocking, from earlier rounds)

- Close issues #79 / #82 / #84 (specs 022/023 shipped).
- Confirm the client purr-render check from the batch handoff was
  done (spontaneous purrs rumble without announcing — the animation
  must key on phase state, not announcements).

Delete this file once consumed.
