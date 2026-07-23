# Briefing for Erick — Anchor Paper for AI-Era Ethics Approval

> **Positioning update:** ESR is a valuable process precedent for societal-risk
> reflection and interdisciplinary iteration, but it is not a university
> ethics-approval standard or the sole AI-era anchor. SafeBARS now also uses
> Makridis et al. (2023), DOI 10.3389/fcomp.2023.1235226, for AI-specific
> human-subjects review questions and Connelly et al. (2025), DOI
> 10.5281/zenodo.13739834, for university REC guidance. See
> `83_supervisor_feedback_ai_ethics_and_study_plan.md`.

> Purpose: this paper provides a complementary societal-risk and expert-review
> process lens for SafeBARS. Forward it with the AI-specific review sources and
> ask Erick which parts fit the institution's actual requirements.

## The paper

**Bernstein, M. S., Levi, M., Magnus, D., Rajala, B. A., Satz, D., & Waeiss, C. (2021).**
*Ethics and society review: Ethics reflection as a precondition to research funding.*
**Proceedings of the National Academy of Sciences (PNAS), 118(52), e2117261118.**
DOI: **10.1073/pnas.2117261118**
Link: https://doi.org/10.1073/pnas.2117261118

## Why this paper

The core problem with ethics approval in the AI era is that a standard IRB
under the U.S. Common Rule is **expressly barred from reviewing long-range
societal consequences** — it only looks at risks to individual participants.
AI- and data-intensive research increasingly creates risks to *subgroups* and
to *society* that fall through that gap. This paper proposes the **Ethics and
Society Review (ESR)**: before funding, researchers must author a statement of
the risks their work creates for **society, for subgroups within society, and
globally**, plus the **mitigation strategies** they commit to. An
interdisciplinary panel then iterates on that statement with the researchers.

It is a useful process anchor because it identifies a gap that SafeBARS can
help researchers discuss: turning a rough protocol into a reviewable statement
of societal risk and mitigations, without pretending to *grant* approval.

## What the paper argues (short version)

1. Individual-subject review (IRB/Common Rule) is necessary but **not
   sufficient** for research with societal spillover.
2. Researchers should **pre-state** risks to society/subgroups/globally and
   the mitigations they will use — i.e. reflection *before* the work, as a
   funding precondition.
3. An interdisciplinary panel should review that statement and iterate with
   the researchers; this is a different job from consent-form review.
4. The output is a **document** (the ESR statement), not a verdict — the
   researcher remains accountable for it.

## How SafeBARS follows this framework

| ESR requirement | Where SafeBARS implements it |
| --- | --- |
| Identify risks to society / subgroups / globally | Framework selector routes AI/ICT protocols to **Menlo**, **NIST AI RMF**, **VSD**, and **ESR** dimensions (beyond Belmont's individual focus) |
| Researcher states the risks | The exported ethics-application draft now contains a **"Societal & Community Risk Statement (Ethics and Society Review)"** section that surfaces those dimensions with their coverage evidence and leaves a *"Mitigation statement (researcher to complete)"* blank per dimension |
| Commit to mitigations | The blank mitigation lines are explicitly the researcher's to fill and carry into the university committee application |
| Reflection as precondition, not a verdict | The app never issues approval; it produces a draft + a "Submission readiness" statement and hands irreducibly subjective questions to a human reviewer (handoff) |
| References | The export appends a **References** block citing Bernstein 2021, Belmont, Menlo, NIST AI RMF, and VSD |

## Suggested asks for Erick

- Which combination of ESR, Makridis et al. (2023), Connelly et al. (2025),
  and the institution's own policy is appropriate for the study?
- Does your institution's ethics committee already request a societal-impact
  statement we should mirror more closely in the export template?
- Any additional steps from the paper (e.g. the interdisciplinary-panel
  iteration loop) we should represent as a SafeBARS stage?

## Status in repo

- App change landed in `modules/encounter_report.py`
  (`_add_esr_societal_risk_section` + References in
  `build_ethics_application_docx`).
- Research plan citing this paper: `research/chi2027/83_research_plan_and_user_study.md`.
