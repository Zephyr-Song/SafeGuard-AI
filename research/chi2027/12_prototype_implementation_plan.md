# Prototype Implementation Plan

Last updated: 2026-06-16

## Goal

Transform the existing SafeGuard-AI prototype into a minimal SafeBARS prototype for formative CHI study sessions.

The first implementation should support one complete research rehearsal loop:

1. Researcher enters an action research plan.
2. Researcher selects a stakeholder role and bias profile.
3. Researcher chats with the synthetic stakeholder.
4. System generates a reflection report.
5. Researcher exports the session for study analysis.

## Existing Code Assets

### app.py

Current role:

- Flask application entry point.
- Provides routes for starting learning, submitting responses, transparency analysis, and reports.

Reuse plan:

- Keep Flask app structure.
- Add SafeBARS routes under `/api/safebars/*`.
- Add a new researcher-facing page, likely `templates/safebars.html`.

### modules/scenario_simulator.py

Current role:

- Manages anti-fraud learning scenarios and multi-round user responses.

Reuse plan:

- Keep as reference.
- Do not force SafeBARS into the old learning scenario model.
- Extract useful ideas: rounds, active sessions, red flags, summaries.

Potential new module:

- `modules/rehearsal_engine.py`

### modules/transparency_dashboard.py

Current role:

- Explains AI decisions, bias checks, and counterfactuals.

Reuse plan:

- Adapt ideas into researcher-facing reflection:
  - hidden assumptions
  - safety gaps
  - missing stakeholders
  - limitation warnings

Potential new module:

- `modules/reflection_dashboard.py`

### modules/safety_guardian.py

Current role:

- Detects distress and safety risks.

Reuse plan:

- Reuse distress detection concepts.
- Add researcher-facing safety review:
  - whether questions are too direct
  - whether participant exit routes are missing
  - whether support resources are absent

### modules/learning_tracker.py

Current role:

- Tracks learning sessions and progress.

Reuse plan:

- Use as reference for session logging.
- SafeBARS needs simpler session logs for research analysis.

Potential new module:

- `modules/rehearsal_logger.py`

### modules/ai_analyzer.py

Current role:

- Calls LLM API to analyze user responses.

Reuse plan:

- Reuse OpenAI-compatible API calling pattern.
- Add a more general LLM client or extend this class for stakeholder chat and reflection analysis.

Potential new module:

- `modules/llm_client.py`

## Proposed New Modules

### modules/bias_profile.py

Responsibilities:

- Define bias/risk-response dimensions.
- Validate 0-4 values.
- Convert numeric profiles into prompt instructions.
- Provide presets.

Core classes:

- `BiasProfile`
- `BiasDimension`
- `BiasProfileLibrary`

### modules/stakeholder_agent.py

Responsibilities:

- Define stakeholder roles.
- Create stakeholder agent prompts.
- Generate stakeholder responses.

Core classes:

- `StakeholderAgent`
- `StakeholderRole`
- `StakeholderFactory`

### modules/rehearsal_engine.py

Responsibilities:

- Manage SafeBARS rehearsal sessions.
- Store research plan, selected stakeholder, conversation turns, and profile settings.
- Coordinate stakeholder responses.

Core classes:

- `ResearchPlan`
- `RehearsalSession`
- `RehearsalEngine`

### modules/reflection_dashboard.py

Responsibilities:

- Analyze the research plan and conversation.
- Produce reflection reports.
- Identify missing stakeholders, ethical risks, safety gaps, and trust calibration notes.

Core classes:

- `ReflectionReport`
- `ReflectionDashboard`

### modules/rehearsal_logger.py

Responsibilities:

- Export sessions to JSON and Markdown.
- Support study analysis.
- Avoid identifiable participant data by default.

## Proposed Routes

### Page Route

`GET /safebars`

Returns researcher-facing prototype interface.

### API Routes

`POST /api/safebars/start`

Input:

- research_plan
- selected_stakeholder_role
- bias_profile

Output:

- session_id
- stakeholder_agent
- limitation_note

`POST /api/safebars/message`

Input:

- session_id
- message

Output:

- stakeholder_response
- safety_flags
- bias_expression_notes

`POST /api/safebars/reflection`

Input:

- session_id

Output:

- reflection_report

`GET /api/safebars/session/<session_id>`

Output:

- full session data

`GET /api/safebars/export/<session_id>`

Output:

- markdown or json export

## Prototype UI v1

Single-page layout:

1. Research plan panel.
2. Stakeholder role selector.
3. Bias profile controls.
4. Chat panel.
5. Reflection report panel.
6. Export button.

Important UI text:

- "Synthetic stakeholders are fictional rehearsal aids. They do not represent real participants or communities."
- "Use this output to identify assumptions and questions for real fieldwork, not as evidence."

## Fallback Mode

If LLM API is unavailable, the prototype should still work for demonstration with scripted responses.

Fallback behavior:

- Use rule-based stakeholder response templates.
- Use bias profile values to select response style.
- Generate reflection report from heuristics.

This ensures the formative study is not blocked by API issues.

## First Engineering Milestone

Milestone name:

SafeBARS v0.1

Target capability:

- Start a session.
- Select affected participant or family helper.
- Configure a bias profile preset.
- Send 3-5 messages.
- Generate a simple reflection report.
- Export session.

## Implementation Order

1. Create data classes for research plan, bias profile, stakeholder agent, and rehearsal session.
2. Implement prompt mapping from bias profile to stakeholder response instructions.
3. Implement rehearsal engine with in-memory sessions.
4. Implement reflection dashboard with heuristic analysis.
5. Add Flask API routes.
6. Add simple HTML template.
7. Test one demo case.
8. Add export.

## Demo Case 1

Title:

Community workshop on online fraud prevention for older adults.

Researcher plan:

"I want to interview older adults about suspicious online investment messages and then run a community workshop teaching them how to identify scams."

Stakeholder:

Affected Participant.

Bias profile:

- shame_stigma_sensitivity: 4
- privacy_sensitivity: 4
- institutional_distrust: 3
- help_seeking_reluctance: 3
- distress_sensitivity: 3

Expected rehearsal value:

The stakeholder should push back on direct questions about loss, ask privacy questions, resist recording, and reveal that the plan needs a clearer distress and exit procedure.

## Demo Case 2

Title:

Family helper support plan after online fraud.

Stakeholder:

Family Helper.

Bias profile:

- authority_trust: 3
- urgency_sensitivity: 3
- victim_blaming_risk: 3
- privacy_sensitivity: 2

Expected rehearsal value:

The stakeholder may want immediate action and may unintentionally blame the affected person, helping the researcher revise family-facing materials.

## Engineering Risks

- LLM responses may not follow bias profile reliably.
- Reflection report may be too generic.
- UI may look like a generic chatbot.
- Logs may capture sensitive study data if not designed carefully.

## Risk Controls

- Keep all profiles visible to the researcher.
- Add limitation warnings in interface and export.
- Include bias-expression notes for transparency.
- Avoid claiming realism.
- Use structured outputs for reflection reports.
- Add explicit "questions to verify with real participants" section.

