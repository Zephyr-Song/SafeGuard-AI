# SafeBARS — Research Plan & User-Study Design (CHI 2027)

> **Superseded planning draft.** Keep this file as a record of the earlier
> ESR-centred direction, but do not treat its formative statements, expected
> results, sample size, or “committee-ready” wording as established evidence.
> The controlling, literature-checked plan is
> `83_supervisor_feedback_ai_ethics_and_study_plan.md`.

> Working research plan. Goal: take SafeBARS from a working prototype to a
> CHI 2027 submission with a clear contribution, research questions, and a
> defensible user study. Structure follows the canonical HCI arc:
> **Formative Study → Design Goals → Artifact → Research Questions →
> User Study → Analysis → Results & Conclusions.**

## 1. Problem & Contribution

Institutional Review Boards (IRBs) under the Common Rule focus on risks to
*individual participants*. They are expressly barred from reviewing
*long-range societal consequences*. Yet AI-enabled and data-intensive research
increasingly creates risks to subgroups and to society that no one reviews.
Researchers also lack tooling that turns a rough protocol into a
committee-ready ethics application.

**Contribution.** SafeBARS is an interactive workspace that:

- **(C1) Makes the ethics pathway explicit and auditable** — a framework
  selector routes each protocol to the right backbone (Belmont for
  human-subjects, Menlo for ICT, NIST AI RMF for AI, plus Value Sensitive
  Design and the Ethics and Society Review), instead of a one-size form.
- **(C2) Surfaces societal/community risks beyond the IRB** — the exported
  ethics-application draft includes an *Ethics and Society Review (ESR)*
  societal-risk statement with mitigation prompts, so researchers state risks
  to society, subgroups, and globally (Bernstein et al., PNAS 2021).
- **(C3) Keeps a transparent, revisable audit trail** — encounter map,
  breakdown traces, researcher decisions, and unresolved questions are all
  inspectable and editable.
- **(C4) Hands irreducibly subjective questions to humans** — when a question
  needs judgment, SafeBARS creates a handoff to a human reviewer and never
  fabricates an approval.

## 2. Related Work

- **Ethics and Society Review (ESR)** — Bernstein, Levi, Magnus, Rajala,
  Satz & Waeiss (2021), *PNAS* 118(52):e2117261118. Requires researchers to
  author a statement of risks to society/subgroups/globally + mitigations,
  with an interdisciplinary panel iterating. The conceptual backbone of C2.
- **Farsight** — Wang, Kulkarni, Wilcox, Terry & Madaio (CHI 2024). An
  in-situ tool that helps people identify potential harms while prototyping
  AI applications; validated with a co-design study (10) + user study (42).
  *Closest analog*: SafeBARS is the research-ethics-protocol counterpart,
  and its export is a committee application rather than a harm brainstorm.
- **PASTA** — Yang, Kim & Yoon (CHI 2026). Multi-policy AI compliance
  evaluation with interpretable heatmaps; expert + practitioner (N=12)
  evaluation. Relevant for the "interpretable, actionable output" design goal.
- **Participatory auditing of predictive AI** — CHI 2026. Co-design workshops
  showing non-experts can surface impacts beyond current taxonomies.
  Supports C3/C4 (stakeholder voice + human review).
- **Framework backbone already in the app** — Belmont Report (1979),
  Menlo Report (2012), NIST AI RMF (AI 100-1), Value Sensitive Design.

## 3. Formative Study (hypotheses to validate)

The following are design hypotheses, not completed formative findings:

- Researchers may miss **societal/community risks** when drafting alone and
  may default to individual-consent language.
- The six-question guided intake + conditional AI-governance follow-up
  is intended to reduce burden while retaining application-relevant material;
  this must be checked against real institutional workflows.
- A complete draft to react to may be more useful than a blank form, but this
  remains an empirical question.

For CHI, formalize this with a short interview study (n≈8–12 researchers)
coding *what people struggle to anticipate* in ethics review, to motivate
DG1–DG4 below.

## 4. Design Goals

