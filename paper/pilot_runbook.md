# Study 1 — Friend Pilot Runbook (8/12–8/25)

> Goal of the pilot: **prove the full loop works end-to-end before spending Prolific money** — and
> confirm the core mechanism ("user realizes the blind spot themselves") actually triggers, not just
> that the buttons click. 5–8 friends, unpaired, ~20 min each, think-aloud.

---

## 0. What "跑通" means (acceptance criteria)

All of the following must hold for the pilot to count as 跑通:

1. Friend can open the link → produce a plan → reach Step 4 (three views + self-discovery) with **zero console errors**.
2. The **self-discovery card appears**, the "No — this is new to me" → reveal → realize-textarea → **Save** flow works.
3. The **realize→fix bridge** in Step 5 shows the exact text they typed in Step 4.
4. After Save, `self_discovery` is **actually in the server DB** (verify via §5 command, not just localStorage).
5. At least **2 of N** friends verbally produce a self-attributed "I never thought of X" moment (think-aloud).
6. The **text-only arm** (`?cond=text`) shows no multimodal panel; the **split arm** shows both "Mirror only asks" and "Mirror states the issue" badges.

If any criterion fails, fix and re-run that arm before Prolific.

---

## 1. Arms to pilot (assign friends round-robin)

| Arm | URL suffix | Manipulation | What to watch |
|-----|-----------|--------------|---------------|
| A. Multimodal (baseline) | *(no suffix)* | `?cond=multimodal` implicit, `disc=withhold`, `align=critical` | Does the red node trigger an "aha"? |
| B. Text-only (control) | `?cond=text` | no views, no self-discovery card | Do they still notice blind spots? (they shouldn't as easily) |
| C. Disc split (RQ2) | `?disc=split` | half tensions prescribe, half withhold | Do they attribute the withhold ones to themselves more? |
| D. Sycophantic (RQ-align) | `?align=sycophantic` | affirming tone | Do they trust more but scrutinize less? |

Assign so each friend does **one** arm (between-subjects). Keep a roster (§4).

Base URL (use Render, same-origin, no CORS blocks):
`https://safebars.onrender.com/safebars/mirror` + suffix.

> Cold start: Render sleeps after 15 min idle (~35 s to wake). Send the friend the link **after** you've
> hit it once yourself, or tell them "wait up to a minute on first load."

---

## 2. Recruitment message (send to each friend)

> Hey — I'm piloting a research-tool study for my CHI paper. It's ~20 min, you design a (fictional or real)
> AI/system plan and the tool mirrors back ethical blind spots. I'll sit with you (or you screen-share) and
> you just **think out loud** the whole time — say what you're noticing, what surprises you, what you'd change.
> No right answers. Could you do it [date/time]? I'll send a link.

Keep it light. Remind them: **thinking aloud is the data**, not the final plan.

---

## 3. Think-aloud guide (moderator prompts — do NOT lead)

Open with: "There are no right answers. Just say whatever you're thinking as you go."

During Step 4, if they go quiet: "What's going through your mind looking at this red node?"
If they say "the tool told me X": gently probe — "Did you already suspect that, or is that new to you?"
After Step 5: "You changed your plan — what made you decide to change it? Was it something you realized, or something the tool said?"

**Do NOT** say "this is a blind spot" or "you should fix X". The whole point is whether *they* arrive there.

---

## 4. Pilot roster (fill one row per friend)

| # | Code | Arm | Date | Minutes | "Aha" observed? (Y/N) | Console errors? | Notes |
|---|------|-----|------|---------|----------------------|----------------|-------|
| 1 | F01 | A | | | | | |
| 2 | F02 | B | | | | | |
| 3 | F03 | C | | | | | |
| 4 | F04 | D | | | | | |
| 5 | F05 | A | | | | | |
| 6 | F06 | C | | | | | |

Code maps to the session so you can join roster ↔ server data later.

---

## 5. Server-side data self-check (run after each friend saves)

The `self_discovery` object is posted through `add_revision` and stored on `session["self_discovery"]`.
Verify it landed (replace `SESSION_ID` with the friend's session id from the URL `?session=`):

```bash
curl -s -m 30 -A "Mozilla/5.0" \
  "https://safebars.onrender.com/api/safebars/mirror/sessions/SESSION_ID" \
  | python -m json.tool | grep -A 20 '"self_discovery"'
```

Expected (multimodal arm): a JSON block with `realized`, `anticipated`, `party`, `realizations`,
and `condition: { cond, disc, align }`. If `self_discovery` is `null`, the Save didn't reach the
server — check the friend's network / that they clicked Save, and re-test locally.

---

## 6. Debrief (say at the end)

"Thanks — that was the real data: we're studying whether *showing* ethical gaps (vs being told)
helps people catch their own blind spots. You won't see a score; your session is anonymized by code."

---

## 7. Pilot exit decisions (8/25)

- **If ≥2/arm show genuine self-attributed aha** → design validated; lock instruments, go Prolific.
- **If friends mostly say "the tool told me"** → the withhold phrasing is leaking prescription; tighten
  `withholdQ` in `mirror_multimodal.js` (remove any implicit naming) and re-pilot arm A/C.
- **If any console error / Save-not-landing** → fix code, re-deploy, re-run that arm.
- **If questionnaire confusing** → revise `study1_participant_packet.docx` items (pilot is the item-pretest).

Record decisions in `experiment_plan.md §5`.
