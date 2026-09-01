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

## Follow-up (same day): the collateral elevation, and boxing ruled out

Owner observed live that Clementine's eat/drink/play also ran high
(~30), then that the pattern cleared and "she was not stuck"; asked
whether a 4-cat box explains it. Checked both mechanisms on the
repro server (positions + needs, 200 samples over ~300k ticks;
raw `boxing.json` in the session scratchpad):

- **Boxing is real but rare and weak.** Kitty moves are 4-way and a
  kitty-occupied destination is illegal (`action.rs:368`), so a full
  box is possible — but it occurred in 5/200 samples, and blocked≥2
  vs blocked=0 moves her needs only modestly (eat 32.0 vs 26.4).
  Not the driver; matches the owner's "not stuck" observation.
- **The driver is the high-cuddle regime itself.** Split by her own
  cuddle level: eat 18.1 → 35.5, drink 11.9 → 34.2, play 14.2 →
  45.1 (cuddle <30 vs >60). Her artifact trained under an economy
  where cuddle idled near 5 and never saw 60–100; with that input
  far out of distribution her WHOLE servicing degrades — the
  "mind broken, not world harder" side of the separator. Since her
  cuddle sits high most of the time (mean 57), this is her steady
  state, not an excursion.
- **The mild roster-wide elevation is a different, benign thing**:
  seats that CAN rest now spend real turns resting (33–43
  scenes/ring each — a new time sink 041 introduced), so everyone's
  other needs ride somewhat higher than the pre-041 census. Miso
  shows the shape mildly and stays content/purring.

Consequence for the options above: the trait dial and the cosleep
reprice both work by keeping Clementine's cuddle OUT of the OOD
region — they fix the collateral degradation too, not just the
cuddle number. Accept-until-retrain means accepting a seat whose
policy is degraded most of the time, not merely one high need.
