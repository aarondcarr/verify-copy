# Patterns

Flag rates and clusters, not a single occurrence, unless the phrase is a hard tell.

## Hard tells (usually cut)

- Throat-clearing: "Here's the thing," "Here's what I," "Let me be clear," "The uncomfortable truth is," "It turns out," "The real X is"
- Emphasis crutches: "Let that sink in," "Full stop," "This matters because," "Make no mistake"
- Meta-commentary: "In this section we'll," "As we'll see," "Let me walk you through," "The rest of this document"
- Sign-offs: "Let me know if you'd like me to expand," "Happy to dive deeper," "Hope this helps"

## Residual tells that persist after cleaner models (Opus 5.5 and peers)

- "It's not X, it's Y" / "This isn't X. It's Y." used as a template
- Groups of three that feel padded
- A short point expanded into headers, bullets, and bold
- Opening by restating the ask; closing with a recap
- Flourish: "landscape," "unpack," "navigate," "the real story," "quietly," "load-bearing," "earns its keep"
- Answers that run long after the point is made

## Opus 5.5-era residuals (public measurements, Sep–Oct 2026)

- Salience flags: "this matters," "why X matters," "matters most," "just as important" (Graphite: "this matters" 116x the human rate in Opus 5.5)
- Contrast frames that replaced "it's not X, it's Y": "is more than an X, it's a Y" (98x), "rather than simply" (32x)
- Stock transitions: "looking ahead," "adds another layer," "what comes next"
- Rating words: "dependable" (23x), "steady"
- Structure: more bold lead-in bullets and three-part lists, ~8% longer (Arize, Opus 5 vs 5.5)

These are moves, not fixed phrases. Arize's hand-built phrase list caught 9 of 153 human-flagged Claudisms. Treat the regex gate as a floor and use a classifier for the rest.

## Classic tells (rate, don't auto-ban)

- Em dashes per 100 words (a few are fine; a high rate is a tell)
- Adverbs and softeners: really, just, literally, genuinely, honestly, simply, actually, crucially
- Business jargon: navigate, unpack, lean into, game-changer, deep dive, circle back, moving forward
- Vague declaratives: "The implications are significant," "The reasons are structural," "The stakes are high"
- False agency: "the decision emerges," "the platform wants"

## Surfaces

| Surface | Gate is stricter on | Allow |
|---|---|---|
| Proposal / workshop / lesson | vagueness, jargon, recap, over-structure | precise terms of art, necessary tables |
| Email | throat-clearing, sign-offs, length | a short greeting and one ask |
| Slack | recap, bullets for a one-line point | fragments, informal tone |

## Over-correction (this is also a fail)

A rewrite is worse if it removes every adverb or em dash, forbids Wh- sentence openers, or sounds stiff and clipped. Score over-correction as a defect, not a win.
