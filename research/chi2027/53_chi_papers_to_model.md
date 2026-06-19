# CHI Papers to Model for SafeBARS

Last updated: 2026-06-19

Purpose: identify papers SafeBARS can imitate in contribution framing, study design, system presentation, and limitations. This is not only a citation list. It is a writing plan for building a CHI-style paper.

## Recommended Positioning

SafeBARS should not imitate papers that claim AI can replace participants. It should imitate papers that:

1. identify a risky emerging HCI practice;
2. build a bounded tool or workflow;
3. study how researchers/designers use it;
4. explicitly discuss limitations, overtrust, and ethical boundaries.

The paper we should write is closest to:

> a formative HCI systems paper about a bounded AI scaffold for pre-fieldwork research rehearsal.

Not:

> a model benchmark paper, a fraud education intervention, or a synthetic participant replacement paper.

## Tier 1: Core Papers to Imitate Closely

### 1. CoBRA: Programming Cognitive Bias in Social Agents Using Classic Social Science Experiments

- Link: https://github.com/AISmithLab/CoBRA
- Paper: https://arxiv.org/abs/2509.13588
- ACM: https://dl.acm.org/doi/10.1145/3772318.3790804
- Why it matters: CoBRA argues that natural-language persona descriptions are too implicit and inconsistent, then proposes explicit bias control for LLM social agents.
- What to imitate:
  - Start from a concrete weakness in existing practice.
  - Present the system as a toolkit/workflow, not only an app.
  - Use diagrams that show profile specification, response generation, and calibration/feedback.
  - Use a controlled-agent framing: not "realistic people," but "specified behavioral tendencies."
- How SafeBARS differs:
  - CoBRA focuses on programmable agent bias and benchmarks.
  - SafeBARS focuses on a researcher-facing workflow for safer action research planning.
- SafeBARS writing move:
  - "Inspired by CoBRA's explicit control of agent behavior, we ask how such controllability can support bounded pre-fieldwork rehearsal rather than social simulation as evidence."

### 2. 'Simulacrum of Stories': Examining Large Language Models as Qualitative Research Participants

- Link: https://arxiv.org/abs/2409.19430
- ACM: https://dl.acm.org/doi/10.1145/3706598.3713220
- Why it matters: This is the strongest "do not replace participants" paper. It reports interviews with qualitative researchers and argues that LLMs as participant proxies create ethical and epistemological problems.
- What to imitate:
  - The non-replacement stance.
  - Interview/formative study with researchers as the participant group.
  - Results organized around tensions, concerns, and boundaries.
  - Strong limitations about consent, agency, and lived experience.
- How SafeBARS differs:
  - This paper critiques LLM participants.
  - SafeBARS responds by designing a bounded alternative: rehearsal prompts for researchers, not participant data.
- SafeBARS writing move:
  - "We treat the surrogate effect as a design constraint: the system must make clear that synthetic stakeholder outputs are prompts for researcher reflection, not empirical findings."

### 3. Large Language Models in Qualitative Research: Uses, Tensions, and Intentions

- Link: https://arxiv.org/abs/2410.07362
- ACM: https://dl.acm.org/doi/10.1145/3706598.3713120
- Why it matters: CHI 2025 paper on how qualitative researchers use and worry about LLMs.
- What to imitate:
  - "Uses, tensions, intentions" style framing.
  - Treat researchers as situated users with competing goals, not as generic productivity seekers.
  - Use findings to derive design implications for AI research tools.
- How SafeBARS differs:
  - That paper studies broad LLM use in qualitative research.
  - SafeBARS builds and studies a specific pre-fieldwork rehearsal scaffold.
- SafeBARS writing move:
  - Frame our study around what researchers want from synthetic stakeholder rehearsal, where they find it useful, and where they resist or distrust it.

### 4. AI-Driven Co-Construction of Synthetic Personas for Early-Stage B2B User Research

- ACM: https://dl.acm.org/doi/10.1145/3772363.3798319
- SIGCHI program: https://programs.sigchi.org/chi/2026/program/content/229539
- Why it matters: This is a close related-work threat because it also uses synthetic personas for user research.
- What to imitate:
  - Prototype-based exploratory study.
  - User-research workflow framing.
  - Discussion of where synthetic personas help early-stage ideation.
- How SafeBARS differs:
  - Synthetic persona work helps early-stage user research or persona ideation.
  - SafeBARS focuses on sensitive fieldwork, safety risk, consent, distress, shame, privacy, and non-replacement.
- SafeBARS writing move:
  - "Where synthetic persona systems often support ideation, SafeBARS supports ethical rehearsal and risk surfacing before contact with vulnerable communities."

## Tier 2: Papers to Imitate for Study Design

