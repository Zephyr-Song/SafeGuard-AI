"""Flask Blueprint for the StressLens CHI 2027 study.

This is intentionally separate from the main SafeBARS Ethical Mirror API so
that the experimental intervention can be versioned and analysed independently.
"""

from __future__ import annotations

import json
import os
import random
import re
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, current_app, jsonify, request, url_for

from .mirror_study_data import (
    CONDITIONS,
    FIXES,
    ISSUE_GALLERY,
    SHARED_VIGNETTE,
    classify_issue,
    public_config,
)
from .mirror_study_store import MirrorStudyStore
from .ratelimit import rate_limit
from .llm_client import LLMClient


mirror_study_api = Blueprint(
    "safebars_mirror_study",
    __name__,
    url_prefix="/api/safebars/mirror-study",
)

mirror_study_store = MirrorStudyStore()

# AI analysis client (mirrors the transition-companion architecture: a server-side
# endpoint proxies an LLM and returns structured JSON the front end renders).
_LLM: Any = None


def _get_llm() -> Any:
    global _LLM
    if _LLM is None:
        _LLM = LLMClient()
    return _LLM


# Image ids the AI is allowed to pick from (keeps the visual grounded in the
# curated, paper-ready illustration set rather than generating images on the fly).
_IMAGE_IDS = [item["id"] for item in ISSUE_GALLERY if item["id"] != "default"]
_IMAGE_BY_ID = {item["id"]: item for item in ISSUE_GALLERY}

_ANALYZE_SYSTEM = (
    "You are Mirror, an ethical-research companion for the SafeBARS StressLens study. "
    "A graduate researcher will describe a real ethical concern from their own AI/ML research. "
    "Your job is to help them reflect, not to judge their design. Respond with ONLY a JSON "
    "object (no markdown, no code fences) using exactly these keys:\n"
    "- summary: one warm, non-judgemental sentence that acknowledges the concern\n"
    "- reflection: 2-3 sentences that surface the key ethical tension(s) and why they "
    "matter for someone designing an ethics protocol\n"
    "- theme_label: a short 3-8 word label for the concern\n"
    "- suggested_image_id: the id from this list that BEST matches the concern: "
    f"{', '.join(_IMAGE_IDS)}\n"
    "- related_concerns: an array of exactly 3 short concern phrases (4-8 words each), "
    "each a DIFFERENT facet the researcher might also want to consider\n"
    "- ethical_dimensions: an array of 2-4 short ethical-dimension labels (2-4 words each) "
    "that apply to this concern\n"
    "Be concise, specific and genuinely useful. Never invent an image id outside the list."
)


# ---------------------------------------------------------------------------
# Stage 1 — conversation. Mirror interviews the researcher one question at a
# time instead of analysing everything up front.
# ---------------------------------------------------------------------------
_CHAT_SYSTEM = (
    "You are Mirror, an ethical-research companion talking with a graduate researcher "
    "about their own AI/ML study. This is a CONVERSATION, not a report. You are not "
    "judging their design.\n"
    "Your goal across roughly 4 exchanges is to learn enough to name concrete, fixable "
    "problems later. Work towards understanding:\n"
    "  (a) what data is actually collected and where it travels (which people, which vendors),\n"
    "  (b) who could be harmed and who never agreed to take part,\n"
    "  (c) which single step in the workflow is most fragile (review, escalation, deletion, feedback),\n"
    "  (d) what the researcher personally has the power to change.\n"
    "Rules:\n"
    "- Reply with ONLY a JSON object, no markdown, no code fences.\n"
    "- Ask exactly ONE question per turn. Never stack two questions.\n"
    "- The question must be specific to what they just said, not generic ethics boilerplate.\n"
    "- Use plain language. No jargon, no lecturing, no bullet lists in the reply.\n"
    "- Set ready=true once you understand (a)-(d) well enough, or by the 4th exchange.\n"
    "Keys:\n"
    "- reply: 1-2 warm sentences reflecting back what you just heard (no question here)\n"
    "- question: the ONE next question (empty string if ready is true)\n"
    "- ready: boolean, true when you have enough to summarise concrete issues\n"
    "- still_unknown: a short phrase naming what you still do not know (empty if ready)\n"
)

