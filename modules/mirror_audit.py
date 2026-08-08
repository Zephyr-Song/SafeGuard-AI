"""Deep-audit layer for SafeBARS Ethical Mirror (improvements #1, #3, #4, #5, #6, #8).

The base Mirror *reflects* the researcher's own plan: a lens is Missing only if
the researcher never wrote about it, and a dissonance edge fires mainly from the
rule ``no_linked_lens_has_action_linked_evidence``. That is honest but limited:
it cannot surface risks the researcher did not already hint at.

This module adds discovery without crossing the project's hard boundary (the
Mirror is a reflection aid, not an ethics verdict). It is fully deterministic and
offline by default; an optional LLM may enrich contradiction detection but never
decides evidence states or fabricates findings.

Functions
---------
- ``classify_domain_flags``        (#3) auto-inject high-risk-domain checklists
- ``detect_internal_contradictions`` (#1) commitment-vs-mechanism mismatches
- ``weight_severity``             (#4) severity-weighted coverage gaps
- ``extra_dissonance_rules``      (#5) diverse tension triggers
- ``forced_reflection_questions`` (#6) turn red lenses into discovery prompts
- ``build_real_evidence_bridge``  (#8) attach real-stakeholder evidence
- ``run_deep_audit``              orchestrator used by ``mirror_engine``
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .mirror_analogues import recommend_analogues
from .mirror_patterns import match_patterns


DEEP_AUDIT_NOTICE = (
    "Deep-audit cues are hypothesis-generating discovery aids, not ethics "
    "findings or approval. They surface risks the plan did not state, using "
    "deterministic signal matching, a real-case library, and curated patterns. "
    "Every cue still requires human judgement and real-stakeholder verification."
)

# ---------------------------------------------------------------------------
# Domain detection (#3)
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS: Dict[str, Dict[str, Any]] = {
    "surveillance_monitoring": {
        "label": "Surveillance / continuous monitoring",
        "severity": "high",
        "keywords": [
            "monitor", "surveillance", "track", "scan", "scanning", "watch",
            "cctv", "supervis", "observ", "surveil", "监控", "监测", "扫描",
            "追踪", "监视",
        ],
        "checklist": [
            {
                "title": "Lawful basis & DPIA",
                "detail": "Document a lawful basis for monitoring and complete a "
                          "Data Protection Impact Assessment before launch.",
                "regulation": "GDPR Art. 35; FERPA (US schools)",
            },
            {
                "title": "Purpose limitation",
                "detail": "State in writing what the monitoring may and may not be "
                          "reused for (e.g. no disciplinary reuse).",
                "regulation": "GDPR Art. 5(1)(b)",
            },
            {
                "title": "Transparency / notice",
                "detail": "Tell monitored people they are in the system and how to "
                          "object; silent monitoring is a consent breach.",
                "regulation": "GDPR Art. 13-14; FERPA notice",
            },
        ],
    },
    "minors_students": {
        "label": "Minors / students",
        "severity": "high",
        "keywords": [
            "student", "minor", "child", "under 18", "pupil", "learner",
            "underage", "学生", "未成年人", "青少年", "儿童",
        ],
        "checklist": [
            {
                "title": "Age-appropriate consent",
                "detail": "Obtain valid parental/guardian consent AND age-appropriate "
                          "assent; inform the child in plain language.",
                "regulation": "GDPR Art. 8; FERPA",
            },
            {
                "title": "Best-interests safeguard",
                "detail": "Map how the design serves the minor's welfare, not only "
                          "the institution's efficiency.",
                "regulation": "UNCRC Art. 3",
            },
        ],
    },
    "mental_health": {
        "label": "Mental health / crisis",
        "severity": "high",
        "keywords": [
            "mental", "psycholog", "depress", "suicid", "self-harm", "self harm",
            "distress", "crisis", "counsel", "therap", "心理", "抑郁", "自杀",
            "自伤", "危机", "咨询", "治疗",
        ],
        "checklist": [
            {
                "title": "Human crisis protocol",
                "detail": "Define who is notified, within what time, and what they do "
                          "when acute risk is detected; automation must hand off to a person.",
                "regulation": "Clinical duty of care",
            },
            {
                "title": "Stigma & false-positive harm",
                "detail": "Quantify false-positive (stigma) and false-negative "
                          "(missed risk) stakes; state accountability for errors.",
                "regulation": "Do et al. CHI 2023",
            },
        ],
    },
    "sensitive_personal_data": {
        "label": "Sensitive personal data",
        "severity": "high",
        "keywords": [
            "health", "medical", "biometric", "face", "facial", "location", "gps",
            "race", "religion", "ethnic", "sexual", "genetic", "disability", "健康",
            "医疗", "生物识别", "人脸", "位置", "宗教", "种族", "基因", "残障",
        ],
        "checklist": [
            {
                "title": "Special-category safeguards",
                "detail": "Special-category data needs explicit consent or another "
                          "Art. 9 condition; pseudonymisation is not anonymity.",
                "regulation": "GDPR Art. 9",
            },
            {
                "title": "Re-identification risk",
                "detail": "Assume joinable data can be re-identified; restrict sharing "
                          "and retention accordingly.",
                "regulation": "Netflix Prize re-identification (2008)",
            },
        ],
    },
    "automated_decision": {
        "label": "Automated / algorithmic decision",
        "severity": "elevated",
        "keywords": [
            "auto", "algorithm", "predict", "classify", "score", "flag",
            "risk score", "model", "machine learning", "ml ", "自动", "算法",
            "预测", "打分", "标记", "分类",
        ],
        "checklist": [
            {
                "title": "Human-in-the-loop",
                "detail": "Keep a person able to review/override the flag before any "
                          "consequential action.",
                "regulation": "GDPR Art. 22",
            },
            {
                "title": "Subgroup auditing",
                "detail": "Measure error rates per affected subgroup, not only overall "
                          "accuracy.",
                "regulation": "Gender Shades (2018); Obermeyer et al. (2019)",
            },
        ],
    },
    "vulnerable_population": {
        "label": "Vulnerable population",
        "severity": "elevated",
        "keywords": [
            "vulnerable", "marginaliz", "disabl", "low-income", "poor", "homeless",
            "弱势", "边缘", "残障", "低收入", "无家",
        ],
        "checklist": [
            {
                "title": "Equity & access",
                "detail": "Check the design does not disproportionately burden or "
                          "exclude the most vulnerable users.",
                "regulation": "Benefit/harm-assumptions lens",
            },
        ],
    },
}

# Which lenses a domain most raises the stakes on (used by severity weighting).
_DOMAIN_LENS_BOOST: Dict[str, List[str]] = {
    "surveillance_monitoring": ["downstream_use_misuse_scale", "monitoring_learning_redress", "affected_parties_distribution"],
    "minors_students": ["perspective_participation", "affected_parties_distribution", "responsibility_oversight_contestability"],
    "mental_health": ["benefit_harm_assumptions", "monitoring_learning_redress", "responsibility_oversight_contestability"],
    "sensitive_personal_data": ["affected_parties_distribution", "downstream_use_misuse_scale"],
    "automated_decision": ["benefit_harm_assumptions", "mitigation_design_commitment", "responsibility_oversight_contestability"],
    "vulnerable_population": ["affected_parties_distribution", "benefit_harm_assumptions"],
}

_HIGH_RISK_DOMAINS = {
    "surveillance_monitoring", "minors_students", "mental_health", "sensitive_personal_data"
}


def _matched_terms(text: str, terms: Sequence[str]) -> List[str]:
    lowered = (text or "").lower()
    return [term for term in terms if term in lowered]


def classify_domain_flags(
    plan: str,
    intake_answers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Detect high-risk domains in the plan (+ optional intake) and inject checklists."""
    blob = (plan or "")
    if intake_answers:
        blob = blob + "\n" + "\n".join(str(v) for v in intake_answers.values() if v)
    matched: List[Dict[str, Any]] = []
    for domain_id, meta in DOMAIN_KEYWORDS.items():
        hits = _matched_terms(blob, meta["keywords"])
        if hits:
            matched.append(
                {
                    "id": domain_id,
                    "label": meta["label"],
                    "severity": meta["severity"],
                    "matched_terms": sorted(set(hits)),
                    "checklist": deepcopy(meta["checklist"]),
                }
            )
    matched.sort(key=lambda d: (d["severity"] != "high", d["id"]))
    is_high_risk = any(d["id"] in _HIGH_RISK_DOMAINS for d in matched)
    injected: List[Dict[str, Any]] = []
    for d in matched:
        for item in d["checklist"]:
            injected.append(
                {
                    "domain": d["id"],
                    "domain_label": d["label"],
                    "severity": d["severity"],
                    "title": item["title"],
                    "detail": item["detail"],
                    "regulation": item["regulation"],
                    "status": "pending_researcher_action",
                }
            )
    return {
        "matched_domains": matched,
        "is_high_risk": is_high_risk,
        "high_risk_domain_ids": [d["id"] for d in matched if d["id"] in _HIGH_RISK_DOMAINS],
        "injected_checklist": injected,
        "notice": (
            "Domains were detected by keyword matching, not by reading intent. A "
            "match is a prompt to verify, not proof the risk applies."
        ),
    }


