# SafeBARS Revised CHI Contribution, RQs, and MVP

Date: 2026-06-27

This memo converts the novelty collision audit into a buildable and study-ready CHI 2027 direction.

## Working Title

**Before We Meet: Agentic Encounter Stress-Testing for Sensitive Fieldwork Preparation**

Alternative:

**SafeBARS: From Synthetic Participants to Encounter Stress Tests for Sensitive Human-Facing Research**

## One-Sentence Problem

Before sensitive fieldwork, researchers can check whether a protocol contains consent or withdrawal language, but they still lack tools for rehearsing how relational and procedural breakdowns may unfold across recruitment, disclosure, pause, withdrawal, escalation, and follow-up.

## One-Sentence System

SafeBARS turns research materials into an encounter map, proactively traces bounded breakdown scenarios through that map, and helps researchers revise exact passages or hand unresolved questions to real stakeholders.

## One-Sentence Boundary

SafeBARS does not predict participants, provide ethics approval, or determine what a community needs; it produces contestable planning hypotheses about the researcher's own protocol.

## Core Conceptual Move

Move from:

> Simulate how a vulnerable participant might respond.

To:

> Stress-test how the research protocol is prepared to respond when a sensitive encounter changes direction.

The first claim requires a model of people. The second requires a visible model of the protocol, its responsibilities, and its missing response paths.

## Final Contribution Structure

### Contribution 1: Design framing

An epistemically bounded framing of agentic encounter stress-testing as a non-substitutive use of LLM agents before sensitive fieldwork.

This contribution explains:

- why generated stakeholder speech is not participant evidence;
- why formal compliance review and relational rehearsal are different tasks;
- why model uncertainty should create a real-person consultation task rather than a stronger simulation;
- why the protocol and researcher decisions, rather than synthetic responses, are the empirical objects.

### Contribution 2: Interactive system

SafeBARS, an artifact-centered agentic workflow with three defining interaction objects:

1. Encounter map: a structured view of planned stages, actors, actions, safeguards, and responsibility.
2. Breakdown trace: a scenario-specific path showing where the protocol can and cannot respond.
3. Epistemic handoff: an unresolved question assigned to a real stakeholder, partner, expert, or ethics reviewer with a reason AI cannot resolve it.

The system also includes passage-level provenance and an accept, edit, reject, or defer decision ledger.

### Contribution 3: Empirical findings

A study of how protocol preparers use, contest, and bound agentic critiques when revising sensitive human-facing materials.

The findings should focus on:

- which breakdowns become visible through scenario tracing;
- how users inspect provenance and agent scope;
- why users accept, modify, reject, or defer suggestions;
- where users preserve responsibility for real community engagement;
- when agent autonomy supports or obstructs reflective preparation.

### Contribution 4: Design implications

Design implications for non-substitutive agentic systems in high-stakes knowledge work, including:

- model the human-authored process before modeling people;
- make uncertainty actionable through handoff;
- preserve normative disagreement rather than synthesize false consensus;
- require passage-level decisions rather than passive report consumption;
- place human checkpoints around responsibility shifts, not merely after a fixed number of agent actions.

## Revised Research Questions

### RQ1: Breakdown discovery and revision

How do protocol preparers use agent-generated encounter traces to identify and revise relational and procedural breakdowns in sensitive fieldwork plans?

### RQ2: Contestability and reliance

How do provenance, agent scope, disagreement, and uncertainty shape users' decisions to accept, edit, reject, or defer agent-generated critiques?

### RQ3: Epistemic boundaries

How do protocol preparers distinguish issues that can be addressed through document revision from questions that require consultation with real participants, community partners, domain experts, or ethics reviewers?

Optional cross-domain RQ if the sample supports it:

### RQ4: Transfer

Which encounter stress-testing needs remain stable, and which differ, across academic HCI, qualitative social or health research, and applied UX or service research?

Do not include RQ4 if the final sample is too small or uneven for meaningful cross-group analysis.

## Minimum Viable Agent Team

Use four agents. More agents would add complexity without increasing the paper contribution.

### 1. Encounter Orchestrator

