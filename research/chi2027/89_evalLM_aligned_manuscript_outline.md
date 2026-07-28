# SafeBARS CHI Manuscript Blueprint

Status: current writing skeleton. Do not insert invented study results.

Primary structural blueprint: Kim et al., *EvalLM: Interactive Evaluation of
Large Language Model Prompts on User-Defined Criteria* (CHI 2024),
https://doi.org/10.1145/3613904.3642216.

Target length: approximately 7,500-8,000 words excluding references, captions,
and appendices. CHI 2027 encourages 5,000-8,000 words and desk-rejects
unjustified submissions above 12,000 words.

## Working title

**SafeBARS: Inspectable AI Scaffolding and Expert Handoffs for Preparing
Sensitive Research Protocols**

Do not put "ethical approval automation" in the title.

## One-sentence paper argument

Compared with a same-model general LLM chat, a structured workflow that grounds
issues in submitted passages, stress-tests participant encounters, records
researcher decisions, and defers situated questions to experts may improve
protocol-preparation artifacts and make reliance on AI more inspectable.

## Abstract: 180-220 words

Use five moves:

1. problem: preparing sensitive research protocols requires translating
   incomplete plans into operational safeguards;
2. gap: general LLM chat is fluent but weakly grounded and poorly bounded;
3. system: SafeBARS connects framework routing, provenance, encounter testing,
   contestation, and expert handoff;
4. method: same-model, within-subject comparison plus blinded artifact rating
   and expert triage;
5. findings and contribution: fill only after analysis, with estimates and
   uncertainty rather than promotional claims.

The abstract must say that SafeBARS does not grant or predict ethics approval.

## 1. Introduction: 750-900 words

### Paragraph 1: consequential preparation work

Explain why recruitment, consent, participation, data handling, distress,
withdrawal, follow-up, and AI governance must be operationalized before
participant contact.

### Paragraph 2: attraction and risk of general LLM assistance

Explain why researchers may use chat systems for drafting, and why fluent
advice can hide missing context, weak provenance, or institutional uncertainty.

### Paragraph 3: research gap

Existing work separately covers responsible-AI toolkits, ethics reflection,
interactive LLM evaluation, and qualitative-research concerns. The missing
workflow connects submitted evidence, encounter-level breakdowns, researcher
contestation, and qualified human escalation.

### Paragraph 4: SafeBARS

Introduce the three parties:

- protocol preparer;
- AI-supported workflow; and
- ethics, methods, safeguarding, data, community, or AI-governance expert.

### Paragraph 5: evaluation

State the same-model, counterbalanced comparison and linked expert review.

### Contributions

1. a literature- and formative-grounded design account of inspectable
   pre-submission ethics preparation;
2. SafeBARS, an integrated system for passage-grounded review, encounter
   stress-testing, researcher decisions, and expert handoff;
3. empirical evidence about artifact quality, revision and reliance, and
   expert triage under the tested tasks; and
4. design implications for AI systems that must stop and transfer authority.

Contribution 3 must be rewritten after results and may include null or adverse
findings.

## 2. Related work: 1,150-1,350 words

### 2.1 Ethics reflection and responsible-research toolkits

Use ESR, Belmont, Menlo, VSD, university guidance, and AI-era governance
frameworks. Explain why the frameworks are complementary rather than a
universal scoring formula.

### 2.2 Interactive AI support for evaluation and revision

Use EvalLM as the methodological anchor. Distinguish output evaluation from
protocol preparation and explain the adaptation from prompt revision to
research-plan revision.

### 2.3 LLMs in qualitative and sensitive research

Use *Simulacrum of Stories* and related work to motivate the non-replacement
boundary. SafeBARS does not generate participant testimony.

### 2.4 Human-AI contestation, uncertainty, and handoff

Review provenance, calibrated reliance, contestability, mixed-initiative work,
and escalation. End with the precise gap addressed by RQ1-RQ3.

## 3. Formative grounding and design goals: 700-850 words

Follow EvalLM's sequence from formative evidence to design requirements.

### 3.1 Participants and procedure

Report recruitment, roles, interview duration, questions, ethics determination,
and analysis. If no formative interviews were conducted, rename this section
"Literature-grounded design requirements" and do not invent participants.

### 3.2 Findings or requirements

Organize around work practices, missing context, evidence needs, escalation,
and decision authority.

### 3.3 Final design goals

- DG1: collect context without reproducing a long static form;
- DG2: route review through cited frameworks without presenting a score;
- DG3: connect every non-missing issue to submitted evidence;
- DG4: test encounter transitions and breakdowns before fieldwork;
- DG5: preserve accept, edit, reject, and defer decisions;
- DG6: stop and route questions that require situated authority;
- DG7: provide experts with concise, provenance-preserving packets.

Each design goal must cite formative or literature evidence and map to a system
feature.

## 4. SafeBARS: 1,250-1,450 words

### 4.1 Scope and non-approval boundary

State inputs, outputs, intended users, and prohibited claims.

### 4.2 Guided intake and pathway selection

Describe six core questions and conditional AI governance follow-up.

### 4.3 Framework-grounded review

Describe the framework selector, evidence states, missingness, and provenance.

