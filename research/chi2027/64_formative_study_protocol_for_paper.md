# Formative Study Protocol for Paper Draft

Draft v0, 2026-06-19

Purpose: convert the SafeBARS paper idea into an executable formative study that can later become the Methods section.

## Study Goal

The formative study evaluates whether SafeBARS helps researchers identify and revise ethical, emotional, and procedural risks in sensitive online-fraud-prevention research plans.

The study does **not** evaluate whether synthetic stakeholders accurately represent older adults, fraud victims, or vulnerable communities.

## Research Questions

### RQ1

How do researchers use bias-calibrated synthetic stakeholders to identify ethical, emotional, and procedural risks in sensitive fieldwork plans?

### RQ2

How does SafeBARS shape revisions to interview questions, workshop scripts, consent language, and safety procedures?

### RQ3

What forms of trust calibration are needed to help researchers treat synthetic stakeholder responses as rehearsal prompts rather than participant evidence?

## Participants

Target participants:

- HCI researchers;
- design researchers;
- UX researchers;
- graduate students who have designed or reviewed user studies;
- researchers with interest in digital safety, vulnerable communities, or qualitative methods.

Planned sample:

- 6-8 participants for initial formative study.

Inclusion criteria:

- age 18+;
- experience with interview, workshop, survey, participatory design, or user-study planning;
- comfortable reading and writing in English for the study task.

Exclusion criteria:

- no prior experience with research planning or design evaluation;
- direct conflict of interest with the project.

## Apparatus

Participants will use the SafeBARS web prototype.

Core system components:

- structured research-plan input;
- stakeholder preset selection;
- bias/risk-response profile controls;
- rehearsal chat;
- LLM-backed responses when configured;
- provider comparison;
- reflection report;
- revised-plan capture;
- export function.

## Task Scenario

Participants will be asked to improve a sensitive fieldwork plan:

> You are preparing a study about online fraud prevention with older adults at a community center. The study includes interviews followed by a workshop. The current plan asks participants how much money they lost, why they believed suspicious messages, and what they would do differently. Your task is to rehearse this plan, identify possible risks, and revise it before real fieldwork.

This scenario is intentionally imperfect so that participants have meaningful issues to discover.

## Procedure

Estimated duration: 45-60 minutes.

### Step 1: Introduction and Consent

The researcher explains:

- the study evaluates SafeBARS as a research-preparation tool;
- synthetic stakeholder responses are fictional;
- participants are not being evaluated for expertise;
- they may skip any question or stop at any time.

### Step 2: Pre-Tool Plan Review

Participant reads the initial research plan and writes:

- risks they already notice;
- questions they would revise;
- what safety procedures they would add.

This creates a baseline artifact.

### Step 3: SafeBARS Walkthrough

The researcher briefly explains:

- research plan panel;
- stakeholder preset;
- bias/risk-response profile;
- rehearsal chat;
- provider comparison;
- reflection report;
- revised plan.

### Step 4: Rehearsal Task

Participant uses SafeBARS to ask at least two rehearsal prompts, such as:

- "Would you be comfortable if I ask how much money you lost?"
- "Does this consent explanation feel clear?"
- "Would a two-hour workshop feel too burdensome?"
- "What might make you distrust this study?"

Participant may adjust stakeholder profiles if they want to test different concerns.

### Step 5: Provider Comparison

Participant runs Compare Providers on one important prompt.

Prompt to participant:

> Look across the provider responses. What risks appear consistently? What risks appear in only one provider? Does this change your trust in the synthetic stakeholder output?

### Step 6: Reflection Report

Participant generates a reflection report and reads the recommended revisions.

Prompt to participant:

> Which report items are useful? Which are generic or questionable? What would you still need to verify with real stakeholders?

### Step 7: Revised Plan

Participant writes a revised plan in the Revised Plan panel.

Required structure:

- issue noticed;
- revision to make;
- remaining question for real stakeholders.

### Step 8: Post-Study Interview

Interview topics:

- what SafeBARS helped them notice;
- what the synthetic stakeholder missed;
- whether any response felt too authoritative or misleading;
- how provider comparison affected trust;
- what they would use or not use in real fieldwork preparation;
- what should be changed before deploying this tool to research teams.

## Data Collected

Artifacts:

- pre-tool risk notes;
- initial research plan;
- SafeBARS session log;
- provider comparison output;
- reflection report;
- revised plan.

Interview data:

- audio recording or notes;
- post-study interview transcript or summary.

Optional observations:

- moments when participants revise prompts;
- moments when participants question model output;
- moments of overtrust or skepticism.

## Analysis Plan

### Artifact Analysis

Compare pre-tool and post-tool plan artifacts.

Code whether the revised plan adds or improves:

- privacy/data boundary language;
- consent explanation;
- skip/pause/withdrawal options;
- distress support;
- non-blaming wording;
- participant-burden reduction;
- stakeholder map;
- community-partner verification;
- follow-up resources;
- questions for real fieldwork.

### Interaction Log Analysis

Code rehearsal turns for:

- risk type surfaced;
- stakeholder role used;
- profile dimensions relevant to response;
- whether researcher followed up;
- whether response led to plan revision.

### Interview Analysis

Use thematic analysis to identify:

- perceived usefulness;
- trust calibration;
- overtrust concern;
- generic or unhelpful responses;
- desired system changes;
- boundaries participants want between rehearsal and evidence.

## Possible Measures / Counts

These are not statistical claims, but useful descriptive indicators:

- number of risks identified before SafeBARS;
- number of additional risks identified after SafeBARS;
- number of concrete revisions in final plan;
- number of revisions linked to privacy, consent, distress, burden, or stakeholder coverage;
- number of times participants mention that real stakeholders must verify an issue;
- provider comparison risks surfaced per provider.

## Ethics and Risk Mitigation

The study uses researchers as participants, not older adults or fraud victims.

Risk mitigation:

- use a fictional research-plan scenario;
- avoid asking participants about personal fraud experiences;
- remind participants that synthetic responses are not evidence;
- collect only necessary study artifacts;
- anonymize participant names and institutions;
- allow participants to skip questions or stop.

## Expected Findings Categories

Findings may be organized as:

1. **From direct questions to safer wording:** participants revise questions about financial loss or belief to reduce shame and blame.
2. **From vague consent to concrete data boundaries:** participants add explanation of recording, anonymization, and access.
3. **From single-user framing to stakeholder ecosystem:** participants add family helpers, community workers, or institutions.
4. **From model trust to calibrated skepticism:** provider comparison makes participants more cautious about treating responses as evidence.
5. **From chat output to research artifact:** reflection reports help transform conversation into revised plans.

## What Would Count as Success

The formative study would support the paper if participants:

- identify risks they did not initially mention;
- revise plans in concrete ways;
- treat synthetic responses as prompts rather than evidence;
- articulate what still requires real stakeholder input;
- find the system useful enough for pre-fieldwork preparation while recognizing its limits.

## What Would Count as Failure or Limitation

Important negative findings:

- participants overtrust synthetic stakeholder responses;
- responses are too generic to support revision;
- participants treat provider comparison as a ranking of truth;
- the tool distracts from real community engagement;
- the interface is too complex for early-stage research planning.

These failures would still be valuable CHI findings if analyzed honestly.

