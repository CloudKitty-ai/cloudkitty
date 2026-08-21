# exp-006a: Biscuit 2.0, the corner shot — preregistration (DRAFT,
# freezes on the owner's word)

**Scope**: minimal follow-on to exp-006, targeted solely at producing
a seatable Biscuit 2.0. Everything not stated here is INHERITED from
the frozen exp-006 prereg and its D-notes (`../exp-006-character-gen/
prereg.md`) — corpus, clone-anchor init, critic6, train_ppo6 recipe
verbatim, fingerprint instrument and bands, G3 floors (the character
definition is unchanged), cert_harness6, the certification world
(`configs/phase1-cutover.toml`, sha `64ca2b9a…`, D-003), and its
fresh scripted anchor conventions. Where this doc and exp-006
disagree, this doc wins for 006a only.

Owner rulings incorporated (2026-08-21, her words quoted where they
are the decision): the G2d bar ("if we can keep biscuit and get a
~10 point welfare uplift, that seems like enough of a win. the issue
with [thermostat parity] is the welfare target will change when we
implement bugs 2.0"); composition solo-s3 + E1-s1; arms "fine dose +
duet-arm + one more L-04 seed so we're maximizing our training
concurrency"; family-11 r5 as report-only benchmark.

## 1. Hypothesis

The efficient-venue corner — near/bug at their G3 floors, duets
elevated, welfare recovered — is reachable by this recipe, either by
dose (it is plausibly bracketed between L-04's β∞ 0.04 and L-05's
0.05: L-04 undershot duets, L-05 overshot venue) or by a small
partnered-play shaping signal at the L-04 dose. Prior grounding:
l-scan-biscuit-2026-08-20.md, body-price-2026-08-21.md (the exchange
line), chase-census-2026-08-21.md (partnered play relieves at twice
the solo/critter rate — the corner is the welfare-efficient
character).

## 2. Arms (one wave, 4 concurrent, ~15 h)

| arm | β∞ | seeds | delta from L-04 recipe |
|---|---|---|---|
| F-dose | 0.045 | s1, s2 | dose only |
| F-duet | 0.04 | s1 | + partnered-play start bonus (§3) |
| L-04 | 0.04 | s3 | none (lottery sample; spread ~2.2 at the seat) |

Init and leash anchor: clone-anchor (as all L arms). Run indices
8–11 in exp-006's claimed PPO band (episode seed base 100M +
run_index×20M, run order F-dose-s1, F-dose-s2, F-duet-s1, L-04-s3;
inside exp-006's 100M–260M claim — no new SEED-BANDS row needed).
Torch/numpy seeds 20260818 + run_index. Stop rules inherited.

## 3. The duet-shaping term (F-duet only)

r_shape = λ per tick at which the subject TRANSITIONS INTO partnered
play (a play activity start with a kitty partner; initiator vs
joiner not distinguished — the state surface cannot attribute
initiation, and the behavior sought is the same). λ = 0.1, sized so
shaping totals ~1% of episode return at anchor duet rates and
~3% at L-05-like rates — self-limiting. No penalties anywhere (the
imitability principle). Grind guard, report-only during training:
per-update partnered-play-start rate; a sustained rate above 3× the
scripted anchor's flags the arm in telemetry (G3's near/bug floors
remain the binding character gate — a duet-spammer that sheds venue
fails G3 like L-05 did). Detected purely from the state stream in
the trainer env wrapper; no engine change.

## 4. Candidate selection (before any battery leg)