# ---------------------------------------------------------------------------
# Stage 2 — exactly five CONCRETE, selectable issues. This is where the old
# hard-coded category list used to be; it is now generated from the dialogue.
# ---------------------------------------------------------------------------
_ISSUES_SYSTEM = (
    "You are Mirror. You have just finished interviewing a graduate researcher about "
    "their AI/ML study. Turn that conversation into EXACTLY 5 issues they can choose "
    "to work on.\n"
    "THE MOST IMPORTANT RULE: every issue must be NARROW AND FIXABLE. It must name a "
    "specific mechanism, artefact, step or moment from THEIR study.\n"
    "FORBIDDEN as a title: broad category words on their own — 'Privacy', 'Consent', "
    "'Transparency', 'Bias', 'Fairness', 'Data collection', 'Ethics', 'Accountability', "
    "'Third parties', 'Model error', 'Deletion', 'Researcher burden'. Those are topics, "
    "not problems. A good title names the thing that breaks, e.g. 'Weekly feedback email "
    "goes out with no human check' or 'Roommates named in diaries never agreed'.\n"
    "Each issue must be solvable by a change the researcher personally controls, within "
    "weeks, without new funding. If an issue would take a policy change or a new grant, "
    "narrow it until it fits.\n"
    "The 5 issues must be clearly distinct (no overlap) and ordered most-urgent first.\n"
    "Reply with ONLY a JSON object, no markdown, no code fences, with key 'issues': an "
    "array of exactly 5 objects, each with these keys:\n"
    "- title: 5-12 words, concrete, names the specific mechanism or moment\n"
    "- one_line: one sentence saying exactly what goes wrong in their setting\n"
    "- changeable_decision: the single decision or step they could change (an action, "
    "not a value or an aspiration)\n"
    "- who_is_affected: who specifically bears the cost\n"
    "- severity: one of low, medium, high, critical\n"
    "- effort: one of low, medium, high\n"
    "- why_specific: one sentence on why this is narrow enough to start this week\n"
    "- image_id: the best match from this list: " + ", ".join(_IMAGE_IDS) + "\n"
    "Never invent an image_id outside that list."
)

# ---------------------------------------------------------------------------
# Stage 3 — a dated trajectory for ONE chosen issue, plus a single leverage
# point. Deliberately refuses to broaden back out to general ethics.
# ---------------------------------------------------------------------------
_TIMELINE_SYSTEM = (
    "You are Mirror. The researcher has chosen ONE specific issue from their own study "
    "to work on. Project how it plays out over time if nothing changes, then give them "
    "one concrete place to intervene.\n"
    "STAY ON THIS ONE POINT. Do not broaden into general AI ethics, do not introduce new "
    "unrelated risks, do not moralise. Every frame must be a plausible downstream "
    "consequence of this exact decision.\n"
    "Reply with ONLY a JSON object, no markdown, no code fences, with these keys:\n"
    "- focus: restate the single specific point being worked on, max 14 words\n"
    "- frames: array of EXACTLY 5 objects with increasing time labels, in this order: "
    "'Week 1', 'Week 3', 'Month 2', 'Month 6', 'Month 12'. Each object has:\n"
    "    when: the time label\n"
    "    headline: 4-9 words naming what has happened by then\n"
    "    what_happens: 1-2 concrete sentences, specific to their study\n"
    "    who_is_affected: who feels it at this point\n"
    "    severity: one of low, medium, high, critical (must not decrease over time)\n"
    "    early_signal: the observable sign they could actually notice at this point\n"
    "- leverage_point: object with keys action (the smallest concrete change that bends "
    "this trajectory), when (a deadline like 'before the next participant enrols'), "
    "owner (which role does it), cost (realistic effort in plain words)\n"
    "- if_nothing_changes: one sentence end-state\n"
    "- if_you_act_now: one sentence better end-state\n"
    "- first_step_this_week: one concrete step, max 20 words, something doable on a laptop\n"
    "- how_to_measure: how they would know the fix actually worked\n"
)

_SEVERITIES = ("low", "medium", "high", "critical")
_EFFORTS = ("low", "medium", "high")
_FRAME_LABELS = ("Week 1", "Week 3", "Month 2", "Month 6", "Month 12")

# Category words that must not stand alone as an issue title — the exact thing
# the researcher objected to in the previous hard-coded build.
_VAGUE_TITLES = {
    "privacy", "consent", "transparency", "bias", "fairness", "ethics",
    "data collection", "accountability", "third parties", "third-party",
    "model error", "deletion", "retention", "researcher burden", "burden",
    "crisis", "human review", "local control", "bystanders", "uncertainty",
    "data protection", "informed consent", "trust", "safety",
}


