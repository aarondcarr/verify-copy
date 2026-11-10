#!/usr/bin/env python3
"""Deterministic slop prefilter (v2). No model calls.

v1 -> v2 changes (tuned on fixtures/dev only; see spike-results.md):
  * ignore text inside quotation marks (quoting a client is not slop)
  * add Opus 5.5 residual tells reported by Graphite (Oct 1, 2026): "this matters", "why X matters",
    "is more than an X, it's a Y", "rather than simply", "looking ahead", "adds another layer",
    "what comes next", evaluative "dependable"/"steady"
  * add structural signals: restating the ask, recaps, markdown scaffolding on short text,
    stacked "X, Y, and Z" triads
  * soft signals need >= 2 to trip; hard tells / contrast templates / sign-offs trip alone
  * per-100 rates still ignored under 80 words (short-text lesson from the starter set)

Also includes `stopslop_presence`, a ban-list gate modeled on stop-slop's Quick Checks
(any adverb, any em dash, any passive, Wh- openers, any "not X" contrast). It is a baseline
for measuring over-correction, not a recommendation.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HARD_TELLS = [
    r"\bhere's the thing\b", r"\bhere's what i\b", r"\blet me be clear\b", r"\bthe uncomfortable truth\b",
    r"\bit turns out\b", r"\bthe real (?:story|question|issue|insight|reason)\b", r"\blet that sink in\b",
    r"\bfull stop\b", r"\bthis matters because\b", r"\bmake no mistake\b", r"\bin this section we(?:'ll| will)\b",
    r"\bas we(?:'ll| will) see\b", r"\blet me walk you through\b", r"\bthe rest of this document\b",
    r"\bi hope this (?:email )?finds you well\b",
]
SIGNOFF = r"hope this helps|happy to dive|let me know if you(?:'d| would) like me to|let me know if you'd like"

# contrast templates (trip alone)
RESIDUAL = [
    r"\bit(?:'s| is) not\b[^.!?]{0,80}\bit(?:'s| is)\b",
    r"\bthis isn(?:'t| not)\b[^.!?]{0,80}\bit(?:'s| is)\b",
    r"\bisn(?:'t| not)\s+[^.!?]{0,80}[.!]\s+it(?:'s| is)\b",
    r"\b(?:is|are) more than (?:a |an |just )?[\w-]+(?:\s[\w-]+)?\s*(?:,|—|--)\s*(?:it|they)(?:'s|'re| is| are)\b",
]
# Opus 5.5 residual phrases (soft)
RESIDUAL_55 = [
    r"\bthis matters\b(?! because)", r"\bwhy [\w ]{1,30} matters?\b", r"\bmatters most\b", r"\bjust as important\b",
    r"\brather than simply\b", r"\blooking ahead\b", r"\badds another layer\b", r"\bwhat comes next\b",
    r"\bnot only about\b",
]
JARGON = [
    r"\bunpack\b", r"\bnavigate\b", r"\blean into\b", r"\bgame[- ]changer\b", r"\bdeep dive\b", r"\bdive deeper\b",
    r"\bcircle back\b", r"\btouch base\b", r"\bmoving forward\b", r"\blandscape\b", r"\bload-bearing\b",
    r"\bearns its keep\b", r"\bdependable\b", r"\bsteady\b",
]
STRUCT_ASK = [r"\byou asked\b", r"\bto answer your question\b", r"\bto summarize your question\b",
              r"\bin summary\b", r"\bin conclusion\b", r"\bto recap\b", r"\bthis section provides\b"]
ADVERBS = [r"\breally\b", r"\bjust\b", r"\bliterally\b", r"\bgenuinely\b", r"\bhonestly\b", r"\bsimply\b",
           r"\bactually\b", r"\bcrucially\b", r"\bquietly\b", r"\btruly\b"]
TRIAD = r"\b[\w-]+(?: [\w-]+)?, [\w-]+(?: [\w-]+)?,? and [\w-]+"
WORD = re.compile(r"\b[\w']+\b")
QUOTE = re.compile(r"\"[^\"]*\"|“[^”]*”")


def words(text: str) -> list[str]:
    return WORD.findall(text.lower())


def n(text: str, patterns) -> int:
    if isinstance(patterns, str):
        patterns = [patterns]
    return sum(len(re.findall(p, text, flags=re.I | re.M)) for p in patterns)


def score(text: str) -> dict:
    body = QUOTE.sub(" ", text)
    w = words(body)
    nw = max(len(w), 1)
    dashes = body.count("—") + len(re.findall(r"\s--\s", body))
    struct_marks = len(re.findall(r"^\s*(?:#{1,6} |[-*] )", body, re.M)) + len(re.findall(r"\*\*[^*]+\*\*", body))
    return {
        "words": len(w),
        "hard_tells": n(body, HARD_TELLS),
        "residual_templates": n(body, RESIDUAL),
        "residual_55": n(body, RESIDUAL_55),
        "jargon": n(body, JARGON),
        "restate_recap": n(body, STRUCT_ASK),
        "struct_marks": struct_marks,
        "triads": n(body, TRIAD),
        "adverbials_per_100": round(100 * n(body, ADVERBS) / nw, 2),
        "em_dashes_per_100": round(100 * dashes / nw, 2),
        "signoff": int(bool(re.search(SIGNOFF, body, re.I))),
    }


def soft_points(s: dict) -> int:
    pts = s["residual_55"] + s["jargon"] + s["restate_recap"]
    if s["words"] < 80 and s["struct_marks"] >= 3:
        pts += 2  # scaffolding on a short point
    if s["triads"] >= 2:
        pts += 1
    return pts


def should_rewrite(s: dict, surface: str = "proposal") -> bool:
    if s["hard_tells"] or s["signoff"] or s["residual_templates"]:
        return True
    if soft_points(s) >= 2:
        return True
    # Per-100 rates are noisy on short drafts (one adverb in 20 words is 5/100).
    if s["words"] < 80:
        return False
    adverb_cap = 4.0 if surface == "slack" else 3.0
    dash_cap = 3.0 if surface in {"proposal", "workshop", "lesson"} else 4.0
    return s["adverbials_per_100"] >= adverb_cap or s["em_dashes_per_100"] >= dash_cap


# ---- baseline: stop-slop-style presence ban list (for over-correction measurement) ----
PASSIVE = r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?\w+(?:ed|en)\b"
def stopslop_presence(text: str, surface: str = "proposal") -> bool:
    t = text
    any_adverb = bool(re.search(r"\b\w{3,}ly\b", t, re.I)) or n(t, ADVERBS) > 0
    return bool(
        any_adverb or "—" in t or re.search(PASSIVE, t, re.I)
        or re.search(r"(?:^|[.!?]\s+)(?:what|when|why|where|who|how)\b", t, re.I | re.M)
        or re.search(r"\b(?:not|isn't|aren't|wasn't)\b", t, re.I)
        or re.search(r"\bhere's (?:what|this|that|the)\b", t, re.I)
    )


def load_fixtures(path: Path) -> list[dict]:
    files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
    out = []
    for f in files:
        data = json.loads(f.read_text())
        out.extend(data if isinstance(data, list) else [data])
    return out


def metrics(rows) -> dict:
    tp = sum(p and l for p, l in rows); fp = sum(p and not l for p, l in rows)
    fn = sum((not p) and l for p, l in rows); tn = sum((not p) and (not l) for p, l in rows)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return dict(n=len(rows), tp=tp, fp=fp, fn=fn, tn=tn, precision=round(prec, 3), recall=round(rec, 3),
                f1=round(f1, 3), flag_rate=round((tp + fp) / len(rows), 3) if rows else 0.0)


def evaluate(fixtures, gate) -> dict:
    by = defaultdict(list); allrows = []
    for it in fixtures:
        p = gate(it["input"], it.get("surface", "proposal")); l = bool(it.get("should_rewrite"))
        allrows.append((p, l)); by[it.get("category", "?")].append((p, l))
    return {"all": metrics(allrows), **{k: metrics(v) for k, v in sorted(by.items())}}


def v2_gate(text, surface):
    return should_rewrite(score(text), surface)


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent / "fixtures"
    if target.is_dir() or (target.exists() and target.suffix == ".json"):
        fixtures = load_fixtures(target)
        for item in fixtures:
            s = score(item["input"])
            pred = should_rewrite(s, item.get("surface", "proposal"))
            print(json.dumps({"id": item.get("id"), "pred": pred, "label": bool(item.get("should_rewrite")),
                              "ok": pred == bool(item.get("should_rewrite")), **s}))
        res = evaluate(fixtures, v2_gate)
        print(json.dumps({"gate": "verify-copy v2", **res["all"],
                          "note": "Synthetic fixtures. Too small to conclude if n < 30 per cell."}))
        return 0
    text = " ".join(argv[1:])
    s = score(text)
    print(json.dumps({"should_rewrite": should_rewrite(s), **s}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
