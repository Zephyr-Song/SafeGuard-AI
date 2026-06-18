# SafeBARS Related Work Synthesis Memo

Last updated: 2026-06-17

This memo turns the literature matrix into a paper argument. It is written for CHI framing: each related work section should create pressure toward the SafeBARS design problem.

## One-Sentence Related Work Argument

Prior work shows that LLM agents can simulate plausible users, that such simulations can be controlled to some extent, and that replacing real participants is ethically risky; however, we know less about how to design bounded AI scaffolds that help researchers rehearse sensitive fieldwork plans while preserving the need for real community participation.

## Recommended Section Structure

### 1. LLM Agents Are Plausible, But Plausibility Is Not Enough

Core message:

LLM agents and synthetic users can produce believable behavior, but believable behavior does not equal trustworthy research evidence.

Use these papers:

- Generative Agents.
- CoBRA.
- Lost in Simulation.
- LLMs replacing human participants can flatten identity groups.

Paragraph move:

Start with the growth of synthetic agents. Then quickly shift from "can simulate" to "what makes simulation usable and safe." CoBRA gives us the language of controllability. Lost in Simulation and identity-flattening work give us the ethical limit.

SafeBARS claim created:

SafeBARS treats synthetic stakeholders as bounded rehearsal aids, not as proxies for real participants.

### 2. Synthetic Participants Create a Replacement Risk

Core message:

The tempting contribution would be "we simulate vulnerable participants." That is the wrong contribution. The CHI contribution should be a scaffold that makes researcher assumptions visible before real contact.

Use these papers:

- Large Language Models that Replace Human Participants Can Harmfully Misportray and Flatten Identity Groups.
- Can AI Replace Human Subjects?
- Out of One, Many.
- Using LLMs to Simulate Multiple Humans.

Paragraph move:

Acknowledge that synthetic populations and simulated participants have been explored. Then distinguish SafeBARS: the system does not produce findings about vulnerable communities. It produces prompts for researcher reflection and plan revision.

SafeBARS claim created:

The output of SafeBARS is not "what participants would say." The output is "where the research plan may be ethically, emotionally, or procedurally fragile."

### 3. Participatory and Action Research Demand Careful Preparation

Core message:

If research is about vulnerable communities, preparation is not only logistics. It is part of the ethics of participation.

Use these papers:

- The Participatory Turn in AI Design.
- Participatory Design: The Third Space in HCI.
- Participatory Action Research foundations.
- Community-Based Participatory Research foundations.
- Value Sensitive Design.
- Ethics and Society Review.

Paragraph move:

Explain that participatory traditions value agency, local knowledge, and situated expertise. Synthetic stakeholders cannot stand in for these. But rehearsal may help researchers enter the real encounter with better questions, clearer consent practices, and more sensitivity to harm.

SafeBARS claim created:

SafeBARS is a pre-participation scaffold: it prepares researchers to participate better, not to avoid participation.

### 4. Online Fraud Prevention Is a High-Risk Test Context

Core message:

Online fraud prevention with older adults or vulnerable groups is a useful initial context because research plans can easily trigger shame, privacy concerns, family conflict, distrust, and distress.

Use these papers:

- ROLESafe.
- Intergenerational support for deepfake scams.
- Sixteen Years of Phishing User Studies.
- Folk Models of Home Computer Security.

Paragraph move:

Show that digital safety education and fraud prevention are active HCI/security topics. Then separate SafeBARS from end-user interventions: it does not teach older adults. It helps researchers prepare safer studies about such interventions.

SafeBARS claim created:

Fraud prevention is not just a domain example. It supplies concrete risk dimensions that make rehearsal necessary: shame, privacy, blame, family dynamics, and institutional distrust.

### 5. Human-AI Tools Need Trust Calibration

Core message:

Because SafeBARS itself is an AI system, it must prevent overtrust. The design should help researchers use synthetic stakeholder responses as signals to inspect, not as evidence to believe.

Use these papers:

- Guidelines for Human-AI Interaction.
- Calibrated Trust in Dealing with LLM Hallucinations.
- Trust-Calibrated Code Review.
- AI overreliance and appropriate reliance literature to be added.

Paragraph move:

Explain that trust calibration is not a warning label at the bottom of the page. It must be designed into the workflow: profile controls, explicit limitations, evidence-linked reflection prompts, and revised-plan capture.

SafeBARS claim created:

SafeBARS contributes a trust-calibrated workflow for AI-assisted research preparation.

## Introduction Gap Paragraph Draft

Researchers increasingly have access to LLM agents that can role-play stakeholders, participants, or users. This creates an appealing but risky possibility for sensitive HCI research: using synthetic people to test research plans before engaging real communities. Prior work shows both the promise of controllable agent behavior and the danger of treating LLM-generated personas as substitutes for human participants. This tension is especially important in action research on online fraud prevention, where poorly prepared interview questions or workshop scripts may evoke shame, privacy concerns, institutional distrust, or distress. We therefore ask a different question: rather than using synthetic stakeholders as evidence, how can they be designed as bounded rehearsal aids that help researchers identify weaknesses in their plans before fieldwork?

## Contribution Framing

### Contribution 1: Design Framing

A reframing of synthetic stakeholders from participant replacement to pre-fieldwork rehearsal scaffold.

Why this matters:

It directly answers the main ethical critique of synthetic users and gives CHI a more responsible use case.

### Contribution 2: System

SafeBARS, a working prototype that combines bias/risk-response profiles, synthetic stakeholder dialogue, evidence-linked reflection, and revised-plan capture.

Why this matters:

It turns an abstract ethical stance into an inspectable system workflow.

### Contribution 3: Empirical Study

A formative study with researchers/designers evaluating whether SafeBARS helps surface ethical and safety issues in study plans.

Why this matters:

The study does not need to prove stakeholder realism. It evaluates whether the scaffold changes researcher reflection and planning.

### Contribution 4: Design Implications

Guidelines for designing bounded synthetic stakeholder systems for sensitive HCI/action research contexts.

Why this matters:

This creates a CHI-relevant contribution beyond the specific prototype.

## What Not To Claim

- Do not claim SafeBARS accurately models older adults, fraud victims, or vulnerable communities.
- Do not claim synthetic stakeholder responses are empirical data about real communities.
- Do not claim bias sliders are psychometric measures.
- Do not claim the system makes fieldwork safe by itself.

## What To Claim Instead

- SafeBARS helps researchers rehearse plans before fieldwork.
- SafeBARS helps surface possible ethical/safety blind spots.
- SafeBARS helps researchers compare initial and revised study plans.
- SafeBARS supports trust-calibrated use of synthetic stakeholders.
- SafeBARS can be studied through plan quality, reflection quality, perceived usefulness, and overtrust risks.

## Suggested Paper Title Direction

Working title:

SafeBARS: Bias-Calibrated Synthetic Stakeholders for Safer Pre-Fieldwork Rehearsal in Sensitive Action Research

Shorter alternative:

SafeBARS: Rehearsing Sensitive Fieldwork with Bias-Calibrated Synthetic Stakeholders

## Reviewer Questions To Pre-Answer

### Is this just another synthetic user system?

Answer:

No. SafeBARS explicitly rejects replacement. It studies how synthetic stakeholders can be bounded, calibrated, and used for pre-fieldwork reflection.

### Why online fraud?

Answer:

Online fraud prevention is socially important and methodologically sensitive. It includes risks that ordinary user-research rehearsal may miss, such as shame, privacy leakage, victim-blaming, family conflict, and distrust of institutions.

### Why CHI?

Answer:

The project contributes to HCI debates on AI-mediated research, participatory design, trust calibration, and ethical preparation for fieldwork.

### What can be completed in 1-2 months?

Answer:

A focused prototype, literature positioning, supervisor review, and a small formative/pilot study with researchers/designers can be completed. The contribution should be scoped as a formative design study rather than a large-scale validation.
