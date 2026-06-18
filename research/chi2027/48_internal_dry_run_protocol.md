# SafeBARS Internal Dry Run Protocol

Last updated: 2026-06-17

Purpose: run one complete rehearsal of the formative study before recruiting participants.

## Goal

Check whether the study workflow, prototype, export process, task sheet, and coding protocol work together.

This dry run can be done by the researcher alone or with one friendly labmate/classmate.

## Dry Run Checklist

Before starting:

- [ ] Restart SafeBARS service.
- [ ] Open `http://127.0.0.1:5050/safebars/study`.
- [ ] Prepare participant ID `DRYRUN01`.
- [ ] Open `43_participant_task_sheet_v1.md`.
- [ ] Open `42_formative_study_session_script_v1.md`.
- [ ] Prepare folder `data/safebars_study/DRYRUN01/`.

## Test Research Plan

Use this plan if doing a self dry run:

Title:

Community workshop on online fraud prevention

Goal:

Understand what makes suspicious investment messages seem trustworthy and design a safer workshop for older adults.

Target community:

Older adults at a community center.

Planned method:

Short interviews followed by a workshop.

Draft materials:

- How much money did you lose?
- Why did you believe the message?
- We will record the session for analysis.
- The university and local police support this project, so participants should feel safe.

Known risks:

Participants may feel embarrassed, worry about privacy, distrust institutions, or become distressed when discussing financial loss.

## Required Prototype Actions

Complete:

1. Enter the plan.
2. Select affected participant preset.
3. Click `Start Session`.
4. Ask at least 3 questions.
5. Generate reflection.
6. Write revised plan.
7. Save revision.
8. Export session.

Optional:

- Repeat one turn with family helper.
- Repeat one turn with community worker.
- Adjust one slider and observe whether response changes.

## Test Questions

Ask:

1. Is "How much money did you lose and why did you believe the message?" okay as an interview question?
2. Would recording the session create privacy concerns?
3. Is a two-hour workshop after the interview too much?
4. Does university or police support make participants more comfortable?

## Revised Plan Expectations

The revised plan should ideally add:

- non-blaming question wording;
- exact-loss disclosure as optional;
- recording choice;
- skip/pause/withdraw language;
- shorter or lower-burden session structure;
- support/follow-up resources;
- verification with real participants or community partners.

## Export Check

Confirm:

- [ ] JSON exported.
- [ ] Markdown exported.
- [ ] revised plan appears in export.
- [ ] reflection report appears in export.
- [ ] evidence notes appear in report.
- [ ] file can be copied into participant folder.

## Coding Check

After dry run:

1. Use `45_coding_protocol_v1.md`.
2. Code the initial/revised plan pair.
3. Fill one row in `33_coding_table_template.csv` or a copy.
4. Note confusing coding categories.
5. Update coding protocol if needed.

## Dry Run Debrief Questions

Answer in a memo:

1. Did any instruction feel unclear?
2. Did any button or workflow step fail?
3. Did the prototype make the non-replacement boundary visible enough?
4. Was the reflection report useful for revising the plan?
5. Was export easy enough?
6. Could a real participant finish within 60 minutes?
7. What should be fixed before recruitment?

## Pass Criteria

The study is ready for first participant recruitment if:

- the full workflow can be completed in 60 minutes;
- prototype actions work without debugging;
- exported data is complete;
- the task sheet is understandable;
- the coding protocol can be applied to the dry-run plan pair;
- the researcher can explain the non-replacement boundary clearly.
