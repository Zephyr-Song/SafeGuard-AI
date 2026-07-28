# SafeBARS Final EvalLM Blueprint, Research Questions, and Study Contract

Date: 27 July 2026  
Status: final methodological and writing decision before formative recruitment

## Decision and precedence

**EvalLM: Interactive Evaluation of Large Language Model Prompts on
User-Defined Criteria** (Kim et al., CHI 2024) is the **sole primary
methodological and writing blueprint** for the SafeBARS CHI paper.

- DOI: https://doi.org/10.1145/3613904.3642216
- Author-hosted paper:
  https://younghokim.net/files/papers/evallm-chi24.pdf
- Project page: https://evallm.kixlab.org/

“Sole primary blueprint” means that SafeBARS will follow EvalLM's empirical and
paper arc:

1. investigate the existing workflow and its difficulties;
2. derive design goals;
3. present an inspectable interactive system;
4. run a bounded technical evaluation;
5. compare the system with current practice in a counterbalanced
   within-participant study;
6. combine interaction logs, task artefacts, questionnaires, and interviews;
7. organise findings by the research questions; and
8. discuss both useful collaboration and overreliance.

EvalLM is not the only citation and does not supply SafeBARS's research-ethics
content. Belmont, Menlo, Makridis et al., Connelly et al., NIST AI RMF, Value
Sensitive Design, and Ethics and Society Review remain framework sources.
Gray et al., Data Ethics Emergency Drill, Simulacrum of Stories, CoBRA, and
other CHI/IUI/DIS work remain supporting design and positioning sources. They
must not silently introduce a second study structure.

For final research questions, experimental design, analysis, and paper
organisation, this document supersedes the incompatible alternatives in the
earlier planning drafts. Those files remain an audit trail. The controlling
product and framework decisions in
`83_supervisor_feedback_ai_ethics_and_study_plan.md` remain in force where they
do not conflict with this study contract.

## What is transferred from EvalLM

EvalLM used formative interviews with eight prompt designers, translated those
findings into design goals, presented an interactive system and a technical
evaluation, and then ran a counterbalanced within-participant comparison with
12 participants. Participants completed two 35-minute tasks under two
conditions. EvalLM combined seven-point ratings, workload items, interaction
logs, post-task interviews, and quantitative paired comparisons. Its findings
were organised around revision, criteria formation, trust, and workload.

SafeBARS transfers the following methodological logic:

| EvalLM logic | SafeBARS adaptation |
|---|---|
| Current manual practice is the comparison target | Same-model general-purpose LLM chat is the current-practice target |
| Two tasks and two conditions per participant | One non-AI and one AI-enabled protocol task; one condition per task |
| Counterbalanced within-participant design | Eight balanced condition × task-type × order sequences |
| A fixed task period | 35 minutes for each protocol-preparation task |
| Inspectable explanations and history | Passage provenance, scenario traces, decision history, and handoff history |
| Revision is an empirical object | Protocol passages, application drafts, decisions, and linked revisions are empirical objects |
| Logs + questionnaires + interviews | Logs + artefacts + questionnaires + stimulated-recall interviews |
| Technical evaluation before the user study | Twenty-one seeded fictional cases test specification conformance |
| Findings reported by research question | Three final research questions determine the Results subsections |
| Explicit discussion of overreliance | Explicit analysis of unsupported claims, contestation, reliance, and human escalation |

## Final thesis

SafeBARS investigates whether a framework-grounded, passage-linked, and
three-party workflow can help people prepare sensitive human-facing protocols
more completely and inspectably than same-model general-purpose LLM chat,
while directing questions that AI cannot responsibly settle to qualified human
reviewers.

SafeBARS prepares material for review. It does not grant ethics approval,
predict committee decisions, determine that a protocol is ethical, or replace
institutional, community, participant, or expert judgement.

## Final contributions

The paper will claim exactly the contributions supported by completed evidence:

1. **A three-party interaction framing for bounded ethics preparation.**
   SafeBARS links researcher-authored protocol material, bounded AI critique,
   and named human expertise through inspectable provenance, contestable
   revision, and epistemic handoff.
2. **SafeBARS, an interactive research prototype.** The system combines
   adaptive intake, framework routing, encounter-level stress testing,
   passage-level issue provenance, accept/edit/reject/defer decisions,
   role-routed handoffs, and distinct researcher and expert outputs.
