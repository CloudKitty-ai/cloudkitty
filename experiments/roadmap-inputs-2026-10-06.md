# 1.3 + register-versioning input set — owner walkthrough, 2026-10-05/06

Companion to `roadmap-inputs-2026-10-05.md`. Two Professor-session
packages (relayed 2026-10-05 on her word) were confirmed item by
item in the Experiments session, with carve-outs and additions of
her own. Source records in the Professor lane:
`~/ai/professor/notes/online-rl-ideation-2026-10-05.md` and
`~/ai/professor/notes/register-versioning-2026-10-05.md`. Nothing
below starts work now; the 2026-10-04 ruled order is unmoved.

## 1) The 1.3 package core — confirmed with one carve-out

Confirmed: online RL at 1.3 with dynamic lab-world elements
(weather/rain, seasons, bug migrations, transient birds); her
relayed words "There are no survival risks in the world ('Kitties
cannot die' is in the constitution), so it can impact
welfare/happiness, but never survival"; warmth at the "bottom of
the pyramid" with eat/drink/sleep; birds "pests and
high value play targets, not food or targets of violence" — no
killing; all shippable; two published worlds (meadow = simple
abundance, lab = dynamic, challenging) with a world selector in
the client. "Year-round" on warmth is Professor's gloss on her
placement ruling.

Carve-out, her words: "I'd say catch=start+fly off+respawn might
be prematurely engineered, particularly the respawn part (e. g.
the bird could fly a couple of spaces off). We can explore that
when we get there." [sic: "start" = startle] The catch mechanic is unspecified until 1.3
design; the no-killing/play-target framing stands.

## 2) Warmth baked into Gen 3 summer-locked — ruled in, two riders

Her words: "Ok, let's include it and flag those gotchas for our
gen 3 design." Riders (the flagged gotchas): (a) inertness is
PROVEN in the Gen 3 prereg, not assumed — the summer-locked
warmth term is constant at max, so its gradient contribution is
provably zero, and that check is declared; (b) only the stable
skeleton is baked (obs dim, welfare component with satiated
default, declared base weight) — yield-map NUMBERS stay
config-side for 1.3 to tune.

W3 weight sketch, her words: "I'd particularly like to be mindful
about the updated need happiness weights and ideally only need to
update them once. Current design thought: set lower tier needs to
a lower weight to better incentivize the higher tier behaviors
once they reach satiation. E. G. Base needs: 10%x4=40%
Cuddle/bath: 17.5%x2=35% Play: 25% Obviously subject to testing"
— i.e. tier budgets 40/35/25 with equal split within tier
(layout (b) below), warmth inside the 4-need base tier at parity.
Banked as the W3 starting point; calibrated against the prereg'd
behavioral criteria before W3 is declared, then frozen.

## 3) Reserved Gen 3 obs dims — ruled

Her words: "Yes, two unnamed spares, all proven inert." Reserved:
season phase, weather, and two unnamed spares — four dims, each
proven inert the e_col way (zero-init additive, not plain
padding; the F-058 check-1 lesson). NO named bird dim: she reads
birds as world entities — her words: "I was thinking birds would
be a separate element rather than just a "presence" dim" —
and Experiments' reading is that birds would likely ride the
existing critter/entity channels — deliberately left open:
whether they fit is a 1.3 design question the spares hedge.

## 4) Register/welfare versioning — confirmed with two amendments

Her words: "Confirm with amendments." The relayed scheme as ruled
in the Professor session ("agreed on all of these"): namespaces
schema vN / welfare Wk / register Rm / eval vN, never
"generation"; WELFARE.md ledger beside FINDINGS.md (retro-labels
W1 = pre-2026-07-27 weights, W2 = current; the unmarked 07-27
rebalance eat/drink .25->.20, cuddle/bath .10->.15 is the
motivating failure); one frozen shared metrics module per
register version (`register/Rm/`), R1 = current cert-harness
lineage; obs via schema-keyed column maps, never raw indices;
every metric declares its currency, "lived" (clamped, Article I
floor) vs "signal" (unclamped); bridge rule — every Wk bump
dual-scores the same rollouts under old and new, no undeclared
cross-W comparison; per-tick need-vector logging on paper-cited
cells and bridge reads; CI hashes the welfare-relevant config
subset against the ledger, unknown hash fails; one Wk across all
served worlds at a time; experimental reward variants are
treatments, never ledger rows; empirical constants pinned with
provenance inside the register version; new needs evaluate at
their satiated value over old data.

