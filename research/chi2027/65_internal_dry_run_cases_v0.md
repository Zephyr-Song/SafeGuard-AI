# Internal Dry-Run Cases v0

Last updated: 2026-06-19

Purpose: create paper-ready examples showing how SafeBARS can surface risks and support study-plan revision. These are internal dry runs, not participant data.

## Boundary Statement

These dry-run cases are not evidence about older adults, families, community workers, or any real community. They are examples of how the SafeBARS workflow can turn a risky research plan into inspectable revision prompts.

## Case 1: Affected Participant and Sensitive Loss Disclosure

### Initial Plan

Title:

> Online investment scam workshop with older adults

Planned method:

> Short interviews followed by a two-hour workshop.

Risky draft material:

> Ask: How much money did you lose? Why did you believe the message? We will record the session for analysis.

### Stakeholder Preset

`affected_high_privacy`

Stakeholder role:

> Affected Participant

### Rehearsal Prompt

> Would you be comfortable if I ask how much money you lost and why you believed the message?

### SafeBARS Response Excerpt

> I would feel uncomfortable with that wording. It sounds like you already think I did something wrong. If this were a real interview, I would want you to ask what I was comfortable sharing and avoid framing the experience as my fault. A safer question might ask what made the message seem trustworthy at the time, rather than asking what mistake I made.

### Signals Surfaced

- potential victim-blaming;
- privacy concern;
- distress risk;
- need for optional disclosure.

### Reflection Report Issues

- Privacy and data-use explanation needs to be explicit before sensitive disclosure.
- Discussion of harm or financial loss may create distress and should include skip/pause options.
- Detailed disclosure may not be necessary and may increase burden.

### Revised Plan

Issue noticed:

> Asking exact loss and why someone believed a message may sound blaming and intrusive.

Revision to make:

> Make loss amount optional, ask what made the message seem trustworthy at the time, explain recording choices and anonymization before any sensitive question.

Remaining question for real stakeholders:

> What kinds of examples feel useful without creating embarrassment or distress?

### Paper Use

This case can be used in Figure 3 as an example of how a synthetic stakeholder response becomes a concrete wording revision.

## Case 2: Family Helper and Older Adult Autonomy

### Initial Plan

Title:

> Family helper interview about fraud reporting

Risky draft material:

> Ask helpers to describe what the older adult did wrong and how they convinced them to report the scam.

### Stakeholder Preset

`family_helper_protective`

Stakeholder role:

> Family Helper

### Rehearsal Prompt

> How should the study avoid making family helpers speak over older adults or convince them to report?

### SafeBARS Response Excerpt

> Family members can help, but we should not become the voice of the older adult. The study should ask how support happens while still protecting the affected person's choice, privacy, and right to disagree. You might need separate consent boundaries for family helpers and affected older adults.

### Signals Surfaced

- autonomy concern;
- missing context;
- family privacy;
- separate consent boundaries.

### Reflection Report Issues

- Some wording may sound victim-blaming; use neutral language about context and decision points.
- Add explicit skip, pause, and withdrawal options.
- Create a stakeholder map and decide which real stakeholders should review the plan.

### Revised Plan

Issue noticed:

> The plan frames older adults as making mistakes and family helpers as correctors.

Revision to make:

> Ask about support strategies, disagreements, and consent boundaries without asking helpers to blame or speak for older adults. Add a note that older adults should have separate agency in any follow-up study.

Remaining question for real stakeholders:

> How do families balance protection with autonomy in fraud response?

### Paper Use

This case can support the argument that online fraud prevention is relational, not only individual. It also justifies multiple stakeholder roles.

## Case 3: Community Worker and Follow-Up Resources

### Initial Plan

Title:

> Community worker workshop safety protocol

Risky draft material:

> Run a two-hour workshop with realistic scam examples and ask attendees to share personal stories.

### Stakeholder Preset

`community_worker_feasibility`

Stakeholder role:

> Community Worker

### Rehearsal Prompt

> What support or follow-up procedure should be in place if someone becomes distressed after the session?

### SafeBARS Response Excerpt

> You should plan what happens after the workshop, not only what happens during it. If someone becomes upset or reveals an active scam, staff need a clear referral path, privacy boundary, and realistic follow-up plan. Please check what resources the community center can actually offer before promising support.

### Signals Surfaced

- distress risk;
- support resource gap;
- community feasibility;
- follow-up planning.

### Reflection Report Issues

- Add explicit skip, pause, and withdrawal options.
- Clarify consent language, recording choices, and data boundaries.
- Session length or activity load may be too high for sensitive topics.

### Revised Plan

Issue noticed:

> The workshop may be too long and may pressure attendees to disclose sensitive stories.

Revision to make:

> Shorten the workshop, make personal story sharing optional, add breaks, prepare referral resources, and check staff capacity before recruitment.

Remaining question for real stakeholders:

> What support resources are actually available locally after the workshop?

### Paper Use

This case can be used to show how SafeBARS moves beyond wording critique into safety-procedure and feasibility planning.

## Cross-Case Takeaways

Across the three dry runs, SafeBARS surfaced:

- direct wording risks;
- privacy/data boundary needs;
- family autonomy and consent boundaries;
- participant burden;
- distress and support-resource planning;
- missing stakeholder verification.

These examples support the planned study coding categories:

- privacy language;
- non-blaming wording;
- consent/withdrawal options;
- distress protocol;
- stakeholder map;
- participant-burden reduction;
- community verification step.

## Prototype Issue Found and Fixed

During the dry run, deterministic fallback responses initially repeated too much for family-helper and community-worker prompts. The fallback rules were updated to detect:

- `money`;
- `why you believed`;
- `why they believed`;
- `speak over`;
- `autonomy`;
- `convince`;
- `support`;
- `follow-up`;
- `resource`;
- `referral`.

This improved the specificity of template responses for demos and offline study sessions.

