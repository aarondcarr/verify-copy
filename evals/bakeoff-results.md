# Model bakeoff: four anti-slop systems on Haiku 5.5, Sonnet 5.5, and Opus 5.5

Run Monday, Nov 9, 2026, about 4:55 to 5:10 PM CT, on Grok Bot's box. Every number below comes from a real Anthropic API response saved in `evals/bakeoff/`. No outputs or scores were made up. The fixtures are the same synthetic, single-author set as the [heuristic-only spike](spike-results.md), so read the absolute numbers as optimistic.

## Bottom line

1. **Winner: Sonnet 5.5 behind the verify-copy gate (system 4b: v2 regex, then a one-word Haiku 5.5 check, then a skill-loaded rewrite only on fail).** On holdout it tied the always-on skill on quality. Both judges agreed 10 of 16 slop drafts were fixed with meaning kept, for both systems. It touched **0 of 22** clean drafts across both splits. At this set's 47% slop rate it cost **$2.87 per 1,000 drafts versus $5.16** for always-on, and it gets cheaper as the real fail rate drops. On the hard cases it caught 8 of 8.
2. **Best value: Haiku 5.5 with the same gate, at $0.20 per 1,000 drafts**, about 14x cheaper than Sonnet. It also touched 0 of 22 clean drafts. It fixed 8 of 16 holdout slop drafts (both judges) versus Sonnet's 10. On the hard cases it fixed only 2 of 8, versus Sonnet's 4. Haiku is a good gate and a weaker rewriter.
3. **The regex gate alone is not enough.** v2 caught 15 of 16 holdout slop drafts but **0 of 8** hard cases. That repeats the earlier spike. Adding the one-word Haiku check fixed it: 16/16 and 8/8, with 0 false positives, for about $0.06 per 1,000 drafts.
4. **Model defaults don't police slop.** Asked to make a draft "ready to send," Sonnet 5.5 returned **8 of 16** holdout slop drafts unchanged. Residual slop on holdout was 14–15 of 16 by judge for both Haiku and Sonnet defaults, and 9–10 of 16 for Opus.
5. **Over-correction showed up only where Haiku had no skill.** Haiku default and Haiku with the contract only added content to clean copy or dropped it. Examples: an invented access request, a dropped quote of the client's deadline, "last month" turned into "before this workshop." The skill and the gate both brought Haiku's harm on clean drafts to 0. Sonnet and Opus harmed at most 1 of 18 holdout clean drafts in any system.
6. **Opus 5.5 got the best quality numbers but costs about twice Sonnet.** With the gate it fixed 11 of 16 holdout and 6 of 8 hard cases (both judges). With the always-on skill it fixed 12 of 16. The gap over Sonnet is 1–2 drafts on holdout and 2 on hard cases. That's suggestive at this n, not proven.
7. **Total spend: $7.49 of the $200 Ultra promotional credit.** That includes $2.23 for final generations, $4.29 for the two judges, $0.54 for the tune-set sanity check, and $0.43 for a discarded run. These figures are API usage times list price. The Console's balance may lag or round differently.

## Methods

