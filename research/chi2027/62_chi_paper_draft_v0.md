# SafeBARS: Rehearsing Sensitive Fieldwork with Bias-Calibrated Synthetic Stakeholders

Draft v0, 2026-06-19

Status: early CHI paper draft. Sections that require future pilot/formative data are marked as **To be completed after study**.

## Abstract

Sensitive HCI and action research can be harmed by poorly prepared interview questions, workshop scripts, consent language, and safety procedures, especially when working with vulnerable communities. LLM-based role-play creates an appealing opportunity to rehearse such plans before fieldwork, but prior work warns that synthetic participants can flatten lived experience, bypass consent and agency, and be mistaken for empirical evidence. We present SafeBARS, a bounded research-preparation scaffold that reframes synthetic stakeholders as prompts for researcher reflection rather than substitutes for real participants. Inspired by controllable-agent work, SafeBARS lets researchers configure bias/risk-response profiles, rehearse study plans with synthetic stakeholders, compare responses across providers, generate reflection reports, and record revised plans. Using online fraud prevention with older adults as an initial sensitive context, SafeBARS explores how AI can support pre-fieldwork ethical reflection while preserving the need for real community participation.

## 1. Introduction

Researchers preparing sensitive HCI and action research often face a difficult problem before fieldwork begins: how to test whether their interview questions, workshop scripts, consent language, and safety procedures might unintentionally create harm. This problem is especially visible in online fraud prevention research with older adults and other vulnerable communities. A question that asks participants how much money they lost, why they believed a fraudulent message, or whether family members intervened may appear methodologically useful, but it can also evoke shame, privacy concerns, distrust, or distress. Researchers therefore need ways to rehearse study plans before engaging real communities.

LLM-based role-play offers a tempting solution. A researcher can ask a model to act as an older adult, family helper, community worker, or institutional gatekeeper, then inspect the generated response. However, recent HCI work warns that synthetic participants can misportray lived experience, bypass participant consent and agency, and create a "surrogate" effect in which simulated narratives are mistaken for empirical evidence. At the same time, work on controllable LLM agents suggests that synthetic agents can be designed with more explicit behavioral tendencies than ordinary persona prompts. This creates a design tension: can synthetic stakeholders be useful without becoming participant replacements?

We explore this tension through SafeBARS, a Safe Bias-Aware Action Research Scaffolding system. SafeBARS supports pre-fieldwork rehearsal through bias/risk-response profiles, synthetic stakeholder dialogue, multi-provider comparison, reflection reports, and revised-plan capture. Rather than asking whether synthetic stakeholders accurately represent vulnerable communities, SafeBARS asks whether bounded synthetic stakeholders can help researchers notice ethical and safety risks in their plans before real fieldwork.

Our initial context is online fraud prevention with older adults. This domain is both socially important and methodologically sensitive: research plans may involve financial loss, embarrassment, family support, institutional reporting, digital literacy, and autonomy. We use this context not to build another anti-fraud education tool, but to study how researchers can rehearse sensitive study designs before working with real participants.

This paper makes four contributions:

1. We introduce a design framing for synthetic stakeholders as bounded pre-fieldwork rehearsal aids rather than substitutes for real participants.
2. We present SafeBARS, a working prototype that combines bias/risk-response profiles, rehearsal chat, multi-provider comparison, reflection reports, and revised-plan capture.
3. We propose and will evaluate a formative study method for examining changes in researcher reflection and study-plan revision.
4. We derive design implications for AI-assisted research preparation in sensitive HCI and action research contexts.

## 2. Related Work

### 2.1 Controllable LLM Agents and Synthetic Social Behavior

LLM agents can produce plausible social behavior and can be organized into interactive simulations. Work such as Generative Agents demonstrates how memory, reflection, and planning can create believable agent behavior. More recent work such as CoBRA argues that ordinary natural-language persona descriptions are too implicit and inconsistent for controlling social agents, and introduces primitives for measuring and regulating cognitive bias in LLM agents.

SafeBARS draws on this shift from vague persona prompting toward explicit behavioral control. However, our goal is not to create realistic simulated people or benchmark cognitive bias. Instead, we use explicit bias/risk-response profiles as functional controls for rehearsal. The profile dimensions, such as privacy sensitivity, shame/stigma sensitivity, institutional distrust, and participant burden sensitivity, are design controls that help researchers explore how their plans might be challenged from different stakeholder positions.