Amendments (hers, on Experiments' recommendation):

- The FINDINGS welfare column is FORWARD-ONLY from F-060; the
  ledger carries a date-range -> Wk map for older entries. No
  retroactive index edits.
- Each Rm pins the schema versions it supports; the column map it
  uses is versioned with it. "Frozen like evals/vN" alone leaves
  a frozen register importing a live map.

Implementation cautions noted with the confirmation: the CI
config hash is computed from the parsed canonical form (sorted
keys, normalized floats), not file bytes; the satiated-value
convention biases old-data Wk scores UPWARD, and the ledger row
states that direction.

## 5) Gen 3 gates/calibration/floor — confirmed

Her word: "Confirm." Hierarchy lives in the gates, not static
weights (flat-weight twin is the control for exactly this);
within-tier equal split from DECLARED tier budgets (layout (b));
(theta, temp) calibrated by small grid against prereg'd
behavioral criteria (below-threshold reallocation >= X%;
abundance recovery of play/cuddle within Y of ungated baseline;
no thrashing at tier boundaries, measured as action-switch rate
near threshold) — never against measured welfare, never "until
the hierarchy emerges"; theta bounded below by the ruled
thresholds-above-distress-band; probes 1–2 seeds, >=3 only for
paper-cited cells; renormalized gated weights carry a TERM_FLOOR
so no need's effective weight reaches zero.

## 6) Two worlds, one model set — working direction

Her words: "Confirm as working direction, open to reconsideration
if there'a a compelling reason" [sic]. One set of models covers
both published worlds (the relayed transfer story: meadow
in-distribution, lab novel); capacity headroom acknowledged if
lab complexity binds.
Closes the shared-vs-per-world flag.

## 7) CTDE declaration for Gen 2 — confirmed

Her word: "Confirmed." The Gen 2 prereg and the paper's methods
declare all THREE training-time global channels: the centralized
critic sees global state including hidden needs; the reward is a
global welfare aggregate (constitutionally global — perfect
information hygiene is impossible); actor weights are shared
across seats (verified in the trainer: one `PolicyV5AddE` batched
over `MAX_SEATS`, one critic). The ToM-flavored claim is scoped
to the DEPLOYED policy — actors' execution inputs are local only,
evidenced by execution-time evals. A critic-blind arm stays a
priced option (one training cell x >=3 seeds if paper-cited),
decidable at a prereg sitting. The self-simulation reading
(shared weights see both sides of a need — own visible, other's
hidden — so inference-by-inversion is testable) is recorded as
HYPOTHESIS-grade framing, not a claim.

## 8) Scripted-critter welfare standing — covered by existing rule

Her words: "Agreed on both." Birds as designed are scripted
automata: props under the 2026-09-26 ruling (covered = shaped by
experience; scripted exempt) — no new doctrine. Corollary to be
recorded at the 1.3 design: any critter that becomes a TRAINED
policy crosses into covered at that moment, welfare machinery
applies before it trains.

## 9) Professor's framing line — declined on a register check

Her words: "Decline and relay, thanks." The offered line ("the
kitty rests when enriched. The dog that didn't bark was the
behaviour.") fails its first half: PREREG-L step 1 fired on NO
tending kind (drink closest, 10/10 sign-consistent but pooled
0.0119 under the 0.0356 bar), so "rests when enriched" is not a
gated claim; the supported form is "plays less when enriched."
The second half fits the ruled paper-1 wording (negative control
against ELEVATED play). Correction relayed to Professor
2026-10-06.
