# SafeBARS Current Canonical Research Plan

Last updated: 2026-07-27

Use this file to answer "what is the current SafeBARS research?" Older files
remain an audit trail and must not be combined into a new study design.

## One-sentence research problem

SafeBARS investigates whether an inspectable, framework-grounded,
provenance-preserving workflow with explicit expert handoffs supports better
preparation of sensitive research protocols than a general chat interface
using the same LLM.

It does not investigate whether AI can grant ethics approval, replace an ethics
committee, simulate vulnerable participants, or guarantee that a study is
ethical.

## Exactly three research questions

### RQ1: Protocol-preparation quality

Compared with same-model general-purpose LLM chat, how does SafeBARS affect the
quality of revised research plans and ethics-application drafts for matched
sensitive human-facing protocol tasks?

Primary outcome: blinded expert-rated Preparation Quality Index, defined before
data collection as the mean of:

1. information completeness;
2. safeguard specificity;
3. actionability; and
4. evidence grounding and traceability.

### RQ2: Contestation and calibrated use

How do passage provenance, scenario traces, explicit boundaries, and revision
controls shape how protocol preparers inspect, accept, edit, reject, defer, and
rely on AI-generated critiques compared with general chat?

Primary process outcome: the within-participant condition difference in the
proportion of the two required consequential decision records that identify or
quote an exact source passage and explain the participant's decision.

### RQ3: Expert handoff work

Compared with unresolved-question packets prepared after general chat, how do
SafeBARS expert summaries and epistemic handoffs affect reviewer triage effort,
clarification needs, routing and evidence quality, and subsequent researcher
revision?

Primary expert-work outcome: blinded expert time from opening a standardized
packet to the first recorded review decision. Triage time may be interpreted as
an improvement only when issue coverage and advice quality do not deteriorate.

## Final study decision

- Primary blueprint: EvalLM, CHI 2024,
  https://doi.org/10.1145/3613904.3642216.
- Formative requirements check: 6 people, after written ethics approval or
  exemption and before final feature/material freeze.
- Main comparison: within-subject, counterbalanced SafeBARS versus same-model
  general LLM chat.
- Protocol preparers: target 24 completed paired sessions across eight frozen
  counterbalancing sequences, three participants per sequence.
- Expert panel: target 6 qualified reviewers; every artifact receives two
  independent blinded ratings.
- Cases: four fictional matched protocols, two non-AI and two AI-enabled.
- Stopping: 24 completed paired sessions or the preregistered calendar stop
  date; never stop based on which condition looks better.
- Interpretation: if fewer than 16 paired sessions are available, frame the
  evaluation as feasibility-oriented and do not make a confirmatory
  effectiveness claim.

## Canonical files

Read these in order:

1. `86_evalLM_blueprint_final_rqs.md` — primary paper blueprint, contribution,
   constructs, estimands, and justified deviations;
2. `87_46_day_chi_execution_plan.md` — dates, ethics gates, owners, go/no-go,
   writing, and submission buffer;
3. `88_final_comparative_study_protocol.md` — complete participant and expert
   protocol, conditions, logging, analysis, and claim boundaries;
4. `89_evalLM_aligned_manuscript_outline.md` — current paper structure;
5. `90_blinded_artifact_quality_rubric.md` — expert rating anchors;
6. `85_quantitative_figure_package.md` and `figures/` — technical-validation
   figures and future study-data schemas;
7. `study_materials/` — shared task, formative guide, questionnaire, expert
   task, and the reproducible eight-sequence assignment schedule.

## Superseded research directions

The following remain useful history but are not current instructions:

- synthetic stakeholders as participant proxies;
- bias-calibrated stakeholder chat as the primary contribution;
- provider-comparison mode as the main experiment;
- online fraud and older adults as the only domain;
- unaided writing or a committee template as the baseline;
- three sequential studies called formative, pilot, and main experiment;
- a proposed fourth confirmatory cross-domain question; and
- any outcome framed as receiving or predicting ethics approval.

When an older file conflicts with the canonical files above, the canonical
files control.

## Evidence status

Completed:

- functional research prototype;
- instrumented two-condition Study Mode with a same-model general-chat
  baseline, immutable assignment manifest, common final submission, and
  pseudonymous timing/model-call export;
- deterministic technical evaluation on 21 fictional seeded cases;
- reproducible technical figures and machine-readable CSV data;
- final RQ and study contract;
- EvalLM-aligned writing blueprint.

Not yet completed:

- written ethics decision for the final human study;
- real formative interviews;
- comparative participant sessions;
- blinded expert ratings;
- empirical analysis and results; and
- final manuscript.

No technical, demo, or development record may be relabeled as participant or
expert evidence.