### 5. Human-AI Collaboration in Thematic Analysis using ChatGPT

- ACM: https://dl.acm.org/doi/10.1145/3613905.3650732
- Why it matters: This is a useful CHI-style example of evaluating an AI support tool in a research workflow.
- What to imitate:
  - Study tasks where participants use the AI tool on a realistic research activity.
  - Pre/post comparison of human work.
  - Design recommendations grounded in observed tool use.
- SafeBARS adaptation:
  - Participants draft or inspect a sensitive research plan, use SafeBARS, then revise the plan.
  - Analyze changes in questions, consent, safety procedure, and trust calibration.

### 6. AI for Qualitative User Research: LLM-Mediated Collaborative Sensemaking

- ACM: https://dl.acm.org/doi/10.1145/3772363.3799210
- SIGCHI program: https://programs.sigchi.org/chi/2026/program/content/225561
- Why it matters: Useful for positioning AI as a sensemaking scaffold, not an autonomous replacement.
- What to imitate:
  - System framing around gaps in human research workflow.
  - Multiple tool functions supporting data collection, synthesis, and interpretation.
  - "AI as scaffold" language.
- SafeBARS adaptation:
  - SafeBARS supports planning-stage sensemaking: identifying risks, missing stakeholders, and revision opportunities.

### 7. How Our AI-assisted Qualitative Analysis Failed

- ACM: https://dl.acm.org/doi/10.1145/3641237.3691672
- Why it matters: Good cautionary paper for writing limitations honestly.
- What to imitate:
  - Be explicit about failure modes.
  - Discuss why generic AI assistance can fail in qualitative work.
  - Use "failure" as contribution, not embarrassment.
- SafeBARS adaptation:
  - Include a section on when SafeBARS is not useful: weak prompts, overtrust, generic model responses, culturally thin stakeholder behavior, or safety risks the system misses.

## Tier 3: Domain Papers to Imitate for Online Fraud / Older Adult Context

### 8. "Auntie, Please Don't Fall for Those Smooth Talkers": How Chinese Younger Family Members Safeguard Seniors from Online Fraud

- Link: https://arxiv.org/abs/2501.10803
- ACM: https://dl.acm.org/doi/10.1145/3706598.3714137
- Why it matters: Strong CHI domain paper on senior-targeted online fraud and family support.
- What to imitate:
  - Ecosystem view: older adults, younger family members, scammers, platforms, institutions.
  - Taxonomy-building style.
  - Sensitivity to family pressure, refusal of help, emotional burden, and cultural context.
- SafeBARS adaptation:
  - Use this to justify stakeholder profiles beyond "older adult victim": affected participant, family helper, community worker, institutional gatekeeper.

### 9. Hear Us, then Protect Us: Navigating Deepfake Scams and Safeguard Interventions with Older Adults through Participatory Design

- ACM: https://dl.acm.org/doi/10.1145/3706598.3714423
- SIGCHI program: https://programs.sigchi.org/chi/2025/program/content/189528
- Why it matters: Strong CHI example of participatory design with older adults around scam protection.
- What to imitate:
  - Respecting participant autonomy and dignity.
  - Using simulated scam materials carefully.
  - Reporting design implications around safeguarding, literacy, and shared responsibility.
- SafeBARS adaptation:
  - Our system should help researchers notice whether their planned interventions preserve autonomy or drift into paternalism.

### 10. Experiencer, Helper, or Observer: Online Fraud Intervention for Older Adults Through Role-based Simulation

- Link: https://arxiv.org/abs/2601.12324
- ACM: https://dl.acm.org/doi/10.1145/3772318.3791003
- Why it matters: Closest "simulation for fraud prevention" paper.
- What to imitate:
  - Clear role-based simulation design.
  - Experimental comparison across roles.
  - Concrete anti-fraud scenario construction.
- How SafeBARS differs:
  - ROLESafe teaches older adults to recognize fraud.
  - SafeBARS helps researchers rehearse study plans before fieldwork.
- SafeBARS writing move:
  - "Unlike role-based simulations for end-user education, SafeBARS uses stakeholder rehearsal as a researcher-facing preparation method."

### 11. Intergenerational Support for Deepfake Scams Targeting Older Adults

- Link: https://arxiv.org/html/2508.11579v1
- Why it matters: Shows online safety around scams is relational and family-mediated.
- What to imitate:
  - Focus on trusted relationships.
  - Include family/youth support as part of scam resilience.
  - Show why a single "older adult user" persona is too simple.
- SafeBARS adaptation:
  - Include a family helper stakeholder profile and risk dimensions around family pressure, autonomy, and disclosure.

## Tier 4: Caution / Boundary Papers

### 12. Large Language Models that Replace Human Participants Can Harmfully Misportray and Flatten Identity Groups

