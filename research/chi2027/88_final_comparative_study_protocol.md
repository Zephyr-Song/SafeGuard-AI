# SafeBARS Final Comparative Study Protocol

Status: canonical study protocol for supervisor review and preregistration.

Date: 2026-07-27

Primary methodological blueprint: Kim et al., *EvalLM: Interactive Evaluation
of Large Language Model Prompts on User-Defined Criteria* (CHI 2024),
https://doi.org/10.1145/3613904.3642216.

This protocol supersedes the study designs in files 21, 35, 42, 45, 64, 70,
73, and `83_research_plan_and_user_study.md`. Those files remain provenance,
not instructions for data collection.

## 1. Research problem

Researchers preparing sensitive human-facing studies must translate incomplete
plans into operational safeguards and institution-facing ethics applications.
A general-purpose LLM can produce fluent advice, but its advice is difficult to
trace to submitted material, may conceal missing context, and may answer
questions that require situated human judgement.

SafeBARS tests a narrower proposition:

> A structured, inspectable workflow may help researchers revise protocols and
> ethics-application drafts more effectively than an otherwise comparable
> general LLM chat, while preserving explicit boundaries and routing unresolved
> questions to qualified people.

The study does not test whether SafeBARS grants approval, predicts committee
decisions, discovers every ethical issue, or replaces an ethics committee.

## 2. Final contribution claim

The candidate contribution is the design and empirical evaluation of an
inspectable three-party workflow connecting:

1. framework-routed, adaptive information collection;
2. passage-grounded review and encounter stress testing;
3. researcher accept, edit, reject, and defer decisions;
4. explicit epistemic stopping and role-specific expert handoff; and
5. linked researcher and expert outputs with preserved provenance.

The novelty claim concerns this integration and its observed effects on
research work. Chat intake, multiple agents, checklists, framework selection,
and LLM-generated advice are not claimed as individually novel.

## 3. Final research questions

### RQ1: Artifact quality

Compared with a general LLM chat using the same model, source materials, task
instruction, and time budget, how does SafeBARS affect the quality of revised
research plans and ethics-application drafts?

The four prespecified components of the primary Preparation Quality Index are:

- information completeness;
- safeguard specificity;
- actionability;
- evidence grounding and traceability.

The primary estimand is the average within-participant condition difference in
the blinded expert-rated four-component Preparation Quality Index. Appropriate
uncertainty and escalation, internal consistency, and unsupported normative,
legal, or compliance claims are prespecified secondary outcomes and must not be
silently added to the primary index after data collection.

### RQ2: Revision and calibrated reliance

How do SafeBARS's provenance, scenario traces, explicit boundaries, and
accept/edit/reject/defer decisions shape researchers' revision behaviour and
reliance on AI advice?

The primary estimand is the within-participant condition difference in the
proportion of the two required consequential decision records that identify or
quote an exact source passage and explain the participant's decision. One
record concerns an important revision; the other concerns something rejected,
substantially changed, or deferred.

This is a mechanism and experience question. Because the SafeBARS features are
evaluated as a bundle, the study cannot make separate causal claims about each
feature. Evidence will combine:

- interaction logs;
- revisions between initial and final artifacts;
- retained unsupported claims;
- appropriate deferrals;
- source inspections;
- decision rationales; and
- stimulated-recall interviews.

### RQ3: Expert review work

How do structured, provenance-preserving handoff packets affect experts'
ability to triage unresolved ethics questions compared with unstructured
protocol and chat materials?

The outcomes are:

- time to first defensible disposition;
- total triage time;
- number of clarification requests;
- consequential issues identified;
- routing and evidence sufficiency;
- advice actionability;
- confidence in the basis of the disposition; and
- expert accounts of what the system should never decide.

## 4. Study architecture

The project contains one formative grounding stage and one integrated
comparative study. It does not run three disconnected user studies.

### Stage F: formative grounding before feature freeze

Recruit 6 people: three protocol preparers and three people who support or
review sensitive human-facing protocols. Conduct a 35-45 minute
semi-structured interview and artifact walkthrough about:

