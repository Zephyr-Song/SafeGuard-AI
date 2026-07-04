# SafeBARS v3 Direction: Three-Party, Framework-Grounded Ethics Preparation

Date: 2026-07-04

Status: revised project direction following supervisor feedback. Phase 1 implementation has started in the current encounter workspace.

## Revised Product Sentence

SafeBARS is a framework-grounded ethics-preparation and review workspace in which researchers develop an ethics-application draft and ethically informed research design, bounded AI agents inspect and stress-test the materials, and appropriate human experts review only the sensitive or situated questions that require their authority or knowledge.

The system prepares an application package. It does not issue ethics approval, certify compliance, or replace an institutional review board.

## Why the Direction Changed

The prior version treated the researcher as the only primary user and treated handoff as an exported list. The supervisor feedback identifies a stronger sociotechnical system:

1. Handoffs should have real recipients and a review workflow.
2. Busy ethics experts should focus on high-sensitivity questions rather than reread every AI output.
3. The current encounter map and stress test should become an intermediate stage rather than the complete product.
4. A conversational intake stage should help researchers provide complete, structured information before analysis.
5. The system should be grounded in cited ethics and responsible-AI frameworks.
6. Connected ethical choices and value tensions should be visualized without turning ethics into one numerical score.
7. The system should produce different work products for researchers and expert reviewers.

## Three Parties

### 1. Standard user: researcher or project designer

Relevant users include academic researchers, doctoral students, UX researchers, service designers, public-sector evaluators, and community research staff who need to prepare a human-facing study or intervention.

They need to:

- understand which information an ethics application requires;
- develop recruitment, consent, activity, safety, data, and follow-up procedures;
- recognize risks and value tensions early enough to redesign the study;
- create an application draft and supporting documents;
- know which issues require expert or community consultation;
- track advice and revisions before formal submission.

### 2. Expert user: reviewer or situated advisor

“Expert” is not one universal role. Handoffs must be routed by question type and authority.

Possible reviewers include:

- university ethics committee members or ethics administrators;
- school or faculty research-governance representatives;
- research-methods advisors;
- data protection or information-security officers;
- safeguarding, clinical, accessibility, or domain experts;
- AI governance or model-risk experts;
- community partners or participant advisory groups.

An institutional ethics expert can advise on review expectations and research protections, but cannot answer every situated question. Questions about local trust, community priorities, acceptable support pathways, or lived consequences may require a community partner or participant representative.

Experts need to:

- receive a prioritized queue rather than a complete unfiltered report;
- see the exact source passage, scenario, AI inference, uncertainty, and researcher decision;
- advise, request clarification, redirect, or close a handoff;
- review the researcher-facing application package;
- inspect a summary of AI assistance and prior expert advice;
- preserve an accountable review trail.

### 3. AI agents

AI agents are bounded process actors, not approval authorities or simulated committee members.

Their responsibilities include:

- scaffold information collection;
- map answers to structured application fields;
- select relevant framework modules;
- identify missing evidence and connected value tensions;
- plan and execute bounded encounter stress tests;
- draft revision options and application language;
- route unresolved questions to the correct human role;
- summarize decisions without claiming consensus or approval.

## Revised End-to-End Workflow

### Stage 0: Role and institutional setup

The user identifies:

- researcher or expert role;
- institution, school, and review pathway;
- applicable form or template;
- project type, jurisdiction, and study status;
- available expert and community contacts.

Institution-specific form support must be implemented through versioned adapters. A generic draft must never be presented as a complete institutional submission.

### Stage 1: Conversational, structured intake

The SafeBARS Intake Assistant asks one question at a time and populates structured fields for:

- project purpose and method;
- direct and indirect stakeholders;
- use of AI, ICT, or sensitive data;
- recruitment and eligibility;
- consent and withdrawal;
- interview questions and activities;
- foreseeable harms and safeguards;
- data access, retention, deletion, and reporting;
- follow-up and support;
- known expert contacts and unresolved questions.

Chat is appropriate here because the task is progressive elicitation. The output is not a conversation transcript alone: every answer must populate an inspectable field with provenance. The assistant can request clarification and offer framework-derived hints when an answer is incomplete.

### Stage 2: Framework routing and ethics map

SafeBARS activates a cited framework stack based on the project:

- Belmont is the human-subject research baseline.
- Menlo is added for ICT and data-centered research.
- NIST AI RMF is added when the project builds, evaluates, studies, or uses AI.
- Value Sensitive Design supports stakeholder and value-tension analysis.
- Ethics and Society Review informs researcher reflection and expert-panel iteration.

The system maps submitted evidence to framework questions. It reports documented, partial, or missing evidence—not ethical compliance scores.