### 2.2 Synthetic Participants and the Risk of Replacement

Prior work warns that synthetic participants are ethically and epistemologically risky when treated as substitutes for real people. Studies of LLMs as qualitative research participants argue that LLM-generated narratives can produce a "surrogate" effect, where simulated accounts appear useful but lack consent, agency, contextual depth, and situated experience. Other work argues that replacing human participants with LLMs can flatten identity groups and misrepresent vulnerable communities.

SafeBARS treats these critiques as design constraints. The system does not ask whether a synthetic stakeholder accurately represents older adults, fraud victims, or any vulnerable group. Instead, it asks whether a fictional stakeholder response can help a researcher notice a fragile assumption, revise a question, or identify a safety gap. This distinction shapes the interface, reflection report, and study design: outputs are framed as planning prompts, not participant evidence.

### 2.3 LLMs in Qualitative and User Research Workflows

Researchers increasingly use LLMs to brainstorm, summarize, code, and support qualitative analysis. CHI and CSCW work on LLMs in qualitative research shows both practical interest and unresolved tensions around transparency, interpretive authority, validity, and research ethics. AI-assisted qualitative analysis tools also show that LLMs can support research work when they are embedded in human-in-the-loop workflows and evaluated through researcher artifacts.

SafeBARS extends this line of work to the pre-fieldwork stage. Rather than helping researchers analyze collected data, SafeBARS helps researchers inspect the study plan before data collection begins. This shifts the evaluation target from coding accuracy or analysis quality to ethical reflection, risk identification, and concrete revision of research plans.

### 2.4 Participatory and Action Research

Participatory design, participatory AI, and action research emphasize stakeholder agency, situated knowledge, and collaborative inquiry. These traditions make clear that communities should not be bypassed by synthetic stand-ins. At the same time, careful preparation is part of ethical fieldwork. Researchers need to enter community engagement with clearer questions, better consent procedures, and more awareness of power, trust, and risk.

SafeBARS is therefore positioned as a pre-participation scaffold. It aims to help researchers prepare for real engagement, not avoid it. The system asks researchers to document what must still be verified with real participants or community partners.

### 2.5 Online Fraud Prevention as a Sensitive HCI Context

Online fraud prevention research with older adults and vulnerable communities is a strong test context for SafeBARS because it involves privacy, shame, family relationships, distrust, and emotional distress. Recent CHI work on senior-targeted online fraud shows that younger family members often help safeguard older adults, but that this support can involve tension, refusal of help, and emotional burden. Role-based fraud interventions such as ROLESafe show the value of simulation for anti-fraud learning, while participatory work on deepfake scams emphasizes autonomy, dignity, and older adults' own concerns.

SafeBARS differs from these interventions. It does not train older adults to identify scams. It helps researchers prepare safer research plans about such interventions. The online-fraud context supplies concrete risk dimensions that make pre-fieldwork rehearsal valuable.

### 2.6 Trust Calibration and Bounded AI Tools

Human-AI interaction research emphasizes that effective AI systems should support appropriate reliance, communicate uncertainty and limitations, and help users recover from failure. In SafeBARS, trust calibration is especially important because synthetic stakeholder responses may sound persuasive. The system therefore includes limitation framing, provider comparison, reflection categories, and revised-plan capture to encourage researchers to treat outputs as prompts for inspection rather than validation.

## 3. Design Goals

We derived five design goals from related work and the online-fraud research context.

### DG1: Frame synthetic stakeholders as rehearsal prompts, not participant substitutes.

SafeBARS should make clear that synthetic stakeholders are fictional and cannot provide evidence about real communities.

### DG2: Make stakeholder assumptions explicit and adjustable.

Instead of relying only on natural-language personas, SafeBARS should expose controllable risk-response dimensions such as privacy sensitivity, shame sensitivity, institutional distrust, and participant burden sensitivity.

### DG3: Surface ethical, emotional, and procedural risks in study plans.

The system should help researchers notice risks around sensitive disclosure, consent, withdrawal, distress, data boundaries, missing stakeholders, and deficit framing.

### DG4: Support trust calibration through comparison and reflection.

SafeBARS should help researchers see that model responses vary and that no provider should be treated as authoritative.

### DG5: Produce artifacts that support formative evaluation.