3. **Empirical and design knowledge about structured AI support for protocol
   preparation.** A within-participant comparison and blinded expert review
   will examine preparation quality, calibrated use, and expert work. This
   contribution may be claimed only after the planned study is completed and
   analysed.

The paper will not claim novelty for chat intake, multiple agents, ethics
checklists, framework selection, protocol review, LLM critique, or dashboards
alone.

## Final research questions

The paper has **exactly three research questions**.

### RQ1 — Protocol-preparation quality

Compared with same-model general-purpose LLM chat, how does SafeBARS affect the
quality of revised research plans and ethics-application drafts for matched
sensitive human-facing protocol tasks?

| Element | Definition |
|---|---|
| Constructs | Application-information completeness; safeguard specificity; revision actionability; evidence grounding; internal consistency; AI-specific governance coverage when applicable; unsupported normative or compliance claims |
| Primary estimand | Mean within-participant difference, SafeBARS minus general chat, in the blinded expert-rated Preparation Quality Index: the mean of completeness, safeguard specificity, actionability, and evidence grounding, each scored 1–5 |
| Secondary estimands | Condition differences in each rubric item; AI-governance coverage for AI cases; contradiction count; unsupported-claim count; final-submission time |
| Data | Standardised final research plan, standardised ethics-application draft, protocol type, case, condition, order, timestamps, two independent expert ratings per artefact |
| Source | Participant-produced artefacts; task logs; blinded expert rubric |
| Analysis | Estimation-first mixed model with condition as the focal fixed effect, protocol type, period/order, and case as fixed controls, and participant and expert as random intercepts; report adjusted mean difference, standardised effect, and 95% confidence interval; paired non-parametric sensitivity analysis |
| Claim boundary | A supported result may show better protocol-preparation quality for this sample and these fictional tasks. It cannot show that SafeBARS makes research ethical, predicts approval, improves real participant outcomes, or generalises to every institution or jurisdiction |

The Preparation Quality Index is a study outcome, not an “ethics score.” Its
four components and their distributions must also be reported. If the
pre-registered reliability check is inadequate, the components must be
reported separately and the index must not be used as a headline result.

### RQ2 — Contestation and calibrated use

How do passage provenance, scenario traces, explicit boundaries, and revision
controls shape how protocol preparers inspect, accept, edit, reject, defer, and
rely on AI-generated critiques compared with general chat?

| Element | Definition |
|---|---|
| Constructs | Source inspection; source-grounded revision; contestation; uptake; retained unsupported claims; perceived control; trust and skepticism; workload |
| Primary estimand | Within-participant condition difference in the proportion of the two required consequential decision records that identify or quote an exact source passage and explain the participant's decision |
| Secondary estimands | Retained unsupported-claim count; time to first substantive revision; perceived-control rating; trust/reliance ratings; five-subscale workload score; distributions and reasons for accept/edit/reject/defer decisions |
| Data | Versioned before/after passages; source-inspection and scenario-open events; issue decisions and rationales; general-chat transcript; final artefacts; seven-point post-task ratings; five NASA-TLX subscales excluding Physical Demand; stimulated-recall interview |
| Source | SafeBARS event log; complete baseline chat log; participant artefacts and questionnaires; screen recording where consented; interview transcript |
| Analysis | Binomial mixed model for source-grounded revision proportion; negative-binomial model for unsupported-claim counts if overdispersed; ordinal mixed models or pre-specified paired tests for seven-point items; log-transformed time model; reflexive thematic analysis of reliance, disagreement, and decision rationales, triangulated with traces |
| Claim boundary | More interaction, more deferral, or lower trust is not automatically better calibration. Claims require convergence among behaviour, retained content, and participant explanation. The study cannot infer a stable psychological trait or prove that a participant relied “correctly” in every instance |

The two common decision records are collected identically in both conditions:
one concerns an important revision and one concerns something rejected,
substantially changed, or deferred. Accept/edit/reject/defer is native to
SafeBARS. For the general-chat condition, independent coders will additionally
identify suggestion units and code their uptake in the final artefact. Native
interface-event counts and retrospectively coded chat units must not be treated
as mechanically identical; direct condition claims will use the common
decision-record and artefact-level measures.

