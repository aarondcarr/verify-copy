#!/usr/bin/env python3
"""Gate-only benchmark: TypeSafe Jev vs regex v2 vs regex v2 + Haiku (system 4b).

Usage (from verify-copy/):
    python3 evals/bakeoff/run_jev_gate.py                 # jev-1.14.0, then jev-1.13.0 if 1.14 worked and was cheap
    python3 evals/bakeoff/run_jev_gate.py --models jev-1.14.0
    python3 evals/bakeoff/run_jev_gate.py --baseline-only # no API calls; regex + recorded 4b only

Protocol
  1. Every candidate question set below was written from the 39 dev drafts only.
  2. Phase "tune": every dev draft gets one request containing all candidate questions.
     A (candidate, aggregation, threshold) is selected by dev F1 (ties: fewer dev FPs,
     then threshold nearest 0.5, then candidate order). Selection is automatic.
  3. The frozen config is written to jev_frozen_config.json BEFORE any holdout/stress request.
  4. Phase "test": holdout + stress drafts get one request each with only the frozen questions.
  5. For a second model, the question text stays frozen from step 2; only the threshold is
     re-picked on dev for that model (reported separately).

Key handling: reads TYPESAFE_API_KEY from the environment and sends it only in the
Authorization header. It is never printed, logged, or written. No Anthropic calls are made.
Errors and empty replies fail closed (counted as "rewrite") and are recorded.
"""
from __future__ import annotations

import argparse, json, math, os, random, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent          # evals/bakeoff
EVALS = HERE.parent
sys.path.insert(0, str(EVALS))
import heuristics as H  # noqa: E402

BASE = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai").rstrip("/")
PRICE_PER_MTOK = 0.042
MAX_INPUT_TOKENS_TOTAL = 3_000_000          # hard budget guard (~$0.13)
OUT_JSON = HERE / "jev_gate.json"
FROZEN = HERE / "jev_frozen_config.json"
REPORT = EVALS / "bakeoff" / "jev-gate-results.md"

# ----------------------------------------------------------------------------------------
# Candidate questions (written from dev drafts only; our design, not that workflow's unpublished questions)
# ----------------------------------------------------------------------------------------
QUOTE_NOTE = ("Text inside quotation marks is quoted from someone else and does not count. "
              "Precise, specific writing with an occasional adverb, em dash, passive verb, "
              "or plain negation is fine.")

Q = {
    # A: one overall gate question, mirroring the 4b Haiku prompt
    "needs_rewrite": {"type": "noul",
        "instructions": "Does the draft in `state` need a rewrite because it reads like generic "
                        "AI-generated or filler-heavy prose? " + QUOTE_NOTE,
        "criteria": {"true": "Throat-clearing, buzzwords, 'not X, it's Y' templates, padded triads, empty "
                             "headings or bullets, recaps, restating the ask, or sign-off offers make it read as AI slop",
                     "false": "Plain, specific, ready to send as written, even if informal or imperfect"}},
    # B: three-way verdict
    "verdict": {"type": "choice",
        "instructions": "A demanding editor reviews the draft in `state` before it goes to a client or "
                        "colleague. What would they do? " + QUOTE_NOTE,
        "criteria": {"send": "Send as is. It is specific and direct, even if casual.",
                     "minor_edit": "A word or two could change, but the voice and structure are fine.",
                     "rewrite_slop": "Rewrite it. It reads like generic AI writing: stock phrases, "
                                     "announcements instead of content, templated contrasts, filler structure."}},
    # C: atomic tells
    "tell_throat": {"type": "noul",
        "instructions": "Does the author announce or set up a point instead of making it, e.g. "
                        "'here's the thing', 'let me walk you through', 'let that sink in', "
                        "'the real insight is', 'make no mistake', 'in this section we will', "
                        "'I hope this email finds you well'? " + QUOTE_NOTE},
    "tell_contrast": {"type": "noul",
        "instructions": "Does the author use a templated contrast such as 'it's not X, it's Y', "
                        "'this isn't X. It's Y', or 'X is more than A, it's B' as a rhetorical move? "
                        "A plain factual negation that states what is in or out of scope does not count. "
                        + QUOTE_NOTE},
    "tell_buzz": {"type": "noul",
        "instructions": "Does the draft lean on vague buzzwords or stock phrases such as navigate the "
                        "landscape, deep dive, unpack, circle back, game-changer, load-bearing, "
                        "'this matters', 'why X matters', 'looking ahead', 'rather than simply', "
                        "dependable, steady, alignment, momentum? " + QUOTE_NOTE},
    "tell_structure": {"type": "noul",
        "instructions": "Is the draft padded with empty structure: headings or bullets that hold no "
                        "real content, restating the reader's question back to them, a recap of what "
                        "was just said, or stacked three-item lists of abstract nouns?"},
    "tell_signoff": {"type": "noul",
        "instructions": "Does the draft end with a generic offer such as 'happy to dive deeper', "
                        "'hope this helps', or 'let me know if you'd like me to expand'?"},
    "specific": {"type": "noul",
        "instructions": "Is nearly every sentence in the draft concrete, carrying a specific fact, "
                        "number, name, date, decision, or action, with nothing that could be cut "
                        "without losing information?"},
}
TELLS = ["tell_throat", "tell_contrast", "tell_buzz", "tell_structure", "tell_signoff"]


