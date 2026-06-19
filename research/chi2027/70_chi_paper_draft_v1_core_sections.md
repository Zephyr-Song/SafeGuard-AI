# SafeBARS CHI Paper Draft v1: Core Sections

Draft date: 2026-06-19

Status: stronger paper-language draft for abstract, introduction, related work framing, and study overview. This is not yet a full ACM-formatted paper.

## Title

SafeBARS: Bounded Synthetic Stakeholders for Rehearsing Sensitive HCI Fieldwork

## Abstract

Researchers preparing sensitive HCI fieldwork often need to test interview questions, workshop scripts, consent language, and safety procedures before meeting real participants. This preparation is especially important in online fraud prevention research with older adults, where questions about financial loss, scam belief, family involvement, or reporting may unintentionally trigger shame, privacy concerns, distrust, or distress. Large language model role-play offers a tempting way to rehearse such plans, but using synthetic participants as stand-ins for vulnerable communities risks bypassing consent, agency, and situated lived experience.

We present SafeBARS, a Safe Bias-Aware Research Scaffolding system that reframes synthetic stakeholders as bounded rehearsal prompts rather than participant substitutes. Inspired by work on controllable LLM agents, SafeBARS lets researchers configure stakeholder roles and risk-response profiles, rehearse study materials through chat, compare responses across providers, generate reflection reports, and record revised plans. We propose a formative study with researchers and research-trained practitioners to examine how SafeBARS supports risk identification, plan revision, and trust calibration. SafeBARS contributes a design framing and prototype for using synthetic stakeholders to prepare for, rather than replace, real community engagement.

## 1. Introduction

"How much money did you lose, and why did you believe the message?"

For a researcher preparing an online fraud prevention study, this question may appear direct and methodologically useful. It asks for concrete information about harm and decision-making. Yet for a participant who has experienced fraud, the same question may feel intrusive, blaming, or embarrassing. It may raise concerns about who will hear the answer, how it will be recorded, whether family members will judge them, or whether the researcher understands the emotional cost of retelling the event. Similar risks appear in workshop scripts, consent procedures, safety plans, and follow-up protocols. In sensitive HCI and action research, harm can begin before data collection if researchers enter the field with poorly prepared materials.

Researchers therefore need ways to rehearse study plans before engaging real communities. This need is not a replacement for participatory work; it is part of preparing for it. A research team that has already considered privacy boundaries, optional disclosure, distress support, participant burden, and stakeholder autonomy can enter real stakeholder engagement with more careful questions and clearer safety procedures.

Large language models make this preparation problem newly complicated. On one hand, LLMs can quickly generate stakeholder-like responses to draft questions. A researcher can ask a model to act as an older adult affected by fraud, a family helper, a community worker, or an institutional gatekeeper. This interaction can create useful friction: a synthetic stakeholder might object to a question, ask for clearer consent language, or point out a missing follow-up procedure. On the other hand, LLM role-play can easily become an ethically dangerous shortcut. If researchers treat generated responses as evidence about vulnerable communities, they risk bypassing the very people whose agency, consent, and situated knowledge should guide the work.

This paper explores a design question at the center of this tension: can synthetic stakeholders help researchers prepare for sensitive fieldwork without becoming synthetic participants?

We investigate this question through SafeBARS, a Safe Bias-Aware Research Scaffolding system for pre-fieldwork rehearsal. SafeBARS is inspired by recent work on controllable LLM agents, which argues that vague natural-language personas provide weak control over agent behavior. Instead of asking users to write a persona such as "an older adult fraud victim," SafeBARS exposes stakeholder roles and risk-response dimensions, such as privacy sensitivity, shame/stigma sensitivity, institutional distrust, distress sensitivity, participant burden sensitivity, and autonomy concerns. These dimensions are not psychometric measures and do not claim to model real people. They are functional controls that let researchers rehearse how different kinds of risk might surface in their study materials.

SafeBARS includes five workflow components. First, researchers enter a structured research plan, including goals, target community, draft materials, and known risks. Second, they select a synthetic stakeholder preset and inspect or adjust its risk-response profile. Third, they rehearse interview questions, workshop scripts, consent language, or safety procedures through chat. Fourth, they can compare multiple response sources to see which risks different providers surface or miss. Finally, they generate a reflection report and write a revised plan that documents concrete changes and unresolved questions for real stakeholders.

