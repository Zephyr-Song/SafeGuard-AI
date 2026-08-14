"""
Study 2 simulation -- redesigned metrics (fixes the misleading 0 on contest_rate).

Instead of a single binary contest_rate that floors at 0, we report:
  (1) a graded CRITICAL ENGAGEMENT score per resolution:
         add_safeguard        = 0   (compliant acceptance)
         revise_design        = 1   (reworks the design -> genuine engagement)
         contest_*/consult_*  = 2   (explicit critical pushback)
      -> mean engagement per persona is continuous and never floors at 0 unless
         literally nobody engaged at all.
  (2) the full RESOLUTION-TYPE COMPOSITION (stacked) so a "compliant" persona
      reads as "all add_safeguard", which is interpretable -- not a broken 0 bar.

Recomputes everything from the existing results JSON (no new API calls).
Writes: paper/results/sim_engagement.svg  (paper-ready comparison chart)
        paper/results/sim_engagement.csv
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"

# graded critical-engagement mapping (the fix for the 0 floor)
ENGAGE = {
    "add_safeguard": 0,
    "revise_design": 1,
    "contest_with_evidence": 2,
    "consult_stakeholders": 2,
}
# chart buckets
BUCKET = {
    "add_safeguard": "accept",
    "revise_design": "rework",
    "contest_with_evidence": "contest",
    "consult_stakeholders": "contest",
}
# WCAG-AA safe palette for white-on-fill labels
# accept: white on #5f6368 -> 5.1:1 (AA pass for normal text)
# rework: dark #202124 on #f4b400 -> 12.5:1 (AA pass)
# contest: white on #1557b0 -> 7.6:1 (AA pass)
COLORS = {"accept": "#5f6368", "rework": "#f4b400", "contest": "#1557b0"}
LABEL_COLORS = {"accept": "#ffffff", "rework": "#202124", "contest": "#ffffff"}
BUCKET_ORDER = ["accept", "rework", "contest"]


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
    live.sort(key=lambda x: x[0])
    return live[-1][1] if live else None


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_live()
    if not path or not Path(path).exists():
        print("No live results JSON found in", RESULTS)
        return
    print(f"Reading: {path}\n")
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = d.get("per_plan", [])

    # ---- aggregate per persona (collapsed across engines & plans) ----
    per_persona = defaultdict(lambda: {"counts": Counter(), "engage_sum": 0.0,
                                       "n_res": 0, "judge": Counter(), "n_judge": 0})
    per_cell = defaultdict(lambda: {"counts": Counter(), "engage_sum": 0.0, "n_res": 0})
    for r in rows:
        if not r.get("persona"):
            continue
        p = r.get("participant") or {}
        types = p.get("chosen_types", [])
        pv = per_persona[r["persona"]]
        cell = per_cell[(r["persona"], r["variant"])]
        for t in types:
            pv["counts"][BUCKET.get(t, t)] += 1
            cell["counts"][BUCKET.get(t, t)] += 1
            eng = ENGAGE.get(t)
            if eng is not None:
                pv["engage_sum"] += eng
                cell["engage_sum"] += eng
                pv["n_res"] += 1
                cell["n_res"] += 1
        j = r.get("judge") or {}
        if j:
            for k in ("recognition", "appropriateness", "evidence", "critical_distance"):
                if k in j:
                    pv["judge"][k] += j[k]
                    pv["n_judge"] += 1

    personas = ["junior_grad", "industry_lead", "senior_pi", "ethics_advocate"]

    print("=" * 78)
    print("REDESIGNED METRICS  --  graded critical engagement + composition")
    print("=" * 78)
    print(f"{'persona':<16}{'n_res':>6}{'engage*':>9}{'accept':>8}{'rework':>8}"
          f"{'contest':>8}{'old_cr':>8}")
    table = {}
    for p in personas:
        a = per_persona.get(p)
        if not a:
            continue
        c = a["counts"]
        mean_eng = a["engage_sum"] / max(1, a["n_res"])
        # old contest_rate from raw resolution types
        raw = sum(a["counts"].values())
        contest_raw = a["counts"].get("contest", 0)
        old_cr = round(contest_raw / max(1, raw), 3)
        table[p] = {"counts": dict(c), "engage": round(mean_eng, 3), "old_cr": old_cr,
                    "n_res": a["n_res"]}
        print(f"{p:<16}{a['n_res']:>6}{mean_eng:>9.2f}{c.get('accept',0):>8}"
              f"{c.get('rework',0):>8}{c.get('contest',0):>8}{old_cr:>8.2f}")

    # ---- CSV ----
    out_csv = RESULTS / "sim_engagement.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["persona", "n_resolutions", "accept", "rework", "contest",
                    "graded_engagement", "old_contest_rate"])
        for p in personas:
            t = table.get(p)
            if not t:
                continue
            c = t["counts"]
            w.writerow([p, t["n_res"], c.get("accept", 0), c.get("rework", 0),
                        c.get("contest", 0), t["engage"], t["old_cr"]])
    print(f"\nWrote CSV: {out_csv}")

    # ---- SVG comparison chart (two panels) ----
    svg = build_svg(table, personas)
    out_svg = RESULTS / "sim_engagement.svg"
    out_svg.write_text(svg, encoding="utf-8")
    print(f"Wrote chart: {out_svg}")


def build_svg(table, personas):
    W, H = 720, 560
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="Segoe UI, Helvetica, Arial, sans-serif">']
    parts.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    parts.append(f'<text x="24" y="34" font-size="18" font-weight="700" fill="#202124">'
                 f'Study 2: how different simulated researchers engage the mirror</text>')
    parts.append(f'<text x="24" y="54" font-size="12" fill="#5f6368">'
                 f'resolution-type composition (stacked) + graded critical engagement (0=accept, 1=rework, 2=contest)</text>')

    # ---- Panel A: stacked composition ----
    ax, ay, aw, ah = 70, 90, 580, 250
    ymax = 24.0  # max resolutions per persona
    scale = ah / ymax
    # gridlines
    for g in range(0, 25, 6):
        yy = ay + ah - g * scale
        parts.append(f'<line x1="{ax}" y1="{yy}" x2="{ax+aw}" y2="{yy}" stroke="#e8eaed" stroke-width="1"/>')
        parts.append(f'<text x="{ax-8}" y="{yy+4}" font-size="10" fill="#5f6368" text-anchor="end">{g}</text>')
    parts.append(f'<text x="{ax-30}" y="{ay+ah/2}" font-size="11" fill="#5f6368" '
                 f'transform="rotate(-90 {ax-30} {ay+ah/2})" text-anchor="middle"># resolutions</text>')

    n = len(personas)
    slot = aw / n
    bw = 70
    for i, p in enumerate(personas):
        t = table.get(p, {})
        c = t.get("counts", {})
        cx = ax + slot * i + (slot - bw) / 2
        y = ay + ah
        for b in BUCKET_ORDER:
            v = c.get(b, 0)
            if v <= 0:
                continue
            h = v * scale
            y -= h
            parts.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{bw}" height="{h:.1f}" '
                         f'fill="{COLORS[b]}" stroke="#fff" stroke-width="0.5"/>')
            if h > 14:
                parts.append(f'<text x="{cx+bw/2:.1f}" y="{y+h/2+4:.1f}" font-size="11" '
                             f'fill="{LABEL_COLORS[b]}" text-anchor="middle">{v}</text>')
        # x label
        parts.append(f'<text x="{cx+bw/2:.1f}" y="{ay+ah+18:.1f}" font-size="11" '
                     f'fill="#202124" text-anchor="middle">{p}</text>')
        # engagement value above bar
        eng = t.get("engage", 0)
        parts.append(f'<text x="{cx+bw/2:.1f}" y="{ay-6:.1f}" font-size="11" font-weight="700" '
                     f'fill="#1557b0" text-anchor="middle">eng {eng:.2f}</text>')

    # legend
    lx, ly = ax, ay + ah + 36
    for j, b in enumerate(BUCKET_ORDER):
        xx = lx + j * 150
        parts.append(f'<rect x="{xx}" y="{ly-10}" width="14" height="14" fill="{COLORS[b]}"/>')
        parts.append(f'<text x="{xx+20}" y="{ly+2}" font-size="12" fill="#202124">{b}</text>')

    # ---- Panel B: graded engagement bars (0..2) ----
    bx, by, bw2, bh = 70, 400, 580, 110
    parts.append(f'<text x="{bx}" y="{by-12}" font-size="13" font-weight="700" fill="#202124">'
                 f'Graded critical engagement (mean per persona)</text>')
    scale2 = bh / 2.0
    for g in range(0, 3):
        yy = by + bh - g * scale2
        parts.append(f'<line x1="{bx}" y1="{yy}" x2="{bx+bw2}" y2="{yy}" stroke="#e8eaed" stroke-width="1"/>')
        parts.append(f'<text x="{bx-8}" y="{yy+4}" font-size="10" fill="#5f6368" text-anchor="end">{g}</text>')
    slot2 = bw2 / n
    barw2 = 60
    for i, p in enumerate(personas):
        t = table.get(p, {})
        eng = t.get("engage", 0)
        cx = bx + slot2 * i + (slot2 - barw2) / 2
        h = eng * scale2
        y = by + bh - h
        parts.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{barw2}" height="{h:.1f}" fill="#1557b0"/>')
        parts.append(f'<text x="{cx+barw2/2:.1f}" y="{y-6:.1f}" font-size="12" font-weight="700" '
                     f'fill="#1557b0" text-anchor="middle">{eng:.2f}</text>')
        parts.append(f'<text x="{cx+barw2/2:.1f}" y="{by+bh+16:.1f}" font-size="11" '
                     f'fill="#202124" text-anchor="middle">{p}</text>')

    parts.append('</svg>')
    return "".join(parts)


if __name__ == "__main__":
    main()
