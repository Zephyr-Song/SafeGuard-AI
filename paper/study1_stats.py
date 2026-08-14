#!/usr/bin/env python3
"""Study 1 inferential statistics -> publication-ready LaTeX tables.

Reads:
  * session JSON exports (full Mirror session dicts, as returned by
    GET /api/safebars/mirror/sessions/{id})  -- DV extraction via analysis_plan
  * a participant ROSTER csv with one row per participant, columns:
        code, session_id, cond, disc, align,
        pre_robustness (1-7),
        SD1..SD4, MC1..MC3, AG1..AG4, CD1..CD3, TR1..TR3,
        [pre_groups_n, post_groups_n]   # optional, for RQ4 Delta-groups

Runs the PRE-REGISTERED tests (H1/H3/H4) plus exploratory (RQ2, RQ-align) and
emits LaTeX tabular blocks + a JSON summary. Stdlib only; uses scipy if present
for exact p-values, else a normal approximation (clearly labelled "approx").

Usage
-----
  python study1_stats.py roster.csv session1.json session2.json ...
  python study1_stats.py --demo        # synthetic data, labelled DEMO

Output
------
  study1_results_tables.tex   (LaTeX fragment, paste into draft)
  study1_results.json         (machine-readable, for the OSF supplement)
"""
import argparse
import csv
import json
import math
import os
import random
import sys
from collections import defaultdict

try:
    import analysis_plan  # local: dvs_for_session, classify_realization
except Exception:  # pragma: no cover
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import analysis_plan

# ---- optional scipy for exact p-values -------------------------------------
try:
    from scipy import stats as sp
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


