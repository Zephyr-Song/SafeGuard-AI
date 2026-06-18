# SafeBARS Citation-to-Claim Map

Last updated: 2026-06-17

This file maps paper claims to supporting literature. It is meant to help write the introduction, related work, and discussion without losing the argument.

## Claim 1: LLM agents can generate plausible social behavior, but plausibility alone is not sufficient for high-risk research use.

Use citations:

- Generative Agents: https://arxiv.org/abs/2304.03442
- CoBRA: https://arxiv.org/abs/2509.13588
- Lost in Simulation: https://arxiv.org/abs/2601.17087

How to phrase:

Recent work demonstrates that LLM agents can produce plausible social behavior and that their behavioral tendencies can be controlled. However, studies of simulated users also show that plausibility does not guarantee reliability, robustness, or fairness.

SafeBARS implication:

SafeBARS should evaluate usefulness for researcher reflection, not human-likeness.

## Claim 2: Synthetic participants are risky when treated as replacements for real people, especially when identity, vulnerability, and lived experience matter.

Use citations:

- Large Language Models that Replace Human Participants Can Harmfully Misportray and Flatten Identity Groups: https://arxiv.org/abs/2402.01908
- Can AI Replace Human Subjects?: https://arxiv.org/abs/2409.00128
- Out of One, Many: https://www.cambridge.org/core/journals/political-analysis/article/out-of-one-many-using-language-models-to-simulate-human-samples/035D7C8A55A8C1DA2C3CBB9FE5B8087F

How to phrase:

Prior work warns that using LLMs as participant substitutes can flatten identity groups and obscure uncertainty. SafeBARS therefore treats synthetic stakeholder outputs as rehearsal prompts rather than empirical evidence.

SafeBARS implication:

Put this boundary in the abstract, system UI, study protocol, and limitations.

## Claim 3: Participatory and action research require preserving stakeholder agency, not shortcutting it.

Use citations:

- The Participatory Turn in AI Design: https://arxiv.org/abs/2310.00907
- Participatory Design: The Third Space in HCI: https://dl.acm.org/doi/10.1207/S15327051HCI1523_02
- Community-Based Participatory Research review: https://www.annualreviews.org/content/journals/10.1146/annurev.publhealth.19.1.173
- Value Sensitive Design: https://dl.acm.org/doi/10.1207/s15327051hci0803_3

How to phrase:

Participatory and action research traditions emphasize stakeholder agency, situated knowledge, and collaborative inquiry. An AI scaffold for this space should help researchers prepare for engagement rather than replace engagement.

SafeBARS implication:

The system should be described as "pre-fieldwork" or "pre-participation" support.

## Claim 4: Online fraud prevention is a sensitive but tractable test context because research can trigger shame, privacy concern, distrust, and family pressure.

Use citations:

- ROLESafe: https://arxiv.org/abs/2601.12324
- Intergenerational Support for Deepfake Scams Targeting Older Adults: https://arxiv.org/abs/2508.11579
- Sixteen Years of Phishing User Studies: https://arxiv.org/abs/2109.04661
- Folk Models of Home Computer Security: https://dl.acm.org/doi/10.1145/1753326.1753385

How to phrase:

Digital safety and fraud-prevention research is not only a technical education problem. It involves social relationships, mental models, trust, shame, and uncertainty, making it a useful context for studying research-plan rehearsal.

SafeBARS implication:

Use fraud prevention as the concrete scenario, but keep the contribution about sensitive action research scaffolding.

## Claim 5: Safe use of AI research tools requires trust calibration, not only stronger model outputs.

Use citations:

- Guidelines for Human-AI Interaction: https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/
- Calibrated Trust in Dealing with LLM Hallucinations: https://arxiv.org/abs/2512.09088
- Trust-Calibrated Code Review: https://arxiv.org/abs/2606.01969

How to phrase:

Human-AI interaction research emphasizes appropriate expectations, correction, and graceful failure. In SafeBARS, trust calibration means that researchers should understand stakeholder responses as prompts for inspection rather than validation.

SafeBARS implication:

Evaluation should ask whether participants overtrust the synthetic stakeholders, how they describe the system's limits, and whether they revise plans for the right reasons.

## Claim 6: The contribution can be evaluated in 1-2 months through a focused formative study.

Use citations:

- Ethics and Society Review: https://dl.acm.org/doi/10.1145/3442188.3445938
- Reflective Design: https://dl.acm.org/doi/10.1145/1013115.1013154
- Scenario-Based Design: https://dl.acm.org/doi/10.1145/175276.175278

How to phrase:

Because SafeBARS is a formative scaffold rather than a validated simulation of real communities, the study can focus on how researchers use the tool to reflect on and revise study plans.

SafeBARS implication:

Primary outcomes:

- issues surfaced in reflection;
- changes between pre/post study plans;
- perceived usefulness and limits;
- trust calibration and overreliance concerns.

## Claim 7: SafeBARS is original because it combines four lines of work that are usually separate.

Use citations:

- CoBRA for controllable bias-aware agents.
- Synthetic participant critique for non-replacement framing.
- Participatory/action research for ethical grounding.
- Human-AI trust calibration for interaction design.

How to phrase:

SafeBARS contributes a new design space for bounded synthetic stakeholders: not synthetic participants for evidence generation, and not end-user fraud education, but a pre-fieldwork rehearsal scaffold for researchers.

SafeBARS implication:

This should become the central novelty paragraph in the supervisor meeting and CHI introduction.

## Paper Claims That Need More Evidence

### Claim: SafeBARS improves research plan quality.

Current evidence:

- We can evaluate this through pre/post plans and coding.

Need:

- Pilot study data.
- Coding protocol reliability check.
- Concrete examples of improved consent wording, safety protocol, question wording, or referral planning.

### Claim: SafeBARS reduces ethical blind spots.

Current evidence:

- Reflection dashboard categories.

Need:

- Participant explanations during think-aloud.
- Expert/supervisor judgment or coding of issues surfaced.

### Claim: SafeBARS prevents overtrust.

Current evidence:

- UI limitation text and explicit non-replacement framing.

Need:

- Interview questions about what participants would and would not use the tool for.
- Observe whether participants cite synthetic stakeholder responses as evidence or as prompts.

## Best Abstract Claim

SafeBARS explores how bias-calibrated synthetic stakeholders can be designed as bounded rehearsal aids for researchers preparing sensitive action research, helping them surface ethical and safety risks without treating simulated responses as substitutes for real community participation.

## Best Supervisor Pitch Claim

I am not trying to build another anti-fraud education tool. I am narrowing the problem to pre-fieldwork preparation: how researchers can safely rehearse sensitive online-fraud-prevention studies with controllable synthetic stakeholders before meeting real vulnerable participants.