- how context is gathered for an ethics application;
- where applicants misunderstand or omit information;
- when advice must be handed to an ethics, safeguarding, data, methods, or AI
  governance specialist;
- what evidence experts need before giving advice;
- what an AI system must not decide; and
- what would make an AI-supported application misleading or unsafe.

Analysis uses rapid framework analysis against the provisional design goals,
with an open column for unanticipated needs. Stage F may confirm, refine, merge,
or remove design goals, but it must not be reported as if it evaluated
SafeBARS's effectiveness.

Only study-blocking usability, instrumentation, and terminology changes are
allowed after Stage F. The feature set is then frozen.

If institutional review does not permit Stage F before the submission
timeline, the paper must describe the design goals as literature-grounded and
supervisor-informed, not as formative findings.

### Stage E: integrated comparative evaluation

Stage E has two linked cohorts:

1. protocol preparers complete a counterbalanced within-subject comparison;
2. qualified experts independently rate the resulting artifacts and complete
   a counterbalanced triage task.

The two cohorts generate evidence for the same three research questions.

## 5. Participants

### 5.1 Protocol preparers

Target 24 completed paired sessions. Recruitment stops when 24 complete
sessions have been obtained or at the preregistered calendar stop date,
whichever occurs first. There is no significance-based optional stopping.

Eligibility:

- age 18 or older;
- has authored, adapted, supported, or reviewed at least one human-facing
  research, evaluation, consultation, UX, service-design, or co-design
  protocol in the previous three years;
- can read and write the study language; and
- is not a developer of SafeBARS.

Recruit across academic HCI, qualitative or social research, UX and service
research, public-sector evaluation, and community research. Record experience
as descriptive context, not as a proxy for ethical expertise.

The target gives three completed participants in each of eight assignment
sequences. A simple paired-test sensitivity calculation indicates
approximately 80% power only for a standardized within-participant effect of
about 0.60. This is a transparent sensitivity statement, not a substitute for
the preregistered mixed model or evidence that smaller effects can be detected.

If fewer than 16 complete paired sessions are available by the stop date, the
paper must frame the evaluation as an estimation-oriented formative comparison
and avoid powered-effectiveness language.

### 5.2 Expert reviewers

Recruit 6 reviewers with recent experience in one or more of:

- university ethics review or research governance;
- qualitative or participatory methods;
- data protection and information governance;
- safeguarding;
- community-engaged research; or
- responsible AI and AI governance.

No reviewer is presented as authoritative across all areas. Expertise
categories and years of relevant experience are reported in aggregate.

Each final artifact receives at least two independent ratings. Assignment uses
a balanced incomplete block so that no expert rates every artifact and each
expert sees artifacts from both conditions.

## 6. Materials and experimental conditions

### 6.1 Fictional matched cases

Use fictional protocols only; participants do not upload confidential live
applications.

Prepare two matched case pairs:

- one pair of non-AI sensitive human-facing protocols; and
- one pair of AI-enabled protocols.

Each pair has equivalent issue families and comparable word count, but
different surface context. The AI pair includes data provenance, population
fit, participant disclosure, human oversight, monitoring, correction, and
redress.

Each case has a sealed authoring key listing planted omissions and intended
ambiguities. The key supports case balancing and coder training; it is not
treated as a complete ground truth for ethics.

### 6.2 SafeBARS condition

Participants use the frozen SafeBARS study build:

- guided intake;
- literature-grounded framework routing;
- encounter map and bounded scenario traces;
- passage-level provenance;
- issue decisions;
- explicit stopping rules and handoffs;
- ethics-application and research-design exports; and
- the same frozen LLM used in the comparison condition.

The study build hides demo cases, development evidence, provider selectors,
legacy V1 links, and previous sessions.

### 6.3 General LLM chat condition

Participants use a minimal chat interface with:

- the same frozen model and provider;
- the same source protocol;
- the same overall task instruction;
- the same time budget;
- the same maximum context and response budget; and
- file or passage access equivalent to the SafeBARS condition.

The baseline instruction asks the model to help identify and revise ethical
weaknesses and prepare an application-oriented draft. It does not mention
SafeBARS's named features or reveal the sealed issue key. Participants may
prompt freely after the standardized opening instruction.