- **DG1 — Explicit, auditable pathway.** The framework selector shows
  *why* a protocol is routed to Belmont/Menlo/NIST/VSD/ESR, with confidence
  and recommended reviewer roles.
- **DG2 — Societal-risk surfacing.** The export forces an ESR-style
  statement of societal/community risk + mitigations, not just participant
  risk.
- **DG3 — Transparent, revisable trail.** Every issue, decision, and
  handoff is inspectable and editable; the dandelion visualizes trade-offs
  and their framework linkages.
- **DG4 — Honest boundaries.** No fabricated approval; irreducible
  questions become human handoffs.

## 5. The Artifact

SafeBARS: Flask-based, agentic workflow with an optional bounded LLM critic.
The v1 "rehearsal" and v2 "encounter
workspace" (four stages: collect → map → trace → decide/hand off). Exports
a generic **ethics-application DOCX** to transfer into an institution's current
form; it now embeds the ESR
societal-risk statement and references.

## 6. Research Questions

- **RQ1 (Effectiveness).** Does SafeBARS-assisted drafting help researchers
  surface *more distinct ethical issues* — especially societal/community
  risks — than unaided writing?
- **RQ2 (Quality).** Are SafeBARS-generated applications rated higher on
  *completeness* and on *ESR societal-risk coverage* by a blinded expert
  panel, versus unaided drafts?
- **RQ3 (Perception & influence).** Do researchers find it useful and usable
  (SUS, USE), and does it change their design thinking — cf. ESR's finding
  that 58% felt the review influenced their project design?
- **RQ4 (Ablation, optional).** Does the explicit ESR societal-risk section
  increase societal-risk coverage versus a version of the export without it?

## 7. User Study

- **Participants.** ~36–42 researchers / HCI graduate students who have (or
  will) design a human-facing or AI-enabled study.
- **Design.** Between-subjects (SafeBARS vs. unaided committee template), or
  within-subjects counterbalanced to control for scenario familiarity.
  Task: produce an ethics-committee application for a provided scenario
  (one human-subjects, one AI-enabled).
- **Measures.**
  1. *Issue quality* — consequential, non-duplicative issues identified and
     revised, tagged by type (individual vs. societal/community). Raw issue
     count is not an ethics-quality outcome.
  2. *Expert-rated quality* — blinded panel scores completeness, ESR
     societal-risk coverage, and Belmont coverage on a rubric.
  3. *Perception* — SUS, USE questionnaire, and a short interview.
- **Analysis.** Mixed-effects models on counts/scores (RQ1–RQ3); reflexive
  thematic analysis of interviews (mirroring the CHI'25 AI-bias study's
  coding pipeline) for the "influence on design" question. Pre-register the
  rubric and hypotheses.
- **No results in advance.** Report paired distributions, uncertainty, expert
  ratings, and qualitative findings whether or not they favour SafeBARS.

## 8. Expected Contributions & Limitations

Contribution: a deployable tool **plus** evidence that structured,
framework-driven drafting improves ethics readiness and surfaces
societal risks IRBs omit. Limitations: scenario-based (not field) tasks,
student sample, single institution — note as threats to ecological validity.

## 9. References

- Bernstein, M. S., Levi, M., Magnus, D., Rajala, B. A., Satz, D., & Waeiss,
  C. (2021). Ethics and society review: Ethics reflection as a precondition
  to research funding. *PNAS*, 118(52), e2117261118.
- Wang, Z. J., Kulkarni, C., Wilcox, L., Terry, M., & Madaio, M. (2024).
  Farsight: Fostering Responsible AI Awareness During AI Application
  Prototyping. *CHI 2024*.
- Yang, Y., Kim, I.-J., & Yoon, D. (2026). PASTA: A Scalable Framework for
  Multi-Policy AI Compliance Evaluation. *CHI 2026*.
- U.S. National Commission (1979). *The Belmont Report*.
- Menlo Report (2012); NIST AI RMF (AI 100-1); Friedman, Kahn & Borning
  (Value Sensitive Design).