### RQ3 — Expert handoff work

Compared with unresolved-question packets prepared after general chat, how do
SafeBARS expert summaries and epistemic handoffs affect reviewer triage effort,
clarification needs, routing and evidence quality, and subsequent researcher
revision?

| Element | Definition |
|---|---|
| Constructs | Triage effort; time to first decision; clarification need; role-routing appropriateness; evidence sufficiency; provenance confidence; advice-to-revision linkage |
| Primary estimand | Mean within-participant condition difference in blinded expert triage time from opening the standardised packet to the first recorded review decision |
| Secondary estimands | Clarification-request count; 1–5 routing-appropriateness rating; 1–5 evidence-sufficiency rating; 1–7 provenance-confidence rating; proportion of expert advice followed by a linked researcher response or passage revision |
| Data | Condition-neutral handoff packet; assigned/recommended role; cited passage; unresolved question; “why AI cannot resolve” rationale; closure condition; expert timestamps and actions; clarification text; expert advice; researcher follow-up revision |
| Source | Expert workspace log; blinded expert rubric; review history; researcher revision history; short expert interview |
| Analysis | Mixed model on log triage time; negative-binomial model for clarification counts; cumulative-link mixed models for ordinal ratings; logistic mixed model for linked revision; qualitative analysis of what experts considered non-delegable |
| Claim boundary | Faster review is not better review by itself. A supported result may show reduced reconstruction effort or better evidenced routing for these packets. It cannot show that experts approved the protocol, that SafeBARS replaces committee deliberation, or that one reviewer role is universally correct |

## Unified formative phase

The formative phase follows EvalLM's “interviews → design goals” structure but
adds the second human role required by SafeBARS.

- **Sample:** 6 participants: three protocol preparers and three ethics,
  methods, data-protection, safeguarding, community, or AI-governance
  reviewers/advisors.
- **Eligibility:** direct experience preparing or reviewing at least one
  human-facing protocol within the previous two years.
- **Session:** 35–45 minutes using fictional non-confidential materials.
- **Procedure:** current-workflow interview; non-AI and AI case walkthrough;
  sorting of literature-derived questions; inspection of one SafeBARS draft and
  one handoff; discussion of what AI may prepare, what requires a named person,
  and what evidence a reviewer needs.
- **Analysis:** reflexive thematic analysis plus a transparent
  feedback-to-design change log.
- **Use:** refine and freeze the design goals, rubric wording, case realism,
  and expert packet before the comparative study.

These participants are not part of the comparative dataset. Formative
statements cannot be written as findings before sessions are conducted.

## Unified comparative study

### Participants

- **Protocol preparers:** 24 participants, allocated evenly across eight
  counterbalancing sequences (three per sequence).
- **Experience requirement:** prepared, reviewed, or materially contributed to
  a human-facing research or evaluation protocol within the previous two
  years.
- **Recruitment breadth:** recruit across academic HCI/qualitative research,
  UX/service/public-sector research, and community, health, education, or other
  applied research. These are breadth targets rather than quotas and support
  breadth; the study is not powered to rank disciplines.
- **Expert panel:** six reviewers spanning research ethics, methods, data
  protection, safeguarding, community engagement, and AI governance.
- **Expert assignment:** every artefact is independently rated by two experts
  using a balanced incomplete block; one is randomly designated to provide the
  response returned to the researcher.

The target of 24 supports three completed sessions in each of eight
counterbalancing sequences and estimation of within-participant differences.
A transparent paired-test sensitivity calculation gives approximately 80%
power only for a standardized within-participant effect of about 0.60; it is
not a promise of power for smaller effects and does not replace the mixed-model
analysis. Recruitment stops at 24 completed paired sessions or the
preregistered calendar stop date, whichever comes first, without
significance-based optional stopping. If fewer than 16 paired sessions are
completed, the work is reported as a feasibility-oriented mixed-methods study
and does not make a confirmatory effectiveness claim.

### Conditions

1. **SafeBARS:** the full structured workflow: intake, framework routing,
   encounter map, scenario traces, issue provenance, decisions, handoffs, and
   exports.
2. **General chat:** free interaction with a general-purpose LLM using one
   neutral protocol-review instruction and the same source materials.