**Models (official IDs, confirmed with `GET /v1/models` on this key):** `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`. Prices are from [platform.claude.com pricing](https://platform.claude.com/docs/en/about-claude/pricing) on Nov 9: Haiku $0.10/$0.50, Sonnet $2/$10, Opus $4/$20 per MTok input/output. There was no caching and no batch, and temperature was left at the API default. Each cell is **one sample per draft**, so there is run-to-run noise. Systems 4 and 4b send the same rewrite prompt on the same drafts, and their outputs still differed.

**Fixtures (checked against the files, which match the spike):**
- Tune (`fixtures/dev`): 39 drafts (19 slop / 20 clean). Used only for a prompt sanity check (`bakeoff/dev_sanity.jsonl`). No numbers are reported from it.
- Holdout (`fixtures/holdout`): 34 drafts. 16 slop (6 classic, 6 Opus-5.5-style residual, 4 structural) and 18 clean (10 clean plus 8 over-correction traps: a precise em dash, a plain "just," sincere "really," a lesson's real Wh- question, a real limitation stated as a negation, a hard tell inside a client quote, a fine passive, and an "actually" marking real disagreement).
- Hard cases (`fixtures/stress`, written after v2 was frozen): 12 drafts. 8 are slop in vocabulary outside the v2 lists. 4 are long clean drafts over 80 words.

**Task (identical user prompt for every system):** "Here is a draft {surface} message. Edit it so it is ready to send. If it is already ready to send, return it exactly as written." The answer goes inside `<final>` tags, and all 690 outputs used the tags.

| System | System prompt | Model calls |
|---|---|---|
| 1 Model default | none | every draft |
| 2 Style contract | the 5-line contract from SKILL.md (measured **+145 input tokens** per call) | every draft |
| 3 Always-on skill | verify-copy SKILL.md body, without `references/patterns.md`, which the skill loads on demand (measured **+1,228 input tokens** per call) | every draft |
| 4 Gate (v2 regex) | `heuristics.py` v2 runs first. On fail, rewrite with system 3's prompt. On pass, keep the draft unchanged. | failed drafts only |
| 4b Gate (v2 + Haiku) | as 4, but a draft that passes v2 also gets a one-word Haiku 5.5 REWRITE/PASS check built from `hooks/prefilter.md` and the contract (about 450 input tokens). It fails closed on an empty reply. | Haiku on v2 passes; rewrite on any fail |

Prompts are in `bakeoff/run_bakeoff.py`. I didn't change SKILL.md or heuristics.py.

**Scoring:**
- *Rewrite decision (P/R/F1):* the prediction is "the output differs from the draft after whitespace normalization" and the label is `should_rewrite`. This is well defined for every system. For 4 and 4b I also report the gate's own P/R/F1. I don't put an F1 on rewrite quality.
- *Residual slop on slop drafts:* (a) whether the v2 heuristics still fail the output; (b) a blind judge verdict from Opus 5.5 and, separately, Sonnet 5.5. The judges never saw the system, the model, or the label. v2 is blind to the hard-case vocabulary by construction, so on hard cases only the judge columns mean anything.
- *Slop fixed AND meaning kept (both judges):* the headline quality number. The output counts only if both judges call it slop-free and both say facts, numbers, names, dates, commitments, and intent are kept. I added this because the cheapest way to "fix" vacuous slop is to invent specifics. Sonnet's contract-only edit added "cut the time you spend on manual work" to a draft that never said that.
- *Over-correction:* "clean drafts touched" counts any change. "Harmed" means a changed clean draft that a judge rated worse, over-flattened, or meaning-changed, or that newly fails v2.
- *Meaning preservation:* (a) both judges on every changed output (337 unique changed outputs); (b) a deterministic check that every number in the draft survives, which found **0 drops in all 690 outputs**; (c) my own read of every changed clean output (25) and every slop output for Sonnet systems 1–3 and 4b and Haiku 4b (about 120). Grok Bot did that read, not a human. Aaron should spot-check before quoting it.
- *Judge sanity:* on the original drafts, the Sonnet judge matched the hand labels 34/34 on holdout and 12/12 on hard cases. The Opus judge matched 33/34 and 12/12. The judges agreed on the slop verdict for 635 of 690 outputs and on the meaning verdict for 295 of 337 changed outputs. The Opus judge is more lenient, especially on hard cases. Opus also judged its own outputs, so I report both judges throughout.

## Results

### Headline (holdout, n=34; hard cases, n=12)

| Model | System | Holdout: slop fixed + meaning kept (both judges) | Holdout: clean touched / harmed (my read) | Hard: slop fixed + meaning kept (both judges) | Hard: clean touched | Cost / 1k drafts, holdout mix (extrapolated) |
|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 default | 1/16 | 5/18 / 2 | 0/8 | 2/4 | $0.17 |
| Haiku 5.5 | 2 contract | 7/16 | 6/18 / 3 | 1/8 | 3/4 | $0.20 |
| Haiku 5.5 | 3 always-on skill | 7/16 | 0/18 / 0 | 2/8 | 0/4 | $0.28 |
| Haiku 5.5 | 4 gate (v2) | 6/16 | 0/18 / 0 | 0/8 (gate missed all) | 0/4 | $0.14 |
| Haiku 5.5 | **4b gate (v2 + Haiku)** | **8/16** | **0/18 / 0** | 2/8 | 0/4 | **$0.20** |
| Sonnet 5.5 | 1 default | 1/16 | 1/18 / 0 | 1/8 | 0/4 | $1.70 |
| Sonnet 5.5 | 2 contract | 8/16 | 1/18 / 0 | 3/8 | 0/4 | $2.31 |
| Sonnet 5.5 | 3 always-on skill | 10/16 | 1/18 / 1 | 2/8 | 0/4 | $5.16 |
| Sonnet 5.5 | 4 gate (v2) | 10/16 | 0/18 / 0 | 0/8 (gate missed all) | 0/4 | $2.84 |
| Sonnet 5.5 | **4b gate (v2 + Haiku)** | **10/16** | **0/18 / 0** | **4/8** | **0/4** | **$2.87** |
| Opus 5.5 | 1 default | 5/16 | 2/18 / 0 | 1/8 | 0/4 | $4.71 |
| Opus 5.5 | 2 contract | 9/16 | 3/18 / 1 | 3/8 | 0/4 | $5.15 |
| Opus 5.5 | 3 always-on skill | 12/16 | 1/18 / 1 | 3/8 | 0/4 | $10.87 |
| Opus 5.5 | 4 gate (v2) | 9/16 | 0/18 / 0 | 0/8 (gate missed all) | 0/4 | $5.53 |
| Opus 5.5 | 4b gate (v2 + Haiku) | 11/16 | 0/18 / 0 | 6/8 | 0/4 | $5.62 |

The "harmed (my read)" column counts changes that altered or dropped a detail, or that undid an over-correction trap. Neutral punctuation or capitalization edits don't count. The harmful holdout edits were:
- **Haiku default:** added "a lot of time and money" to a Slack thanks; changed "last month" to "earlier" and "are out of date" to "may be."
- **Haiku contract:** dropped the client's quoted no-extension line; turned the lesson's real Wh- question into a statement; changed "last month" to "before this workshop."
- **Sonnet skill, Opus contract, and Opus skill:** each turned the lesson's "Why does the model ignore a rule…?" opener into a statement. That is exactly the trap the fixture was written for.

On the hard cases, Haiku default and Haiku contract each harmed 2 of 4 long clean drafts. They added an access request and a pre-commit-script option, dropped the author's offer to draft a note, and named a hook type the author hadn't specified. The judge-based harm counts in the full tables agree within one item.

### Full tables

The tables below are generated from `bakeoff/scores.json` by `bakeoff/tables.py`.


### Holdout (n=34: 16 slop, 18 clean incl. 8 over-correction traps)

| Model | System | Slop drafts rewritten | Clean drafts touched | Rewrite-decision P / R / F1 | Residual slop: v2 | Residual slop: Opus judge | Residual slop: Sonnet judge | Slop fixed AND meaning kept (both judges) | Clean drafts harmed (Opus / Sonnet judge) | Meaning kept on changed outputs (Opus / Sonnet judge) | Cost (USD) | Cost per 1k drafts (extrapolated) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 Model default | 11/16 | 5/18 | 0.69 / 0.69 / 0.69 | 13/16 | 14/16 | 15/16 | 1/16 | 2/18 / 3/18 | 10/16 / 9/16 | $0.0058 | $0.17 |
| Haiku 5.5 | 2 Style contract | 16/16 | 6/18 | 0.73 / 1.00 / 0.84 | 6/16 | 5/16 | 5/16 | 7/16 | 2/18 / 2/18 | 14/22 / 16/22 | $0.0069 | $0.20 |
| Haiku 5.5 | 3 Always-on skill | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 5/16 | 4/16 | 8/16 | 7/16 | 0/18 / 0/18 | 14/15 / 12/15 | $0.0095 | $0.28 |
| Haiku 5.5 | 4 Gate (v2 regex) | 14/16 | 0/18 | 1.00 / 0.88 / 0.93 | 5/16 | 5/16 | 7/16 | 6/16 | 0/18 / 0/18 | 11/14 / 11/14 | $0.0049 | $0.14 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 5/16 | 4/16 | 7/16 | 8/16 | 0/18 / 0/18 | 15/15 / 14/15 | $0.0067 | $0.20 |
| Sonnet 5.5 | 1 Model default | 8/16 | 1/18 | 0.89 / 0.50 / 0.64 | 13/16 | 14/16 | 15/16 | 1/16 | 1/18 / 0/18 | 9/9 / 8/9 | $0.0578 | $1.70 |
| Sonnet 5.5 | 2 Style contract | 16/16 | 1/18 | 0.94 / 1.00 / 0.97 | 6/16 | 5/16 | 5/16 | 8/16 | 0/18 / 0/18 | 14/17 / 15/17 | $0.0786 | $2.31 |
| Sonnet 5.5 | 3 Always-on skill | 16/16 | 1/18 | 0.94 / 1.00 / 0.97 | 3/16 | 4/16 | 5/16 | 10/16 | 0/18 / 1/18 | 17/17 / 16/17 | $0.1753 | $5.16 |
| Sonnet 5.5 | 4 Gate (v2 regex) | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 2/16 | 4/16 | 5/16 | 10/16 | 0/18 / 0/18 | 15/15 / 13/15 | $0.0964 | $2.84 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | 16/16 | 0/18 | 1.00 / 1.00 / 1.00 | 3/16 | 5/16 | 6/16 | 10/16 | 0/18 / 0/18 | 15/16 / 15/16 | $0.0975 | $2.87 |
| Opus 5.5 | 1 Model default | 14/16 | 2/18 | 0.88 / 0.88 / 0.88 | 8/16 | 9/16 | 10/16 | 5/16 | 0/18 / 0/18 | 14/16 / 16/16 | $0.1602 | $4.71 |
| Opus 5.5 | 2 Style contract | 16/16 | 3/18 | 0.84 / 1.00 / 0.91 | 2/16 | 3/16 | 5/16 | 9/16 | 0/18 / 2/18 | 19/19 / 16/19 | $0.1750 | $5.15 |
| Opus 5.5 | 3 Always-on skill | 16/16 | 1/18 | 0.94 / 1.00 / 0.97 | 2/16 | 1/16 | 4/16 | 12/16 | 0/18 / 1/18 | 17/17 / 15/17 | $0.3695 | $10.87 |
| Opus 5.5 | 4 Gate (v2 regex) | 15/16 | 0/18 | 1.00 / 0.94 / 0.97 | 3/16 | 4/16 | 6/16 | 9/16 | 0/18 / 0/18 | 15/15 / 14/15 | $0.1879 | $5.53 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | 16/16 | 0/18 | 1.00 / 1.00 / 1.00 | 2/16 | 2/16 | 4/16 | 11/16 | 0/18 / 0/18 | 16/16 / 14/16 | $0.1910 | $5.62 |

### Hard cases (n=12: 8 unseen-vocabulary slop, 4 long clean)

| Model | System | Slop drafts rewritten | Clean drafts touched | Rewrite-decision P / R / F1 | Residual slop: v2 | Residual slop: Opus judge | Residual slop: Sonnet judge | Slop fixed AND meaning kept (both judges) | Clean drafts harmed (Opus / Sonnet judge) | Meaning kept on changed outputs (Opus / Sonnet judge) | Cost (USD) | Cost per 1k drafts (extrapolated) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 Model default | 6/8 | 2/4 | 0.75 / 0.75 / 0.75 | 0/8 | 6/8 | 7/8 | 0/8 | 2/4 / 2/4 | 4/8 / 5/8 | $0.0029 | $0.24 |
| Haiku 5.5 | 2 Style contract | 8/8 | 3/4 | 0.73 / 1.00 / 0.84 | 0/8 | 2/8 | 5/8 | 1/8 | 2/4 / 2/4 | 7/11 / 7/11 | $0.0030 | $0.25 |
| Haiku 5.5 | 3 Always-on skill | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 1/8 | 4/8 | 2/8 | 0/4 / 0/4 | 6/8 / 6/8 | $0.0039 | $0.32 |
| Haiku 5.5 | 4 Gate (v2 regex) | 0/8 | 0/4 | n/a / 0.00 / n/a | 0/8 | 8/8 | 8/8 | 0/8 | 0/4 / 0/4 | n/a / n/a | $0.0000 | $0.00 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 4/8 | 4/8 | 2/8 | 0/4 / 0/4 | 6/8 / 6/8 | $0.0032 | $0.26 |
| Sonnet 5.5 | 1 Model default | 7/8 | 0/4 | 1.00 / 0.88 / 0.93 | 0/8 | 6/8 | 6/8 | 1/8 | 0/4 / 0/4 | 6/7 / 6/7 | $0.0311 | $2.59 |
| Sonnet 5.5 | 2 Style contract | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 0/8 | 4/8 | 3/8 | 0/4 / 0/4 | 7/8 / 8/8 | $0.0378 | $3.15 |
| Sonnet 5.5 | 3 Always-on skill | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 4/8 | 5/8 | 2/8 | 0/4 / 0/4 | 8/8 / 7/8 | $0.0718 | $5.98 |
| Sonnet 5.5 | 4 Gate (v2 regex) | 0/8 | 0/4 | n/a / 0.00 / n/a | 0/8 | 8/8 | 8/8 | 0/8 | 0/4 / 0/4 | n/a / n/a | $0.0000 | $0.00 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 2/8 | 4/8 | 4/8 | 0/4 / 0/4 | 8/8 / 8/8 | $0.0490 | $4.08 |
| Opus 5.5 | 1 Model default | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 5/8 | 5/8 | 1/8 | 0/4 / 0/4 | 6/8 / 7/8 | $0.0722 | $6.02 |
| Opus 5.5 | 2 Style contract | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 1/8 | 5/8 | 3/8 | 0/4 / 0/4 | 8/8 / 8/8 | $0.0749 | $6.24 |
| Opus 5.5 | 3 Always-on skill | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 3/8 | 5/8 | 3/8 | 0/4 / 0/4 | 8/8 / 7/8 | $0.1523 | $12.69 |
| Opus 5.5 | 4 Gate (v2 regex) | 0/8 | 0/4 | n/a / 0.00 / n/a | 0/8 | 8/8 | 8/8 | 0/8 | 0/4 / 0/4 | n/a / n/a | $0.0000 | $0.00 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | 8/8 | 0/4 | 1.00 / 1.00 / 1.00 | 0/8 | 2/8 | 2/8 | 6/8 | 0/4 / 0/4 | 8/8 / 8/8 | $0.1004 | $8.36 |

### Gate classification (should this draft be rewritten?)

| Gate | Split | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| 4 Gate (v2 regex) (Haiku 5.5 run) | holdout | 15 | 0 | 1 | 18 | 1.00 | 0.94 | 0.97 |
| 4 Gate (v2 regex) (Haiku 5.5 run) | stress | 0 | 0 | 8 | 4 | n/a | 0.00 | n/a |
| 4 Gate (v2 regex) (Sonnet 5.5 run) | holdout | 15 | 0 | 1 | 18 | 1.00 | 0.94 | 0.97 |
| 4 Gate (v2 regex) (Sonnet 5.5 run) | stress | 0 | 0 | 8 | 4 | n/a | 0.00 | n/a |
| 4 Gate (v2 regex) (Opus 5.5 run) | holdout | 15 | 0 | 1 | 18 | 1.00 | 0.94 | 0.97 |
| 4 Gate (v2 regex) (Opus 5.5 run) | stress | 0 | 0 | 8 | 4 | n/a | 0.00 | n/a |
| 4b Gate (v2 + Haiku) (Haiku 5.5 run) | holdout | 16 | 0 | 0 | 18 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Haiku 5.5 run) | stress | 8 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Sonnet 5.5 run) | holdout | 16 | 0 | 0 | 18 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Sonnet 5.5 run) | stress | 8 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Opus 5.5 run) | holdout | 16 | 0 | 0 | 18 | 1.00 | 1.00 | 1.00 |
| 4b Gate (v2 + Haiku) (Opus 5.5 run) | stress | 8 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 |