### Stage 3: Encounter stress testing

The current SafeBARS workflow becomes the intermediate analysis stage:

- encounter map;
- inspectable audit plan;
- bounded breakdown scenarios;
- passage-grounded traces;
- relationship and power checks;
- structured specialist-boundary contestation;
- accept, edit, reject, or defer decisions.

### Stage 4: Handoff and expert review

Each handoff contains:

- unresolved question;
- originating framework dimension, scenario, and issue;
- exact source passages;
- why AI lacks authority or context;
- recommended reviewer role;
- sensitivity, urgency, and project deadline;
- researcher’s current position;
- expert advice, status, and rationale;
- links to resulting revisions.

The router should distinguish at least:

- institutional ethics and methods;
- consent, recruitment, and inclusion;
- privacy, data governance, and security;
- safeguarding or clinical support;
- accessibility;
- AI governance and model risk;
- community knowledge and local service feasibility.

### Stage 5: Revision and dual output

Researcher output:

1. ethics-application draft mapped to the selected institutional template;
2. ethically informed research-design protocol;
3. participant information and consent draft;
4. recruitment and inclusion plan;
5. risk, safeguarding, and escalation plan;
6. data-management summary;
7. AI-use disclosure and AI-risk appendix when applicable;
8. decision, handoff, and expert-advice log;
9. interpretation boundary and submission checklist.

Expert output:

1. prioritized handoff queue;
2. one-page case summary per project;
3. high-sensitivity passages and unresolved decisions;
4. framework coverage and value-tension view;
5. researcher decisions and AI assistance history;
6. expert advice, requests, redirects, and closure status;
7. aggregate summary across assigned applications.

## Cited Framework Stack

### Belmont Report

Use for respect for persons, beneficence, and justice, operationalized through consent, risk-benefit assessment, and fair participant selection.

Source: National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research. *The Belmont Report* (1979). https://www.hhs.gov/ohrp/regulations-and-policy/belmont-report/read-the-belmont-report/

### Menlo Report

Use as an ICT and data-centered extension of Belmont, including respect for law and public interest and attention to people or organizations indirectly affected by ICT research.

Source: Dittrich, D., and Kenneally, E. *The Menlo Report: Ethical Principles Guiding Information and Communication Technology Research* and companion guidance (2012). https://www.dhs.gov/sites/default/files/publications/CSD-MenloPrinciplesCOMPANION-20120103-r731_0.pdf

### NIST AI Risk Management Framework 1.0

Use only when AI is part of the research object, method, intervention, analysis, or participant-facing experience. Its Govern, Map, Measure, and Manage functions provide an operational AI-risk extension, not an ethics-approval standard.

Source: Tabassi, E. *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* (2023). https://doi.org/10.6028/NIST.AI.100-1

### Value Sensitive Design

Use for direct and indirect stakeholder analysis and for representing value tensions through conceptual, empirical, and technical investigations. VSD supports deliberation; it does not mechanically rank values.

Source: Friedman, B., Kahn, P. H., and Borning, A. “Value Sensitive Design and Information Systems” (2013), with later methods consolidated by Friedman and Hendry (2019). https://doi.org/10.1007/978-94-007-7844-3_4

### Ethics and Society Review

Use as process inspiration for researcher-authored risk and mitigation statements followed by iterative feedback from an interdisciplinary expert panel, especially for wider societal and AI impacts.

Source: Bernstein, M. S. et al. “Ethics and Society Review: Ethics Reflection as a Precondition to Research Funding” (2021). https://doi.org/10.1073/pnas.2117261118

## Visualization Design

The framework is cited; the interface visualization is a SafeBARS design contribution.

### Ethics Dandelion

- center: the submitted research protocol;
- inner or radial petals: active cited framework dimensions;
- petal color: documented, partial, or missing submitted evidence;
- click interaction: framework question, source passages, uncertainty, and linked handoffs;
- optional outer nodes: expert owners and unresolved decisions.

This visualization must be described as evidence coverage, not ethical quality.

### Value-Tension Explorer

Initial tensions include:

- narrow recruitment criteria versus equitable reach;
- rich data versus privacy and data minimization;
- AI automation versus human oversight;
- standardization versus contextual adaptation;
- early stopping for safety versus participant autonomy;
- open reporting versus confidentiality and group harm.

Sliders do not calculate a morally optimal answer. They externalize a provisional design position, show connected framework principles and stakeholders, and require a written rationale. Users should be able to compare alternatives rather than collapse ethics into one score.

### Handoff Network

Future visualization:

- issue nodes connected to framework dimensions;
- owner nodes grouped by institutional, domain, data, safeguarding, AI, and community expertise;
- edge state showing requested, viewed, redirected, advised, resolved, or overdue;
- filtering by project stage and sensitivity.

