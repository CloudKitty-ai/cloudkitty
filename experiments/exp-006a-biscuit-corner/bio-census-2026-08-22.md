# Bio census — the Biscuit 2.0 roster (2026-08-22)

Behavioral fact sheet for bio updates, from `bio_census.py`
(committed 696d28f): 10 seeds × 20k ticks of the certified
composition (`c006a-L04s3`) on the certification world, greedy —
the same seats and world the battery certified. All numbers are
10-seed means; initiation counts are per 20k ticks. Reproducible
post-seating with the identical command (below); re-runnable for
any future roster by seating name.

## The pair map (share of ticks on the same or adjacent tile)

| pair | together | mean dist |
|---|---|---|
| Miso–Clementine | .270 | 5.2 |
| Miso–Kittybear | .261 | 5.3 |
| Kittybear–Clementine | .254 | 5.4 |
| Pumpkin–Kittybear | .243 | 5.8 |
| Biscuit–Clementine | .238 | 5.6 |
| Pumpkin–Clementine | .235 | 5.7 |
| Miso–Pumpkin | .231 | 5.7 |
| Biscuit–Pumpkin | .224 | 5.7 |
| Biscuit–Kittybear | .223 | 5.9 |
| Miso–Biscuit | .211 | 6.0 |

An even pile culture (.21–.27 across every pair, no cliques). The
tightest thread runs Miso–Clementine–Kittybear; Biscuit holds the
three loosest pairs — the kitten orbits the pile rather than living
in it, and comes in to play.

## Per-cat signatures

**Miso** — the sleep anchor. Sleeps 29% of ticks (most on the
roster) and is the top sleep-partner of every single cat: 311 and
318 sleep-pile joins per 20k with Clementine and Kittybear, 236–249
with Pumpkin and Biscuit — and it initiates more than it receives
(311 → Clementine vs 228 back). Voice: pure purr, 238/1k. Almost
never grooms others (4–8 initiations).

**Biscuit 2.0 (e006a-L-04-s3)** — the kitten, certified 89.96
happiness here. Plays 21.7% of ticks — four to six times anyone
else — split between critter play and duets with **every** cat
almost equally (217–286 duet starts per 20k with each of the four;
Pumpkin is narrowly the favorite at 286). Sleeps only 8.7%, barely
grooms itself (1.6%, roster low) and grooms others essentially
never — but is the **most-groomed cat on the roster**: Clementine
(265 initiations), Kittybear (256), and Pumpkin (181) all groom the
kitten. Voice: the quietest (27.6/1k) and the only cat with **no
purr at all** — its speech is entirely want-words (WantEat 43%,
WantDrink 31%, WantCuddle 13%, WantSleep 6%, WantBath 4%, WantPlay
2%). It asks; it doesn't croon. (The exp-006 candidate generation
was a near-silent channel isolate at 0.35/1k — the v6 kitten found
the want-register.)

**Pumpkin** — the purrbox, and the kitten's favorite playmate. Far
the loudest voice: 773/1k, 99.8% purr. Biscuit's top duet partner
(286 starts) and a steady groomer of Kittybear (220 initiations).

**Kittybear (e006-E1-s1)** — the groomer and the talker. Highest
grooming budget (16% of ticks) and grooms all four roster-mates at
215–256 initiations each — five of the top grooming flows on the
roster are Kittybear→someone. The conversationalist dialect holds
in this composition: 55.6/1k with a mix of purr 60%, **mew 27%**
(the "I'm coming, stay put" call), **here-water 8.8%, here-critter
3.5%** — the only cat that speaks grounded here-words.

**Clementine (e004, newly seated)** — the doting half of the pile.
Top grooming flow on the roster (→ Kittybear, and 265 initiations
→ Biscuit), heavy sleep partnership with Miso, purrs at 230/1k
(99% purr). Reads as a warm groomer-sleeper in this company.

## Directionality highlights

- Grooming is strongly one-way: Kittybear and Clementine give it
  (200+ initiations per partner), Miso and Biscuit receive it
  (single-digit initiations out).
- The roster grooms the kitten: Biscuit receives the two largest
  incoming grooming flows while giving almost none back.
- Sleep piles are Miso's doing — it out-initiates every partner.
- Duets are symmetric by nature (both cats count the start); the
  asymmetry that matters is *who* Biscuit reaches: all four, evenly.

## Notables

- Resting (awake, with kitty) is essentially extinct on this roster
  (< 0.1% everywhere): sleep is the pile currency, play is the
  daytime currency.
- Happiness context: Miso 95.3 / Clementine 94.8 / Kittybear 94.7 /
  Pumpkin 94.6 / Biscuit 89.96 — the kitten pays its character
  price and the census shows where it goes: play instead of sleep,
  asks instead of purrs.
- Raw per-seed rows in
  `exp-006-character-gen/results-raw/bio-census-c006a-L04s3--870001x10.json`.

## Regeneration (identical post-seating; new roster = new seating name)

```
cd experiments/exp-006-character-gen
.venv/bin/python bio_census.py c006a-L04s3
```
