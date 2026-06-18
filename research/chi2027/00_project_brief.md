# SafeBARS CHI 2027 Project Brief

Last updated: 2026-06-16

## Working Title

SafeBARS: Safe Bias-Aware Action Research Scaffolding with Bias-Calibrated Synthetic Stakeholders

## One-Sentence Pitch

SafeBARS uses bias-calibrated synthetic stakeholders as a pre-fieldwork rehearsal scaffold, helping HCI researchers prepare safer, more reflexive, and more accountable action research in high-risk digital safety contexts.

## Core Reframing

The current SafeGuard-AI prototype is an anti-fraud and AI ethics learning platform for end users. For CHI 2027, the stronger research direction is to reframe it as a researcher-facing system:

- Old framing: an AI anti-fraud education tool for learners.
- New framing: an AI-supported rehearsal scaffold for researchers planning high-risk action research.

The new framing avoids making synthetic agents a replacement for real people. Instead, synthetic stakeholders become controlled rehearsal partners that help researchers identify hidden assumptions, missing stakeholders, ethical risks, and safety gaps before entering the field.

## Research Problem

HCI researchers increasingly use LLMs to brainstorm, role-play, or simulate stakeholders during early-stage research planning. This is attractive in sensitive domains such as online fraud, AI safety, vulnerable communities, and digital literacy, where direct early contact with affected participants may be difficult or risky.

However, ordinary LLM personas have four problems:

1. They are hard to control.
2. They are hard to reproduce across models and prompts.
3. They may flatten or stereotype real groups.
4. They may give researchers false confidence before real fieldwork.

Inspired by CoBRA, this project asks whether bias and risk-response patterns can become measurable, adjustable abstractions for synthetic stakeholders used in pre-fieldwork rehearsal.

## Tentative Research Questions

RQ1. How can bias-calibrated synthetic stakeholders support researchers in preparing safer action research plans for high-risk digital safety contexts?

RQ2. What ethical risks, missing stakeholders, hidden assumptions, and participant-safety concerns can such a system help researchers surface?

RQ3. How do explicit bias profiles and limitation warnings affect researchers' trust calibration toward synthetic stakeholders?

## Proposed System

SafeBARS will include four modules:

1. Research Plan Input
   - Researchers enter a study goal, target community, planned methods, intervention idea, and safety concerns.

2. Bias-Calibrated Synthetic Stakeholders
   - The system generates stakeholder agents such as potential victim, family helper, community worker, platform moderator, skeptical participant, and authority figure.
   - Each agent has an adjustable bias or risk-response profile.

3. Rehearsal Interaction
   - Researchers interact with stakeholder agents to test interview questions, intervention scripts, consent language, and support procedures.

4. Reflection Dashboard
   - The system summarizes missing stakeholders, ethical risks, over-trust warnings, participant burden, safety protocol gaps, and recommended revisions.

## Candidate Bias and Risk-Response Dimensions

- Authority trust or authority pressure.
- Confirmation bias.
- Urgency or scarcity sensitivity.
- Shame and stigma sensitivity.
- Institutional trust or distrust.
- Social proof susceptibility.
- Help-seeking reluctance.
- Privacy sensitivity.
- Financial loss aversion.
- Trauma or distress sensitivity.

## Proposed Index

Working metric name: Stakeholder Risk Response Index (SRRI)

Scale: 0-4

- 0: minimal susceptibility or low-risk response.
- 1: mild hesitation or uncertainty.
- 2: moderate susceptibility under pressure.
- 3: strong susceptibility or high-risk response.
- 4: extreme vulnerability, avoidance, distress, or unsafe response.

SRRI is not intended to measure real human vulnerability. It measures controlled behavioral patterns in synthetic stakeholders for rehearsal and reflection.

## Expected Contributions

1. Problem contribution
   - Defines a new HCI problem: safe use of synthetic stakeholders for pre-fieldwork action research rehearsal.

2. Conceptual contribution
   - Introduces bias-calibrated synthetic stakeholders as controllable rehearsal partners rather than replacements for human participants.

3. System contribution
   - Implements SafeBARS, a scaffold for rehearsal, bias profile control, and reflection.

4. Empirical contribution
   - Shows through formative or pilot study how the system helps researchers revise research plans, identify risks, and calibrate trust.

5. Design implications
   - Offers guidance for building AI tools that support high-risk research preparation without epistemically replacing affected communities.

## CHI 2027 Fit

This project targets CHI themes around responsible AI, human-AI interaction, research ethics, participatory design, action research, AI-assisted design work, and digital safety.

Official CHI 2027 papers page:
https://chi2027.acm.org/authors/papers/

Key official dates from the CHI 2027 papers page:

- Submission site opens: 2026-07-30
- Full paper deadline: 2026-09-10 AoE
- No abstract deadline
- Reviews released: 2026-11-05
- Revision deadline: 2026-12-03
- Final notification: 2026-12-17

## Stage 1 Decision

Do not spend the next month building a larger end-user anti-fraud training platform. The first CHI-facing goal is to produce a strong problem framing, CoBRA transfer analysis, literature map, and prototype specification for a researcher-facing action research scaffold.