### 4.4 Encounter map and bounded stress tests

Explain scenario generation, tools, dependencies, stop conditions, and reruns.

### 4.5 Researcher contestation and revision

Explain issue decisions, rationale, version history, and linked exports.

### 4.6 Expert handoff and workspace

Explain routing, assignment, clarification, advice, redirect, closure condition,
and review history.

### 4.7 Implementation and model use

Separate deterministic components from LLM-dependent components. Report the
frozen provider/model/configuration and failure behaviour.

### 4.8 Data governance

Describe pseudonyms, persistent storage, access roles, backup, deletion,
retention, and what is sent to an external model provider.

## 5. Technical validation: 450-600 words

Report only specification conformance:

- 21 fictional seeded cases;
- pathway and framework activation;
- passage provenance;
- planted missing dimensions;
- deterministic repeatability; and
- 126 executable checks.

Use the current reproducible figures and CSV manifest. State that this does not
establish ethical validity or user benefit.

## 6. Comparative study: 1,250-1,450 words

Mirror EvalLM's clear separation of research questions, participants,
conditions, tasks, procedure, and measures.

### 6.1 Research questions

Use exactly RQ1-RQ3 from the canonical protocol.

### 6.2 Participants

Report protocol preparers and expert reviewers separately, including inclusion
criteria, recruitment, compensation, experience, and aggregate demographics.

### 6.3 Conditions and frozen model

Explain SafeBARS versus same-model general chat, task and token parity, prompts,
model manifest, and why model quality is controlled.

### 6.4 Cases and counterbalancing

Explain matched AI/non-AI fictional cases, variants, sealed issue key, and the
balanced assignment schedule.

### 6.5 Procedure

Report practice, initial note, two timed tasks, final artifacts, post-task
measures, stimulated recall, expert rating, and expert triage.

### 6.6 Measures

Identify one primary artifact-quality outcome and label all other outcomes
secondary or exploratory.

### 6.7 Analysis

Report paired estimation, mixed models, reliability, missing-data rules,
multiple-comparison handling, reflexive thematic analysis, and integration of
logs, artifacts, and interviews.

## 7. Results: 1,350-1,650 words

Do not write results before the data freeze.

### 7.1 Sample, exclusions, and manipulation checks

Report flow, missingness, model failures, timing, condition blinding, and
carryover diagnostic.

### 7.2 RQ1: artifact quality

Lead with the primary paired estimate and interval. Follow with dimension-level
patterns, expert disagreement, and examples linked to the rubric.

### 7.3 RQ2: revision and reliance

Combine process measures with a joint display:

`logged action -> artifact change -> participant explanation`.

Include rejection, correction, and overreliance, not only successful examples.

### 7.4 RQ3: expert work

Report triage time together with issue coverage and advice quality. Faster is
not better if experts miss consequential issues.

### 7.5 Null, adverse, and boundary findings

Report where SafeBARS added burden, produced generic advice, encouraged false
confidence, or failed to support an expert decision.

## 8. Discussion: 1,050-1,250 words

### 8.1 From fluent advice to inspectable preparation

Interpret whether the workflow changed artifacts and why.

### 8.2 Designing AI systems that stop

Discuss epistemic handoff as transfer of authority, not an error state.

### 8.3 Allocating expert attention

Discuss what structured packets help with and what context remains irreducibly
human or institutional.

### 8.4 Comparison with EvalLM

Explain what transferred:

- within-subject comparison;
- revision as observable work;
- trust and interpretation;
- mixed quantitative and qualitative evidence.

Explain justified deviations:

- research protocols rather than prompts;
- same-model chat rather than manual evaluation;
- blinded external artifact ratings;
- expert handoff and triage; and
- explicit non-approval boundaries.

### 8.5 Design implications

Present implications supported by data, not generic principles.

## 9. Limitations: 350-450 words

Address:

- fictional cases;
- small and non-representative sample;
- institutional and jurisdictional specificity;
- model and provider dependence;
- bundled-feature design;
- possible condition unblinding;
- expert disagreement;
- short-term artifact outcomes rather than field safety; and
- no evidence of committee acceptance.

## 10. Conclusion: 150-200 words

Restate the bounded contribution and strongest supported finding. End with the
need for qualified review and situated engagement.

## Planned figures and tables

### Main figures

1. three-party workflow and authority boundaries;
2. design-goal-to-feature map;
3. technical provenance pipeline;
4. counterbalanced study design;
5. RQ1 paired artifact-quality estimation plot;
6. RQ2 revision and reliance joint display;
7. RQ3 expert-triage comparison.

### Main tables

1. related-work gap and SafeBARS response;
2. participant and expert characteristics;
3. conditions, controlled variables, and deviations from EvalLM;
4. artifact-quality rubric;
5. model, prompt, and study freeze manifest; and
6. quantitative estimates with intervals.

## Writing integrity rules

- Never convert technical-validation counts into user-study claims.
- Never describe demo sessions as participants.
- Never write placeholder findings in the past tense.
- Never claim approval, compliance, or ethical correctness.
- Preserve null results, disagreements, and counterexamples.
- Disclose AI assistance in writing as required by ACM policy.

