# Expanded Literature Matrix v0

Last updated: 2026-06-16

This matrix expands the initial seed list into a first working literature base for SafeBARS.

## Legend

- Central: must be discussed in the paper.
- Support: useful for positioning.
- Threat: could make reviewers question novelty.
- Method: useful for study or system design.

## 1. Controllable LLM Agents and Social Simulation

### CoBRA: Cognitive Bias Regulator for Social Agents

- Link: https://github.com/AISmithLab/CoBRA
- Paper: https://arxiv.org/abs/2509.13588
- Category: Central
- Core claim: Natural-language persona descriptions are insufficient for reliable LLM social agents; cognitive bias can be quantified and controlled through CBI and Behavioral Regulation Engine.
- Method: Bias index, benchmark tasks, behavior regulation, cross-model validation.
- Relevance to SafeBARS: Primary methodological inspiration. SafeBARS transfers the idea of measurable behavior control from social agents to synthetic stakeholders for research rehearsal.
- Gap: CoBRA focuses on controlling agents, not supporting human researchers in action research planning.
- Notes: Must be framed as inspiration, not baseline to beat.

### Generative Agents: Interactive Simulacra of Human Behavior

- Link: https://arxiv.org/abs/2304.03442
- Category: Central background
- Core claim: LLM agents can create believable individual and social behaviors in simulated environments.
- Method: Agent architecture with memory, reflection, planning.
- Relevance to SafeBARS: Provides the broader foundation for agent-based social simulation.
- Gap: Believability is not sufficient for high-risk research preparation. SafeBARS emphasizes controllability, limitation awareness, and researcher reflexivity.

### Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human Users in Agentic Evaluations

- Link: https://arxiv.org/abs/2601.17087
- Category: Central caution / Threat
- Core claim: LLM-simulated users are unreliable proxies for human users in agentic evaluations, with robustness, calibration, fairness, and dialect-related problems.
- Method: User study across countries and comparison between simulated and human users in agentic tasks.
- Relevance to SafeBARS: Strong support for our decision not to position synthetic stakeholders as replacements for human participants.
- Gap: Focuses on evaluation proxies. SafeBARS focuses on pre-fieldwork rehearsal and trust calibration.

## 2. Synthetic Participants and Replacement Risks

### Large Language Models that Replace Human Participants Can Harmfully Misportray and Flatten Identity Groups

- Link: https://arxiv.org/abs/2402.01908
- Category: Central
- Core claim: LLMs used as replacements for human participants can misportray and flatten identity groups, especially when identity and positionality matter.
- Method: Analytical argument plus empirical studies across demographic identities.
- Relevance to SafeBARS: Provides the ethical foundation for our "rehearsal, not replacement" framing.
- Gap: Offers caution and mitigation but does not design a researcher-facing scaffold for safer pre-fieldwork planning.

### Can AI Replace Human Subjects? A Large-Scale Replication of Psychological Experiments with LLMs

- Link: https://arxiv.org/abs/2409.00128
- Category: Support / Caution
- Core claim: GPT-4 can replicate many psychological main effects but struggles with interactions, confidence intervals, and false positives.
- Method: Large-scale replication of psychological experiments.
- Relevance to SafeBARS: Supports a nuanced stance: LLMs may complement human research but cannot fully replace human subjects.
- Gap: Focuses on psychology experiment replication, not HCI action research planning.

### Can Large Language Models Replace Humans in the Systematic Review Process?

- Link: https://arxiv.org/abs/2310.17526
- Category: Support / Caution
- Core claim: LLMs can help with some review tasks under reliable prompts, but substantial caution is needed for human-out-of-the-loop workflows.
- Method: Pre-registered evaluation of GPT-4 in systematic review screening and extraction.
- Relevance to SafeBARS: Useful for arguing that AI assistance needs oversight and task boundaries.
- Gap: Not about participant simulation or action research.

## 3. Participatory AI, Action Research, and Reflexivity

### The Participatory Turn in AI Design: Theoretical Foundations and the Current State of Practice

- Link: https://arxiv.org/abs/2310.00907
- Category: Central
- Core claim: Participatory AI varies widely in how much substantive agency stakeholders receive; the paper provides a framework for evaluating participation.
- Method: Theoretical synthesis plus empirical investigation with AI researchers/practitioners.
- Relevance to SafeBARS: Helps ground why SafeBARS must not replace participation and should prepare researchers for better participation.
- Gap: Does not focus on synthetic stakeholders or pre-fieldwork rehearsal tools.

### Enabling Value Sensitive AI Systems through Participatory Design Fictions

