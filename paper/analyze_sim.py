"""
Analyze Study 2 live simulation results (multi_model_eval.py output).

Reads the newest *live* results JSON from paper/results/, prints per-persona and
per-variant tables, and writes a cleaned CSV of persona x plan x variant metrics.
This is a computational-simulation analysis: it characterizes the engine and how
*different simulated researchers* engage the mirror. It is NOT human data and
does not answer RQ1-RQ4 (those need the human Study 1).

Usage:
    python paper/analyze_sim.py                # newest live json
    python paper/analyze_sim.py <path.json>    # specific file
"""
import csv
import json
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"


def latest_live():
    cands = [p for p in RESULTS.glob("multi_model_eval_*.json")]
    live = []
    for p in cands:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("mode") == "live":
            live.append((d.get("generated_at", ""), p))
    if not live:
        return None
    live.sort(key=lambda x: x[0])
    return live[-1][1]


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_live()
    if not path or not Path(path).exists():
        print("No live results JSON found in", RESULTS)
        return
    print(f"Reading: {path}\n")
    d = json.loads(Path(path).read_text(encoding="utf-8"))

    rows = d.get("per_plan", [])
    persona_summary = d.get("persona_summary", [])
    summary = d.get("summary", [])

    # --- per persona (researcher effect) ---
    print("=" * 78)
    print("PERSONA (simulated researcher) SUMMARY  --  the 'different researchers' view")
    print("=" * 78)
    print(f"{'persona':<16}{'runs':>5}{'contest_rate':>14}{'recog':>7}{'appro':>7}"
          f"{'evid':>7}{'crit_dist':>10}")
    for e in persona_summary:
        j = e.get("avg_judge", {})
        print(f"{e['persona']:<16}{e['n_runs']:>5}{e['avg_contest_rate']:>14}"
              f"{j.get('recognition','-'):>7}{j.get('appropriateness','-'):>7}"
              f"{j.get('evidence','-'):>7}{j.get('critical_distance','-'):>10}")
        rc = e.get("resolution_counts", {})
        print(f"    resolution mix: " + ", ".join(f"{k}={v}" for k, v in rc.items()))

    # --- per variant (engine effect) ---
    print("\n" + "=" * 78)
    print("VARIANT (engine) SUMMARY  --  the 'engine characterization' view (RQ5)")
    print("=" * 78)
    for e in summary:
        print(f"\n[{e['variant']}]  avg_edges/plan={e['avg_edges_per_plan']}  "
              f"avg_role_probes/plan={e['avg_role_probes_per_plan']}  "
              f"coverage={e['coverage_states_total']}")
        if "avg_contest_rate" in e:
            print(f"    avg_contest_rate={e['avg_contest_rate']}  avg_judge={e.get('avg_judge')}")

    # --- persona x variant contest_rate matrix ---
    print("\n" + "=" * 78)
    print("CONTEST_RATE matrix  (persona rows x variant cols)  -- researcher x engine")
    print("=" * 78)
    personas = sorted({r.get("persona") for r in rows if r.get("persona")})
    variants = sorted({r["variant"] for r in rows})
    print(f"{'persona':<16}" + "".join(f"{v:>22}" for v in variants))
    for p in personas:
        line = f"{p:<16}"
        for v in variants:
            cell = [r for r in rows if r.get("persona") == p and r["variant"] == v]
            crs = [r["participant"]["contest_rate"] for r in cell if r.get("participant")]
            line += f"{(sum(crs)/len(crs) if crs else float('nan')):>22.3f}"
        print(line)

    # --- cleaned CSV ---
    out = RESULTS / "sim_persona_plan_variant.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["persona", "variant", "plan_id", "plan_title", "n_edges",
                    "n_role_probes", "judge_evidence", "judge_critical_distance",
                    "contest_rate", "resolution_types"])
        for r in rows:
            if not r.get("persona"):
                continue
            j = r.get("judge") or {}
            p = r.get("participant") or {}
            w.writerow([r["persona"], r["variant"], r["plan_id"], r["plan_title"],
                        r["n_edges"], r["n_role_probes"], j.get("evidence", ""),
                        j.get("critical_distance", ""), p.get("contest_rate", ""),
                        ";".join(p.get("chosen_types", []))])
    print(f"\nWrote cleaned CSV: {out}")


if __name__ == "__main__":
    main()
