#!/usr/bin/env python3
"""Deterministic slop prefilter. No model calls."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HARD_TELLS = [
    r"\bhere's the thing\b",
    r"\bhere's what i\b",
    r"\blet me be clear\b",
    r"\bthe uncomfortable truth\b",
    r"\bit turns out\b",
    r"\bthe real (?:story|question|issue|insight|reason)\b",
    r"\blet that sink in\b",
    r"\bfull stop\b",
    r"\bthis matters because\b",
    r"\bmake no mistake\b",
    r"\bin this section we(?:'ll| will)\b",
    r"\bas we(?:'ll| will) see\b",
    r"\blet me walk you through\b",
    r"\bthe rest of this document\b",
    r"\blet me know if you(?:'d| would) like me to (?:expand|dive|go deeper)\b",
    r"\bhappy to dive deeper\b",
    r"\bhope this helps\b",
]

RESIDUAL = [
    r"\bit(?:'s| is) not\b[^.!?]{0,80}\bit(?:'s| is)\b",
    r"\bthis isn(?:'t| not)\b[^.!?]{0,80}\bit(?:'s| is)\b",
    r"\bisn(?:'t| not)\s+[^.!?]{0,80}[.!]\s+it(?:'s| is)\b",
]

JARGON = [
    r"\bunpack\b",
    r"\bnavigate\b",
    r"\blean into\b",
    r"\bgame[- ]changer\b",
    r"\bdeep dive\b",
    r"\bcircle back\b",
    r"\bmoving forward\b",
    r"\blandscape\b",
    r"\bload-bearing\b",
    r"\bearns its keep\b",
]

ADVERBS = [
    r"\breally\b",
    r"\bjust\b",
    r"\bliterally\b",
    r"\bgenuinely\b",
    r"\bhonestly\b",
    r"\bsimply\b",
    r"\bactually\b",
    r"\bcrucially\b",
    r"\bquietly\b",
]

WORD = re.compile(r"\b[\w']+\b")


def words(text: str) -> list[str]:
    return WORD.findall(text.lower())


def count_patterns(text: str, patterns: list[str]) -> int:
    t = text.lower()
    return sum(len(re.findall(p, t, flags=re.I)) for p in patterns)


def score(text: str) -> dict:
    w = words(text)
    n = max(len(w), 1)
    hard = count_patterns(text, HARD_TELLS)
    residual = count_patterns(text, RESIDUAL)
    jargon = count_patterns(text, JARGON)
    adverbs = count_patterns(text, ADVERBS)
    dashes = text.count("—") + len(re.findall(r"\s--\s", text))
    return {
        "words": len(w),
        "hard_tells": hard,
        "residual_templates": residual,
        "jargon": jargon,
        "adverbials_per_100": round(100 * adverbs / n, 2),
        "em_dashes_per_100": round(100 * dashes / n, 2),
        "signoff": int(bool(re.search(r"hope this helps|happy to dive|let me know if you", text, re.I))),
    }


def should_rewrite(s: dict, surface: str = "proposal") -> bool:
    # Rate-based, not presence-based, except hard tells and sign-offs.
    if s["hard_tells"] or s["signoff"] or s["residual_templates"]:
        return True
    if s["jargon"] >= 2:
        return True
    # Per-100 rates are noisy on short drafts (one adverb in 20 words is 5/100).
    if s["words"] < 80:
        return False
    adverb_cap = 4.0 if surface == "slack" else 3.0
    dash_cap = 3.0 if surface in {"proposal", "workshop", "lesson"} else 4.0
    if s["adverbials_per_100"] >= adverb_cap:
        return True
    if s["em_dashes_per_100"] >= dash_cap:
        return True
    return False


def load_fixtures(path: Path) -> list[dict]:
    files = sorted(path.glob("*.json")) if path.is_dir() else [path]
    out = []
    for f in files:
        data = json.loads(f.read_text())
        if isinstance(data, list):
            out.extend(data)
        else:
            out.append(data)
    return out


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent / "fixtures"
    if target.is_dir() or (target.exists() and target.suffix == ".json"):
        fixtures = load_fixtures(target)
        tp = fp = fn = tn = 0
        for item in fixtures:
            s = score(item["input"])
            pred = should_rewrite(s, item.get("surface", "proposal"))
            label = bool(item.get("should_rewrite"))
            if pred and label:
                tp += 1
            elif pred and not label:
                fp += 1
            elif (not pred) and label:
                fn += 1
            else:
                tn += 1
            print(json.dumps({"id": item.get("id"), "pred": pred, "label": label, **s}))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        print(
            json.dumps(
                {
                    "n": len(fixtures),
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "tn": tn,
                    "precision": round(prec, 3),
                    "recall": round(rec, 3),
                    "f1": round(f1, 3),
                    "note": "Heuristic gate only. Too small to conclude if n < 30.",
                }
            )
        )
        return 0
    text = Path(argv[1]).read_text() if target.exists() else " ".join(argv[1:])
    s = score(text)
    print(json.dumps({"should_rewrite": should_rewrite(s), **s}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