# ---------------------------------------------------------------------------
# Internal contradiction detection (#1)
# ---------------------------------------------------------------------------

_TRANSPARENCY_SIGNALS = [
    "opt-out", "opt out", "optout", "transparent", "visible", "not hidden",
    "disclose", "inform", "consent", "consented", "公开", "透明", "可见",
    "告知", "同意", "知情同意",
]
_HIDDEN_SIGNALS = [
    "silent", "silently", "secret", "covert", "without telling",
    "without notifying", "without informing", "hidden", "undisclosed", "不告知",
    "静默", "秘密", "隐蔽", "不通知", "隐瞒", "未被告知",
]
_CONSENT_SIGNALS = ["consent", "opt-in", "opt in", "同意", "知情同意", "征得"]
_COERCED_SIGNALS = [
    "mandatory", "required", "forced", "compulsory", "no choice", "强制",
    "必须", "无选择", "被迫",
]

_RULE_PAIRS: List[Tuple[List[str], List[str], str, str]] = [
    (
        _TRANSPARENCY_SIGNALS, _HIDDEN_SIGNALS,
        "commitment_claims_transparency_but_mechanism_hidden",
        "The commitment claims transparency, visibility, or notice, but the plan "
        "mechanism is silent, covert, or undisclosed.",
    ),
    (
        _CONSENT_SIGNALS, _COERCED_SIGNALS,
        "commitment_claims_consent_but_mechanism_coerced",
        "The commitment claims consent, but the mechanism is mandatory, required, "
        "or offers no real choice.",
    ),
]