- Link: https://arxiv.org/abs/1912.07381
- Category: Support / Method inspiration
- Core claim: Participatory design fictions can help study stakeholder values in AI systems.
- Method: Conceptual argument and preliminary case study.
- Relevance to SafeBARS: Design fictions are an important analogy: SafeBARS uses synthetic stakeholders as rehearsal fictions, not factual evidence.
- Gap: Does not use controllable LLM stakeholder profiles.

### Participatory Action Research

- Link: https://en.wikipedia.org/wiki/Participatory_action_research
- Category: Foundational background
- Core claim: PAR emphasizes participation and action by communities affected by research; research should be done with people, not on or for them.
- Relevance to SafeBARS: Supports the ethical boundary that synthetic stakeholders cannot replace community participation.
- Gap: Needs primary sources for final paper, but this is useful as a quick orientation.

### Community-Based Participatory Research

- Link: https://en.wikipedia.org/wiki/Community-based_participatory_research
- Category: Foundational background
- Core claim: CBPR emphasizes community partnership, co-learning, local relevance, mutual benefit, and long-term relationships.
- Relevance to SafeBARS: Helps define what ethical action research preparation should respect.
- Gap: Need to cite primary CBPR literature in final paper.

## 4. Online Fraud and Anti-Fraud Education

### ROLESafe: Experiencer, Helper, or Observer

- Link: https://arxiv.org/abs/2601.12324
- Category: Threat / Related work
- Core claim: Role-based online fraud simulation can improve older adults' fraud awareness; Experiencer and Helper roles significantly improved ability to identify fraud.
- Method: Between-subjects study with 144 older adults in China.
- Relevance to SafeBARS: This is a close anti-fraud education paper and is the main reason SafeBARS should not be framed as another end-user fraud education system.
- Gap: ROLESafe targets older adult learners. SafeBARS targets researchers preparing action research.

### Intergenerational Support for Deepfake Scams Targeting Older Adults

- Link: https://arxiv.org/abs/2508.11579
- Category: Support
- Core claim: Older adults rely on trusted relationships to detect deepfake scams; youth can be active partners in intergenerational resilience.
- Method: Focus groups with 37 older adults.
- Relevance to SafeBARS: Supports inclusion of family helper and intergenerational stakeholder roles.
- Gap: Focuses on deepfake scams, not researcher-facing scaffolding.

### Sixteen Years of Phishing User Studies: What Have We Learned?

- Link: https://arxiv.org/abs/2109.04661
- Category: Support
- Core claim: Phishing user studies show mixed results about demographics and susceptibility; training improves detection, but findings vary.
- Method: Systematic review and meta-analysis.
- Relevance to SafeBARS: Useful background for digital safety and anti-phishing education; warns against simplistic assumptions about demographic vulnerability.
- Gap: Not about LLMs or action research planning.

## 5. Trust Calibration and Human-AI Interaction

### Guidelines for Human-AI Interaction

- Link: https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/
- Category: Foundational support
- Core claim: Human-AI systems need interaction guidelines that support appropriate expectations, feedback, corrections, and graceful failure.
- Method: Synthesis and validation of guidelines.
- Relevance to SafeBARS: Useful for interface design, especially limitation warnings, feedback, and trust calibration.
- Gap: General HAI guidelines, not synthetic stakeholder rehearsal.

### Calibrated Trust in Dealing with LLM Hallucinations

- Link: https://arxiv.org/abs/2512.09088
- Category: Support
- Core claim: Hallucinations do not produce blanket mistrust; users calibrate trust based on context, prior experience, expertise, and risk.
- Method: Qualitative study with 192 participants.
- Relevance to SafeBARS: Supports studying trust calibration as an outcome.
- Gap: Focuses on hallucinations in everyday LLM use, not research planning.

### Trust-Calibrated Code Review

- Link: https://arxiv.org/abs/2606.01969
- Category: Method analogy
- Core claim: Reviewing LLM-generated multi-file changes is a trust-calibration problem; workflow and interface design should surface risk at useful levels of attention.
- Method: Participatory design with practitioners plus prototype validation survey.
- Relevance to SafeBARS: Useful analogy for designing a workflow around trust calibration rather than a generic AI output.
- Gap: Software engineering domain, not HCI fieldwork planning.

## Initial Related Work Positioning

SafeBARS should be positioned between four conversations:

1. Controllable LLM agents and social simulation.
2. Risks of synthetic users replacing real participants.
3. Participatory/action research and stakeholder agency.
4. Trust-calibrated human-AI tools for high-stakes work.

The central gap:

There is growing work on generating or evaluating synthetic users, and growing concern that they should not replace human participants. However, less is known about how to design AI tools that use synthetic stakeholders safely as bounded rehearsal aids for researchers preparing high-risk action research.

