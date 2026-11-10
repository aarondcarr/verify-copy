#!/usr/bin/env python3
"""Score bakeoff outputs: v2 heuristics + blind LLM judges (Opus 5.5 primary, Sonnet 5.5 secondary)."""
import json, re, sys, collections
from pathlib import Path
B = Path(__file__).parent; sys.path.insert(0, str(B.parent)); import heuristics as H

def norm(s): return re.sub(r"\s+", " ", s).strip()
def load(p): return [json.loads(l) for l in open(p)]
rs = [r for r in load(B / "raw_outputs.jsonl") if not r.get("error")]
J = {}
for jm in ("claude-opus-5-5", "claude-sonnet-5-5"):
    d = {}
    for j in load(B / f"judgments_{jm}.jsonl"):
        if not j["error"]: d[json.loads(j["key"]) and j["key"]] = j["verdict"]
    J[jm] = d

def jv(jm, r):
    o = J[jm].get(json.dumps(["orig", r["id"]]))
    if norm(r["output"]) == norm(r["input"]):
        return dict(slop=bool(o["slop"]), meaning_preserved=True, vs_original="same", over_flattened=False, changed=False)
    p = J[jm].get(json.dumps(["pair", r["id"], norm(r["output"])]))
    if p is None: return None
    return dict(slop=bool(p.get("slop")), meaning_preserved=bool(p.get("meaning_preserved")),
                vs_original=p.get("vs_original"), over_flattened=bool(p.get("over_flattened")),
                meaning_issue=p.get("meaning_issue", ""), changed=True)

NUM = re.compile(r"\d[\d,.:]*\d|\d")
def nums_dropped(a, b):
    na = [x.strip(".,:") for x in NUM.findall(a)]; nb = set(x.strip(".,:") for x in NUM.findall(b))
    return [x for x in na if x not in nb and x.replace(",", "") not in nb]

def prf(pairs):
    tp = sum(p and l for p, l in pairs); fp = sum(p and not l for p, l in pairs)
    fn = sum(l and not p for p, l in pairs); tn = len(pairs) - tp - fp - fn
    pr = tp / (tp + fp) if tp + fp else None; rc = tp / (tp + fn) if tp + fn else None
    f1 = 2 * pr * rc / (pr + rc) if pr and rc else (0.0 if pr is not None and rc is not None else None)
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=pr, recall=rc, f1=f1)

def cost(r): return r["usage"]["cost_usd"] + r.get("gate_usage", {}).get("cost_usd", 0)
def toks(r, k): return r["usage"][k] + r.get("gate_usage", {}).get(k, 0)

rows = []
for r in rs:
    r["changed"] = norm(r["output"]) != norm(r["input"])
    r["v2_out_fail"] = H.v2_gate(r["output"], r["surface"])
    r["v2_in_fail"] = H.v2_gate(r["input"], r["surface"])
    r["nums_dropped"] = nums_dropped(r["input"], r["output"])
    r["judge_opus"] = jv("claude-opus-5-5", r); r["judge_sonnet"] = jv("claude-sonnet-5-5", r)

groups = collections.defaultdict(list)
for r in rs: groups[(r["model"], r["system"], r["split"])].append(r)

def rate(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs), sum(xs), len(xs)) if xs else (None, 0, 0)

