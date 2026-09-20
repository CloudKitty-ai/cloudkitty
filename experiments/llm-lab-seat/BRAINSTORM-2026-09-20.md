# LLM seats: brainstorm notes, 2026-09-20

A record of the owner's conversation with Experiments on 2026-09-20,
kept so the #392 definition sitting starts from it rather than from
memory. Nothing here is ruled unless marked so. The engine ask that came
out of it is `HANDOVER-product-2026-09-20.md`.

## Where it stands

- **#392 (dataset generator) is not a kickoff.** Owner: "I'd like to
  spend more time defining exactly what we're building, and the future
  of LLMs in this project."
- **Served-world LLM seats are tabled** (owner). LLM seats are tested
  first in the lab's tickless world, which already exists: the headless
  env advances only when the harness calls `step`, so an LLM seat is the
  harness calling a model per decision, batched across LLM cats, with
  the world waiting.
- **The one engine ask**: the wire's DecisionRequest rendered on the
  Python binding, so the lab prompt is the served prompt (handover).

## The owner's sketch and the read on it

Owner's sketch: fine-tune on the output format; a harness that supplies
limited history plus logged reasoning traces; a standard prompt prefix
explaining the world, the objective, and action legality.

Experiments' read: the right skeleton, the standard shape for this kind
of system, with a better answer available for each of four choices.

1. **Fine-tune for decisions, not for format.** The wire gives the model
   the legal mask every tick; a harness turns that into constrained
   decoding, so only legal action ids and words are sampleable and
   format failures go to zero without training. The fine-tune then
   buys decision quality, once #392 says whose decisions.
2. **Cadence.** Per-tick is the wrong clock for a reasoning model. The
   alternative is two clocks: the model issues a standing order every N
   ticks or on an event, and an executor in the harness answers the
   per-tick wire from it (below).
3. **History should be model-authored.** The observation already
   carries the engine's history (meow digest, element memory, scene
   age). What the model lacks is episodic memory; a bounded journal the
   model appends to and reads back beats a window of raw ticks, and is
   where the reasoning trace lives (spec 053 research R10).
4. **The rules prefix should be generated** from the served config and
   the encodings docs at boot, sha-stamped like `/settings`, and cached.
   A hand-written one drifts from the engine.

Constraints carried into the definition: rule 5 (a seat that could ever
teach or enter a corpus sees the fog view only); an LLM seat is a seat
and clears the battery floor and welfare gates like any other (F-042);
its refusals land in the refusal ring.

The framing question, unresolved and the owner's: is the LLM there to
be a cat, or to be something the cats are not? If a cat, a fine-tuned
model at per-tick cadence is a slower Gen 2 mind and the generator is a
distillation set. If something else (narrative, long horizon, language
to the viewer), the planner shape is the design and the interesting
corpus is plans and journals, not tick decisions.

## Planner mode (Experiments' description, on the owner's ask)

- **The plan is a standing order** from a small typed vocabulary (go to
  the nearest beam and nap; stay beside Miso; go drink then rest by the
  pond; answer that want_food; play with whoever is nearest; idle and
  watch), each with a target, a done condition and a give-up condition,
  plus one sentence of reasoning for the journal and the viewer.
- **The executor answers the wire** every tick from the current order,
  deterministic and dull: step toward the target, use the element or
  propose the partner action when adjacent, say the named word when
  legal, otherwise idle. It never calls the model. Its competence is the
  cat's ceiling, which is the design's main cost.
- **Replanning is event driven** (order completes or gives up, a need
  crosses a line, a want is heard, a refusal comes back, something new in
  view) with a timer backstop, N around 30 to 50 ticks. Five cats at one
  call per 40 ticks is one call every 6 s.
- **Memory is the journal** the model writes; each call gets the rules
  prefix, the fog view, the order and how it ended, and the last few
  journal lines.
