"""Focused end-to-end check of the STEP-5 conversational resolution guide.

Isolates the new step-5 feature from the heavy `use_llm=True` analyze (which can
exceed Render's free-tier request timeout and 502). We analyze WITHOUT the LLM
(fast, deterministic) so the session has tensions, then drive the new
guide-resolution endpoints + DOCX export.
"""

import json
import urllib.request
import urllib.error

BASE = "https://safebars.onrender.com/api/safebars/mirror"


def post(path, body=None, timeout=180):
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode()
        except Exception:  # noqa: BLE001
            raw = ""
        return e.code, {"_error": f"HTTP {e.code}", "_raw": raw[:300]}
    except Exception as e:  # noqa: BLE001
        return "ERR", {"_error": str(e)[:200]}


def sid_of(d):
    sess = (d or {}).get("session")
    if isinstance(sess, str):
        return sess
    if isinstance(sess, dict):
        return sess.get("id")
    return None


def main():
    st, d = post("/sessions", {
        "title": "Campus mental-health check-in app",
        "research_plan": (
            "A campus app that silently notifies counsellors when a student's mood "
            "entries suggest distress, without the student's explicit consent, and "
            "retains chat logs for 90 days."
        ),
        "value_commitments": [
            "Students control whether counsellors are notified about their wellbeing.",
        ],
    })
    sid = sid_of(d)
    print("1) create:", st, "id=", sid)
    if not sid:
        print("   FAILED", d)
        return

    # Fast, deterministic analyze (no heavy LLM literature matching).
    st2, d2 = post(f"/sessions/{sid}/analyze", {"use_llm": False})
    s2 = d2.get("session") if isinstance(d2.get("session"), dict) else {}
    edges = s2.get("dissonance_edges", [])
    print(f"2) analyze(no-llm): {st2} | tensions={len(edges)} | "
          f"ids={[e.get('id') for e in edges]}")
    if d2.get("_error"):
        print("   ANALYZE ERROR", d2)
        return

    st3, d3 = post(f"/sessions/{sid}/guide-resolution", {"action": "start"})
    hist = d3.get("history") or []
    print(f"3) start: {st3} | llm_available={d3.get('llm_available')} | "
          f"opener_head={(d3.get('reply') or '')[:55]!r}")

    for m in [
        "I'll add an explicit opt-out toggle for the silent notification so students "
        "stay in control of whether counsellors are alerted.",
        "I'll cut data retention to 30 days and let students delete their logs anytime.",
    ]:
        hist = hist + [{"role": "user", "content": m}]
        str_, dr = post(f"/sessions/{sid}/guide-resolution",
                        {"action": "reply", "history": hist})
        hist = dr.get("history", hist)
        print(f"4) reply: {str_} | llm_error={dr.get('llm_error')} | "
              f"reply_head={(dr.get('reply') or '')[:45]!r}")

    stf, df = post(f"/sessions/{sid}/guide-resolution",
                   {"action": "finalize", "history": hist})
    parsed = df.get("parsed") or {}
    sf = df.get("session") if isinstance(df.get("session"), dict) else {}
    revs = sf.get("revisions") or []
    print(f"5) finalize: {stf} | llm_error={df.get('llm_error')} | "
          f"resolutions={len(parsed.get('resolutions') or [])} | "
          f"saved_revisions={len(revs)}")
    for r in (parsed.get("resolutions") or []):
        print(f"     - {r.get('edge_id')} [{r.get('resolution_type')}] "
              f"{(r.get('rationale') or '')[:50]}")
    if df.get("_error"):
        print("   FINALIZE ERROR", df)

    req = urllib.request.Request(
        BASE + f"/sessions/{sid}/export-application",
        data=b"{}", headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            blob = r.read()
            print(f"6) export DOCX: {r.status} | bytes={len(blob)} | "
                  f"is_docx={blob[:2] == b'PK'}")
    except Exception as e:  # noqa: BLE001
        print("6) export ERR:", e)


if __name__ == "__main__":
    main()
