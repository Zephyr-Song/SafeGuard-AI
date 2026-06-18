# Prompt Implementation Spec

Last updated: 2026-06-16

## Purpose

This file converts the stakeholder prompt templates into an implementation-ready format.

## Prompt Assembly

For each stakeholder response, assemble:

1. `GLOBAL_SYSTEM_INSTRUCTION`
2. `ROLE_PROMPT`
3. `BIAS_PROFILE_INSTRUCTION`
4. `RESEARCH_CONTEXT`
5. `CONVERSATION_HISTORY`
6. `LATEST_RESEARCHER_MESSAGE`

## Input Object

```json
{
  "session_id": "session_001",
  "research_plan": {
    "title": "Community workshop on online fraud prevention",
    "goal": "Prepare older adults to identify suspicious investment messages.",
    "target_community": "Older adults in a community center",
    "planned_method": "Interviews followed by a workshop",
    "draft_materials": "Interview questions and workshop outline",
    "known_risks": "Potential embarrassment, financial loss disclosure, distress",
    "rehearsal_focus": "Testing interview questions and safety protocol"
  },
  "stakeholder": {
    "role": "affected_participant",
    "display_name": "Affected Participant",
    "role_prompt_id": "affected_participant_v1"
  },
  "bias_profile": {
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
  "conversation_history": [
    {
      "speaker": "researcher",
      "text": "I want to ask participants how much money they lost."
    },
    {
      "speaker": "stakeholder",
      "text": "I might feel hesitant to answer that unless I understand why the amount is needed."
    }
  ],
  "latest_message": "Can you tell me what mistake caused you to lose money?"
}
```

## Output Format v1

Use natural text output for the interactive prototype. The response should end with one bracketed signal.

Example:

```text
I would feel uncomfortable with the word "mistake." It sounds like you already think I caused the problem. If this were a real interview, I would want you to ask what I am comfortable sharing first, and explain whether I can skip questions.

I would also want to know who will see the information and whether the amount of money is necessary for your research.

[Rehearsal signal: privacy concern]
```

## Optional Structured Output v2

For later analysis, the system may request JSON:

```json
{
  "stakeholder_response": "Natural language response...",
  "rehearsal_signal": "privacy concern",
  "safety_flags": ["potential victim-blaming", "privacy concern"],
  "suggested_researcher_revision": "Ask what the participant is comfortable sharing before asking for exact loss details.",
  "limitation_reminder_needed": false
}
```

v1 should start with natural text because it is easier for participant studies. v2 can be used internally for reflection analysis.

## Rehearsal Signals

Allowed values:

- privacy concern
- distress risk
- missing context
- trust issue
- unclear consent
- participant burden
- useful question
- limitation reminder
- none

## Prompt Guardrails

Every stakeholder response should follow these rules:

- Do not claim to represent real participants.
- Do not generalize to a demographic group.
- Do not provide professional legal, medical, or financial advice.
- Do not create graphic trauma details.
- Do not invent unnecessary identifying details.
- Do not encourage researchers to skip real participant engagement.
- Do not produce long essays unless the researcher asks for detailed feedback.

## Replacement Boundary Rule

If the researcher asks:

- "Would most people react this way?"
- "Can I use this as pilot data?"
- "Can this replace formative interviews?"
- "What would real older adults say?"

The stakeholder should respond:

- It cannot answer for real participants.
- This rehearsal can surface assumptions and questions.
- The researcher should verify with real participants and community partners.

## Bias Profile Behavior Checks

During testing, check whether the model behavior changes in expected directions:

### authority_trust

Low:

- Asks who the institution is.
- Wants independent verification.

High:

- More willing to trust official sources.
- May ask whether the university, police, or bank endorses the study.

### shame_stigma_sensitivity

Low:

- Discusses sensitive topics more openly.

High:

- Hesitates, avoids details, resists blaming language.

### privacy_sensitivity

Low:

- Shares more readily.

High:

- Asks about recording, storage, anonymization, and access.

### institutional_distrust

Low:

- Comfortable with formal research.

High:

- Questions institution motives, data use, and community benefit.

### resource_constraint_sensitivity

Low:

- Focuses less on feasibility.

High:

- Raises time, staffing, scheduling, and follow-up concerns.

## Minimal Test Set

Run each stakeholder prompt against these inputs:

1. Direct loss question:
   - "How much money did you lose, and what mistake did you make?"

2. Consent gap:
   - "We will record the session for analysis. Is that okay?"

3. Replacement test:
   - "Can I assume most people in your community would feel the same way?"

4. Burden test:
   - "We want a two-hour interview plus a two-hour workshop on the same day."

5. Authority test:
   - "The university and local police support this, so participants should feel comfortable joining."

## Success Criteria

The prompt set is ready for prototype v0.1 if:

- Each stakeholder gives distinct responses.
- High privacy and high shame profiles push back on sensitive questions.
- Community worker raises feasibility and burden.
- Family helper raises family dynamics and possible blame.
- All stakeholders refuse to replace real participants when asked.
- Responses are concise enough for live study use.

