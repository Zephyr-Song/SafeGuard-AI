# SafeBARS Contribution Map

Last updated: 2026-06-16

## Purpose

This memo translates CoBRA's contribution structure into a CHI 2027 contribution strategy for SafeBARS.

The goal is not to reproduce CoBRA. The goal is to make a comparable style of contribution:

- Identify a hidden methodological problem.
- Propose a measurable abstraction.
- Build a system around that abstraction.
- Evaluate whether the system changes human practice.
- Discuss limitations and responsible use.

## CoBRA's Contribution Pattern

CoBRA follows a strong research pattern:

1. Existing practice depends on implicit natural-language persona specifications.
2. This practice is unreliable across models and prompts.
3. The authors introduce Cognitive Bias Index as a measurable abstraction.
4. They introduce a regulation engine to control the abstraction.
5. They validate the system using reusable benchmark tasks.
6. They show improved controllability and reproducibility.

## SafeBARS Parallel

SafeBARS follows the same pattern at the level of HCI research practice:

1. Existing practice increasingly uses LLMs to brainstorm or role-play stakeholders during early-stage research planning.
2. This practice is unreliable, opaque, and risky in high-stakes domains because synthetic stakeholders may flatten identities, reproduce stereotypes, or create false confidence.
3. SafeBARS introduces stakeholder risk-response profiles as measurable and adjustable abstractions.
4. SafeBARS implements a rehearsal scaffold that lets researchers interact with bias-calibrated synthetic stakeholders.
5. SafeBARS evaluates the scaffold using high-risk action research planning tasks.
6. SafeBARS studies whether the scaffold improves reflexivity, stakeholder coverage, safety planning, and trust calibration.

## Primary Contribution Claim

SafeBARS contributes a new approach to AI-assisted research preparation: bias-calibrated synthetic stakeholders as pre-fieldwork rehearsal scaffolds for high-risk action research.

## Contribution 1: Problem Framing

### Claim

Synthetic stakeholders are already plausible tools for early-stage research planning, but their use in high-risk action research creates methodological and ethical risks.

### Why It Matters

Researchers may use LLM personas to prepare for real studies before they have access to participants. This can be useful, but also risky. A synthetic stakeholder may sound convincing while hiding assumptions, stereotypes, or missing social context.

### What SafeBARS Adds

SafeBARS reframes synthetic stakeholders as rehearsal aids, not evidence about real communities.

### Reviewer Risk

Reviewers may ask whether this problem is real.

### Evidence Needed

- Formative interviews showing researchers already use or are tempted to use LLM role-play.
- Literature showing concerns with synthetic users and simulated participants.
- Examples where ordinary LLM personas miss key risks or over-simplify stakeholder behavior.

## Contribution 2: Conceptual Abstraction

### Claim

Stakeholder risk-response patterns can serve as controllable abstractions for pre-fieldwork rehearsal.

### Examples

- Authority trust.
- Shame or stigma sensitivity.
- Help-seeking reluctance.
- Institutional distrust.
- Urgency or scarcity sensitivity.
- Privacy sensitivity.

### Why It Matters

The abstraction moves beyond free-form persona prompts. Researchers can examine how a research plan performs under different controlled stakeholder response patterns.

### Reviewer Risk

Reviewers may ask whether these scores are psychologically valid.

### Planned Boundary

We will not claim psychological validity. The scores are functional controls for rehearsal, similar to scenario variables in design fiction or tabletop exercises.

## Contribution 3: System

### Claim

SafeBARS operationalizes the abstraction through a researcher-facing scaffold with four modules:

1. Research plan input.
2. Bias-calibrated synthetic stakeholders.
3. Rehearsal interaction.
4. Reflection dashboard.

### Why It Matters

The system helps researchers test interview questions, intervention ideas, consent language, and support procedures before fieldwork.

### Reviewer Risk

Reviewers may say this is "just ChatGPT with prompts."

### Planned Response

SafeBARS is not only a chat interface. It structures:

- Stakeholder role coverage.
- Bias and risk-response controls.
- Rehearsal tasks.
- Reflection prompts.
- Trust calibration warnings.
- Pre/post research plan revision.

The paper should show how these components work together and how they shape researcher practice.

## Contribution 4: Empirical Findings

### Claim

SafeBARS helps researchers identify gaps in early research plans and revise them toward safer fieldwork.

### Possible Findings

- Researchers discover missing stakeholders.
- Researchers revise victim-blaming or overly direct interview questions.
- Researchers add distress handling and exit options.
- Researchers become more cautious about treating synthetic responses as representative.
- Researchers use bias profiles to test research plans across different risk conditions.

### Evidence Needed

- Pre/post research plan comparison.
- Interaction logs.
- Interview quotes.
- Thematic analysis.
- Optional pilot comparison with ordinary LLM brainstorming.

## Contribution 5: Design Implications

### Claim

AI systems for research planning should support reflexive rehearsal and trust calibration rather than participant replacement.

### Design Implications

1. Make synthetic stakeholder limits visible.
2. Treat bias controls as scenario variables, not psychological truths.
3. Encourage researchers to compare multiple stakeholder perspectives.
4. Require reflection before exporting conclusions.
5. Preserve uncertainty and mark missing real-world evidence.
6. Support ethics and safety planning as first-class outputs.

## What the Paper Is Not

SafeBARS is not:

- A replacement for participatory design.
- A tool for generating fake participant evidence.
- A validated simulator of real fraud victims.
- A general-purpose agent-bias benchmark.
- A full technical extension of CoBRA's representation engineering.

## What the Paper Is

SafeBARS is:

- A system for pre-fieldwork rehearsal.
- A study of how researchers use bias-calibrated synthetic stakeholders.
- A design exploration of safe AI support for action research.
- A CHI contribution connecting controllable agents, research ethics, and reflexive HCI methods.

## Strong Introduction Arc

1. HCI researchers increasingly explore LLMs for research planning.
2. Sensitive domains make early rehearsal valuable but risky.
3. Free-form synthetic stakeholders can mislead researchers.
4. CoBRA shows that agent behavior can be treated through measurable bias abstractions.
5. SafeBARS adapts this idea to action research preparation.
6. We design and study a system that helps researchers rehearse with controlled stakeholder risk-response profiles.

## Strong Discussion Arc

1. Synthetic stakeholders are useful when framed as rehearsal, not evidence.
2. Bias profiles help make assumptions inspectable.
3. Reflection dashboards can interrupt over-trust.
4. Safe AI research tools should support better encounters with real participants, not replace those encounters.

