#!/usr/bin/env python3
"""Runs the gate comparison on dev and holdout and prints a JSON report. No model calls."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import heuristics as v2
import heuristics_v1 as v1

root = Path(__file__).parent / "fixtures"
gates = {
    "v1 (starter gate)": lambda t, s: v1.should_rewrite(v1.score(t), s),
    "v2 (verify-copy, tuned on dev)": v2.v2_gate,
    "stop-slop presence ban-list": v2.stopslop_presence,
    "always rewrite (always-on skill as gate)": lambda t, s: True,
}
out = {}
for split in ("dev", "holdout", "stress", ""):
    fx = v2.load_fixtures(root / split if split else root)
    out[split or "all"] = {g: v2.evaluate(fx, f) for g, f in gates.items()}
    misses = [it["id"] for it in fx if v2.v2_gate(it["input"], it["surface"]) != it["should_rewrite"]]
    out[(split or "all") + "_v2_misses"] = misses
print(json.dumps(out, indent=1))