### Tokens and per-call cost

| Model | System | Split | Model calls | Haiku gate calls | Input tokens | Output tokens | Mean cost per rewrite call | Mean latency per draft (s) |
|---|---|---|---|---|---|---|---|---|
| Haiku 5.5 | 1 Model default | holdout | 34 | 0 | 4,649 | 10,618 | $0.00017 | 1.8 |
| Haiku 5.5 | 1 Model default | stress | 12 | 0 | 2,029 | 5,404 | $0.00024 | 2.5 |
| Haiku 5.5 | 2 Style contract | holdout | 34 | 0 | 9,579 | 11,885 | $0.00020 | 2.1 |
| Haiku 5.5 | 2 Style contract | stress | 12 | 0 | 3,769 | 5,346 | $0.00025 | 2.6 |
| Haiku 5.5 | 3 Always-on skill | holdout | 34 | 0 | 46,401 | 9,666 | $0.00028 | 1.9 |
| Haiku 5.5 | 3 Always-on skill | stress | 12 | 0 | 16,765 | 4,387 | $0.00032 | 2.2 |
| Haiku 5.5 | 4 Gate (v2 regex) | holdout | 15 | 0 | 20,496 | 5,693 | $0.00033 | 1.1 |
| Haiku 5.5 | 4 Gate (v2 regex) | stress | 0 | 0 | 0 | 0 | $0.00000 | 0.0 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | holdout | 16 | 19 | 30,111 | 7,297 | $0.00036 | 1.3 |
| Haiku 5.5 | 4b Gate (v2 + Haiku) | stress | 8 | 12 | 16,532 | 3,030 | $0.00030 | 1.3 |
| Sonnet 5.5 | 1 Model default | holdout | 34 | 0 | 4,649 | 4,847 | $0.00170 | 1.7 |
| Sonnet 5.5 | 1 Model default | stress | 12 | 0 | 2,029 | 2,706 | $0.00259 | 2.3 |
| Sonnet 5.5 | 2 Style contract | holdout | 34 | 0 | 9,579 | 5,945 | $0.00231 | 1.9 |
| Sonnet 5.5 | 2 Style contract | stress | 12 | 0 | 3,769 | 3,026 | $0.00315 | 2.3 |
| Sonnet 5.5 | 3 Always-on skill | holdout | 34 | 0 | 46,401 | 8,249 | $0.00516 | 2.3 |
| Sonnet 5.5 | 3 Always-on skill | stress | 12 | 0 | 16,765 | 3,829 | $0.00598 | 2.8 |
| Sonnet 5.5 | 4 Gate (v2 regex) | holdout | 15 | 0 | 20,496 | 5,545 | $0.00643 | 1.4 |
| Sonnet 5.5 | 4 Gate (v2 regex) | stress | 0 | 0 | 0 | 0 | $0.00000 | 0.0 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | holdout | 16 | 19 | 30,111 | 5,674 | $0.00603 | 1.4 |
| Sonnet 5.5 | 4b Gate (v2 + Haiku) | stress | 8 | 12 | 16,532 | 3,044 | $0.00602 | 2.1 |
| Opus 5.5 | 1 Model default | holdout | 34 | 0 | 4,649 | 7,082 | $0.00471 | 2.6 |
| Opus 5.5 | 1 Model default | stress | 12 | 0 | 2,029 | 3,204 | $0.00602 | 3.1 |
| Opus 5.5 | 2 Style contract | holdout | 34 | 0 | 9,579 | 6,832 | $0.00515 | 2.5 |
| Opus 5.5 | 2 Style contract | stress | 12 | 0 | 3,769 | 2,991 | $0.00624 | 2.9 |
| Opus 5.5 | 3 Always-on skill | holdout | 34 | 0 | 46,401 | 9,193 | $0.01087 | 3.3 |
| Opus 5.5 | 3 Always-on skill | stress | 12 | 0 | 16,765 | 4,261 | $0.01269 | 4.4 |
| Opus 5.5 | 4 Gate (v2 regex) | holdout | 15 | 0 | 20,496 | 5,296 | $0.01253 | 1.8 |
| Opus 5.5 | 4 Gate (v2 regex) | stress | 0 | 0 | 0 | 0 | $0.00000 | 0.0 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | holdout | 16 | 19 | 30,111 | 5,508 | $0.01187 | 1.6 |
| Opus 5.5 | 4b Gate (v2 + Haiku) | stress | 8 | 12 | 16,532 | 3,228 | $0.01245 | 2.7 |