- Link: https://arxiv.org/abs/2402.01908
- Nature Machine Intelligence: https://www.nature.com/articles/s42256-025-00986-z
- Why it matters: Strong evidence for why SafeBARS must avoid replacement claims.
- What to imitate:
  - Clear ethical warning.
  - Identity flattening as a central risk.
  - Discuss positionality and representational limits.
- SafeBARS adaptation:
  - Use this in the abstract/intro to say SafeBARS does not model vulnerable communities as data sources.

### 13. The Challenges of Synthetic Users in UX Research

- ACM Interactions: https://dl.acm.org/doi/10.1145/3779007
- Why it matters: Useful practitioner-facing critique of synthetic users.
- What to imitate:
  - Plain-language critique.
  - Clear cautions for when synthetic users can mislead UX research.
- SafeBARS adaptation:
  - Helps explain the project to supervisors/reviewers without becoming too technical.

## Best Three Papers to Copy Structurally

If we can only closely imitate three papers:

1. **CoBRA** for system contribution and agent-control logic.
2. **Simulacrum of Stories** for ethical framing and researcher study.
3. **Hear Us, then Protect Us** for sensitive fraud/older-adult participatory context.

This gives SafeBARS a clean CHI identity:

> CoBRA-like controllability + Simulacrum-like non-replacement ethics + CHI fraud/older-adult sensitivity.

## Proposed CHI Paper Skeleton to Imitate

### Abstract

Problem, system, study, findings, implications.

Do not say "we simulate older adults." Say:

> We explore how bias-calibrated synthetic stakeholders can scaffold researchers' pre-fieldwork rehearsal of sensitive action research plans.

### Introduction

1. Sensitive action research can harm if researchers enter fieldwork with weak questions or unclear safety procedures.
2. LLM role-play is tempting but risky because synthetic participants can be mistaken for evidence.
3. Prior work shows controllable agents are possible, but also warns against participant replacement.
4. SafeBARS reframes synthetic stakeholders as rehearsal prompts for researcher reflection.
5. Contributions.

### Related Work

1. Controllable LLM agents and synthetic users.
2. LLMs in qualitative/user research.
3. Participatory/action research and non-replacement ethics.
4. Online fraud prevention with older adults/vulnerable communities.
5. Trust calibration and bounded AI tools.

### System

Show the workflow:

1. researcher enters study plan;
2. selects stakeholder profile;
3. rehearses interview/workshop/consent script;
4. compares provider responses;
5. receives reflection report;
6. revises plan.

Important figures:

- Figure 1: SafeBARS workflow.
- Figure 2: Bias/risk profile dimensions.
- Figure 3: Example rehearsal and reflection report.
- Figure 4: Provider comparison view.

### Study

Feasible version:

- 6-8 researchers/design students, or if limited, initial expert walkthrough + 3-5 dry-run cases.
- Task: improve a sensitive online-fraud-prevention research plan.
- Data: initial plan, rehearsal transcript, reflection report, revised plan, short interview.
- Analysis: code changes in plan quality, risk identification, trust calibration, and overtrust.

### Findings

Potential finding categories to look for:

1. SafeBARS surfaced sensitive wording that researchers initially overlooked.
2. Stakeholder profiles helped researchers consider privacy, shame, trust, and burden.
3. Provider comparison made model instability visible.
4. Participants valued rehearsal but worried about overtrust and cultural thinness.
5. Revised plans improved consent, skip options, data boundaries, and question wording.

### Discussion

1. Synthetic stakeholders as rehearsal, not replacement.
2. Designing for productive discomfort without false authority.
3. Multi-provider comparison as trust calibration.
4. Limits of bias sliders and model-based role-play.
5. Implications for AI-assisted HCI research preparation.

## Immediate Reading Assignment

Read in this order:

1. CoBRA.
2. Simulacrum of Stories.
3. Large Language Models in Qualitative Research.
4. Auntie, Please Don't Fall for Those Smooth Talkers.
5. Hear Us, then Protect Us.
6. ROLESafe.
7. AI-Driven Co-Construction of Synthetic Personas.
8. Human-AI Collaboration in Thematic Analysis.

For each paper, extract:

- problem sentence;
- contribution sentence;
- study method;
- figure/table style;
- limitation paragraph;
- one sentence SafeBARS can imitate.

## What to Tell the Supervisor

I found a paper model that makes the project more concrete. The paper can be positioned between CoBRA-style controllable agents and recent CHI critiques of LLMs as qualitative participants. The novelty is not simulating vulnerable people, but designing a bounded rehearsal scaffold that helps researchers identify risks in study plans before fieldwork. I am now using CHI fraud/older-adult papers as the test context and CHI qualitative-research/AI-tool papers as the study design model.