Both conditions must use the same provider, model snapshot, temperature,
language, time limit, and task instruction. The model configuration, system
prompts, run date, failures, retries, and transmitted material must be archived.
If exact provider parity is impossible, recruitment must pause until the
comparison is redesigned and re-registered.

### Tasks and cases

Each participant completes two 35-minute tasks:

- one sensitive non-AI human-subjects protocol; and
- one AI-enabled protocol with issues involving data provenance, population
  fit, disclosure, oversight, monitoring, correction, and redress.

Four fictional cases will be frozen before recruitment: two non-AI cases and
two AI-enabled cases. They will be matched by length, number and severity of
seeded issues, reading level, and required output. Independent methods experts
will pilot the match without seeing the final condition allocation.

Eight Latin-style sequences will balance:

- condition order;
- non-AI/AI task order;
- case identity; and
- the condition in which each case appears.

Every task produces the same condition-neutral deliverables:

1. revised research plan;
2. ethics-application draft;
3. unresolved-question handoff packet containing question, recommended owner,
   rationale, cited evidence, and closure condition; and
4. a short decision memo explaining two important revisions.

### Procedure

1. Consent, background questionnaire, and pre-task briefing.
2. Condition and case 1 walkthrough.
3. Task 1, 35 minutes.
4. Post-task questionnaire and 8–10 minute stimulated-recall interview.
5. Break and condition/case 2 walkthrough.
6. Task 2, 35 minutes.
7. Post-task questionnaire and condition-comparison interview.
8. Blinded expert review after the participant session.
9. Within seven days, a 20-minute researcher follow-up in which the participant
   receives one expert response per condition and may clarify, reject, or link
   it to a final passage revision.

### Blinding and standardisation

Condition names and interface branding will be removed from final artefacts and
handoff packets. Layout, headings, typography, file type, and requested
sections will be normalised before expert review. Artefacts will be randomised.
Experts will not be told the condition allocation.

This is masked review rather than guaranteed perfect blinding: writing style or
provenance detail may reveal a condition. Experts will record a condition
guess and confidence so the analysis can report possible unblinding.

## Unified measures

### Blinded artefact rubric

Each positive item uses a behaviourally anchored 1–5 scale:

1. application-information completeness;
2. safeguard specificity and operational detail;
3. revision actionability;
4. evidence grounding and traceability;
5. internal consistency;
6. appropriate uncertainty and handoff quality; and
7. AI purpose, data, population, bias, disclosure, oversight, monitoring, and
   redress coverage for AI-enabled cases only.

Experts also record counts of:

- internal contradictions;
- unsupported normative or compliance claims;
- consequential issues retained; and
- duplicated or low-value issues.

The full anchors and examples must be frozen in a coder manual. At least two
held-out artefacts must be used for training before study artefacts are rated.
Original independent ratings must be retained even when disagreements are
discussed.

### Participant questionnaire

After each condition:

- perceived control: four seven-point items;
- usefulness/collaboration: three seven-point items adapted to protocol
  preparation;
- trust and skepticism: four seven-point items, including verification and
  overreliance;
- confidence in the final protocol: two seven-point items; and
- NASA-TLX Mental Demand, Temporal Demand, Performance, Effort, and Frustration
  on 0–100 scales; Physical Demand is omitted, following EvalLM's
  task-appropriate adaptation.

Item wording, scoring direction, and planned subscale calculation must be
included in the preregistration. Adapted items must not be described as
validated psychometric scales without separate evidence.

### Process measures

- time to first substantive revision and final submission;
- number and type of substantive revisions;
- exact-source-grounded revision proportion;
- source passages and scenario traces opened;
- suggestions accepted, edited, rejected, deferred, or ignored;
- retained unsupported claims;
- model failures, retries, and unavailable states;
- handoff owner and closure-condition quality; and
- researcher responses and linked revisions after expert advice.

## Unified analysis contract

### General rules

1. Preregister hypotheses, outcomes, exclusions, models, and figure templates
   after the formative study and before comparative recruitment.
2. Treat the condition coefficient as the focal estimand and report effect
   sizes and 95% confidence intervals, not only p-values.
3. Use case as a fixed control because four stimuli are insufficient for a
   defensible population-level random-case inference.
4. Include participant and expert random intercepts where the outcome contains
   repeated observations from both.
