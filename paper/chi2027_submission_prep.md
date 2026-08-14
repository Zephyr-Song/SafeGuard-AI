# CHI 2027 — Paper Submission Preparation Pack

> **Source of truth:** official CHI 2027 author pages (chi2027.acm.org/authors/papers), retrieved 2026-08-13.
> **Companion:** `safebars_chi2027_draft.tex` (full draft), `irb_application.md`, `osf_preregistration.md`, `引用文献.md`.
> ⚠️ Verify any date against the live PCS page before acting — CHI occasionally shifts by a day.

---

## 0. 🔴 Timeline reality check (read first)

| Milestone | Date (AoE) | Status vs today (2026-08-13) |
|---|---|---|
| Submission site open | 2026-08-13 | **today** |
| **Paper submission deadline** | **2026-09-10** | **~28 days** |
| Reviews released | 2026-11-05 | — |
| Revise-and-resubmit window | 2026-11-05 → 12-03 | — |
| Final notification | 2026-12-17 | — |
| E-Rights completion | 2027-01-07 | — |
| TAPS upload | 2027-01-14 | — |
| Publication-ready | 2027-02-18 | — |
| Conference | 2027-05 (Pittsburgh) | — |

**Hard risk flagged:** your Study 1 plan is pilot 8/26 (runbook says 8/12–8/25) + Prolific 9/2. To meet **2026-09-10** you would need Prolific collection (≈9/2–9/9) **plus** 2-coder coding (κ≥.70) **plus** analysis **plus** a written Results section — inside ~8 days. For N=80–120 that is realistically infeasible at quality. Two honest options:

- **(A) Aim for 9/10 with a leaner Study 1** — report the friend pilot (n=5–8) as an exploratory "formative evaluation" + keep the full Prolific as *registered future work*; OR run a smaller Prolific slice (e.g., n≈30–40) and label results preliminary. The simulation (Study 2) already carries the paper; Study 1 becomes supportive.
- **(B) Prepare everything to submission-grade now, submit to a later cycle / next venue** — same assets, no deadline panic.

This is your call. Everything below is built so **either path is one click + data-entry away**.

---

## 1. Track & review model

- **Track:** **Papers** (archival, competitive, refereed). Not Panels/Posters/Workshops.
- **Review model:** **NOT anonymous.** CHI 2027 Papers explicitly require *all author names, affiliations, and contact information* in the submission. → The draft's `anonymous` mode must be removed (see §4).
- **Revise-and-resubmit:** papers above a threshold get a revision round — plan buffer for the Nov–Dec window if you submit 9/10.

---

## 2. Formatting & length

- **Template:** ACM Master Article Submission Templates, **single column**. In `acmart`, use `\documentclass[manuscript,screen]{acmart}` (drop `anonymous`).
- **Length:** **5,000–8,000 words encouraged**; **>12,000 words desk-rejected** unless justified; **<5,000 = short paper**. Current draft (Study 1 pending) is under-length — the Results section + discussion expansion will fill it. Target final **~9,000–10,000 words incl. references**.
- **No abstract deadline** — single hard deadline on 9/10 (incl. video + supplements).
- **References:** author-year (`acmauthoryear`); our `引用文献.md` already enforces ≥2023 / zero self-cite / zero fiction.

---

## 3. Required submission components (PCS checklist)

| Component | Status | Note |
|---|---|---|
| Title | ✅ in draft | keep ≤ CHI limit |
| Abstract | ✅ in draft | 1 paragraph, ~150–200 words |
| Author block (names/affils/contact) | ⚠️ placeholders | fill real names; remove `Anonymous Author(s)` |
| CCS concepts | ✅ in draft | keep |
| Keywords | ✅ in draft | keep |
| PDF (single-column acmart) | ⏳ compile locally/Overleaf | no LaTeX on this sandbox |
| ACM eRights form | ⏳ at submission | corresponding-author institutional email decides APC |
| Human-subjects note to reviewers | ⚠️ to add | see §5 |
| Supplementary materials | ⏳ | OSF link + analysis scripts + (post-acceptance) de-identified data |
| Video preview (optional) | ⏳ optional | system demo clip strengthens |
| Accessible submission | ⚠️ verify | follow SIGCHI Guide to Accessible Submission |

