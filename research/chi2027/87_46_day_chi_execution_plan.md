# SafeBARS 46-Day CHI 2027 Execution Plan

Date range: 27 July 2026 to 10 September 2026 AoE  
Status: controlling execution plan for the current ethics-preparation and
human-handoff direction  
Supersedes for scheduling purposes:
`03_two_month_plan.md` and the schedule in
`73_significance_and_formative_study_v2.md`

## 1. Deadline and non-negotiable boundary

The official CHI 2027 Papers page states that the full paper, video, and
supplementary-material deadline is **Thursday, 10 September 2026, Anywhere on
Earth (AoE)**:

https://chi2027.acm.org/authors/papers/

This plan uses **9 September as the internal submission deadline**. The final
AoE day is failure-recovery buffer, not a normal writing or analysis day.

No recruitment, consent, pilot/soft-launch session, expert rating, interview,
or other research-participant data collection may begin until the team holds a
written institutional decision that the current protocol is approved or exempt.
The decision must cover:

- protocol preparers as participants;
- expert reviewers/raters as participants, if their judgments are research data;
- collection of task artefacts, interaction logs, questionnaires, interviews,
  and ratings;
- the named LLM provider and any data transmitted to it;
- recording, transcription, retention, withdrawal, and anonymization; and
- recruitment channels and compensation, if any.

Internal software tests conducted only by the research team may continue before
approval. Feedback from colleagues or advisors must not be treated as research
data unless it is covered by the institutional decision and consent.

## 2. Study decision

Run one compact formative requirements check followed by **one within-subject,
counterbalanced comparative study**. Do not add a separate pilot and a second
main experiment. The first two comparative sessions are a preregistered soft
launch within the main study.

### Conditions

- **SafeBARS:** the full structured workflow, including framework routing,
  passage-grounded checks, encounter stress tests, contestable revisions, and
  explicit human handoff.
- **General LLM chat:** free chat using the same model/provider, source material,
  time limit, and neutral task instruction.

### Counterbalancing

Prepare four matched fictional protocols:

- non-AI variants A1 and A2; and
- AI-enabled variants B1 and B2.

Each participant sees one non-AI case and one AI-enabled case, one in each
condition, and never sees both variants of a matched pair. Freeze eight balanced
sequences crossing condition order, AI/non-AI order, and case variant. With 24
completed sessions, each sequence receives three participants.

Assignment must be generated and frozen before the first participant. Do not
change assignments in response to observed outcomes.

### Sample and stopping rule

- Recruitment target: **24 protocol preparers**.
- Minimum analyzable comparative sample: **16 participants with both tasks
  completed**, balanced as closely as possible across the eight sequences.
- Expert panel target: **6 qualified reviewers**, with two independent,
  blinded ratings for every final artefact.
- Stop at 24 complete protocol-preparer sessions or at the end of 18 August,
  whichever occurs first.
- Do not increase or stop the sample because one condition appears better.

The target is a feasibility-constrained, estimation-focused CHI study, not a
claim of universal effectiveness. A simple paired-test sensitivity calculation
shows that 24 completed pairs provide approximately 80% power only for a
standardized within-participant effect of about 0.60; smaller effects remain
uncertain, and the preregistered mixed model plus interval estimates control
the actual analysis. EvalLM is a useful methodological precedent for
comparative evaluation of an interactive LLM tool using user-defined
criteria, but its sample size is **not** a power justification for SafeBARS:

Kim et al. (2024), *EvalLM: Interactive Evaluation of Large Language Model
Prompts on User-Defined Criteria*, CHI 2024.
https://doi.org/10.1145/3613904.3642216

### Session

Plan a 95-110 minute session:

1. information, consent, and background questionnaire: 10 minutes;
2. task 1: 35 minutes;
3. task 2: 35 minutes;
4. post-task measures and stimulated-recall interview: 15-20 minutes.

The study evaluates ethics-preparation work, not institutional approval. It must
not ask participants to submit personal or live confidential protocols.

## 3. Frozen primary and secondary outcomes

### Primary outcome

Blinded expert-rated **ethics-preparation quality** of the final artefact. Before
data collection, define behaviourally anchored rubric items for:

- application-information completeness;
- safeguard specificity and operational detail;
- evidence traceability;
- actionability of revisions;
- appropriate uncertainty and handoff; and
- unsupported normative/compliance claims, reverse scored.

