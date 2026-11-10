# Cheap prefilter

Run this before a frontier rewrite. The point is to spend almost nothing to decide whether a rewrite is worth it.

## Deterministic first

`evals/heuristics.py` counts hard tells, residual templates, jargon, sign-offs, and rates (em dashes and adverbials per 100 words). Use it in a hook on save or send. It is free, repeatable, and good enough to catch obvious slop.

## Calibrated classifier (Jev or equivalent)

A published consulting workflow used TypeSafe Jev for this layer: unstructured text in, a typed score or classification out, no generated prose. That is the right shape.

Suggested questions against the draft (plus the style contract as context):

- Score 0–1: "Does this read like generic AI-generated professional prose rather than a specific author writing for a specific reader?"
- Noul: "Does the draft open by restating the ask or throat-clearing before the point?"
- Noul: "Does it use an 'it's not X, it's Y' contrast as a template?"
- Noul: "Does it pad a short point into a triad, or into headers and bullets the point does not need?"
- Noul: "Does it end with a recap or an offer to expand?"
- Score 0–1: "Would a rewrite change any fact, number, or commitment?" (if yes, do not auto-rewrite)

Tune thresholds on the eval fixtures, by surface and by model. A gate that is cheap and slightly conservative is better than always calling Sonnet or Opus.

## Routing

- High-volume daily drafts on a cheaper model (for example Sonnet): always prefilter; rewrite only on fail.
- Customer-facing copy on a model that already follows a short style contract (Opus 5.5 class): prefilter only; skip the skill and the rewrite on pass.
- Retire rules that stop firing after a model upgrade. That is how a style contract plus a gate stays cheaper than a growing skill.
