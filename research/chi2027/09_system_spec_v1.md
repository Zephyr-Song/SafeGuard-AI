# SafeBARS System Specification v1

Last updated: 2026-06-16

## System Goal

SafeBARS helps researchers rehearse high-risk action research plans with bias-calibrated synthetic stakeholders before entering real fieldwork.

The system is designed to support:

- Reflexive research planning.
- Stakeholder coverage.
- Ethical risk discovery.
- Safety protocol improvement.
- Trust calibration toward synthetic stakeholders.

The system is not designed to produce evidence about real communities.

## Target Users

Primary users:

- HCI researchers.
- UX researchers.
- CSCW researchers.
- AI safety researchers.
- Graduate students planning user studies or action research.

Secondary users:

- Supervisors reviewing study plans.
- Ethics reviewers evaluating early protocols.
- Research teams planning community engagement.

## Primary Use Case

A researcher is preparing an action research project about online fraud prevention for older adults or another high-risk digital safety group. Before recruiting participants, the researcher wants to test:

- Whether interview questions may cause distress.
- Whether the plan misses important stakeholders.
- Whether consent and exit procedures are clear.
- Whether the intervention assumes too much trust in institutions.
- Whether the researcher is unintentionally blaming victims.

SafeBARS lets the researcher rehearse the plan with synthetic stakeholders whose risk-response profiles can be adjusted.

## User Workflow

### Step 1: Enter Research Plan

The researcher enters:

- Study title.
- Research goal.
- Target community.
- Planned method.
- Draft interview questions or intervention script.
- Known risks.
- Desired rehearsal focus.

Example:

"I am designing a community workshop to help older adults recognize online investment scams. I plan to interview older adults who have encountered suspicious messages and ask them to describe their decision-making."

### Step 2: Select Stakeholder Set

The researcher selects or generates stakeholders:

- Primary affected participant.
- Family helper or caregiver.
- Community worker.
- Platform representative.
- Authority figure.
- Skeptical or disengaged participant.

The system should recommend missing stakeholders based on the research plan.

### Step 3: Configure Bias and Risk-Response Profiles

For each stakeholder, the researcher can select preset profiles or adjust individual dimensions.

Example dimensions:

- Authority trust: 0-4.
- Shame/stigma sensitivity: 0-4.
- Help-seeking reluctance: 0-4.
- Institutional distrust: 0-4.
- Urgency/scarcity sensitivity: 0-4.
- Privacy sensitivity: 0-4.

### Step 4: Rehearsal Interaction

The researcher interacts with one or multiple stakeholders.

Supported rehearsal modes:

- Interview rehearsal.
- Consent explanation rehearsal.
- Intervention walkthrough.
- Risk scenario stress test.
- Stakeholder conflict rehearsal.

### Step 5: Reflection Dashboard

The system summarizes:

- Stakeholder reactions.
- Signs of distress or burden.
- Missed stakeholders.
- Hidden assumptions.
- Potential victim-blaming language.
- Safety protocol gaps.
- Trust calibration warnings.
- Suggested revisions.

### Step 6: Revise Research Plan

The researcher revises the research plan and exports:

- Revised interview questions.
- Safety protocol checklist.
- Stakeholder map.
- Open questions for real participants.
- Limitations of synthetic rehearsal.

## Core Modules

### 1. Research Plan Parser

Input:

- Free-text research plan.
- Structured fields.

Output:

- Domain.
- Target community.
- Planned method.
- Stakeholder candidates.
- Risk keywords.
- Safety needs.

v1 implementation:

- Rule-based extraction plus optional LLM analysis.

### 2. Stakeholder Generator

Input:

- Parsed research plan.
- Selected stakeholder roles.
- Bias profile presets.

Output:

- Stakeholder agent definitions.

Each stakeholder definition includes:

- Role.
- Relationship to research context.
- Knowledge level.
- Goals and concerns.
- Bias/risk-response profile.
- Boundaries and limitations.

### 3. Bias Profile Controller

Input:

- Bias dimension values from 0-4.

Output:

- Behavioral instructions for stakeholder responses.

