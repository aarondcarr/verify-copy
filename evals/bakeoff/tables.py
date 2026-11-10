#!/usr/bin/env python3
"""Render markdown tables from scores.json and compute total spend."""
import json
from pathlib import Path
B = Path(__file__).parent
S = json.load(open(B / "scores.json"))
MN = {"claude-haiku-5-5": "Haiku 5.5", "claude-sonnet-5-5": "Sonnet 5.5", "claude-opus-5-5": "Opus 5.5"}
SN = {"S1_default": "1 Model default", "S2_contract": "2 Style contract", "S3_skill": "3 Always-on skill",
      "S4_gate_v2": "4 Gate (v2 regex)", "S4b_gate_v2_or_haiku": "4b Gate (v2 + Haiku)"}
def fr(x): v, k, n = x; return f"{k}/{n}" if n else "n/a"
def ff(x): return "n/a" if x is None else f"{x:.2f}"
out = []
for sp, title in (("holdout", "Holdout (n=34: 16 slop, 18 clean incl. 8 over-correction traps)"),
                  ("stress", "Hard cases (n=12: 8 unseen-vocabulary slop, 4 long clean)")):
    out.append(f"\n### {title}\n")
    out.append("| Model | System | Slop drafts rewritten | Clean drafts touched | Rewrite-decision P / R / F1 | Residual slop: v2 | Residual slop: Opus judge | Residual slop: Sonnet judge | Slop fixed AND meaning kept (both judges) | Clean drafts harmed (Opus / Sonnet judge) | Meaning kept on changed outputs (Opus / Sonnet judge) | Cost (USD) | Cost per 1k drafts (extrapolated) |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for m in MN:
        for s in SN:
            c = S["cells"].get(f"{m}|{s}|{sp}")
            if not c: continue
            d = c["rewrite_decision"]
            out.append(f"| {MN[m]} | {SN[s]} | {fr(c['slop_rewritten'])} | {fr(c['clean_rewritten'])} | {ff(d['precision'])} / {ff(d['recall'])} / {ff(d['f1'])} | "
                       f"{fr(c['residual_v2_on_slop'])} | {fr(c['residual_judge_opus_on_slop'])} | {fr(c['residual_judge_sonnet_on_slop'])} | "
                       f"{fr(c['slop_fixed_faithfully_both'])} | {fr(c['overcorrection_harmed_opus'])} / {fr(c['overcorrection_harmed_sonnet'])} | "
                       f"{fr(c['meaning_preserved_changed_opus'])} / {fr(c['meaning_preserved_changed_sonnet'])} | ${c['cost_usd']:.4f} | ${c['cost_per_1000_drafts_extrapolated']:.2f} |")
out.append("\n### Gate classification (should this draft be rewritten?)\n")
out.append("| Gate | Split | TP | FP | FN | TN | Precision | Recall | F1 |\n|---|---|---|---|---|---|---|---|---|")
for s in ("S4_gate_v2", "S4b_gate_v2_or_haiku"):
    for m in MN:
        for sp in ("holdout", "stress"):
            g = S["cells"][f"{m}|{s}|{sp}"]["gate"]
            out.append(f"| {SN[s]} ({MN[m]} run) | {sp} | {g['tp']} | {g['fp']} | {g['fn']} | {g['tn']} | {ff(g['precision'])} | {ff(g['recall'])} | {ff(g['f1'])} |")
out.append("\n### Tokens and per-call cost\n")
out.append("| Model | System | Split | Model calls | Haiku gate calls | Input tokens | Output tokens | Mean cost per rewrite call | Mean latency per draft (s) |\n|---|---|---|---|---|---|---|---|---|")
for m in MN:
    for s in SN:
        for sp in ("holdout", "stress"):
            c = S["cells"][f"{m}|{s}|{sp}"]
            out.append(f"| {MN[m]} | {SN[s]} | {sp} | {c['model_calls']} | {c['haiku_gate_calls']} | {c['input_tokens']:,} | {c['output_tokens']:,} | ${c['cost_per_model_call']:.5f} | {c['mean_latency_s']:.1f} |")
cal = S["judge_calibration"]
out.append("\n### Judge calibration on the original drafts (judge's slop verdict vs. the hand label)\n")
out.append("| Judge | Split | TP | FP | FN | TN |\n|---|---|---|---|---|---|")
for k, v in cal.items():
    j, sp = k.split("|"); out.append(f"| {MN[j]} | {sp} | {v['tp']} | {v['fp']} | {v['fn']} | {v['tn']} |")
a, m_ = S["judge_agreement_slop"], S["judge_agreement_meaning_on_changed"]
out.append(f"\nJudge agreement: slop verdict {a[1]}/{a[2]} outputs; meaning verdict {m_[1]}/{m_[2]} changed outputs.")
# spend
def tot(f):
    c = it = ot = n = 0
    for l in open(B / f):
        r = json.loads(l)
        for u in (r.get("usage"), r.get("gate_usage")):
            if u: c += u["cost_usd"]; it += u["input_tokens"]; ot += u["output_tokens"]
        n += (r.get("raw") is not None) + (r.get("gate_raw") is not None) if "system" in r else 1
    return n, it, ot, c
out.append("\n### Actual spend (from API usage fields x list prices)\n")
out.append("| Stage | API calls | Input tokens | Output tokens | Cost (USD) |\n|---|---|---|---|---|")
T = [0, 0, 0, 0]
for label, f in (("Prompt sanity check on tune set (dev, 39 drafts; not reported)", "dev_sanity.jsonl"),
                 ("Bakeoff generations, holdout + hard cases (final)", "raw_outputs.jsonl"),
                 ("System 4b first run (discarded: gate max_tokens bug)", "raw_outputs_S4b_firstrun_gate_truncated.jsonl"),
                 ("Opus 5.5 judge (incl. 95 truncated replies re-run)", "judgments_claude-opus-5-5.jsonl"),
                 ("Sonnet 5.5 judge", "judgments_claude-sonnet-5-5.jsonl")):
    r = tot(f); T = [a + b for a, b in zip(T, r)]
    out.append(f"| {label} | {r[0]:,} | {r[1]:,} | {r[2]:,} | ${r[3]:.2f} |")
out.append(f"| **Total** | **{T[0]:,}** | **{T[1]:,}** | **{T[2]:,}** | **${T[3]:.2f}** |")
(B / "tables.md").write_text("\n".join(out) + "\n")
print("\n".join(out[-8:]))