The preregistration must state whether these items form one composite or are
treated as separate outcomes. Do not decide after inspecting condition results.

### Secondary outcomes

- task-completion time and time to first substantive revision;
- retained consequential issues and revisions;
- correctly routed and sufficiently evidenced handoffs;
- unsupported AI statements retained;
- clarification requests required by expert reviewers;
- perceived control, usefulness, workload, and trust;
- accept, edit, reject, and defer actions; and
- qualitative explanations of revision, contestation, and reliance.

### Analysis boundary

Receiving university ethics approval is not an outcome. Raw issue count alone
is not an ethics-quality measure. Seeded technical cases establish software
conformance, not ethical correctness or user benefit.

## 4. Roles

Replace each placeholder with a named person on 27 July.

| Role placeholder | Responsibility |
|---|---|
| `[Student researcher / study lead]` | daily coordination, sessions, logs, paper integration |
| `[Supervisor / PI]` | framing, ethics decision, go/no-go authority, claim review |
| `[Prototype owner]` | study build, version lock, defect triage, reproducibility |
| `[Recruitment coordinator]` | approved recruitment, scheduling, tracking, compensation |
| `[Coder A]` and `[Coder B]` | independent coding, codebook audit, disagreement record |
| `[Expert-rating lead]` | blinded packets, rater calibration, completeness checks |
| `[Statistician / methods advisor]` | preregistered analysis and sensitivity checks |
| `[Paper lead]` | section owners, figure/table integration, submission package |
| `[All authors]` | final claims, anonymization, disclosure, and submission sign-off |

One person may hold multiple roles, but every dated deliverable needs one named
accountable owner.

## 5. Entry and exit gates

| Gate | Latest date | Entry condition | Exit evidence | Failure action |
|---|---:|---|---|---|
| G0 Direction lock | 27 Jul | supervisor meeting available | signed one-paragraph contribution, RQs, single-study decision, named owners | stop feature expansion; resolve framing that day |
| G1 Ethics route | 29 Jul | current protocol and data flow described | submission receipt or existing written approval/exemption mapped to the exact study | no participant contact or data collection |
| G2 Approval go/no-go | 3 Aug preferred; 7 Aug absolute | written institutional decision received | approval/exemption ID, approved versions, conditions logged | switch to no-human-data fallback; do not run an informal study |
| G3 Material/preregistration freeze | before participant P001 | G2 passed; dry runs completed | timestamped preregistration, commit/hash manifest, counterbalance list | delay P001; no verbal freeze |
| G4 Soft-launch QA | 10 Aug | first two consented sessions completed under frozen protocol | complete paired artefacts/logs, no blocking defect, masking works | pause; document change, seek amendment if needed |
| G5 Recruitment sufficiency | 18 Aug | approved recruitment active | target 24 or minimum 16 complete paired sessions with acceptable balance | narrow claims to feasibility/qualitative evidence; no powered-effect claim |
| G6 Rating/coding completeness | 25 Aug | masked packets and transcripts complete | two expert ratings per artefact; qualitative double-coding quota met | add raters/coding time; delay results freeze, not standards |
| G7 Analysis freeze | 29 Aug | clean data, deviations, exclusions and ratings complete | read-only analysis dataset, scripts, output manifest, commit/tag | results remain provisional and cannot enter final claims |
| G8 Full-paper freeze | 1 Sep | all sections and figures present | complete 5,000-8,000-word target draft with limitations and disclosures | cut secondary analysis; do not sacrifice verification |
| G9 Submission ready | 8 Sep | author review complete | validated PDF, video, supplement, metadata and anonymization checklist | use 9 Sep for repair |
| G10 Internal submission | 9 Sep | PCS package passes inspection | uploaded files opened and independently checked | 10 Sep AoE is emergency recovery only |

## 6. Dated execution schedule

### 27 July — reset and ownership

**Deliverables**

- Freeze the current contribution around inspectable ethics preparation,
  encounter stress-testing, contestability, and epistemic handoff.
- Confirm RQ1-RQ3; keep cross-domain transfer secondary.
- Replace all role placeholders with names.
- Open one risk register covering ethics, recruitment, expert availability,
  provider stability, analysis, and submission.

