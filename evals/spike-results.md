# Spike results: cheapest stack that still prevents slop

Run Monday, Nov 9, 2026 (America/Chicago) on Grok Bot's box. No model API calls were made. All fixtures are synthetic and labeled by one author. Nobody was contacted.

## 1. Verdict on validity

**A public write-up of that consulting workflow is still a valid spike, but one condition in it has already been met.** "Useful until Sonnet 5.5 drops" happened six days after it was posted. Haiku 5.5 has also shipped. So the current question is whether that workflow still needs a gate at all after 5.5, and how cheap that gate can be.

| Date (2026) | Event | Source |
|---|---|---|
| Sep 22 (9:28 PM CT) | A public post: Jev hook built, then made "somewhat obsolete" by Opus 5.5. "Useful until Sonnet 5.5 drops." | Public post (time decoded from the activity ID; link omitted) |
| Sep 22 | Opus 5.5 released at $4 / $20 per MTok. | [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| **Sep 28** | **Sonnet 5.5 released** at $2 / $10, described as "writes more clearly than our previous generation." | [Anthropic](https://www.anthropic.com/claude-sonnet-5-5), [Reuters](https://www.reuters.com/technology/anthropic-rolls-out-second-claude-55-model-it-builds-toward-ipo-2026-09-28/) |
| Sep (day not shown) | Arize ran evals on Opus 5 vs 5.5. Em dashes fell from 12.9 to 0.05 per 1k words, and other Claudisms fell by half (4.79 to 2.38 per 1k). New habits appeared: 2.5x more bold lead-in bullets, 35% more three-part lists, 8% longer output. A phrase list caught **9 of 153** human flags. | [Arize](https://arize.com/blog/anthropic-says-it-fixed-claudes-writing/) |
| Oct 1 | Graphite: Opus 5.5 still shows 2,548 tells, only 4% fewer than Opus 5. "This matters" appears at 116x the human rate and "is more than an X, it's a Y" at 98x. | [Graphite](https://graphite.io/research/ai-tells-opus-5-5-update), [TechCrunch](https://techcrunch.com/2026/10/01/opus-5-5-loves-to-tell-you-this-matters-and-other-ai-writing-tells/) |
| **Oct 2** | **A follow-up public post:** the same workflow's baseline still ships "twelve skills covering … stopping slop" as a versioned package. | Public post (link omitted) |
| Oct 7 | Haiku 5.5 released at $0.10 / $0.50 per MTok for prompts up to 100k tokens. Anthropic positions it for classification. | [Anthropic](https://www.anthropic.com/claude-haiku-5-5) |
| Oct 14 | Jev 1.14 released. Price unchanged at $0.042 per MTok input, and output is free. | [TypeSafe docs](https://docs.typesafe.ai/models) |
| Oct 21 | KudoWrite measured fiction only. Sonnet 5.5 used 0 listed clichés in about 27k words, but still wrote 0.89 "not X, but Y" constructions per 1k words. | [KudoWrite](https://kudowrite.com/research/ai-slop-index) |
| Mar 18 (last commit) | stop-slop has had no commits since before that September post. Its rules still say "all adverbs," "no passive," "no em dashes," and restructure any Wh- opener. | [GitHub](https://github.com/hardikpandya/stop-slop) |

**What's stale:** the "until Sonnet 5.5" line, and any assumption that em dashes or "it's not X, it's Y" are the main 5.5 tells. **What still holds:** residual slop after 5.5 is measured and public. The tells moved to salience flags, "more than X" frames, and over-structure. And a later public post shows stop-slop is still part of that workflow's baseline. I found no public follow-up saying the hook or the skill had been removed.

## 2. What ran and what didn't

| System | Measured here? |
|---|---|
| (A) Style contract only | Size (139 estimated tokens) and cost only. Generation quality **not measured**, because no model was available. |
| (B) Always-on stop-slop skill | Size (3,595 estimated tokens), cost, and a *proxy* for its rule set: a ban-list gate built from its Quick Checks. Model rewrite **not run**. |
| (C) verify-copy gate, rewrite only on fail | Gate fully measured (v1 vs v2) on 85 fixtures. Rewrite **not run**. Cost estimated. |
| (D) Model default | **Not measured.** No model was available. |

**No model bakeoff ran.** The environment has no Anthropic, OpenAI, TypeSafe, or other model API keys, and no local model runtime (no GPU, no ollama or llama.cpp). Following the brief, I did not create accounts or ask for keys, and I did not fabricate any model outputs. So meaning-preservation and residual-after-rewrite are **unmeasured**.

## 3. Gate results (real numbers, synthetic fixtures)

Fixture set: 85 synthetic items.

- **dev**, 39 items. Includes the 5 starter items. v2 was tuned on this split.
- **holdout**, 34 items. Written before v2 was run on it.
- **stress**, 12 items. Written *after* v2 was frozen to probe its blind spots.

Categories: classic slop, Opus 5.5-style residuals, structural slop, clean human copy, and over-correction traps. Surfaces: email, Slack, proposal, workshop, lesson.

Gates compared:

- **v1**: the starter gate.
- **v2**: v1 plus quote stripping, Graphite and Arize 5.5 residuals, restate/recap and scaffolding signals, and soft signals that need two hits to trip.
- **ban-list**: stop-slop's Quick Checks applied literally (any adverb, em dash, passive, Wh- opener, or "not").
- **always-rewrite**: system B's routing.

Holdout (n=34):

| Gate | TP | FP | FN | TN | Precision | Recall | F1 | Flag rate |
|---|---|---|---|---|---|---|---|---|
| v1 (starter) | 8 | 1 | 8 | 17 | 0.889 | 0.500 | 0.640 | 0.265 |
| v2 (verify-copy) | 15 | 0 | 1 | 18 | 1.000 | 0.938 | 0.968 | 0.441 |
| ban-list (stop-slop rules, literal) | 12 | 13 | 4 | 5 | 0.480 | 0.750 | 0.585 | 0.735 |
| always rewrite (B) | 16 | 18 | 0 | 0 | 0.471 | 1.000 | 0.640 | 1.000 |

Stress (n=12: 8 slop items using vocabulary outside the regex lists, plus 4 long clean items over 80 words):

| Gate | TP | FP | FN | TN | Recall | Note |
|---|---|---|---|---|---|---|
| v1 / v2 | 0 | 0 | 8 | 4 | **0.000** | Misses "in today's fast-paced world," "delve," "leverage," "not merely X; they're Y." No false positives on long clean copy. |
| ban-list | 6 | 4 | 2 | 0 | 0.750 | Flags all 4 long clean items. |

All 85 items: v2 has precision 1.000, recall 0.767, F1 0.868. v1 has precision 0.905, recall 0.442, F1 0.594.

Per category, dev and holdout combined (correct / n):

| Gate | classic | 5.5 residual | structural | clean | over-correction traps |
|---|---|---|---|---|---|
| v1 | 13/13 | 5/13 | 1/9 | 21/21 | 15/17 |
| v2 | 13/13 | 13/13 | 7/9 | 21/21 | 17/17 |
| ban-list | 10/13 | 10/13 | 2/9 | **12/21** | **0/17** |

What this shows:

1. **Lexical rules go stale with each model.** The starter gate was written around Claude 5-style tells and caught 5 of 13 Opus 5.5-style residuals. It got to 13/13 only after I added the patterns Graphite published. This matches Graphite's finding that each model version brings its own tells.
2. **Regex is a floor, not the gate.** v2 caught **0 of 8** slop drafts phrased with words it had never seen. Arize hit the same wall: a phrase list caught 9 of 153 human flags. A cheap learned classifier (Jev or Haiku 5.5) is the layer that has to cover "moves, not phrases."
3. **A literal ban-list over-corrects.** It flagged 9 of 21 clean drafts and all 17 over-correction traps. Those traps include a sincere "really," a precise em dash, and a client quotation. Over-correction is a fail, so the ban-list loses even though its recall is decent.
4. **The short-text lesson still holds.** Under 80 words, per-100 rates come from one or two tokens. One adverb in 20 words reads as 5 per 100. v2 ignores rates below 80 words and caught nothing on rates in this set. Every true positive came from phrases and structure.
5. **Quoted text must be excluded.** v1 flagged a client quotation ("Here's the thing: …") as slop. v2 strips quotes before scoring.

## 4. Bloat and cost (estimates)

Token counts are estimates. I used Anthropic's documented ratio for the current tokenizer, about 555k words per 1M tokens (1.8 tokens per word). I could not run a real tokenizer on the box.

| Context | Words | Est. tokens |
|---|---|---|
| stop-slop frontmatter (always listed) | 36 | ~65 |
| stop-slop SKILL.md | 361 | ~650 |
| stop-slop SKILL.md + 3 references (always-on "full" load) | 1,995 | **~3,595** |
| verify-copy SKILL.md | 598 | ~1,077 |
| verify-copy patterns.md (before today's addition) | 343 | ~618 |
| Style contract (5 lines) | 77 | **~139** |

**Honest bloat finding:** verify-copy's SKILL.md (598 words) is *longer* than stop-slop's SKILL.md (361). Its only saving is that it loads only when the gate fails and leaves out the long reference files. Next, cut it down to the contract plus the rewrite rules.

Cost per **1,000 drafts**, counting only the slop-control overhead (the draft's own generation is excluded). Assumptions:

- A rewrite reads the draft and outputs about as many tokens as the draft.
- B runs a rewrite pass on every draft.
- C pays for a rewrite only on the share r of drafts that fail the gate.
- Prices are Anthropic list prices as of Nov 9 and Jev at $0.042 per MTok input. r is a scenario, not a measurement: that workflow's real failure rate after 5.5 isn't public, and my fixture flag rates come from how I wrote the set.

| Draft size | Model | A: contract only | B: always-on, uncached | B: skill cached | C: r=10% | C: r=25% | C: r=50% | Jev gate add-on |
|---|---|---|---|---|---|---|---|---|
| 250 tokens (Slack/email) | Sonnet 5.5 | $0.28 | $10.19 | $3.36 | $0.64 | $1.60 | $3.19 | +$0.02 |
| 250 tokens | Opus 5.5 | $0.56 | $20.38 | $6.72 | $1.28 | $3.19 | $6.39 | +$0.02 |
| 250 tokens | Haiku 5.5 | $0.01 | $0.51 | $0.19 | $0.03 | $0.08 | $0.16 | +$0.02 |
| 1,500 tokens (proposal section) | Sonnet 5.5 | $0.28 | $25.19 | $18.36 | $2.14 | $5.35 | $10.70 | +$0.08 |
| 1,500 tokens | Opus 5.5 | $0.56 | $50.38 | $36.72 | $4.28 | $10.70 | $21.39 | +$0.08 |
| 1,500 tokens | Haiku 5.5 | $0.01 | $1.26 | $0.94 | $0.11 | $0.27 | $0.53 | +$0.08 |

What the table says:

- **The skill's context costs little once cached.** On Sonnet 5.5, ~3,595 cached tokens cost about $0.36 per 1,000 drafts.
- **The extra pass is what costs money.** Rewrite output is $10 per MTok on Sonnet 5.5 and $20 on Opus 5.5.
- **So "skills are bloat" is mostly about attention and over-correction, not dollars.** The dollars come from running a frontier rewrite on drafts that didn't need one. On these fixtures, 42 of 85 always-rewrite calls (49%) landed on drafts labeled no-rewrite.
- **A Jev gate is close to free.** About $0.08 per 1,000 proposal-sized drafts, and below cached-skill cost even at r=10%.
- **Haiku 5.5 is now a competing gate.** At $0.10 / $0.50, the gate input alone would be about $0.18 per 1,000 drafts at 1,500 tokens, roughly 2x Jev, but it can say *why* a draft failed. It didn't exist when that September post was written.

## 5. Too small or too weak to conclude

- **n < 30 per cell everywhere.** Per category and surface there are 4 to 10 items per split. No system × model × surface cell has any model output at all.
- **The holdout isn't really independent.** The same person wrote the fixtures, the labels, and the rules, so v2's 0.968 holdout F1 is in-distribution. The stress result (0/8) is the more honest number for how v2 does on unseen slop.
- **The ban-list stands in for B's rules, not B itself.** A model running stop-slop applies judgment, so it may over-correct less than the literal ban-list. That needs a model run to measure.
- **A, B rewrite, C rewrite, and D quality are all unmeasured.** That includes meaning preservation, residual slop after rewrite, over-correction rate, and latency.
- **Cost rows use assumed r and assumed rewrite length.** Treat them as orders of magnitude.

## 6. Next run, once a key exists

Use Sonnet 5.5, Opus 5.5, and Haiku 5.5 as generators, run on Batch at 50% off.

1. Freeze 30+ briefs per surface.
2. Generate under A and D, and rewrite under B and C (C gated by v2 plus Jev or Haiku).
3. Score with v2 counts plus a span judge from a different model family, as Arize did with a non-Claude judge.
4. Check meaning preservation by hand: facts, numbers, names, dates, commitments.
5. Rate over-correction on a sample.
6. Report the cheapest stack that meets the quality bar, by model and surface.

## 7. Takeaways

1. **"The 'until Sonnet 5.5' line landed six days later, and Haiku 5.5 a week after that."** So the question has changed from whether to keep the hook to what the hook should be now that the daily model writes cleaner. The answer probably isn't zero: Graphite still counted 2,548 tells in Opus 5.5 on Oct 1, and a later public post still lists stop-slop in the baseline.
2. **"The tells moved; they didn't disappear."** Em dashes and "it's not X, it's Y" are mostly gone. "This matters," "is more than an X, it's a Y," bold lead-in bullets, and padded triads replaced them. My starter regex caught 5 of 13 of those until I added the 5.5 patterns. Any rule-based skill ages with every model release, and Hardik's repo hasn't changed since March.
3. **"Context bloat costs attention and over-correction more than dollars."** Cached, the full skill is about $0.36 per 1,000 Sonnet drafts. The money is in the frontier rewrite pass. A literal reading of the skill's rules flagged 9 of 21 clean drafts and all 17 over-correction traps in my set. A short contract (~139 tokens) plus a gate avoids both.
4. **"Regex is the free floor, and Jev is the right second layer."** My tuned regex gate had no false positives but caught 0 of 8 slop drafts in vocabulary it hadn't seen. Arize's phrase list caught 9 of 153 human flags. These are moves, not phrases, and that's the job a typed classifier is for, at about $0.08 per 1,000 proposal-sized drafts.
5. **"Retire rules on evidence."** That workflow already has a before/after eval set and roughly 0.9 AUC ("AOC" in the public post) on Jev. Rerun it per model release, track the gate fail rate, and remove rules that stop firing. When the fail rate on a surface falls below some bar, drop to contract only for that surface.
6. **Be upfront about the evidence:** "This ran on 85 synthetic fixtures with no model calls. It's directional. The real comparison runs on production before/after pairs." Credit Hardik's MIT repo and the Jev hook.

## Artifacts

- `evals/build_fixtures.py` builds the dev and holdout fixtures. `fixtures/stress/` was written separately.
- `evals/heuristics.py` is the v2 gate plus `stopslop_presence`. `evals/heuristics_v1.py` is the starter gate.
- `evals/run_spike.py` produces `evals/spike_run.json`, which holds all gate metrics by split and category.
- `evals/bloat.json`, `evals/cost_table.md`, and `evals/tables.md` hold the raw numbers.
- `references/patterns.md` gained a section on the 5.5-era residuals, which adds 117 words to that file (343 to 460).
