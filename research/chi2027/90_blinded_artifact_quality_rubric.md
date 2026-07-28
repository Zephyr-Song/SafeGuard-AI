# SafeBARS Blinded Artifact-Quality Rubric

Status: draft for expert calibration. Freeze before experts see study outputs.

Purpose: evaluate the quality of research-plan and ethics-application artifacts,
not predict institutional approval.

## Rating instructions

- Rate only the submitted artifact.
- Do not infer missing procedures from good intentions.
- A long answer is not automatically a complete answer.
- Credit safeguards only when the responsible role, action, timing, and
  escalation or follow-up are sufficiently operationalized.
- Mark uncertainty when the artifact does not provide enough evidence.
- Do not use the case's planted issue key while assigning the primary score.
- Provide a short evidence note with a passage or section reference.

Use integer ratings from 1 to 5. Anchors for 1, 3, and 5 are defined below.
Ratings 2 and 4 represent defensible intermediate states.

## D1. Information completeness

**1 — Substantially absent:** Multiple decision-critical elements are missing,
including who participates, what happens, what data are collected, or how
withdrawal and follow-up work.

**3 — Partly complete:** The main procedure is understandable, but one or more
decision-critical elements remain ambiguous or are covered only generically.

**5 — Decision-relevant coverage:** The artifact covers participants,
recruitment, consent, procedure, data, risk, withdrawal, follow-up, and
applicable AI governance at a level that supports focused expert review.

## D2. Safeguard specificity

**1 — Labels without procedures:** Uses phrases such as "ensure privacy" or
"obtain consent" without stating actors, actions, timing, or escalation.

**3 — Partial operational detail:** Some safeguards identify concrete actions,
but important responsibilities, triggers, or follow-up steps remain unclear.

**5 — Operational safeguards:** Important safeguards identify who acts, what
they do, when they do it, what triggers escalation, and how the action is
documented or followed up.

## D3. Actionability

**1 — Not actionable:** Advice or plans are too abstract, contradictory, or
outside the researcher's control.

**3 — Partly actionable:** Several revisions can be implemented, but others
require interpretation or do not identify a responsible role.

**5 — Directly actionable:** The artifact translates concerns into feasible
protocol changes, decisions, owners, and next steps.

## D4. Evidence traceability

**1 — Unsupported:** Important claims and proposed changes cannot be connected
to source material, an explicit missing-information statement, or a named
framework rationale.

**3 — Mixed traceability:** Some consequential revisions are grounded, while
others rely on generic assertions or unclear evidence.

**5 — Inspectable basis:** Consequential revisions clearly identify the
submitted passage, missing field, scenario evidence, or framework rationale
that motivated them.

## Primary Preparation Quality Index

The single primary score is the unweighted mean of D1-D4:

1. information completeness;
2. safeguard specificity;
3. actionability; and
4. evidence traceability.

Report the four component distributions as well as the mean. If the
preregistered reliability threshold is not met, do not use the mean as the
headline result.

D5-D7 are prespecified secondary outcomes. They must not be added to the
primary index after inspecting results.

## D5. Appropriate uncertainty and escalation

**1 — False certainty or absent escalation:** The artifact presents local,
legal, clinical, community, or normative judgements as settled, or leaves
critical uncertainty unaddressed.

**3 — Uncertainty acknowledged:** Important unknowns are identified, but the
expert role, question, evidence need, or closure condition is incomplete.

**5 — Calibrated handoff:** The artifact distinguishes what can be revised from
what requires human authority and states the question, responsible expert role,
evidence needed, and closure condition.

## D6. Internal consistency

**1 — Material contradictions:** Sections conflict about participants,
procedures, data use, withdrawal, risk, AI use, or responsibility.

**3 — Mostly consistent:** The central design is coherent, but one or more
cross-section tensions or undefined terms remain.

**5 — Coherent:** Recruitment, consent, procedure, data, safeguards, AI role,
follow-up, and handoffs agree across the artifact.

## D7. Unsupported normative, legal, or compliance claims

This dimension is positively scored: higher means fewer unsupported claims.

**1 — Consequential unsupported claims:** The artifact asserts approval,
compliance, safety, representativeness, fairness, or legal adequacy without an
appropriate basis.

**3 — Limited overclaiming:** Most boundaries are appropriate, but one or more
claims exceed the submitted evidence or the system's authority.

**5 — Bounded claims:** The artifact avoids unsupported approval or compliance
claims and clearly separates preparation support from institutional judgement.

## Conditional AI-governance subscale

Rate these only for AI-enabled cases. Report separately from the seven-item
primary composite:

1. AI purpose and decision role;
2. data source and provenance;
3. intended population, sample fit, and subgroup performance;
4. privacy, security, provider access, and retention;
5. participant disclosure and consent;
6. human oversight and stopping authority;
7. monitoring, correction, complaint, and redress.

Use the same 1-5 logic:

- 1: absent or materially misleading;
- 3: partial and generic;
- 5: operational and internally consistent.

## Secondary issue coding

After the primary rating is locked, a separate coding pass may use the sealed
case-authoring key to record:

- planted issue family addressed: yes/no/partial;
- additional consequential issue: yes/no with rationale;
- duplicate or low-value issue;
- contradiction introduced;
- unsupported claim retained;
- appropriate handoff; and
- inappropriate or unnecessary handoff.

The authoring key is not exhaustive ground truth. Additional expert-identified
issues remain valid data.

## Calibration procedure

1. Train reviewers on two held-out artifacts not used in the study.
2. Each reviewer rates independently.
3. Discuss anchor interpretation, not the desired score.
4. Revise wording only before the rubric freeze.
5. Rate a third held-out artifact independently as a calibration check.
6. Freeze the manual and record its hash.
7. Preserve all independent study ratings without consensus replacement.

## Reliability reporting

Report a two-way random-effects, absolute-agreement intraclass correlation for
the composite score:

- single-rater reliability; and
- reliability of the mean rating used in analysis.

Also show dimension-level distributions and substantive disagreements.