5. Check residuals, dispersion, zero inflation, and convergence; document any
   model change as a deviation.
6. Do not choose paired t-tests versus non-parametric tests solely from a
   low-powered normality test. Use the pre-registered mixed model and a robust
   paired sensitivity analysis.
7. Preserve null, mixed, and negative results.

### Reliability and coding

- Report a two-way random, absolute-agreement ICC for the Preparation Quality
  Index and weighted kappa for individual ordinal rubric items.
- Report agreement before adjudication.
- If index reliability is inadequate, analyse and discuss its four components
  rather than hiding disagreement in a composite.
- Two trained coders will identify substantive revisions, suggestion uptake,
  exact passage links, contradictions, and unsupported claims from
  condition-neutral artefacts.
- Reflexive thematic analysis will be used for interviews and stimulated
  recall. It will not be presented as a reliability exercise; a second
  researcher will provide critical discussion and challenge interpretations
  rather than manufacture a consensus coefficient.

### Multiple outcomes

The Preparation Quality Index condition difference is the single primary
quantitative estimand. Other outcomes are secondary or exploratory. For
pre-specified families of secondary quantitative tests, report unadjusted
effect estimates and confidence intervals plus Holm-adjusted p-values. Do not
turn exploratory process measures into confirmatory findings after seeing the
data.

### Missing data and exclusions

- Record withdrawal, technical failure, missing surveys, incomplete artefacts,
  and unavailable expert reviews separately.
- Include every completed task with an analysable artefact; do not exclude a
  participant because their result disfavors SafeBARS.
- Do not impute missing primary outcomes in the initial study. Report the
  missingness pattern and run a documented sensitivity analysis if attrition is
  non-trivial.
- Do not winsorise time or count outcomes silently. Report influential cases
  and robust sensitivity results.
- Freeze the exclusion decisions before condition labels are revealed to
  expert raters and analysts of blinded artefacts.

## Reasoned deviations from EvalLM

### General chat instead of an ablated SafeBARS interface

EvalLM compared its full system with a manual version of the same interface.
SafeBARS compares against general-purpose LLM chat because the paper asks
whether the structured workflow adds value beyond the practice researchers can
already use. Using the same underlying model, source material, task, language,
and time limit controls model quality while preserving an ecologically
meaningful baseline.

This baseline does not isolate every individual SafeBARS component. The paper
must therefore claim a **workflow-level** effect, not an effect of provenance,
the encounter map, or handoff in isolation.

### Blinded external expert panel

EvalLM did not externally score final prompts because participants defined
subjective task criteria that could differ across conditions. SafeBARS uses
matched protocol tasks and a frozen, literature-derived, behaviourally anchored
rubric. Protocol preparation also has a genuine second user: the reviewer who
must reconstruct context and judge whether an unresolved question is
sufficiently evidenced.

The expert panel is therefore necessary for the SafeBARS contribution, but its
ratings remain expert judgements rather than approval decisions or objective
ethical truth.

### Handoff-centred third research question

EvalLM's third question examined interpretation and trust in automated
evaluations. SafeBARS retains calibrated reliance in RQ2 and extends the third
question to epistemic handoff because a high-stakes ethics-preparation system
must stop where institutional authority or situated knowledge is required.
The three-party researcher–AI–expert workflow is a defining SafeBARS
contribution, not an optional feature.

### Shared framework criteria rather than entirely user-defined criteria

EvalLM let prompt designers define criteria because application goals were
subjective. SafeBARS lets formative participants and researchers contest the
framework mapping, but the comparative study freezes a common rubric so
conditions can be compared fairly. The criteria are application-relevant
review dimensions, not automatic compliance rules.

### Larger and role-diverse sample

EvalLM's comparative study involved 12 prompt designers. SafeBARS plans 24
protocol preparers plus six expert reviewers because it includes
counterbalanced non-AI/AI cases, blinded artefact ratings, and expert-work
outcomes. The sample remains modest and does not support population-wide or
cross-discipline ranking claims.

### Technical specification tests rather than ethics validation

EvalLM technically evaluated its automatic evaluator. SafeBARS uses 21 seeded
fictional cases to test routing, framework activation, planted omission
detection, passage provenance, confidence reporting, and deterministic
repeatability. Passing these cases shows specification conformance only; it
does not validate ethical reasoning.