Our initial context is online fraud prevention with older adults. We use this context because it is socially important and methodologically sensitive. Research plans in this domain often involve financial loss, embarrassment, family support, institutional reporting, digital literacy, autonomy, and emotional distress. SafeBARS is not an anti-fraud education intervention. It is a research-preparation tool for people designing studies about such interventions.

We plan to evaluate SafeBARS through a formative study with researchers, graduate students, and research-trained practitioners. Participants will review an intentionally imperfect online-fraud-prevention study plan, record initial concerns, use SafeBARS to rehearse the plan, compare provider responses, generate a reflection report, and write a revised plan. We will analyze pre/post artifacts and interviews to understand how the tool shapes risk identification, plan revision, and trust calibration.

This work makes four contributions:

1. We introduce a non-replacement framing for synthetic stakeholders as bounded rehearsal prompts for sensitive HCI fieldwork preparation.
2. We present SafeBARS, a working prototype that combines stakeholder roles, risk-response profiles, rehearsal chat, provider comparison, reflection reporting, and revised-plan capture.
3. We propose an artifact-based formative study method for evaluating whether AI-assisted rehearsal changes researchers' study plans and ethical reflection.
4. We derive design implications for AI systems that support preparation for community engagement while preserving the need for real participation.

## 2. Related Work

### 2.1 From Persona Prompts to Controllable Synthetic Stakeholders

LLM agents can produce fluent social responses, but ordinary persona prompting provides limited control over the behavioral tendencies that matter in research rehearsal. A prompt such as "act as an older adult" hides assumptions about experience, risk, emotion, trust, and social context inside a broad identity label. This is especially problematic in sensitive domains, where the relevant issue may not be age alone but privacy concern, shame, institutional distrust, family dynamics, or support needs.

Recent work on controllable social agents, including CoBRA, argues for more explicit control over cognitive and social tendencies. SafeBARS adopts this design move but redirects it toward research preparation. The system does not attempt to simulate a population or benchmark psychological realism. Instead, it exposes risk-response dimensions so researchers can inspect how their materials might be challenged under different assumptions. In this sense, SafeBARS treats controllability as a reflective design resource rather than a claim of representational accuracy.

### 2.2 Synthetic Participants and the Non-Replacement Constraint

HCI and qualitative research communities have raised concerns about using LLMs as synthetic participants. Generated narratives may sound plausible, but they lack consent, agency, situated embodiment, and accountability. They can also flatten identity groups and create a surrogate effect, where simulated responses appear to stand in for people who were never consulted.

SafeBARS begins from this critique. The system is not designed to answer what older adults, fraud victims, or community workers really think. It is designed to help researchers notice what might be wrong with their own plans. This distinction changes the unit of analysis. The relevant artifact is not the synthetic stakeholder response as data; it is the researcher's revised question, revised consent language, revised safety procedure, or documented question for real stakeholders.

### 2.3 LLMs in Qualitative Research Workflows

Researchers increasingly use LLMs for brainstorming, summarization, coding, and sensemaking, while also expressing concerns about transparency, interpretive authority, confidentiality, and validity. Prior work suggests that LLM support is more appropriate when tools are embedded in human workflows, make limitations visible, and preserve researcher responsibility.

SafeBARS extends this line of work to the pre-fieldwork stage. Instead of helping researchers analyze data after collection, it helps them inspect the plan before collection begins. This shifts the evaluation target from output correctness to changes in preparation: what risks researchers identify, what revisions they make, and how they describe the boundaries of AI-generated rehearsal.

### 2.4 Sensitive Fieldwork, Participatory Commitments, and Preparation

Participatory design, action research, and community-based research emphasize that people affected by a problem should shape how it is studied and addressed. This commitment creates an important boundary for SafeBARS: synthetic stakeholders cannot replace real community engagement. However, preparation is also part of ethical participation. Researchers should not rely on community partners to catch every avoidable problem in a rough study plan.

SafeBARS is positioned as a pre-participation scaffold. It can help a researcher identify fragile wording, missing consent boundaries, or unclear support procedures before meeting real stakeholders. Its output should therefore lead to better questions for communities, not fewer interactions with them.

