# Codex Workflow for SafeBARS

Last updated: 2026-06-16

This file describes how to use Codex as a project partner for the CHI 2027 submission.

## Working Principle

Codex should help produce artifacts, not only suggestions. Each phase should end with files in the repository:

- Research notes.
- Prototype code.
- Study materials.
- Analysis scripts.
- Paper drafts.
- Submission checklists.

## Project File Structure

Recommended structure:

```text
research/
  chi2027/
    00_project_brief.md
    01_cobra_transfer_analysis.md
    02_literature_matrix_seed.md
    03_two_month_plan.md
    04_chi2027_submission_checklist.md
    05_codex_workflow.md
  protocols/
  literature/
  data/
  analysis/
paper/
supplement/
```

## Codex Roles

### 1. Research Manager

Use Codex to:

- Maintain the master timeline.
- Convert vague goals into weekly tasks.
- Track deliverables.
- Prepare supervisor update drafts.

Example request:

"Update the CHI2027 plan based on today's supervisor feedback and convert it into next week's checklist."

### 2. Literature Assistant

Use Codex to:

- Create a literature matrix.
- Summarize papers into comparable fields.
- Identify threat-to-novelty papers.
- Draft related work outlines.

Important:

Codex can summarize and organize, but the human researcher must read central papers and make final novelty judgments.

### 3. Prototype Engineer

Use Codex to:

- Refactor existing SafeGuard-AI modules.
- Implement stakeholder agents.
- Implement bias profiles.
- Implement reflection dashboard.
- Add logging and export.
- Run local tests.

Relevant existing files:

- app.py
- modules/scenario_simulator.py
- modules/transparency_dashboard.py
- modules/safety_guardian.py
- modules/learning_tracker.py

### 4. Study Designer

Use Codex to draft:

- Study protocol.
- Consent form.
- Recruitment email.
- Task sheet.
- Interview guide.
- Coding scheme.
- Data management plan.
- Ethics note.

Human researcher must:

- Confirm ethics requirements.
- Recruit participants.
- Conduct sessions.
- Protect participant data.

### 5. Data Analyst

Use Codex to:

- Create session summaries.
- Compare pre/post research plans.
- Draft qualitative coding tables.
- Generate descriptive statistics.
- Create charts and result tables.

Important:

Do not upload sensitive or identifiable data unless anonymized. Keep raw identifiable data outside shared or public artifacts.

### 6. Paper Co-Pilot

Use Codex to:

- Draft section outlines.
- Generate introduction variants.
- Check argument flow.
- Tighten contribution claims.
- Prepare figure captions.
- Check anonymization.
- Prepare rebuttal drafts after reviews.

Human researcher must:

- Own final argument.
- Verify claims.
- Rewrite key prose.
- Coordinate supervisor feedback.

## AI Use Documentation

Maintain a simple log for CHI transparency:

```text
Date:
Artifact:
AI assistance used:
Human verification:
Final owner:
```

Examples:

- Codex drafted initial study protocol; human researcher revised ethics and procedure.
- Codex implemented prototype logging; human researcher tested with sample sessions.
- Codex drafted related work outline; human researcher verified citations and claims.

## Immediate Next Codex Tasks

1. Expand the literature matrix.
2. Create system specification for SafeBARS v1.
3. Create prompt templates for stakeholder agents.
4. Create prototype implementation plan.
5. Draft supervisor update email.

