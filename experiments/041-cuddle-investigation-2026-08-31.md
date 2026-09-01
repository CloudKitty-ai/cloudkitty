# Post-041 cuddle climb — investigation (2026-08-31)

Client report during the 041 deploy window: roster cuddle climbing
(22.5 → 30.8 → 34.0; mean unmet 12.6 → 18.8), "the world isn't
settling." Investigated on a headless local server at the owner's
word: the exact served composition (cloudkitty.toml @ a12853b, all
five policy artifacts), fresh world, tick_ms 1, ~237k ticks sampled
every ~2k. Raw: `attn-cert-2026-08-14/results-raw/`
`041-cuddle-repro-samples-2026-08-31.json` (uncommitted).

## Verdict: not a runaway — but not benign either

1. **The roster mean settles into a high band, ~25 ± 8** (samples
   ran 17–35), versus the pre-041 census mean of 5.1. The client's
   climb is the transition into this band, and it tops out.
2. **The per-seat tail is a real welfare regression.** Clementine's
   cuddle: mean **57**, saturated ≥ 90 in 10/53 samples, full range
   0.7–100.0. The spec-040 watchdog went **alarm-live in 7/53
   samples** (threshold 150 on distress-age; entries always
   Clementine/cuddle). On the live box the watchdog will fire
   intermittently — **the G6 soak as gated will fail**.
3. The other four seats sit at mean 20.3 with occasional spikes
   (max 92.7) — elevated but self-recovering.

## Mechanism (confirmed in the event ring)

The pre-declaration ("zero incumbent rest scenes EXPECTED") was
wrong in the happy direction for four seats: kitties 1–4 initiate
rest routinely (33–43 scenes each per 1000-event ring — frozen
policies DID select rest on untrained weights). **Clementine
(e004-a1-s2-o4, the oldest MLP artifact) initiates rest exactly
never** — zero scenes in the ring.

Her arithmetic post-041: cuddle rises 0.7/tick (the "cuddlier"
3-dial trait — not to be confused with Miso's spec-035 persona name
"the cuddler", which carries no cuddle-rise override),
and the only channel faster than that is `rest_mutual_relief` 8.0 —
which she receives only PASSIVELY, when another cat rests beside her
(she is the roster's most popular rest partner: 35 of the ring's
partnered rests anchor on her). Everything she can earn actively —
being groomed (0.5), cosleep (0.6 + 0.25) — is at or barely above
her rise. So she cycles: climb at ~0.7/tick toward saturation →
distress-age accrues toward the 150 alarm → a neighbor happens to
rest beside her → full drain → repeat. Pre-041 any groom scene
drained her at 8.0/tick; 041's reprice (groom_cuddle_relief 8.0 →
0.5) removed her lifeline knowingly, on the assumption rest would
carry the need — true for seats that rest, false for the one seat
that never does, and she is also the seat with the highest rise.

## Options (owner's call; not applied)

- **Trait dial**: Clementine's cuddle rise 0.7 is stage-3 mortal (a
  pin, not a forever number). Dropping it toward ~0.4 makes her
  passive channels sufficient. Smallest change, config-only, but
  softens the designed "cuddler" character.
- **Economy dial**: raise `cosleep_mutual_relief` (0.6 → ~1.5–2) on
  the serving config — she cosleeps as partner often (22 of the
  ring's partnered sleeps). Keeps her character, touches everyone's
  economy; needflow can price it in minutes.
- **Accept until the Gen-1 retrain** (fog seats train under 041 and
  will rest properly) — means weeks of intermittent watchdog alarms
  and a soak gate that cannot pass as written.
- Any combination goes out as its own small config deploy; none of
  this touches the contagion sequencing.

Caveat: fresh world, not the box's resumed snapshot — same engine,
config, and artifacts; the equilibrium behavior is the claim, exact
tick numbers are not.