**Owner:** `[Supervisor / PI]`, `[Student researcher / study lead]`  
**Entry:** current prototype and controlling plan available  
**Exit:** G0 passed

### 28-29 July — ethics and study-protocol alignment

**Deliverables**

- Convert the current research plan into the institution's protocol,
  participant-information, consent, recruitment, data-management, withdrawal,
  and debriefing documents.
- Remove superseded synthetic-stakeholder/older-adult study wording.
- Document LLM data transfer, retention assumptions, fallback behaviour, and
  prohibition on live confidential protocols.
- Obtain submission receipt or map an existing approval/exemption to the exact
  current study in writing.

**Owner:** `[Student researcher / study lead]`, `[Supervisor / PI]`  
**Entry:** G0  
**Exit:** G1

### 28 July-2 August — writing and technical work in parallel

**Deliverables**

- Draft current Introduction, Related Work, Contribution, System, and Technical
  Evaluation sections.
- Integrate the existing reproducible technical figures without calling them
  human validation.
- Produce Fig. 1 system/evidence workflow and Fig. 2 study design.
- Freeze provider/model candidate and verify logging of model, version,
  temperature, prompt, timestamp, errors, and retries.

**Owner:** `[Paper lead]`, `[Prototype owner]`  
**Entry:** G0  
**Exit:** complete non-results paper spine and reproducible technical package

### 30 July-2 August — internal dry runs and matched-case check

**Deliverables**

- Run 2-3 full browser-based internal dry runs by research-team members only.
- Verify 95-110 minute timing, export, masking, counterbalance assignment,
  recovery from provider failure, and withdrawal/deletion workflow.
- Ask advisors acting as collaborators, not research participants, to check case
  realism and rubric wording; do not analyze their comments as study data.
- Revise the matched cases so issue opportunity and task burden are comparable,
  while not identical.

**Owner:** `[Prototype owner]`, `[Student researcher / study lead]`  
**Entry:** study build and draft materials available  
**Exit:** no blocking defect; dry-run log and case-match memo complete

### 3-7 August — approval, preregistration, and total material freeze

**Deliverables**

- Pass G2 by 3 August if possible; 7 August is the absolute deadline.
- If G2 passes by 3 August, run the approved compact formative requirements
  check with six people: three protocol preparers and three ethics, methods,
  data, safeguarding, community, or AI-governance reviewers.
- Complete rapid framework analysis and a feedback-to-design change log by
  6 August. Only study-blocking terminology, instrumentation, case realism,
  rubric, and handoff-packet changes are permitted.
- If the formative phase cannot be completed before the freeze, describe the
  design goals as literature-grounded and supervisor-informed; do not invent or
  retrospectively label formative findings.
- Timestamp the preregistration before P001.
- Freeze and hash:
  - approved protocol, information sheet, consent, recruitment and debrief;
  - RQs, primary/secondary outcomes and directional hypotheses;
  - cases and hidden seeded-issue key;
  - neutral general-chat prompt and SafeBARS instructions;
  - model/provider/version/temperature and retry policy;
  - counterbalance sequence;
  - task timing and questionnaires;
  - expert rubric, masking rules and held-out calibration examples;
  - exclusions, missing-data rules, stopping rule and deviation policy;
  - coder manual and analysis-script skeleton.
- Archive a manifest containing the Git commit and SHA-256 hashes.

**Owner:** `[Supervisor / PI]`, `[Methods advisor]`, `[Prototype owner]`  
**Entry:** G2 and completed dry runs  
**Exit:** G3

### 4-18 August — approved recruitment and scheduling

Recruitment may start only after G2. Schedule the eight sequences evenly. Track
screening, consent, completion, withdrawal and sequence without storing
unnecessary identifiable information with study data.

**Owner:** `[Recruitment coordinator]`  
**Entry:** G2  
**Exit:** target 24 or recruitment close on 18 August

### 8-10 August — soft launch inside the single main study

Run P001-P002 under the frozen, approved main protocol. This is an operational
soft launch, not a separate formative sample.

- Do not inspect condition differences.
- Include the sessions only under the preregistered inclusion rule.
- If only wording/instruction clarification changes, log the deviation.
- If cases, outcomes, timing, data flow, or core interaction changes, pause,
  consult the ethics route, version the protocol, and apply the preregistered
  exclusion rule to pre-change sessions.