## EvalLM-to-SafeBARS writing map

| EvalLM paper section | Required SafeBARS section | Mapping and justified difference |
|---|---|---|
| Abstract | Abstract | Problem, SafeBARS workflow, two-stage empirical method, actual findings only, contributions, and explicit non-approval boundary |
| 1. Introduction | 1. Introduction | Begin with the difficulty of preparing a sensitive protocol and the attraction and limits of general chat; state the three-party gap, exactly three research questions, and contributions |
| 2. Related Work | 2. Related Work | Organise around research-ethics preparation, AI-assisted research work, contestable agentic systems, calibrated reliance, and human handoff; framework sources are separated from HCI system precedents |
| 3. Formative Interviews | 3. Formative Study | Report the 10-participant dual-role study, current practices, missing information, AI boundaries, reviewer needs, and feedback-to-design changes; do not present supervisor comments as participant findings |
| 4. Design Goals | 4. Design Goals | Derive and freeze context-first intake, low-burden completeness, evidence linkage, encounter stress testing, calibrated handoff, dual outputs, and contestability/version history |
| 5. EvalLM | 5. SafeBARS | Walk through researcher, bounded agents, and expert roles; explain framework routing, evidence lineage, encounter traces, issue decisions, handoffs, expert workspace, and exports with one end-to-end example |
| 6. Technical Evaluation | 6. Technical Evaluation | Report the seeded suite, exact assertions, provenance checks, failures, and limitations; never mix these results with participant outcomes |
| 7. User Study | 7. Comparative Study | Participants, same-model conditions, four cases, eight counterbalancing sequences, procedure, common deliverables, expert panel, measures, preregistered analysis, ethics and data handling |
| 7.2 Results | 8. Results | One subsection per final research question; within each, report quantitative estimate first, then behavioural/log evidence and qualitative explanation, including null and adverse findings |
| 8. Discussion | 9. Discussion | Structured workflow versus general chat; productive contestation; calibrated reliance; expert attention allocation; non-delegable judgement; transfer limits; design implications |
| Discussion limitations | 10. Limitations | Fictional cases, modest and partly university-linked sample, imperfect blinding, institution/jurisdiction dependence, model/version dependence, expert disagreement, short-term outcomes, and no approval or field-harm measure |
| 9. Conclusion | 11. Conclusion | Restate only empirically supported preparation, contestation, and reviewer-work contributions |
| Appendices/supplement | Appendices/supplement | Frozen cases, prompts, model settings, counterbalancing table, questionnaires, rubric, coder manual, deviations, analysis code, figure data, and anonymised materials permitted by consent |

The Results section must not be drafted as if the expected findings occurred.
Placeholders may name the estimand and planned figure, but may not contain
directional claims, fabricated quotations, or example p-values.

## Reproducibility and audit requirements

- Obtain institutional ethics approval for the SafeBARS evaluation before
  recruitment.
- Use fictional protocols; do not upload confidential active protocols or
  identifiable participant data to a model provider.
- Freeze cases, prompts, rubric, survey, counterbalancing, analysis code
  skeleton, and exclusion rules before the comparative study.
- Archive the exact app commit, provider, model version, temperature, prompts,
  run dates, and provider failures.
- Keep raw independent expert ratings and all analysis transformations.
- Generate paper figures from tidy exported data and commit-linked scripts.
- Distinguish formative participants, comparative participants, experts,
  internal dry runs, seeded technical cases, and development/demo telemetry in
  every table and figure.
- Publish de-identified materials and code only to the extent permitted by
  consent, institutional review, licensing, and provider terms.

## Claim and publication boundary

Following EvalLM as a single blueprint improves coherence; it does not guarantee
scientific validity, novelty, statistical power, positive findings, reviewer
agreement, or acceptance at CHI. CHI acceptance depends on the final
contribution, execution, ethical approval, evidence quality, analysis,
transparency, writing, venue fit, and peer review.

The paper must not say that it is accepted, under review, validated, effective,
or expert-approved unless that statement is factually true at the time of
writing. A null or mixed comparison remains reportable. If the formative study
invalidates the design goals or the pilot reveals that tasks, measures, or
conditions are not comparable, the study must be revised before recruitment
rather than preserving this blueprint for appearance.
