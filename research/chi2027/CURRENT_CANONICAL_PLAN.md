# SafeBARS Current Canonical Research Plan

Last updated: 2026-07-30

Use this file to answer “what is the current SafeBARS research?” The earlier
protocol-approval and expert-caseload direction remains in the repository as an
audit trail, but it is no longer the primary intervention or paper claim.

## Current research problem

Computer-science researchers can acknowledge that unintended consequences are
important while still struggling to connect abstract values to concrete changes
in an AI-app research plan. A normal LLM conversation can list risks, but it
does not necessarily make the researcher’s own commitment–design discrepancy
visible, preserve its evidence chain, or test whether a revision addresses it.

SafeBARS Ethical Mirror investigates a non-judgmental, literature-grounded
reflection workflow for that gap. It does not grant ethics approval, determine
whether a project is ethical, infer sensitive researcher demographics, or
replace participation by affected people.

## Single research question

> Compared with general-purpose LLM chat, how does a literature-grounded,
> multi-role Ethical Mirror that visualises discrepancies between researchers’
> stated values and plausible affected-party scenarios influence the
> recognition of unintended consequences and consequential revision of AI-app
> research plans?

Primary outcome: blinded expert-rated consequence-to-change quality, combining
affected-position breadth, causal specificity, revision specificity and
feasibility, and evidence traceability. The final rubric and aggregation rule
must be frozen before data collection.

## Current intervention

The implemented prototype is available at `/safebars/mirror` and contains:

1. eight one-question-at-a-time guided-intake turns;
2. one conditional sensitive-data necessity question;
3. nine literature-derived evidence-coverage lenses;
4. five bounded synthetic role probes with explicit stopping rules;
5. a commitment → plan evidence → consequence → affected-party map;
6. revise, safeguard, contest, and consult responses; and
7. counterfactual replay with a concise before/after ledger.

A configured server-side model enriches each role contract in one batched call.
If all providers fail, SafeBARS labels and uses a deterministic bounded fallback.
Neither route changes evidence states or counts as stakeholder testimony.

## Study direction

- Population: computer-science students and early-career researchers actively
  developing AI-app ideas.
- Comparison: SafeBARS Ethical Mirror versus general-purpose LLM chat, using
  the same underlying model and time budget.
- Controlled task: counterbalanced matched AI-app research plans.
- Ecological follow-up: optional reflection on the participant’s own project
  after the controlled task.
- Primary evidence: blinded ratings of revised plans.
- Process evidence: commitments, scenario and graph inspection, accept/contest/
  consult choices, plan edits, and replay.
- Qualitative evidence: stimulated recall focused on genuine reframing,
  superficial compliance, defensiveness, useful contestation, and epistemic
  handoff.

Exact sample size, exclusion rules, rating reliability rule, and analysis model
remain to be frozen after a short formative usability check and before the
first main-study participant.

## Canonical files

Read these in order:

1. `91_ethical_mirror_redesign.md` — current contribution, interaction
   mechanism, literature mapping, privacy decision, and candidate experiment;
2. `90_blinded_artifact_quality_rubric.md` — prior rubric material to adapt for
   consequence-to-change quality;
3. `86_evalLM_blueprint_final_rqs.md` — useful experimental blueprint and
   same-model comparison logic, but its old three-RQ protocol-preparation
   framing is superseded;
4. `87_46_day_chi_execution_plan.md` — timing and ethics-gate material to revise
   around the Ethical Mirror study; and
5. `figures/` and `study_materials/` — technical artefacts and earlier study
   materials that must not be presented as evidence for the new intervention
   until updated.

## Superseded primary directions

- generating university ethics-approval applications as the main contribution;
- expert caseload and ethics-board handoff as the main evaluated workflow;
- protocol-preparation quality across sensitive human-facing domains as the
  sole outcome;
- three separate research questions for preparation, contestation, and expert
  work;
- synthetic stakeholders as participant proxies;
- a static intake form or a chat-only intervention; and
- any outcome framed as receiving or predicting ethics approval.

Expert or stakeholder consultation remains one legitimate response to an
unresolved tension, but it is no longer a separate expert-workspace paper claim.

## Evidence status

Completed:

- isolated Ethical Mirror prototype;
- persistent guided-intake sessions;
- nine auditable literature-derived lenses;
- five bounded role contracts with model enrichment and deterministic fallback;
- interactive scenario, dissonance-map, revision, replay, and ledger workflow;
- unit, API, backward-compatibility, and browser end-to-end checks.

Not yet completed:

- written ethics decision for the revised human study;
- formative sessions with target users;
- final experiment and analysis freeze;
- comparative participant sessions;
- blinded expert ratings;
- empirical results; and
- final manuscript.

No technical test, generated scenario, or development session may be relabelled
as participant, expert, or effectiveness evidence.