### 2.5 Online Fraud Prevention as a Sensitive HCI Context

Online fraud prevention research with older adults provides a concrete test context for SafeBARS because it combines digital safety with emotional, relational, and institutional concerns. Fraud research may involve financial loss, embarrassment, fear of judgment, family intervention, reporting decisions, distrust of institutions, and uncertainty about support resources. These issues make the domain more complex than a simple digital-literacy problem.

Existing fraud-prevention work has studied scams, family support, role-based education, and participatory safeguards. SafeBARS differs from this work by moving one step earlier in the research process. It does not teach older adults how to avoid scams. It helps researchers rehearse the study designs they might use when developing or evaluating such interventions.

### 2.6 Trust Calibration for AI-Assisted Research Preparation

Because synthetic stakeholder responses can sound fluent and persuasive, SafeBARS must support calibrated reliance. The system includes limitation framing, deterministic fallback responses, multi-provider comparison, reflection categories, and revised-plan capture. These features are intended to make AI output inspectable and contestable.

Provider comparison is especially important for this framing. It does not determine which provider is correct. Instead, it shows that different response sources may surface different risks, produce generic answers, fail with API errors, or miss important boundaries. This variation can help researchers treat the output as partial and unstable, rather than as authoritative participant-like evidence.

## 3. System Overview

SafeBARS is a web-based prototype for rehearsing sensitive research plans. The interface is organized around six panels:

1. Research Plan: structured input for the study title, goal, target community, planned method, draft materials, risks, and rehearsal focus.
2. Stakeholder Profile: role selection and risk-response dimensions.
3. Rehearsal Chat: interaction with the synthetic stakeholder about interview questions, scripts, consent, or safety procedures.
4. Provider Comparison: side-by-side responses from available providers and a summary of consensus or unique risks.
5. Reflection Report: a generated report that groups issues, revision cues, and open questions.
6. Revised Plan: a structured space for documenting what will change before real fieldwork.

The current prototype supports several stakeholder presets:

- Affected Participant: emphasizes privacy, shame/stigma, distress, and reluctance to disclose.
- Family Helper: emphasizes protection, autonomy, family privacy, and the risk of speaking over the affected person.
- Community Worker: emphasizes feasibility, participant burden, referral resources, and follow-up capacity.

## 4. Planned Formative Study Overview

The formative study will examine how researchers use SafeBARS, not whether SafeBARS accurately simulates real stakeholders.

### Participants

We will recruit researchers, graduate students, UX researchers, or research-trained practitioners who have experience designing interviews, workshops, surveys, participatory sessions, or user studies.

### Task

Participants will review an intentionally imperfect study plan for online fraud prevention with older adults. The plan includes sensitive questions about financial loss and scam belief, recording, a workshop activity, and limited safety procedures.

### Procedure

Participants will:

1. review the plan and record initial concerns;
2. use SafeBARS to rehearse at least two questions or procedures;
3. run provider comparison on one important prompt;
4. generate a reflection report;
5. write a revised plan;
6. complete a short interview about usefulness, limitations, and trust.

### Analysis

We will compare pre-tool and post-tool artifacts using codes such as privacy/data boundary, non-blaming wording, optional disclosure, consent/withdrawal, distress support, participant burden, stakeholder ecosystem, autonomy boundary, trust calibration, and real-stakeholder questions. Interview analysis will focus on perceived usefulness, overtrust, generic responses, model variation, and boundaries between rehearsal and evidence.

## 5. Expected Contribution Shape

If the formative study is successful, the final CHI paper should show:

1. Researchers identified additional risks after using SafeBARS.
2. Revised plans included more concrete privacy, consent, distress, burden, and autonomy language.
3. Provider comparison helped some participants become more cautious about treating AI output as authoritative.
4. Participants used SafeBARS to prepare questions for real stakeholders rather than replacing real stakeholder engagement.

If the formative study reveals problems, those problems can still produce a CHI contribution. For example, if participants overtrust the synthetic stakeholder, that becomes evidence that stronger interface boundaries are needed. If responses are too generic, that becomes evidence about the limits of LLM rehearsal for sensitive research preparation.

