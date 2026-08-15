"""SafeBARS Ethical Redesign Studio — visualization-condition engine.

This module powers *Condition B* of the two-condition study: instead of only
showing the Ethical Mirror findings as text (Condition A), it renders each
identified ethical issue as a small set of safe, emotionally-resonant
visualizations that help a researcher decide whether (and how) to fix the
issue without sacrificing the core value of their work.

Everything here is deterministic and offline by default (mirroring the
design philosophy of the deep-audit layer).  No LLM budget is consumed.
Optional ``img_prompt`` fields are emitted so a future image provider can
render hand-drawn concept sketches without changing the data contract.

Study framing (from advisor feedback, 2026-08-15)
------------------------------------------------
- The researcher's plan is *almost complete* and *not entirely unethical*.
- The app surfaces issues **one by one** and argues, per issue, whether to fix.
- The researcher may **Accept-risk** (the core value is worth the trade) or
  **Defer**; the app records the rationale instead of forcing compliance.
- The goal is to make the *research-effort vs ethical-risk* trade-off visible,
  recorded, and defensible — not to force a fully "clean" design.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Domain-aware narrative fragments
# ---------------------------------------------------------------------------
# Each domain maps to: short label, three "fix" future beats, three "ignore"
# future beats, and two role-swap paragraphs.  Text is deliberately *safe but
# clear*: it names consequences without depicting real harm to real people.

_DOMAIN_NARRATIVE: Dict[str, Dict[str, Any]] = {
    "surveillance_monitoring": {
        "label": "Surveillance / continuous monitoring",
        "fix": [
            "A visible notice and an honest opt-out appear on the first screen; a pilot cohort confirms they understand they are observed.",
            "The consent flow is documented in the method section and clears the department's privacy review.",
            "The tool is cited as a transparent early-warning model other campuses ask to adapt — no stories of covert watching.",
        ],
        "ignore": [
            "A student mentions the system to a friend; word spreads that the app 'reads your posts silently'.",
            "A screenshot of the hidden dashboard circulates in a group chat; the department asks what participants were told.",
            "A student union or journalist flags it; the project is paused and the paper is pulled over consent.",
        ],
        "researcher": "As the researcher, monitoring is the engine of the help you want to give — earlier, quieter signals mean earlier support. The safeguard feels like paperwork that delays a tool that could matter.",
        "participant": "As the participant, you later learn the app read your late-night posts to judge your state. The help arrived, but you were never asked — and the quiet part is what sticks.",
    },
    "minors_students": {
        "label": "Minors / students",
        "fix": [
            "Age-appropriate assent and guardian consent are collected before any data is used.",
            "A best-interests statement shows how the design serves the student, not only the study.",
            "The protocol is approved by the school's ethics board and shared with participants in plain language.",
        ],
        "ignore": [
            "A parent hears the tool profiled their child's mood without permission and contacts the school.",
            "A complaint reaches the ethics board; the study is flagged for lacking lawful basis.",
            "The finding is reported as a safeguarding concern and the publication is halted.",
        ],
        "researcher": "As the researcher, students are exactly who you want to reach — the value is real and time-sensitive. Consent steps feel like they slow help to the people who need it most.",
        "participant": "As the student, you are the subject of a study about you that your parents or you never clearly agreed to. Being 'helped' without a say can feel like being managed, not supported.",
    },
    "mental_health": {
        "label": "Mental health / crisis",
        "fix": [
            "A human crisis protocol names who is notified, within what window, and what they do.",
            "False-positive and false-negative rates are measured and shared with oversight.",
            "The tool routes to care rather than only flagging; a clinician co-signs the approach.",
        ],
        "ignore": [
            "An at-risk post is flagged but no one is tasked to act; a week passes with no follow-up.",
            "A false alarm strains a friendship; a missed case sparks a formal complaint.",
            "A review finds no duty-of-care pathway and the crisis feature is disabled.",
        ],
        "researcher": "As the researcher, the crisis use-case is the most meaningful one — the reason the whole system is worth building. Safeguards can feel like they blunt the very feature that saves lives.",
        "participant": "As the participant in distress, you post something raw and a system decides your state without a human. Being flagged, or not flagged when it mattered, both feel like the machine owned a moment that was yours.",
    },
    "sensitive_personal_data": {
        "label": "Sensitive personal data",
        "fix": [
            "Data minimisation removes fields not needed for the stated aim; retention is capped at the minimum.",
            "Access is logged and limited to named, trained members of the team.",
            "A data-protection checklist is signed before any analysis runs.",
        ],
        "ignore": [
            "An export of sensitive fields sits in a shared drive longer than intended.",
            "A request for the data map reveals more columns than the consent covered.",
            "A breach or audit finds processing beyond the lawful basis and the data is deleted under order.",
        ],
        "researcher": "As the researcher, richer signals make the model sharper and the finding stronger. Trimming data feels like throwing away exactly the detail that powers the result.",
        "participant": "As the participant, you discover intimate categories about you — health, identity, beliefs — were processed far beyond what you signed for. The harm is quiet: a profile of you, assembled without your knowledge.",
    },
    "automated_decision": {
        "label": "Automated decision-making",
        "fix": [
            "A human stays in the loop for any consequential decision; the model only advises.",
            "The logic behind a flag is explainable to the person affected.",
            "An appeal path lets someone challenge a consequential output.",
        ],
        "ignore": [
            "A flag quietly triggers an action (a message, a referral) with no human review.",
            "A person affected asks why and receives no explanation.",
            "An error with no appeal erodes trust and draws a regulator's attention.",
        ],
        "researcher": "As the researcher, automation is what scales the help to thousands. A human-in-the-loop requirement can feel like it caps the very thing that makes the system worthwhile.",
        "participant": "As the participant, a decision about you was made by a system you cannot see or question. Being judged without a say, and with no way to appeal, is the part that feels unfair.",
    },
    "vulnerable_population": {
        "label": "Vulnerable population",
        "fix": [
            "Extra protections are added for the most exposed participants.",
            "Recruitment avoids coercion and offers genuine alternatives.",
            "An independent check confirms the group is not exploited for convenience.",
        ],
        "ignore": [
            "The easiest-to-reach group is also the least able to refuse.",
            "A power imbalance in recruitment goes unaddressed.",
            "A reviewer flags exploitation and the sample is reconsidered.",
        ],
        "researcher": "As the researcher, the vulnerable group is often where the need is greatest — excluding them can feel like giving up on the people who need the tool. Protections can read as barriers.",
        "participant": "As the participant from that group, you sense the study needed you more than it protected you. Being useful to the research, rather than respected by it, is a quiet kind of imbalance.",
    },
}

_GENERIC_NARRATIVE: Dict[str, Any] = {
    "label": "Ethical gap",
    "fix": [
        "The concern is named openly and a concrete safeguard is added to the design.",
        "The change is documented and reviewed by a second pair of eyes.",
        "The revised plan is stronger and defensible if questioned later.",
    ],
    "ignore": [
        "The concern stays unaddressed while the project moves forward.",
        "A stakeholder or reviewer later asks why it was left open.",
        "The issue resurfaces at a worse moment and costs more to fix.",
    ],
    "researcher": "As the researcher, this is one concern among many; fixing it feels like effort that does not change the result you care about.",
    "participant": "As the person affected, the unaddressed concern is a small risk you never agreed to carry.",
}

_FUTURE_LABELS = ["+2 weeks", "+3 months", "+1 year"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _short(text: str, limit: int = 220) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _narrative_for(domain_id: Optional[str]) -> Dict[str, Any]:
    return _DOMAIN_NARRATIVE.get(domain_id) or _GENERIC_NARRATIVE


def _safe_img_prompt(issue_label: str, branch: str, label: str) -> str:
    branch_word = "repaired" if branch == "fix" else "left unaddressed"
    mood = "calm, trusting" if branch == "fix" else "tense, uneasy"
    return (
        f"Hand-drawn CHI-style concept sketch, soft pencil and watercolor on white: "
        f"a campus AI ethics scenario at '{label}', the issue '{issue_label}' {branch_word}. "
        f"{mood} mood, symbolic not literal, no real faces, generous white space."
    )


def build_two_futures(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Return a forked two-future timeline for one issue (deterministic)."""

    narrative = _narrative_for(issue.get("domain_id"))
    fix_beats = narrative["fix"]
    ignore_beats = narrative["ignore"]
    fix, ignore = [], []
    for i, label in enumerate(_FUTURE_LABELS):
        f_scenario = fix_beats[i] if i < len(fix_beats) else _GENERIC_NARRATIVE["fix"][i]
        i_scenario = ignore_beats[i] if i < len(ignore_beats) else _GENERIC_NARRATIVE["ignore"][i]
        fix.append({
            "t": label,
            "scenario": f_scenario,
            "img_prompt": _safe_img_prompt(issue.get("label", "the issue"), "fix", label),
        })
        ignore.append({
            "t": label,
            "scenario": i_scenario,
            "img_prompt": _safe_img_prompt(issue.get("label", "the issue"), "ignore", label),
        })
    return {"fix": fix, "ignore": ignore}