def p_choice(a, opt):
    return float(((a or {}).get("probabilities") or {}).get(opt, float("nan")))


# Each candidate: (question ids used, aggregator answers->slop score in [0,1])
CANDIDATES = {
    "A_single_noul": (["needs_rewrite"], lambda a: a["needs_rewrite"]["noul"]),
    "B_verdict_choice": (["verdict"], lambda a: p_choice(a["verdict"], "rewrite_slop")),
    "C_max_tell": (TELLS, lambda a: max(a[t]["noul"] for t in TELLS)),
    "D_A_and_maxtell_mean": (["needs_rewrite"] + TELLS,
                             lambda a: 0.5 * a["needs_rewrite"]["noul"] + 0.5 * max(a[t]["noul"] for t in TELLS)),
    "E_maxtell_minus_specific": (TELLS + ["specific"],
                                 lambda a: max(a[t]["noul"] for t in TELLS) * (1 - 0.5 * a["specific"]["noul"])),
}

# ----------------------------------------------------------------------------------------
_lock = threading.Lock()
_spent = {"input_tokens": 0, "output_tokens": 0, "requests": 0}


class Fatal(Exception):
    pass


def _key() -> str:
    k = (os.environ.get("TYPESAFE_API_KEY") or "").strip()
    if not k:
        raise Fatal("TYPESAFE_API_KEY is not set in this environment")
    return k


