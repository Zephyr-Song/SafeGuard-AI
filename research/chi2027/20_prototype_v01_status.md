# SafeBARS Prototype v0.1 Status

Last updated: 2026-06-16

## Summary

SafeBARS v0.1 has been implemented as a local Flask prototype inside the existing SafeGuard-AI project.

The prototype currently supports:

- Research plan input.
- Stakeholder preset selection.
- Editable bias/risk-response sliders.
- Bias-profile-driven synthetic stakeholder responses.
- Rehearsal chat.
- Heuristic reflection report.
- Evidence notes from stakeholder turns in the reflection report.
- Revised research plan capture for pre/post comparison.
- JSON and Markdown session export.
- Optional LLM-backed stakeholder responses with deterministic fallback.
- Profile consistency check script for standard stress-test prompts.

This version is intentionally LLM-free so it can run without API access during early demonstrations and formative study planning.

## New Code Files

- `modules/bias_profile.py`
  - Defines 0-4 functional risk-response profiles.
  - Includes presets for affected participant, family helper, and community worker.

- `modules/stakeholder_agent.py`
  - Defines stakeholder roles.
  - Generates deterministic stakeholder responses based on role, message, and bias profile.

- `modules/rehearsal_engine.py`
  - Manages in-memory SafeBARS sessions.
  - Stores research plan, selected stakeholder, conversation turns, and profile settings.

- `modules/reflection_dashboard.py`
  - Produces researcher-facing reflection reports.
  - Flags missing stakeholders, hidden assumptions, ethical risks, safety gaps, participant burden, and trust calibration notes.
  - Extracts evidence quotes from stakeholder responses for report grounding.

- `modules/rehearsal_logger.py`
  - Exports sessions to `data/safebars/` as JSON and Markdown.

- `modules/llm_client.py`
  - Provides optional OpenAI-compatible LLM calls.
  - Falls back safely when no response is available.

- `modules/safebars_prompt_builder.py`
  - Assembles SafeBARS stakeholder prompts from role, bias profile, research plan, and conversation history.

- `templates/safebars.html`
  - Researcher-facing prototype interface.
  - Includes research plan input, bias sliders, rehearsal chat, reflection report, and revised plan capture.
  - Includes participant-facing task instructions and limitation reminders.
  - Supports study mode for participant sessions.

- `templates/safebars_brief.html`
  - Supervisor-facing visual summary page for project discussion.

- `run_safebars.py`
  - Local development runner for the SafeBARS prototype.

- `scripts/safebars_profile_check.py`
  - Runs deterministic profile checks across stakeholder presets and standard stress prompts.

- `scripts/compare_research_plans.py`
  - Generates heuristic hints for comparing initial and revised research plans.

## Updated Existing File

- `app.py`
  - Added `/safebars` page route.
  - Added `/safebars/study` participant study mode route.
  - Added `/safebars/brief` visual brief route.
  - Added `/api/safebars/options`.
  - Added `/api/safebars/start`.
  - Added `/api/safebars/message`.
  - Added `/api/safebars/reflection`.
  - Added `/api/safebars/session/<session_id>`.
  - Added `/api/safebars/export/<session_id>`.

## How to Run

```bash
python run_safebars.py
```

Then open:

```text
http://127.0.0.1:5050/safebars
```

## Verification Completed

Python syntax compilation passed for:

- `app.py`
- `run_safebars.py`
- all new SafeBARS modules

Flask test client checks passed:

- `GET /safebars` returns 200.
- `GET /safebars/study` returns 200.
- `GET /safebars/brief` returns 200.
- `GET /api/safebars/options` returns 200.
- `POST /api/safebars/start` creates a session.
- `POST /api/safebars/message` returns a stakeholder response.
- `POST /api/safebars/reflection` returns a reflection report.
- `POST /api/safebars/reflection` includes evidence notes when stakeholder turns contain rehearsal signals.
- `POST /api/safebars/revise` saves a revised research plan.
- `GET /api/safebars/options` reports whether an LLM API appears configured.

Profile check generated:

- `research/chi2027/profile_checks/safebars_profile_check_v0.json`

Example plan comparison generated:

- `research/chi2027/examples/example_plan_comparison.md`

## Current Limitations

- Stakeholder responses are deterministic templates, not LLM-generated.
- Bias profiles are functional rehearsal controls, not validated psychological measures.
- Reflection analysis is heuristic.
- Sessions are stored in memory until exported.
- The interface is sufficient for internal demonstration but should be polished before study use.

## Next Implementation Steps

1. Deepen literature matrix to 25-40 papers.
2. Add study mode toggle if needed after supervisor feedback.
3. Run profile consistency checks with LLM mode when API/network is stable.
4. Prepare final coding protocol after first formative sessions.
