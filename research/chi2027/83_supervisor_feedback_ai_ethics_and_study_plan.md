# SafeBARS: AI-Era Ethics Basis and Empirical Study Plan

Status: supervisor-feedback synthesis retained for provenance. Its study
sequence and sample decisions are superseded by
`CURRENT_CANONICAL_PLAN.md` and files 86-90.
Date: 23 July 2026

## Decision in one sentence

SafeBARS is a pre-submission research-ethics preparation system that helps a
researcher turn a human-facing research plan into (1) a framework-grounded,
stress-tested ethics application draft and research design, and (2) a focused
expert-review record for questions that AI cannot responsibly settle.

It does not predict approval, replace a university form, or act as an ethics
committee.

## What the three reports contribute

The two progress reports and the CoBRA study report are background design
inputs, not evidence that SafeBARS is effective.

### Progress Report and Progress Report Project 2

The reusable lessons are:

1. represent difficult situations as a classified and progressively varied
   case library;
2. keep data, analysis, interaction, and evaluation modules separable;
3. preserve traceable intermediate artefacts;
4. evaluate against explicit criteria instead of relying only on a polished
   demonstration; and
5. begin from a concrete research problem rather than adding technology first.

SafeBARS applies these lessons through its scenario library, passage-level
provenance, bounded specialist tasks, inspectable stopping rules, and seeded
technical cases. The older reports' proposed ethics-learning and learner-bias
features are not part of the current contribution.

### CoBRA study report

The transferable methodological lesson is to operationalise an abstract goal
into observable constructs and controlled test cases. For SafeBARS, the
construct is not a single “ethics score.” It is decomposed into:

- completeness of application-relevant information;
- specificity and actionability of safeguards;
- evidence traceability;
- appropriate escalation of situated questions;
- unsupported or overconfident claims;
- quality of researcher revisions; and
- expert triage effort.

The report is an internal design input. Any external claims about CoBRA must be
verified from the original publication before being used in a paper.

## Literature basis for ethics approval in the AI era

### Primary AI-era review anchor

Makridis et al. (2023), “Informing the ethical review of human subjects research
utilizing artificial intelligence,” proposes modular AI questions that can be
added to an existing IRB process. The questions cover the purpose and autonomy
of AI, data sources, intended population versus the development sample,
performance and bias, privacy and security, participant disclosure, impact,
human oversight, monitoring, and accountability. The work is especially useful
for SafeBARS because it was designed to support dialogue between researchers and
reviewers without replacing an existing review process.

DOI: https://doi.org/10.3389/fcomp.2023.1235226

### University research-ethics guidance

Connelly, Osborne, Black, and Terras (2025), “Guidance for research ethics
committees and researchers on designing research in the age of AI,” is directed
at university research ethics committees and researchers. It adds review
guidance, risk and impact assessment, committee challenges, and a checklist for
AI-era research.

DOI: https://doi.org/10.5281/zenodo.13739834

### Human expert review and iteration

Bernstein et al. (2021) shows why conventional human-subjects review can miss
broader societal AI impacts and describes an iterative Ethics and Society Review
process: researcher statement, interdisciplinary panel review, feedback and
revision, and recommendation. SafeBARS uses this as a process precedent for
explicit handoffs; it does not automate the panel's judgment.

DOI: https://doi.org/10.1073/pnas.2117261118

### Framework stack used in the system

- Belmont Report: respect for persons, beneficence, and justice.
- Menlo Report: ICT and data-research extension.
- Makridis et al.: AI-specific human-subjects review questions.
- Connelly et al.: university REC guidance, risk, and impact assessment.
- NIST AI RMF 1.0: Govern, Map, Measure, and Manage.
- Value Sensitive Design: stakeholders, values, and tensions.
- Ethics and Society Review: interdisciplinary reflection and iteration.

These sources are complementary. They are not merged into a universal
compliance rule or a numerical ethics score.

## Comparable CHI work and what to borrow

### Gray et al., CHI 2024