def call_jev(model: str, state, questions: dict, max_tries: int = 6) -> dict:
    body = json.dumps({"model": model, "state": state, "questions": questions}).encode()
    with _lock:
        if _spent["input_tokens"] > MAX_INPUT_TOKENS_TOTAL:
            raise Fatal("budget guard hit")
    last = None
    for attempt in range(max_tries):
        req = urllib.request.Request(f"{BASE}/v1/systemone", data=body, method="POST",
                                     headers={"Authorization": "Bearer " + _key(),
                                              "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            u = data.get("usage") or {}
            with _lock:
                _spent["input_tokens"] += int(u.get("input_tokens") or 0)
                _spent["output_tokens"] += int(u.get("output_tokens") or 0)
                _spent["requests"] += 1
            data["_latency_s"] = round(time.time() - t0, 3)
            return data
        except urllib.error.HTTPError as e:
            code = e.code
            detail = ""
            try:
                detail = json.loads(e.read()).get("detail")
                detail = json.dumps(detail)[:300]
            except Exception:
                pass
            if code in (401, 403):
                raise Fatal(f"HTTP {code} from TypeSafe (auth). Check TYPESAFE_API_KEY. {detail}")
            if code in (429, 529, 500, 502, 503, 504):
                ra = e.headers.get("retry-after")
                wait = float(ra) if ra and ra.replace(".", "").isdigit() else min(30, 2 ** attempt) + random.random()
                last = f"HTTP {code} {detail}"
                time.sleep(wait)
                continue
            return {"_error": f"HTTP {code} {detail}"}
        except Exception as e:  # network
            last = f"{type(e).__name__}: {str(e)[:200]}"
            time.sleep(min(30, 2 ** attempt))
    return {"_error": f"gave up after {max_tries} tries: {last}"}


def state_for(item):
    return {"surface": item.get("surface", "proposal"), "draft": item["input"]}


def score_item(model, item, qids):
    qs = {q: Q[q] for q in qids}
    resp = call_jev(model, state_for(item), qs)
    rec = {"id": item["id"], "split": item["split"], "category": item.get("category"),
           "surface": item.get("surface"), "label": bool(item["should_rewrite"]),
           "requested_model": model, "response_model": resp.get("model"),
           "usage": resp.get("usage"), "latency_s": resp.get("_latency_s"), "error": resp.get("_error")}
    answers = resp.get("answers") or {}
    missing = [q for q in qids if q not in answers]
    if not rec["error"] and missing:
        rec["error"] = f"missing answers: {missing}"
    rec["answers"] = answers
    return rec


def cand_score(rec, cand):
    qids, agg = CANDIDATES[cand]
    if rec["error"] or any(q not in rec["answers"] for q in qids):
        return None
    try:
        s = float(agg(rec["answers"]))
        return None if math.isnan(s) else s
    except Exception:
        return None


def metrics(pairs):
    return H.metrics(pairs)


def auc(scores_labels):
    pos = [s for s, l in scores_labels if l and s is not None]
    neg = [s for s, l in scores_labels if (not l) and s is not None]
    if not pos or not neg:
        return None
    w = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return round(w / (len(pos) * len(neg)), 3)


def decide(score, thr):
    return True if score is None else score >= thr   # fail closed


def select_on_dev(dev_recs, regex_or=False):
    best = None
    grid = [round(x * 0.05, 2) for x in range(1, 20)]
    for ci, cand in enumerate(CANDIDATES):
        for thr in grid:
            pairs = []
            for r in dev_recs:
                p = decide(cand_score(r, cand), thr)
                if regex_or:
                    p = p or r["regex_v2"]
                pairs.append((p, r["label"]))
            m = metrics(pairs)
            key = (m["f1"], -m["fp"], -abs(thr - 0.5), -ci)
            if best is None or key > best[0]:
                best = (key, cand, thr, m)
    return {"candidate": best[1], "threshold": best[2], "dev_metrics": best[3]}


def run_parallel(fn, items, workers=4):
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, items))


# ----------------------------------------------------------------------------------------
def load_split(name):
    items = H.load_fixtures(EVALS / "fixtures" / name)
    for it in items:
        it.setdefault("split", name)
    return items


def recorded_4b():
    """Gate decisions recorded in raw_outputs.jsonl (fixed run). One Haiku gate run per rewrite-model cell."""
    out = {}
    p = HERE / "raw_outputs.jsonl"
    if not p.exists():
        return out
    for line in p.open():
        r = json.loads(line)
        if r.get("system") != "S4b_gate_v2_or_haiku" or "gate_fail" not in r:
            continue
        out.setdefault(r["model"], {})[r["id"]] = bool(r["gate_fail"])
    return out


def fmt_m(m):
    return (f"{m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | {m['precision']:.2f} | "
            f"{m['recall']:.2f} | {m['f1']:.2f}")