# ===== basic stats ==========================================================
def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def sd(xs):
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 2:
        return float("nan")
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def cohen_d(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    sa, sb = sd(a), sd(b)
    sp_ = math.sqrt(((na - 1) * sa ** 2 + (nb - 1) * sb ** 2) / (na + nb - 2))
    if sp_ == 0:
        return float("nan")
    return (mean(a) - mean(b)) / sp_


def _student_two_tailed_p(t, df):
    """Two-tailed p for Student's t. Exact if scipy, else normal approx."""
    if HAVE_SCIPY:
        return 2 * sp.t.cdf(-abs(t), df)
    # Abramowitz-Stegun normal approx for large df (labelled approx downstream)
    z = t / math.sqrt(1 + t * t / df) if df > 0 else t
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def welch_t(a, b):
    na, nb = len(a), len(b)
    va, vb = sd(a) ** 2, sd(b) ** 2
    if na < 2 or nb < 2 or va == 0 and vb == 0:
        return float("nan"), float("nan")
    t = (mean(a) - mean(b)) / math.sqrt(va / na + vb / nb)
    df = (va / na + vb / nb) ** 2 / (
        (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1) + 1e-12)
    return t, df


def paired_t(a, b):
    d = [x - y for x, y in zip(a, b) if x is not None and y is not None]
    n = len(d)
    if n < 2:
        return float("nan"), float("nan")
    md = sum(d) / n
    s = math.sqrt(sum((x - md) ** 2 for x in d) / (n - 1))
    if s == 0:
        return float("nan"), float("nan")
    t = md / (s / math.sqrt(n))
    return t, n - 1


def oneway_anova(groups):
    allv = [v for g in groups for v in g]
    gm = mean(allv)
    ss_between = sum(len(g) * (mean(g) - gm) ** 2 for g in groups)
    ss_within = sum(sum((v - mean(g)) ** 2 for v in g) for g in groups)
    k = len(groups)
    n = len(allv)
    if n - k < 1 or ss_within == 0:
        return float("nan"), float("nan"), float("nan")
    F = (ss_between / (k - 1)) / (ss_within / (n - k))
    df_num, df_den = k - 1, n - k
    if HAVE_SCIPY:
        p = 1 - sp.f.cdf(F, df_num, df_den)
    else:
        p = float("nan")  # labelled approx in caller if needed
    eta2 = ss_between / (ss_between + ss_within)
    return F, p, eta2


def mcnemar(b_a, b_b):
    """Paired binary: b_a/b_b are lists of 0/1 (e.g., SELF=1). Returns (n_discordant, p)."""
    disc = sum(1 for x, y in zip(b_a, b_b) if x != y)
    # exact binomial on the discordant pairs (arbitrary direction)
    if HAVE_SCIPY:
        p = sp.binomtest(disc, len(b_a)).pvalue
    else:
        p = float("nan")
    return disc, p


# ===== behavioral 'correction' evidence (plan-diff instrument) =============
def correction_metrics(session):
    """Behavioral correction evidence from the before/after plan-diff instrument
    (study1_plandiff_instrument.md). Returns
        {corrected_blind, surfaced_blind, rate}  or  None if not captured.
    was_blind  = the mirror's finding was NOT already in plan_before
    addressed  = the participant action-linked it (resolved_state) AND the
                 revision text appears in plan_after.
    """
    if not session:
        return None
    pb = (session.get("plan_before") or "").lower()
    pa = (session.get("plan_after") or "").lower()
    links = session.get("revision_links") or []
    if not links:
        return None
    corrected = 0
    surfaced = 0
    for r in links:
        summary = (r.get("finding_summary") or "").lower()
        rtext = (r.get("revision_text") or "").lower()
        was_blind = bool(summary) and summary not in pb
        addressed = (r.get("resolved_state") == "action_linked"
                     and bool(rtext) and rtext in pa)
        if was_blind:
            surfaced += 1
            if addressed:
                corrected += 1
    if surfaced == 0:
        return {"corrected_blind": 0, "surfaced_blind": 0, "rate": None}
    return {"corrected_blind": corrected, "surfaced_blind": surfaced,
            "rate": corrected / surfaced}


# ===== OLS / ANCOVA (pure python) ==========================================
def _solve(A, b):
    """Gaussian elimination, returns x solving A x = b (A: list of rows)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col] or 1e-12
        M[col] = [v / pv for v in M[col]]
        for r in range(n):
            if r != col:
                f = M[r][col]
                M[r] = [M[r][j] - f * M[col][j] for j in range(n + 1)]
    return [M[i][n] for i in range(n)]


def ols(X, y):
    """X: list of rows (each len p), y: list. Returns (coef, rss, n, p)."""
    XtX = [[sum(X[i][a] * X[i][b] for i in range(len(X))) for b in range(len(X[0]))]
           for a in range(len(X[0]))]
    Xty = [sum(X[i][a] * y[i] for i in range(len(X))) for a in range(len(X[0]))]
    beta = _solve(XtX, Xty)
    resid = [y[i] - sum(beta[j] * X[i][j] for j in range(len(beta))) for i in range(len(y))]
    rss = sum(r * r for r in resid)
    return beta, rss, len(y), len(beta)


def ancova(y, group, cov):
    """One-factor ANCOVA (k groups, one covariate). Returns F, p, adjusted means."""
    groups = sorted(set(group))
    k = len(groups)
    n = len(y)
    # full model: intercept + (k-1) dummies + covariate
    def design(rows):
        X = []
        for i in range(n):
            row = [1.0]
            gi = groups.index(group[i])
            row += [1.0 if gi == g else 0.0 for g in range(1, k)]
            row.append(cov[i])
            X.append(row)
        return X
    Xf = design(list(range(n)))
    _, rss_full, _, pf = ols(Xf, y)
    # reduced: intercept + covariate only
    Xr = [[1.0, cov[i]] for i in range(n)]
    _, rss_red, _, pr = ols(Xr, y)
    df_num, df_den = (k - 1), (n - k - 1)
    if df_den < 1 or (rss_full == 0):
        return float("nan"), float("nan"), {}
    F = ((rss_red - rss_full) / df_num) / (rss_full / df_den)
    p = (1 - sp.f.cdf(F, df_num, df_den)) if HAVE_SCIPY else float("nan")
    # adjusted means: set covariate to its grand mean
    gc = mean(cov)
    beta = ols(Xf, y)[0]
    adj = {}
    for gi, g in enumerate(groups):
        val = beta[0] + (beta[gi] if gi >= 1 else 0.0) + beta[-1] * gc
        adj[g] = val
    return F, p, adj


# ===== composite scores from roster ========================================
COMPOSITES = {
    "SD": ["SD1", "SD2", "SD3", "SD4"],
    "MC": ["MC1", "MC2", "MC3"],
    "AG": ["AG1", "AG2", "AG3", "AG4"],
    "CD": ["CD1", "CD2", "CD3"],
    "TR": ["TR1", "TR2", "TR3"],
}


def composite(row, keys):
    vals = []
    for k in keys:
        v = row.get(k)
        if v not in (None, ""):
            try:
                vals.append(float(v))
            except ValueError:
                pass
    return mean(vals) if vals else None


# ===== LaTeX emission ======================================================
def fmt(x, nd=2):
    return "%.*f" % (nd, x) if isinstance(x, (int, float)) and x == x else "—"


def cell_ci(d):
    """Cohen's d 95% CI (approx, Hedges)."""
    if not isinstance(d, (int, float)) or d != d:
        return ""
    se = math.sqrt(4 / (len([1]) * 0 + 1))  # placeholder, replaced below
    return ""


def latex_results(out, demo_label):
    lines = []
    lines.append("% ===== Study 1 results tables (generated by study1_stats.py) =====")
    if demo_label:
        lines.append(f"% !! DEMO / SYNTHETIC DATA — numbers are NOT real. {demo_label}")
    for block in out:
        lines.append("")
        lines.append(r"\begin{table}[t]")
        lines.append(r"  \centering")
        lines.append(f"  \\caption{{{block['caption']}}}")
        lines.append(r"  \begin{tabular}{" + block["cols"] + "}")
        lines.append(r"    \toprule")
        for r in block["header"]:
            lines.append("    " + " & ".join(r) + r" \\")
        lines.append(r"    \midrule")
        for r in block["rows"]:
            lines.append("    " + " & ".join(str(c) for c in r) + r" \\")
        lines.append(r"    \bottomrule")
        lines.append(r"  \end{tabular}")
        if block.get("note"):
            lines.append(r"  \label{" + block["label"] + "}")
            lines.append(r"  \\ \footnotesize " + block["note"])
        lines.append(r"\end{table}")
        lines.append("")
    return "\n".join(lines)


# ===== main =================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roster", nargs="?", help="participant roster CSV")
    ap.add_argument("sessions", nargs="*", help="session JSON files")
    ap.add_argument("--demo", action="store_true", help="synthetic data (labelled DEMO)")
    args = ap.parse_args()

    demo_label = ""
    if args.demo:
        args.roster, args.sessions, demo_label = _make_demo()

    if not args.roster:
        print("No roster given. Use --demo or pass roster.csv + sessions.", file=sys.stderr)
        return 1

    # load roster
    rows = []
    with open(args.roster, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    # load sessions, join by session_id (or id)
    sess_by_id = {}
    for f in args.sessions:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                s = json.load(fh)
            sess_by_id[s.get("id")] = s
        except Exception as e:
            print(f"! cannot read {f}: {e}", file=sys.stderr)

    records = []
    for r in rows:
        sid = r.get("session_id") or r.get("id")
        s = sess_by_id.get(sid)
        dv = analysis_plan.dvs_for_session(s) if s else {}
        rec = {
            "code": r.get("code"),
            "cond": (r.get("cond") or (dv.get("condition") or {}).get("cond") or "?"),
            "align": (r.get("align") or (dv.get("condition") or {}).get("align") or "critical"),
            "pre_robust": _num(r.get("pre_robustness")),
            "SD": composite(r, COMPOSITES["SD"]),
            "MC": composite(r, COMPOSITES["MC"]),
            "AG": composite(r, COMPOSITES["AG"]),
            "CD": composite(r, COMPOSITES["CD"]),
            "TR": composite(r, COMPOSITES["TR"]),
            "self_rate": dv.get("self_discovery_rate"),
            "by_disc": dv.get("by_disc_style") or {},
            "coverage": dv.get("coverage_changed_lens", 0) + dv.get("coverage_resolved_edges", 0),
            "pre_groups": _num(r.get("pre_groups_n")),
            "post_groups": _num(r.get("post_groups_n")),
            "corrected_rate": (correction_metrics(s) or {}).get("rate"),
            "corrected_blind": (correction_metrics(s) or {}).get("corrected_blind", 0),
            "surfaced_blind": (correction_metrics(s) or {}).get("surfaced_blind", 0),
        }
        records.append(rec)

    multimodal = [x for x in records if x["cond"] == "multimodal"]
    text = [x for x in records if x["cond"] == "text"]
    blocks, summary = _run_tests(multimodal, text, records, demo_label)

    tex = latex_results(blocks, demo_label)
    with open("study1_results_tables.tex", "w", encoding="utf-8") as fh:
        fh.write(tex)
    with open("study1_results.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(tex)
    print("\n[written] study1_results_tables.tex  +  study1_results.json")
    return 0


def _num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (ValueError, TypeError):
        return None


def _run_tests(multimodal, text, records, demo_label):
    blocks = []
    summary = {"n_multimodal": len(multimodal), "n_text": len(text), "tests": {}}
    papprox = "" if HAVE_SCIPY else " (p approx: no scipy)"

    # ---- H1: self_discovery_rate by cond ----
    a = [x["self_rate"] for x in multimodal if x["self_rate"] is not None]
    b = [x["self_rate"] for x in text if x["self_rate"] is not None]
    t, df = welch_t(a, b)
    p = _student_two_tailed_p(t, df)
    d = cohen_d(a, b)
    summary["tests"]["H1_self_rate"] = {"M_mm": fmt(mean(a)), "M_tx": fmt(mean(b)),
                                        "t": fmt(t), "df": fmt(df), "p": fmt(p), "d": fmt(d)}
    blocks.append({
        "caption": "H1 (RQ1): Self-discovery rate by modality arm.",
        "cols": "l c c c c c",
        "label": "tab:h1",
        "header": [["Arm", "n", "M", "SD", "Welch t", "Cohen's d"]],
        "rows": [
            ["Multimodal", str(len(a)), fmt(mean(a)), fmt(sd(a)), "", ""],
            ["Text-only", str(len(b)), fmt(mean(b)), fmt(sd(b)),
             f"t({fmt(df,0)})={fmt(t)}, p={fmt(p)}{papprox}", fmt(d)],
        ],
        "note": "Primary confirmatory contrast (pre-registered H1). " + demo_label,
    })

    # ---- H1 ANCOVA with pre_robustness ----
    if all(x["pre_robust"] is not None for x in multimodal + text) and len(multimodal + text) > 4:
        y = [x["self_rate"] for x in multimodal + text if x["self_rate"] is not None]
        g = [x["cond"] for x in multimodal + text if x["self_rate"] is not None]
        c = [x["pre_robust"] for x in multimodal + text if x["self_rate"] is not None]
        F, p, adj = ancova(y, g, c)
        summary["tests"]["H1_ancova"] = {"F": fmt(F), "p": fmt(p),
                                         "adj_mm": fmt(adj.get("multimodal", float("nan"))),
                                         "adj_tx": fmt(adj.get("text", float("nan")))}
        blocks.append({
            "caption": "H1 ANCOVA: self-discovery rate by modality, covarying pre-task ethical robustness.",
            "cols": "l c c c",
            "label": "tab:h1ancova",
            "header": [["Source", "F", "p", "Adj. M (MM / Text)"]],
            "rows": [["Modality", fmt(F), fmt(p) + papprox,
                      f"{fmt(adj.get('multimodal', float('nan')))} / {fmt(adj.get('text', float('nan')))}"]],
            "note": "Confirmatory, covariate = pre-task self-rated robustness. " + demo_label,
        })

    # ---- H3: agency/ownership (AG) by cond ----
    a3 = [x["AG"] for x in multimodal if x["AG"] is not None]
    b3 = [x["AG"] for x in text if x["AG"] is not None]
    t3, df3 = welch_t(a3, b3)
    p3 = _student_two_tailed_p(t3, df3)
    summary["tests"]["H3_agency"] = {"M_mm": fmt(mean(a3)), "M_tx": fmt(mean(b3)),
                                     "t": fmt(t3), "p": fmt(p3), "d": fmt(cohen_d(a3, b3))}
    blocks.append({
        "caption": "H3 (RQ3): Agency / ownership composite by modality arm.",
        "cols": "l c c c c",
        "label": "tab:h3",
        "header": [["Arm", "n", "M", "SD", "Welch t"]],
        "rows": [
            ["Multimodal", str(len(a3)), fmt(mean(a3)), fmt(sd(a3)), ""],
            ["Text-only", str(len(b3)), fmt(mean(b3)), fmt(sd(b3)),
             f"t({fmt(df3,0)})={fmt(t3)}, p={fmt(p3)}{papprox}"],
        ],
        "note": "Confirmatory (pre-registered H3). " + demo_label,
    })

    # ---- H4: coverage improvement + MC composite by cond ----
    a4 = [x["coverage"] for x in multimodal]
    b4 = [x["coverage"] for x in text]
    t4, df4 = welch_t(a4, b4)
    p4 = _student_two_tailed_p(t4, df4)
    summary["tests"]["H4_coverage"] = {"M_mm": fmt(mean(a4)), "M_tx": fmt(mean(b4)),
                                       "t": fmt(t4), "p": fmt(p4)}
    # MC composite
    a4m = [x["MC"] for x in multimodal if x["MC"] is not None]
    b4m = [x["MC"] for x in text if x["MC"] is not None]
    t4m, df4m = welch_t(a4m, b4m)
    p4m = _student_two_tailed_p(t4m, df4m)
    blocks.append({
        "caption": "H4 (RQ4): Evidence-coverage improvement and mindset-change by modality arm.",
        "cols": "l c c c c",
        "label": "tab:h4",
        "header": [["Measure", "Arm", "M", "SD", "Welch t"]],
        "rows": [
            ["Coverage improvement", "MM", fmt(mean(a4)), fmt(sd(a4)), ""],
            ["", "Text", fmt(mean(b4)), fmt(sd(b4)), f"t({fmt(df4,0)})={fmt(t4)}, p={fmt(p4)}{papprox}"],
            ["Mindset-change", "MM", fmt(mean(a4m)), fmt(sd(a4m)), ""],
            ["", "Text", fmt(mean(b4m)), fmt(sd(b4m)), f"t({fmt(df4m,0)})={fmt(t4m)}, p={fmt(p4m)}{papprox}"],
        ],
        "note": "Confirmatory (pre-registered H4). " + demo_label,
    })

    # ---- RQ4 correction: corrected_blindspot_rate by cond (plan-diff) ----
    a4c = [x["corrected_rate"] for x in multimodal if x["corrected_rate"] is not None]
    b4c = [x["corrected_rate"] for x in text if x["corrected_rate"] is not None]
    if a4c or b4c:
        t4c, df4c = (float("nan"), float("nan"))
        p4c = float("nan")
        if len(a4c) >= 2 and len(b4c) >= 2:
            t4c, df4c = welch_t(a4c, b4c)
            p4c = _student_two_tailed_p(t4c, df4c)
        pooled = (sum(x["corrected_blind"] for x in records) /
                  max(1, sum(x["surfaced_blind"] for x in records)))
        summary["tests"]["RQ4_correction"] = {
            "M_mm": fmt(mean(a4c)), "M_tx": fmt(mean(b4c)),
            "pooled_rate": fmt(pooled), "t": fmt(t4c), "p": fmt(p4c), "d": fmt(cohen_d(a4c, b4c))}
        blocks.append({
            "caption": "RQ4 (correction): Behavioral blind-spot correction rate by modality arm.",
            "cols": "l c c c c",
            "label": "tab:h4corr",
            "header": [["Arm", "n", "M (corrected rate)", "SD", "Welch t"]],
            "rows": [
                ["Multimodal", str(len(a4c)), fmt(mean(a4c)), fmt(sd(a4c)), ""],
                ["Text-only", str(len(b4c)), fmt(mean(b4c)), fmt(sd(b4c)),
                 (f"t({fmt(df4c,0)})={fmt(t4c)}, p={fmt(p4c)}{papprox}"
                  if t4c == t4c else "n/a (one arm <2)")],
            ],
            "note": ("Corrected-blind-spot rate = mirror-surfaced blind spots the participant "
                     "action-linked in plan\\_after (plan-diff instrument, study1\\_plandiff\\_instrument.md). "
                     "Confirmatory extension of pre-registered H4. " + demo_label),
        })

    # ---- RQ2 (exploratory): within-disc SELF rate (withhold vs prescribe) ----
    w_self = sum(x["by_disc"].get("withhold", {}).get("SELF", 0) for x in records)
    w_tot = sum(x["by_disc"].get("withhold", {}).get("n", 0) for x in records)
    p_self = sum(x["by_disc"].get("prescribe", {}).get("SELF", 0) for x in records)
    p_tot = sum(x["by_disc"].get("prescribe", {}).get("n", 0) for x in records)
    wr = (w_self / w_tot) if w_tot else float("nan")
    pr = (p_self / p_tot) if p_tot else float("nan")
    summary["tests"]["RQ2_disc"] = {"withhold_SELF_rate": fmt(wr), "prescribe_SELF_rate": fmt(pr)}
    blocks.append({
        "caption": "RQ2 (exploratory): Self-attributed realization rate by disclosure style (within-session).",
        "cols": "l c c",
        "label": "tab:rq2",
        "header": [["Style", "n tensions", "SELF rate"]],
        "rows": [
            ["Withhold (mirror only asks)", str(w_tot), fmt(wr)],
            ["Prescribe (mirror states issue)", str(p_tot), fmt(pr)],
        ],
        "note": "Exploratory; report with Holm correction. " + demo_label,
    })

    # ---- RQ-align (exploratory): CD/TR by align ----
    crit = [x for x in records if x["align"] == "critical"]
    syc = [x for x in records if x["align"] == "sycophantic"]
    if crit and syc:
        cd_c = [x["CD"] for x in crit if x["CD"] is not None]
        cd_s = [x["CD"] for x in syc if x["CD"] is not None]
        tc, dfc = welch_t(cd_c, cd_s)
        pc = _student_two_tailed_p(tc, dfc)
        summary["tests"]["RQalign_cd"] = {"crit_M": fmt(mean(cd_c)), "syc_M": fmt(mean(cd_s)), "p": fmt(pc)}
        blocks.append({
            "caption": "RQ-align (exploratory): critical distance by tone (critical vs sycophantic).",
            "cols": "l c c c",
            "label": "tab:rqalign",
            "header": [["Tone", "n", "M (CD)", "Welch t"]],
            "rows": [
                ["Critical", str(len(cd_c)), fmt(mean(cd_c)), ""],
                ["Sycophantic", str(len(cd_s)), fmt(mean(cd_s)), f"t={fmt(tc)}, p={fmt(pc)}{papprox}"],
            ],
            "note": "Exploratory 2x2; report with correction. " + demo_label,
        })

    return blocks, summary


def _make_demo():
    """Synthetic dataset so the pipeline is demonstrably runnable. LABELLED DEMO."""
    import tempfile
    random.seed(20260813)
    roster_path = os.path.join(tempfile.gettempdir(), "study1_demo_roster.csv")
    sess_files = []
    with open(roster_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["code", "session_id", "cond", "disc", "align", "pre_robustness",
                    "SD1", "SD2", "SD3", "SD4", "MC1", "MC2", "MC3",
                    "AG1", "AG2", "AG3", "AG4", "CD1", "CD2", "CD3",
                    "TR1", "TR2", "TR3", "pre_groups_n", "post_groups_n"])
        for i, cond in enumerate(["multimodal"] * 8 + ["text"] * 8):
            code = f"P{i:03d}"
            sid = f"demo_{i}"
            # MM gets higher self-discovery & agency
            base = 5.2 if cond == "multimodal" else 4.1
            sd_vals = [round(min(7, max(1, base + random.gauss(0, 1))), 1) for _ in range(4)]
            ag_vals = [round(min(7, max(1, base + random.gauss(0, 0.8))), 1) for _ in range(4)]
            cd_vals = [round(min(7, max(1, 4.5 + random.gauss(0, 1))), 1) for _ in range(3)]
            tr_vals = [round(min(7, max(1, 4.0 + random.gauss(0, 1))), 1) for _ in range(3)]
            mc_vals = [round(min(7, max(1, base + random.gauss(0, 1))), 1) for _ in range(3)]
            pre = round(random.uniform(3, 6), 1)
            pre_g = random.randint(3, 5)
            post_g = pre_g + (random.randint(1, 3) if cond == "multimodal" else random.randint(0, 1))
            w.writerow([code, sid, cond, "split", "critical", pre] + sd_vals + mc_vals +
                       ag_vals + cd_vals + tr_vals + [pre_g, post_g])
            # session JSON — arm-differentiated realization phrasing so the
            # lexical heuristic (frozen in analysis_plan.py) separates the arms
            # in the DEMO only. Real data uses human coding as the gold standard.
            if cond == "multimodal":
                r1, r2 = ("I had not realized this group would be affected",
                          "I never considered that the downstream team inherits this risk")
                st1, st2 = "withhold", "prescribe"
            else:
                r1 = "the tool indicated this group was affected"
                r2 = "the mirror stated plainly that deployers inherit the biased model"
                st1, st2 = "withhold", "prescribe"
            sess = {
                "id": sid,
                "dissonance_edges": [{"id": "e1", "affected_party": "g1", "attention_required": True},
                                     {"id": "e2", "affected_party": "g2", "attention_required": True}],
                "lenses": [{"id": "l1", "label": "Privacy", "state": "Reasoned"}],
                "replay_history": [{"summary": {"changed_lens_count": 2 if cond == "multimodal" else 1,
                                                "resolved_edges": 1, "open_edges": 1}}],
                "self_discovery": {
                    "condition": {"cond": cond, "disc": "split", "align": "critical"},
                    "anticipated": "not",
                    "realizations": {
                        "e1": {"edge_id": "e1", "style": st1, "anticipated": "not",
                               "realized": r1, "party": "g1"},
                        "e2": {"edge_id": "e2", "style": st2, "anticipated": "not",
                               "realized": r2, "party": "g2"},
                    },
                },
                # --- plan-diff instrument fields (study1_plandiff_instrument.md) ---
                "plan_before": ("We build a dorm fairness assistant that reads smart-plug data and "
                                "group-chat tone to label a free-riding roommate and draft a private "
                                "message. Privacy is claimed."),
                "plan_after": ("We build a dorm fairness assistant that reads smart-plug data and "
                               "group-chat tone to label a free-riding roommate and draft a private "
                               "message. Privacy is claimed. Add: we add an explicit opt-out and a "
                               "redress path, and prohibit sharing labels with landlords or "
                               "disciplinary systems."),
                "revision_links": [
                    {
                        "finding_id": "EDGE-001",
                        "finding_summary": ("downstream misuse: labels could be shared with landlords "
                                            "or disciplinary systems"),
                        "revision_text": "prohibit sharing labels with landlords or disciplinary systems",
                        "link_type": "add_safeguard" if cond == "multimodal" else "none",
                        "resolved_state": "action_linked" if cond == "multimodal" else "none",
                    }
                ],
            }
            sp = os.path.join(tempfile.gettempdir(), f"study1_demo_{sid}.json")
            with open(sp, "w", encoding="utf-8") as sf:
                json.dump(sess, sf)
            sess_files.append(sp)
    return roster_path, sess_files, "DEMO synthetic data — replace with real exports before submission."


if __name__ == "__main__":
    sys.exit(main())