### Judge calibration on the original drafts (judge's slop verdict vs. the hand label)

| Judge | Split | TP | FP | FN | TN |
|---|---|---|---|---|---|
| Opus 5.5 | holdout | 15 | 0 | 1 | 18 |
| Opus 5.5 | stress | 8 | 0 | 0 | 4 |
| Sonnet 5.5 | holdout | 16 | 0 | 0 | 18 |
| Sonnet 5.5 | stress | 8 | 0 | 0 | 4 |

Judge agreement: slop verdict 635/690 outputs; meaning verdict 295/337 changed outputs.

### Actual spend (from API usage fields x list prices)

| Stage | API calls | Input tokens | Output tokens | Cost (USD) |
|---|---|---|---|---|
| Prompt sanity check on tune set (dev, 39 drafts; not reported) | 312 | 209,684 | 80,868 | $0.54 |
| Bakeoff generations, holdout + hard cases (final) | 624 | 450,993 | 153,786 | $2.23 |
| System 4b first run (discarded: gate max_tokens bug) | 158 | 130,424 | 25,189 | $0.43 |
| Opus 5.5 judge (incl. 95 truncated replies re-run) | 478 | 286,376 | 118,774 | $3.52 |
| Sonnet 5.5 judge | 383 | 225,927 | 31,768 | $0.77 |
| **Total** | **1,955** | **1,303,404** | **410,385** | **$7.49** |