**Owner:** `[Student researcher / study lead]`, `[Prototype owner]`  
**Entry:** G3  
**Exit:** G4

### 10-18 August — main data collection

- Run the remaining paired sessions.
- Complete same-day completeness checks without scoring outcomes by condition.
- Store consent keys separately from pseudonymous study artefacts.
- Write a session memo and deviation log within 24 hours.
- Permit only study-blocking fixes; freeze all analytic behaviour.

**Owner:** `[Student researcher / study lead]`  
**Entry:** G4  
**Exit:** G5

### 8-18 August — Methods and System writing in parallel

- Complete Participants, Apparatus, Cases, Conditions, Procedure, Measures,
  Ethics, Data Management and Analysis Plan using frozen materials.
- Complete the System section with implementation provenance and limitations.
- Create empty result-table shells; do not write expected findings as results.

**Owner:** `[Paper lead]`, `[Methods advisor]`, `[Prototype owner]`  
**Entry:** G3  
**Exit:** Methods and System ready for coauthor review by 18 August

### 10-24 August — blinded expert rating

- Recruit and consent expert raters under G2.
- Train on held-out examples, not study artefacts.
- Normalize and mask final artefacts so interface formatting does not reveal
  condition.
- Assign every artefact to two independent raters.
- Preserve original ratings and rationales; adjudication must not overwrite
  disagreement.
- Report inter-rater reliability appropriate to the scale. If reliability is
  weak, show rater-level distributions and sensitivity analyses rather than
  silently averaging.

**Owner:** `[Expert-rating lead]`  
**Entry:** G3; first masked artefacts available  
**Exit:** all assigned ratings complete by 24 August

### 19-25 August — data cleaning and double coding

- Freeze a raw, read-only export and generate the analysis dataset by script.
- Validate participant IDs, counterbalance cells, timestamps, exclusions,
  missing data, provider errors and rating coverage.
- Coder A and Coder B independently code all primary artefact outcomes.
- Double-code a stratified minimum of 30% of interviews across both conditions,
  task orders, and AI/non-AI case families; refine the qualitative codebook
  with an audit trail, then code
  the remainder without erasing alternative interpretations.
- Record deviations and exclusions before condition results are opened.

**Owner:** `[Coder A]`, `[Coder B]`, `[Methods advisor]`  
**Entry:** data collection closed  
**Exit:** G6

### 26-29 August — analysis and result freeze

Primary analysis:

- show participant-level paired observations;
- estimate the condition difference with confidence intervals;
- account for case and order; use a participant random intercept only if the
  model is supported by the achieved sample and diagnostics;
- report effect sizes and uncertainty, not significance alone; and
- run preregistered sensitivity analyses for rater disagreement, exclusions and
  provider failures.

Integrated analysis:

- connect logs and interview evidence to accepted, edited, rejected and deferred
  issues;
- analyze expert triage, clarification and handoff quality;
- report negative, null and failure findings; and
- keep cross-domain patterns descriptive unless the achieved sample supports
  comparison.

Freeze the clean dataset, scripts, tables, figures and manifest at G7.

**Owner:** `[Methods advisor]`, `[Coder A]`, `[Coder B]`, `[Paper lead]`  
**Entry:** G6  
**Exit:** G7

### 26 August-1 September — Results and Discussion writing

- Fill result shells only from frozen outputs.
- Write findings around preparation quality, revision/contestation, calibrated
  handoff and expert work.
- Distinguish technical conformance, participant outcomes and expert judgments.
- State limits from sample, fictional cases, institution, model/provider and
  short-term task context.
- Complete the abstract only after results and contributions are stable.

**Owner:** `[Paper lead]`, `[All authors]`  
**Entry:** verified analysis outputs  
**Exit:** G8 on 1 September

### 2-5 September — author review and claim audit

- Supervisor/coauthors review the complete paper, not isolated sections.
- Trace each abstract/contribution claim to a table, figure, quote or technical
  artefact.
- Remove causal, ethical-correctness, institutional-acceptance and workload
  claims that the achieved evidence cannot support.
- Check the CHI word limit, accessibility and disclosure requirements against
  the current official Papers page.

