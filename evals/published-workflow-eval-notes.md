# A published Jev slop-gate eval: what is public, and a documented reconstruction

_Research done Nov 9, 2026 (CT) from public web sources only. Nobody from that workflow was contacted. No items or numbers below
were invented. Each statement is tagged **[SOURCED]** (from a public post, quoted without a personal or company link) or **[INFERRED]** (our reading, not their wording)._

## 1. Bottom line

- **The eval fixtures are not public.** We found no repo, Gist, talk, or TypeSafe post with the items,
  the Jev questions, the threshold, or the set size. **[SOURCED: absence across the searches listed in section 5]**
- The only primary description is one public post about a consulting engineering workflow that uses a style contract, a stop-slop skill, and a Jev hook.
  Public activity lists date it **2026-09-23**. Our brief says Sep 22. The post says "Ahead of my flight to NYC
  yesterday", so the work may have been done on the 22nd and posted on the 23rd. **[SOURCED: post + public activity list]**
- So what follows rebuilds the *design* of that eval from the post. It does not rebuild the data.

## 2. What the post actually says (quoted)

Source: a September 2026 public post describing the workflow. The post URL is omitted here so this repo does not name the author or the practice.

| Topic | Exact wording | Tag |
|---|---|---|
| Model | "the new TypeSafe AI Jev model from 4 days ago" | SOURCED |
| Build time | "built in a few hours" | SOURCED |
| Content types | "customized content for customers (for example using Claude to take in context to tailor proposals, lessons, workshops, etc ...)" | SOURCED |
| Problem | "the Claude 5 series of models had a writing style that ran the risk of making our content sound like 'AI Slop'... despite the writing style guidelines we provide" | SOURCED |
| Baseline | "a /stop-slop skill (link in comments...) that detects and removes a series of these 'tells'"; "uses a high powered model over what could be a very large document to determine if it is slop-filled" | SOURCED |
| Eval set origin | "We already had the eval set in place (using the claude plugin eval tooling that Anthropic recently released) and have built it up over time based on the before and after pairs of past /stop-slop runs as we added rules." | SOURCED |
| Tuning target | "tune the Jev input questions to get to a model that performed the same check" | SOURCED |
| Tuning method + metric | "we used /goal mode to get to about .9 AOC" | SOURCED (the word is "AOC"; reading it as **ROC AUC** is **[INFERRED]**) |
| Pipeline | "The re-write still needs to run using the full Claude model, but now only if the input is below our slop threshold." | SOURCED (the score's direction, where "below threshold" means slop, is the post's wording; how the score is built is unknown) |
| Deployment | "run it as a hook ahead of writing documents, sending slack messages or email drafts, etc." | SOURCED |
| Aftermath | Opus 5.5 "dramatically reduced the amount of slop produced by default"; "the percentage of inputs needing a stop-slop pass appears to be much lower"; still useful while "the team still uses Sonnet" until Sonnet 5.5 | SOURCED |

Related public context:
- A later public post said that workflow still ships "twelve skills covering ... stopping slop, plus the standards and CI gates", versioned into every engagement repo. **[SOURCED: October 2026 follow-up post; link omitted]**
- The post's stop-slop link sat in a comment we could not load. A public skill named stop-slop exists (https://github.com/hardikpandya/stop-slop). It covers banned phrases, structural clichés, and sentence rules, scored on 5 dimensions with "below 35/50: revise". **[SOURCED for the repo's contents; that this is the skill the post linked is INFERRED, not confirmed]**
- Jev versions: `jev-1.13.0` was current in Sep 2026, and `jev-1.14.0` shipped Oct 14, 2026 (https://docs.typesafe.ai/models.md). So that run most likely used 1.13. **[1.14 date SOURCED; their version INFERRED]**

## 3. What is NOT published (do not quote numbers for these)

Set size; slop/clean ratio; how many surfaces; label definition; whether "after" texts were used as negatives;
number and wording of Jev questions; question types (Noul/Choice/Score); aggregation; threshold; held-out split
(or none); precision/recall/F1; cost or latency figures; whether ".9" was measured on the tuning data itself.

## 4. Reconstructed eval design (INFERRED unless tagged)

1. **Unit:** one draft, labelled by whether `/stop-slop` should change it. Positives are the "before" side of past
   /stop-slop runs **[SOURCED that pairs exist]**. Negatives probably include the "after" side, and maybe drafts
   stop-slop left alone **[INFERRED]**.
2. **Surfaces:** proposals, lessons, workshops **[SOURCED]**, plus Slack messages and email drafts as hook targets **[SOURCED]**.
3. **Slop categories:** the "tells" that stop-slop rules target, added "over time ... as we added rules" **[SOURCED]**. The exact
   taxonomy is unknown. The closest public taxonomy is the stop-slop repo: throat-clearing, emphasis crutches,
   jargon, adverbs, binary contrasts, dramatic fragmentation, rhetorical setups, passive voice, Wh- openers, em dashes **[INFERRED mapping]**.
4. **Model under test:** Jev returns a probability per question. The post describes a continuous "slop score" with a threshold **[SOURCED]**.
   The metric was AUC over that score **[INFERRED from "AOC"]**.
5. **Tuning:** question wording iterated by an agent loop (/goal mode) against the eval set **[SOURCED]**. Whether a
   held-out split was kept is not stated. Treat ~0.9 as possibly in-sample **[INFERRED caution]**.
6. **Target behaviour:** "perform the same check" as the stop-slop model judgment, so the label is effectively *agreement with
   the stop-slop decision*, not human judgment **[INFERRED from SOURCED wording]**.

## 5. How our verify-copy set compares, and what to add for "similar tests"

| Published workflow (per post) | verify-copy today | Gap / suggestion |
|---|---|---|
| Real before/after pairs from past /stop-slop runs | Synthetic drafts (dev 39 / holdout 34 / stress 12) with `should_rewrite` labels | Add **paired** items: for each recorded slop draft, add its accepted rewrite (already in `bakeoff/raw_outputs.jsonl`) as a clean negative. That matches the before/after structure. Label the new items `synthetic: true, source: bakeoff-rewrite` and get them human-checked. |
| Proposals, lessons, workshops, Slack, email | Same five surfaces | Already aligned. |
| Long documents ("very large document") | Max ~100 words | Add a few long proposal/lesson drafts (1–3k words) to test Jev's context and decide on long-context. |
| AUC (~0.9) | We report P/R/F1, and AUC for Jev in `jev-gate-results.md` | Keep AUC for Jev so it can be compared with the published number, but it is not like-for-like (different data, different questions). |
| Tuned with /goal, split unknown | Frozen on dev, scored on holdout + stress | Keep our held-out protocol, which is stricter than what the post describes. |
| Opus 5.5 lowered the slop rate | Our holdout is 47% slop | Report the gate at realistic base rates (10–25%), as `bakeoff-results.md` already does for cost. |

We did not create these new fixtures. Doing so needs a decision and a human check of the labels.

## Searches performed (all public)

The public post and its activity list; web search for public write-ups of a Jev slop-gate eval, stop-slop eval fixtures,
and Jev questions; TypeSafe docs (docs.typesafe.ai, llms.txt index, models page). Other
public Jev slop work, **not** from that workflow, that is useful for comparison: nunezb/can-jev-detect-slop (AUC 0.87 on non-fiction
AI-text detection, which is a different task), qbash "Jev + Claude loop to stop AI slop" (12 questions, thresholds published),
a LinkedIn slop extension by Robert Fitt (1 Choice + 10 Nouls). These use different tasks and labels. Do not cite them as that workflow's numbers.
