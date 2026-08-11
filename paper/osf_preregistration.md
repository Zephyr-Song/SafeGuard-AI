# OSF Pre-registration — SafeBARS Ethical Mirror, Study 1

> Upload this file to OSF (create pre-registration, fork the template, paste sections).
> Freeze the analysis script `paper/analysis_plan.py` at the same commit. Pre-register
> H1/H3/H4 + primary DVs as confirmatory; RQ2 (disc split) and RQ-align as exploratory.

---

## 1. Study information

- **Title:** Multimodal self-discovery vs. AI-prescription in an ethical-mirror tool for AI/LM system designers.
- **Design:** Between-subjects on modality (`?cond=text` vs multimodal); within-session on disclosure style (RQ2, `?disc=split`); exploratory between on tone (RQ-align, `?align=`).
- **Participants:** N target = 120 (Prolific, ~30/arm across the 2×2 of cond × align after collapsing disc to within). Friend pilot N=5–8 (8/12–8/25) for instrument validation only — excluded from confirmatory analysis.
- **Power:** pilot variance used to set final N; aim 0.80 at d ≥ 0.45 on self-discovery rate.

## 2. Hypotheses (confirmatory)

- **H1 (RQ1):** Multimodal arm yields a higher *self-discovery rate* (SELF / (SELF+SYSTEM+NEUTRAL) from `self_discovery.realizations`) than the text-only arm. *Predicted direction: multimodal > text.*
- **H3 (RQ3):** Multimodal arm reports higher *agency / ownership* (post-questionnaire Likert, 7-pt) over the final revision than text-only. *Predicted: multimodal > text.*
- **H4 (RQ4):** Multimodal arm shows greater post-revision *evidence-coverage improvement* (`replay_history.summary.changed_lens_count` + `resolved_edges`) than text-only. *Predicted: multimodal > text.*

## 3. Exploratory (not pre-registered as confirmatory)

- **RQ2:** Within a session, tensions disclosed via *withhold* (mirror only asks) produce more SELF-attributed realizations than *prescribe* (mirror states the issue). Report as within-subjects contrast; treat as hypothesis-generating.
- **RQ-align:** `?align=sycophantic` raises trust/rapport Likert but lowers critical-distance vs `?align=critical`. Exploratory 2×2.

## 4. Primary dependent variables

1. `self_discovery_rate` — from session `self_discovery.realizations`, classified SELF/SYSTEM/NEUTRAL by `analysis_plan.py::classify_realization` (lexical) AND by 2 human coders on the free-text (gold standard, target IRR κ ≥ .70).
2. `agency_ownership` — post-questionnaire item avg (7-pt).
3. `coverage_improvement` — `changed_lens_count` + `resolved_edges` after revision.
4. `n_distinct_affected_parties` realized — breadth of blind spots caught.

## 5. Analysis plan

- Primary: ANCOVA on `self_discovery_rate` with `cond` as factor, baseline ethical-familiarity (pre-survey) as covariate; contrast multimodal vs text (H1). Same family for H3/H4.
- RQ2: within-subjects McNemar / paired t on SELF rate by `disc` style.
- RQ-align: 2×2 ANOVA on trust × critical-distance.
- Alpha = .05; report effect sizes (Cohen's d / η²) and 95% CIs. No within-cell peeking before pre-registered N reached.
- Exclusions: sessions with < 60 s on Step 4 or empty `realized` dropped as invalid-attempt (logged).

## 6. Materials (frozen at this commit)

- `paper/study1_protocol.md` — full instrument.
- `paper/study1_participant_packet.docx` — consent + questionnaire + debrief.
- `paper/pilot_runbook.md` — pilot procedure.
- `paper/analysis_plan.py` — DV extractor (frozen).
- Deployed tool: `https://safebars.onrender.com/safebars/mirror` (+ `?cond=text`, `?disc=split`, `?align=`).

## 7. Data sharing

Session JSON (anonymized by participant code) + questionnaire roster released on OSF upon acceptance. Raw think-aloud transcripts stored separately with consent.
