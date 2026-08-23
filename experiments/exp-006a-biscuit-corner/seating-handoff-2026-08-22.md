# Biscuit 2.0 seating handoff (owner's word 2026-08-22)

The owner has given the seating word for ppo-L-04-s3. This is the
Experiments→Product handshake package for the cutover PR, mirroring
the e006-E1-s1 procedure.

## The artifact

`exp-006-character-gen/handoff/e006a-L-04-s3.ckpolicy` — 313,931
bytes, sha256
`a32c457e247e19cc894c05cb876daa79cd6a7f2425bafe74b1fcd5bbe9497558`.
make_oracle_v4 dump of the battery-measured torch actor
(`artifacts/ppo-L-04-s3/policy-final.pt`, strict-loaded plain V4).
Forward parity: max logit delta **2.29e-05** over 2,000 real
certification-world Biscuit obs rows (seed 870001, the certified
composition driving), exact argmax agreement on both heads; a
bit-flipped-byte negative control diverges at 7.2e-02, so the parity
check is non-vacuous. Product copies the file byte-identical into
`policies/`.

## Roster change (TWO seats move)

| seat | now serving | after cutover |
|---|---|---|
| Biscuit | e004-a1-s2-o4 | **e006a-L-04-s3** (Biscuit 2.0) |
| Clementine | scripted | **e004-a1-s2-o4** (its BC lineage's incumbent) |

Miso (attn-a1-s1-o4), Pumpkin (attn-a1-s3-o4, solo), Kittybear
(e006-E1-s1) unchanged. This is exactly the composition the battery
certified — both moved seats carry battery readings (Biscuit 89.95
vs bar 87.31; Clementine-e004 94.81 vs scripted bar 90.10). Greedy
selection everywhere, as served today.

## Registry facts for the policies/README.md row (Product authors)

- Provenance: exp-006a lineage PPO product — clone-anchor-v6
  init/leash (β∞ 0.04, run_index 11, seed base 320M), dataset v6
  (anchor-playful-v6 ∪ far-spawn), trained on family-spread-bugs2.
- Character: G3 fingerprint PASS (play 0.91×, near 0.77×, bug
  0.73×, duets 1.01× — `exp-006a-biscuit-corner/
  fingerprints-2026-08-22.md`).
- Certification: `exp-006a-biscuit-corner/battery-2026-08-22.md`,
  ALL GATES (owner's Biscuit bar 87.31 per frozen prereg 9a329e9).
- e004-a1-s2-o4's row updates its service line (Biscuit →
  Clementine, same battery).

## Cutover PR checks (who owns what)

- Product: config kitty-block changes against the CERTIFICATION
  config's blocks (not any stale copy), registry rows same-PR,
  artifact copy.
- Experiments (pre-merge, on the PR's bytes): sha match + a re-run
  of the export-parity check against the shipped file.
- Deploy: owner-gated as always. NOTE — unlike the phase-1 cutover
  this needs **no --fresh**: it is a seat swap on the served world
  (precedent: the bugs-2.0 deploy continued the world across the
  restart). Her call regardless.
- Post-deploy (Experiments): G5 census on the new roster, G6 soak
  watch, watchdog already live. The live-play census question
  (sticker freeze) gets its first genuine learner datum from
  Biscuit 2.0 on the served world.
