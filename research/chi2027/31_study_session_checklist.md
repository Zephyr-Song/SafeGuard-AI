# SafeBARS Study Session Checklist

Last updated: 2026-06-17

## Purpose

Use this checklist when running each formative study session.

## Before the Session

- [ ] Assign participant ID, such as P01.
- [ ] Confirm participant meets recruitment criteria.
- [ ] Prepare participant information and consent form.
- [ ] Prepare pre/post research plan template.
- [ ] Start SafeBARS locally:

```bash
python run_safebars.py
```

- [ ] Open:

```text
http://127.0.0.1:5050/safebars
```

- [ ] Check that the page loads.
- [ ] Check that stakeholder presets load.
- [ ] Prepare note-taking document.
- [ ] If recording, confirm audio/screen recording settings and consent.

## Opening Script

Say:

"This study is about the prototype and research-planning workflow, not about evaluating your research ability. The synthetic stakeholders are fictional rehearsal aids. They do not represent real participants or communities. You can skip any question or stop at any time."

## Consent

- [ ] Confirm participant has read study information.
- [ ] Confirm voluntary participation.
- [ ] Confirm whether audio recording is allowed.
- [ ] Confirm whether screen recording is allowed.
- [ ] Remind participant not to include real personal or third-party identifying information.

## Step 1: Initial Plan

Ask participant to complete:

- [ ] Study goal.
- [ ] Target community.
- [ ] Planned method.
- [ ] Draft questions or activity script.
- [ ] Expected risks.
- [ ] Stakeholders considered.
- [ ] Safety plan.

Save as:

```text
P##_initial_plan.md
```

## Step 2: Prototype Walkthrough

Show:

- [ ] Research plan input.
- [ ] Stakeholder preset.
- [ ] Bias/risk-response sliders.
- [ ] Rehearsal chat.
- [ ] Reflection report.
- [ ] Revised plan area.

Emphasize:

- [ ] Outputs are not participant evidence.
- [ ] The goal is to find assumptions and risks to check later.

## Step 3: Rehearsal Task

Ask participant to:

- [ ] Enter or paste their initial plan.
- [ ] Select a stakeholder profile.
- [ ] Ask the stakeholder to react to an interview question, workshop script, consent language, or safety procedure.
- [ ] Try at least 3 turns.
- [ ] Generate reflection report.
- [ ] Optionally adjust sliders or switch stakeholder preset.

Observe:

- [ ] What questions they ask.
- [ ] Which stakeholder responses they notice.
- [ ] Whether they mention ethical or safety concerns.
- [ ] Whether they trust, doubt, or challenge the synthetic response.

## Step 4: Revised Plan

Ask participant to revise their plan in the interface or template.

Prompt:

"Based on the rehearsal, what would you change before real fieldwork?"

Save:

- [ ] Revised plan in SafeBARS.
- [ ] Revised plan in external study document if needed.

## Step 5: Export Session

In SafeBARS:

- [ ] Click Export.
- [ ] Confirm JSON export exists.
- [ ] Confirm Markdown export exists.

Expected folder:

```text
data/safebars/
```

Rename or copy using participant ID if needed:

```text
P##_safebars_session.md
P##_safebars_session.json
```

## Step 6: Interview

Use:

```text
research/chi2027/22_interview_guide_v0.md
```

Focus on:

- [ ] What was useful.
- [ ] What was misleading or insufficient.
- [ ] What changed in the plan.
- [ ] What risks were surfaced.
- [ ] How participant understood limitations.
- [ ] What should be improved.

## After the Session

- [ ] Stop recording, if used.
- [ ] Save field notes immediately.
- [ ] Check exported logs for accidental identifying information.
- [ ] Replace names with participant ID.
- [ ] Store raw data securely.
- [ ] Write a 5-10 minute session memo.

## Session Memo Template

```text
Participant ID:
Date:
Session duration:

Initial plan summary:

Most important prototype interaction:

Risks surfaced:

Plan revisions:

Trust calibration observations:

Prototype issues:

Potential quote:

Follow-up notes:
```

## Stop Criteria

Pause or stop the session if:

- Participant appears uncomfortable.
- Participant shares personal sensitive experiences unrelated to the task.
- Participant asks to stop.
- Recording or data handling becomes unclear.

