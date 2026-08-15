"""Curated 'researchers like you usually missed Y' patterns.

Powers improvement #7. Unlike the deterministic lens coverage (which only
reflects what the researcher wrote), these patterns encode recurrent blind
spots observed across real AI-ethics retrospectives and the failure cases in
``mirror_analogues``. When a session's detected high-risk domains or plan text
match a pattern, the Mirror surfaces it as a hypothesis: 'people building X
commonly forgot Y — you may be repeating it unless …'.

This is explicitly a hypothesis-generating cue, not a finding. It must not be
presented as an ethics score.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


_PATTERNS: List[Dict[str, Any]] = [
    {
        "id": "p_silent_monitoring",
        "domains": ["surveillance_monitoring", "minors_students", "mental_health"],
        "keywords": ["silent", "silently", "covert", "without telling", "without notifying", "静默", "隐蔽", "不告知"],
        "pattern": (
            "The team assumes silent or covert monitoring is acceptable because the "
            "aim is beneficial, and treats 'non-notification' as a design detail."
        ),
        "usually_missed": (
            "Non-notification of the monitored person is itself a consent breach, "
            "independent of how worthy the goal is."
        ),
        "prompt": (
            "Who is monitored, and have they been told they are in the system? If "
            "not, what specifically justifies keeping it silent?"
        ),
        "hint_source": "Sweden school facial-recognition fine (2019); exam-proctoring concerns (2020)",
    },
    {
        "id": "p_proxy_consent",
        "domains": ["minors_students", "consent_transparency"],
        "keywords": ["parent", "institution", "school approves", "admin approves", "家长", "学校批准", "机构批准"],
        "pattern": (
            "The team treats institutional or parental approval as sufficient consent "
            "for everyone affected."
        ),
        "usually_missed": (
            "The directly affected student still has no agency or awareness; proxy "
            "consent does not substitute for informing the person monitored."
        ),
        "prompt": (
            "Beyond the approver, what channel informs the actual student, and what "
            "can they do if they object?"
        ),
        "hint_source": "Children's-data guidance (GDPR Art. 8; FERPA)",
    },
    {
        "id": "p_opt_out_illusion",
        "domains": ["consent_transparency", "surveillance_monitoring"],
        "keywords": ["opt-out", "opt out", "退出", "选择退出"],
        "pattern": (
            "An opt-out is offered, but the people monitored are never told they are "
            "in the system, so opt-out is never reachable in practice."
        ),
        "usually_missed": (
            "Opt-out that requires first discovering the system is not a real choice."
        ),
        "prompt": (
            "How would a monitored person first learn they can opt out? If they cannot "
            "learn it, is 'opt-out' honest?"
        ),
        "hint_source": "FTC 'dark pattern' guidance; exam-proctoring disclosures",
    },
    {
        "id": "p_algorithm_as_truth",
        "domains": ["automated_decision", "mental_health", "bias_fairness"],
        "keywords": ["flag", "score", "predict", "risk score", "classify", "标记", "预测", "打分", "分类"],
        "pattern": (
            "The model's flag is treated as a factual signal that warrants action on "
            "its own."
        ),
        "usually_missed": (
            "False positives stigmatise innocent people; false negatives create "
            "accountability gaps when harm later occurs."
        ),
        "prompt": (
            "What is the consequence of a wrong flag, and who is accountable when the "
            "model is wrong?"
        ),
        "hint_source": "COMPAS (2016); UK A-levels (2020)",
    },
    {
        "id": "p_drift_no_owner",
        "domains": ["monitoring_learning_redress", "automated_decision", "surveillance_monitoring"],
        "keywords": ["threshold", "monitor", "retrain", "drift", "阈值", "监测", "重训"],
        "pattern": (
            "Thresholds and monitoring are specified, but no named person owns "
            "review, recall, or recalibration over time."
        ),
        "usually_missed": (
            "Models drift as the world changes (Google Flu Trends); without a named "
            "owner the safeguard decays silently."
        ),
        "prompt": (
            "Whose name is attached to 'review the threshold monthly'? What triggers "
            "a mandatory re-check?"
        ),
        "hint_source": "Google Flu Trends (2014); monitoring/learning/redress lens",
    },
    {
        "id": "p_downstream_scope",
        "domains": ["downstream_use_misuse_scale", "surveillance_monitoring", "minors_students"],
        "keywords": ["campus", "admin", "discipline", "safety", "purpose", "校园", "行政", "纪律", "目的"],
        "pattern": (
            "The system is built for one caring purpose but has no purpose limitation "
            "preventing administrative reuse."
        ),
        "usually_missed": (
            "A wellness scanner is one policy change away from becoming a discipline "
            "or surveillance tool (PredPol-style feedback loops)."
        ),
        "prompt": (
            "What explicitly prohibits reusing this data/system for discipline or "
            "other purposes, and who enforces that limit?"
        ),
        "hint_source": "PredPol (2020); downstream-use/misuse-scale lens",
    },
    {
        "id": "p_no_real_stakeholder",
        "domains": ["perspective_participation", "vulnerable_population", "minors_students"],
        "keywords": ["assume", "we believe", "should be fine", "认为", "应该没问题"],
        "pattern": (
            "The team consults literature and their own reasoning but not the actual "
            "affected people."
        ),
        "usually_missed": (
            "Lived-experience blind spots (stigma, mistrust, accessibility) are "
            "invisible from inside the research team."
        ),
        "prompt": (
            "Which real affected person or community has seen this plan, and what did "
            "they say that changed it?"
        ),
        "hint_source": "Do et al. CHI 2023; perspective/participation lens",
    },
    {
        "id": "p_anonymity_illusion",
        "domains": ["sensitive_personal_data", "downstream_use_misuse_scale"],
        "keywords": ["pseudonym", "anonym", "aggregate", "de-identif", "化名", "匿名", "聚合", "去标识"],
        "pattern": (
            "Pseudonymisation or aggregation is treated as if it were anonymity."
        ),
        "usually_missed": (
            "Joinable datasets are re-identifiable (Netflix Prize); 'pseudonymous' is "
            "not 'safe to share'."
        ),
        "prompt": (
            "If this pseudonymous data were combined with one outside source, could a "
            "person be re-identified? What stops that join?"
        ),
        "hint_source": "Netflix Prize re-identification (2008)",
    },
    {
        "id": "p_crisis_protocol_absent",
        "domains": ["mental_health", "automated_decision"],
        "keywords": ["crisis", "risk", "self-harm", "suicid", "危机", "自伤", "自杀", "风险"],
        "pattern": (
            "Risk is detected by automation but there is no defined human crisis "
            "protocol or duty-of-care path."
        ),
        "usually_missed": (
            "A detected risk with no human hand-off creates moral and legal exposure "
            "and can harm the very person the system aimed to help."
        ),
        "prompt": (
            "When the system flags acute risk, exactly who is notified, within what "
            "time, and what do they do?"
        ),
        "hint_source": "Clinical-duty-of-care literature; mental-health lens",
    },
    {
        "id": "p_fairness_metric_missing",
        "domains": ["bias_fairness", "automated_decision", "vulnerable_population"],
        "keywords": ["accuracy", "precision", "recall", "perform", "准确", "精度", "表现"],
        "pattern": (
            "Performance is reported in aggregate (accuracy / overall score) only."
        ),
        "usually_missed": (
            "Subgroup disparity hides inside aggregate metrics (Gender Shades; "
            "Obermeyer health bias)."
        ),
        "prompt": (
            "Have you measured error rates separately for the subgroups most affected "
            "by this system, not just overall?"
        ),
        "hint_source": "Gender Shades (2018); Obermeyer et al. (2019)",
    },
]


def match_patterns(
    domain_ids: Sequence[str],
    plan: str = "",
) -> List[Dict[str, Any]]:
    """Return patterns whose high-risk domain or plan keyword matches this session."""
    domains = set(domain_ids or [])
    lowered = (plan or "").lower()
    matched: List[Dict[str, Any]] = []
    for pat in _PATTERNS:
        domain_hit = bool(domains & set(pat["domains"]))
        keyword_hit = any(kw in lowered for kw in pat["keywords"])
        if domain_hit or keyword_hit:
            matched.append(
                {
                    "id": pat["id"],
                    "pattern": pat["pattern"],
                    "usually_missed": pat["usually_missed"],
                    "prompt": pat["prompt"],
                    "hint_source": pat["hint_source"],
                    "match": "domain" if domain_hit else "keyword",
                }
            )
    return matched