## Handoff Prioritization

Do not prioritize only by an LLM severity label. Priority should be a transparent combination of:

- potential magnitude and reversibility of harm;
- proximity to participant contact;
- uncertainty and missing context;
- institutional or legal authority required;
- whether the choice changes inclusion, consent, data rights, safety, or research purpose;
- whether a real stakeholder has already been consulted;
- deadline in the research lifecycle.

AI can suggest routing. A human researcher or administrator confirms the owner.

## Research Contribution

The contribution is no longer only encounter stress testing. The stronger research object is a three-party division of ethical labor:

> How should bounded AI agents scaffold ethics preparation, expose connected value tensions, and route high-sensitivity questions so researchers remain responsible and scarce human experts focus attention where their authority and situated knowledge are most needed?

Potential contributions:

1. a framework-grounded interaction model joining structured intake, protocol stress testing, and epistemic handoff;
2. a three-party workflow for allocating work among researchers, AI agents, and heterogeneous expert reviewers;
3. Ethics Dandelion and Value-Tension Explorer visualizations for inspectable deliberation without false scoring;
4. empirical findings on handoff quality, expert attention allocation, researcher understanding, and changes to research design;
5. design implications for agentic systems that prepare high-stakes documents without claiming approval authority.

## Evaluation Direction

### Formative study

Recruit both roles:

- 10-15 researchers or protocol preparers across academic and applied domains;
- 4-6 ethics, methods, data, safeguarding, accessibility, AI-governance, or community experts.

Study the complete loop:

1. researcher completes guided intake;
2. researcher inspects the framework and trade-off views;
3. agents run encounter traces;
4. researcher decides or creates handoffs;
5. expert reviews a prioritized subset;
6. researcher revises and exports the application draft.

### Comparison

Compare against a general-purpose LLM chat using the same case and, where possible, the same model. Examine:

- application-field completeness;
- passage and framework traceability;
- unsupported ethical or community claims;
- quality and correctness of handoff routing;
- expert time and proportion spent on consequential issues;
- researcher understanding and revision quality;
- unresolved uncertainty preserved rather than hidden;
- perceived control, workload, and usefulness.

Do not evaluate success by approval rate or number of issues alone.

## Implementation Phases

### Phase 1: Framework-grounded intake and visualization

- [x] guided conversational intake that populates structured fields;
- [x] explicit AI-use routing control;
- [x] Belmont, Menlo, NIST AI RMF, VSD, and ESR source registry;
- [x] conditional framework assessment;
- [x] Ethics Dandelion evidence map;
- [x] initial interactive value-tension controls;
- [ ] persist trade-off positions and rationales;
- [ ] add framework-derived clarification hints to the server-side event log.

### Phase 2: Expert handoff workflow

- [x] expert-role taxonomy and routing rules;
- [x] handoff assignment, redirect, advice, request, resolve, and reopen actions;
- [x] expert review page and prioritized queue;
- [x] explicit expert-advice-to-researcher-revision linkage;
- [ ] external researcher/expert notification;
- [x] session-scoped researcher/expert capability tokens and API authorization;
- [x] expert invitation rotation and revocation;
- [x] browser-session researcher resume and expert invited-case overview;
- [x] protocol version creation that preserves prior human review;
- [x] append-only review event logging.

### Phase 3: Application drafting

- [x] generic ethics-application draft schema and Word export;
- [x] generic human-research and AI-enabled application profiles;
- [x] field-level missing/partial/documented completeness checks;
- [ ] adapter for a named institution's current official form;
- [ ] standalone participant information and consent-document generator;
- [x] data, safeguarding, AI-use, and mitigation sections in the generic draft;
- [x] expert summary Word export;
- [x] unresolved-handoff and field-level submission-readiness statement;

### Phase 4: Study readiness

- [ ] persistent production database;
- [x] prototype session-level role authorization;
- [ ] institution-managed identity, account recovery, and multi-case expert authorization;
- [ ] encryption, retention, deletion, and provider-disclosure controls;
- [ ] expert validation of mappings and routing;
- [ ] standardized human-subject, ICT, and AI research cases;
- [ ] institutional ethics approval for the SafeBARS study itself.

## Non-Negotiable Boundaries

- Never label an application “approved,” “compliant,” or “safe.”
- Never fabricate an expert review, community view, or institutional requirement.
- Never route every situated question to a university ethics board; use the appropriate authority or community owner.
- Never reduce ethical acceptability to a single score.
- Never silently include generated text in a submission.
- Preserve framework version, source, model assistance, human decisions, expert advice, and unresolved uncertainty in the audit trail.