## Cost extrapolations (labeled; not measured at these rates)

The measured per-call costs are in the token table above. For the gate, cost per 1,000 drafts ≈ 1,000 × (r × rewrite call cost + Haiku gate cost). Here r is the share of drafts that fail the gate. The measured Haiku gate call averaged **$0.000057** (447 input and 24 output tokens), which adds about $0.06 per 1,000 drafts.

| Model | Always-on skill (every draft, uncached) | Contract-only edit pass (every draft) | Gate 4b at r=10% | r=25% | r=47% (this holdout, measured) |
|---|---|---|---|---|---|
| Haiku 5.5 | $0.28 | $0.20 | ~$0.09 | ~$0.14 | $0.20 |
| Sonnet 5.5 | $5.16 | $2.31 | ~$0.66 | ~$1.56 | $2.87 |
| Opus 5.5 | $10.87 | $5.15 | ~$1.30 | ~$3.10 | $5.62 |

Caching the 1,228-token skill would lower the always-on column. Under Sonnet 5.5's 5% cache-read price that input would cost about $0.12 per 1,000 instead of $2.46, though the output tokens would stay. The gate's advantage comes mainly from skipping calls on clean drafts, not from context size. Against a contract-only edit pass, the gate breaks even at r ≈ 38% on Sonnet. Below that fail rate, the gate is cheaper.

