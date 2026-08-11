# Changelog

CloudKitty is a living world first and a software project second, so this
changelog tracks something ordinary changelogs don't have to: the world
itself. Each release entry opens with what the release *means*, then walks
the arcs of work that made it up. Pull requests are cited as references —
the story should read without them.

Because changes here can invalidate things that outlive the code — saved
worlds, trained policy artifacts, measured baselines — entries carry
**compatibility markers** where they apply:

- **`[obs-schema]`** — the observation layout policies are trained against
  changed; existing `.ckpolicy` artifacts refuse to load on the new engine.
- **`[world-fresh]`** — the world fingerprint (size, seed, roster) changed;
  a saved world cannot resume and a redeploy needs `update.sh --fresh`.
- **`[rng-sequence]`** — the order of random draws changed; every seeded
  world regenerates differently even at the same seed.
- **`[stamp]`** — the engine-defaults hash (`engine_defaults_sha256`)
  moved; measurements pinned to the old stamp are history, and baselines
  re-derive on the new engine before anything is compared against them.

The absence of a marker is a claim too: several of the largest changes
below were engineered specifically to move *none* of these, and proving
that (byte-identical outputs, unchanged stamps) was most of the work.

What was *learned* in the experiments lives in
[`experiments/FINDINGS.md`](experiments/FINDINGS.md); this file records
what *shipped*. Findings are cited by number (F-###) where they drove a
change.

---

## Unreleased

- Spec 03: the meadow grows in drifts — one low-frequency fertility
  field gates all three ground scatters, so grass, flowers and shrubs
  thicken together and the meadow has *places*, not texture; the
  density normaliser is bisected per field against the realised count
  (world-size dependent — a baked constant is right for exactly one
  world, and normalising to the nominal rate had silently cut shrubs
  38%); a second shrub species with a mix dial, ground shading that
  knows where the sun is, and the spec-03 dials in the lab (#189).
- Crossfade fix: shrubs and flowers went black mid-phase — `shadeHex`
  parses only hex while the phase mixer emits `rgb()`; the five things
  spec 03 shades now go through `mixPaletteColor`, which parses both.
  Forty-odd meadow checks all drew at blend 0; the new one draws the
  crossfade (#191).
- Three hygiene fixes: card text keeps contrast through a phase change
  (`--card`/`--ink` both invert and met at 1.17:1 mid-crossfade; they
  now swap at the halfway mark on their own 0.18s transition — the v3
  plan's ask, finally landed on the DOM side); a backgrounded tab's
  socket is latest-wins, so a two-hour backlog can no longer replay
  ~9,000 renders through the DOM; flower lower petals shade toward the
  heart, not toward grey (#193).
- Catch-up keeps a buffer: strict latest-wins (from #193) dropped
  ordinary ticks whenever a frame outlasted the 800ms tick, lurching a
  cat two tiles in one tick's ease — up to 4 pending states now replay
  in order, and only a genuine backlog collapses, bumping the
  generation so the world snaps across the gap like the reconnect path
  already did (#194).
- Docs: rl-training + howto-rl caught up to spec 028 (two-head wire,
  20×20, certification assumptions rewritten — the channel is
  restrained by law, not economics), and kitty-eval is a pre-seating
  smoke, not the bar: certification is the §9-harness pipeline,
  written down in `experiments/PIPELINE.md`; every doc number re-run
  for real (#190).
- Spec 028 FR-021 amended — the acceptance check evaluates within
  behavior class where demonstrator composition differs (the v4
  composition artifact), echo sites tagged; py-binding width accessors
  became properties and two stale comments were corrected (#192).

---

## v2.7.1 — 2026-08-10 — the cat becomes an animal

No compatibility markers: everything here draws pixels or records
measurements. The engine, the world, and the stamp are exactly v2.7's.

A client-only patch release — the animation handover from Design, applied
in five rounds (#182–#187), plus the first experiment records taken from
the all-policy world v2.7 seated.

### The rig (#182)

The idea the whole arc hangs on: **a pose is a position; an animal is
mostly the lag between positions** — the tail that hasn't caught up, the
head that led the turn, the ears that arrived late. None of that can live
in a pose, so a new layer (the rig) sits after the pose and after any
blend, and offsets it, springing to zero so a cat at rest is exactly the
un-rigged cat. The handoff landed as a verbatim drop (`73bc715`) with
every change on top reviewable as one range. With it: a walk that works
on every axis — closing the north/south foot-slide finding by
foreshortening, not the piston that was costed — the full pounce beat,
the hunting face, and a dial pass that baked the owner's judged values
(pounce hold/launch/land, wiggle, tread depth per context, focusLidTilt).
Biscuit got green eyes. The tail tip renders at 2.55px on a 31px cat —
the first cat-art feature to clear the sub-pixel wall.

### Four rounds of making it true

- **The hunter's face was unreachable (#183).** Found by review after
  the merge: `expressionFor` compared a quarry that arrives as an object
  (`{target: 'kitty', id}`) against the string `'element'`, so the
  headline visual of #182 had never once appeared in the live world.
- **Card portraits got an idle life (#184).** One weighted beat table,
  one beat at a time, priced *in* like the map's motion table — a
  portrait now draws nothing 79.8% of the time, and a sit, stretch,
  pounce, yawn, or ear-flick the rest.
- **The world's wake-stretch left the portraits (#185).** Owner spotted
  it by eye against the census; the census was measuring only what the
  client *schedules*. Live cats nap in exactly-5-tick bouts and wake
  every ~21s, and every wake fired an unscheduled stretch that
  out-drew the entire beat table. Portraits now ignore it; the map
  keeps it.
- **Water became a place, not a timer (#186); north and south became
  real drawings (#187).** Submersion by location, one shared surface
  line with a guarded meniscus, far-side legs, axial facings with a
  muzzle on the face. Both rounds ported by three-way merge against the
  previous drop (zero conflicts), because the bundle's `client/` forked
  before #182 — a straight application would have reverted rounds 1–3
  and every pasted dial. #187 also caught that `cat-v2.js` installs its
  namespace by name on the real page and only four symbols were being
  installed — the whole feature would have shipped inert.

### Records, no code shipped

- First measurements off the all-policy world: **the policies invented a
  contact call**. A cat drifts away from the pack, purrs at the far
  point of the excursion, and turns back — an "I'm fine, out here,"
  not a cuddle invitation — and the purring is deliberate: selective
  (the head declines ~24 of every 25 legal chances), answered, and
  load-bearing (erasing the purr digest slot changes downstream
  decisions; zeroing a null slot doesn't). Records in
  `experiments/exp-004-meow-channel/results/` (purr-deliberateness +
  purr-semantics, 2026-08-10); the contact-census tool grew the
  instruments.
- Portrait gaze tabled for its own sitting; the ear twitch stays
  (BACKLOG).
- The exp-004 policy pipeline written down as standing doctrine
  (`experiments/PIPELINE.md`).

---

## v2.7 — 2026-08-09 — the meow channel, and the world goes all-policy

`[obs-schema 2→3]` `[rng-sequence]` `[stamp]` — deliberately **not**
`[world-fresh]`

The generation-3 release, and the shortest span between tags for the
largest change of state. Its meaning in one line: **every decision is now
a pair — an activity, and a message riding along for free — and for the
first time every seat in the served world runs a learned policy.** Rolled
out 2026-08-09 via a plain `update.sh`: no `--fresh`, because the schema
break is policy-side only — the live world *resumed*, history intact,
soak clock past 215,000 ticks, with cosleeping visible in the first
snapshot.

### The Meow Channel (spec 028)

One wall crossed on purpose. `Action::Meow` retired by the Purr precedent
(parses, validates to Idle); announcing stopped costing the turn. Menu
40 → 34; message head 9 (Silent + 8 want-kinds — WantBath and WantSleep
join); observation 183 → 197 (digest v3: one coherent freshest audible
emitter, with the engine-stamped intensity); mask wire 43 = 34 ∥ 9;
artifact v2 (one trunk, two heads, one split RNG draw when sampling).
New `engine_defaults_sha256`:
`412d00e2a92e4f5a3a4f4e72caa8f0266b18455e331ed41aef3044f05e749c87`
(recorded, not triaged — baselines re-derive on this engine). Pre-028
world snapshots load and run; the committed fixture is the proof (#163).

- Message legality is engine law: a want-kind needs its need armed
  (announce_threshold 30 / hysteresis 5, updated beside distress) and
  its per-kind cooldown clear (= recent_window_ticks); Silent is never
  masked, structurally. The `[meow]` courtesy trio retired loudly;
  the sweep gained the pinned-generation exclusion manifest
  (`config-sweep-exclusions.txt`, decided with Experiments).
- Scripted cats are demonstrators now: deterministic announce (the
  lotteries died), a groom-response rung keyed on the audible
  `WantBath` alone (imitability — GroomKitty went from 0-in-800k to
  occurring by construction), cosleep routed to a friend's side when
  cuddle is real (`cuddle_real_threshold` 15), and cosleep priced by
  presence (`cosleep_drip_relief`/`cosleep_mutual_relief`, 15/15
  behavior-preserving until the pilot re-prices them).
- The distress-tick census rides every welfare report (instrument
  convention verbatim; reported, never gated).
- The batch briefly re-parked the policy seats to scripted across the
  generation gap (e003 artifacts speak action schema 1) — a parking
  that lasted exactly as long as it took a generation-3 artifact to
  certify (below).

### The first certified seating — then all four seats

exp-004 ran its preregistered arc end to end: freeze (#170), dataset v4
(#171), behavior cloning (#172), the PPO grid (#173), and the verdict
(#174) — **e004-a1-s2**, the shaping arm's seed-2 winner: 15/15 on the
settled §9.2 gate, §9.3 welfare +0.0440 over the paired baseline, zero
fallbacks under stress. The artifact landed with its certification
record (#175).

It took Miso's and Kittybear's seats first (#176) — the first certified
generation-3 seating, retiring e003-m0-g998-s3 to `policies/retired/`;
the seats-a-policy release test returned for its second tour,
superseding the generation-gap test per its own instruction. The
remaining two seats followed the same day (#178), on the 4x deployment
screen: 30 fresh seeds at 0.9499 reserved-band welfare vs the live 2+2
composition's 0.8866 — the scripted seats were the live-welfare cap —
with §9.1 water bounds PASS at the all-policy composition. Biscuit's
playful era ends; Pumpkin keeps the snacky needs override (world-law,
not behavior).

### The client: phase-4 cats, deeper ponds, the new vocabulary

The cat learned to move like a body instead of a sprite: legs pivot
inside the silhouette and the gait rides distance, not the tick clock
(#137); the pounce launches instead of switching (#152), and a chase
only draws it once the quarry is within four tiles (#157); body:head
proportion became a judged dial (#148); every soft cat got a belly
(#158); the sleep-curl head joined the head-radius band every waking
pose already kept (#180). The pond gained depth — palette, dials, and
the blur ceiling (#177), plus the lost `groupWaterTiles` call restored
(#179) — and the wading cat stopped making its own ripples (#159). The
client also learned spec 028's language: `MEOW_TEXT` gained want_bath
and want_sleep (#162).

### Housekeeping

- The changelog itself (#135): the whole story, v1.0 to v2.6, told for
  a reader — with the compatibility-marker convention this entry uses.
- exp-004 design inputs committed (#134): working notes toward making
  the meow carry more signal — explicitly inputs, not yet a design.
- Findings register housekeeping: archived findings split out, F-017
  registered (the multi-copy training collapse is largely a symmetry
  artifact), and exp-003's record corrected from a verification sweep.
- Operational, post-v2.6: the 20×20 world went live 2026-08-08 via
  `update.sh --fresh` — the first world of the canonical generation,
  and the world this release *resumed* rather than replaced.
- Refactor, no markers: `[rl]` config defaults collapsed to
  container-level serde defaults and eleven dead accessors deleted
  across core and rl — behavior-identical, stamp verified unchanged;
  also corrects `policies/README.md`'s pre-#114 claim that unknown
  `[rl.policy.*]` keys are silently inert (they refuse to load) (#142).

---

## v2.6 — 2026-08-07 — exp-003 shipped, the world remade, client v3

`[obs-schema 1→2]` `[world-fresh]` `[rng-sequence]` `[stamp]`

The biggest span in the project's history (PRs #87–#131, three weeks of
work across four parallel threads). Its meaning in one line: **learned
policies now hold both policy seats in the served world, and the world was
rebuilt around what training taught us it needed.** Rolled out to the live
site 2026-08-08 via `update.sh --fresh` — the old world's history closed,
and the soak clock restarted on a canonically generated 20×20 world.

### The roster becomes two-policy

Kittybear took seat s3 (#87), joining Miso (s6, seated in v2.5) — two
learned policies alongside scripted Biscuit and Pumpkin. From here on,
"the deployed composition" means this mix, and evaluation had to learn to
construct it (neither `--roster` flag did).

### The wet-fur batch (specs 024, 025)

Water gained a cost: standing on a water tile now charges a wet-fur
mechanic that raises the Bath need (spec 024, #90), and play relief was
split so playing in water stopped double-paying (spec 025, #93). The
client learned to show it — a swim gait for kitties crossing water (#92).
One counterintuitive result came out of tuning this: raising the wet-fur
*gain* — the dial that prices water — actually **increases** scripted
kitties' time on water, because a wet cat wants a bath and grooms where it
stands (F-016). The ceiling, not the gain, is the lever.

### exp-002 → exp-003: the observation was the bottleneck, not the reward

exp-002 (mixed-population training) closed with its central negative
result intact: training a policy against copies of itself collapses, and
it collapses monotonically with the mix — a self-interaction failure, not
a data-volume one (later refined by F-017: largely a symmetry artifact).
Its successor asked a sharper question: is the policy's water problem a
*reward* problem or a *perception* problem?

exp-003 answered it. **One observation bit — "am I in water" (spec 026,
#106) — bought what no reward dial could**: the winning candidate,
`e003-m0-g998-s3`, ended up *drier than the scripted baseline*
(2.79% in-water vs 3.44%; 0.62% lounging vs 1.50%). The preregistration
was frozen before results (#115), with water bounds defined as multiples
of a same-engine scripted baseline rather than absolutes — a construction
that twice saved a better world from being blocked by an absolute
threshold. The winner was deployed to **both** policy seats (#118).

The schema bump is the release's sharpest edge: `[obs-schema 1→2]`
stranded every schema-1 policy artifact (they exit rather than
misbehave), which is why the deploy path grew `--client-only` (below) and
why the old anchors were retired rather than re-measured.

### The worldgen batch (spec 027) and the 20×20 world

Worldgen learned placement opinions (#107): a **conditional lake** —
worlds whose water minimum allows it get a guaranteed 2×2 water square,
and resumed worlds grow one at rollout — plus an edge-avoidance penalty
on element spawns, and the last spawn constants promoted from code to
config. `[rng-sequence]` `[stamp]`: every seeded world regenerates
differently, so the measurement baselines were re-derived on the new
engine *before* the exp-003 prereg froze (the ordering exists because
exp-002's registered water gate turned out to sit below the new scripted
baseline — freezing first would have demanded the policy out-avoid its
own baseline). One batch item — a minimum same-type element separation
(item 3b) — was **proposed and withdrawn the same day** by the owner;
spec 027 records it as deliberately unbuilt.

Then the world itself moved: **24×24 → 20×20 "optE"** (#127) — water 7,
chow 6, bug 3, sunbeam 4, greeble 1. Screened 6/6 against the world it
replaced and measurably better on the deployed composition (0/30 seeds
with a distress-threshold crossing vs 1/30; worst distress 107 → 6).
The screen also taught a lesson worth recording: element *density* is a
visual metric, not a welfare one — the 16%-"busier" world has measurably
better-off cats. `[world-fresh]`.

### The config loader stops being polite

`#[serde(deny_unknown_fields)]` landed on all 27 config structs (#114)
after a near-miss in the lab: a typo'd dial (`bath_gain_ceilling`) was
silently accepted and silently ignored, and the error was caught only
because bit-identical results looked too clean to be true. Unknown keys
and keys in the wrong table now refuse to load, by name. The wrinkle:
the same TOML file is parsed by three owners (core, RL, plugins), so the
core parser recognises the other two's tables as opaque foreign tables.
Engineered to be `[stamp]`-neutral and proven so — the deserialization-
only change left the defaults hash byte-identical, so the frozen eval
exams and the re-baseline stayed pinned.

### Client graphics v3 and the card-layout arc

The viewer got its biggest rework since v2.1: a generative meadow ground
(#111, phases 0–3 of the v3 plan), then a run of layout work — cards
that collapse, animated portraits, landscape fitting to width, water
occlusion so wading kitties read as *in* the water, and click-to-toggle
panels (#116–#129, #131). All deployed. Phase 4 (cat art) and phase 5
(props/ponds) are chartered but not started.

### The deploy estate grows up

Three gaps in `update.sh`, each found by a real rollout: `--client-only`
(#105) deploys viewer assets without touching a server that can't yet
boot the newer schema; the cargo-PATH fix (#119) after a non-interactive
SSH deploy died mid-script (harmlessly — before the backup window); and
`--fresh` (#130), which retires the saved world (backup first, rename
aside, rollback renames it straight back) so a fingerprint-changing
config can regenerate instead of failing the resume guard. `--fresh` was
exercised in anger for the 20×20 rollout the day after tagging.

### Also in this release

- **Apache 2.0 license** — the repo is now formally open source.
- A 22×22 geometry screen and a resource-declutter screen both *passed*
  on welfare and were **recommended against anyway** (#101 archives the
  data): 22×22 is sub-floor on observation signal (F-014), and declutter
  spent 76% of the welfare margin for a visual preference. Screens that
  pass are not mandates.
- Repo hygiene: stacked-PR CI gap fixed (#109), backlog groomed, the
  config file's placement dials moved under a real `[elements]` header
  they had only appeared to be under.

---

## v2.5 — 2026-07-31 — the first learned kitty, the purr batch, the deployment estate

`[world-fresh]` `[stamp]`

The release where a trained policy first went live. exp-001 ran
end-to-end — dataset, behavior cloning, PPO/MAPPO arms, certification,
forensics — and its surviving artifact, **s6, was seated as Miso in the
served world** (#78): the first kitty whose mind is a neural network
rather than a script.

### exp-001: behavior cloning wins, and the collapse gets a name

The experiment's one-line outcome: **the behavior-cloned policy certified
clean and took a seat; the from-scratch RL arms collapsed**, and the
forensics (#77, #80) traced the collapse to roster-out-of-distribution
catatonia — a policy that freezes when the world contains an empty kitty
slot it never saw in training (F-010, superseding the earlier F-008
account). En route the experiment built the lab's durable tooling: the
engine-defaults stamp that pins every measurement to the engine that made
it (#61), the world-family collector, the twin probe, and `kitty-eval
--sample` (#71). Winners s3/s4/s6 all certified clean on the restored
world.

### The purr batch (specs 022, 023)

Purring became deliberate (spec 022, #79/#82): a kitty *chooses* the
quiet motor rather than it being a side effect, with a third-emitter
yield rule so purr choruses stay polite. The meow cooldown was retired
(spec 023, #84) — analysis showed it was doing nothing the turn economy
didn't already do. Soak §9.1 passed on the new shape.

### Withdrawn, deliberately: spec 021

The "welfare Cuddle" spec was **withdrawn before implementation**
(2026-07-27, parked at tag `parked/021-withdrawn`) when review falsified
its premise: busy neighbors already *are* lawful cuddle relief —
`Sleep{with}` and `Groom{target}` need only adjacency, so the "bug" the
spec existed to fix was the engine working as designed. The rule is now
durable in `docs/cuddle-relief-semantics.md`. Cheapest bug fix of the
project: zero lines.

### Estate work

- `policies/` became the committed artifact home, with s6's bytes
  verified against the training run's hash (#86).
- `kitty-eval` learned world identity (#83): certification output names
  the world it certified against, closing an ambiguity found when two
  worlds shared a config name.
- The served world was restored to 24×24 (it had drifted to 32×32),
  which is why this release carries `[world-fresh]`.
- Client, quietly: the v2 kitty portraits became the default viewer
  (footer toggle keeps v1). One dead end recorded honestly: pupil-gaze
  tracking was built, measured at ~0.24px of visible effect, and
  reverted.

---

## v2.4 — 2026-07-26 — the refactor arc complete (specs 018–020)

The three survey-ranked refactors shipped one at a time, each spec-first
and behavior-proven — **zero unratified behavior change across the arc**,
which is the entire point of the entry:

- **018** (#56): the certification CLI's four duplicated concerns
  single-sourced into `cli_support`; byte-identical output in both modes.
- **019** (#57): the need→relief pairing centralized into one exhaustive
  mapping, with score/walk/grab agreement compiler-enforced;
  bit-identical decisions throughout.
- **020** (#58): the config module restructured into
  `config/{mod,defaults,validate}.rs`, the validation catch-all dissolved
  into six section validators on a documented ordering; a 46-rule
  enumerated sweep stayed byte-identical throughout.

The by-product that mattered most: the **bit/byte-identical refactor
methodology** proved out here and became house practice — later releases
(the v2.6 strictness change especially) lean on it. This arc also
surfaced the welfare-Cuddle false positive that became spec 021's
withdrawal in v2.5.

---

## v2.3 — 2026-07-26 — the lab notebook opens

Zero engine changes — the release is the **experiments/ scaffold** (#55):
a governance rule separating the lab from the product, a findings
register opening with F-001 (two-channel credit assignment: fast for
self, slow for teammates), exp-001's preregistration with its first
honest Deviations entry, the twin probe with a first committed result,
and non-blocking drift-annotation CI. The project's working rules picked
up two clauses the same week: reach for existing code before writing new
(rule 2), and read the findings register before designing experiments
(rule 5). Specs 018–020 were chartered from a refactoring survey, setting
up v2.4.

---

## v2.2 — 2026-07-25 — the held-out evaluation suite (spec 017)

Certification stopped meaning "passes on the default world."
`kitty-eval --suite` scores a policy across **committed, frozen exam
configs** — four exams in `eval-suite-v1`: scale (48×48, 8 kitties),
scarcity at the validation floor, heterogeneity with a 40× trait spread,
and mixed-roster composition cells (guest/half/host) probing ad-hoc
teamwork via the guest-welfare differential. The suite is frozen by a
sha256 manifest verified at startup and in CI; evolution means a new
version alongside, never an edit — a discipline that later saved the
frozen exams through two engine strictness changes.

Verdicts anchor to the suite's own all-scripted baseline, never the
default world's bounds, with a per-kitty paired sign test (warn by
default, tighten-only enforcement). Also landed: `training.toml`, the
reference training world — the gym, not the bar. (#54)

---

## v2.1 — 2026-07-24 — RL hardened for round one; the meadow gets a sky

Two stories share the span. The RL surface was hardened for the first
real training round (#51–#53): a release-safe reward guard, a bounded
power-mean, unified reset-panic behavior, batch-vs-solo equivalence
tested at the Python surface, and full **PettingZoo 1.26 conformance**
behind a pinned, non-optional CI gate (the conformance work found a real
space-identity bug). Alongside it, spec 015 upgraded the pyo3 bridge and
spec 016 introduced **behavior plugins** (#45) — external brains behind a
trait, which is also where the plugin config's strict unknown-key
precedent was set.

Meanwhile the viewer became a place: night and dusk themes, a sky with
crepuscular tuning dials, mobile rendering fixes, kitty favicons, card
layout polish, and a serialize-once WebSocket optimization. The
deployment doc was written (#30) — the first version of what became the
deploy estate.

---

## v2.0 — 2026-07-23 — the world becomes a training environment

One spec, one merge, a new identity: **multi-agent RL** (spec 014, #22).
The world gained a PettingZoo `ParallelEnv` face over a pyo3 bridge,
observation schema 1, a welfare-shaped reward, and — the part that makes
it CloudKitty rather than a gym wrapper — **policy seats**: a trained
policy can be exported as a `.ckpolicy` artifact and installed as a
kitty's mind in the served world, sitting beside scripted kitties in the
same turn order under the same rules. Everything after this tag is the
consequence of that decision.

---

## v1.0 — 2026-07-23 — the living world

The state of the world at first tag (specs 001–013): a meadow grid
served over WebSocket to a vanilla-JS viewer, inhabited by kitties with
**needs** (thirst, hunger, play, sleep, bath, cuddle) that decay and
demand relief, **scripted brains** (needs-driven and playful) choosing
activities with real durations, **meows** as the signal vector between
kitties, purring, approach etiquette, water-averse pathing (a kitty
wades only when water is the only way forward — an invariant every later
water feature had to preserve), a **fair turn order** so no kitty
systematically moves last, and **welfare instrumentation** — happiness
tracking with anti-lock-in dynamics (spec 004) and the distress
thresholds that every later certification gate builds on. The world
persists as a snapshot and resumes across restarts; elements (water,
chow, bugs, sunbeams) spawn to configured minimums with jittered TTLs.

The versions before 1.0 are the road to exactly this; the specs
(001–013) are the honest record of how it got here.