out = {}
for (m, s, sp), g in sorted(groups.items()):
    slop = [r for r in g if r["label"]]; clean = [r for r in g if not r["label"]]
    chg = [r for r in g if r["changed"]]
    def harmed(r, jm):
        j = r[jm]
        if not r["changed"] or j is None: return False if r["changed"] is False else None
        return (j["vs_original"] == "worse") or j["over_flattened"] or (not j["meaning_preserved"]) or (r["v2_out_fail"] and not r["v2_in_fail"])
    res = dict(model=m, system=s, split=sp, n=len(g), n_slop=len(slop), n_clean=len(clean),
        rewrite_decision=prf([(r["changed"], r["label"]) for r in g]),
        slop_rewritten=rate([r["changed"] for r in slop]),
        clean_rewritten=rate([r["changed"] for r in clean]),
        residual_v2_on_slop=rate([r["v2_out_fail"] for r in slop]),
        residual_judge_opus_on_slop=rate([r["judge_opus"]["slop"] if r["judge_opus"] else None for r in slop]),
        residual_judge_sonnet_on_slop=rate([r["judge_sonnet"]["slop"] if r["judge_sonnet"] else None for r in slop]),
        slop_fixed_faithfully_opus=rate([(not r["judge_opus"]["slop"]) and r["judge_opus"]["meaning_preserved"] if r["judge_opus"] else None for r in slop]),
        slop_fixed_faithfully_sonnet=rate([(not r["judge_sonnet"]["slop"]) and r["judge_sonnet"]["meaning_preserved"] if r["judge_sonnet"] else None for r in slop]),
        slop_fixed_faithfully_both=rate([(not r["judge_opus"]["slop"]) and r["judge_opus"]["meaning_preserved"] and (not r["judge_sonnet"]["slop"]) and r["judge_sonnet"]["meaning_preserved"] for r in slop]),
        meaning_flag_on_clean_either=sum(1 for r in clean if r["changed"] and not (r["judge_opus"]["meaning_preserved"] and r["judge_sonnet"]["meaning_preserved"])),
        cost_per_model_call=(sum(r["usage"]["cost_usd"] for r in g if r.get("raw") is not None) / max(1, sum(1 for r in g if r.get("raw") is not None))),
        clean_judged_slop_after_opus=rate([r["judge_opus"]["slop"] if r["judge_opus"] else None for r in clean]),
        overcorrection_harmed_opus=rate([harmed(r, "judge_opus") for r in clean]),
        overcorrection_harmed_sonnet=rate([harmed(r, "judge_sonnet") for r in clean]),
        meaning_preserved_changed_opus=rate([r["judge_opus"]["meaning_preserved"] for r in chg if r["judge_opus"]]),
        meaning_preserved_changed_sonnet=rate([r["judge_sonnet"]["meaning_preserved"] for r in chg if r["judge_sonnet"]]),
        numbers_dropped_items=sum(1 for r in g if r["nums_dropped"]),
        worse_than_original_opus=rate([r["judge_opus"]["vs_original"] == "worse" for r in chg if r["judge_opus"]]),
        cost_usd=sum(cost(r) for r in g),
        input_tokens=sum(toks(r, "input_tokens") for r in g), output_tokens=sum(toks(r, "output_tokens") for r in g),
        model_calls=sum(1 for r in g if r.get("raw") is not None), haiku_gate_calls=sum(1 for r in g if r.get("gate_raw") is not None),
        mean_latency_s=sum(r["latency_s"] for r in g) / len(g))
    if s.startswith("S4"):
        res["gate"] = prf([(r["gate_fail"], r["label"]) for r in g])
    res["cost_per_1000_drafts_extrapolated"] = res["cost_usd"] / len(g) * 1000
    out[f"{m}|{s}|{sp}"] = res

# judge calibration on original drafts vs labels
cal = {}
seen = {}
for r in rs: seen[r["id"]] = r
for jm in J:
    for sp in ("holdout", "stress"):
        pairs = [(bool(J[jm][json.dumps(["orig", i])]["slop"]), r["label"]) for i, r in seen.items() if r["split"] == sp]
        cal[f"{jm}|{sp}"] = prf(pairs)
# judge agreement
agree = [ (r["judge_opus"]["slop"] == r["judge_sonnet"]["slop"]) for r in rs if r["judge_opus"] and r["judge_sonnet"]]
agree_m = [ (r["judge_opus"]["meaning_preserved"] == r["judge_sonnet"]["meaning_preserved"]) for r in rs if r["changed"] and r["judge_opus"] and r["judge_sonnet"]]
json.dump(dict(cells=out, judge_calibration=cal, judge_agreement_slop=rate(agree), judge_agreement_meaning_on_changed=rate(agree_m),
               total_generation_cost_usd=sum(cost(r) for r in rs)), open(B / "scores.json", "w"), indent=1, default=str)
json.dump([{k: r[k] for k in ("id","split","category","surface","label","model","system","input","output","changed","v2_in_fail","v2_out_fail","nums_dropped","judge_opus","judge_sonnet")} for r in rs],
          open(B / "per_item_scored.json", "w"), indent=1)
print("ok", len(rs))