- parses submitted materials;
- proposes stages and actors;
- creates a visible scenario queue;
- asks the researcher to confirm scope;
- pauses when required information is absent.

### 2. Breakdown Scenario Agent

- selects a bounded adverse event;
- traces what happens through the encounter map;
- cites the protocol passage used at each step;
- stops at missing or ambiguous transitions;
- produces no claims about a population's likely behavior.

### 3. Relationship and Power Agent

- examines who can support, pressure, gatekeep, receive disclosure, or take responsibility;
- challenges assumptions around family, institutional, platform, and community roles;
- creates relationship-specific questions and scenario variants;
- does not generate demographic biographies.

### 4. Boundary, Revision, and Handoff Agent

- detects unsupported claims about communities;
- separates protocol text, inference, and unknowns;
- drafts passage-level revisions for triaged issues;
- turns unresolved knowledge into named handoff tasks;
- cannot save a revision without a human decision.

## Encounter Map Schema

Each stage should contain:

- stage ID and name;
- planned action;
- initiating actor;
- affected actor or relationship;
- source passage;
- expected transition;
- available pause, skip, withdrawal, or escalation route;
- responsible person;
- information collected or disclosed;
- unresolved assumptions.

Initial stages:

1. outreach and recruitment;
2. eligibility or gatekeeping;
3. information and consent;
4. arrival or onboarding;
5. interview, workshop, or activity;
6. sensitive disclosure;
7. pause, skip, or withdrawal;
8. safeguarding or escalation;
9. debrief and support;
10. follow-up, data use, and reporting.

The user can remove irrelevant stages and add domain-specific ones.

## Breakdown Trace Schema

- scenario title;
- triggering stage and event;
- why this scenario was selected;
- step sequence;
- protocol evidence at each step;
- actor responsible at each step;
- first missing, conflicting, or underspecified transition;
- potential consequence stated as a planning hypothesis;
- revision candidate;
- uncertainty note;
- real-person verification requirement;
- researcher decision.

## Initial Scenario Library

Build a small, transparent library instead of unconstrained scenario generation.

### Consent and autonomy

- a person agrees because a family helper is present;
- the participant wants to skip one activity but continue the session;
- withdrawal is requested after some data have already been recorded.

### Privacy and disclosure

- identifying financial or health information is disclosed unexpectedly;
- another stakeholder asks to see the participant's responses;
- the participant asks who can access recordings or transcripts.

### Distress and stigma

- a question produces visible discomfort or shame;
- a participant interprets wording as blame;
- the session surfaces an unmet support need.

### Trust and institutions

- the protocol assumes willingness to contact an authority or service;
- the participant distrusts the named reporting pathway;
- the community partner and research team disagree about escalation.

### Burden and access

- the planned session becomes too long;
- a participant cannot complete a required digital activity;
- compensation, travel, language, or accessibility assumptions fail.

Every scenario should be labeled as a test condition, not a prediction.

## Epistemic Handoff Schema

- question that remains unresolved;
- originating scenario and issue;
- why the AI cannot answer it;
- recommended real-world owner: participant group, community partner, domain expert, methods advisor, ethics reviewer, or institution;
- suggested consultation method;
- project stage by which it should be resolved;
- status and researcher notes.

This is the most important feature for differentiating SafeBARS from synthetic participants and automated ethics review.

## User Interface Priorities

### Primary workspace

Use a four-column or staged workspace:

1. Materials and encounter map;
2. Scenario queue and active trace;
3. Issue and evidence ledger;
4. Revision and handoff decisions.

### Required interactions

- inspect and edit the encounter map before running agents;
- choose scenario categories and scope;
- open the exact source passage for any agent claim;
- compare conflicting traces without a forced winner;
- accept, edit, reject, or defer each issue;
- convert an issue to a handoff task;
- export the revised protocol, decision ledger, and handoff list.

### Demote from the current interface

- free-form rehearsal chat;
- provider comparison as a main panel;
- generic Reflection Report;
- bias sliders described as psychological calibration;
- one large Revised Plan text box.

Provider comparison may remain in a developer or robustness view. It is not part of the main research contribution.

## Formative Comparative Study

Given the CHI deadline, use one study that provides both design insight and a direct chatbot comparison.

