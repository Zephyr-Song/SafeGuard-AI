# SafeBARS Coding Protocol v1

Last updated: 2026-06-17

Status: draft for supervisor approval and pilot refinement.

## Analysis Goal

Analyze whether and how SafeBARS helps researchers revise sensitive action research plans before fieldwork.

The analysis should not claim that synthetic stakeholders reveal real community needs. The analysis should focus on researcher reflection, plan revision, trust calibration, and prototype usability.

## Data Sources

For each participant:

- initial research plan;
- SafeBARS interaction log;
- reflection report;
- revised research plan;
- post-task interview notes/transcript;
- researcher memo.

## Primary Analysis Questions

AQ1. What kinds of ethical or safety issues appear in revised plans after SafeBARS use?

AQ2. What changes occur between initial and revised plans?

AQ3. How do participants interpret synthetic stakeholder responses?

AQ4. Where does the system support reflection, and where does it risk confusion or overtrust?

## Coding Unit

Primary unit:

- one initial/revised plan pair.

Secondary units:

- individual plan changes;
- stakeholder response moments;
- reflection report items;
- interview explanations.

## Step 1: Prepare Case Packet

For each participant, collect:

1. initial plan;
2. revised plan;
3. exported SafeBARS Markdown;
4. exported SafeBARS JSON;
5. interview notes/transcript;
6. researcher memo.

Create a short case summary:

- participant background;
- stakeholder presets used;
- number of rehearsal turns;
- main issues surfaced;
- main revisions;
- notable trust-calibration moment.

## Step 2: Code Plan Revisions

Use categories from `32_pre_post_plan_coding_framework.md`.

Categories:

- C1 Stakeholder Coverage
- C2 Privacy and Data Handling
- C3 Distress and Safety Protocol
- C4 Victim-Blaming Language Reduction
- C5 Participant Burden Reduction
- C6 Consent Clarity
- C7 Community Benefit and Follow-Up
- C8 Trust Calibration About Synthetic Stakeholders
- C9 Method Feasibility

For each category, assign:

- 0: no change;
- 1: vague or superficial change;
- 2: concrete change;
- 3: concrete change plus participant choice, support, owner, or verification step.

Record evidence:

- initial plan excerpt;
- revised plan excerpt;
- rationale from interview, if available.

## Step 3: Code Rehearsal Interaction

For each session, code:

### I1. Prompt Type

- interview question testing;
- workshop/activity testing;
- consent/recording testing;
- safety procedure testing;
- stakeholder mapping;
- feasibility/logistics;
- general brainstorming.

### I2. Rehearsal Signal

Use system metadata where available:

- privacy concern;
- distress risk;
- participant burden;
- trust issue;
- missing context;
- unclear consent;
- limitation reminder;
- useful question;
- none/unclear.

### I3. Participant Uptake

Code whether participant appears to use the response:

- 0: ignored or no evidence;
- 1: acknowledged verbally only;
- 2: used in revised plan;
- 3: used in revised plan and connected to real stakeholder verification.

### I4. Overtrust or Misuse Risk

Code:

- 0: no overtrust observed;
- 1: mild ambiguity, such as treating response as plausible participant opinion;
- 2: clear overgeneralization from synthetic response;
- 3: treats synthetic response as evidence about real community.

If I4 is 2 or 3, record exact evidence and discuss in limitations/findings.

## Step 4: Code Interview Themes

Use thematic analysis around these initial themes:

- perceived usefulness;
- ethical/safety risk discovery;
- missing stakeholders;
- trust calibration;
- confusing interface elements;
- profile/sliders interpretation;
- realism vs usefulness;
- limitations and failure modes;
- desired stakeholder roles;
- desired reflection report improvements;
- future use cases.

Allow new themes to emerge.

## Step 5: Cross-Case Matrix

Create one row per participant:

```text
participant_id,
research_experience,
llm_experience,
presets_used,
turn_count,
C1,
C2,
C3,
C4,
C5,
C6,
C7,
C8,
C9,
overall_revision_quality,
main_usefulness_theme,
main_risk_theme,
overtrust_risk_level,
prototype_issue
```

Use or extend:

- `research/chi2027/33_coding_table_template.csv`

## Step 6: Derive Findings

Possible finding types:

### Finding Type A: Plan Improvement Patterns

Example:

Participants often revised plans by reducing blaming wording, clarifying privacy/recording choices, and adding skip/pause options.

Evidence:

- pre/post excerpts;
- coding table;
- participant explanation.

### Finding Type B: Synthetic Stakeholders as Assumption Probes

Example:

Participants used stakeholder responses to identify missing relationships, such as family helpers or community workers.

Evidence:

- stakeholder prompt;
- synthetic response;
- revised plan addition.

### Finding Type C: Trust Calibration Tensions

Example:

Participants understood the tool as a rehearsal aid, but some responses felt authoritative enough to risk overgeneralization.

Evidence:

- interview quotes;
- overtrust coding;
- UI feedback.

### Finding Type D: Design Improvements

Example:

Participants wanted clearer labels for profile sliders, stronger evidence boundaries, or more explicit real-fieldwork verification prompts.

Evidence:

- interview themes;
- observed confusion;
- prototype issue logs.

## Reliability and Quality Check

For formative stage:

- primary coder codes all cases;
- second coder/reviewer checks 2 cases if available;
- discuss disagreements and update code definitions;
- keep an audit memo of coding changes.

If only one coder is available:

- code all cases twice with at least 2-3 days between passes;
- compare first and second pass;
- document changes in a coding memo.

## What Not To Report

Avoid reporting:

- statistics implying generalizable effectiveness from 6-8 participants;
- claims that synthetic stakeholders were accurate;
- claims about real older adults, fraud victims, or vulnerable communities;
- participant quotes that include sensitive or identifiable personal information.

## What To Report

Report:

- concrete plan revisions;
- how participants interpreted the tool;
- where the system helped or failed;
- how the non-replacement boundary worked;
- design implications for bounded synthetic stakeholder tools.

## Minimum Evidence Needed for CHI Findings

Each main finding should include at least two evidence types:

- plan revision excerpt;
- interaction log moment;
- interview quote;
- researcher observation memo;
- coding count/pattern.

Example:

If claiming "SafeBARS helped participants notice victim-blaming wording," include:

- initial wording;
- stakeholder response/reflection flag;
- revised wording;
- participant explanation.
