# SafeBARS v2: Broader Significance and Formative Study Plan

Date: 2026-06-27

Purpose: answer the supervisor's third question: how to enlarge the target population and significance without making the system or paper vague.

## The Narrow Framing Problem

The current framing targets HCI researchers who study vulnerable populations. This is a legitimate group, but it creates three problems:

1. recruitment may depend on a very small specialist network;
2. the contribution can appear tied only to online fraud and older adults;
3. reviewers may see the system as a niche rehearsal chatbot rather than a reusable research-workflow intervention.

The solution is not to claim that SafeBARS is for everyone. The solution is to define a broader shared task.

## Broader Shared Task

> Preparing and reviewing sensitive human-facing protocols before contact with participants, service users, or community members.

A protocol is sensitive when failure could create avoidable emotional, informational, relational, or procedural harm. Relevant factors include:

- discussion of trauma, stigma, health, disability, safety, or financial loss;
- collection of private or identifying information;
- unequal power or dependency;
- difficult consent, withdrawal, disclosure, or safeguarding decisions;
- involvement of family members, gatekeepers, institutions, or community partners;
- risk that researchers impose assumptions on people whose context they do not understand.

Online fraud research with older adults remains the first design case, but it is not the boundary of the contribution.

## Target User Definition

Recruit by task experience rather than discipline or job title.

### Primary inclusion criterion

A participant must have authored, adapted, facilitated, or reviewed at least one human-facing research, evaluation, consultation, or co-design protocol in the past two years.

### Relevant user groups

1. Academic HCI and UX researchers, including doctoral researchers and research staff.
2. Qualitative or mixed-method researchers in health, social science, communication, education, and related fields.
3. Applied UX researchers, service designers, public-sector evaluators, and community or nonprofit research staff.

### Secondary stakeholders

- research supervisors;
- ethics and governance support staff;
- community research coordinators;
- safeguarding or domain advisors.

Secondary stakeholders can provide expert walkthroughs, but the first main study should recruit people who actively prepare protocols so that all participants perform a comparable task.

## Boundaries of the Broader Framing

SafeBARS is not positioned as:

- automated ethics approval;
- legal, clinical, or safeguarding advice;
- a substitute for community review;
- a method for predicting participant behavior;
- a general-purpose document reviewer;
- a tool only for novice researchers.

The common object across domains is a protocol and its human-facing consequences.

## Four Layers of Significance

### 1. Methodological significance

SafeBARS explores pre-fieldwork reflection as a distinct stage of AI-assisted research. Most research tools focus on ideation, data collection, transcription, coding, or analysis. SafeBARS studies how AI can support inspection of plans before participant contact.

### 2. Human-AI interaction significance

The project investigates how agent autonomy can coexist with meaningful human control in a high-stakes knowledge task. It contributes design mechanisms for visible task planning, bounded roles, structured disagreement, uncertainty, escalation, and approval.

### 3. Ethical and epistemic significance

The system operationalizes non-replacement. It redirects generated perspectives away from claims about communities and toward questions, protocol edits, and consultation tasks that preserve the authority of real participants and partners.

### 4. Practical significance

Researchers and practitioners already draft recruitment messages, consent language, interview guides, workshop activities, and safety procedures. SafeBARS fits this existing work and aims to catch avoidable weaknesses before scarce participant or community time is used.

The defensible practical claim is improved preparation and auditability, not guaranteed ethical research.

## Evidence That the Audience Is Broader Than HCI

The CHI 2025 study *Large Language Models in Qualitative Research: Uses, Tensions, and Intentions* recruited 20 qualitative and mixed-method researchers across seven fields, including HCI, communication, political science, social work, sociology, anthropology, and psychology. It reports LLM use and concerns across data collection, analysis, recruitment materials, privacy, validity, bias, responsibility, and researcher control.

This supports a task-centered recruitment frame across disciplines. SafeBARS answers its call for intentional, transparent, contextual, participant-conscious LLM tools by focusing on a bounded pre-fieldwork task.

Community-based HCI work such as *Strangers at the Gate* also shows that access, rapport, and co-construction are central methodological work rather than implementation details. SafeBARS should therefore be presented as preparation for better real engagement, not a way to avoid it.

## Formative Study Objective

The first study will not test whether SafeBARS makes research objectively ethical. It will investigate:

- where protocol preparers see value or danger in agentic review;
- which agent tasks fit their existing practices;
- what information they need to understand and contest agent findings;
- which recommendations they accept, reject, edit, or defer;
- when the system should stop and hand a question to a real person;
- whether the workflow transfers across research and practice settings.

## Formative Research Questions

### F-RQ1: Workflow Fit

How do people who prepare sensitive human-facing protocols integrate an agentic audit into their existing planning and review practices?

### F-RQ2: Control and Contestability

What controls, provenance, and disagreement representations do users need to inspect, challenge, and act on agent-generated issues?

### F-RQ3: Boundaries and Handoff

How do users distinguish actionable protocol critiques from questions that require real participants, community partners, ethics reviewers, or domain experts?

### F-RQ4: Transfer

Which parts of the workflow remain useful across academic research, applied UX or service research, and health or social research contexts?

## Participant Plan

### Target sample

Target 12 participants, approximately four from each primary user group:

- 4 academic HCI or UX researchers;
- 4 qualitative or mixed-method researchers outside HCI;
- 4 applied UX, service, public-sector, or community research practitioners.

This is a feasible formative sample, not a representative survey. A smaller final sample should be justified through the depth and relevance of participation, not by claiming statistical power.

### Optional expert walkthroughs

Conduct two or three separate walkthroughs with ethics, community-engagement, or safeguarding advisors. Treat these as design feedback, not as part of the main comparative dataset unless the protocol explicitly includes them.

### Screening requirements

Participants should:

- have prepared or reviewed a relevant protocol within two years;
- be able to describe at least one sensitive or high-stakes consideration in their work;
- have enough English proficiency to review the study materials;
- not need to upload confidential participant data or an identifiable active protocol.

Prior use of LLMs should be recorded but not required.

## Recruitment Channels

- HCI, UX, communication, social science, education, and health research groups at the university;
- doctoral and postdoctoral researcher mailing lists;
- research-methods and ethics training groups;
- local UX research and service-design communities;
- public-interest, nonprofit, or community organizations that conduct consultation or evaluation;
- supervisor and collaborator networks, followed by controlled snowball recruitment.

The recruitment message should describe the task as protocol preparation, not as research on vulnerable people. This widens relevance without weakening the ethical framing.

## Study Materials

### Standardized case package

Use one fictional but realistic online-fraud research package containing:

- a recruitment message;
- consent language;
- six to eight interview questions;
- a workshop activity;
- a short safety and follow-up procedure.

Seed the package with subtle, not cartoonish, problems across privacy, shame, burden, withdrawal, family involvement, reporting, and follow-up. Do not disclose a fixed answer key to participants.

### Transfer prompts

Prepare two short alternate cases from different domains, for example:

- a student mental-health service interview;
- a public-benefits access co-design workshop.

These cases are used to discuss transfer, not to claim domain validation.

### Participant-owned examples

Participants may discuss an anonymized past example, but should not upload confidential protocols or participant data during the formative study.

## Session Procedure

Estimated duration: 70-80 minutes.

1. Background interview, 10 minutes: role, methods, recent protocol work, current review practices, and LLM experience.
2. Baseline protocol review, 10-12 minutes: inspect the standardized case without SafeBARS and record concerns or proposed changes.
3. SafeBARS audit planning, 5 minutes: inspect the artifact map and approve or edit the agent task queue.
4. Agentic audit and think-aloud, 20-25 minutes: review issue cards, inspect provenance and disagreements, pause or rerun agents, and triage findings.
5. Revision task, 10-12 minutes: accept, edit, reject, or defer proposed changes and create real-stakeholder handoff items.
6. Transfer and boundary interview, 15 minutes: compare the workflow with current practice and discuss use in the participant's own domain.

The baseline-first order is acceptable for formative discovery but cannot support strong causal claims. A later comparative evaluation should counterbalance conditions.

## Data to Collect

- participant background and relevant protocol experience;
- baseline concern list;
- screen and interaction recording, subject to consent;
- think-aloud and interview audio or transcript;
- audit-plan changes;
- agent task and error events;
- issue cards opened and inspected;
- accept, edit, reject, and defer decisions with reasons;
- before-and-after protocol passages;
- real-stakeholder handoff items;
- post-session usefulness, control, workload, and trust ratings;
- researcher field notes.