### Participants

Target 12-18 protocol preparers recruited by task experience across:

- academic HCI or UX;
- qualitative social, health, communication, or education research;
- applied UX, service, public-interest, or community research.

### Conditions

- General LLM chat: the participant asks a general-purpose LLM to review a protocol using a supplied neutral prompt.
- SafeBARS: the participant uses encounter mapping, scenario traces, decisions, and handoffs.

Use the same underlying model where technically possible so the comparison tests interaction and workflow rather than model brand.

### Materials

Use two matched fictional protocol packages and counterbalance condition order:

- online fraud research with older adults;
- a sensitive public-service or student-support research case.

Both packages should contain realistic but non-obvious gaps. Pilot the match with methods experts before the main study.

### Evidence

- risks and missing transitions identified;
- source passages inspected;
- revisions made;
- suggestions accepted, edited, rejected, or deferred;
- unsupported claims about communities;
- handoff tasks created;
- interaction traces and time;
- perceived control, workload, usefulness, and trust;
- think-aloud and interview accounts.

### Analysis boundary

Do not treat the number of issues as ethical quality. Analyze the nature, traceability, use, rejection, and consequences of issues and revisions.

## Small Technical Evaluation

Create 18-24 seeded protocol cases across three domains. Each case should contain one documented missing transition or boundary violation. Compare SafeBARS with a general LLM prompt on:

- valid source-passage references;
- detection of the seeded missing transition;
- unsupported identity or community claims;
- schema completion and agent failures;
- appropriate handoff generation;
- variation across repeated runs.

This does not validate ethics reasoning. It checks whether the implemented workflow behaves as specified.

## Two-Week Implementation Order

### Days 1-2: Data model and persistence

- protocol artifacts and passage IDs;
- encounter stages and transitions;
- scenarios and traces;
- issues, decisions, and handoffs;
- persistent SQLite session storage.

### Days 3-5: Encounter mapping

- parser for four artifact types;
- editable stage view;
- missing-stage prompts;
- scope confirmation.

### Days 6-8: Scenario tracing

- bounded scenario library;
- Orchestrator and Breakdown Agent;
- source-passage retrieval;
- missing-transition detection;
- structured trace output.

### Days 9-10: Boundary and handoff

- claim-type checks;
- unsupported-community-claim flags;
- handoff creation;
- agent stopping rules.

### Days 11-12: Revision decisions

- passage-level before and after text;
- accept, edit, reject, and defer controls;
- decision rationale;
- exports.

### Days 13-14: Study readiness

- standardized cases;
- deterministic fallback;
- event logging;
- boundary tests;
- responsive UI checks;
- two internal dry runs.

## Go/No-Go Criteria Before Recruitment

Do not begin the study until:

1. every agent output links to an input passage, a declared heuristic, or an explicit unknown;
2. the system never labels its output as participant evidence or ethics approval;
3. users can stop and scope every agent task;
4. unsupported community claims are visible and cannot silently enter revisions;
5. all revision proposals require an explicit human decision;
6. every unresolved issue can become a real-person handoff;
7. sessions persist across server restarts;
8. the full standardized task can be completed without free-form chat;
9. failure and unavailable-provider states are visible;
10. the study has institutional ethics approval.

## Supervisor-Facing Answer

The literature search changed the framing in an important way. Mirror already covers multi-agent ethics review, while Interview AI-ssistant and InterFlow cover AI support for interview preparation and execution. I therefore do not plan to claim novelty for protocol review or multiple agents. The revised gap is agentic encounter stress-testing before sensitive fieldwork: the system traces how recruitment, consent, disclosure, withdrawal, escalation, and follow-up can break down, links each issue to the researcher's materials, and turns questions that AI cannot answer into explicit consultation tasks for real stakeholders. I will build the encounter map, breakdown traces, and epistemic handoff as the minimum v2 contribution, then compare this workflow with a general LLM chat using fictional protocols.

## Final Decision

The project remains viable for CHI 2027 only if the prototype and study center on encounter breakdowns and epistemic handoff. A polished multi-agent ethics report or synthetic stakeholder chat would no longer provide sufficient originality.