def build_role_swap(issue: Dict[str, Any], plan: str = "") -> Dict[str, str]:
    """Return the same future seen through two lenses (deterministic)."""

    narrative = _narrative_for(issue.get("domain_id"))
    label = issue.get("label", "this issue")
    domain_label = issue.get("domain_label", "")
    ctx = f" ({domain_label})" if domain_label else ""
    return {
        "as_researcher": f"{narrative['researcher']}",
        "as_participant": f"{narrative['participant']}",
        "issue_label": label + ctx,
    }


def _issue_from_contradiction(c: Dict[str, Any], idx: int) -> Dict[str, Any]:
    return {
        "id": c.get("id") or f"ISS-{idx:02d}",
        "source": "contradiction",
        "source_ref": c.get("id", ""),
        "severity": "high",
        "label": f"Contradiction: {_short(c.get('type', 'stated vs mechanism'), 60)}",
        "summary": _short(c.get("explanation") or c.get("suggested_action") or "", 240),
        "detail": _short(c.get("commitment_text", ""), 200),
        "domain_id": None,
        "domain_label": "",
        "suggested_action": _short(c.get("suggested_action", ""), 200),
    }


def _issue_from_edge(e: Dict[str, Any], idx: int) -> Dict[str, Any]:
    sev = (e.get("severity") or "elevated").lower()
    if sev not in ("high", "medium", "low"):
        sev = "elevated"
    return {
        "id": e.get("id") or f"ISS-{idx:02d}",
        "source": "discovery_tension",
        "source_ref": e.get("id", ""),
        "severity": sev,
        "label": f"Tension: {_short(e.get('rule', 'discovery'), 60)}",
        "summary": _short(e.get("tension") or e.get("attention_basis") or "", 240),
        "detail": _short(e.get("attention_basis", ""), 200),
        "domain_id": None,
        "domain_label": "",
        "suggested_action": "",
    }


