# XJTLU Ethics Review Application — SafeBARS Ethical Mirror Study (Study 1)

> **Status:** Draft ready to paste into the XJTLU Research Ethics Review System.
> **Version:** v1.0 · 2026-08-13
> **Companion documents (attach all):** `study1_protocol.md`, `study1_participant_packet.docx` (consent + questionnaire + debrief), `osf_preregistration.md`, `pilot_runbook.md`, `analysis_plan.py`.
> **Pre-registration:** OSF (fork CHI 2027 template) — H1/H3/H4 confirmatory, RQ2/RQ-align exploratory. Freeze `analysis_plan.py` at the submission commit.
>
> ⚠️ **Placeholders in `[ ]` must be filled with real PI / student / supervisor names, XJTLU staff/student IDs, and the IRB approval number before submission.** Do not submit with brackets intact.

---

## 1. Project Information

| Field | Content |
|---|---|
| Project title | SafeBARS Ethical Mirror: How Multimodal (vs Text-only) Feedback Helps AI/HCI Researchers Discover Their Own Ethical Blind Spots |
| Research type | Student research project (undergraduate / master's thesis component) |
| Principal Investigator | [PI Full Name], [Title], [Department], Xi'an Jiaotong-Liverpool University — staff ID [ ] |
| Student researcher (lead) | [Student Full Name], [Student ID ], [Programme], XJTLU |
| Academic supervisor | [Supervisor Full Name], [Title], [Department], XJTLU |
| Proposed start date | [YYYY-MM-DD] (pilot) → [YYYY-MM-DD] (Prolific main study) |
| Proposed end date | [YYYY-MM-DD] (data analysis) / publication TBD |
| Funding | None external (student project; Prolific participant compensation from [source/budget]) |
| Expected participants | Pilot N = 5–8 (friends + XJTLU students, unpaired); Main N = 80–120 (Prolific, international, ≥18) |

---

## 2. Lay Summary (for non-specialists)

We are building and studying a web tool called an "ethical mirror." When a researcher describes an AI or HCI system they are designing, the tool reflects back the groups of people who might be affected — including vulnerable or overlooked groups — and shows where the design might cause harm. Unlike a checklist or a report that simply tells the researcher what is wrong, the mirror deliberately *withholds the verdict* and asks questions, so that the researcher arrives at the insight themselves.

This study tests whether showing ethical gaps through interactive visuals (maps, heatmaps, scenario trees) helps researchers notice their own blind spots and change their designs more than a plain text version of the same tool. Participants use the tool for ~10–15 minutes with a research plan, then answer a short questionnaire. The study is low-risk: participants reflect on their own design and type text; no sensitive measurements are taken. All data are stored anonymously/pseudonymously and reported only in aggregate.

---

## 3. Background & Rationale

Anticipating the unintended consequences of one's own research design is widely considered important by computer-science researchers, yet is rarely practiced for lack of a formal process or strategy (Do, Pang, Jiang & Reinecke, CHI 2023). Recent CHI work shows AI-mediated dialogue can shift bias recognition and that resisting a biased AI coach can strengthen moral boundaries (Taheri et al., CHI 2026), but that work is (a) text-only, (b) studies reflection on *others'* bias rather than the user's *own* design, and (c) treats self-reflection as incidental. SafeBARS targets exactly this gap: a multimodal mirror that externalizes the ethical structure of the user's *own* design and lets the user discover gaps themselves.

The study is pre-registered (OSF) to protect against p-hacking: primary hypotheses H1/H3/H4 are confirmatory; RQ2 (disclosure style) and RQ-align (critical vs sycophantic tone) are explicitly exploratory.

---

## 4. Research Questions & Hypotheses

| ID | Research question | Hypothesis (confirmatory in **bold**) |
|---|---|---|
| RQ1 | Does the multimodal mirror produce more *self-attributed* blind-spot discovery than text-only? | **H1:** multimodal > text on self-discovery rate |
| RQ2 (expl.) | Does "mirror only asks" (withhold) yield more self-attribution than "mirror states the issue" (prescribe)? | exploratory within-session contrast |
| RQ3 | Does scaffolded co-revision preserve ownership while producing high-quality revisions? | **H3:** multimodal ≥ text on agency/ownership; revisions rated specific + ethically grounded |
| RQ4 | Does the mirror produce real mindset change (not just a report)? | **H4:** multimodal shows greater post-revision evidence-coverage improvement |
| RQ-align (expl.) | Does critical (non-sycophantic) tone raise critical distance without harming trust? | exploratory 2×2 |

---

## 5. Methodology

### 5.1 Design
- **Between-subjects** on modality: `Multimodal` (default) vs `Text-only` (`?cond=text`).
- **Within-session** on disclosure style for RQ2: half of a participant's tensions rendered `withhold` (mirror only asks), half `prescribe` (mirror states the issue), via `?disc=split`.
- **Exploratory between** on tone for RQ-align: `?align=critical` (default) vs `?align=sycophantic`.
- Random assignment per Prolific quota; friends pilot assigned round-robin (see `pilot_runbook.md`).

### 5.2 Participants
- **Pilot:** 5–8 friends / XJTLU students, ~20 min each, think-aloud, for instrument validation only. **Excluded from confirmatory analysis.**
- **Main (Prolific):** target **N = 80–120** (40–60 per modality arm). Eligibility screener: "Have you designed or are you designing an AI or HCI system? (yes/no)" → exclude "no". Age ≥ 18.
- **Power:** pilot variance used to finalize N; aim 0.80 power at d ≥ 0.45 on self-discovery rate.

### 5.3 Procedure (per participant, ~20–30 min total)
1. **Consent** (electronic, see §8) — must be agreed before any data collected.
2. **Pre-task (~5 min):** list affected groups (open text); self-rate ethical robustness (7-pt); receive a shared research-plan stimulus (one of two provided scenarios to control variance).
3. **Intervention (~10–15 min):** use assigned mirror link; system logs self-discovery, revisions, condition, session duration.
4. **Post-task (~5 min):** re-list affected groups; free reflection; 7-pt Likert battery (self-discovery, mindset change, agency/ownership, critical distance, trust) + manipulation checks + open items.
5. **Debrief** (electronic) — explains purpose, manipulation, data handling, contact, withdrawal.

Full verbatim participant-facing text is in `study1_protocol.md` §C–§H and `study1_participant_packet.docx`.

### 5.4 Materials / Instruments
- Deployed web tool: `https://safebars.onrender.com/safebars/mirror` (+ `?cond=text`, `?disc=split`, `?align=`).
- Two shared research-plan stimuli (low-sensitivity "dorm fairness assistant"; high-sensitivity "CampusMind campus mental-health silent screener") to control stimulus variance.
- Post-questionnaire: 7-pt Likert scales (Self-Discovery SD1–4, Mindset-Change MC1–3, Agency AG1–4, Critical-Distance CD1–3, Trust TR1–3, Aha AH1–2) + manipulation checks (MK1–3) + open items (OP1–2). See `study1_protocol.md` §E.
- Behavioural coding scheme (2 coders, target κ/ICC ≥ .70): Δ affected-groups, safeguard-action count, revision-quality rubric (4 dims × 1–5), self-attribution coding (SELF/SYSTEM/NEUTRAL). See `study1_protocol.md` §F.

---

## 6. Recruitment & Inclusion / Exclusion

- **Source:** Prolific (main) + personal network / XJTLU students (pilot).
- **Inclusion:** age ≥ 18; have designed or are designing an AI/HCI system (screener).
- **Exclusion:** fail screener; session < 60 s on Step 4 or empty realization (invalid-attempt, logged, excluded per pre-registered rule).
- **No vulnerable-population targeting** (no children, no patients, no institutionalized persons). General adult population via Prolific.
- **Compensation:** Prolific standard rate for ~20–30 min; pilot friends compensated per XJTLU/local norms or volunteer. No coercion; participation voluntary.

---

## 7. Informed Consent Process

- **Mode:** electronic, presented *before* the study; participant must tick "I voluntarily participate and may withdraw at any time" to proceed.
- **Content (full text in `study1_participant_packet.docx` and `study1_protocol.md` §D):** purpose; what participants will do; data & privacy (recorded, anonymous/pseudonymous, aggregate-only reporting, no individual decisions); minimal risk; voluntary participation & withdrawal; contact; IRB approval number `[to be filled post-approval]`.
- **Capacity:** adults ≥ 18; no reduced-capacity groups.
- **Withdrawal:** participants may stop anytime; already-submitted data may be retained per IRB policy. Main-study participants may email [PI] within [window, e.g., 14 days] to request withdrawal of their session (identified by participant code shown at debrief).

---

## 8. Risks, Benefits & Safeguards

| | Assessment |
|---|---|
| **Risk level** | **Minimal.** Participants reflect on their *own* design; no physiological, psychological, or deception stress beyond ordinary self-reflection. No deception (debrief discloses manipulation openly). |
| **Potential discomfort** | Mild — confronting limitations in one's own design. Mitigated by neutral, non-judgmental tool language and debrief normalizing the exercise. |
| **Benefits** | Direct: participants may improve their design's ethics. Societal: advances tools for responsible AI design. No guaranteed personal benefit; no cost to participant. |
| **Safeguards** | No sensitive personal data collected beyond free-text design reflections; free-text screened for accidental PII and de-identified in coding; opt-out at any time; debrief with contact + support pointer. |

---

## 9. Data Management, Privacy & Retention

- **What is collected:** free-text design reflections, affected-group lists, self-discovery realizations, revisions, questionnaire Likert responses, session metadata (condition, duration). **No** names, emails, or contact data are linked to sessions.
- **Identifiers:** participants are assigned a **participant code** (pilot roster `F01…`; Prolific `P001…`). The Prolific worker ID is used only for payment and is **not** joined to research data except via the code.
- **Storage:** server database on Render (cloud PaaS; data-at-rest encrypted, access restricted to the research team). Local analysis copies are pseudonymized (code only).
- **Anonymization:** free-text is reviewed and de-identified before coding/release; direct quotes used in publication are paraphrased or stripped of identifying detail unless explicitly authorized.
- **Retention:** raw data retained per XJTLU policy (recommend [5 years] from publication, or until study closure). De-identified session JSON + analysis scripts + coding scheme released on **OSF upon acceptance** (open-science compliance).
- **International data:** Prolific participants may be outside China; data handling complies with XJTLU policy and applicable transfer principles (minimal collection, pseudonymization, no special-category data).
- **Security:** access controlled by team credentials; no third-party resale; research-only use.

---

## 10. Debrief & Dissemination

- Electronic debrief at study end (text in `study1_protocol.md` §H / packet): explains the multimodal-vs-text manipulation, the self-discovery mechanism, anonymous handling, contact for results/withdrawal.
- Results disseminated via CHI 2027 publication, OSF, and summary to participants on request.

---

## 11. Investigator Qualifications & Training

- Lead student researcher: trained in HCI research methods; completed XJTLU research-ethics training `[confirm module name/date]`; supervised by [Supervisor].
- Coding: 2 trained coders (including lead + [second coder]); pilot used to calibrate κ/ICC ≥ .70 before main coding.
- Tool operation: backend maintained by the research team; pilot runbook verifies end-to-end data capture before Prolific launch.

---

## 12. References

- Do, K., Pang, R. Y., Jiang, J., & Reinecke, K. (2023). "That's important, but…": How CS Researchers Anticipate Unintended Consequences of Their Research Innovations. *CHI '23*, Article 602.
- Taheri, A., El Alaoui, H., Carrington, P., & Bigham, J. P. (2026). "I followed what felt right, not what I was told": Autonomy, Coaching, and Recognizing Bias Through AI-Mediated Dialogue. *CHI '26*.
- Makridis, C. A., et al. (2023). Informing the ethical review of human subjects research utilizing AI. *Frontiers in Computer Science*, 5, 1235226.
- ACM (2021). *Publications Policy on Research Involving Humans.* https://www.acm.org/publications/policies/research-involving-humans
- XJTLU Research Ethics Review guidelines (internal).

---

## 13. Attachments Checklist (submit with this form)

- [ ] `study1_protocol.md` (full instrument & analysis plan)
- [ ] `study1_participant_packet.docx` (consent + questionnaire + debrief)
- [ ] `osf_preregistration.md` (pre-reg content)
- [ ] `pilot_runbook.md` (pilot procedure & acceptance criteria)
- [ ] `analysis_plan.py` (frozen DV extractor)
- [ ] Recruitment message / Prolific study listing text
- [ ] Two shared research-plan stimuli (R1 / R2)
- [ ] Data-management & retention statement (this §9)
- [ ] PI / supervisor signatures (per XJTLU submission step)

---

### Notes for the submitter
1. Replace every `[ ]` placeholder (names, IDs, dates, retention years, approval number).
2. Confirm the XJTLU ethics category (this is low-risk, likely "exempt" or "minimal-risk" fast-track — verify with the current XJTLU form).
3. The tool is **already deployed**; the IRB reviews the *study*, not the deployment. State the deployment URL and data-host explicitly (§5.4, §9).
4. Pre-register on OSF **before** the first Prolific participant is collected, and freeze `analysis_plan.py` at that commit.