“Building an Ethics-Focused Action Plan: Roles, Process Moves, and Trajectories”
used six co-creation workshops with 26 technology and design practitioners. It
shows that ethics support must resonate with local work practices and that a
single checklist can create false security. SafeBARS should therefore preserve
open-ended rationale, revisions, multiple stakeholder positions, and expert
handoffs.

DOI: https://doi.org/10.1145/3613904.3642302

### Hanschke et al., CHI 2024

“Data Ethics Emergency Drill” developed a context-specific role-play toolbox
through three studies with data-science teams. It supports the use of realistic
breakdown scenarios and iterative field testing rather than abstract warnings.

DOI: https://doi.org/10.1145/3613904.3642402

### Sadek et al., CHI 2024

“Guidelines for Integrating Value Sensitive Design in Responsible AI Toolkits”
used four workshops with 17 early-career AI researchers. Its findings support
illustrative examples, collaboration, education, and open-ended prompts rather
than closed checklist compliance.

DOI: https://doi.org/10.1145/3613904.3642810

### Kim et al., CHI 2024

“EvalLM” evaluated an interactive LLM-supported workflow in a within-subject
comparison with 12 participants and examined revision decisions, user-defined
criteria, and trust. It is a useful methodological analogue for comparing a
structured interactive system with current practice while studying how users
interpret AI-produced evaluations.

DOI: https://doi.org/10.1145/3613904.3642216

### Ledo et al., CHI 2018

“Evaluation Strategies for HCI Toolkit Research” argues that an evaluation
should follow from the claims of the research contribution. SafeBARS should
therefore test protocol revision, traceability, handoff quality, and reviewer
effort—not only usability or satisfaction.

DOI: https://doi.org/10.1145/3173574.3173610

## Formative Study → Design Goals → App

The formative study has not yet been conducted. The supervisor comments and
reports motivate the following provisional goals; they must be refined through
real participants before being reported as formative findings.

### Planned formative study

Recruit 8–12 people across two roles:

- 4–6 researchers or research-support staff who have prepared human-subjects
  ethics applications; and
- 4–6 ethics committee members, school representatives, data-protection,
  safeguarding, methods, or AI-governance advisors.

Use a 60–75 minute semi-structured session:

1. ask participants to describe their current application and review workflow;
2. identify where information is missing, duplicated, or difficult to judge;
3. walk through a non-AI and an AI-enabled protocol case;
4. sort the literature-derived questions into essential, conditional, unclear,
   and institution-specific groups;
5. inspect a SafeBARS application draft and expert handoff;
6. discuss what AI may prepare, what requires a named human, and what evidence a
   reviewer needs; and
7. co-edit the provisional design goals.

Analyse transcripts with reflexive thematic analysis and maintain a transparent
feedback-to-design change log.

### Provisional design goals

DG1 — Context before analysis
Capture research area, institution or organisation, school or department,
committee or pathway, and jurisdiction without assuming that the user is a
student.

DG2 — Low-burden but complete intake
Use six short core questions. Add one structured AI supplement only when AI is
declared or detected.

DG3 — Framework-grounded, evidence-linked preparation
Show which submitted passage supports each review question and distinguish
documented, partial, and missing evidence from ethical acceptability.

DG4 — Encounter-level stress testing
Rehearse concrete breakdowns across recruitment, consent, participation,
distress, withdrawal, data use, and follow-up.

DG5 — Calibrated automation and epistemic handoff
Let bounded agents organise and test materials, but route institutional,
community, safeguarding, data-governance, and AI-governance judgments to a
qualified person with a reason and closure condition.

DG6 — Actionable dual outputs
Generate a submission-oriented ethics application draft and research design for
the researcher, plus a concise caseload, advice history, and portfolio summary
for expert reviewers.

DG7 — Contestability and version history
Allow users to inspect sources, reject or revise issues, record rationale,
rerun bounded tasks, and preserve human decisions across versions.

### Current application mapping

