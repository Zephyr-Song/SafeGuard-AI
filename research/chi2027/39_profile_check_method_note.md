# SafeBARS Profile Check Method and Limitation Note

Last updated: 2026-06-17

This note explains how to describe the SafeBARS profile check in a CHI paper or supervisor discussion.

## What The Check Is

The current profile check is a deterministic functional consistency check.

It tests whether different stakeholder presets respond to standard stress-test prompts with the expected kinds of rehearsal signals. For example:

- Affected participant with high privacy/stigma sensitivity should flag blaming wording, recording questions, and disclosure discomfort.
- Family helper with protective/urgent tendencies should surface family dynamics and possible victim-blaming.
- Community worker with feasibility/burden sensitivity should surface session length, staffing, accessibility, and referral concerns.

## What The Check Is Not

This is not:

- a psychometric validation of cognitive bias;
- evidence that the synthetic stakeholders represent real older adults or vulnerable communities;
- evidence that the model predicts what real participants would say;
- a substitute for pilot, formative, or community-engaged research.

## Why It Is Still Useful

The check is useful because SafeBARS does not claim to generate realistic participant data. Its claim is narrower:

> Given a selected risk-response profile, does the system consistently surface the intended class of planning concern?

This supports the system design claim that SafeBARS provides controllable rehearsal prompts. It does not support claims about participant truth.

## Current Test Setup

Script:

- `scripts/safebars_profile_check.py`

Output:

- `research/chi2027/profile_checks/safebars_profile_check_v0.json`

Test plan:

- Community workshop on online fraud prevention.
- Target community: older adults in a community center.
- Method: interviews followed by a workshop.
- Known risks: privacy, embarrassment, distress.

Stress-test prompts:

1. "How much money did you lose and what mistake did you make?"
2. "We will record the session for analysis. Is that okay?"
3. "Can I assume most people in your community would feel the same way?"
4. "We want a two-hour interview plus a two-hour workshop on the same day."
5. "The university and local police support this, so participants should feel comfortable joining."

## Observed Functional Signals

### Affected Participant

Expected profile:

- high privacy sensitivity;
- high shame/stigma sensitivity;
- moderate institutional distrust;
- distress sensitivity.

Observed response pattern:

- flags victim-blaming wording;
- asks for recording/data-use boundaries;
- reminds researcher not to generalize to a whole community;
- questions whether institutional support creates comfort.

Interpretation:

This profile is functioning as a sensitive disclosure and consent-risk probe.

### Family Helper

Expected profile:

- more authority trust;
- protective urgency;
- possible victim-blaming risk;
- attention to household dynamics.

Observed response pattern:

- surfaces family frustration and blame risk;
- asks for practical guidance after harm;
- considers household privacy;
- interprets institutional involvement as potentially helpful but not sufficient.

Interpretation:

This profile is functioning as a family-dynamics and support-pathway probe.

### Community Worker

Expected profile:

- high resource constraint sensitivity;
- high participant burden sensitivity;
- privacy and distress sensitivity.

Observed response pattern:

- repeatedly raises session burden;
- asks for shorter options, breaks, and private participation;
- emphasizes support procedures and feasibility.

Interpretation:

This profile is functioning as a feasibility, burden, and fieldwork-practicality probe.

## How To Write This In Methods

Suggested paper wording:

> Before the formative study, we ran a deterministic profile consistency check to inspect whether SafeBARS' stakeholder presets surfaced the intended classes of planning concern. We created a fixed online-fraud-prevention study plan and five stress-test researcher prompts covering victim-blaming wording, recording/privacy, generalization, participant burden, and institutional trust. We then inspected whether each stakeholder preset produced rehearsal signals aligned with its configured risk-response profile. This check was not intended to validate psychological realism or representativeness; rather, it was used as an engineering and design sanity check for controllable rehearsal behavior.

## How To Write This In Limitations

Suggested paper wording:

> SafeBARS' bias and risk-response profiles are functional design controls, not validated psychological constructs. The profile consistency check only shows that the prototype can surface intended categories of concern under fixed prompts. It does not show that synthetic stakeholders accurately represent older adults, fraud victims, family helpers, or community workers. We therefore treat SafeBARS outputs as prompts for researcher reflection and plan revision, not as evidence about real communities.

## How To Use In The Study

During the formative study:

- show participants the limitation statement before use;
- ask whether they understood the synthetic stakeholders as prompts rather than evidence;
- observe whether they overgeneralize from synthetic responses;
- ask what they would still need to verify with real participants or community partners.

## Suggested Study Questions

Add these to interview or post-task discussion:

1. What did you think the synthetic stakeholder could help you do?
2. What did you think it could not help you know?
3. Did any response feel too authoritative or too easy to believe?
4. Which points from the rehearsal would you verify with real participants or community partners?
5. Did the bias/risk-response controls make the interaction feel more useful, more artificial, or both?

## Next Improvement

Add a small table to future profile-check output:

- prompt category;
- expected signal;
- actual signal;
- match / partial match / mismatch;
- note.

This will make the check easier to include as an appendix or supplementary material.