## Analysis Plan

### Artifact analysis

Code baseline concerns, agent-surfaced issues, final revisions, and handoff items using:

- risk category;
- source passage specificity;
- novelty relative to baseline;
- actionability;
- evidence or provenance inspected;
- researcher decision;
- unsupported community claim;
- real-world verification need.

Use counts descriptively to explain workflow patterns, not to claim ethical effectiveness.

### Qualitative analysis

Use reflexive thematic analysis focused on:

- perceived division of labor;
- appropriate and inappropriate autonomy;
- confidence and skepticism;
- contestability and control;
- cross-domain workflow fit;
- reasons for accepting, changing, rejecting, or deferring findings;
- perceived relationship to real participants and communities.

### Cross-group matrix

Compare themes and artifact patterns across the three user groups. The goal is to identify stable workflow needs and meaningful differences, not rank disciplines.

## Formative Success Criteria

The study supports continued development if:

1. participants from all three groups can map at least one agent task to a real preparation need;
2. issue cards lead to passage-specific decisions rather than only generic discussion;
3. participants use provenance, disagreement, or uncertainty information when deciding what to do;
4. the workflow produces both revisions and appropriate real-person handoffs;
5. users can explain why the system is not participant evidence or ethics approval;
6. findings identify concrete redesign requirements for a later evaluation.

These are design-learning criteria, not acceptance thresholds for a deployed safety system.

## Later Evaluation Direction

After the formative redesign, conduct a counterbalanced comparison between:

- a general-purpose LLM chat using a standard protocol-review prompt;
- SafeBARS v2 using the same protocol and underlying model where possible.

The comparison should examine traceability, revision quality, unsupported claims, real-stakeholder handoffs, control, workload, and calibrated reliance. This would directly test whether the agentic workflow adds value beyond a chatbot interface.

## Ethics and Data Protection

- Obtain institutional ethics approval before recruiting or recording participants.
- Use fictional standardized protocols in the main task.
- Do not collect real vulnerable-participant data.
- Ask participants not to paste confidential or identifiable materials.
- Store consent, recordings, interaction logs, and exports according to the approved data plan.
- Disclose model providers, transmitted data, retention assumptions, and failures.
- Provide a no-LLM or local-artifact alternative if required by institutional policy.

The ethics application should begin immediately because approval time is now a project-critical dependency.

## Schedule to CHI 2027

The official CHI 2027 full-paper deadline is September 10, 2026, with no separate abstract deadline. The following schedule leaves only a small writing buffer.

### June 28-July 5

- confirm framing and v2 requirements with the supervisor;
- prepare or amend the ethics application;
- finalize standardized cases, recruitment criteria, and study instruments;
- create a paper skeleton using the new contribution claim.

### July 6-July 19

- implement the complete v2 audit loop;
- add persistent study logging;
- run technical and boundary tests;
- conduct two or three internal pilot sessions.

### July 20-August 9

- recruit across the three groups after approval;
- conduct the first six to eight formative sessions;
- analyze data continuously and fix only study-blocking usability problems.

### August 10-August 20

- complete approximately 12 sessions;
- finish artifact coding and thematic analysis;
- produce final figures, tables, and findings structure.

### August 21-August 31

- complete the main paper draft;
- write limitations without overstating formative evidence;
- prepare anonymized supplementary materials and system video.

### September 1-September 9

- supervisor and coauthor revision;
- accessibility, anonymity, references, metadata, video, and supplement checks;
- submit before the September 10 AoE deadline.

## Sources

- CHI 2027 paper dates and requirements: https://chi2027.acm.org/papers/
- Large Language Models in Qualitative Research: https://doi.org/10.1145/3706598.3713120
- Simulacrum of Stories: https://doi.org/10.1145/3706598.3713220
- Strangers at the Gate: https://doi.org/10.1145/2675133.2675147
- Ethics and Society Review: https://doi.org/10.1073/pnas.2117261119

## Step 3 Decision

Position the project around sensitive human-facing protocol preparation, recruit across three groups that share this task, and use online fraud as the standardized formative case rather than the full boundary of the contribution.

The resulting CHI claim is broader but still coherent:

> SafeBARS demonstrates how bounded agentic systems can support inspectable, contestable, and non-substitutive preparation for sensitive human-facing work.