### 6.4 Frozen model manifest

Before the first main-study session, record and freeze:

- provider;
- model and version identifier;
- endpoint or deployment identifier;
- system and initial task prompts;
- prompt hashes;
- temperature and other sampling parameters;
- maximum tokens;
- tool availability;
- date and time;
- fallback policy; and
- SafeBARS commit SHA.

If the provider silently changes the model, has a material outage, or returns
an unrecoverable error, flag the session and follow the preregistered
rescheduling rule. Do not switch providers mid-study.

## 7. Assignment and counterbalancing

Each protocol preparer completes two 35-minute tasks:

- one non-AI case and one AI-enabled case;
- one in SafeBARS and one in general LLM chat.

Use a computer-generated balanced schedule crossing:

- condition order;
- AI versus non-AI case;
- case variant; and
- task order.

Participants never see both variants of the same matched pair. The second task
uses a different context to reduce recall. Condition and case assignments are
stored in the study manifest before the participant starts and cannot be
changed through the interface.

The analysis includes order and AI-case indicators. A condition-by-order
interaction is a preregistered carryover diagnostic, not a new primary
hypothesis.

## 8. Protocol-preparer procedure

1. Verify consent and eligibility.
2. Assign a pseudonymous participant ID; never enter a real name in SafeBARS.
3. Complete a short background questionnaire.
4. Receive standardized task training on a practice case.
5. Record an initial five-minute risk and revision note for Task 1.
6. Start the assigned condition and the 35-minute timer.
7. Inspect the protocol, identify weaknesses, revise the research design,
   produce an application-oriented draft, and mark unresolved questions.
8. Submit the artifact and two decision rationales.
9. Complete post-task workload, perceived control, confidence, and trust items.
10. Repeat Steps 5-9 for Task 2.
11. Complete a 15-20 minute stimulated-recall interview focused on one accepted
    or edited suggestion and one rejected or deferred suggestion.
12. Debrief and remind the participant that neither output is ethics approval.

Expected duration: 95-110 minutes.

## 9. Expert-rating and triage procedure

### 9.1 Blinded artifact rating for RQ1

Normalize final artifacts into a condition-neutral format. Remove product
names, chat transcript labels, interface screenshots, and provenance metadata
not required by the rubric. Randomize artifact order.

Experts independently rate the artifact-quality rubric without seeing the
condition, participant identity, or sealed issue key. After rating, ask the
expert to guess the condition and state confidence; report this as a blinding
check.

Independent ratings are preserved. Do not replace them with a post-hoc
consensus score. Disagreement is analytically informative.

### 9.2 Counterbalanced handoff triage for RQ3

Each expert reviews four matched unresolved-question packets:

- two structured SafeBARS packets containing the cited passage, unresolved
  question, prior researcher decision, suggested expert role, and closure
  condition;
- two unstructured packets containing the corresponding protocol section and
  relevant chat material.

Counterbalance packet format, case, and order. Experts:

1. assign or redirect the issue;
2. request clarification if needed;
3. write a disposition and rationale;
4. identify what evidence is missing; and
5. indicate whether the issue can be closed.

Record time to first disposition, total time, clarifications, redirects,
evidence inspections, advice, confidence, and a short post-task interview.

## 10. Measures

### 10.1 Primary outcome

Blinded expert-rated artifact quality, calculated as the prespecified mean of
the four primary rubric dimensions in RQ1: completeness, safeguard specificity,
actionability, and evidence grounding. Each dimension uses behaviourally
anchored 1-5 ratings.

The rubric manual is trained on held-out artifacts. It is frozen before experts
see study outputs.

### 10.2 Secondary artifact outcomes

- number of consequential, non-duplicative issues addressed;
- number of planted issue families addressed;
- appropriate uncertainty and escalation;
- internal consistency;
- unsupported compliance or normative claims retained;
- appropriate unresolved questions and handoffs;
- contradictions introduced or removed; and
- application-field completeness.

The planted key measures response to authored omissions, not complete ethical
correctness.

