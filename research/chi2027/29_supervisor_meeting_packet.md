# Supervisor Meeting Packet

Last updated: 2026-06-16

## Project Direction

Working title:

SafeBARS: Bias-Calibrated Synthetic Stakeholders for Safer Action Research Planning

## Concrete Problem

Before doing online fraud prevention or other high-risk digital safety action research with vulnerable communities, researchers often need to test interview questions, workshop scripts, consent language, and safety procedures.

Directly testing rough materials with real affected participants can create ethical risks. Ordinary LLM persona role-play is also risky because it is hard to control and may miss issues such as shame, privacy concerns, institutional distrust, family pressure, distress, or participant burden.

## Core Idea

Inspired by CoBRA, SafeBARS uses controllable synthetic stakeholders with adjustable bias/risk-response profiles.

The system is not meant to replace real participants. It is meant to help researchers rehearse sensitive research plans before fieldwork and identify questions that must be verified with real participants or community partners.

## Tentative Research Question

Can bias-calibrated synthetic stakeholders help researchers identify ethical and safety risks before conducting high-risk digital safety action research with vulnerable communities?

## Why This Could Be CHI

- It addresses a timely HCI problem: researchers using LLMs to simulate or role-play stakeholders during research planning.
- It responds to concerns that synthetic users can flatten or misrepresent real groups.
- It adapts CoBRA's controllable-bias idea into a new setting: researcher-facing pre-fieldwork rehearsal.
- It contributes a system, a study, and design implications for responsible AI-assisted research preparation.

## Current Prototype

SafeBARS v0.1 is implemented locally.

It currently supports:

- Research plan input.
- Stakeholder role presets.
- Bias/risk-response sliders.
- Rehearsal chat.
- Optional LLM-backed response with fallback templates.
- Reflection report.
- Evidence notes from conversation.
- Revised research plan capture.
- JSON/Markdown export.

Prototype route:

```text
/safebars
```

Run:

```bash
python run_safebars.py
```

## Current Study Plan

First study:

Formative study with HCI/UX/AI safety/design research participants.

Basic flow:

1. Participant drafts an initial action research plan.
2. Participant uses SafeBARS to rehearse with synthetic stakeholders.
3. Participant reviews the reflection report.
4. Participant revises the research plan.
5. Participant completes a short interview.

Data:

- Initial plan.
- Interaction logs.
- Reflection report.
- Revised plan.
- Interview notes/transcript.

## What We Need to Decide

1. Is this problem original enough for CHI?
2. Should the paper mainly emphasize researcher reflexivity, trust calibration, or controllable stakeholder rehearsal?
3. Should online fraud be the main domain, or one example of broader high-risk digital safety research?
4. Is a formative study enough for the first submission, or should we plan a small comparison pilot?
5. Who should we recruit first: HCI students, UX researchers, AI safety researchers, or mixed early-career researchers?

## Immediate Next Step After Approval

If the framing is approved:

1. Polish prototype for study use.
2. Finalize ethics/consent materials.
3. Recruit pilot/formative study participants.
4. Run initial sessions after June 22.
5. Use findings to iterate the prototype and shape the CHI paper.