def detect_internal_contradictions(
    plan: str,
    commitments: Sequence[str],
    passages: Sequence[Dict[str, Any]],
    use_llm: bool = False,
    llm_client: Any = None,
) -> List[Dict[str, Any]]:
    """Find commitment-vs-mechanism mismatches deterministically.

    The heuristic catches the classic case (e.g. 'monitoring is opt-out, not
    hidden' vs 'silently notifies the counseling center') without an LLM. An
    optional LLM call may add nuance but is best-effort and never overrides the
    deterministic findings.
    """
    findings: List[Dict[str, Any]] = []
    passage_texts = [p.get("text", "") for p in passages] + [plan]

    def has_any(text: str, signals: Sequence[str]) -> bool:
        lowered = (text or "").lower()
        return any(sig in lowered for sig in signals)

    for commitment in commitments or []:
        for sig_set_a, sig_set_b, rule, explanation in _RULE_PAIRS:
            if not has_any(commitment, sig_set_a):
                continue
            for pt in passage_texts:
                if has_any(pt, sig_set_b):
                    findings.append(
                        {
                            "id": f"CNTR-{len(findings) + 1:03d}",
                            "type": rule,
                            "severity": "high",
                            "commitment_text": commitment,
                            "mechanism_quote": _short(pt, 240),
                            "explanation": explanation,
                            "suggested_action": (
                                "Reconcile the two statements: either make the "
                                "mechanism visible/consented, or remove the "
                                "transparency claim from the commitment."
                            ),
                            "boundary_notice": (
                                "Detected by deterministic signal matching; confirm "
                                "with human judgement and real stakeholders."
                            ),
                        }
                    )
                    break  # one mechanism quote per commitment/rule pair is enough
            if len(findings) and findings[-1]["type"] == rule:
                # avoid double counting the same rule for the same commitment
                pass

    if use_llm and llm_client is not None:
        try:
            extra = _llm_contradiction_scan(plan, commitments, llm_client)
            seen = {(f["type"], f["commitment_text"]) for f in findings}
            for item in extra:
                key = (item.get("type"), item.get("commitment_text"))
                if key not in seen:
                    findings.append(item)
        except Exception:
            # LLM is strictly optional; never let it break the audit.
            pass

    # Re-number for stable ids after optional LLM merge.
    for index, f in enumerate(findings, start=1):
        f["id"] = f"CNTR-{index:03d}"
    return findings


