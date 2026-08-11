#!/usr/bin/env python3
"""Study 1 analysis plan (runnable stub).

Reads one or more Mirror session JSON exports and computes the pre-registered
dependent variables. Keeps the "how we analyze" story reproducible and
pre-registration-friendly. Stdlib only — no pandas/numpy required.

Usage
-----
  # Analyze exported session files (see pilot_runbook.md §5 for the export curl)
  python analysis_plan.py session1.json session2.json ...

  # Self-contained demo (no data needed)
  python analysis_plan.py --demo

Each session JSON is what the API returns for
  GET /api/safebars/mirror/sessions/{id}
i.e. the full session dict with lenses / scenarios / dissonance_edges /
replay_history / revisions / self_discovery.
"""

import argparse
import json
import re
import sys
from collections import defaultdict


# ----- DV helpers -----------------------------------------------------------

SELF_MARKERS = re.compile(r"\b(i|i'?m|i?ve|my|me|myself|we|our|we'?ve)\b", re.I)
SYS_MARKERS = re.compile(r"\b(the (tool|mirror|system|app)|it (told|said|showed|flagged|pointed)|the ai)\b", re.I)


def classify_realization(text):
    """SELF = user attributes the insight to themselves; SYSTEM = to the tool."""
    if not text:
        return "MISSING"
    self_hits = len(SELF_MARKERS.findall(text))
    sys_hits = len(SYS_MARKERS.findall(text))
    if sys_hits > self_hits:
        return "SYSTEM"
    if self_hits == 0 and sys_hits == 0:
        return "NEUTRAL"
    return "SELF"


def dvs_for_session(session):
    sd = session.get("self_discovery") or {}
    edges = session.get("dissonance_edges") or []
    lenses = session.get("lenses") or []

    # RQ1 / RQ3 — self-discovery attribution
    realizations = sd.get("realizations") or {}
    realized_items = [v for v in realizations.values() if v.get("realized")]
    n_realized = len(realized_items)
    klass = [classify_realization(v.get("realized", "")) for v in realized_items]
    self_count = sum(1 for k in klass if k == "SELF")
    system_count = sum(1 for k in klass if k == "SYSTEM")

    # RQ2 — disc style effect: within-session, did withhold tensions yield more SELF?
    by_style = defaultdict(lambda: {"SELF": 0, "SYSTEM": 0, "NEUTRAL": 0, "n": 0})
    for v in realized_items:
        style = v.get("style", "unknown")
        by_style[style][classify_realization(v.get("realized", ""))] += 1
        by_style[style]["n"] += 1

    # RQ4 — evidence coverage improvement after revision (proxy for real change)
    history = session.get("replay_history") or []
    last = (history[-1] or {}).get("summary", {}) if history else {}
    changed_lens = int(last.get("changed_lens_count", 0) or 0)
    resolved_edges = int(last.get("resolved_edges", 0) or 0)
    open_edges = int(last.get("open_edges", 0) or 0)

    # Delta groups = distinct affected parties the mirror inferred (blind-spot surface)
    parties = {e.get("affected_party") for e in edges if e.get("affected_party")}
    attention_parties = sum(1 for e in edges if e.get("attention_required"))

    # Mindset / agency Likert live in the post-questionnaire (roster join), not the
    # session. Stub the join key so the pipeline is end-to-end.
    return {
        "session_id": session.get("id"),
        "condition": sd.get("condition") or {
            "cond": "?", "disc": "?", "align": "?",
        },
        "n_tensions": len(edges),
        "n_attention_tensions": attention_parties,
        "n_distinct_affected_parties": len(parties),
        "n_realized": n_realized,
        "self_discovery_SELF": self_count,
        "self_discovery_SYSTEM": system_count,
        "self_discovery_rate": round(self_count / n_realized, 3) if n_realized else None,
        "by_disc_style": {k: dict(v) for k, v in by_style.items()},
        "coverage_changed_lens": changed_lens,
        "coverage_resolved_edges": resolved_edges,
        "coverage_open_edges": open_edges,
        "anticipated_raw": sd.get("anticipated"),
        "realized_text_sample": (realized_items[0].get("realized", "")[:120] if realized_items else None),
    }


def aggregate(rows):
    """Pool-level summary used for the pre-registered ANCOVA readout."""
    agg = {
        "n_sessions": len(rows),
        "by_condition": defaultdict(lambda: {"n": 0, "self_rate_sum": 0.0, "n_realized": 0}),
    }
    for r in rows:
        cond = (r["condition"].get("cond"), r["condition"].get("disc"), r["condition"].get("align"))
        cell = agg["by_condition"][cond]
        cell["n"] += 1
        if r["self_discovery_rate"] is not None:
            cell["self_rate_sum"] += r["self_discovery_rate"]
        cell["n_realized"] += r["n_realized"]
    out = {"n_sessions": len(rows), "cells": {}}
    for cond, cell in agg["by_condition"].items():
        out["cells"]["/".join(cond)] = {
            "n": cell["n"],
            "mean_self_discovery_rate": round(cell["self_rate_sum"] / cell["n"], 3) if cell["n"] else None,
            "total_realized": cell["n_realized"],
        }
    return out


def main():
    ap = argparse.ArgumentParser(description="Study 1 DV extractor")
    ap.add_argument("files", nargs="*", help="session JSON files")
    ap.add_argument("--demo", action="store_true", help="run on a synthetic session")
    args = ap.parse_args()

    if args.demo:
        args.files = [_demo_session()]

    rows = []
    for f in args.files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                session = json.load(fh)
        except Exception as e:  # noqa
            print(f"! cannot read {f}: {e}", file=sys.stderr)
            continue
        rows.append(dvs_for_session(session))

    if not rows:
        print("No sessions parsed.", file=sys.stderr)
        return 1

    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    print("\n=== AGGREGATE ===")
    print(json.dumps(aggregate(rows), ensure_ascii=False, indent=2))
    return 0


def _demo_session():
    import tempfile, os
    sess = {
        "id": "demo_001",
        "dissonance_edges": [
            {"id": "e1", "affected_party": "non-consenting peers", "attention_required": True,
             "consequence": "Silent counselor alerts expose peers the user never opted to involve."},
            {"id": "e2", "affected_party": "future deployers", "attention_required": True,
             "consequence": "Downstream teams inherit the biased model with no audit trail."},
        ],
        "lenses": [{"id": "l1", "label": "Privacy", "state": "Reasoned"}],
        "replay_history": [{"summary": {"changed_lens_count": 2, "resolved_edges": 1, "open_edges": 1}}],
        "self_discovery": {
            "condition": {"cond": "multimodal", "disc": "split", "align": "critical"},
            "anticipated": "not",
            "realizations": {
                "e1": {"edge_id": "e1", "style": "withhold", "anticipated": "not",
                       "realized": "I never thought the silent alert would also pull in peers who didn't consent.",
                       "party": "non-consenting peers", "saved_at": "2026-08-12T10:00:00Z"},
                "e2": {"edge_id": "e2", "style": "prescribe", "anticipated": "not",
                       "realized": "The tool told me future deployers get a biased model; I'll add an audit log.",
                       "party": "future deployers", "saved_at": "2026-08-12T10:01:00Z"},
            },
            "realized": "I never thought the silent alert would also pull in peers who didn't consent.  |  The tool told me future deployers get a biased model; I'll add an audit log.",
        },
    }
    p = os.path.join(tempfile.gettempdir(), "study1_demo_session.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(sess, fh)
    return p


if __name__ == "__main__":
    sys.exit(main())