Fingerprint every finished arm (instrument and floors unchanged).
G3 pass/fail adjudicates character exactly as in exp-006. The
fingerprint subj-happiness column is TRIAGE ONLY (it rank-predicted
exp-006's cert readings 4/4): battery order runs best-subj-hap
G3-passer first; it gates nothing. If no arm passes G3, the
experiment reports out with no battery (stop; no gate-shopping).

## 5. Certification composition (the 006a seating under test)

Miso = attn-a1-s1-o4 · Biscuit = **the 006a candidate** · Pumpkin =
attn-a1-s3-o4 (solo — no twin pair, F-027) · Kittybear =
**ppo-E1-s1 stripped actor** · Clementine = e004-a1-s2-o4.
E1-s1 is certified BY this battery as part of the composition (it
carries report-only validation from 2026-08-20/21 only). Reference
composition for G2c/G2d comparators: unchanged from exp-006 (four
expanded incumbents at §6 seats + scripted Clementine), freshly run
same-instrument, paired seeds.

## 6. Gates

- **G1** zero fallbacks — inherited.
- **G2a** stress: certification-world shapes iii and r3 GATED with
  exp-006's frozen arithmetic (bar 225, max(1, floor(0.05n))
  exceedances, constitutional mda ≤ 150, floor 0). **family-11 r5
  runs as the named tail benchmark, REPORT-ONLY** (owner ruling; its
  deadlock class is structurally absent from this twin-free roster,
  and its constitutional line prices 26×26 travel, not policy
  health — see the 159 travel streak in the solo-s3 cell).
- **G2b** team ≥ the fresh scripted anchor, re-derived on the
  certification config at battery time (D-003 discipline: the sha
  is CHECKED against the intended world, not just stamped).
- **G2c** candidate-roster team ≥ reference composition − 0.005.
- **G2d** per-seat, paired, G3-coupled:
  - **Biscuit (the owner's uplift bar — 006a-LOCAL, not a standing
    formula)**: candidate ≥ the playful-behavior scripted anchor at
    the Biscuit seat, freshly derived at battery time on the
    certification config, **+ 10.0 happiness**. Today that anchor
    reads 79.72 → bar ≈ 89.7, deliberately just under thermostat
    parity (90.64). Valid only with the candidate's G3 pass.

    **Scope ruling (owner, 2026-08-21, verbatim)**: "+10 happiness
    makes sense NOW, but we need to see what bug 2.0 does to biscuit
    before we commit (it could end up putting biscuit+10 above
    scripted). We still don't know what the theoretical welfare
    ceiling for a 'still biscuit biscuit' is, so I want to be
    cautious about setting a bar so high that our only viable
    personality is welfare optimized to the point that individual
    character is minimal (if that's where we end up after more
    testing then so be it, but I don't think we're there yet)."
    Operationalized: (a) the +10 does NOT auto-carry across world
    changes — at bugs 2.0 (or any re-priced world) the Biscuit bar
    is RE-DECIDED by the owner with fresh anchors in hand, never
    inherited as a formula; (b) standing cap pending that decision:
    no future Biscuit bar sits above the same world's thermostat
    (needs_driven) parity reading; (c) standing design principle:
    the welfare bar must never be positioned such that only
    minimal-character minds can pass — G3 protects character from
    the welfare gate as much as the reverse, and if testing ever
    shows the two cannot coexist, that conclusion is the owner's to
    draw explicitly, not a gate's to impose silently.
  - Carried seats (Miso, Pumpkin) and Kittybear (E1-s1): ≥ their
    reference-composition readings − 0.006. (E1-s1's comparator is
    s3-at-Kittybear in the reference composition — the seat's
    incumbent-equivalent; E1-s1 read +0.15 above it in the
    report-only cells.)
  - Clementine: ≥ scripted needs_driven at her seat − 0.006.
- **G5/G6**: census + soak inherited unchanged, at seating time.

Bands: eval 870001–030, stress 880001–030, 30 × 20k, greedy — the
battery convention bands, declared here before any leg. Stop rule:
any gate failure → stop, no gate-shopping, report out.

## 7. What deliberately stays out of scope

The bugs-2.0 mechanics decision (tether/ttl — Product's spec lane;
sequencing per the 2026-08-21 review: mechanics → re-baseline →
corpus re-collection → NEXT generation, never this one); any G3
floor movement; any change to the certification world; the exp-006
r5 fork (superseded for this roster by the twin-free composition +
report-only ruling, but the F-027 record and tail benchmark stand).

## Deviations

(append-only after freeze)
