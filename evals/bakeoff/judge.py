#!/usr/bin/env python3
"""Blind LLM judge for bakeoff outputs. Judge never sees the system name, model, or label.
Unchanged outputs (identical to the draft) are not re-judged for meaning/quality (trivially preserved/same);
their slop verdict comes from judging the original draft once."""
import json, sys, re, argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
sys.path.insert(0, str(Path(__file__).parent)); import run_bakeoff as R

ORIG_P = ("You are a strict but fair editor of professional writing (consulting proposals, workshops, lessons, email, Slack).\n"
 "Text inside quotation marks is quoted from someone else; do not count it against the author.\n"
 "Draft ({surface}):\n<text>\n{text}\n</text>\n\n"
 "Does this text contain AI-slop or filler that a careful editor would cut or fix before sending (throat-clearing, buzzwords, "
 "templated 'not X, it's Y' contrasts, padded triads, empty headers/bold/bullets, recaps, restating the ask, sign-off offers, "
 "vague grand claims)? Precise, specific copy with an occasional adverb, em dash, passive, or plain negation is NOT slop.\n"
 'Reply with JSON only: {{"slop": true|false, "why": "<=15 words"}}')
PAIR_P = ("You are a strict but fair editor of professional writing (consulting proposals, workshops, lessons, email, Slack).\n"
 "Text inside quotation marks is quoted from someone else; do not count it against the author.\n"
 "ORIGINAL draft ({surface}):\n<original>\n{orig}\n</original>\n\nEDITED version:\n<edited>\n{out}\n</edited>\n\n"
 "Judge the EDITED version.\n"
 "1. slop: does EDITED still contain AI-slop or filler a careful editor would cut (throat-clearing, buzzwords, templated "
 "'not X, it's Y' contrasts, padded triads, empty structure, recaps, sign-off offers, vague grand claims)? Occasional adverbs, em dashes, passives, or plain negations are NOT slop.\n"
 "2. meaning_preserved: are all facts, numbers, names, dates, times, commitments, requests, and the author's intent kept, with nothing material added or dropped? "
 "Cutting empty filler or empty claims is fine. Changing, inventing, or dropping a concrete detail or commitment is not.\n"
 "3. vs_original: is EDITED better, about the same, or worse than ORIGINAL as copy to send?\n"
 "4. over_flattened: compared with ORIGINAL, did the edit make it stiffer, lose the author's voice or register (e.g., casual Slack turned formal), or strip legitimate emphasis/precision?\n"
 'Reply with JSON only: {{"slop": true|false, "meaning_preserved": true|false, "meaning_issue": "<=20 words or empty", '
 '"vs_original": "better"|"same"|"worse", "over_flattened": true|false}}')

def norm(s): return re.sub(r"\s+", " ", s).strip()

def parse(t):
    m = re.search(r"\{.*\}", t, re.S)
    return json.loads(m.group(0)) if m else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--judge", default="claude-opus-5-5")
    ap.add_argument("--inp", default=str(Path(__file__).parent / "raw_outputs.jsonl"))
    a = ap.parse_args()
    out_p = Path(__file__).parent / f"judgments_{a.judge}.jsonl"
    rs = [json.loads(l) for l in open(a.inp) if not json.loads(l).get("error")]
    done = {}
    if out_p.exists():
        for l in out_p.read_text().splitlines():
            j = json.loads(l)
            if not j["error"]: done[j["key"]] = j
    tasks = {}
    for r in rs:
        tasks[("orig", r["id"])] = ("orig", r, None)
        if norm(r["output"]) != norm(r["input"]):
            tasks[("pair", r["id"], norm(r["output"]))] = ("pair", r, r["output"])
    lock = threading.Lock()
    f = open(out_p, "a")
    def go(kv):
        key, (kind, r, out) = kv; ks = json.dumps(key)
        if ks in done: return
        p = ORIG_P.format(surface=r["surface"], text=r["input"]) if kind == "orig" else \
            PAIR_P.format(surface=r["surface"], orig=r["input"], out=out)
        try:
            raw, usage, lat, _ = R.call(a.judge, None, p, 1500)
            res = parse(raw); err = None if res else "unparsed"
        except Exception as e:
            raw, usage, res, err = None, R.zero(), None, str(e)[:200]
        rec = dict(key=ks, kind=kind, id=r["id"], output=out, verdict=res, raw=raw, usage=usage, error=err)
        with lock: f.write(json.dumps(rec) + "\n"); f.flush()
    todo = [kv for kv in tasks.items() if json.dumps(kv[0]) not in done]
    print(len(tasks), "unique judgments,", len(todo), "to do", file=sys.stderr)
    with ThreadPoolExecutor(6) as ex: list(ex.map(go, todo))
if __name__ == "__main__": main()