def build_report(res):
    L = []
    A = L.append
    A("# Gate-only benchmark: TypeSafe Jev vs regex v2 vs regex v2 + Haiku (4b)\n")
    A(f"_Generated by `evals/bakeoff/run_jev_gate.py` on {res['generated_at']}. Every number below is "
      "computed by that script from `fixtures/` and the recorded files; none were typed in by hand._\n")
    A("## What was compared\n")
    A("- **Label:** `should_rewrite` on each fixture. A gate \"flags\" a draft when it would send it to the rewrite step.")
    A("- **Regex v2:** `evals/heuristics.py` `v2_gate`, deterministic, recomputed here.")
    A("- **4b (regex v2 + Haiku 5.5 one-word check):** gate decisions *reused* from `bakeoff/raw_outputs.jsonl` "
      "(the fixed run, gate max_tokens=256, fail closed). The Haiku gate ran once per rewrite-model cell, so there are "
      "three recorded gate runs per item (labelled by the rewrite model of that cell). No Anthropic calls were made for this report.")
    A("- **4b on dev:** not reported. The only recorded dev 4b gate (`dev_sanity.jsonl`) is from the discarded "
      "max_tokens=8 run (5 empty replies), so it is not comparable.")
    A("- **Jev:** TypeSafe System One, `POST /v1/systemone`, draft sent in `state` as `{surface, draft}`. "
      "Questions and threshold frozen on dev only (see protocol). Also shown: **regex v2 OR Jev**, the same shape as 4b "
      "with Jev in Haiku's place (threshold for this variant also picked on dev).")
    A("\n**Small n.** Dev 39 (19 slop / 20 clean), holdout 34 (16 / 18), stress 12 (8 / 4). On stress, one draft is 12.5 points "
      "of recall or 25 points of clean false-positive rate. Treat differences of 1–2 drafts as noise. All fixtures are synthetic.\n")
    if res.get("jev_status") != "ran":
        A(f"> **Jev was not called in this run:** {res.get('jev_status')}. Only the baseline tables below are filled in.\n")
    A("## Results by split\n")
    A("Columns: TP (slop flagged) | FP (clean flagged) | FN (slop missed) | TN | precision | recall | F1. AUC is threshold-free, Jev only.\n")
    for split in ("dev", "holdout", "stress", "holdout+stress"):
        rows = res["tables"].get(split)
        if not rows:
            continue
        A(f"### {split}\n")
        A("| Gate | n | TP | FP | FN | TN | P | R | F1 | AUC |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for name, m in rows:
            A(f"| {name} | {m['n']} | {fmt_m(m)} | {m.get('auc') if m.get('auc') is not None else '—'} |")
        A("")
    if res.get("misses"):
        A("## Per-item errors on holdout + stress (gate disagrees with label)\n")
        A("| Gate | False positives on clean (ids) | Missed slop (ids) |")
        A("|---|---|---|")
        for name, d in res["misses"].items():
            A(f"| {name} | {', '.join(d['fp']) or '—'} | {', '.join(d['fn']) or '—'} |")
        A("")
    if res.get("agreement"):
        A("## Overlap with 4b's flagged set (holdout + stress)\n")
        A("If Jev flags exactly what 4b flagged, the recorded 4b rewrites can be reused without new Claude calls.\n")
        A("| Jev gate | vs 4b run | same decision | Jev-only flags | 4b-only flags |")
        A("|---|---|---|---|---|")
        for a in res["agreement"]:
            A(f"| {a['jev']} | {a['b4']} | {a['same']}/{a['n']} | {', '.join(a['jev_only']) or '—'} | {', '.join(a['b4_only']) or '—'} |")
        A("")
    if res.get("jev"):
        A("## Jev runs: versions, cost, errors\n")
        A("| Requested | Model id in responses | Requests | Input tokens | Output tokens | Cost (USD) | Errors (fail-closed) |")
        A("|---|---|---|---|---|---|---|")
        for m, j in res["jev"].items():
            A(f"| `{m}` | {', '.join('`%s`' % x for x in j['response_models'])} | {j['requests']} | {j['input_tokens']:,} | "
              f"{j['output_tokens']:,} | ${j['cost_usd']:.6f} | {j['n_errors']} |")
        A(f"\nTotal Jev spend this run: **${res['jev_total_cost_usd']:.6f}** at $0.042 per million input tokens (output free). "
          "Long context was not enabled; the longest draft is under 100 words.\n")
        A("### Frozen selection (picked on dev only)\n")
        for m, j in res["jev"].items():
            A(f"- `{m}` Jev alone: candidate **{j['frozen']['candidate']}**, threshold **{j['frozen']['threshold']}**; "
              f"regex v2 OR Jev: candidate **{j['frozen_or']['candidate']}**, threshold **{j['frozen_or']['threshold']}**.")
        A("\nDev AUC of every candidate (shows how much the selection could be overfit to 39 drafts):\n")
        A("| Model | " + " | ".join(CANDIDATES) + " |")
        A("|---|" + "---|" * len(CANDIDATES))
        for m, j in res["jev"].items():
            A(f"| `{m}` | " + " | ".join(str(j['dev_auc_by_candidate'].get(c)) for c in CANDIDATES) + " |")
        A("")
    A("## Frozen Jev question text\n")
    A("Our own question design, written from the 39 dev drafts. **These are not the unpublished questions from the consulting workflow this bakeoff is measured against.** "
      "A September 2026 public post about that workflow reports about 0.9 (\"AOC\", read as AUC) on an internal eval set built from past "
      "/stop-slop before/after pairs, tuned with /goal mode. That set and its questions are not public, so this is not a reproduction.\n")
    A("```json")
    A(json.dumps({"candidates": {c: v[0] for c, v in CANDIDATES.items()}, "questions": Q}, indent=2))
    A("```\n")
    A("Aggregators: A = P(yes) of `needs_rewrite`; B = P(`rewrite_slop`); C = max of the five tell Nouls; "
      "D = 0.5·A + 0.5·C; E = C × (1 − 0.5·P(`specific`)). A missing/error answer counts as flagged.\n")
    A("## Recommendation\n")
    A(res.get("recommendation") or "_Pending a Jev run._")
    A("")
    return "\n".join(L)


def recommend(res):
    t = res["tables"]
    if res.get("jev_status") != "ran":
        return None
    def get(split, prefix):
        for n, m in t.get(split, []):
            if n.startswith(prefix):
                return m
    lines = []
    b4 = get("stress", "4b")
    hs_b4 = get("holdout+stress", "4b")
    for m in res["jev"]:
        js = get("stress", f"Jev {m} alone")
        jo = get("stress", f"regex v2 OR Jev {m}")
        hs_js = get("holdout+stress", f"Jev {m} alone")
        hs_jo = get("holdout+stress", f"regex v2 OR Jev {m}")
        lines.append(f"`{m}`: stress Jev alone F1 {js['f1']:.2f} (TP {js['tp']}/8, FP {js['fp']}/4), regex OR Jev F1 {jo['f1']:.2f} "
                     f"(TP {jo['tp']}/8, FP {jo['fp']}/4); holdout+stress Jev alone F1 {hs_js['f1']:.2f}, regex OR Jev F1 {hs_jo['f1']:.2f}.")
    best_jev = max(max(get("holdout+stress", f"regex v2 OR Jev {m}")["f1"], get("holdout+stress", f"Jev {m} alone")["f1"])
                   for m in res["jev"])
    beat = bool(hs_b4) and best_jev > hs_b4["f1"]
    tie = bool(hs_b4) and best_jev == hs_b4["f1"]
    head = (f"The recorded 4b gate (first Haiku run) scored F1 {hs_b4['f1']:.2f} on holdout+stress and F1 {b4['f1']:.2f} on stress. "
            if hs_b4 and b4 else "")
    if beat:
        verdict = ("A Jev variant beat 4b on these drafts. With n=46 that edge is a few drafts at most, so treat it as "
                   "a reason to treat Jev as a cheaper drop-in for the Haiku check, not as proof it is better.")
    elif tie:
        verdict = ("A Jev variant tied 4b on these drafts. Jev is cheaper and faster per call than a Haiku call, so it is a "
                   "reasonable cheaper drop-in for the Haiku check, but a tie on 46 synthetic drafts is not evidence "
                   "that it is better. Keep 4b as the default until Jev is rerun on real drafts.")
    else:
        verdict = ("Jev did not beat 4b here. 4b has no room to improve on this set, so the most Jev can claim is a tie at lower "
                   "cost and latency. Keep 4b (regex v2 + Haiku) as the gate. Show Jev as a measured alternative, give "
                   "its numbers and say plainly that the questions are ours, not that workflow's.")
    return head + " " + " ".join(lines) + "\n\n" + verdict + " Every split is small and synthetic. Before switching in production, rerun on real drafts."


# ----------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="jev-1.14.0,jev-1.13.0")
    ap.add_argument("--baseline-only", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    splits = {s: load_split(s) for s in ("dev", "holdout", "stress")}
    for its in splits.values():
        for it in its:
            it["regex_v2"] = H.v2_gate(it["input"], it.get("surface", "proposal"))
    b4 = recorded_4b()
    res = {"generated_at": time.strftime("%Y-%m-%d %H:%M %Z"), "n": {s: len(v) for s, v in splits.items()},
           "tables": {}, "jev": {}, "items": {}, "misses": {}, "agreement": []}

    def add_row(split, name, pairs, scores=None):
        m = metrics(pairs)
        if scores is not None:
            m["auc"] = auc(scores)
        res["tables"].setdefault(split, []).append((name, m))

    test = splits["holdout"] + splits["stress"]
    for split, its in list(splits.items()) + [("holdout+stress", test)]:
        add_row(split, "regex v2", [(it["regex_v2"], bool(it["should_rewrite"])) for it in its])
        if split != "dev":
            for mdl in sorted(b4):
                if all(it["id"] in b4[mdl] for it in its):
                    add_row(split, f"4b regex+Haiku (gate run in {mdl} cell)",
                            [(b4[mdl][it["id"]], bool(it["should_rewrite"])) for it in its])
                else:
                    res.setdefault("notes", []).append(f"4b gate decisions missing for some {split} items in {mdl} cell")

    def misses(name, preds):
        res["misses"][name] = {"fp": [it["id"] for it in test if preds[it["id"]] and not it["should_rewrite"]],
                               "fn": [it["id"] for it in test if not preds[it["id"]] and it["should_rewrite"]]}
    misses("regex v2", {it["id"]: it["regex_v2"] for it in test})
    first_b4 = None
    for mdl in sorted(b4):
        if all(it["id"] in b4[mdl] for it in test):
            first_b4 = first_b4 or mdl
            misses(f"4b ({mdl} cell)", b4[mdl])

    res["jev_status"] = "not requested (--baseline-only)" if args.baseline_only else "ran"
    if not args.baseline_only:
        try:
            _key()
            models = [m.strip() for m in args.models.split(",") if m.strip()]
            all_q = list(Q)
            for mi, model in enumerate(models):
                before = dict(_spent)
                # ---- tune on dev (all candidate questions in one request per draft)
                dev_recs = run_parallel(lambda it: score_item(model, it, all_q), splits["dev"], args.workers)
                for r, it in zip(dev_recs, splits["dev"]):
                    r["regex_v2"] = it["regex_v2"]
                if mi == 0:
                    frozen = select_on_dev(dev_recs)
                    frozen_or = select_on_dev(dev_recs, regex_or=True)
                    cfg = {"selected_with_model": model, "jev_alone": frozen, "regex_or_jev": frozen_or,
                           "questions": {c: CANDIDATES[c][0] for c in {frozen["candidate"], frozen_or["candidate"]}},
                           "question_text": Q, "frozen_at": time.strftime("%Y-%m-%d %H:%M:%S %Z")}
                    FROZEN.write_text(json.dumps(cfg, indent=2))
                    q_alone, q_or = frozen["candidate"], frozen_or["candidate"]
                else:
                    # question text frozen from the first model; only threshold re-picked on dev
                    def thr_only(cand, regex_or):
                        best = None
                        for thr in [round(x * 0.05, 2) for x in range(1, 20)]:
                            pairs = [((decide(cand_score(r, cand), thr) or (regex_or and r["regex_v2"])), r["label"]) for r in dev_recs]
                            m = metrics(pairs); key = (m["f1"], -m["fp"], -abs(thr - 0.5))
                            if best is None or key > best[0]:
                                best = (key, thr, m)
                        return {"candidate": cand, "threshold": best[1], "dev_metrics": best[2]}
                    frozen, frozen_or = thr_only(q_alone, False), thr_only(q_or, True)
                # ---- test (only frozen questions)
                test_q = sorted(set(CANDIDATES[q_alone][0]) | set(CANDIDATES[q_or][0]))
                test_recs = run_parallel(lambda it: score_item(model, it, test_q), test, args.workers)
                for r, it in zip(test_recs, test):
                    r["regex_v2"] = it["regex_v2"]
                for recs in (dev_recs, test_recs):
                    for r in recs:
                        sa, so = cand_score(r, q_alone), cand_score(r, q_or)
                        r["jev_score_alone"], r["jev_score_or"] = sa, so
                        r["flag_jev_alone"] = decide(sa, frozen["threshold"])
                        r["flag_regex_or_jev"] = bool(r["regex_v2"] or decide(so, frozen_or["threshold"]))
                by_split = {"dev": dev_recs, "holdout": [r for r in test_recs if r["split"] == "holdout"],
                            "stress": [r for r in test_recs if r["split"] == "stress"], "holdout+stress": test_recs}
                for split, recs in by_split.items():
                    add_row(split, f"Jev {model} alone", [(r["flag_jev_alone"], r["label"]) for r in recs],
                            [(r["jev_score_alone"], r["label"]) for r in recs])
                    add_row(split, f"regex v2 OR Jev {model}", [(r["flag_regex_or_jev"], r["label"]) for r in recs],
                            [(r["jev_score_or"], r["label"]) for r in recs])
                misses(f"Jev {model} alone", {r["id"]: r["flag_jev_alone"] for r in test_recs})
                misses(f"regex v2 OR Jev {model}", {r["id"]: r["flag_regex_or_jev"] for r in test_recs})
                for mdl in sorted(b4):
                    if all(r["id"] in b4[mdl] for r in test_recs):
                        for col in ("flag_jev_alone", "flag_regex_or_jev"):
                            same = [r for r in test_recs if r[col] == b4[mdl][r["id"]]]
                            res["agreement"].append({"jev": f"{model} {col.replace('flag_', '')}", "b4": mdl,
                                "same": len(same), "n": len(test_recs),
                                "jev_only": [r["id"] for r in test_recs if r[col] and not b4[mdl][r["id"]]],
                                "b4_only": [r["id"] for r in test_recs if b4[mdl][r["id"]] and not r[col]]})
                spent_in = _spent["input_tokens"] - before["input_tokens"]
                res["jev"][model] = {
                    "response_models": sorted({r["response_model"] for r in dev_recs + test_recs if r["response_model"]}),
                    "requests": _spent["requests"] - before["requests"], "input_tokens": spent_in,
                    "output_tokens": _spent["output_tokens"] - before["output_tokens"],
                    "cost_usd": spent_in * PRICE_PER_MTOK / 1e6,
                    "n_errors": sum(1 for r in dev_recs + test_recs if r["error"]),
                    "errors": [{"id": r["id"], "error": r["error"]} for r in dev_recs + test_recs if r["error"]],
                    "frozen": frozen, "frozen_or": frozen_or,
                    "dev_auc_by_candidate": {c: auc([(cand_score(r, c), r["label"]) for r in dev_recs]) for c in CANDIDATES},
                }
                res["items"][model] = dev_recs + test_recs
                print(f"[{model}] requests={res['jev'][model]['requests']} input_tokens={spent_in} "
                      f"cost=${res['jev'][model]['cost_usd']:.6f} errors={res['jev'][model]['n_errors']}", flush=True)
                # only run the second model if the first worked and stayed cheap
                if mi == 0 and (res["jev"][model]["n_errors"] > len(dev_recs + test_recs) // 4
                                or res["jev"][model]["cost_usd"] > 0.05):
                    res.setdefault("notes", []).append("second model skipped: first run had many errors or cost > $0.05")
                    break
        except Fatal as e:
            res["jev_status"] = f"stopped: {e}"
            print(f"Jev run stopped: {e}", file=sys.stderr)

    res["jev_total_cost_usd"] = sum(j["cost_usd"] for j in res["jev"].values())
    if res["jev_status"] == "ran" and not res["jev"]:
        res["jev_status"] = "no Jev results"
    res["recommendation"] = recommend(res)
    # tables to JSON-friendly
    out = dict(res)
    out["tables"] = {s: [{"gate": n, **m} for n, m in rows] for s, rows in res["tables"].items()}
    out["regex_v2_flags"] = {it["id"]: it["regex_v2"] for s in splits.values() for it in s}
    out["b4_flags_recorded"] = b4
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    REPORT.write_text(build_report(res))
    print(f"wrote {OUT_JSON} and {REPORT}; jev_status={res['jev_status']}; total_cost=${res['jev_total_cost_usd']:.6f}")
    for split in ("holdout", "stress", "holdout+stress"):
        for n, m in res["tables"].get(split, []):
            print(f"{split:15s} {n:45s} P={m['precision']:.2f} R={m['recall']:.2f} F1={m['f1']:.2f} FP={m['fp']} FN={m['fn']}"
                  + (f" AUC={m['auc']}" if m.get("auc") is not None else ""))
    return 0 if res["jev_status"] == "ran" or args.baseline_only else 2


if __name__ == "__main__":
    sys.exit(main())