The system should capture initial plans, rehearsal logs, reflection reports, and revised plans so that researchers' changes can be analyzed.

## 4. SafeBARS System

SafeBARS is a web-based prototype for rehearsing sensitive action research plans with bias-calibrated synthetic stakeholders. The current implementation is built as a Flask application and deployed as a Render web service. The prototype supports both deterministic fallback responses and optional LLM-backed responses through OpenAI-compatible providers.

### 4.1 Research Plan Input

The left panel asks researchers to enter a structured study plan:

- title;
- research goal;
- target community;
- planned method;
- draft materials;
- known risks;
- rehearsal focus.

The default example concerns a community workshop on online fraud prevention with older adults. The default draft intentionally includes potentially sensitive wording, such as asking how much money participants lost and why they believed a scam message. This creates a concrete opportunity for rehearsal.

### 4.2 Stakeholder Presets and Bias/Risk-Response Profiles

Researchers select a stakeholder preset and can inspect or adjust the bias/risk-response profile. Initial presets include an affected participant, family helper, and community worker. Profiles include dimensions such as:

- authority trust;
- confirmation bias;
- urgency sensitivity;
- shame/stigma sensitivity;
- institutional distrust;
- social proof susceptibility;
- help-seeking reluctance;
- privacy sensitivity;
- distress sensitivity;
- victim-blaming risk;
- resource constraint sensitivity;
- participant burden sensitivity.

These dimensions are not psychometric measures. They are functional rehearsal controls that shape how a fictional stakeholder might push back on a research plan.

### 4.3 Rehearsal Chat

The central panel supports chat-based rehearsal. After the session begins, the researcher can ask the synthetic stakeholder to react to an interview question, consent explanation, workshop step, or safety procedure. SafeBARS records the researcher message and stakeholder response. For each stakeholder response, the interface also provides an interpretation box that translates the response into planning implications, such as privacy/data risk, shame/judgment risk, purpose clarity gap, revision cue, or safety-procedure issue.

### 4.4 Multi-Provider Comparison

SafeBARS includes a provider comparison mode. Given the same research-plan context and researcher message, it compares the deterministic fallback response with responses from configured LLM providers. The comparison view summarizes:

- risks surfaced;
- boundary cues;
- revision cues;
- overtrust warnings;
- provider-specific errors.

This feature is not intended to decide which model is "correct." Instead, it helps researchers see that providers surface different risks and may fail in different ways. This is a trust-calibration mechanism.

### 4.5 Reflection Report

After several rehearsal turns, researchers can generate a reflection report. The report groups potential issues into:

- missing stakeholders;
- hidden assumptions;
- ethical risks;
- safety gaps;
- participant burden;
- trust calibration notes;
- recommended revisions;
- open questions for real fieldwork;
- evidence from rehearsal.

The report is designed to convert chat interaction into actionable revision prompts.

### 4.6 Revised Plan Capture and Export

The right panel asks researchers to write concrete changes they would make before real fieldwork. The prompt asks for:

- issue noticed;
- revision to make;
- remaining question for real stakeholders.

SafeBARS can export session artifacts, including the initial plan, stakeholder profile, conversation, reflection report, and revised plan.

## 5. Planned Formative Study

**To be completed after pilot/formative study.**

We plan to evaluate SafeBARS through a formative study with researchers or graduate students who have experience with HCI, UX research, design research, or digital-safety study planning.

### 5.1 Participants

We plan to recruit 6-8 participants for a formative study. Participants will be HCI/design researchers, graduate students, or UX researchers who can reason about interview questions, consent, workshops, or fieldwork preparation.

### 5.2 Procedure

Each session will last approximately 45-60 minutes:

1. Introduction and consent.
2. Participant reviews or drafts an initial online-fraud-prevention research plan.
3. Participant marks initial concerns or makes a first revision without SafeBARS.
4. Participant uses SafeBARS to rehearse the plan.
5. Participant runs at least one provider comparison.
6. Participant generates a reflection report.
7. Participant writes a revised plan.
8. Semi-structured interview about usefulness, limits, trust, and what still requires real stakeholder input.

### 5.3 Data Collection

We will collect:

- initial research plan;
- optional initial revision or concern notes;
- SafeBARS interaction logs;
- provider comparison output;
- reflection report;
- revised plan;
- interview transcript or notes.

### 5.4 Analysis

