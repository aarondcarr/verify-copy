# Similar tests (paired before/after)

This folder is a **look-alike** eval, not a reconstruction of anyone's unpublished set.

A published consulting workflow said their Jev gate was tuned on before/after pairs from past `/stop-slop` runs. Their drafts, questions, threshold, and set size were never posted. The pairs here copy that *shape* (a sloppy before and a cleaned after, same item) from sources we can actually cite.

Do not report numbers on this folder as a reproduction of that workflow's ~0.9 score.

## What's in here

- `stop-slop-examples.json` — 5 public before/after pairs (10 items) copied verbatim from [Hardik Pandya's stop-slop examples](https://github.com/hardikpandya/stop-slop/blob/HEAD/references/examples.md). MIT licensed; copyright (c) 2025 Hardik Pandya. These are his demo pairs, not customer drafts.
- `bakeoff-rewrite-pairs.json` — 12 pairs (24 items) from this repo's own bakeoff. For each one, the before is a synthetic slop draft on holdout or stress, and the after is the Sonnet 5.5 + regex/Haiku (4b) rewrite. Included only when both LLM judges said meaning was kept and slop was gone, no numbers were dropped, the rewrite was not marked over-flattened, and the regex gate also passed on the after. `needs_human_check` is true on every one of these.

Of 24 Sonnet 5.5 + 4b slop drafts on holdout+stress, 12 met that bar. Left out: 8 still judged sloppy, 2 failed meaning preservation, 1 over-flattened, 1 still failed regex after the rewrite.

## How to read a row

Same fields as the other fixtures, plus `pair_id`, `role` (`before` or `after`), `source`, and `needs_human_check`. `split` is always `similar` so these are not mixed into the original holdout. `should_rewrite` is true on befores and false on afters.

## How to run

```bash
python3 evals/heuristics.py evals/fixtures/similar
```

That scores the regex gate only. A later Jev or 4b pass can use the same files.

## Still missing versus the published design

- Real customer proposals, lessons, workshops, Slack, and email
- Long documents (these afters are still short)
- A human pass on the bakeoff afters
- Their Jev questions and threshold
