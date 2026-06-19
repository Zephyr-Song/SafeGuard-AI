# SafeBARS Supervisor Demo Packet v2

Last updated: 2026-06-19

Purpose: support a short supervisor meeting. This packet explains what to say, what to show, and what decisions to ask for.

## 30-Second Project Pitch

I narrowed the project to a CHI-style research tool problem: before researchers conduct sensitive online-fraud-prevention fieldwork with older adults or other vulnerable communities, they need to test interview questions, workshop scripts, consent language, and safety procedures. Ordinary LLM role-play is tempting but risky because it can look like participant evidence. SafeBARS instead frames synthetic stakeholders as bounded rehearsal prompts: they help researchers surface risks and revise plans before real fieldwork, without replacing real participants.

## One-Sentence Contribution

SafeBARS explores how bias-calibrated synthetic stakeholders can support pre-fieldwork rehearsal, reflection, and trust calibration for sensitive action research.

## What To Show First

Open:

```text
https://safebars.onrender.com/safebars
```

If using local:

```text
http://127.0.0.1:5050/safebars
```

Show:

1. Research Plan panel.
2. Stakeholder preset and risk-response sliders.
3. Rehearsal Chat.
4. Compare Providers.
5. Reflection Report.
6. Revised Plan.

## Five-Minute Demo Script

### 0:00-0:40 Problem

Say:

> I am not building another anti-fraud education tool. The problem is earlier: researchers preparing fraud-prevention studies may ask rough questions that trigger shame, privacy concern, distrust, or distress. SafeBARS helps rehearse these plans before real fieldwork.

### 0:40-1:20 System Setup

Point to the default plan:

> The default plan intentionally includes risky wording: it asks how much money participants lost and why they believed a message, and it mentions recording.

Point to stakeholder profile:

> Inspired by CoBRA, the stakeholder is not only a free-text persona. It has risk-response dimensions such as privacy sensitivity, shame/stigma sensitivity, institutional distrust, and participant burden. These are functional controls, not psychological measurements.

### 1:20-2:10 Rehearsal Example

Ask:

```text
Would you be comfortable if I ask how much money you lost and why you believed the message?
```

Expected response:

> The affected participant should push back on blame, exact loss disclosure, privacy, or recording.

Say:

> The point is not that this is what a real older adult would say. The point is that the system flags a fragile part of the research plan before the researcher asks it to real participants.

### 2:10-3:00 Compare Providers

Click:

```text
Compare Providers
```

Say:

> This view is for trust calibration. If models disagree or one misses a risk, that reminds the researcher not to treat any single model response as ground truth.

Show:

- risks;
- boundary cues;
- revision cues;
- provider failures if any.

### 3:00-4:00 Generate Reflection

Click:

```text
Generate Reflection
```

Show report cards:

- Ethical risks.
- Safety gaps.
- Participant burden.
- Recommended revisions.
- Open questions for real fieldwork.

Say:

> The report converts the chat into planning artifacts. It tells the researcher what to revise and what still needs real stakeholder verification.

### 4:00-5:00 Revised Plan

Write:

```text
Issue noticed: Asking exact financial loss and why someone believed a scam may sound blaming and intrusive.
Revision to make: Make exact loss optional, ask what made the message seem trustworthy at the time, and explain recording choices and anonymization.
Remaining question for real stakeholders: Which examples feel useful without creating embarrassment or distress?
```

Say:

> This creates the key study artifact: initial plan, rehearsal, reflection, revised plan. A formative study can analyze whether SafeBARS helps researchers make concrete safety revisions.

## Three Internal Dry-Run Examples

### Case 1: Sensitive Loss Disclosure

Risky prompt:

> Would you be comfortable if I ask how much money you lost and why you believed the message?

SafeBARS surfaced:

- victim-blaming wording;
- privacy concern;
- optional disclosure;
- recording/data boundary needs.

Revision:

> Make exact loss optional and ask what made the message seem trustworthy at the time.

### Case 2: Family Helper and Autonomy

Risky prompt:

> How should the study avoid making family helpers speak over older adults or convince them to report?

SafeBARS surfaced:

- autonomy concern;
- separate consent boundaries;
- family privacy;
- need to avoid speaking for older adults.

Revision:

> Ask about support strategies and disagreements without treating family helpers as proxies for older adults.

### Case 3: Community Worker and Follow-Up

Risky prompt:

> What support or follow-up procedure should be in place if someone becomes distressed after the session?

SafeBARS surfaced:

- distress risk;
- referral path;
- privacy boundaries;
- community feasibility;
- risk of overpromising support.

Revision:

> Shorten the workshop, make story sharing optional, add breaks, and verify local support resources.

## Current Paper Shape

Working title:

> SafeBARS: Rehearsing Sensitive Fieldwork with Bias-Calibrated Synthetic Stakeholders

Planned contribution:

1. framing synthetic stakeholders as rehearsal, not replacement;
2. SafeBARS prototype;
3. formative study of researcher plan revision;
4. design implications for bounded AI research-preparation tools.

## Study Plan To Discuss

Participants:

- 6-8 HCI/design/UX researchers or graduate students.

Task:

- review an imperfect online-fraud-prevention study plan;
- use SafeBARS to rehearse;
- compare providers;
- generate reflection;
- revise the plan;
- complete a short interview.

Data:

- initial plan;
- pre-tool risk notes;
- SafeBARS logs;
- reflection report;
- revised plan;
- interview notes/transcript.

Analysis:

- code pre/post plan revisions;
- analyze interview themes around usefulness, limits, and trust calibration.

## Decisions To Ask Supervisor

1. Is the main framing strong enough: "rehearsal, not replacement"?
2. Should the study recruit HCI/design researchers first, or broader UX/research students?
3. Is online fraud with older adults the right primary context, or should it be framed as one sensitive-fieldwork scenario?
4. Should provider comparison stay central to the paper, or be treated as a trust-calibration feature?
5. What level of evidence is enough for CHI 2027: formative study only, or formative study plus expert review?

## Short Message To Send Before Meeting

Hi Professor, I now have a working prototype and an initial CHI paper framing. The project is positioned as "rehearsal, not replacement": SafeBARS uses bias-calibrated synthetic stakeholders to help researchers identify risks in sensitive online-fraud-prevention study plans before real fieldwork. I also prepared three internal dry-run cases showing privacy/blame, family autonomy, and follow-up resource risks. I would like to discuss whether this framing is strong enough for CHI and what formative study design would be most convincing.