---

## 4. Concrete edits to `safebars_chi2027_draft.tex`

1. **Remove anonymous mode:**
   - `\documentclass[manuscript,screen,anonymous]{acmart}` → `\documentclass[manuscript,screen]{acmart}`
2. **Replace author block** (currently `Anonymous Author(s)`):
   ```latex
   \author{[Your Name]}
   \affiliation{\institution{Xi'an Jiaotong-Liverpool University}}
   \email{[you@xjtlu.edu.cn]}
   % repeat \author/\affiliation for co-authors; add \orcid links if available
   ```
   XJTLU students are typically dual-award with **University of Liverpool** — list both affiliations per ACM policy if applicable.
3. **Add the human-subjects note** (CHI requires a short reviewer note on ethics context). Insert right after Abstract or as a footnote:
   > *This paper reports a computational simulation (Study 2) and a human-subject study (Study 1). Study 1 was approved by [XJTLU IRB], approval #[#]; participants gave informed consent; data are pseudonymized and released on OSF upon acceptance.*
4. **Study 1 Results** — replace the 3-line placeholder (lines 453–456) with the structured fill-in template (see `study1_stats.py` output + draft template in §108).

---

## 5. Human-participants policy note (CHI 2027)

> "Any research … involving human subjects must comply with the ethics review requirements applicable to the authors' research environment. … authors are asked to submit a short note to reviewers that provides this context."

→ We supply: IRB approval number, consent process, anonymization, and the OSF pre-registration link. Pre-registration is a *strength* for reviewer confidence.

---

## 6. Budget / APC (ACM Open)

- All CHI 2027 papers are **ACM Open** (100% OA from 2026-01-01).
- **APC:** **$500** (ACM/SIG member) or **$750** (non-member). The corresponding author's *institutional email* in the eRights form determines whether an APC applies (XJTLU may be an ACM Open institution — verify on the ACM Open list; if so, likely **$0**).
- Waiver: financial-hardship waiver exists but is rare — apply only if truly needed.

---

## 7. Pre-submission checklist (run before 9/10)

- [ ] IRB approved (approval # obtained) — see `irb_application.md`
- [ ] OSF pre-registration live, `analysis_plan.py` frozen at that commit
- [ ] Pilot completed; instruments calibrated; coding κ/ICC ≥ .70 rehearsed
- [ ] Prolific main study collected **or** leaner Study 1 decision made (§0)
- [ ] `study1_stats.py` run on real data → Results tables pasted into draft
- [ ] Author block filled; `anonymous` removed; human-subjects note added
- [ ] Compile in Overleaf/TexLive (acmart single-column); check < 12,000 words
- [ ] Accessibility pass (SIGCHI Guide); figures are vector PDF + 300 DPI PNG
- [ ] References re-verified (≥2023, zero self-cite, zero fiction) — `引用文献.md` is the source of truth
- [ ] Supplementary materials zipped (scripts, stimuli, consent, debrief, OSF link)
- [ ] Video preview recorded (optional but recommended)
- [ ] eRights + APC path confirmed; corresponding-author email set
- [ ] Submit in PCS before **2026-09-10 23:59 AoE** (24h grace, no support)

---

## 8. PCS entry notes

- **Submission system:** PCS (not the `2268` AC Volunteering form — that is unrelated).
- **No abstract-only deadline** — you submit the full PDF + supplements on 9/10.
- **Metadata integrity:** author names are locked at the 9/10 deadline; changes only during Publication-Ready phase. List all authors correctly the first time.
- **Track selection:** "Papers." Do not pick Posters (different, non-archival, anonymous) by mistake.