### 10.3 Process outcomes

- time to first substantive revision;
- task completion time;
- number and type of revisions;
- source and provenance inspections;
- scenario traces opened;
- issues accepted, edited, rejected, or deferred;
- decision rationale completeness;
- LLM calls, errors, latency, and token usage;
- post-task workload;
- perceived control;
- confidence; and
- trust and appropriate-reliance items.

### 10.4 Expert-work outcomes

- time to first defensible disposition;
- total triage time;
- clarification requests;
- redirects;
- routing appropriateness;
- evidence sufficiency;
- consequential issues identified;
- low-value or duplicate issues;
- advice actionability; and
- confidence in provenance.

## 11. Data capture

Every study session must export a machine-readable manifest with:

- study ID;
- pseudonymous participant ID;
- consent confirmation timestamp;
- condition;
- case ID and variant;
- task and condition order;
- task start and completion timestamps;
- model manifest;
- prompt and source hashes;
- interaction events;
- generated outputs;
- researcher decisions;
- final artifacts;
- completion status; and
- software commit SHA.

Names, email addresses, institution names, and live confidential protocols are
not stored in the application database. Recruitment contact information is
kept separately from study data.

The production study database must be persistent, access-controlled, backed up,
and covered by a retention and deletion policy. Render `/tmp` storage is not
acceptable for formal data collection.

## 12. Analysis plan

### 12.1 General principles

- Freeze the analysis script and synthetic test fixture before unblinding
  condition labels.
- Report raw distributions and participant-level paired plots.
- Prioritize effect estimates and 95% confidence intervals.
- Distinguish the single primary outcome from secondary and exploratory
  analyses.
- Report null, mixed, and adverse findings.
- Do not interpret a rubric score as institutional approval.

### 12.2 RQ1 primary analysis

For each participant, average the independent expert ratings within condition
and compute the paired SafeBARS-minus-chat difference in composite artifact
quality. Report:

- condition means and distributions;
- mean paired difference;
- bias-corrected bootstrap 95% confidence interval; and
- standardized paired effect size with its interval.

The adjusted confirmatory model is:

`composite_score ~ condition + ai_case + order + (1|participant) + (1|case) + (1|rater)`

Use a linear mixed model for the prespecified composite after checking residual
diagnostics. Use a cumulative-link mixed model for dimension-level ordinal
ratings. The condition coefficient is the primary effect. The AI-case and order
terms control design variation; they are not additional primary claims.

### 12.3 RQ1 secondary analyses

Use generalized mixed models appropriate to the outcome:

- negative-binomial for overdispersed counts;
- logistic for binary outcomes;
- cumulative-link for ordinal ratings; and
- log-time linear mixed models for positively skewed duration.

If a model does not converge, report paired descriptive estimates and
bootstrap intervals instead of selecting a favourable alternative.

Apply false-discovery-rate control within each prespecified secondary outcome
family. Label all other tests exploratory.

### 12.4 RQ2 analysis

Code the two common decision records independently for exact-source
identification and an intelligible decision explanation. The prespecified RQ2
primary estimate compares, within participant, the proportion meeting both
criteria in each condition. Because each task contributes only two records,
report the paired raw 0, 0.5, and 1 distributions and a bootstrap interval; use
a binomial mixed model at decision-record level as a sensitivity analysis, not
as a replacement for the paired estimate.

Construct secondary participant-level process summaries for:

- source inspection;
- decision type;
- unsupported-advice retention;
- appropriate deferral;
- revision type; and
- rationale quality.

Compare conditions using paired estimation and the appropriate mixed models.
Integrate these results with stimulated-recall interviews using a joint display
that connects a logged action, artifact change, and participant explanation.

Interview data use reflexive thematic analysis. Two researchers collaboratively
develop themes, keep analytic memos, examine negative cases, and document how
their positions shaped interpretation. Do not report inter-rater reliability
for reflexive thematic analysis.

### 12.5 RQ3 analysis

Compare structured and unstructured expert packets using:

- paired time and clarification estimates;
- mixed models with packet format and order as fixed effects and expert and
  case as random intercepts;
