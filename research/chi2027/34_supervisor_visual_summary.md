# SafeBARS Supervisor Visual Summary

Last updated: 2026-06-17

## One-Line Idea

SafeBARS helps researchers rehearse sensitive fieldwork plans with bias-calibrated synthetic stakeholders before working with real vulnerable communities.

## Concrete Problem

Researchers preparing online fraud prevention action research need to test interview questions, workshop scripts, and safety procedures before fieldwork.

But:

- Testing rough materials with vulnerable participants can be ethically risky.
- Ordinary LLM persona role-play is uncontrolled.
- Generic personas may miss shame, privacy concerns, institutional distrust, family pressure, distress, or participant burden.

## CoBRA-Inspired Move

CoBRA:

Natural-language personas are unreliable, so agent behavior needs measurable and controllable bias abstractions.

SafeBARS:

Use adjustable stakeholder risk-response profiles as rehearsal controls for research planning.

Examples:

- privacy sensitivity
- shame/stigma sensitivity
- institutional distrust
- help-seeking reluctance
- distress sensitivity
- participant burden sensitivity

## System Workflow

```text
Initial research plan
        ↓
Choose synthetic stakeholder
        ↓
Adjust bias/risk-response profile
        ↓
Rehearse interview or workshop plan
        ↓
Generate reflection report with evidence
        ↓
Revise research plan before real fieldwork
```

## Prototype Status

SafeBARS v0.1 currently supports:

- Research plan input.
- Stakeholder presets.
- Bias sliders.
- Rehearsal chat.
- Optional LLM response with template fallback.
- Reflection report with evidence notes.
- Revised plan capture.
- JSON/Markdown export.

Local route:

```text
http://127.0.0.1:5050/safebars
```

## Example

Initial researcher question:

> How much money did you lose and what mistake did you make?

Affected participant response:

> This wording feels uncomfortable because it sounds like you already think I did something wrong.

Reflection report flags:

- potential victim-blaming
- privacy concern
- distress risk
- need for skip/pause options
- need to verify with real participants

Revised plan:

> Ask what made the message seem trustworthy at the time. Add skip options, privacy explanation, recording choices, and support resources.

## Proposed Study

Participants:

HCI/UX/AI safety/design research students or researchers.

Flow:

1. Draft initial action research plan.
2. Use SafeBARS to rehearse with synthetic stakeholders.
3. Review reflection report.
4. Revise plan.
5. Interview about usefulness, risks, and trust calibration.

Data:

- initial plan
- interaction logs
- reflection report
- revised plan
- interview notes/transcript

## Possible CHI Contribution

1. A problem framing for synthetic stakeholders as rehearsal aids, not participant replacements.
2. A system for bias-aware pre-fieldwork research scaffolding.
3. Findings on how researchers identify ethical/safety risks and revise plans.
4. Design implications for responsible AI-assisted research preparation.

## Decisions Needed From Supervisor

1. Is this problem original enough for CHI?
2. Should the paper emphasize researcher reflexivity, trust calibration, or controllable stakeholder rehearsal?
3. Should online fraud be the main domain or one example of broader high-risk digital safety?
4. Is a formative study enough, or should we plan a small comparison pilot?
5. Who should we recruit first?

