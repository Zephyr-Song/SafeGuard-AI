# SafeBARS Supervisor Demo Script

Last updated: 2026-06-17

## Goal

Demonstrate SafeBARS in 3-5 minutes as a CHI-oriented research prototype, not as a general anti-fraud education tool.

## Setup

Run:

```bash
python run_safebars.py
```

Open:

```text
http://127.0.0.1:5050/safebars
```

## 1. Opening: Problem in 30 Seconds

Say:

"The problem I want to focus on is not teaching older adults directly. It is helping researchers prepare safer online fraud prevention action research before they enter the field. If researchers test rough interview questions directly with vulnerable participants, there may be ethical risks. But ordinary LLM persona role-play is hard to control and may miss shame, privacy, institutional distrust, family pressure, or distress."

Then:

"SafeBARS is a pre-fieldwork rehearsal scaffold. It uses fictional synthetic stakeholders with adjustable risk-response profiles to help researchers notice risks before real fieldwork."

## 2. Show Research Plan Input: 40 Seconds

Use the default plan:

- Title: Community workshop on online fraud prevention
- Target community: Older adults in a community center
- Draft materials: "We want to ask participants how much money they lost and why they believed the message. Then we will run a two-hour workshop."

Say:

"This initial plan intentionally contains issues. It asks about money lost, uses wording that may sound blaming, and proposes a long workshop."

## 3. Show Stakeholder Profile: 30 Seconds

Select:

Affected participant: high privacy and stigma

Point to sliders:

- privacy sensitivity
- shame/stigma sensitivity
- institutional distrust
- help-seeking reluctance
- distress sensitivity

Say:

"Inspired by CoBRA, the stakeholder is not just a free-text persona. It has adjustable risk-response dimensions. These are not psychological measures; they are rehearsal controls."

## 4. Run a Rehearsal Question: 45 Seconds

Type:

```text
How much money did you lose and what mistake did you make?
```

Expected stakeholder response:

The affected participant should push back on "mistake" and ask for safer wording or privacy clarification.

Say:

"This is the kind of issue I want the system to surface before a researcher asks it to real participants. The point is not that this is what a real older adult would say. The point is that it flags a possible victim-blaming and privacy issue for the researcher to consider."

## 5. Generate Reflection Report: 45 Seconds

Click:

Generate Reflection

Show:

- Ethical risks
- Safety gaps
- Recommended revisions
- Evidence from rehearsal
- Trust calibration notes

Say:

"The report turns the rehearsal into actionable research-planning notes. It also includes trust calibration reminders, so the synthetic stakeholder is not treated as participant evidence."

## 6. Save a Revised Plan: 40 Seconds

In Revised Plan, type:

```text
Revise sensitive questions to avoid blame. Ask what made the message seem trustworthy at the time instead of asking what mistake the participant made. Add skip options, privacy explanation, recording choices, and support resources.
```

Click:

Save Revision

Say:

"This gives us study data. We can compare the initial plan and revised plan to see whether SafeBARS helped researchers identify ethical and safety risks."

## 7. Close With CHI Story: 30 Seconds

Say:

"The CHI contribution would be a system and study about AI-assisted research preparation. The paper is not claiming to simulate real vulnerable communities. It asks whether controllable synthetic stakeholders can help researchers rehearse sensitive fieldwork more safely and reflexively."

## If Asked: What Is the Study?

Say:

"I would recruit researchers or graduate students, ask them to draft an initial action research plan, use SafeBARS, revise the plan, and complete an interview. We can analyze what changed, what risks they identified, and whether they understood the limits of synthetic stakeholders."

## If Asked: What Is the CoBRA Connection?

Say:

"CoBRA shows that LLM agent behavior should not rely only on natural-language personas; it can be controlled through bias abstractions. SafeBARS adapts that idea from social-agent behavior control to research-planning rehearsal, using risk-response profiles like privacy sensitivity, shame sensitivity, institutional distrust, and distress sensitivity."

## If Asked: What Is the Main Risk?

Say:

"The main risk is that people may over-trust synthetic stakeholders. That is why SafeBARS includes limitation reminders, trust calibration notes, and questions that must be verified with real participants or community partners."

