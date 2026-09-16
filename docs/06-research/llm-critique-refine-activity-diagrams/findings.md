# LADEX — findings & what they mean for GraphPilot

**In one sentence:** a research team tested whether an LLM that draws UML activity diagrams from
text should have its *structure* checked by a **deterministic algorithm** or by **another LLM** — and
the algorithm won clearly (well-formed diagrams, higher accuracy, far cheaper). That is the same bet
GraphPilot makes.

*Paper:* Khamsepour et al., *The Impact of Critique on LLM-Based Model Generation from Natural
Language: The Case of Activity Diagrams* (Univ. of Ottawa + Ciena) — arXiv
[2509.03463](https://arxiv.org/abs/2509.03463) v2, Nov 2025. Local copy:
[`ladex-khamsepour-2025.pdf`](./ladex-khamsepour-2025.pdf).

> **About this doc.** A plain-English reading summary, kept for traceability. GraphPilot's actual
> design decisions live in [04-generation-design.md](../../03-design/07-generation.md)
> and [07-evaluation-and-doe-design.md](../../07-history/retired-evaluation-and-doe-design.md);
> this file summarizes the paper and points there instead of restating it.
>
> **Since removed:** the eval/DOE *implementation* this doc maps to (the ground-truth matcher, the
> LLM judge, and the DOE runner) was later removed — pending an embeddings-based rebuild — so the
> code-file mappings below are historical. The generation-side structural critic + critique-refine
> loop it also cites are retained.

---

## The 30-second version

The paper builds a pipeline called **LADEX** that turns a written procedure into a UML activity
diagram using the popular "draft it, then critique-and-fix" loop. Its core question: **in that loop,
who should do the checking — code, or the LLM?**

One way to hold it: the LLM is the **writer**; the checker is the **editor**. The paper's result is
that the editor should be a **rulebook (an algorithm)**, not a second opinion from the same kind of
writer.

What they found:

- **Check structure with an algorithm, not the LLM.** About 17% more correct, 15% more complete,
  always well-formed — and much cheaper. *(This is the headline.)*
- **Letting the LLM check *meaning* barely helps.** Small, dataset-dependent gain for a big jump in
  LLM calls.
- **The fix-up loop is worth it** (beats one-shot generation), and **reasoning models beat
  instruction-following ones**.

Two configurations they recommend:

| If you want… | Use | Correct | Complete | LLM calls |
| --- | --- | --- | --- | --- |
| Best quality | algorithmic structure check **+** LLM meaning check, on O4 Mini | ~86% | ~92% | ~4.9 |
| Best value | algorithmic structure check only, on O4 Mini | ~86% | ~90% | ~1.1 |

---

## The problem it tackles

The usual way to make a diagram from text is: have an LLM draft one, then run a loop where it
critiques its own draft and fixes it. The authors point out that such a loop has to fix **two very
different kinds of mistakes**, and that the two deserve different treatment:

- **Structure** — is the diagram well-formed? (One start node, decision branches are labelled,
  everything is reachable, etc.) These are hard rules, so a computer can check them.
- **Meaning** — does the diagram actually match the text? (Right steps, right order, right parallel
  branches, nothing invented.) This needs interpretation, so it is hard to check with code.

That leads to the two questions the study answers:

1. For the **structure** check, use an **algorithm** (rules taken from the UML spec) or the **LLM**?
2. For the **meaning** check, how good — and how expensive — is the LLM as a stand-in for a human?

They study this for **activity diagrams**, in a pipeline they call **LADEX** (LLM-based Activity
Diagram EXtractor).

---

## The design: LADEX

### The pipeline

```
Input: a written procedure (natural language)

  Step 1  GENERATE  (LLM)      -> a first-draft activity diagram

  Step 2  CRITIQUE-REFINE LOOP (repeats, with a cap)
     2.1  CRITIQUE              -> find rule violations in the draft
                                     - structure: algorithm OR LLM
                                     - meaning:   LLM (or skipped)
     2.2  REFINE   (LLM)        -> fix the draft, given the critique + past rejected drafts

  Loop stops when the critique finds nothing, or the cap is hit.

Output: the diagram (kept only if it passes the critique)
```

Two things to note:

- Generating and refining are **always** done by the LLM. Only the **structure** part of the
  critique can be swapped between an algorithm and the LLM. The **meaning** check is always the LLM
  (or turned off — you can't do it with code).
- In the experiments the loop is capped at **5 rounds**. If it still hasn't converged, they throw the
  draft away and start over (in practice, one restart was always enough).

### The rules the diagram must follow

These rules are written into the prompts. **Structure rules (SC1–SC6)** — six checkable rules, boiled
down from the 17 well-formedness statements in the UML 2.5.1 spec:

| # | Rule |
| --- | --- |
| SC1 | Exactly one start (initial) node. |
| SC2 | At least one end node. |
| SC3 | The start node has nothing pointing into it. |
| SC4 | End nodes have nothing pointing out of them. |
| SC5 | Every decision node has ≥2 outgoing branches, each labelled with a guard. |
| SC6 | Every node is reachable from the start. |

**Meaning rules (AC1–AC5)** — from UML control-flow semantics plus prior LLM work:

| # | Rule |
| --- | --- |
| AC1 | Labels match the text. |
| AC2 | Actions are in the right order, with the right triggers. |
| AC3 | Every described flow is present; nothing is invented. |
| AC4 | Things that happen at the same time are drawn as parallel branches. |
| AC5 | Keep only the real steps — drop examples and commentary. |

(AC1–AC3 come from earlier work and UML; AC4 was added for parallelism, AC5 to strip filler.)

### How a diagram is written down

LADEX represents a diagram as **Draw.io-style CSV** — one row per incoming arrow:
`node id, type, predecessor id, arrow label` (type is action / decision / initial / end). A node with
several arrows into it gets several rows; the start node leaves the predecessor and label blank.

### The five versions they compared (the ablation)

They build five versions to isolate what matters — does the loop help, does an algorithm beat the LLM
at structure, and does the meaning check earn its cost:

| Version | Fix-up loop | Structure check | Meaning check |
| --- | --- | --- | --- |
| **Baseline** | no (one shot) | — | — |
| **LADEX-LLM-LLM** | yes | LLM | LLM |
| **LADEX-Alg-LLM** | yes | **algorithm** | LLM |
| **LADEX-LLM-NA** | yes | LLM | none |
| **LADEX-Alg-NA** | yes | **algorithm** | none |

---

## How they tested it

**Scoring — two independent checkers, so neither is trusted alone.** Each generated diagram is
compared to an expert-made "correct" diagram by matching up their nodes:

- **B-Match** — a plain algorithm. It walks both diagrams from the start (breadth-first) and matches
  nodes by how similar their labels are, using text embeddings (`Alibaba-NLP/gte-base-en-v1.5`) plus
  the arrow/guard labels.
- **L-Match** — an LLM (O4 Mini) asked to match nodes by text, then behaviour, then structure. They
  checked it against human annotators and it agreed closely (F1 ≈ 96% on the Ciena data, ≈ 91% on the
  public data).

**The two scores** (both come out of that node matching):

- **Correctness** — of the nodes the LLM drew, how many are right (i.e., found in the expert diagram).
- **Completeness** — of the nodes the expert diagram has, how many the LLM actually captured.

Plus **structural consistency** (how many diagrams break a structure rule) and **cost** (number of
LLM calls).

**Data and models:**

| | Industry (Ciena) | PAGED (public) |
| --- | --- | --- |
| Diagram/text pairs | 20 | 200 (sampled from 3,394) |
| Avg. nodes per diagram | 29.2 | 10.5 |
| Avg. tokens per description | 1,412 | 133 |

Models: **GPT-4.1 Mini** (instruction-following), **O4 Mini** (reasoning), and
**DeepSeek-R1-Distill-Llama-70B** (reasoning, public data only). Every run was repeated 5× (~16,000
descriptions in total).

---

## How they scored "how correct" (deeper — reference for our eval framework)

*(The mechanics behind "How they tested it" above, since this is what a GraphPilot eval will reuse. GraphPilot's own eval design is owned by [07-evaluation-and-doe-design.md](../../07-history/retired-evaluation-and-doe-design.md).)*

### The core idea: match nodes to a reference, then take two ratios

Everything rests on a **node-to-node matching** between the generated diagram and an expert
**ground-truth** diagram. Once you have that matching, two scores fall out:

- **Correctness** = matched generated nodes ÷ *all* generated nodes — *"of what the model drew, how
  much is right?"* (precision-like; catches invented/extra nodes). Formula: `cor = |A| / |N_generated|`.
- **Completeness** = matched ground-truth nodes ÷ *all* ground-truth nodes — *"of what should be
  there, how much did it capture?"* (recall-like; catches missing nodes). Formula: `com = |B| / |N_truth|`.

So "how correct is the graph" is never one opaque number — it's *match to a reference, then report
both ratios*. A diagram can be 100% correct but 40% complete (right as far as it goes, but missing
half the steps), or the reverse.

### Two matchers — run both, cross-check

They build that matching two independent ways so no single scorer is trusted:

- **B-Match (deterministic).** Walk both diagrams breadth-first from the start node; for each
  already-matched pair, match each successor to the best-scoring successor on the other side; never
  revisit a pair. The per-step score averages **label similarity** (text embeddings — `gte-base`,
  cosine) with the **edge/guard-label similarity**. Free, reproducible, offline.
- **L-Match (LLM judge).** Ask an LLM to match nodes using three criteria *in priority order*:
  **textual** (labels mean the same) → **behavioural** (they share some matched predecessors/
  successors) → **structural** (same node type). Catches synonym/paraphrase matches that pure
  string/embedding similarity misses.

### Make the LLM judge trustworthy (don't skip this)

They didn't just trust the LLM judge — they **calibrated it against humans**. Experts hand-annotated
node matches on a small sample (5 diagrams per dataset), then scored the LLM's matching against the
expert's:

- true positive = matched by both · false positive = LLM-only · false negative = expert-only → **precision / recall / F1**.
- Result: **F1 96.3%** (Ciena), **90.6%** (public) → high agreement, so the judge is a credible instrument.

*Lesson for our eval:* before trusting an LLM judge, score it against a handful of hand-labelled
diagrams and report its P/R/F1.

### Comparing configurations (the stats)

Because LLM output is noisy, they:

- **repeat every run 5×** (and fix temperature where the model allows);
- compare configs with the **Wilcoxon rank-sum test** + **Vargha-Delaney Â₁₂** effect size
  (Â₁₂ ≤ 0.44 / 0.36 / 0.29 = small / medium / large; 0.44–0.56 = negligible), at 5% significance;
- correct for many comparisons with **Benjamini–Hochberg** (adjusted p-values);
- cross-check the two matchers with **Spearman** correlation (0.8–1.0 — the deterministic and LLM scorers agree).

### Report several axes, not one number

The scorecard per config stays split: **structural validity** (how many diagrams break a rule),
**correctness**, **completeness**, and **cost** (LLM calls / tokens) — never blended into a single figure.

### What to borrow for the GraphPilot eval framework

- The **match-to-reference → correctness + completeness** model *is* GraphPilot's planned deterministic matcher (removed pending an embeddings-based rebuild — see `07-evaluation-and-doe-design.md`).
- The **deterministic + LLM-judge, cross-checked** pattern maps to GraphPilot's validity anchor + deterministic matcher + LLM closeness judge (see 07).
- Steal the **judge-calibration** step (P/R/F1 vs a few hand-labelled examples) and the **stats recipe** (repeat + non-parametric test + effect size + BH) for the DOE.
- One fidelity gap to plan around: they match labels with **embeddings**; GraphPilot's matcher uses stdlib string/token overlap, so a *correctly renamed* node can score as a miss. If eval precision matters, an embeddings backend closes that gap — which is exactly the planned rebuild (see `07-evaluation-and-doe-design.md`).

---

## What they found

- **The two checkers agree (RQ1).** B-Match and L-Match line up closely (Spearman ρ = 0.8–1.0) and
  never disagree on which version is better — so the conclusions aren't an artefact of one scorer.
- **The loop beats one-shot (RQ2).** The one-shot baseline left ~22% of diagrams malformed; the
  algorithm-checked loop versions left **0%**. The loop also raised correctness and completeness,
  costing roughly 0.9–6.3 extra LLM calls depending on version.
- **Algorithm >> LLM for the structure check (RQ3 — the main result).** Algorithm-checked versions
  were *always* well-formed; LLM-checked ones still left ~18–19% malformed even after fixing. On
  average the algorithm gave **+16.95% correctness** and **+15.12% completeness**.
- **The LLM meaning check earns little (RQ4).** It helped correctness on only one of the two
  datasets, while pushing average LLM calls from **~1.08 to ~4.91** (about 5.4 more calls).
- **Reasoning models win.** O4 Mini gave the best quality *and* used fewer calls than GPT-4.1 Mini.

The authors' suggested next step is a **neuro-symbolic** design: the LLM generates, and an algorithm
acts as the formal-checking layer — exactly the division of labour the results point to.

---

## What it means for GraphPilot

GraphPilot makes the same core bet: **check structure with code, not the LLM, and keep meaning-judging
offline.** Each row below ties a paper finding to the GraphPilot choice it supports, and to the doc
that actually owns that choice.

| Paper finding | GraphPilot does… | Owned by |
| --- | --- | --- |
| Algorithm beats LLM at structure (RQ3) | A deterministic structure critic, `services/diagrams/validation/structural_constraints.py`, used at generation time and reused as the eval "validity anchor" | [04](../../03-design/07-generation.md) · [07](../../07-history/retired-evaluation-and-doe-design.md) |
| Stating rules up front prevents mistakes | Injects the rules into the generate/repair prompts via a `{{structural_rules}}` placeholder | [04](../../03-design/07-generation.md) |
| The loop helps; the cheap version is best value (RQ2) | A bounded loop, `DiagramGenerationService(refine_max_rounds=…)`, default 1 (0 = one-shot); swept 0/1/2 in the DOE | [04](../../03-design/07-generation.md) |
| Reasoning models win | Reasoning on by default: `AZURE_OPENAI_REASONING_EFFORT=medium` | [04](../../03-design/07-generation.md) |
| LLM meaning-check costs a lot for little (RQ4) | No LLM meaning-check inside the live loop — meaning is judged **offline**, in eval | [04](../../03-design/07-generation.md) · [07](../../07-history/retired-evaluation-and-doe-design.md) |
| B-Match scores correctness/completeness | A deterministic matcher (planned — removed pending an embeddings-based rebuild) — GraphPilot's B-Match analogue | [07](../../07-history/retired-evaluation-and-doe-design.md) |
| An LLM matcher (L-Match) tracks expert judgment | An LLM "closeness" judge as the headline semantic score (offline, sampled and averaged), cross-checked by the deterministic matcher | [07](../../07-history/retired-evaluation-and-doe-design.md) |

**Where GraphPilot goes further than the paper:**

- **More diagram types.** LADEX only does activity diagrams. GraphPilot reuses the same
  structure-critic idea for `activity_diagram`, `use_case_diagram` (UML) and `bdd_diagram` (SysML),
  with conservative per-type versions of the UML rules.
- **The same idea, applied to layout.** The paper's whole point is *LLM for meaning, algorithm for the
  formal parts*. GraphPilot extends that to a job the paper never touches — **placing the nodes**. The
  LLM only decides *which* nodes and edges exist; a deterministic step
  (`services/generation/pipeline/diagram_layout_service.py`) works out *where* they go (Graphviz, with a
  pure-Python `grandalf` fallback), because LLMs are notoriously bad at graph layout. The paper avoids
  the problem entirely by handing its CSV to Draw.io. See the *Layout* section of
  [04-generation-design.md](../../03-design/07-generation.md).

---

## Quick reference

**The paper, section by section:**

| § | Section | In short |
| --- | --- | --- |
| I | Introduction | Why models beat text; the two kinds of mistakes; the two questions. |
| II | Constraints | The activity-diagram definition; the SC and AC rules; a worked example. |
| III | Generation & Refinement | The pipeline, the CSV format, the prompts, the five versions. |
| IV | Matching | B-Match and L-Match (with L-Match checked against experts). |
| V | Evaluation | The four questions, data, metrics, results, threats. |
| VI | Related Work | How LADEX compares to earlier text-to-model tools. |
| VII | Conclusion | Recommends algorithm-structure + LLM-meaning on a reasoning model; next up = neuro-symbolic. |
| App. | Appendices | Full 17 structure rules; the prompt templates. |

**Caveats the authors flag:**

- **One "correct" answer per text** — but a procedure can have several valid diagrams; the scores
  assume a single reference.
- **Limited scope** — plain action nodes only; no swimlanes or nested/composite nodes.
- **Possible data leakage** — the public dataset may be in training data, but that affects every
  version equally; the Ciena data is private and unseen.
- **A few models** — three LLMs, but the trends hold across all of them.
