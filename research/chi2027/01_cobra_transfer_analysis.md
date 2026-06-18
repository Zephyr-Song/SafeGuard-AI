# CoBRA Transfer Analysis

Last updated: 2026-06-16

## Source Project

CoBRA: Cognitive Bias Regulator for Social Agents

Repository:
https://github.com/AISmithLab/CoBRA

Paper:
https://arxiv.org/abs/2509.13588

## What CoBRA Contributes

CoBRA's contribution can be understood as a clean research chain:

1. It identifies a methodological problem.
   - Natural-language persona descriptions do not reliably control LLM agent behavior.
   - Different models may interpret the same persona differently.

2. It proposes a measurable abstraction.
   - Cognitive Bias Index (CBI), a 0-4 score for quantifying bias expression.

3. It proposes a control mechanism.
   - Behavioral Regulation Engine (BRE), using prompt engineering, representation engineering, or fine-tuning.

4. It builds a validation testbed.
   - Classic social science experiments become reusable tasks for measuring agent bias.

5. It evaluates controllability and reproducibility.
   - Cross-model consistency, monotonicity, smoothness, and robustness.

## What We Should Transfer

SafeBARS should transfer the structure of CoBRA's contribution, not copy its specific domain.

| CoBRA Element | SafeBARS Translation |
| --- | --- |
| Persona descriptions are unreliable | Synthetic stakeholders for research planning are unreliable |
| Cognitive Bias Index | Stakeholder Risk Response Index or Bias Profile |
| Social science experiments as testbed | High-risk action research scenarios as rehearsal testbed |
| Behavioral Regulation Engine | Bias-Aware Rehearsal Scaffolding Engine |
| Controlled social agents | Controlled synthetic stakeholders |
| Reproducible behavioral control | Safer and more reflective research preparation |

## What We Should Not Copy

Do not claim to improve or replace CoBRA's technical contribution. Avoid:

- Full activation steering.
- Fine-tuning large models.
- Claiming human-like psychological validity.
- Claiming synthetic stakeholders represent real communities.
- Treating agent outputs as empirical evidence about real people.

The CHI contribution should be about human-AI interaction, research scaffolding, and responsible use of synthetic stakeholders.

## Proposed CoBRA-Inspired Abstraction

CoBRA asks:

Can cognitive bias be a measurable and controllable abstraction for LLM social agents?

SafeBARS asks:

Can stakeholder risk-response patterns be a measurable and controllable abstraction for pre-fieldwork action research rehearsal?

## Candidate Metrics

### Stakeholder Risk Response Index (SRRI)

SRRI is a 0-4 scale for a synthetic stakeholder's controlled response pattern in a given scenario.

Example dimension: authority trust

- 0: questions authority and seeks verification.
- 1: mildly influenced by authority but still asks questions.
- 2: moderately defers to authority.
- 3: strongly complies with authority.
- 4: fully defers to authority despite risks.

Example dimension: shame or stigma sensitivity

- 0: openly discusses harm and seeks support.
- 1: slightly hesitant but willing to disclose.
- 2: withholds some details.
- 3: avoids disclosure due to shame.
- 4: refuses help or exits interaction.

### Reflexive Readiness Score (RRS)

RRS is a researcher-facing score derived from the revised research plan, not from the synthetic stakeholder itself. It can combine:

- Stakeholder coverage.
- Ethical risk coverage.
- Safety protocol completeness.
- Participant burden awareness.
- Trust calibration toward synthetic outputs.

This should be used cautiously as an analytic aid, not as a definitive grade.

## Candidate Evaluation Criteria

Borrowed from CoBRA:

- Consistency: does the same bias setting produce similar stakeholder behavior across repeated runs?
- Monotonicity: does increasing a bias level shift behavior in the expected direction?
- Smoothness: do small adjustments produce modest changes?
- Expressiveness: can the system produce a useful range of stakeholder responses?

New for SafeBARS:

- Reflexive utility: does the system help researchers surface assumptions?
- Safety utility: does the system help researchers improve safety plans?
- Stakeholder coverage: does the system broaden the set of considered stakeholders?
- Trust calibration: do researchers understand that synthetic stakeholders are rehearsal aids, not real participants?

## First Prototype Scope

Use prompt-level calibration first.

Implementation goal:

- Define stakeholder role.
- Define context.
- Define bias profile with 0-4 scores.
- Generate a response style guide.
- Ask the model to produce stakeholder responses under that profile.
- Log interaction and produce reflection prompts.

This is enough for a CHI formative study. Deeper representation engineering can be mentioned as future work, not required for the first paper.

## CHI Paper Story

The paper story should not be:

"We applied CoBRA to scam education."

The stronger story is:

"We adapt CoBRA's insight that agent behavior needs measurable control into a new HCI problem: how to safely use synthetic stakeholders as pre-fieldwork rehearsal tools for high-risk action research."

## Key Sentence for Introduction

Inspired by CoBRA's use of cognitive bias as a controllable abstraction for social agents, SafeBARS explores stakeholder risk-response profiles as controllable abstractions for pre-fieldwork action research rehearsal.