def _extract_json(text: str) -> Any:
    """Best-effort JSON extraction from an LLM response."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```", 2)
        if len(parts) >= 2:
            text = parts[1]
            if text.lower().startswith("json"):
                text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None


def _normalize_analysis(data: Dict[str, Any], issue: str) -> Dict[str, Any]:
    suggested = data.get("suggested_image_id")
    if suggested not in _IMAGE_BY_ID:
        suggested = classify_issue(issue)["id"]
    theme = _IMAGE_BY_ID.get(suggested, ISSUE_GALLERY[-1])
    related = [str(x).strip() for x in data.get("related_concerns", []) if str(x).strip()][:3]
    dims = [str(x).strip() for x in data.get("ethical_dimensions", []) if str(x).strip()][:4]
    return {
        "issue": issue,
        "summary": str(data.get("summary", "")).strip()[:400],
        "reflection": str(data.get("reflection", "")).strip()[:1200],
        "theme_label": str(data.get("theme_label", theme["label"])).strip()[:120],
        "theme_id": theme["id"],
        "image_url": _image_url(theme["image"]),
        "related_concerns": related,
        "ethical_dimensions": dims,
    }


def _fallback_analysis(issue: str) -> Dict[str, Any]:
    theme = classify_issue(issue)
    others = [t["label"] for t in ISSUE_GALLERY if t["id"] not in (theme["id"], "default")]
    return {
        "issue": issue,
        "summary": "Thanks for sharing that — it is worth thinking through carefully.",
        "reflection": theme["reflection"],
        "theme_label": theme["label"],
        "theme_id": theme["id"],
        "image_url": _image_url(theme["image"]),
        "related_concerns": others[:3],
        "ethical_dimensions": [],
    }


def _call_deepseek_json(
    api_key: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 900,
    temperature: float = 0.5,
) -> Dict[str, Any]:
    """Direct OpenAI-compatible DeepSeek call returning a parsed JSON object.

    Uses the exact endpoint/model/flags the Transition Companion prototype relies on
    (Aliyun MaaS `deepseek-v4-pro`, `enable_thinking: false`, `response_format: json_object`)
    and falls back to a user-configured DEEPSEEK_BASE_URL or standard api.deepseek.com.
    Captures the real HTTP status so a bad key vs. wrong model is diagnosable.
    """
    import requests

    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
    configured = (os.getenv("DEEPSEEK_BASE_URL") or "").rstrip("/")
    candidates: List[str] = []
    if configured:
        candidates.append(configured)
    for base in [
        "https://ws-rpz6r7sem6fuiceu.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        "https://api.deepseek.com/v1",
    ]:
        if base not in candidates:
            candidates.append(base)

    last_err: Any = RuntimeError("DeepSeek unavailable")
    last_detail: str = ""
    for base in candidates:
        try:
            payload = {
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_object"},
                "enable_thinking": False,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            resp = requests.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            if resp.status_code != 200:
                last_detail = f"HTTP {resp.status_code}: {resp.text[:180]}"
                raise RuntimeError(last_detail)
            text = resp.json()["choices"][0]["message"]["content"]
            data = _extract_json(text)
            if not isinstance(data, dict):
                raise ValueError("DeepSeek returned no JSON object")
            return data
        except Exception as exc:  # try next candidate endpoint
            last_err = exc
            continue
    detail = f" ({last_detail})" if last_detail else ""
    raise RuntimeError(f"{type(last_err).__name__}{detail}")


def _llm_json(
    system: str,
    user: str,
    max_tokens: int = 900,
    temperature: float = 0.5,
    label: str = "llm",
) -> Tuple[Optional[Dict[str, Any]], str]:
    """Generic structured-JSON LLM call shared by /chat, /issues and /timeline.

    Prefers a dedicated DeepSeek key (matching the Transition Companion prototype),
    then tries EVERY configured SafeBARS provider (active one first) in OpenAI-compatible
    JSON mode. Returns (parsed_dict, error_string); (None, errors) when all fail.
    """
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    errors: List[str] = []

    # 1) Dedicated DeepSeek key (mirrors the Transition Companion prototype).
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    if ds_key:
        try:
            return _call_deepseek_json(ds_key, messages, max_tokens, temperature), ""
        except Exception as exc:
            errors.append(f"deepseek:{exc}")
            current_app.logger.warning("Mirror %s DeepSeek call failed: %s", label, exc)

    # 2) Configured SafeBARS providers (active first), JSON mode.
    #    Cap the fallback chain so the total LLM budget stays well under the
    #    gunicorn worker timeout (Render free tier): active provider first, then
    #    at most ONE more, each with a 25s timeout. A single good provider is
    #    enough; exhausting every provider only risks a 502 on heavy prompts.
    llm = _get_llm()
    if llm and llm.is_configured():
        order: List[str] = []
        if llm.active_provider_id:
            order.append(llm.active_provider_id)
        order += [pid for pid in llm.providers if pid not in order]
        order = order[:2]  # active + one fallback only
        for pid in order:
            try:
                resp = llm.chat_with_provider_detailed(
                    pid,
                    messages,
                    temperature=temperature,
                    timeout=25,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                if resp and resp.get("ok") and resp.get("text"):
                    data = _extract_json(resp["text"])
                    if isinstance(data, dict):
                        return data, ""
                    errors.append(f"{pid}:no_json")
                else:
                    status = resp.get("status_code") if resp else None
                    err_type = (resp or {}).get("error_type", "?")
                    errors.append(f"{pid}:{err_type}" + (f"[{status}]" if status else ""))
            except Exception as exc:
                errors.append(f"{pid}:{type(exc).__name__}")
                current_app.logger.warning("Mirror %s %s failed: %s", label, pid, exc)

    return None, " | ".join(errors)[:400]


def _analyze_with_llm(issue: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Legacy single-shot analysis (kept for backwards compatibility)."""
    data, err = _llm_json(
        _ANALYZE_SYSTEM,
        f"Researcher's concern: {issue}",
        max_tokens=700,
        temperature=0.4,
        label="/analyze",
    )
    if data and data.get("reflection") and isinstance(data.get("related_concerns"), list):
        return _normalize_analysis(data, issue), ""
    return None, err or "incomplete_response"


# ---------------------------------------------------------------------------
# Shared helpers for the three-stage flow
# ---------------------------------------------------------------------------