## Caveats (read before quoting)

- **Same author wrote the drafts, the labels, the traps, and the v2 rules,** and v2 was tuned on the same author's dev split. The gate's 0 false positives and the Haiku check's perfect 24/24 on slop are in-distribution. Expect lower numbers on real consulting drafts.
- **Small n.** There are 16 slop and 18 clean drafts on holdout and 8 and 4 on hard cases. Differences of 1–2 drafts (Sonnet 4b vs. 3, Opus vs. Sonnet) are within noise. There is one sample per cell, and repeat runs of the same prompt differed.
- **Systems 1–3 were tested as an edit pass on finished drafts.** They were not tested as generation-time instructions. In production, a style contract mostly works by preventing slop while the draft is written, and this run doesn't measure that. Contract-only results here understate it as a prevention layer.
- **"Fixing" vacuous slop is ill-posed.** Many slop fixtures, especially the hard cases, have no facts to keep ("Our robust, seamless solution…"). A system can only (a) cut the draft down to a thin true sentence, which judges often still call vague, or (b) invent specifics, which judges flag as a meaning change. For these drafts, the skill's own rule ("if in doubt, report the issue and do not rewrite") is probably the right behavior, and no system was scored on it.
- **LLM judges.** The judges come from the same family as the generators, and Opus judged its own outputs. I mitigated this with two judges, blind prompts, and both-judges-agree headline numbers. The Sonnet judge was stricter. A non-Claude judge, as Arize used, would be better.
- **Bug found and fixed during the run.** The Haiku gate first ran with `max_tokens=8`. On 14 of 93 calls it returned empty text, which the code counted as PASS, so 4b missed two or three slop drafts per model. I raised the limit to 256, made the gate fail closed on empty replies, and reran all 4b cells. The bad run is kept in `bakeoff/raw_outputs_S4b_firstrun_gate_truncated.jsonl` and is not used in any table. Separately, 95 Opus judge replies were cut off at 300 tokens and were re-run at 1,500 tokens, so their cost is included twice.
- **Latency** is wall-clock time from the box with 6 parallel workers. Treat it as rough.

