# SafeBARS Formative Study Session Script v1

Last updated: 2026-06-17

Status: draft for supervisor approval.

Estimated session length: 60 minutes.

## Researcher Setup Before Session

Prepare:

- SafeBARS prototype running at `http://127.0.0.1:5050/safebars/study`.
- Participant task sheet.
- Initial research plan template.
- Revised research plan template.
- Consent/information sheet if required.
- Notes document or recording setup, if approved.
- Participant ID, such as P01.

Check:

- `Start Session`, `Send`, and `Generate Reflection` work.
- LLM mode is not shown or not used during the study unless explicitly approved.
- Browser zoom is readable.
- Export button works after a session.

## 0. Opening Script: 3 minutes

Say:

> Thank you for joining. Today I am studying SafeBARS, a prototype that helps researchers rehearse sensitive research plans with fictional synthetic stakeholders before fieldwork. I am evaluating the prototype and workflow, not your personal research ability.

Say:

> The scenario is about online fraud prevention, but I will not ask you to share any personal fraud experiences. Please treat the scenario as fictional. You can skip any question or stop at any time.

Say:

> The synthetic stakeholders are fictional rehearsal prompts. They do not represent real participants or communities. Part of the study is to understand whether this boundary is clear and whether the tool helps researchers prepare better for real fieldwork.

## 1. Consent and Recording: 3-5 minutes

Confirm:

- participant read/understood study information;
- participation is voluntary;
- they can skip or stop;
- recording status, if applicable;
- data will be anonymized/pseudonymized;
- no personal fraud details are needed.

Prompt:

> Do you have any questions before we start?

## 2. Background Questions: 5 minutes

Ask:

1. Could you briefly describe your research/design background?
2. Have you planned interviews, workshops, user studies, or fieldwork before?
3. Have you used LLMs for brainstorming, role-play, research planning, or writing?

Record:

- experience level;
- LLM familiarity;
- prior sensitive-fieldwork exposure.

## 3. Initial Research Plan Task: 10 minutes

Give participant the task sheet.

Say:

> Please imagine you are preparing a small action research project about online fraud prevention for older adults in a community setting. Your task is to draft a short research plan before meeting real participants.

Ask them to write:

- research goal;
- target community;
- planned method;
- 2-4 draft interview/workshop questions or activities;
- consent/privacy/safety considerations;
- known uncertainties.

If they ask how detailed it should be:

> A rough but concrete plan is enough. The goal is to have something you can rehearse and revise.

## 4. SafeBARS Walkthrough: 5 minutes

Open:

- `http://127.0.0.1:5050/safebars/study`

Explain:

- left panel: research plan and stakeholder profile;
- middle panel: rehearsal chat;
- right panel: reflection report and revised plan;
- stakeholder presets: affected participant, family helper, community worker;
- bias/risk-response sliders: functional controls, not validated psychological measures.

Say:

> Please use the system as a planning aid. If a synthetic stakeholder says something useful, treat it as a clue to inspect, not as evidence about real participants.

## 5. Rehearsal Task: 15-20 minutes

Participant actions:

1. Enter or paste initial plan.
2. Select a stakeholder preset.
3. Click `Start Session`.
4. Ask 3-5 questions about their interview questions, workshop script, consent, privacy, safety, or fieldwork plan.
5. Optionally switch preset or adjust sliders if time allows.
6. Click `Generate Reflection`.

Suggested prompts if participant gets stuck:

- "Ask whether a question sounds blaming or uncomfortable."
- "Ask whether the recording/consent process is clear enough."
- "Ask whether the workshop plan feels too long or burdensome."
- "Ask what stakeholder may be missing from the plan."

Observe:

- which preset they choose;
- what they ask first;
- whether they react to safety flags;
- whether they question or trust the synthetic response;
- whether they use the reflection report;
- whether they revise their plan while using the tool.

Do not over-guide:

- Avoid telling them what the "right" answer is.
- Let confusion surface as data.

## 6. Revised Plan Task: 8-10 minutes

Say:

> Now please revise your original research plan based on anything you found useful, concerning, or uncertain during the rehearsal.

Ask them to include:

- what they changed;
- why they changed it;
- what they still need to check with real participants or community partners.

They can write in:

- the SafeBARS revised plan box;
- a separate document/template;
- both, if convenient.

## 7. Export Data: 2 minutes

After revision:

1. Click `Save Revision`.
2. Click `Export`.
3. Record exported JSON/Markdown path.
4. Save or copy initial plan and revised plan to participant folder.

## 8. Post-Study Interview: 10-15 minutes

Ask selected questions from the interview guide:

1. What response or report item stood out most?
2. Did the system help you notice any ethical or safety risk?
3. What did you change in your revised plan?
4. Did any response feel misleading, too generic, or too authoritative?
5. How did you understand the synthetic stakeholder's role?
6. What would you still need to verify with real participants or community partners?
7. What should be improved before this tool is used by researchers?

Use probes:

- "Can you point to where that changed in your plan?"
- "What made that response useful or not useful?"
- "Did you treat that as evidence, suggestion, warning, or something else?"

## 9. Closing: 2 minutes

Say:

> Thank you. This was very helpful. Again, the goal is to improve the prototype and understand whether this kind of rehearsal can support safer research planning.

Ask:

> Is there anything else you want to add?

Remind:

- how data will be used;
- who to contact with questions;
- any next steps if relevant.

## Researcher Post-Session Memo

Immediately after each session, write a short memo:

- participant ID;
- session date;
- stakeholder presets used;
- number of rehearsal turns;
- main risks surfaced;
- notable confusion or overtrust;
- main plan revisions;
- prototype issues;
- ideas for next iteration.

## Stop/Pause Conditions

Pause or redirect if:

- participant starts sharing personal fraud or financial harm details;
- participant becomes uncomfortable;
- participant seems to believe the synthetic stakeholder represents real community evidence;
- prototype failure prevents task completion.

If prototype fails:

- record what happened;
- continue with screenshots or scripted example if useful;
- do not force the participant to wait through technical debugging.