v1 implementation:

- Prompt-level behavior mapping.
- No representation engineering.
- No fine-tuning.

### 4. Rehearsal Chat Engine

Input:

- Researcher message.
- Stakeholder definition.
- Conversation context.

Output:

- Stakeholder response.
- Optional safety flags.
- Optional bias-expression notes.

v1 implementation:

- OpenAI-compatible API if available.
- Fallback scripted/demo responses if API unavailable.

### 5. Reflection Analyzer

Input:

- Research plan.
- Conversation logs.
- Stakeholder profiles.

Output:

- Reflection report.

Analysis categories:

- Missing stakeholders.
- Ethical risks.
- Safety gaps.
- Assumptions.
- Participant burden.
- Over-trust warnings.
- Suggested revisions.

### 6. Trust Calibration Layer

Purpose:

Prevent users from treating synthetic stakeholder outputs as real participant evidence.

Mechanisms:

- Persistent limitation banner.
- Report section: "What this rehearsal cannot tell you."
- Prompts asking researchers what must be verified with real participants.
- Exported limitation statement.

### 7. Logging and Export

Logged data:

- Research plan.
- Stakeholder profiles.
- Bias settings.
- Conversation turns.
- Reflection report.
- Researcher revisions.

Export formats:

- JSON for analysis.
- Markdown summary for study sessions.

## Data Model

### ResearchPlan

- id
- title
- goal
- target_community
- domain
- planned_method
- draft_questions
- known_risks
- rehearsal_focus
- created_at

### StakeholderAgent

- id
- role
- name
- context_relationship
- goals
- concerns
- knowledge_level
- bias_profile
- safety_boundaries
- limitation_note

### BiasProfile

- authority_trust
- confirmation_bias
- urgency_sensitivity
- shame_stigma_sensitivity
- institutional_distrust
- social_proof_susceptibility
- help_seeking_reluctance
- privacy_sensitivity
- distress_sensitivity

### RehearsalSession

- id
- research_plan_id
- stakeholder_ids
- turns
- safety_flags
- reflection_report
- created_at

### ReflectionReport

- missing_stakeholders
- hidden_assumptions
- ethical_risks
- safety_gaps
- participant_burden
- trust_calibration_notes
- recommended_revisions
- open_questions_for_real_fieldwork

## v1 Prototype Scope

Must have:

- Research plan input form.
- Stakeholder selection.
- Bias profile presets.
- Single-stakeholder chat.
- Reflection report.
- Markdown/JSON export.
- Limitation warnings.

Should have:

- Multi-stakeholder comparison.
- Pre/post plan revision view.
- Simple dashboard visualization.

Out of scope for v1:

- Representation engineering.
- Fine-tuning.
- Claims of psychological validity.
- Multi-agent autonomous simulation.
- Real participant recruitment support.

## Example Stakeholder Presets

### Cautious Affected Participant

- High privacy sensitivity.
- Moderate institutional distrust.
- High shame/stigma sensitivity.
- Low authority trust.

### Authority-Deferential Participant

- High authority trust.
- Moderate urgency sensitivity.
- Low help-seeking reluctance.
- Low institutional distrust.

### Family Helper

- High protective orientation.
- Moderate victim-blaming risk.
- High desire for actionable guidance.
- Medium privacy sensitivity.

### Community Worker

- High practical constraints.
- High concern about participant burden.
- Medium institutional trust.
- High need for feasible procedures.

## Study-Relevant Outputs

The prototype should create artifacts useful for evaluation:

- Initial plan.
- Rehearsal transcript.
- Reflection report.
- Revised plan.

These artifacts can be compared to examine whether SafeBARS changed the researcher's plan.

## Success Criteria for Prototype v1

The prototype is successful enough for formative study if:

1. A participant can enter a research plan in under 5 minutes.
2. A participant can interact with at least one stakeholder agent.
3. The stakeholder response visibly reflects the selected bias profile.
4. The reflection report identifies at least 3 actionable research-planning issues.
5. The system clearly communicates that outputs are rehearsal aids, not real participant evidence.