- blinded ratings of routing, evidence sufficiency, and actionability; and
- thematic analysis of what experts refuse to delegate.

Do not claim workload reduction if faster triage is accompanied by lower issue
coverage or lower-quality advice.

### 12.6 Rating reliability

Report the intraclass correlation for the expert-rated composite under a
two-way random-effects, absolute-agreement model. Report both single-rater and
average-rater reliability. Preserve dimension-level distributions and
disagreements.

### 12.7 Missing data and exclusions

Before data collection, preregister:

- eligibility exclusions;
- withdrawal handling;
- minimum artifact required for an analyzable task;
- technical-failure and provider-outage rules;
- duplicate-session handling; and
- maximum allowable missing questionnaire items.

Do not impute the primary artifact score. Mixed models use available valid
ratings under their stated assumptions. Report attrition and missingness by
condition. Run a complete-pair sensitivity analysis and a sensitivity analysis
excluding sessions with material LLM failure.

## 13. Ethics and governance gate

No formative interview, pilot, main study, expert rating, or research logging
with participants begins until the current study has written institutional
approval, exemption, or another documented determination applicable to the
actual protocol.

Internal developer dry runs may test functionality without recruiting
participants or treating their behaviour as research data.

The participant materials must state:

- SafeBARS cannot provide institutional approval;
- outputs may be incomplete or wrong;
- fictional cases are used;
- interaction logs and generated content are recorded;
- how data are stored, retained, deleted, and accessed;
- how to withdraw; and
- whether any external LLM provider receives study text.

## 14. Preregistration and freeze package

Before the main study, freeze:

- RQ1-RQ3 and the primary estimand;
- sample-size target and calendar stopping rule;
- eligibility and exclusion rules;
- cases, variants, planted issue keys, and matching checks;
- counterbalancing schedule;
- conditions and baseline prompt;
- model and prompt manifest;
- feature set and commit SHA;
- expert rubric and training examples;
- task instructions and questionnaires;
- analysis models and fallbacks;
- missing-data rules; and
- anonymized data dictionary.

Record deviations with date, reason, decision-maker, and whether the change was
made before or after inspecting outcomes.

## 15. Interpretation boundaries

Supported claims may concern:

- artifact quality under the tested tasks;
- observed revision and reliance behaviour;
- traceability and handoff use;
- expert triage under the tested packets; and
- participant and expert experiences.

The study cannot establish:

- universal ethical correctness;
- committee acceptance;
- legal compliance;
- field safety;
- correctness for all institutions or domains;
- superiority of each SafeBARS component separately; or
- replacement of ethics reviewers, community partners, or participants.

## 16. Go/no-go checklist

The main study is **No-Go** unless all items are true:

- [ ] written ethics determination covers the final protocol;
- [ ] primary EvalLM blueprint and justified deviations are documented;
- [ ] Stage F or literature-grounded design rationale is complete;
- [ ] study build hides demo and development content;
- [ ] study manifest and event logging pass tests;
- [ ] persistent database, backup, retention, and deletion are configured;
- [ ] model, prompts, cases, rubric, and analysis are frozen;
- [ ] 2-3 internal dry runs pass without data loss;
- [ ] expert workflow requires a rationale and closure condition;
- [ ] condition-neutral artifact export passes a blinding check;
- [ ] counterbalancing schedule is generated; and
- [ ] preregistration is timestamped.

## 17. CHI paper evidence chain

The manuscript should follow:

1. **Formative grounding:** current practices and handoff needs.
2. **Design goals:** requirements derived from the formative evidence and
   literature.
3. **System:** SafeBARS features mapped one-to-one to those goals.
4. **Research questions:** claims made testable without claiming approval.
5. **Comparative study:** same-model, counterbalanced workflow comparison.
6. **Expert review:** blinded artifact ratings and handoff triage.
7. **Analysis:** paired estimation, mixed models, and qualitative explanation.
8. **Results:** RQ-by-RQ evidence, including null and negative findings.
9. **Discussion:** workflow contribution, appropriate reliance, expert
   allocation, limits, and transfer conditions.
