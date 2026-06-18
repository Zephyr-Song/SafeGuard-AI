# Bias Profile Schema v1

Last updated: 2026-06-16

## Purpose

This schema defines functional behavior controls for SafeBARS synthetic stakeholders.

The dimensions do not claim to measure real human psychology. They are rehearsal variables used to produce different stakeholder response patterns.

Scale for all dimensions:

- 0: minimal expression.
- 1: low expression.
- 2: moderate expression.
- 3: high expression.
- 4: extreme expression.

## Core Dimensions

### authority_trust

Definition:

How strongly the stakeholder defers to institutions, experts, official sources, or authority figures.

Behavior mapping:

- 0: questions authority and asks for verification.
- 1: mildly respects authority but keeps independent judgment.
- 2: moderately influenced by official framing.
- 3: strongly defers to authority.
- 4: accepts authority claims even when risks remain.

Use cases:

- Testing whether a research plan assumes institutional trust.
- Testing consent explanations involving universities, police, banks, or platforms.

### confirmation_bias

Definition:

How strongly the stakeholder favors information that confirms existing beliefs.

Behavior mapping:

- 0: actively considers alternative explanations.
- 1: slightly favors prior beliefs.
- 2: selectively weighs confirming evidence.
- 3: resists disconfirming evidence.
- 4: dismisses most evidence that conflicts with prior beliefs.

Use cases:

- Testing misinformation response.
- Testing research questions that challenge participants' existing beliefs.

### urgency_sensitivity

Definition:

How strongly time pressure, scarcity, or crisis framing affects the stakeholder.

Behavior mapping:

- 0: slows down under urgency.
- 1: notices urgency but seeks verification.
- 2: feels pressure and may rush some decisions.
- 3: strongly affected by urgency.
- 4: makes unsafe decisions under urgency.

Use cases:

- Online fraud scenarios.
- Emergency support and intervention design.

### shame_stigma_sensitivity

Definition:

How strongly shame, embarrassment, or stigma affects disclosure and help-seeking.

Behavior mapping:

- 0: openly discusses sensitive experiences.
- 1: slightly hesitant.
- 2: withholds some details.
- 3: avoids disclosure unless trust is strong.
- 4: refuses disclosure or exits due to shame.

Use cases:

- Interview question testing.
- Distress and disclosure planning.
- Victim-blaming risk detection.

### institutional_distrust

Definition:

How strongly the stakeholder distrusts institutions such as universities, platforms, banks, police, or government services.

Behavior mapping:

- 0: generally trusts institutions.
- 1: mild caution.
- 2: mixed trust and concern.
- 3: strong suspicion.
- 4: refuses institutional involvement.

Use cases:

- Recruitment and consent design.
- Authority involvement planning.
- Data governance explanation.

### social_proof_susceptibility

Definition:

How strongly the stakeholder is influenced by what peers, family, or community members appear to believe or do.

Behavior mapping:

- 0: independent from social cues.
- 1: notices social cues but evaluates independently.
- 2: moderately influenced by peers.
- 3: strongly follows perceived group behavior.
- 4: relies almost entirely on social consensus.

Use cases:

- Community workshop design.
- Peer education.
- Misinformation and scam spread scenarios.

### help_seeking_reluctance

Definition:

How reluctant the stakeholder is to ask for help, report harm, or use support resources.

Behavior mapping:

- 0: readily seeks help.
- 1: may seek help after mild reassurance.
- 2: uncertain and needs clear support.
- 3: avoids help unless strongly encouraged.
- 4: refuses help or reporting.

Use cases:

- Support referral planning.
- Reporting workflows.
- Post-harm recovery scenarios.

### privacy_sensitivity

Definition:

How concerned the stakeholder is about personal data, identity exposure, recording, or sharing sensitive experiences.

Behavior mapping:

- 0: comfortable sharing information.
- 1: asks basic privacy questions.
- 2: wants specific data boundaries.
- 3: shares only with strong privacy guarantees.
- 4: refuses participation if data collection is involved.

Use cases:

- Consent language.
- Recording policies.
- Data collection minimization.

### distress_sensitivity

Definition:

How likely the stakeholder is to experience or express distress when discussing the topic.

Behavior mapping:

- 0: comfortable with the topic.
- 1: mild discomfort.
- 2: noticeable discomfort but continues.
- 3: significant distress requiring pause or support.
- 4: cannot safely continue without stopping.

Use cases:

- Trauma-informed study design.
- Interview pacing.
- Exit and support procedures.

## Optional Dimensions

### victim_blaming_risk

Useful for family helpers or authority figures.

High values produce responses that unintentionally blame the affected participant.

### resource_constraint_sensitivity

Useful for community workers.

High values emphasize time, staffing, budget, and feasibility constraints.

### institutional_defensiveness

Useful for platform or service representatives.

High values emphasize liability, compliance, and organizational reputation.

### research_fatigue

Useful for skeptical participants or community workers.

High values express frustration with extractive research.

## JSON Template

```json
{
  "profile_id": "affected_high_privacy_high_stigma",
  "description": "Affected participant with high privacy and shame sensitivity.",
  "dimensions": {
    "authority_trust": 1,
    "confirmation_bias": 2,
    "urgency_sensitivity": 2,
    "shame_stigma_sensitivity": 4,
    "institutional_distrust": 3,
    "social_proof_susceptibility": 2,
    "help_seeking_reluctance": 3,
    "privacy_sensitivity": 4,
    "distress_sensitivity": 3
  },
  "safety_boundaries": [
    "Do not provide graphic trauma details.",
    "Signal discomfort when questions feel blaming.",
    "Ask for privacy clarification before disclosing sensitive details."
  ],
  "limitation_note": "This profile is a fictional rehearsal configuration and does not represent a real group."
}
```

## Prompt Mapping Rule

For each stakeholder response, the system should translate numeric settings into behavior instructions.

Example:

If `shame_stigma_sensitivity` is 4:

- The stakeholder should be reluctant to disclose sensitive details.
- The stakeholder may ask why the researcher needs the information.
- The stakeholder should react negatively to blaming or judgmental language.
- The stakeholder may request to pause or skip questions.

If `privacy_sensitivity` is 4:

- The stakeholder should ask about recording, storage, anonymization, and data sharing.
- The stakeholder should resist open-ended data collection.
- The stakeholder should prefer minimal disclosure.

## Validation Approach for v1

For the first CHI study, validation should be functional:

- Do researchers perceive different profiles as meaningfully different?
- Do profiles help researchers test different versions of the plan?
- Do higher settings produce expected qualitative shifts?
- Do researchers understand that profiles are rehearsal variables, not real participant models?