_FILLER = {
    "and", "or", "the", "of", "in", "a", "an", "issues", "issue", "concerns",
    "concern", "problems", "problem", "risks", "risk", "amp",
}


def _norm_choice(value: Any, allowed: Tuple[str, ...], default: str) -> str:
    v = str(value or "").strip().lower()
    for a in allowed:
        if a in v:
            return a
    return default


def _clip(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _is_vague_title(title: str) -> bool:
    """True when a title is only a broad category label.

    The researcher explicitly rejected a hard-coded list of topic labels
    ('Consent & transparency', 'Model error & uncertainty', ...), so any AI
    output that drifts back to that shape is rewritten downstream.
    """
    cleaned = re.sub(r"[^a-z ]+", " ", (title or "").lower())
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return True
    if cleaned in _VAGUE_TITLES:
        return True
    words = cleaned.split()
    if len(words) <= 4:
        core = [w for w in words if w not in _FILLER]
        if core and " ".join(core) in _VAGUE_TITLES:
            return True
        if core and all(w in _VAGUE_TITLES for w in core):
            return True
    return False


def _sentence_title(text: str, limit: int = 74) -> str:
    """Turn a sentence into a compact concrete title."""
    t = " ".join(str(text or "").split())
    t = t.rstrip(".")
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def _clean_messages(raw: Any, limit: int = 24) -> List[Dict[str, str]]:
    """Validate a client-supplied transcript into role/content pairs."""
    out: List[Dict[str, str]] = []
    if not isinstance(raw, list):
        return out
    for item in raw[-limit:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        content = _clip(item.get("content"), 1500)
        if role not in ("user", "assistant") or not content:
            continue
        out.append({"role": role, "content": content})
    return out


def _transcript_text(messages: List[Dict[str, str]], limit: int = 4000) -> str:
    lines = []
    for m in messages:
        who = "Researcher" if m["role"] == "user" else "Mirror"
        lines.append(f"{who}: {m['content']}")
    return "\n".join(lines)[:limit]


def _user_text(messages: List[Dict[str, str]]) -> str:
    return " ".join(m["content"] for m in messages if m["role"] == "user")[:4000]


# ---------------------------------------------------------------------------
# Stage 1 — chat
# ---------------------------------------------------------------------------

_FALLBACK_QUESTIONS = [
    "What data does the study actually collect, and where does it end up — your own "
    "machine, a university server, or an outside company?",
    "Who could be affected by this without ever having agreed to take part?",
    "Which single step worries you most: how it is reviewed, what happens in an "
    "emergency, or how data gets deleted?",
    "Of everything you have described, what could you personally change in the next "
    "two weeks without asking anyone's permission?",
]


def _fallback_chat(turn: int, last_user: str) -> Dict[str, Any]:
    idx = max(0, min(turn, len(_FALLBACK_QUESTIONS) - 1))
    ready = turn >= len(_FALLBACK_QUESTIONS) - 1
    snippet = _clip(last_user, 90)
    reply = (
        f"Thanks — I hear you on {snippet.rstrip('.')}." if snippet
        else "Thanks for starting this off."
    )
    return {
        "reply": reply,
        "question": "" if ready else _FALLBACK_QUESTIONS[idx],
        "ready": ready,
        "still_unknown": "" if ready else "how the data moves and who reviews it",
    }


def _normalize_chat(data: Dict[str, Any], turn: int) -> Dict[str, Any]:
    ready = bool(data.get("ready")) or turn >= 4
    return {
        "reply": _clip(data.get("reply"), 500),
        "question": "" if ready else _clip(data.get("question"), 300),
        "ready": ready,
        "still_unknown": "" if ready else _clip(data.get("still_unknown"), 160),
    }


# ---------------------------------------------------------------------------
# Stage 2 — five concrete issues
# ---------------------------------------------------------------------------


def _normalize_issues(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = data.get("issues")
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, Any]] = []
    for i, item in enumerate(raw[:5]):
        if not isinstance(item, dict):
            continue
        one_line = _clip(item.get("one_line"), 320)
        decision = _clip(item.get("changeable_decision"), 320)
        title = _clip(item.get("title"), 110)
        # Guard against the AI drifting back to broad category labels.
        if _is_vague_title(title):
            title = _sentence_title(one_line or decision or title)
        if not title:
            continue
        image_id = item.get("image_id")
        if image_id not in _IMAGE_BY_ID:
            image_id = classify_issue(f"{title} {one_line} {decision}")["id"]
        theme = _IMAGE_BY_ID.get(image_id, ISSUE_GALLERY[-1])
        out.append({
            "id": f"iss_{i + 1}",
            "title": title,
            "one_line": one_line,
            "changeable_decision": decision,
            "who_is_affected": _clip(item.get("who_is_affected"), 200),
            "severity": _norm_choice(item.get("severity"), _SEVERITIES, "medium"),
            "effort": _norm_choice(item.get("effort"), _EFFORTS, "medium"),
            "why_specific": _clip(item.get("why_specific"), 260),
            "image_id": theme["id"],
            "image_url": _image_url(theme["image"]),
        })
    return out


def _fallback_issues(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Deterministic issue set so the study still runs without any LLM key.

    Titles stay concrete by describing the mechanism, never the bare category.
    """
    text = _user_text(messages)
    primary = classify_issue(text)
    ordered = [primary] + [
        t for t in ISSUE_GALLERY if t["id"] not in (primary["id"], "default")
    ]
    templates = {
        "data_collection": (
            "Free-text answers leave your machine for an outside vendor",
            "Raw participant text is sent to a third-party service that is not named in the consent form.",
            "List every service the text touches, then name them in the consent form.",
            "Participants and anyone they mention",
        ),
        "consent": (
            "The consent form does not match what the system really does",
            "Participants agree to a short description that leaves out the automated analysis step.",
            "Rewrite the one paragraph that describes the automated analysis.",
            "Every enrolled participant",
        ),
        "model_risk": (
            "Model labels are shown without any confidence or check",
            "A confident-looking label reaches a person even when the model is unsure or wrong.",
            "Hide labels below a confidence threshold until a human has read them.",
            "Anyone the model mislabels",
        ),
        "deletion": (
            "A deletion request stops at your copy of the data",
            "Withdrawal removes your local row but not backups, embeddings or vendor logs.",
            "Write a deletion checklist that names each store, then test it once end to end.",
            "Participants who withdraw",
        ),
        "burden": (
            "One assistant reads distressing material alone",
            "Flagged content lands on a single person with no rota, no cap and no debrief.",
            "Cap how much flagged content one person reviews per session and add a second reader.",
            "Research assistants",
        ),
        "crisis": (
            "A crisis flag has nowhere to go after hours",
            "The system can detect distress but there is no named person to escalate to at night.",
            "Name one on-call contact and write the escalation steps on a single page.",
            "Participants in distress",
        ),
        "human_review": (
            "Automated output reaches people with no human in between",
            "Generated feedback is delivered directly, so nobody catches a harmful message first.",
            "Add a hold queue so a person releases the first week of messages by hand.",
            "Participants receiving feedback",
        ),
        "local_control": (
            "Sensitive text is processed off-site when it need not be",
            "Content that could stay on your own hardware is routed through an external API by default.",
            "Move the most sensitive field to local processing and keep the rest as is.",
            "All participants",
        ),
        "bystanders": (
            "People named in the data never agreed to be there",
            "Friends, roommates and family appear in participant text without any say in it.",
            "Strip or pseudonymise third-party names at intake, before analysis.",
            "Named non-participants",
        ),
    }
    out: List[Dict[str, Any]] = []
    sev = ["critical", "high", "high", "medium", "medium"]
    eff = ["low", "medium", "low", "medium", "low"]
    for i, theme in enumerate(ordered[:5]):
        tpl = templates.get(theme["id"])
        if tpl:
            title, one_line, decision, who = tpl
        else:
            title = _sentence_title(theme["reflection"])
            one_line = theme["reflection"]
            decision = "Write down the one step you would change first."
            who = "Participants"
        out.append({
            "id": f"iss_{i + 1}",
            "title": title,
            "one_line": one_line,
            "changeable_decision": decision,
            "who_is_affected": who,
            "severity": sev[i],
            "effort": eff[i],
            "why_specific": "It touches one step you already control, so you can start on it this week.",
            "image_id": theme["id"],
            "image_url": _image_url(theme["image"]),
        })
    return out


# ---------------------------------------------------------------------------
# Stage 3 — dated trajectory for one chosen issue
# ---------------------------------------------------------------------------


def _normalize_timeline(data: Dict[str, Any], issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    raw = data.get("frames")
    if not isinstance(raw, list) or len(raw) < 3:
        return None
    frames: List[Dict[str, Any]] = []
    rank = {s: i for i, s in enumerate(_SEVERITIES)}
    floor = 0
    for i, item in enumerate(raw[:5]):
        if not isinstance(item, dict):
            continue
        sev = _norm_choice(item.get("severity"), _SEVERITIES, "medium")
        # Severity must not decrease along the trajectory.
        if rank[sev] < floor:
            sev = _SEVERITIES[floor]
        floor = rank[sev]
        frames.append({
            "when": _clip(item.get("when"), 24) or _FRAME_LABELS[min(i, 4)],
            "headline": _clip(item.get("headline"), 110),
            "what_happens": _clip(item.get("what_happens"), 420),
            "who_is_affected": _clip(item.get("who_is_affected"), 160),
            "severity": sev,
            "early_signal": _clip(item.get("early_signal"), 220),
        })
    if not frames:
        return None
    lp = data.get("leverage_point")
    lp = lp if isinstance(lp, dict) else {}
    return {
        "focus": _clip(data.get("focus"), 140) or _clip(issue.get("title"), 140),
        "frames": frames,
        "leverage_point": {
            "action": _clip(lp.get("action"), 300) or _clip(issue.get("changeable_decision"), 300),
            "when": _clip(lp.get("when"), 120) or "Before the next participant enrols",
            "owner": _clip(lp.get("owner"), 120) or "You, as lead researcher",
            "cost": _clip(lp.get("cost"), 160) or "A few hours",
        },
        "if_nothing_changes": _clip(data.get("if_nothing_changes"), 320),
        "if_you_act_now": _clip(data.get("if_you_act_now"), 320),
        "first_step_this_week": _clip(data.get("first_step_this_week"), 220),
        "how_to_measure": _clip(data.get("how_to_measure"), 260),
    }


def _fallback_timeline(issue: Dict[str, Any]) -> Dict[str, Any]:
    title = _clip(issue.get("title"), 110) or "this decision"
    who = _clip(issue.get("who_is_affected"), 160) or "Participants"
    decision = _clip(issue.get("changeable_decision"), 300) or "Change the one step you control."
    specs = [
        ("Week 1", "Nobody notices yet", "low",
         "The study runs as designed and the gap is invisible from the inside.",
         "Nothing looks wrong, which is exactly why it stays unfixed."),
        ("Week 3", "The first uncomfortable case", "medium",
         "A single case appears that the current process cannot handle cleanly.",
         "Someone asks a question your documentation cannot answer."),
        ("Month 2", "Workarounds become the process", "high",
         "The team improvises a fix per case, and the informal habit hardens into the norm.",
         "Decisions get made in chat messages rather than in the protocol."),
        ("Month 6", "It becomes hard to undo", "high",
         "Data, expectations and downstream analyses now depend on the shortcut.",
         "Fixing it would mean re-contacting people or re-running analysis."),
        ("Month 12", "It surfaces where it costs most", "critical",
         "The gap shows up in review, publication or a complaint, when options are narrowest.",
         "You are explaining the decision to someone outside your team."),
    ]
    frames = [
        {
            "when": when,
            "headline": headline,
            "what_happens": f"{what} Concretely: {title.lower()}.",
            "who_is_affected": who,
            "severity": sev,
            "early_signal": signal,
        }
        for when, headline, sev, what, signal in specs
    ]
    return {
        "focus": title,
        "frames": frames,
        "leverage_point": {
            "action": decision,
            "when": "Before the next participant enrols",
            "owner": "You, as lead researcher",
            "cost": "A few hours of writing and one team conversation",
        },
        "if_nothing_changes": (
            "The shortcut quietly becomes permanent, and the cost lands on "
            f"{who.lower()} rather than on the team."
        ),
        "if_you_act_now": (
            "One small change made this week keeps the choice reversible and "
            "documented, so nobody has to guess later."
        ),
        "first_step_this_week": _sentence_title(decision, 120),
        "how_to_measure": (
            "You can point to one written line that says what happens, and one "
            "person who is responsible for it."
        ),
    }


@mirror_study_api.post("/chat")
@rate_limit(max_requests=40, window_seconds=120, scope="mirror_study_chat")
def chat():
    """Stage 1: one conversational turn with Mirror.

    Mirror asks a single specific question at a time instead of analysing the
    whole concern up front, then signals `ready` when it can summarise issues.

    Body: {"messages": [{"role": "user"|"assistant", "content": "..."}]}
    """
    payload, error = _json_object()
    if error:
        return error

    messages = _clean_messages(payload.get("messages"))
    if not messages or messages[-1]["role"] != "user":
        return jsonify({"success": False, "error": "A final 'user' message is required."}), 400

    turn = sum(1 for m in messages if m["role"] == "user")
    prompt = (
        f"{_transcript_text(messages)}\n\n"
        f"This is exchange {turn}. Reply as Mirror with the JSON object."
    )
    data, ai_error = _llm_json(_CHAT_SYSTEM, prompt, max_tokens=420, temperature=0.6, label="/chat")

    if data and _clip(data.get("reply"), 500):
        result = _normalize_chat(data, turn)
        source = "ai"
    else:
        result = _fallback_chat(turn, messages[-1]["content"])
        source = "fallback"

    return jsonify({
        "success": True,
        "source": source,
        "turn": turn,
        "ai_error": ai_error if source == "fallback" else "",
        **result,
    })


@mirror_study_api.post("/issues")
@rate_limit(max_requests=15, window_seconds=120, scope="mirror_study_issues")
def issues():
    """Stage 2: summarise the conversation into exactly 5 selectable issues.

    Each issue names a concrete, fixable mechanism from the researcher's own
    study rather than a broad ethics category.

    Body: {"messages": [...]}
    """
    payload, error = _json_object()
    if error:
        return error

    messages = _clean_messages(payload.get("messages"))
    if not messages:
        return jsonify({"success": False, "error": "'messages' is required."}), 400

    prompt = (
        f"Conversation with the researcher:\n{_transcript_text(messages)}\n\n"
        "Now return the JSON object with exactly 5 concrete, fixable issues."
    )
    data, ai_error = _llm_json(_ISSUES_SYSTEM, prompt, max_tokens=1600, temperature=0.45, label="/issues")

    items = _normalize_issues(data) if data else []
    if len(items) >= 3:
        source = "ai"
    else:
        items = _fallback_issues(messages)
        source = "fallback"

    return jsonify({
        "success": True,
        "source": source,
        "ai_error": ai_error if source == "fallback" else "",
        "issues": items,
    })


@mirror_study_api.post("/timeline")
@rate_limit(max_requests=20, window_seconds=120, scope="mirror_study_timeline")
def timeline():
    """Stage 3: dated trajectory plus one leverage point for a chosen issue.

    Body: {"issue": {...one issue object...}, "messages": [...]}
    """
    payload, error = _json_object()
    if error:
        return error

    issue = payload.get("issue")
    if not isinstance(issue, dict) or not _clip(issue.get("title"), 110):
        return jsonify({"success": False, "error": "'issue' with a title is required."}), 400

    messages = _clean_messages(payload.get("messages"))
    prompt = (
        f"The researcher's study, in their own words:\n{_transcript_text(messages, 2500) or 'not provided'}\n\n"
        "THE ONE ISSUE THEY CHOSE TO WORK ON:\n"
        f"- title: {_clip(issue.get('title'), 200)}\n"
        f"- what goes wrong: {_clip(issue.get('one_line'), 320)}\n"
        f"- the decision they can change: {_clip(issue.get('changeable_decision'), 320)}\n"
        f"- who is affected: {_clip(issue.get('who_is_affected'), 200)}\n\n"
        "Return the JSON object. Stay strictly on this one point."
    )
    data, ai_error = _llm_json(_TIMELINE_SYSTEM, prompt, max_tokens=1200, temperature=0.5, label="/timeline")

    result = _normalize_timeline(data, issue) if data else None
    if result:
        source = "ai"
    else:
        result = _fallback_timeline(issue)
        source = "fallback"

    return jsonify({
        "success": True,
        "source": source,
        "ai_error": ai_error if source == "fallback" else "",
        "issue_id": _clip(issue.get("id"), 40),
        **result,
    })


def _json_object() -> Tuple[Dict[str, Any], Any]:
    payload = request.get_json(silent=True)
    if payload is None:
        return {}, None
    if not isinstance(payload, dict):
        return {}, (
            jsonify({"success": False, "error": "Request body must be a JSON object."}),
            400,
        )
    return payload, None


def _image_url(path: str) -> str:
    """Resolve a static image path to an absolute URL."""
    return url_for("static", filename=path, _external=False)


def _condition_with_urls(condition: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of a condition with image URLs resolved."""
    out = {**condition}
    out["frames"] = [
        {**frame, "image_url": _image_url(frame["image"])}
        for frame in condition.get("frames", [])
    ]
    return out


def _fixes_with_urls() -> List[Dict[str, Any]]:
    return [{**fix, "image_url": _image_url(fix["image"])} for fix in FIXES]


def _issue_gallery_with_urls() -> List[Dict[str, Any]]:
    return [{**item, "image_url": _image_url(item["image"])} for item in ISSUE_GALLERY]


@mirror_study_api.get("/config")
def get_config():
    """Return the public vignette, conditions, fixes and issue gallery with URLs."""
    cfg = public_config()
    cfg["conditions"] = {
        k: _condition_with_urls(v) for k, v in cfg["conditions"].items()
    }
    cfg["fixes"] = _fixes_with_urls()
    cfg["issue_gallery"] = _issue_gallery_with_urls()
    return jsonify({"success": True, **cfg})


@mirror_study_api.post("/issue-image")
@rate_limit(max_requests=10, window_seconds=60, scope="mirror_study_issue_image")
def issue_image():
    """Map a user-supplied issue to a generated AI illustration.

    Body:
      {"issue": "free-text description of the ethical concern"}

    Response:
      {
        "success": true,
        "theme_id": "...",
        "theme_label": "...",
        "image_url": "...",
        "reflection": "...",
        "matched_issue": "user text"
      }

    The mapping is deterministic and reproducible, matching issue keywords to
    curated AI-generated themes.  This satisfies the CHI 2027 expectation that
    each participant's own issue is reflected back as a concrete visual.
    """
    payload, error = _json_object()
    if error:
        return error

    issue = payload.get("issue", "").strip()
    if not issue:
        return jsonify({"success": False, "error": "'issue' text is required."}), 400

    if len(issue) > 2000:
        return jsonify({"success": False, "error": "Issue text is too long (max 2000 chars)."}), 400

    theme = classify_issue(issue)
    return jsonify({
        "success": True,
        "theme_id": theme["id"],
        "theme_label": theme["label"],
        "image_url": _image_url(theme["image"]),
        "reflection": theme["reflection"],
        "matched_issue": issue,
    })


@mirror_study_api.post("/analyze")
@rate_limit(max_requests=15, window_seconds=60, scope="mirror_study_analyze")
def analyze():
    """AI-analyse a researcher's free-text concern and return structured content.

    This mirrors the transition-companion architecture: the server proxies an LLM
    and returns structured JSON (reflection, theme, related concerns, ethical
    dimensions) that the front end renders. When no LLM key is configured it
    degrades gracefully to the deterministic classifier so the study still works.

    Body: {"issue": "free-text description of the ethical concern"}
    Response: {"success": true, "source": "ai"|"fallback", "theme_label", ...}
    """
    payload, error = _json_object()
    if error:
        return error

    issue = (payload.get("issue") or "").strip()
    if not issue:
        return jsonify({"success": False, "error": "'issue' text is required."}), 400
    if len(issue) > 2000:
        return jsonify({"success": False, "error": "Issue text is too long (max 2000 chars)."}), 400

    analysis, ai_error = _analyze_with_llm(issue)
    source = "ai" if analysis is not None else "fallback"
    if analysis is None:
        analysis = _fallback_analysis(issue)

    llm = _get_llm()
    return jsonify({
        "success": True,
        "source": source,
        "deepseek_configured": bool(os.getenv("DEEPSEEK_API_KEY")),
        "llm_configured": bool(llm and llm.is_configured()),
        "provider_count": len(llm.providers) if llm else 0,
        "ai_error": ai_error,
        **analysis,
    })


@mirror_study_api.post("/sessions")
@rate_limit(max_requests=20, window_seconds=60, scope="mirror_study_create")
def create_session():
    """Create a new study session and randomly assign a condition.

    Body (optional):
      {"condition_id": "c1_nothing_changes" | "c2_you_could_be_anyone"}
    If omitted, condition is assigned uniformly at random.
    """
    payload, error = _json_object()
    if error:
        return error

    condition_id = payload.get("condition_id")
    if condition_id and condition_id not in CONDITIONS:
        return jsonify(
            {"success": False, "error": f"Unknown condition_id: {condition_id}"}
        ), 400
    if condition_id is None:
        condition_id = random.choice(list(CONDITIONS.keys()))

    condition = _condition_with_urls(CONDITIONS[condition_id])
    issue_text = (payload.get("issue") or "").strip()
    req_theme = payload.get("theme_id")
    if issue_text:
        issue_theme = (
            next((t for t in ISSUE_GALLERY if t["id"] == req_theme), None)
            or classify_issue(issue_text)
        )
    else:
        issue_theme = None
    session_payload = {
        "condition_id": condition_id,
        "condition_label": condition["label"],
        "issue_text": issue_text,
        "issue_theme": issue_theme,
        # Three-stage flow provenance: the interview, the generated issue set,
        # the single issue the participant chose, and its projected trajectory.
        "chat_transcript": _clean_messages(payload.get("messages")),
        "generated_issues": payload.get("issues") if isinstance(payload.get("issues"), list) else [],
        "selected_issue": payload.get("selected_issue") if isinstance(payload.get("selected_issue"), dict) else None,
        "timeline": payload.get("timeline") if isinstance(payload.get("timeline"), dict) else None,
        "vignette": SHARED_VIGNETTE,
        "condition": condition,
        "fixes": _fixes_with_urls(),
        "responses": {},
        "timestamps": {"created": mirror_study_store._now()},
    }

    try:
        session_id = mirror_study_store.create(condition_id, session_payload)
    except Exception as exc:
        current_app.logger.exception("Could not create mirror-study session")
        return jsonify(
            {"success": False, "error": "Could not create session. Please retry."}
        ), 500

    return jsonify(
        {
            "success": True,
            "session_id": session_id,
            "condition_id": condition_id,
            "condition": condition,
            "vignette": SHARED_VIGNETTE,
            "fixes": session_payload["fixes"],
            "max_fixes": 3,
        }
    )


@mirror_study_api.get("/sessions/<session_id>")
def get_session(session_id: str):
    """Return the current state of a study session."""
    record = mirror_study_store.get(session_id)
    if record is None:
        return jsonify({"success": False, "error": "Session not found."}), 404
    return jsonify(
        {
            "success": True,
            "session_id": session_id,
            "status": record["status"],
            "condition_id": record["condition_id"],
            "data": record["payload"],
        }
    )


@mirror_study_api.post("/sessions/<session_id>/response")
@rate_limit(max_requests=40, window_seconds=120, scope="mirror_study_response")
def save_response(session_id: str):
    """Save participant responses for a session.

    Body:
      {
        "step": "frames" | "veil" | "fixes" | "demographics" | "final",
        "data": { ... }
      }
    The step field lets the front end save incrementally.
    """
    payload, error = _json_object()
    if error:
        return error

    step = payload.get("step")
    data = payload.get("data")
    if not step or not isinstance(data, dict):
        return jsonify(
            {"success": False, "error": "Both 'step' and 'data' are required."}
        ), 400

    record = mirror_study_store.get(session_id)
    if record is None:
        return jsonify({"success": False, "error": "Session not found."}), 404

    session_payload = record["payload"]
    session_payload["responses"][step] = data
    if "timestamps" not in session_payload:
        session_payload["timestamps"] = {}
    session_payload["timestamps"][step] = mirror_study_store._now()

    if step == "final":
        session_payload["timestamps"]["submitted"] = mirror_study_store._now()
        mirror_study_store.set_status(session_id, "completed")

    try:
        mirror_study_store.update_payload(session_id, session_payload)
    except Exception as exc:
        current_app.logger.exception("Could not save mirror-study response")
        return jsonify(
            {"success": False, "error": "Could not save response. Please retry."}
        ), 500

    return jsonify({"success": True, "session_id": session_id, "step": step})
