# verify-copy

A cheaper alternative to an always-on anti-slop skill. This repo is a bakeoff: can a cheap gate plus a thin rewrite skill beat loading a large writing skill on every draft, and match a consulting workflow that uses a style contract, an always-on skill, and a typed classifier hook? MIT licensed, inspired by [Hardik Pandya's stop-slop](https://github.com/hardikpandya/stop-slop), not a copy of that repo.

Hardik's public record: SVP Design, Research & Taste at Pocket FM (Bengaluru); previously Atlassian and Google. A consulting practice may have extended the public skill; they have not published a fork.

## The spike: are skills bloat?

Yes, if you load a large writing skill on every draft. Skills consume context, cost tokens, and invite over-correction (ban all adverbs, strip every em dash, forbid Wh- openers). That is a worse failure than leftover slop in consulting prose.

A published consulting workflow already ran a version of this experiment:

- They had writing guidelines and still got slop on Claude 5. A customization alone was not enough on that model.
- They added a stop-slop skill and ran a high-powered model over large documents. That works, and it is expensive.
- They put TypeSafe Jev on a hook as a cheap typed classifier so they were not generating a second full draft every time.
- Opus 5.5 (model release, not a Claude skill) started following the guidelines and reduced default slop, which made the always-on skill and the hook "somewhat obsolete" for that model.
- They still run Sonnet daily, so a cheap gate remains useful until the daily model catches up.

The real question is not "which skill is better." It is: **what is the cheapest stack that keeps copy at an agreed quality bar?**

The stack this repo argues for:

1. A short **style contract** in `CLAUDE.md` or project instructions (the customization layer).
2. A **cheap prefilter**: deterministic heuristics first, a calibrated classifier (Jev or equivalent) if you need recall on residual patterns.
3. A **frontier rewrite only on a failed gate**, using a thin skill that knows residual 5.5 tells and refuses to over-correct.
4. **Retire rules** that stop firing after a model upgrade, so the skill does not grow into bloat.

If the style contract plus a better default model already passes the eval, skip the skill. That is a successful result, not a failed skill.

## What is in here

- [SKILL.md](SKILL.md) — thin skill for the rewrite path
- [references/patterns.md](references/patterns.md) — residual vs classic tells; over-correction is a fail
- [hooks/prefilter.md](hooks/prefilter.md) — routing and the Jev-shaped classifier
- [evals/](evals/) — protocol, `heuristics.py`, fixtures, bakeoff and gate results

## Starter eval (honest, small)

`python3 evals/heuristics.py evals/fixtures` on the five starter fixtures, after a fix: first run false-positived a 20-word "over-correction trap" because one adverb and one em dash look loud per 100 words. The gate now ignores rate caps under 80 words and still flags hard tells, residual templates, sign-offs, and jargon clusters.

On n=5: 3 TP, 2 TN, 0 FP, 0 FN. That is too small to conclude anything. Next step is a holdout of at least 30 per cell (model × surface), plus cost and over-correction, comparing four systems: style contract only, always-on skill, verify-copy, and model default.

## Notes

- Credit Hardik and the public skill. Don't imply he works at the consulting practice that adopted a similar workflow.
- The Jev hook is the right shape: cheapest decision, typed output, no generated prose.
- Skills are a tool, not the product. The product is a measured quality bar at the lowest cost.
- This bakeoff is on synthetic fixtures. It is not a claim that the stack already beats production.
- If the question is what "killed" an always-on stop-slop skill: not another skill. A model that finally followed a short style contract, plus a hook that made the expensive pass optional.
