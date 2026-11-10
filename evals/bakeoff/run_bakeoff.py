#!/usr/bin/env python3
"""Four-way anti-slop bakeoff with real Anthropic API calls.
Reads ANTHROPIC_API_KEY from env (never printed or written). Writes raw outputs + usage to JSONL."""
import json, sys, re, time, threading, argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import anthropic

EV = Path(__file__).resolve().parents[1]; ROOT = EV.parent
sys.path.insert(0, str(EV)); import heuristics as H

PRICES = {  # USD per MTok (input, output, cache_write_5m, cache_read), platform.claude.com pricing, Nov 9 2026
 "claude-haiku-5-5": (0.10, 0.50, 0.125, 0.01),
 "claude-sonnet-5-5": (2.0, 10.0, 2.50, 0.10),
 "claude-opus-5-5": (4.0, 20.0, 5.0, 0.20)}

SKILL = (ROOT / "SKILL.md").read_text()
SKILL_BODY = SKILL.split("---", 2)[2].strip() if SKILL.startswith("---") else SKILL
m = re.search(r"Put these lines in the repo, not a large skill:\n\n(.*?)\n\n## ", SKILL, re.S)
CONTRACT = "Writing style contract:\n" + m.group(1).strip()

USER_TMPL = ("Here is a draft {surface} message. Edit it so it is ready to send. "
             "If it is already ready to send, return it exactly as written.\n\n<draft>\n{text}\n</draft>\n\n"
             "Put the final text, and nothing else, inside <final></final> tags.")
SYSTEMS = {"S1_default": None, "S2_contract": CONTRACT, "S3_skill": SKILL_BODY}  # S4 = v2 gate + S3 on fail

GATE_PROMPT = ("You are a cheap prefilter for AI-slop in professional writing. Answer about the draft only; do not rewrite it.\n"
  "Text inside quotation marks is quoted from someone else and is not the author's slop.\n" + CONTRACT +
  "\n\nDraft ({surface}):\n<draft>\n{text}\n</draft>\n\n"
  "Does this draft need a rewrite because it reads like generic AI-generated or filler-heavy prose "
  "(throat-clearing, buzzwords, 'not X, it's Y' templates, padded triads, empty structure, recaps, sign-off offers)? "
  "Precise, specific copy with an occasional adverb, em dash, passive, or plain negation does NOT need a rewrite. "
  "Reply with exactly one word: REWRITE or PASS.")

client = anthropic.Anthropic(max_retries=2)
lock = threading.Lock(); STOP = threading.Event()

class Fatal(Exception): pass

def call(model, system, user, max_tokens=1024):
    if STOP.is_set(): raise Fatal("stopped")
    kw = dict(model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": user}])
    if system: kw["system"] = system
    t = time.time()
    try:
        r = client.messages.create(**kw)
    except (anthropic.AuthenticationError, anthropic.PermissionDeniedError, anthropic.RateLimitError) as e:
        STOP.set(); raise Fatal(f"{type(e).__name__} status={getattr(e,'status_code',None)}")
    except anthropic.BadRequestError as e:
        msg = str(getattr(e, "message", ""))
        if "credit" in msg.lower() or "billing" in msg.lower():
            STOP.set(); raise Fatal(f"credit/billing error status=400")
        raise
    u = r.usage
    usage = dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                 cache_creation_input_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
                 cache_read_input_tokens=getattr(u, "cache_read_input_tokens", 0) or 0)
    p = PRICES[model]
    usage["cost_usd"] = (usage["input_tokens"]*p[0] + usage["output_tokens"]*p[1] +
                         usage["cache_creation_input_tokens"]*p[2] + usage["cache_read_input_tokens"]*p[3]) / 1e6
    text = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    return text, usage, round(time.time()-t, 2), r.stop_reason

def extract(raw):
    mm = re.search(r"<final>\s*(.*?)\s*</final>", raw, re.S)
    return (mm.group(1).strip(), True) if mm else (raw.strip(), False)

def zero(): return dict(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0, cost_usd=0.0)

def run_one(item, model, system_name, out_f):
    text, surface = item["input"], item["surface"]
    rec = dict(id=item["id"], split=item["split"], category=item["category"], surface=surface,
               label=bool(item["should_rewrite"]), model=model, system=system_name, input=text)
    try:
        if system_name.startswith("S4"):
            gate_fail = H.v2_gate(text, surface); gate_usage = zero(); gate_raw = None
            if system_name == "S4b_gate_v2_or_haiku" and not gate_fail:
                gate_raw, gate_usage, _, _ = call("claude-haiku-5-5", None, GATE_PROMPT.format(surface=surface, text=text), 256)
                gate_fail = ("REWRITE" in gate_raw.upper()) or ("PASS" not in gate_raw.upper())  # fail closed on empty/unclear
            rec.update(gate_fail=gate_fail, gate_raw=gate_raw, gate_usage=gate_usage)
            if gate_fail:
                raw, usage, lat, stop = call(model, SKILL_BODY, USER_TMPL.format(surface=surface, text=text))
                out, ok = extract(raw)
            else:
                raw, usage, lat, stop, out, ok = None, zero(), 0.0, None, text, True
        else:
            raw, usage, lat, stop = call(model, SYSTEMS[system_name], USER_TMPL.format(surface=surface, text=text))
            out, ok = extract(raw)
        rec.update(raw=raw, output=out, tagged=ok, usage=usage, latency_s=lat, stop_reason=stop, error=None)
    except Fatal as e:
        rec.update(error=str(e)); print("FATAL", e, file=sys.stderr)
    except Exception as e:
        rec.update(error=f"{type(e).__name__}: {str(e)[:200]}")
    with lock:
        out_f.write(json.dumps(rec) + "\n"); out_f.flush()
    return rec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude-haiku-5-5,claude-sonnet-5-5")
    ap.add_argument("--systems", default="S1_default,S2_contract,S3_skill,S4_gate_v2,S4b_gate_v2_or_haiku")
    ap.add_argument("--splits", default="holdout,stress")
    ap.add_argument("--out", default=str(EV / "bakeoff" / "raw_outputs.jsonl"))
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    items = []
    for s in a.splits.split(","):
        for it in H.load_fixtures(EV / "fixtures" / s):
            it.setdefault("split", s); it.setdefault("category", Path("x").stem); items.append(it)
    done = set()
    op = Path(a.out)
    if op.exists():
        for l in op.read_text().splitlines():
            r = json.loads(l)
            if not r.get("error"): done.add((r["id"], r["model"], r["system"]))
    jobs = [(it, m, s) for m in a.models.split(",") for s in a.systems.split(",") for it in items
            if (it["id"], m, s) not in done]
    print(f"{len(jobs)} jobs", file=sys.stderr)
    with open(op, "a") as f, ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(lambda j: run_one(*j, f), jobs))
    print("stopped early" if STOP.is_set() else "done", file=sys.stderr)

if __name__ == "__main__":
    main()