def _llm_contradiction_scan(plan: str, commitments: Sequence[str], llm_client: Any) -> List[Dict[str, Any]]:
    """Best-effort LLM enrichment. Mirrors the engine's provider-agnostic pattern."""
    if not hasattr(llm_client, "chat"):
        return []
    prompt = (
        "You are reviewing an AI research plan for INTERNAL CONTRADICTIONS only "
        "(a commitment or stated value that conflicts with the described mechanism). "
        "Return JSON: {\"contradictions\": [{\"type\": str, \"commitment_text\": str, "
        "\"mechanism_quote\": str, \"explanation\": str}]}. If none, return empty list. "
        "Do not invent findings.\n\nPLAN:\n" + plan[:6000] +
        "\n\nCOMMITMENTS:\n" + "\n".join(f"- {c}" for c in commitments)
    )
    try:
        resp = llm_client.chat(prompt, max_tokens=800)
        data = resp if isinstance(resp, dict) else {}
        items = data.get("contradictions", []) if isinstance(data, dict) else []
        out = []
        for it in items[:5]:
            if not isinstance(it, dict):
                continue
            out.append(
                {
                    "id": "CNTR-LLM",
                    "type": it.get("type", "llm_flagged_contradiction"),
                    "severity": "high",
                    "commitment_text": str(it.get("commitment_text", "")),
                    "mechanism_quote": _short(str(it.get("mechanism_quote", "")), 240),
                    "explanation": str(it.get("explanation", "")),
                    "suggested_action": "Verify this LLM-flagged mismatch with human judgement.",
                    "boundary_notice": "LLM-generated cue; confirm before acting.",
                }
            )
        return out
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Severity-weighted coverage gaps (#4)
# ---------------------------------------------------------------------------

def weight_severity(
    lenses: Sequence[Dict[str, Any]],
    domain_flags: Dict[str, Any],
) -> Dict[str, Any]:
    """Add severity to coverage gaps using detected high-risk domains."""
    high_domains = set(domain_flags.get("high_risk_domain_ids", []))
    boosted_lens: Dict[str, List[str]] = {}
    for d in high_domains:
        for lid in _DOMAIN_LENS_BOOST.get(d, []):
            boosted_lens.setdefault(lid, []).append(d)

    per_lens: List[Dict[str, Any]] = []
    for lens in lenses:
        state_id = lens.get("state_id") or lens.get("state")
        state_id = state_id.lower().replace(" ", "_") if isinstance(state_id, str) else ""
        is_red = state_id in ("missing", "claimed")
        severity = "standard"
        reasons: List[str] = []
        if is_red and lens.get("id") in boosted_lens:
            severity = "high"
            reasons.append(
                "Linked to a detected high-risk domain: "
                + ", ".join(boosted_lens[lens["id"]])
            )
        elif is_red and any(
            d in high_domains for d in ("automated_decision", "vulnerable_population")
        ):
            severity = "elevated"
            reasons.append("Plan operates in an elevated-risk domain.")
        per_lens.append(
            {
                "lens_id": lens.get("id"),
                "label": lens.get("label"),
                "state": lens.get("state"),
                "severity": severity,
                "reasons": reasons,
            }
        )
    prioritized = [p for p in per_lens if p["severity"] != "standard"]
    sev_rank = {"high": 0, "elevated": 1, "standard": 2}
    prioritized.sort(key=lambda p: sev_rank.get(p["severity"], 3))
    return {
        "per_lens": per_lens,
        "prioritized_gaps": prioritized,
        "has_high_severity_gap": any(p["severity"] == "high" for p in per_lens),
    }


# ---------------------------------------------------------------------------
# Additional dissonance rules (#5)
# ---------------------------------------------------------------------------

_RESPONSE_OPTIONS = [
    {
        "id": "revise",
        "label": "Revise the design",
        "description": "Change a feature, scope, method, safeguard, or stopping rule.",
    },
    {
        "id": "contest_with_evidence",
        "label": "Contest with evidence",
        "description": "Explain why the scenario does not fit and cite inspectable evidence.",
    },
    {
        "id": "consult_stakeholder",
        "label": "Consult real stakeholders",
        "description": "Transfer the unresolved assumption to people with relevant lived or domain knowledge.",
    },
    {
        "id": "retain_with_rationale",
        "label": "Retain with rationale",
        "description": "Keep the design choice while recording the trade-off and reassessment trigger.",
    },
]

# Lenses each rule most relates to, for provenance display.
_RULE_LENS: Dict[str, List[str]] = {
    "consent_not_evidenced": ["perspective_participation", "affected_parties_distribution"],
    "affected_party_has_no_agency": ["perspective_participation", "affected_parties_distribution"],
    "automated_decision_without_human_in_loop": ["responsibility_oversight_contestability", "benefit_harm_assumptions"],
    "no_purpose_limitation": ["downstream_use_misuse_scale", "lifecycle_integration"],
    "monitoring_without_redress": ["monitoring_learning_redress", "responsibility_oversight_contestability"],
}


def extra_dissonance_rules(
    plan: str,
    lenses: Sequence[Dict[str, Any]],
    domain_flags: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate tensions from rules beyond 'no action-linked evidence'.

    Each rule fires only when its precondition is met, so it adds *discovery*
    rather than duplicating the base edges.
    """
    lowered = (plan or "").lower()
    high = set(domain_flags.get("high_risk_domain_ids", []))
    edges: List[Dict[str, Any]] = []
    counter = [0]

    def has(*terms: str) -> bool:
        return any(t in lowered for t in terms)

    def add(rule: str, lens_ids: List[str], tension: str, basis: str, severity: str) -> None:
        counter[0] += 1
        edges.append(
            {
                "id": f"AUD-EDGE-{counter[0]:03d}",
                "rule": rule,
                "relation": "discovery_tension",
                "attention_required": True,
                "severity": severity,
                "tension": tension,
                "attention_basis": basis,
                "attention_lens_ids": lens_ids,
                "status": "open",
                "decision": None,
                "status_reason": "Deep-audit discovery tension; no researcher resolution yet.",
                "response_options": deepcopy(_RESPONSE_OPTIONS),
                "epistemic_status": "deep_audit_rule",
                "boundary_notice": (
                    "This tension was generated by a discovery rule, not by your own "
                    "commitments. Treat it as a prompt to look where you did not write."
                ),
            }
        )

    # Rule: consent not evidenced
    if has("data", "collect", "scan", "monitor", "track") and not has(
        "consent", "opt-in", "opt in", "同意", "知情同意"
    ):
        if high & {"sensitive_personal_data", "surveillance_monitoring", "minors_students"}:
            add(
                "consent_not_evidenced",
                _RULE_LENS["consent_not_evidenced"],
                "The plan collects or monitors data but shows no explicit consent or "
                "opt-in step for the people affected.",
                "Data collection without an evidenced consent pathway is a recurring "
                "failure mode (see school facial-recognition fine, 2019).",
                "high",
            )

    # Rule: affected party has no agency
    if has("student", "user", "people", "学生", "用户", "人群") and not has(
        "consult", "opt-in", "voice", "participate", "咨询", "参与", "发声"
    ):
        add(
            "affected_party_has_no_agency",
            _RULE_LENS["affected_party_has_no_agency"],
            "The plan affects people but gives them no stated way to be informed, "
            "consulted, or to object.",
            "Affected non-users are easy to omit; the perspective/participation lens "
            "stays at Claimed without a participation pathway.",
            "elevated",
        )

    # Rule: automated decision without human in the loop
    if high & {"mental_health", "automated_decision"} and has(
        "flag", "predict", "score", "classify", "标记", "预测", "打分"
    ) and not has(
        "clinician", "counselor", "human review", "overrides", "咨询师", "人工复核", "人工审核"
    ):
        add(
            "automated_decision_without_human_in_loop",
            _RULE_LENS["automated_decision_without_human_in_loop"],
            "An automated flag operates without a named human review/override before "
            "any consequential action.",
            "Automated decisions need a person able to review and override (GDPR Art. 22).",
            "high",
        )

    # Rule: no purpose limitation
    if high & {"surveillance_monitoring", "minors_students"} and not has(
        "purpose limitation", "only for", "prohibit reuse", "禁止复用", "仅用于", "目的限制"
    ):
        add(
            "no_purpose_limitation",
            _RULE_LENS["no_purpose_limitation"],
            "The system is built for one caring purpose but has no stated limit "
            "preventing administrative or disciplinary reuse.",
            "Purpose creep is common once monitoring infrastructure exists (PredPol).",
            "high",
        )

    # Rule: monitoring without redress
    if has("silent", "silently", "monitor", "静默", "监测") and not has(
        "appeal", "redress", "complain", "申诉", "救济", "投诉"
    ):
        add(
            "monitoring_without_redress",
            _RULE_LENS["monitoring_without_redress"],
            "The plan monitors or flags people but states no appeal or redress path.",
            "Monitoring without recourse is a recurring injustice vector (exam proctoring).",
            "elevated",
        )

    return edges


# ---------------------------------------------------------------------------
# Forced reflection questions (#6)
# ---------------------------------------------------------------------------

_LENS_REFLECTION: Dict[str, List[str]] = {
    "lifecycle_integration": [
        "What specifically stops this system being reused for a purpose you did not intend?",
        "Who owns the system after the study ends, and what is deleted?",
    ],
    "benefit_harm_assumptions": [
        "Whose harm did you explicitly model, and how would you know if you were wrong?",
        "What is the false-positive (stigma) vs false-negative (missed harm) trade-off?",
    ],
    "affected_parties_distribution": [
        "Which subgroup is most likely to be burdened, and did they see this plan?",
        "How do you know the benefit actually reaches the people you claim it helps?",
    ],
    "downstream_use_misuse_scale": [
        "If an administrator repurposed this tomorrow, what prevents harm?",
        "What evidence do you have that a stated use-limit will be enforced?",
    ],
    "perspective_participation": [
        "Which real affected person has challenged this design, and what changed?",
        "Where is the opt-out/objection path, and is it actually reachable?",
    ],
    "responsibility_oversight_contestability": [
        "Whose name is on 'review the model monthly'?",
        "What can an affected person contest, and to whom?",
    ],
    "evidence_analogues_horizon": [
        "Name one real system like yours that failed, and what specifically you did differently.",
        "What analogous evidence would change your design if it contradicted your assumption?",
    ],
    "mitigation_design_commitment": [
        "Is each safeguard assigned to a named owner with a trigger and a date?",
        "What makes this mitigation real rather than aspirational?",
    ],
    "monitoring_learning_redress": [
        "When the model drifts, who is paged, and what is the fallback?",
        "What redress exists for someone wrongly flagged?",
    ],
}

_DOMAIN_REFLECTION_TAIL: Dict[str, List[str]] = {
    "surveillance_monitoring": [
        "Have the monitored people been told they are in the system, in plain language?",
    ],
    "minors_students": [
        "Did you obtain both guardian consent and the student's own assent?",
    ],
    "mental_health": [
        "When the system flags acute risk, exactly who is notified and what do they do?",
    ],
    "sensitive_personal_data": [
        "If this pseudonymous data were joined to one outside source, could a person be re-identified?",
    ],
    "automated_decision": [
        "Have you measured error rates per affected subgroup, not only overall?",
    ],
}


def forced_reflection_questions(
    lens: Dict[str, Any],
    domain_flags: Dict[str, Any],
) -> List[str]:
    """Turn a red lens into 2-3 concrete discovery questions."""
    state = (lens.get("state_id") or lens.get("state") or "").lower().replace(" ", "_")
    if state not in ("missing", "claimed"):
        return []
    base = list(_LENS_REFLECTION.get(lens.get("id"), []))
    for d in domain_flags.get("high_risk_domain_ids", []):
        base.extend(_DOMAIN_REFLECTION_TAIL.get(d, []))
    # de-dup, keep order
    seen = set()
    out = []
    for q in base:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out[:3]


# ---------------------------------------------------------------------------
# Real-evidence bridge (#8)
# ---------------------------------------------------------------------------

REAL_EVIDENCE_TYPES: List[Dict[str, Any]] = [
    {
        "id": "stakeholder_minutes",
        "label": "Consultation minutes",
        "description": "Notes or recording from a real affected-person / community consultation.",
    },
    {
        "id": "opt_in_rate",
        "label": "Opt-in / assent rate",
        "description": "Measured consent or assent rate among the affected population.",
    },
    {
        "id": "dpia",
        "label": "DPIA / ethics review",
        "description": "Data Protection Impact Assessment or IRB / ethics-committee approval.",
    },
    {
        "id": "crisis_protocol",
        "label": "Crisis-handoff protocol",
        "description": "Documented human hand-off when acute risk is detected.",
    },
    {
        "id": "redress_path",
        "label": "Redress / appeal path",
        "description": "A reachable appeal or complaint route for wrongly-flagged people.",
    },
]


def build_real_evidence_bridge(dissonance_edges: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    open_edges = [
        e for e in dissonance_edges
        if (e.get("status") or "open") in ("open", "transferred")
    ]
    return {
        "evidence_types": deepcopy(REAL_EVIDENCE_TYPES),
        "open_edge_count": len(open_edges),
        "notice": (
            "Synthetic role probes are hypotheses, not evidence. Attach real "
            "stakeholder artefacts to convert an open tension into a "
            "real-evidence-backed resolution."
        ),
        "validation_rule": (
            "An edge is marked real_evidence_backed only when the attached payload "
            "names a recognised evidence type and a concrete artefact reference."
        ),
    }


def validate_real_evidence(payload: Any) -> Tuple[bool, str]:
    """Validate a researcher-submitted real-evidence attachment."""
    if not isinstance(payload, dict):
        return False, "Evidence payload must be an object."
    etype = payload.get("evidence_type")
    if etype not in {t["id"] for t in REAL_EVIDENCE_TYPES}:
        return False, f"Unknown evidence_type: {etype!r}."
    ref = (payload.get("artifact_reference") or "").strip()
    if len(ref) < 4:
        return False, "artifact_reference must name a concrete artefact (>=4 chars)."
    return True, "ok"


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_deep_audit(
    plan: str,
    commitments: Sequence[str],
    passages: Sequence[Dict[str, Any]],
    lenses: Sequence[Dict[str, Any]],
    scenarios: Sequence[Dict[str, Any]],
    intake_answers: Optional[Dict[str, str]] = None,
    domain_flags: Optional[Dict[str, Any]] = None,
    use_llm: bool = False,
    llm_client: Any = None,
    dissonance_edges: Optional[Sequence[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Run the full deep-audit layer and return a single serialisable block."""
    domain_flags = domain_flags or classify_domain_flags(plan, intake_answers)
    contradictions = detect_internal_contradictions(
        plan, commitments, passages, use_llm=use_llm, llm_client=llm_client
    )
    severity = weight_severity(lenses, domain_flags)
    extra_edges = extra_dissonance_rules(plan, lenses, domain_flags)

    forced: Dict[str, List[str]] = {}
    for lens in lenses:
        qs = forced_reflection_questions(lens, domain_flags)
        if qs:
            forced[lens["id"]] = qs

    missing_lens_ids = [
        lens["id"] for lens in lenses
        if (lens.get("state_id") or lens.get("state", "")).lower().replace(" ", "_")
        in ("missing", "claimed")
    ]
    analogues = recommend_analogues(
        missing_lens_ids, domain_flags.get("high_risk_domain_ids", []), plan
    )
    patterns = match_patterns(domain_flags.get("high_risk_domain_ids", []), plan)

    return {
        "schema": "deep_audit.v1",
        "notice": DEEP_AUDIT_NOTICE,
        "domain_flags": domain_flags,
        "internal_contradictions": contradictions,
        "severity_weighted_gaps": severity,
        "additional_dissonance_edges": extra_edges,
        "forced_reflection": forced,
        "analogues": analogues,
        "patterns": patterns,
        "real_evidence_bridge": build_real_evidence_bridge(
            list(dissonance_edges) if dissonance_edges is not None else []
        ),
        "counts": {
            "domain_flags": len(domain_flags.get("matched_domains", [])),
            "internal_contradictions": len(contradictions),
            "additional_dissonance_edges": len(extra_edges),
            "prioritized_gaps": len(severity.get("prioritized_gaps", [])),
            "forced_reflection_lenses": len(forced),
            "analogues": len(analogues),
            "patterns": len(patterns),
        },
    }


def _short(text: str, limit: int = 240) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"
