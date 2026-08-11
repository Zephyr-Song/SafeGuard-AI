"""End-to-end check of the step-5 conversational resolution guide on Render.

Mirrors what the front end does:
  * create session -> analyze (LLM) -> guide-resolution start -> reply x N -> finalize
  * finalize saves revisions server-side and returns the parsed resolutions
  * export-application returns a .docx

The back end's `reply` action ignores any `message` field and relies on the
client appending the user turn to `history`; we do the same here.
"""

import json
import urllib.request
import urllib.error

BASE = "https://safebars.onrender.com/api/safebars/mirror"


def post(path, body=None):
    """POST JSON; always return (status, dict). On error the dict has `_error`."""
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body_txt = e.read().decode()
        except Exception:  # noqa: BLE001
            body_txt = ""
        return e.code, {"_error": f"HTTP {e.code}", "_raw": body_txt[:300]}
    except Exception as e:  # noqa: BLE001
        return "ERR", {"_error": str(e)[:200]}


def sess_id(d):
    """Extract the session id whether `session` is a str or dict."""
    sess = (d or {}).get("session")
    if isinstance(sess, str):
        return sess
    if isinstance(sess, dict):
        return sess.get("id")
    return None


def main():
    # 1) create ---------------------------------------------------------------
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
    sid = sess_id(d)
    print("1) create:", st, "success=", d.get("success"), "id=", sid)
    if not sid:
        print("   CREATE FAILED ->", d)
        return

    # 2) analyze (LLM) --------------------------------------------------------
    st2, d2 = post(f"/sessions/{sid}/analyze", {"use_llm": True})
    s2 = d2.get("session") if isinstance(d2.get("session"), dict) else {}
    edges = s2.get("dissonance_edges", [])
    print(f"2) analyze: {st2} | tensions={len(edges)} | "
          f"ids={[e.get('id') for e in edges][:6]}")
    if d2.get("_error"):
        print("   ANALYZE ERROR ->", d2)
        return

    # 3) guide-resolution start ----------------------------------------------
    st3, d3 = post(f"/sessions/{sid}/guide-resolution", {"action": "start"})
    hist = d3.get("history") or []
    print(f"3) start: {st3} | llm_available={d3.get('llm_available')} | "
          f"opener_head={(d3.get('reply') or '')[:60]!r}")

    # 4) guide-resolution reply x N (append user turn to history first) -------
    for m in [
        "For the silent notification, I'll add an explicit opt-out toggle so students "
        "control whether counsellors are notified.",
        "For data retention, I'll shorten it to 30 days and let students delete their "
        "logs anytime.",
    ]:
        hist = hist + [{"role": "user", "content": m}]
        str_, dr = post(f"/sessions/{sid}/guide-resolution",
                        {"action": "reply", "history": hist})
        hist = dr.get("history", hist)
        print(f"4) reply: {str_} | llm_error={dr.get('llm_error')} | "
              f"reply_head={(dr.get('reply') or '')[:50]!r}")

    # 5) finalize -> saves revisions + returns parsed resolutions --------------
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
              f"{(r.get('rationale') or '')[:55]}")
    if df.get("_error"):
        print("   FINALIZE ERROR ->", df)

    # 6) export DOCX ----------------------------------------------------------
    req = urllib.request.Request(
        BASE + f"/sessions/{sid}/export-application",
        data=b"{}", headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            blob = r.read()
            is_docx = blob[:2] == b"PK"
            print(f"6) export DOCX: {r.status} | bytes={len(blob)} | is_docx={is_docx}")
    except Exception as e:  # noqa: BLE001
        print("6) export ERR:", e)


if __name__ == "__main__":
    main()