def _issue_from_gap(g: Dict[str, Any], idx: int) -> Dict[str, Any]:
    sev = (g.get("severity") or "medium").lower()
    if sev not in ("high", "medium", "low"):
        sev = "medium"
    return {
        "id": f"GAP-{idx:02d}",
        "source": "severity_gap",
        "source_ref": f"GAP-{g.get('label', idx)}",
        "severity": sev,
        "label": f"Gap: {_short(str(g.get('label', 'coverage gap')), 60)}",
        "summary": _short((g.get("reasons") or [""])[0] or "", 240),
        "detail": "",
        "domain_id": None,
        "domain_label": "",
        "suggested_action": "",
    }


def _issue_from_domain(d: Dict[str, Any], idx: int, domain_id: str) -> Dict[str, Any]:
    sev = (d.get("severity") or "high").lower()
    if sev not in ("high", "medium", "low"):
        sev = "high"
    return {
        "id": f"DOM-{idx:02d}",
        "source": "high_risk_domain",
        "source_ref": f"DOM-{domain_id}",
        "severity": sev,
        "label": f"High-risk domain: {_short(str(d.get('label', domain_id)), 60)}",
        "summary": _short("Matched terms: " + ", ".join((d.get("matched_terms") or [])[:6]), 240),
        "detail": "",
        "domain_id": domain_id,
        "domain_label": str(d.get("label", domain_id)),
        "suggested_action": "",
    }


_SEVERITY_RANK = {"high": 0, "elevated": 1, "medium": 2, "low": 3}