**Owner:** `[Supervisor / PI]`, `[All authors]`  
**Entry:** G8  
**Exit:** author sign-off by 5 September

### 6-8 September — submission package

- Anonymize paper, supplement, repository references, screenshots, metadata and
  video.
- Package approved study materials, preregistration link, rubric, masked data
  excerpts, analysis scripts, technical-figure manifest and README.
- Add alt text and verify grayscale/colour-blind readability.
- Document AI assistance and data/provider use accurately.
- Build and open the final PDF on a second machine or account.
- Upload a complete draft package by 8 September.

**Owner:** `[Paper lead]`, `[All authors]`  
**Entry:** author sign-off  
**Exit:** G9

### 9 September — internal submission deadline

- Perform an independent PCS inspection.
- Download and open every uploaded file.
- Verify title, author metadata, PDF, video, supplement, anonymity and
  disclosures.
- Record submission confirmation.

**Owner:** `[Student researcher / study lead]`, `[Supervisor / PI]`  
**Entry:** G9  
**Exit:** G10

### 10 September AoE — emergency buffer only

Use only for failed upload, corrupt file, metadata error or a conference-system
problem. Do not schedule new analysis, major rewriting, study sessions or author
debate on this day.

## 7. Go/no-go branches

### Branch A — written approval/exemption by 3 August

Proceed with the full plan. Begin approved recruitment immediately, freeze by
7 August, and protect the 18 August data-collection close.

### Branch B — written approval/exemption arrives 4-7 August

Proceed only if at least 16 eligible participants and 4 expert raters can be
scheduled by the hard close. Keep the study estimation-focused and cut
secondary and exploratory analyses before compressing rating, analysis or
writing.

### Branch C — no written decision by 7 August

Do not collect participant data. Reframe the submission as a system,
framework-grounding and technical-conformance paper only if the supervisor
believes that contribution is sufficient. Otherwise select a later venue.
Never replace approval with informal recruitment, demo telemetry, colleague
feedback, fabricated expert identity, or retrospective consent.

### Branch D — fewer than 16 paired completions by 18 August

Report the work as feasibility/qualitative evidence with participant-level
distributions. Do not claim a reliable comparative effect or use a complex
powered model. Preserve null and negative evidence.

### Branch E — expert ratings incomplete or unreliable

Do not substitute LLM ratings for the expert panel. Report rater disagreement,
use sensitivity analyses, narrow the claims, and move unverified outcomes out of
the abstract and contribution list.

## 8. Paper production map

| Paper output | Evidence/source | Owner | Due |
|---|---|---|---:|
| Abstract and contributions | frozen results and claim map | `[Paper lead]` | 1 Sep |
| Introduction and Related Work | literature and current problem framing | `[Paper lead]` | 2 Aug draft |
| System and workflow figure | production build and provenance | `[Prototype owner]` | 2 Aug |
| Technical evaluation | seeded cases, CSV, manifest, current figures | `[Prototype owner]` | 5 Aug |
| Study design figure | frozen counterbalance and procedure | `[Methods advisor]` | 8 Aug |
| Methods | approved and preregistered materials | `[Methods advisor]` | 18 Aug |
| Comparative estimation figure | frozen paired analysis | `[Methods advisor]` | 29 Aug |
| Handoff/expert-work figure or table | blinded expert ratings | `[Expert-rating lead]` | 29 Aug |
| Results | frozen tables, figures and coded evidence | `[Paper lead]` | 31 Aug |
| Discussion and limitations | achieved evidence and failure cases | `[All authors]` | 1 Sep |
| Supplement and reproducibility README | materials, scripts, manifest | `[Prototype owner]` | 6 Sep |
| Anonymized video | frozen study build | `[Student researcher / study lead]` | 7 Sep |
| PCS-ready package | all verified artefacts | `[All authors]` | 8 Sep |

## 9. Daily control

From 27 July through 9 September, maintain a five-minute daily log:

- deliverable completed yesterday;
- deliverable due today;
- active blocker and owner;
- current gate status;
- ethics/recruitment/session/rating counts without outcome peeking;
- paper sections and figures in red/amber/green status; and
- decision needed within 24 hours.

Hold twice-weekly 20-minute go/no-go reviews with the supervisor. Any task that
does not advance an exit gate, study integrity, paper evidence, or submission
quality is deferred until after 10 September.
