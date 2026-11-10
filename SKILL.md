---
name: verify-copy
description: Gate and, only if needed, rewrite prose to cut AI slop without bloating context. Use when reviewing or sending customer-facing copy, Slack, email, proposals, workshops, or lessons, or when asked to /verify-copy. Prefer a short style contract plus a cheap prefilter over loading this skill on every draft.
---

# Verify Copy

A thin writing gate, not an always-on style overlay.

Most slop is cheaper to prevent than to clean. Put a short style contract in `CLAUDE.md` or project instructions. Run a cheap prefilter (heuristics, or a calibrated classifier such as TypeSafe Jev) before send. Load this skill and spend a frontier rewrite only when the gate says the draft is at risk.

## When not to run a rewrite

- The prefilter score is at or above the surface threshold, or a later model already follows the style contract (for example Opus 5.5 on customer-facing copy).
- The text is a quotation, a legal clause, a log, or code.
- A rewrite would change a fact, number, commitment, name, or date. If in doubt, report the issue and do not rewrite.

## Two stages

1. **Measure.** Count residual and classic tells with the heuristic checklist in [references/patterns.md](references/patterns.md). Optionally ask a cheap classifier the questions in [hooks/prefilter.md](hooks/prefilter.md). Record surface, model, scores, and whether a rewrite ran.
2. **Rewrite only if needed.** Fix the flagged spans. Keep meaning, claims, and the author's voice. Do not "de-AI" the draft into stiff, adverb-free, em-dash-free prose.

After a rewrite, measure again. If the gate still fails, say what remains rather than looping. Append a before/after pair to the eval set when the rewrite is accepted.

## Style contract (keep this short; this is the customization layer)

Put these lines in the repo, not a large skill:

- Open with the point. No throat-clearing or recap of the question.
- Say things literally. Skip "it's not X, it's Y" unless correcting a real misconception.
- Use as many points as there are. Do not pad to three. Do not turn a short point into headers, bullets, and bold.
- No sign-off offers or "let me know if you'd like me to expand."
- Follow any client or practice style guide when one is provided.

## Rewrite rules (only on a failed gate)

1. Cut throat-clearing, emphasis crutches, and meta-commentary ("Here's the thing," "Let that sink in," "This matters because," "In this section we'll").
2. Flatten "not X, it's Y," punchy one-line paragraph endings, and rhetorical questions answered immediately.
3. Replace vague declaratives with the specific fact. Cut flourish words that are not doing work ("landscape," "unpack," "game-changer," "the real X," "load-bearing").
4. Prefer active voice when the actor matters. Do not ban every passive or every adverb. Flag high rates, not presence.
5. Do not strip every em dash or every sentence that starts with a Wh- word. Those bans make consulting prose worse.
6. For Opus 5.5 and similar: watch leftover verbosity, over-structuring, padded triples, and polite closers more than classic em-dash slop.
7. Match the surface: proposals and workshops stay precise; Slack and email stay short. See [references/patterns.md](references/patterns.md).

## Output

For a review, return:

- Gate: pass or fail, with heuristic counts and any classifier score
- If fail: a rewritten draft, a list of what changed, and a confirmation that claims and numbers are unchanged
- If pass: say so and do not rewrite

## Scoring

Use the checklist counts as the primary, repeatable score. A 1–10 judgment pass (directness, rhythm, trust, authenticity, density) is optional commentary, not the benchmark. The eval protocol lives in [evals/README.md](evals/README.md).