| Design goal | Current SafeBARS feature |
|---|---|
| DG1 | “Research area and ethics-review context” field and first intake question |
| DG2 | Six core questions plus conditional AI ethics-review supplement |
| DG3 | Framework map, source passages, readiness fields, cited sources |
| DG4 | Participant journey and selected breakdown scenario traces |
| DG5 | Role-routed handoffs and separate researcher/expert workspaces |
| DG6 | Application draft, research design, expert summary, and caseload exports |
| DG7 | Issue decisions, linked revisions, reruns, event history, and protocol versions |

### Claim traceability matrix

This table is the controlling link between the formative work, system, study,
and eventual claims. Rows may change after the formative study; results must
not be written into it in advance.

| Formative need to validate | Design goal | Feature | RQ | Study evidence | Claim permitted if supported |
|---|---|---|---|---|---|
| Application context is institution-specific and often missing | DG1 | Review-context field and readiness check | RQ1 | Missing/complete fields; expert realism rating | SafeBARS helped users state review context more completely |
| Long forms and chat exchanges create intake burden | DG2 | Six core questions plus conditional AI supplement | RQ1 | Completion time, omissions, workload, interview | The staged intake balanced burden and coverage for this sample |
| Generic AI advice lacks inspectable grounds | DG3 | Cited framework dimensions and passage evidence | RQ1, RQ2 | Valid-source rate, unsupported claims, source inspections | Provenance improved grounding or user understanding |
| Static review misses encounter breakdowns | DG4 | Journey map and scenario traces | RQ1, RQ2 | Consequential issues and revisions found per case | Encounter testing surfaced actionable issues beyond the baseline |
| AI cannot settle institutional or situated judgments | DG5 | Stopping rules and role-routed handoffs | RQ2, RQ3 | Correct routing, handoff quality, reliance interviews | Explicit boundaries supported more appropriate escalation |
| Experts spend time reconstructing context | DG6, DG7 | Expert summary, history, and linked revision | RQ3 | Triage time, clarification requests, provenance confidence | Structured handoffs improved expert triage for the tested tasks |

## Research goals and research questions

### Research goals

RG1 — Improve the quality of ethics preparation
Help researchers produce more complete, specific, and internally consistent
protocols and application drafts.

RG2 — Make AI support inspectable and appropriately limited
Increase traceability and useful human escalation while reducing unsupported
ethical conclusions.

RG3 — Improve expert attention allocation
Help reviewers focus on sensitive, situated, or unresolved questions without
concealing missing information or increasing false confidence.

### Research questions

RQ1 — Protocol and application quality
Compared with general-purpose LLM chat, how does SafeBARS affect the
completeness, specificity, actionability, and evidence-grounding of revised
research plans and ethics application drafts?

RQ2 — Revision and calibrated reliance
How do provenance, scenario traces, explicit boundaries, and human handoffs
shape researchers' revision decisions, contestation, and reliance on AI advice?

RQ3 — Expert review work
How do SafeBARS expert summaries and handoffs affect reviewers' triage time,
clarification needs, identification of consequential issues, and confidence in
the basis of their advice?

RQ4 — Transfer across research contexts (secondary)
Which benefits and breakdowns recur across academic HCI, qualitative
social/health research, and applied UX or public-service evaluation?

RQ4 should remain secondary unless the final sample supports a credible
cross-domain comparison.

## Comparative user study

### Conditions

A within-subject, counterbalanced comparison:

- SafeBARS condition: the full structured workflow, including the same
  configured LLM provider if the optional critic is enabled;
- general LLM condition: free chat with the same model, source materials, time
  limit, and task instruction.

Using the same model isolates the interaction and workflow contribution rather
than comparing model quality. The model, version, temperature, prompts, and run
date must be logged.

### Participants

Pilot with 12–16 protocol preparers, then determine the main-study sample from
pilot variance and the smallest effect worth detecting. Recruit beyond HCI:
qualitative researchers, UX/service researchers, public-sector evaluators,
community research staff, and postgraduate or staff researchers who have
prepared or contributed to human-facing protocols.

Recruit a separate blinded expert panel of 6–10 people across ethics review,
methods, data protection, safeguarding, community research, and AI governance.
No individual expert needs to cover every category.

### Tasks and cases

Each participant revises two matched fictional protocols:

- one non-AI sensitive human-facing study; and
- one AI-enabled study containing issues in data provenance, population fit,
  disclosure, oversight, monitoring, and redress.

Counterbalance condition and case order. Seed comparable but not identical
issues. Do not tell participants the issue list.

Each 35-minute task requires:

1. inspect the protocol;
2. identify and revise ethical weaknesses;
3. produce an application-oriented draft;
4. mark unresolved questions for expert review; and
5. explain two important decisions.

### Primary outcome rubric

Blinded experts score each final artefact using literature-derived, behaviourally
anchored criteria:

- application-information completeness;
- safeguard specificity and operational detail;
- AI-purpose, data, population, bias, disclosure, oversight, monitoring, and
  redress coverage where applicable;
- evidence traceability;
- actionability of revisions;
- appropriate uncertainty and handoff quality;
- internal contradictions; and
- unsupported normative or compliance claims.

Use at least two independent coders, train on held-out examples, report
agreement, and resolve disagreements without hiding the original ratings.

### Process and experience measures

- time to first substantive revision and final submission;
- number and type of revisions;
- source inspections and scenario traces opened;
- accepted, rejected, edited, and deferred issues;
- handoff owner and closure-condition quality;
- number of unsupported AI statements retained;
- perceived control, workload, usefulness, and trust;
- post-task confidence; and
- stimulated-recall interview about two decisions.

### Expert-work outcomes

- triage time;
- time to first decision;
- number of clarification requests;
- proportion of handoffs judged correctly routed and sufficiently evidenced;
- consequential issues identified;
- duplicated or low-value issues;
- reviewer confidence in evidence provenance; and
- qualitative account of what the system should never decide.

### Analysis

For the pilot, report paired distributions, effect sizes, confidence intervals,
and qualitative themes; do not over-interpret significance tests. For a
powered main study, use mixed-effects models with condition as a fixed effect
and participant and case as random effects where assumptions and sample size
permit. Analyse interview and interaction-log data together to explain why
outcomes changed.

Do not use “received ethics approval” as the primary outcome. Approval depends
on institution, jurisdiction, committee, and project context and would encourage
automation bias. The defensible outcomes are preparation quality, traceability,
revision behaviour, calibrated handoff, and reviewer work.

## Technical evaluation before human recruitment

The existing 21 seeded cases test deterministic specification conformance:
pathway routing, framework activation, surfaced missing dimensions, provenance,
and repeatability. Expand the AI cases to cover:

1. AI merely used for transcription or analysis;
2. AI directly interacting with participants;
3. AI recommendations informing a researcher;
4. AI output driving a consequential decision;
5. external model-provider access to sensitive data;
6. population mismatch and subgroup performance;
7. missing participant disclosure;
8. missing human override and stopping rule; and
9. missing correction, complaint, and redress process.

Passing these cases shows that the software follows its specification. It does
not establish ethical validity; that requires the formative and comparative
studies above.

## Revised originality claim

Do not claim novelty for chat intake, multiple agents, ethics checklists, AI risk
frameworks, or protocol review alone.

The candidate contribution is the integration and empirical evaluation of an
inspectable three-party workflow that links:

1. low-burden, framework-routed information collection;
2. passage-grounded encounter stress testing;
3. explicit epistemic stopping and role-specific human handoff;
4. researcher contestation and protocol revision; and
5. dual researcher/expert outputs with preserved provenance.

Whether this integration is useful, usable, and original is an empirical
question for the planned studies, not a completed claim.

## Immediate execution order

1. Conduct 2–3 internal dry runs of the revised intake and AI supplement.
2. Ask two knowledgeable colleagues to check question wording and export
   transferability to the local university form.
3. Run the 8–12 person formative study.
4. Freeze the design goals and primary outcome rubric.
5. Pilot the counterbalanced comparison with 4–6 participants.
6. Refine timing, cases, logging, and coder manual.
7. Obtain ethics approval for the SafeBARS evaluation study itself.
8. Run the full comparative study and blinded expert review.
9. Analyse results and write only claims supported by the evidence.