We will analyze both artifacts and interviews. For pre/post plan artifacts, we will code whether participants add or improve:

- privacy language;
- consent and withdrawal options;
- skip/pause procedures;
- distress support;
- non-blaming question wording;
- stakeholder map;
- participant-burden reduction;
- community verification step.

For interviews, we will conduct thematic analysis around perceived usefulness, trust calibration, overtrust risks, generic responses, and desired improvements.

## 6. Expected Findings Structure

**To be replaced with empirical findings after study.**

We expect findings to be organized around how SafeBARS shaped researcher reflection and plan revision. Candidate finding themes include:

### Finding 1: Synthetic stakeholder pushback surfaced sensitive disclosure risks.

Researchers may revise questions about loss amount, belief, or scam experience after stakeholders express discomfort, privacy concern, or fear of judgment.

### Finding 2: Bias/risk-response profiles helped researchers inspect assumptions.

Participants may use high privacy sensitivity, shame sensitivity, or institutional distrust profiles to explore how different concerns change the rehearsal.

### Finding 3: Provider comparison made model variation visible.

Participants may notice that different providers surface different risks or produce generic responses, helping them treat AI output as partial and unstable.

### Finding 4: Reflection reports translated conversation into revisions.

The report may help participants move from "the stakeholder was uncomfortable" to concrete changes in consent, question wording, or safety protocol.

### Finding 5: Participants still wanted real stakeholder verification.

Participants may value SafeBARS as preparation but reject it as evidence, reinforcing the non-replacement framing.

## 7. Discussion

### 7.1 Rehearsal, Not Replacement

SafeBARS contributes a bounded way to use synthetic stakeholders without treating them as participant proxies. The system's value lies in provoking researcher reflection, not in accurately modeling a community.

### 7.2 Productive Discomfort as a Design Goal

A useful rehearsal system should not simply reassure researchers. It should create productive discomfort by surfacing questions that feel intrusive, unclear, burdensome, or ethically fragile.

### 7.3 Bias Profiles as Inspectable Assumptions

The bias/risk-response profile does not measure real people. Instead, it makes assumptions visible. Researchers can ask: what if a participant distrusts institutions? What if shame blocks disclosure? What if a family helper wants to protect but also speaks over the older adult?

### 7.4 Multi-Provider Comparison as Trust Calibration

Provider comparison helps researchers see AI instability. If models disagree, miss risks, or fail, the interface can remind users that LLM responses are not ground truth.

### 7.5 Implications for Sensitive HCI Research Tools

SafeBARS suggests that AI research tools for sensitive contexts should:

- preserve the distinction between rehearsal and evidence;
- require researchers to document what must be verified with real stakeholders;
- support artifact-based reflection, not only chat;
- make limitations part of the workflow rather than a footer warning.

## 8. Limitations

SafeBARS is an early prototype. The current system does not validate whether synthetic stakeholders accurately represent older adults, fraud victims, or vulnerable communities. Bias/risk-response profiles are functional controls rather than psychological measures. The initial context focuses on online fraud prevention, which may not generalize to all sensitive research domains. LLM provider outputs vary and may be generic, culturally thin, or misleading. Finally, a small formative study can show how researchers use SafeBARS, but cannot prove that it improves real fieldwork outcomes.

## 9. Conclusion

SafeBARS explores how bias-calibrated synthetic stakeholders can support safer pre-fieldwork planning for sensitive HCI and action research. By framing synthetic stakeholder responses as rehearsal prompts rather than participant evidence, SafeBARS aims to help researchers surface assumptions, revise risky plans, and calibrate trust before engaging real communities. The broader contribution is a design direction for AI tools that prepare researchers for participation rather than replacing participation.

## References To Add

This draft should later be converted to ACM format and expanded with full BibTeX entries for:

- CoBRA.
- Generative Agents.
- Simulacrum of Stories.
- Large Language Models in Qualitative Research.
- AI-Driven Co-Construction of Synthetic Personas.
- Human-AI Collaboration in Thematic Analysis.
- Auntie, Please Don't Fall for Those Smooth Talkers.
- Hear Us, then Protect Us.
- ROLESafe.
- Large Language Models that Replace Human Participants Can Harmfully Misportray and Flatten Identity Groups.
- Participatory design / participatory AI foundations.
- Human-AI guidelines and trust calibration literature.

