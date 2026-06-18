# SafeBARS Data Export and File Naming Checklist

Last updated: 2026-06-17

Status: draft for formative study operations.

## Goal

Keep each formative study session organized so analysis can connect:

- initial plan;
- SafeBARS interaction log;
- reflection report;
- revised plan;
- interview notes/transcript;
- researcher memo.

## Folder Structure

Recommended local structure:

```text
data/safebars_study/
  P01/
    P01_initial_plan.md
    P01_safebars_session.json
    P01_safebars_session.md
    P01_revised_plan.md
    P01_interview_notes.md
    P01_researcher_memo.md
  P02/
    ...
```

Do not use real participant names in file names.

## Participant ID Format

Use:

- P01, P02, P03, etc.

Optional suffixes:

- `_pilot` for internal pilot sessions;
- `_excluded` only if a session is unusable and must be clearly separated.

## Before Session

Create participant folder:

```text
data/safebars_study/PXX/
```

Create:

- `PXX_initial_plan.md`
- `PXX_revised_plan.md`
- `PXX_interview_notes.md`
- `PXX_researcher_memo.md`

Record separately:

- participant background category;
- consent status;
- recording status;
- session date.

Do not store real names in the analysis folder.

## During Session

Save or copy:

- initial plan before SafeBARS use;
- important notes about participant behavior;
- prototype problems;
- notable quotes if recording is not used.

Avoid collecting:

- personal fraud details;
- personal financial details;
- names of real victims or family members;
- unnecessary institutional identifiers.

## SafeBARS Export

At the end of the task:

1. Click `Save Revision`.
2. Click `Export`.
3. SafeBARS exports files to:

```text
data/safebars/
```

Exported files are named by session ID, for example:

```text
data/safebars/safebars_abcd123456.json
data/safebars/safebars_abcd123456.md
```

Copy these into the participant folder and rename:

```text
PXX_safebars_session.json
PXX_safebars_session.md
```

## Researcher Memo Template

Use this after every session:

```text
# PXX Researcher Memo

Date:
Session length:
Participant background:
LLM experience:
Research experience:

## Prototype Use

Stakeholder presets used:
Number of rehearsal turns:
Reflection generated: yes/no
Export successful: yes/no

## Main Risks Surfaced

- 

## Main Plan Revisions

- 

## Trust Calibration Notes

- Did the participant treat synthetic responses as evidence, suggestions, warnings, or something else?
- Did they mention need to verify with real participants/community partners?

## Prototype Issues

- 

## Researcher Reflections

- 
```

## Data Completeness Checklist

For each participant, confirm:

- [ ] consent recorded or noted;
- [ ] initial plan saved;
- [ ] SafeBARS JSON exported;
- [ ] SafeBARS Markdown exported;
- [ ] revised plan saved;
- [ ] interview notes/transcript saved;
- [ ] researcher memo completed;
- [ ] participant ID used consistently;
- [ ] no direct identifiers stored in analysis files.

## Analysis Linking Table

Maintain a separate secure tracking table if needed:

```text
participant_id, session_date, background_category, safebars_session_id, recording_status, notes
P01, YYYY-MM-DD, HCI PhD student, safebars_xxxxx, audio yes/no, ...
```

If this table contains identifiable scheduling information, store it separately from analysis data.

## After Study

Prepare an analysis folder:

```text
research/chi2027/study_analysis/
  plan_coding/
  interview_themes/
  prototype_issues/
  example_excerpts/
```

Only move anonymized excerpts into paper-writing folders.
