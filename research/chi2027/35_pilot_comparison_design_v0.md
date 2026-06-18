# Pilot Comparison Design v0

Last updated: 2026-06-17

## Status

Backup study design for supervisor discussion. Use if we need stronger evidence after the formative study.

## Goal

Compare ordinary LLM brainstorming with SafeBARS for preparing high-risk digital safety action research plans.

## Core Question

Does SafeBARS help researchers identify more actionable ethical and safety risks than ordinary LLM-based brainstorming or role-play?

## Conditions

### Condition A: Ordinary LLM Brainstorming

Participants use a general LLM/chatbot to improve an online fraud prevention action research plan.

Suggested instruction:

"Use this chatbot to get feedback on your research plan, interview questions, workshop script, and safety procedures."

### Condition B: SafeBARS

Participants use SafeBARS to rehearse the plan with bias-calibrated synthetic stakeholders and generate a reflection report.

## Study Design Options

### Option 1: Between-Subjects

- Participants are assigned to either ordinary LLM or SafeBARS.
- Pros: avoids learning/carryover effects.
- Cons: needs more participants.

Recommended sample:

- 8-10 per condition, total 16-20.

### Option 2: Within-Subjects

- Each participant tries both tools on two comparable planning tasks.
- Pros: fewer participants needed.
- Cons: carryover effects likely.

Recommended sample:

- 8-12 participants.

Counterbalance task/tool order if used.

## Recommended Pilot Choice

Start with a small between-subjects pilot if recruitment is feasible.

If recruitment is hard, use a within-subjects design with counterbalanced tasks.

## Participant Population

HCI, UX, design research, CSCW, AI safety, or related graduate students/researchers.

## Task

Participants receive the same high-risk digital safety scenario:

"You are preparing an action research project about online fraud prevention for older adults in a community setting. You need to design interview questions, a workshop plan, and a safety procedure before entering the field."

They produce:

1. Initial plan.
2. Tool-assisted revision.
3. Final revised plan.
4. Short reflection/interview.

## Outcome Measures

### Artifact-Based Measures

Use pre/post coding framework:

- Stakeholder coverage.
- Privacy/data handling.
- Distress/safety protocol.
- Victim-blaming language reduction.
- Participant burden reduction.
- Consent clarity.
- Community benefit/follow-up.
- Trust calibration.
- Method feasibility.
- Overall revision quality.

### Process Measures

- Number of distinct risks identified.
- Number of concrete revisions.
- Whether participant mentions real participant/community verification.
- Whether participant treats AI output as evidence or as suggestion.

### Self-Report Measures

Likert items, 1-7:

- The tool helped me identify ethical risks.
- The tool helped me improve participant safety procedures.
- The tool helped me notice missing stakeholders.
- The tool helped me avoid potentially blaming language.
- The tool made the limits of AI-generated feedback clear.
- I would use this tool before sensitive fieldwork.

Open-ended:

- What was most useful?
- What was misleading or insufficient?
- What would you still need to verify with real people?

## Hypotheses / Expectations

This is exploratory, but expected patterns:

- SafeBARS participants will add more concrete safety and consent procedures.
- SafeBARS participants will identify more stakeholder relationships.
- SafeBARS participants will show stronger trust calibration language.
- Ordinary LLM participants may produce broader but less grounded suggestions.

## Data Analysis

Quantitative:

- Descriptive comparison of coded revision scores.
- If sample allows, compare condition means with non-parametric tests.

Qualitative:

- Thematic analysis of revised plans and interviews.
- Compare types of risk surfaced in each condition.

## Risks and Controls

Risk:

Participants may see SafeBARS as more authoritative because it looks structured.

Control:

Include limitation reminders in both instructions and interface.

Risk:

Ordinary LLM condition depends on model quality.

Control:

Use the same model family if possible, or describe it clearly as an ecological comparison.

Risk:

Small sample may not support strong statistical claims.

Control:

Frame as pilot evidence and focus on artifact-rich qualitative findings.

## Decision Criteria

Run this pilot if:

- Formative study suggests SafeBARS is usable.
- Supervisor wants comparative evidence.
- Recruitment for 12-20 participants is feasible.

Do not run this pilot yet if:

- Prototype needs major redesign.
- Ethics approval timeline is tight.
- The first paper can be framed as a design probe/formative system paper.

