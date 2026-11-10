# Benchmark plan

Do not claim a win without numbers. The comparison is four systems, not two skills.

## Systems under test

1. **Style contract only.** Short writing rules in `CLAUDE.md` / project instructions. No skill, no hook.
2. **Always-on skill.** A full stop-slop-style skill loaded on every draft (the expensive default).
3. **verify-copy.** Cheap prefilter; rewrite only on a failed gate.
4. **Model default.** No style contract and no skill, by model family (Sonnet-class daily model vs Opus 5.5-class).

If 1 or 4 already matches 3 on a given model and surface, the skill is bloat. Report that. The interesting number is the cheapest stack that stays at or above an agreed quality bar.

## Metrics

- **Gate precision / recall / F1** against labeled fixtures: should this draft be rewritten?
- **Rewrite needed rate** by model and surface (what share actually tripped the gate).
- **Cost** in tokens or dollars per accepted draft, including skill context and rewrite passes.
- **Latency** to a send-ready draft.
- **Meaning preservation:** no changed facts, numbers, names, dates, or commitments (binary, human-checked on a sample).
- **Over-correction rate:** human flag when the rewrite is stiffer or less usable than the original.
- **Residual slop after rewrite:** heuristic counts and an optional human 1–10 (directness, rhythm, trust). The counts are the official score.

## Fixtures

Start with [fixtures/](fixtures/). Each JSON file has `id`, `surface`, `model_hint`, `input`, `should_rewrite`, `notes`, and when useful a `reference_rewrite`. Harvest accepted before/after pairs from real consulting work into the same shape. Keep classic slop, residual 5.5 slop, clean human copy, and over-correction traps in the set.

## How to run

```bash
python3 evals/build_fixtures.py          # regenerate dev/ and holdout/ synthetic fixtures
python3 evals/heuristics.py evals/fixtures/holdout   # v2 gate, per-item + summary
python3 evals/run_spike.py > evals/spike_run.json    # v1 vs v2 vs ban-list vs always-rewrite, by split and category
```

Fixtures live in `fixtures/dev` (tune here), `fixtures/holdout` (do not tune), and `fixtures/stress` (written after v2 was frozen to probe blind spots: slop vocabulary outside the regex lists, and long clean copy). All fixtures are synthetic and hand-labeled by one author. `heuristics_v1.py` is the starter gate kept for comparison. Results: [spike-results.md](spike-results.md).

That prints counts and a pass/fail against the default thresholds. It does not call a model. A later pass can add a classifier score and a rewrite model, then score those outputs against the same labels.

## Fairness rules

- Same fixtures, same surfaces, same claims.
- Do not tune thresholds on the holdout set.
- Flag n < 30 per cell as too small to conclude.
- A skill that lowers slop by wrecking voice is a loss.

## Similar tests

A look-alike before/after pack, not a reconstruction of any unpublished eval, lives in [fixtures/similar/](fixtures/similar/). See that README before scoring it.