- **Where the edge shows**: commitment across ticks, the thing tier 2 is
  measuring whether PPO can be made to hold ("walk to the beam before
  sleeping"). A planner holds it because it is told and can carry an
  intention. What it cannot do is react inside a tick; the executor and
  the engine's own validation cover that.
- **What stays the engine's**: legality, refusals, the exchange
  deadline, welfare. A late or malformed reply falls to the seat's
  built-in behaviour for that tick; the harness retries within the
  deadline (R10). The engine cannot tell a planner seat from any other
  advisor.
- **The fine-tune becomes** plans and journal lines, a few thousand
  examples, likely bootstrapped by prompting a larger model and keeping
  what the executor completed. The generator on #392 becomes a
  plan-and-outcome recorder. Prompting alone may carry a first seat.
- **Evaluation**: the battery unchanged, plus plan completion rate by
  kind and time-to-replan under events.
- **Risks**: the executor is the ceiling; event triggers chatter without
  debouncing; a planner cat is legible, which is charm and a discipline.
- **Cheapest first step**: the executor plus a hand-written planner that
  always says "nap on a beam when sleepy", through the existing wire.

## Hardware and pace (numbers as stated in the conversation)

Machine: Apple M5 Pro, 18 cores, 64 GB, no local LLM runtime installed
as of 2026-09-20.

- **Owner's benchmark point**: Qwen 3.5 4B at 8-bit on this hardware,
  0.2 s time to first token, 161 tokens/s (existing benchmarks, prompt
  length unstated).
- **Per-tick arithmetic on those numbers**: one cat, no reasoning,
  about 0.35 s; five cats batched, 0.4 to 0.6 s, inside the 800 ms tick;
  with a 100-token trace, 1.0 to 1.2 s, over it. The swing term is time
  to first token, which scales with prompt length; prefix caching of the
  rules prefix is a requirement of the harness, not a nicety.
- **4B at 4-bit**: roughly 1.5 to 1.8× the decode speed (240 to 290
  tokens/s), prefill unchanged; five cats no reasoning 0.3 to 0.5 s,
  with a trace 0.6 to 0.8 s. Quantisation loss shows more on a 4B than
  an 8B; the practice is train at higher precision, quantise after, and
  check held-out decision accuracy at both.
- **8B at 8-bit** on this machine: about 80 to 90 tokens/s by bandwidth
  scaling; fine as a planner every N ticks, tight per tick across five
  seats. A natural split is a 4B actor on the tick and an 8B planner
  above it, both resident.
- **H100**: single-stream decode only 1.3 to 1.8× the Mac at 4B (kernel
  overhead, not bandwidth); time to first token 50 to 100 ms; a 70B at
  fp8 fits one card at 30 to 40 tokens/s. What it buys is throughput:
  a certification-scale battery (30 seeds by 20k ticks by five cats,
  about 3 M decisions) is half a day on an H100 and weeks on the Mac;
  LoRA on an 8B does 50 M tokens in about an hour. Serving from a cloud
  card to kitties.ai adds 20 to 100 ms per call.
- **Tickless lab**: latency stops being a design input, but call count
  does not: a 20k-tick run with one LLM cat is 20k calls, two to three
  hours at the 4B numbers without reasoning, ten times that with. Lab
  reads start at screen scale (five seeds by five thousand ticks);
  certification scale is the H100 question, only if a seat earns it.

## Training and portability (owner: a rented NVIDIA GPU for training and validation, the Mac for long-term serving)

- **QLoRA** is LoRA against a 4-bit base: about a third of the memory,
  1.5 to 2× slower steps, a small quality cost. Not needed for a 4B or
  8B on 64 GB (bf16 LoRA fits and is better); it earns its keep for a
  30B-class planner trained locally, or when the served precision is
  4-bit (adapters trained against the quantised base lose less at
  serving than train-then-quantise). On an H100 it is what puts a 70B
  fine-tune on one card.
- **Portability checklist** for a GPU-trained model served on the Mac:
  merge the adapter and save plain bf16 safetensors before leaving the
  GPU; quantise on the Mac in the Mac's format (MLX `convert -q`, or
  GGUF), never ship a CUDA quant; validate the served artifact itself
  with a screen-scale run on the same seeds as the GPU run and count
  disagreements; pin the model like a policy (checkpoint sha, base
  revision, quantisation recipe, runtime version; spec 034's registry
  discipline); ship the tokenizer and chat template with the weights;
  pick one Mac runtime (MLX preferred: native, fast M5 prefill, prefix
  caching, batching server) and stay on it. The harness talks to an
  OpenAI-shaped local endpoint so it is runtime-agnostic.

## Open decisions (the definition sitting's list)

1. What an LLM seat is for: a sixth cat, a teacher, a narrator, an
   operator tool.
2. What the model sees and says: the per-tick wire as the whole
   interface, or plans above it.
3. Whether a model's reasoning ever enters lineage rows or corpora
   (rules 5 and 6).
4. Fine-tune or prompt, and on whose decisions or plans.
5. Where it runs and what it may cost per call (the Mac serves; the
   GPU trains and certifies).
6. Actor versus planner, now testable in the same lab world on the
   same seeds once the binding renders the request.

## Preliminary model screen (owner, later in the day: "not yet, just brainstorming"; comfortable compiling)

A screen over models, sizes and quantisations before any fine-tune, on
the Mac, so the seat's shape is chosen on numbers. Three reads, each a
script to mock up first:

1. **Serving numbers on real prompts** (`bench_serve.py`): for each
   model and quant, time to first token with and without prefix caching,
   decode tokens/s, and a batch of five, on prompts of the served shape
   (rules prefix plus a rendered request of real length), not benchmark
   prompts. MLX server as the default runtime, llama.cpp as the check.
2. **Zero-shot decision agreement** (`eval_decisions.py`): prompts built
   from the held-out corpus traces (`trace.jsonl` carries the
   start-of-tick snapshot the wire's `world` is built from, plus the
   legal mask), the model's choice constrained to the legal set, scored
   as agreement with the teacher's applied action and with a Gen 1
   mind's argmax on the same rows, by activity class. Reads prompt
   design (what to render, how to name legality) as much as the model.
   Until the binding renders the request (handover), the prompt is a
   lab rendering and is marked as such.
3. **Quantisation sensitivity** (`quant_agreement.py`): the same prompts
   through bf16, 8-bit and 4-bit of one model; disagreement rate against
   bf16 is the number that decides the served precision, before any
   fine-tune exists.

Candidates worth a row: Qwen 3.5 at 1.7B, 4B, 8B (the owner's benchmark
family); Gemma and Llama at 4B and 8B for a second lineage; instruct
variants first, base variants only if a fine-tune is planned. The small
end matters: a 1.7B actor at 8-bit may be enough on the tick and leaves
the budget for a planner. Nothing here is scheduled.

**Pencilled extension arm (owner): a 30B-class model**, run only if the
1.7B → 4B → 8B arc on the decision-agreement read is still climbing at
8B. A flat arc means the seat is prompt- or executor-bound and a bigger
model buys nothing; a rising one says capacity is still paying and the
30B point tells whether it keeps paying. On the Mac a 30B runs at 4-bit
(about 17 GB, MLX) at planner cadence only; on the GH200 it runs at
bf16 or fp8 for the screen. The decision to run it is read off the
arc, not scheduled in advance.