## Takeaways

1. **"I ran it for real: three 5.5 models, four systems, 46 held-out drafts, $7.49 total."** On my synthetic set the gate held quality and cut cost: Sonnet 5.5 behind a gate matched the always-on skill on holdout (10 of 16 fixed with meaning kept, both judges). It never touched a clean draft (0 of 22). It cost $2.87 per 1,000 drafts versus $5.16, and that gap widens as the fail rate drops.
2. **"Regex is still the free floor, and Haiku 5.5 is the second layer, replacing Jev in my test."** v2 alone caught 0 of 8 hard-case slop drafts. A one-word Haiku check fixed that, with 24 of 24 slop caught and 0 of 22 clean flagged, for about $0.06 per 1,000 drafts. The open question is whether that workflow's unpublished eval, reported at ~0.9 AUC, beats this at a similar price.
3. **"Model defaults don't self-police."** Asked to make drafts ready to send, Sonnet 5.5 left half the slop drafts untouched, and residual slop stayed at 14–15 of 16. So "Sonnet 5.5 writes cleaner" doesn't mean an edit pass will clean up someone else's slop. You still need a gate or a contract.
4. **"Over-correction is a cheap-model problem."** Haiku without the skill invented content in clean copy and dropped a quoted client deadline. Loading the skill, or gating so clean drafts never reach the rewriter, took Haiku's harm to 0. Sonnet and Opus mostly over-corrected one trap: they rewrote a lesson's real "Why…?" question.
5. **"For vacuous slop, the right move is to flag it, not rewrite it."** Every system either kept vague claims or invented specifics on the buzzword drafts. That argues for the skill's "report, don't rewrite" rule and for a gate that returns a reason.
6. **Be upfront:** "Synthetic, single-author fixtures, one sample per cell, LLM judges from the same family. It's directional. The real comparison is on your before/after set."

## Artifacts (all under `evals/bakeoff/`, no key material)

- `run_bakeoff.py`: the runner (prompts, systems, cost accounting, and a stop on auth, credit, or rate-limit errors; none occurred).
- `judge.py`: the blind judge. `score.py` does the scoring. `tables.py` renders the tables and the spend.
- `raw_outputs.jsonl`: 690 final outputs, 46 drafts × 5 systems × 3 models, with usage, cost, and latency.
- `judgments_claude-opus-5-5.jsonl`, `judgments_claude-sonnet-5-5.jsonl`: raw judge replies.
- `scores.json`, `per_item_scored.json`, `tables.md`: the computed metrics.
- `dev_sanity.jsonl`: tune-set prompt check. `raw_outputs_S4b_firstrun_gate_truncated.jsonl`: the discarded buggy run.
