# CHI Paper Outline v1

Last updated: 2026-06-16

## Working Title Options

1. SafeBARS: Bias-Calibrated Synthetic Stakeholders for Safer Action Research Planning
2. Rehearsing Before the Field: Bias-Aware Synthetic Stakeholders for High-Risk Digital Safety Research
3. Not Participants, Not Proxies: Calibrating Synthetic Stakeholders for Reflexive Fieldwork Preparation

## Current Preferred Title

SafeBARS: Bias-Calibrated Synthetic Stakeholders for Safer Action Research Planning

## One-Sentence Thesis

SafeBARS explores how bias-calibrated synthetic stakeholders can help researchers rehearse high-risk action research plans, surface ethical and safety risks, and calibrate trust before engaging real participants.

## Abstract Skeleton

Researchers increasingly use LLMs to brainstorm, role-play, and prepare user research. In sensitive domains, such as online fraud prevention with vulnerable communities, early rehearsal can be useful but risky: ordinary synthetic personas are hard to control, may flatten lived experience, and may give researchers false confidence before fieldwork.

We present SafeBARS, a bias-aware action research scaffolding system that uses fictional synthetic stakeholders with adjustable risk-response profiles. Rather than treating synthetic stakeholders as participant replacements, SafeBARS frames them as bounded rehearsal aids for surfacing assumptions, safety gaps, missing stakeholders, and trust-calibration issues.

We describe the design of SafeBARS and report a formative study with researchers using the system to rehearse digital safety action research plans. Findings show how bias-calibrated stakeholder rehearsal can support reflexive planning while also revealing limits and risks of synthetic stakeholder use.

We discuss design implications for AI tools that prepare researchers for, rather than replace, real community engagement.

## Contribution Statement Draft

This paper contributes:

1. A problem framing for synthetic stakeholders as pre-fieldwork rehearsal aids rather than participant replacements.
2. SafeBARS, a researcher-facing system combining stakeholder roles, adjustable risk-response profiles, rehearsal chat, reflection reporting, and trust-calibration reminders.
3. Empirical findings from a formative study showing how researchers use SafeBARS to identify ethical risks, missing stakeholders, and safety gaps in high-risk digital safety research plans.
4. Design implications for responsible AI tools that support reflexive and accountable research preparation.

## 1. Introduction

### Opening Problem

HCI researchers increasingly use LLMs in research planning. They may ask ChatGPT to role-play participants, critique interview questions, or simulate stakeholder reactions.

This is especially tempting in sensitive domains:

- Online fraud prevention.
- AI safety education.
- Work with older adults or vulnerable communities.
- Digital privacy and harm recovery.

But this creates a problem:

- Ordinary LLM personas are plausible but uncontrolled.
- They may miss shame, privacy, distress, institutional distrust, or family dynamics.
- They may flatten real communities.
- They may create false confidence before real fieldwork.

### Gap

Prior work shows LLM agents can simulate behavior and that controllability matters. Other work warns that synthetic participants can misrepresent identity groups. However, less is known about how to design AI systems that use synthetic stakeholders safely as bounded rehearsal aids for research preparation.

### Proposed Approach

SafeBARS:

- Uses fictional synthetic stakeholders.
- Gives them adjustable risk-response profiles.
- Supports researcher rehearsal.
- Generates reflection reports.
- Emphasizes limitation and trust calibration.

### Research Questions

RQ1. How can bias-calibrated synthetic stakeholders scaffold researchers' preparation for high-risk action research?

RQ2. What assumptions, missing stakeholders, ethical risks, and safety gaps do researchers surface through SafeBARS rehearsal?

RQ3. How do explicit bias profiles and limitation-aware reflection reports shape researchers' trust calibration toward synthetic stakeholder outputs?

## 2. Related Work

### 2.1 LLM Agents and Controllable Social Simulation

Discuss:

- Generative Agents.
- CoBRA.
- LLM-simulated users and reliability concerns.

Argument:

Believable agents are not enough; controlled and bounded use matters.

### 2.2 Synthetic Participants and Replacement Risks

Discuss:

- LLMs replacing human participants can flatten identity groups.
- AI replacing human subjects debates.
- Synthetic users in UX/HCI.

Argument:

SafeBARS explicitly rejects participant replacement.

### 2.3 Participatory and Action Research

Discuss:

- Participatory/action research principles.
- Participatory AI.
- Design fictions as rehearsal or value exploration.

Argument:

AI tools should help researchers prepare for better engagement, not bypass engagement.

### 2.4 Digital Safety and Online Fraud as a High-Risk Context

Discuss:

- ROLESafe.
- Phishing education studies.
- Older adults and digital fraud.
- Intergenerational scam support.

Argument:

Online fraud prevention is a useful test context because it involves privacy, shame, family dynamics, trust, and distress.

### 2.5 Trust Calibration in Human-AI Systems

Discuss:

- Guidelines for Human-AI Interaction.
- Trust calibration with LLMs.
- Interface support for appropriate reliance.

Argument:

SafeBARS must help researchers avoid over-trusting synthetic stakeholders.

## 3. Formative Design Motivation

Optional depending on study sequence.

Could include:

- Initial analysis of CoBRA.
- Existing SafeGuard-AI prototype.
- Design goals derived from literature.

Design goals:

DG1. Make stakeholder assumptions explicit.

DG2. Support controlled variation in stakeholder risk-response patterns.

DG3. Help researchers identify ethical and safety risks.

DG4. Make limitations of synthetic rehearsal visible.

DG5. Produce artifacts for pre/post research plan comparison.

## 4. SafeBARS System

### 4.1 Overview

Describe workflow:

1. Research plan input.
2. Stakeholder selection.
3. Bias/risk-response profile adjustment.
4. Rehearsal chat.
5. Reflection report.
6. Revised plan capture.

### 4.2 Stakeholder Roles

Initial roles:

- Affected participant.
- Family helper.
- Community worker.

Optional/future:

- Platform representative.
- Authority figure.
- Skeptical participant.

### 4.3 Bias and Risk-Response Profiles

Dimensions:

- privacy sensitivity.
- shame/stigma sensitivity.
- institutional distrust.
- help-seeking reluctance.
- authority trust.
- distress sensitivity.
- participant burden sensitivity.

Boundary:

These are functional rehearsal controls, not psychological measures.

### 4.4 Rehearsal Interaction

Template/fallback mode plus optional LLM-backed responses.

Important:

- Synthetic stakeholders are fictional.
- Responses include rehearsal signals.
- System discourages replacing real participant engagement.

### 4.5 Reflection Report

Report sections:

- Missing stakeholders.
- Hidden assumptions.
- Ethical risks.
- Safety gaps.
- Participant burden.
- Trust calibration notes.
- Recommended revisions.
- Questions for real fieldwork.

## 5. Study Method

### 5.1 Participants

6-8 researchers or graduate students for formative study.

### 5.2 Procedure

1. Consent.
2. Initial research plan.
3. SafeBARS walkthrough.
4. Rehearsal task.
5. Revised research plan.
6. Post-study interview.

### 5.3 Data

- Initial plans.
- Interaction logs.
- Reflection reports.
- Revised plans.
- Interview transcripts/notes.

### 5.4 Analysis

- Pre/post artifact comparison.
- Thematic analysis of interviews.
- Coding of reflection and interaction logs.

## 6. Expected Findings Structure

The final findings will depend on study data. Candidate finding types:

### Finding 1: Synthetic stakeholders surfaced missing social relationships

Example:

Participants added family helpers, community workers, or platform actors after rehearsal.

### Finding 2: Bias profiles helped researchers notice sensitive disclosure risks

Example:

High privacy/shame profiles pushed researchers to rewrite direct or blaming questions.

### Finding 3: Reflection reports converted chat outputs into actionable plan revisions

Example:

Participants added skip options, privacy explanations, or follow-up support.

### Finding 4: Limitation reminders shaped trust calibration

Example:

Participants treated outputs as prompts for verification rather than participant evidence.

### Finding 5: Synthetic rehearsal remained incomplete and sometimes generic

Example:

Participants wanted real community partner input, richer context, or clearer evidence.

## 7. Discussion

### 7.1 Synthetic Stakeholders as Rehearsal, Not Replacement

Core argument:

SafeBARS is valuable because it supports preparation for real engagement.

### 7.2 Bias Profiles as Inspectable Assumptions

Profiles help researchers ask:

- What if participants distrust institutions?
- What if shame blocks disclosure?
- What if family pressure shapes help-seeking?

### 7.3 Designing for Trust Calibration

Design implications:

- Show limitation reminders.
- Require questions for real fieldwork.
- Separate rehearsal artifacts from evidence.

### 7.4 Implications for High-Risk Digital Safety Research

Online fraud prevention research must consider:

- shame.
- privacy.
- family dynamics.
- institutional trust.
- distress.
- follow-up support.

## 8. Limitations

- Small formative study.
- Researcher participants, not affected community members.
- Prompt/template behavior does not validate real human responses.
- Initial domain focused on online fraud/digital safety.
- Bias profiles are functional controls, not psychometric measures.
- LLM responses may vary across models.

## 9. Conclusion

SafeBARS explores how bias-calibrated synthetic stakeholders can support safer pre-fieldwork action research planning. By treating synthetic stakeholders as rehearsal aids rather than participant proxies, the system aims to help researchers surface assumptions, safety gaps, and trust-calibration issues before engaging real communities.

## Figure Plan

Figure 1:

SafeBARS workflow from research plan to rehearsal, reflection, and revised plan.

Figure 2:

Stakeholder role and bias profile interface.

Figure 3:

Example rehearsal transcript and reflection report.

Figure 4:

Study procedure.

Figure 5:

Example pre/post research plan revision.

