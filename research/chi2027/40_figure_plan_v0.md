# SafeBARS CHI Figure Plan v0

Last updated: 2026-06-17

This file lists the figures likely needed for a CHI 2027 submission. The goal is to plan visuals early so the prototype, study, and paper tell the same story.

## Figure 1: Problem and Positioning

Purpose:

Show the key distinction:

- unsafe framing: synthetic stakeholders as participant replacement;
- SafeBARS framing: synthetic stakeholders as bounded pre-fieldwork rehearsal.

Recommended form:

A two-column conceptual diagram.

Left:

Researcher asks LLM persona what vulnerable participants would say, then treats output as evidence.

Right:

Researcher uses SafeBARS to rehearse a study plan, receives risk signals, revises plan, then verifies with real participants/community partners.

Paper location:

Introduction.

Why it matters:

This figure can make the originality clear in five seconds.

## Figure 2: SafeBARS Workflow

Purpose:

Show the end-to-end workflow.

Recommended stages:

1. Researcher enters study plan.
2. Researcher selects stakeholder role and risk-response profile.
3. Researcher rehearses interview/workshop scripts.
4. SafeBARS surfaces stakeholder responses and safety flags.
5. Researcher reviews reflection dashboard.
6. Researcher revises plan and identifies questions for real fieldwork.

Paper location:

System section.

Prototype source:

- `/safebars`
- `/safebars/study`

## Figure 3: Bias/Risk-Response Profile Interface

Purpose:

Show what "bias-aware" means concretely.

Recommended content:

- stakeholder preset selector;
- sliders for privacy sensitivity, shame/stigma sensitivity, institutional distrust, distress sensitivity, participant burden, etc.;
- limitation text that says the profile is a functional rehearsal control.

Paper location:

System design.

Important caption language:

Do not call these sliders validated psychological measures. Call them functional risk-response controls.

## Figure 4: Example Rehearsal Moment

Purpose:

Show how SafeBARS catches a concrete planning issue.

Example:

Researcher prompt:

"How much money did you lose and what mistake did you make?"

Synthetic stakeholder response:

Flags victim-blaming and suggests non-judgmental wording.

Recommended form:

Annotated screenshot or transcript excerpt with callouts:

- risky wording;
- stakeholder concern;
- safety flag;
- revised question.

Paper location:

System walkthrough or findings.

## Figure 5: Reflection Dashboard

Purpose:

Show how the system converts rehearsal into planning work.

Recommended content:

- ethical risks;
- safety gaps;
- participant burden;
- trust calibration notes;
- evidence-linked notes from stakeholder turns;
- recommended revisions.

Paper location:

System section.

Why it matters:

This supports the claim that SafeBARS is a scaffold, not a chatbot.

## Figure 6: Study Procedure

Purpose:

Show the formative study flow.

Recommended stages:

1. Consent and background.
2. Initial research plan.
3. SafeBARS rehearsal task.
4. Reflection dashboard review.
5. Revised research plan.
6. Interview.
7. Pre/post plan coding.

Paper location:

Method.

## Figure 7: Pre/Post Plan Revision Example

Purpose:

Show evidence of how participants changed a plan.

Recommended form:

Before/after table:

- interview question wording;
- consent/recording procedure;
- safety protocol;
- stakeholder involvement;
- follow-up support.

Paper location:

Findings.

Important:

Use anonymized excerpts from study data after the pilot/formative study. Until then, use the example files only for internal demonstration.

## Figure 8: Contribution Summary

Purpose:

End the paper discussion with a clear design-space contribution.

Recommended axes:

- replacement vs rehearsal;
- generic persona vs bias/risk-calibrated profile;
- free-form chat vs reflection scaffold;
- model confidence vs trust-calibrated limitation.

Paper location:

Discussion.

## Near-Term Visual Deliverables

Before meeting supervisor:

1. Use `/safebars/brief` as the live overview.
2. Capture one screenshot of the profile/rehearsal interface.
3. Capture one screenshot of the reflection dashboard.
4. Prepare one simple workflow diagram for the meeting packet.

Current screenshot files:

- `research/chi2027/screenshots/safebars_main_latest.png`
- `research/chi2027/screenshots/safebars_study_mode_latest.png`
- `research/chi2027/screenshots/safebars_brief_latest.png`

Note:

Use the `*_latest.png` screenshots. Earlier `safebars_brief.png` and `safebars_study_mode.png` were captured before restarting the latest Flask app and show a 404 page.

Before pilot/formative study:

1. Make sure participant study mode hides technical LLM settings.
2. Save screenshots of the exact interface participants used.
3. Archive the profile settings used in each session.

Before CHI paper writing:

1. Replace mock examples with real anonymized study excerpts.
2. Ensure each figure supports one contribution claim.
3. Avoid decorative diagrams that do not add evidence or explanation.
