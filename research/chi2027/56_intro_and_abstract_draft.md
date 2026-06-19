# SafeBARS Intro and Abstract Draft

Last updated: 2026-06-19

Purpose: turn the model-paper patterns into draft CHI framing text.

## Working Titles

1. **SafeBARS: Rehearsing Sensitive Fieldwork with Bias-Calibrated Synthetic Stakeholders**
2. **Before the Field: Bias-Aware Synthetic Stakeholders for Safer Research Rehearsal**
3. **Rehearsal, Not Replacement: Synthetic Stakeholders for Reflective Action Research Planning**
4. **SafeBARS: A Bounded LLM Scaffold for Pre-Fieldwork Reflection in Sensitive HCI Research**

Recommended title for now:

> SafeBARS: Rehearsing Sensitive Fieldwork with Bias-Calibrated Synthetic Stakeholders

It is short, CHI-like, and makes "rehearsing" the center rather than "simulating participants."

## 80-Word Abstract Draft

Researchers preparing sensitive fieldwork often need to test interview questions, workshop scripts, and safety procedures before engaging real communities. LLM role-play offers a tempting rehearsal method, but synthetic participants can mislead researchers if treated as evidence. We present SafeBARS, a bounded scaffold that uses bias-calibrated synthetic stakeholders to surface risks in online-fraud-prevention research plans. SafeBARS supports rehearsal chat, multi-provider comparison, reflection reports, and revised-plan capture. We propose studying how researchers use it to identify risks without replacing real participation.

## 150-Word Abstract Draft

Sensitive HCI and action research can be harmed by poorly prepared interview questions, workshop scripts, consent language, and safety procedures, especially when working with vulnerable communities. LLM-based role-play creates an appealing opportunity to rehearse such plans before fieldwork, but prior work warns that synthetic participants can flatten lived experience, bypass consent and agency, and be mistaken for empirical evidence. We present SafeBARS, a bounded research-preparation scaffold that reframes synthetic stakeholders as prompts for researcher reflection rather than substitutes for real participants. Inspired by controllable agent work, SafeBARS lets researchers configure bias/risk-response profiles, rehearse study plans with synthetic stakeholders, compare responses across providers, generate reflection reports, and record revised plans. Using online fraud prevention with older adults as an initial sensitive context, SafeBARS explores how AI can support pre-fieldwork ethical reflection while preserving the need for real community participation.

## 250-Word Introduction Draft

Researchers preparing sensitive HCI and action research often face a difficult problem before fieldwork begins: how to test whether their interview questions, workshop scripts, consent language, and safety procedures might unintentionally create harm. This problem is especially visible in online fraud prevention research with older adults and other vulnerable communities. A question that asks participants how much money they lost, why they believed a fraudulent message, or whether family members intervened may appear methodologically useful, but it can also evoke shame, privacy concerns, distrust, or distress. Researchers therefore need ways to rehearse study plans before engaging real communities.

LLM-based role-play offers a tempting solution. A researcher can ask a model to act as an older adult, family helper, community worker, or institutional gatekeeper, then inspect the generated response. However, recent HCI work warns that synthetic participants can misportray lived experience, bypass participant consent and agency, and create a "surrogate" effect in which simulated narratives are mistaken for empirical evidence. At the same time, work on controllable LLM agents suggests that synthetic agents can be designed with more explicit behavioral tendencies than ordinary persona prompts. This creates a design tension: can synthetic stakeholders be useful without becoming participant replacements?

We explore this tension through SafeBARS, a Safe Bias-Aware Action Research Scaffolding system. SafeBARS supports pre-fieldwork rehearsal through bias/risk-response profiles, synthetic stakeholder dialogue, multi-provider comparison, reflection reports, and revised-plan capture. Rather than asking whether synthetic stakeholders accurately represent vulnerable communities, SafeBARS asks whether bounded synthetic stakeholders can help researchers notice ethical and safety risks in their plans before real fieldwork.

## Problem Statement

Before conducting sensitive action research, researchers need to rehearse study plans for ethical and safety risks. Existing LLM role-play makes this easy but unsafe: synthetic stakeholders may appear plausible while lacking consent, agency, and situated lived experience. SafeBARS addresses the narrower problem of designing synthetic stakeholders as bounded rehearsal prompts that help researchers inspect and revise their own plans before fieldwork.

## Research Questions

### RQ1

How do researchers use bias-calibrated synthetic stakeholders to identify ethical, emotional, and procedural risks in sensitive fieldwork plans?

### RQ2

How does SafeBARS shape revisions to interview questions, workshop scripts, consent language, and safety procedures?

### RQ3

What forms of trust calibration are needed to help researchers treat synthetic stakeholder responses as rehearsal prompts rather than participant evidence?

## Contribution Draft

This paper makes four contributions:

1. We introduce a design framing for synthetic stakeholders as bounded pre-fieldwork rehearsal aids rather than substitutes for real participants.
2. We present SafeBARS, a working prototype that combines bias/risk-response profiles, rehearsal chat, multi-provider comparison, reflection reports, and revised-plan capture.
3. We outline a formative study method for evaluating changes in researcher reflection and study-plan revision.
4. We derive design implications for AI-assisted research preparation in sensitive HCI and action research contexts.

## Related Work Bridge Paragraph

SafeBARS sits at the intersection of four lines of work. Controllable-agent research shows that LLM behavior can be specified more explicitly than ordinary personas. Critiques of LLMs as qualitative participants show why synthetic stakeholders must not be treated as participant replacements. Participatory and action research traditions emphasize that community agency and situated knowledge cannot be bypassed. Online fraud research with older adults shows why this preparation matters: fraud prevention is entangled with shame, privacy, family support, institutional trust, and autonomy. SafeBARS combines these threads into a bounded research-preparation workflow.

## Supervisor Pitch Version

I am narrowing the project to a concrete CHI problem: researchers preparing online-fraud-prevention fieldwork with older adults need to test interview questions, consent language, workshop scripts, and safety procedures before meeting real participants. Ordinary LLM role-play is risky because it can look like participant evidence. Inspired by CoBRA, SafeBARS instead uses bias-calibrated synthetic stakeholders as bounded rehearsal prompts. The paper contribution would be a prototype plus a formative study showing how researchers use it to surface risks and revise plans without replacing real community participation.

## What This Paper Is Not

- It is not an anti-fraud education tool for older adults.
- It is not a claim that LLMs can simulate vulnerable participants.
- It is not a benchmark of which model best represents a community.
- It is not a substitute for pilot studies, participatory design, or real fieldwork.

## What This Paper Is

- A researcher-facing pre-fieldwork rehearsal tool.
- A trust-calibrated use case for synthetic stakeholders.
- A system for making study-plan assumptions visible.
- A CHI contribution about designing bounded AI tools for sensitive research preparation.