def extract_issues(
    deep_audit: Optional[Dict[str, Any]] = None,
    dissonance_edges: Optional[Sequence[Dict[str, Any]]] = None,
    plan: str = "",
    max_issues: int = 8,
) -> List[Dict[str, Any]]:
    """Build the ordered, de-duplicated issue list from a completed analysis.

    Sources (in priority order): internal contradictions, severity-weighted
    gaps, additional discovery tensions, high-risk domains.  Core
    ``dissonance_edges`` are *not* added here to avoid double-counting with the
    discovery tensions already surfaced by the deep-audit layer.
    """

    da = deep_audit or {}
    candidates: List[Dict[str, Any]] = []
    idx = 1

    # Priority order: contradictions (most concrete) -> high-risk domains
    # (safety-relevant) -> severity gaps -> discovery tensions.
    for c in (da.get("internal_contradictions") or []):
        candidates.append(_issue_from_contradiction(c, idx)); idx += 1
    for d in ((da.get("domain_flags", {}) or {}).get("matched_domains") or []):
        candidates.append(_issue_from_domain(d, idx, d.get("id", ""))); idx += 1
    for g in (da.get("severity_weighted_gaps", {}).get("prioritized_gaps") or []):
        candidates.append(_issue_from_gap(g, idx)); idx += 1
    for e in (da.get("additional_dissonance_edges") or []):
        candidates.append(_issue_from_edge(e, idx)); idx += 1

    # De-duplicate by normalised label, keeping the first (highest priority).
    seen = set()
    unique = []
    for cand in candidates:
        key = cand["label"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(cand)

    # Rank by severity, then assign stable ids.
    unique.sort(key=lambda c: _SEVERITY_RANK.get(c["severity"], 9))
    issues: List[Dict[str, Any]] = []
    for i, cand in enumerate(unique[:max_issues], start=1):
        issue = dict(cand)
        issue["id"] = f"ISS-{i:02d}"
        issue["two_futures"] = build_two_futures(issue)
        issue["role_swap"] = build_role_swap(issue, plan)
        issue["decision"] = None
        issues.append(issue)
    return issues


# ---------------------------------------------------------------------------
# Decisions & design evolution
# ---------------------------------------------------------------------------

VALID_CHOICES = ("fix", "accept_risk", "defer")


def record_decision(
    session: Dict[str, Any],
    issue_id: str,
    choice: str,
    rationale: str = "",
    tradeoff: Optional[int] = None,
) -> Dict[str, Any]:
    """Record a researcher's per-issue decision and append to the evolution log."""

    if choice not in VALID_CHOICES:
        raise ValueError(
            f"choice must be one of {VALID_CHOICES}, got {choice!r}"
        )
    issues = session.setdefault("issues", [])
    issue = next((i for i in issues if i.get("id") == issue_id), None)
    if not issue:
        raise ValueError(f"Unknown issue id: {issue_id}")

    tradeoff_val: Optional[int] = None
    if tradeoff is not None:
        try:
            tradeoff_val = max(0, min(100, int(tradeoff)))
        except (TypeError, ValueError):
            tradeoff_val = None

    at = _utc_now()
    issue["decision"] = {
        "choice": choice,
        "rationale": (rationale or "").strip()[:2000],
        "tradeoff": tradeoff_val,
        "at": at,
    }
    evo = session.setdefault("design_evolution", [])
    evo.append({
        "issue_id": issue_id,
        "choice": choice,
        "tradeoff": tradeoff_val,
        "at": at,
        "index": len(evo) + 1,
    })
    return session


def _week_day(iso_ts: str, first_iso: str) -> int:
    try:
        a = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        b = datetime.fromisoformat(first_iso.replace("Z", "+00:00"))
        delta_days = max(0, (a - b).total_seconds() / 86400.0)
        return max(1, min(7, int(delta_days) + 1))
    except Exception:
        return 1


def derive_evolution(session: Dict[str, Any]) -> Dict[str, Any]:
    """Derive the Day-1 → Day-7 design-evolution visualization from decisions."""

    issues = session.get("issues", []) or []
    evo = session.get("design_evolution", []) or []
    by_issue = {i["id"]: i for i in issues}

    first_at = evo[0]["at"] if evo else None
    # Status per issue: start "open"; updated by its latest decision.
    status = {i["id"]: "open" for i in issues}
    for e in evo:
        status[e["issue_id"]] = e["choice"]

    markers = []
    for e in evo:
        markers.append({
            "index": e.get("index"),
            "issue_id": e["issue_id"],
            "issue_label": by_issue.get(e["issue_id"], {}).get("label", e["issue_id"]),
            "choice": e["choice"],
            "day": _week_day(e["at"], first_at) if first_at else e.get("index", 1),
            "at": e["at"],
        })

    counts = {"fix": 0, "accept_risk": 0, "defer": 0, "open": 0}
    for sid, st in status.items():
        counts[st] = counts.get(st, 0) + 1

    return {
        "total_issues": len(issues),
        "decided": len(evo),
        "open": counts["open"],
        "fix": counts["fix"],
        "accept_risk": counts["accept_risk"],
        "defer": counts["defer"],
        "status_by_issue": status,
        "timeline": markers,
        "started_at": first_at,
    }
