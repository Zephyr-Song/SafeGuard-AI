# SafeBARS Next Tasks Roadmap

Last updated: 2026-06-17

## Current Status

SafeBARS now has:

- CHI project framing.
- CoBRA transfer analysis.
- Literature matrix and novelty risk memo.
- System specification.
- Stakeholder taxonomy and bias profile schema.
- Prompt templates.
- Working Flask prototype.
- Bias sliders.
- Rehearsal chat.
- Reflection report.
- Evidence-grounded reflection notes.
- Revised plan capture.
- Formative study protocol, interview guide, and pre/post template.
- Consent, recruitment, data management, and paper outline drafts.
- Supervisor demo script and study session checklist.
- Pre/post plan coding framework and analysis helper.
- Supervisor-facing visual summary page.
- Participant study mode route.
- Pilot comparison design draft.
- Literature matrix v1 with 30 entries.
- Related work synthesis memo.
- Citation-to-claim map for CHI writing.
- Profile consistency check method/limitation note.
- CHI figure plan v0.
- Formative study recruitment/screening criteria v1.
- Formative study session script v1.
- Participant task sheet v1.
- Data export and file naming checklist.
- Coding protocol v1.
- Formative study packet index.
- Recruitment tracking table.
- Internal dry run protocol.
- API-based internal dry run export and memo.
- Dry-run coding example.
- LLM provider comparison mode.
- Multi-provider startup script.
- Provider comparison heuristic analysis and export.

## Next Priority

Move from internal prototype to study-ready prototype.

## Track A: Prototype

### A1. Add Optional LLM-Backed Stakeholder Responses

Goal:

Use a real LLM when API keys are available, but keep deterministic fallback.

Why:

LLM responses will make rehearsal more natural. Fallback keeps the study robust.

Deliverables:

- [x] LLM response path.
- [x] Prompt assembly based on templates.
- [x] Fallback when API fails.
- [x] UI indicator showing template or LLM mode.
- [x] Provider comparison endpoint.
- [x] Compare Providers UI.
- [x] Multi-provider startup script for Zhipu/Profile A/Profile B.
- [x] Aliyun Bailian provider support.
- [x] Provider comparison risk/boundary/revision analysis.
- [x] Export provider comparison results.

### A2. Add Prompt/Profile Consistency Test

Goal:

Check whether higher bias settings produce expected response changes.

Why:

This helps defend the "bias-calibrated" idea without claiming psychometric validity.

Deliverables:

- [x] Small script that tests profiles against standard prompts.
- [x] JSON output.
- [x] Notes for paper method or limitation section.

### A3. Polish Study Interface

Goal:

Make the interface clearer for participants.

Deliverables:

- [x] Cleaner instructions.
- [x] Better report display.
- [x] Clear limitation text.
- [ ] Short study mode toggle if needed.

## Track B: Study Preparation

### B1. Supervisor Review Packet

Goal:

Prepare a concise package for supervisor meeting.

Deliverables:

- [x] One-page novelty memo.
- [x] Prototype link/instructions.
- [x] Study protocol v0.
- [x] 3 key questions for supervisor.

### B2. Ethics/Consent Draft

Goal:

Prepare materials for ethics review or supervisor approval.

Deliverables:

- [x] Participant information sheet.
- [x] Consent form.
- [x] Recruitment message.
- [x] Data management note.

### B3. Pilot Recruitment Plan

Goal:

Identify possible participants and recruitment channels.

Deliverables:

- [x] Recruitment criteria.
- [x] Screening questions.
- [x] Recruitment channels.
- [x] Scheduling/tracking table.
- [ ] Target participant list.

### B4. Pre/Post Plan Analysis

Goal:

Prepare for analysis of participant plan revisions.

Deliverables:

- [x] Coding framework.
- [x] Coding table template.
- [x] Heuristic comparison helper script.
- [x] Coding protocol v1.
- [ ] Final coding protocol after supervisor feedback.

### B5. Formative Study Operations

Goal:

Prepare materials needed to run the first pilot/formative session.

Deliverables:

- [x] Moderator/session script.
- [x] Participant task sheet.
- [x] Data export and file naming checklist.
- [x] Study packet index.
- [x] Internal dry run protocol.
- [x] API-based internal dry run.
- [ ] Browser-based internal dry run with a human/labmate.
- [ ] First pilot/formative session.

## Track C: Literature and Framing

### C1. Deepen Literature Matrix

Goal:

Move from seed matrix to 25-40 papers.

Deliverables:

- [x] Full citations and source links for first 30 entries.
- [x] Related work notes.
- [x] Threat-to-novelty notes.
- [ ] Add 8-10 more CHI/CSCW papers after ACM DL search.

### C2. Write Related Work Skeleton

Goal:

Prepare paper sections early.

Deliverables:

- [x] 5 related work subsections.
- [x] Key arguments and citations.
- [x] Citation-to-claim map.
- [ ] Convert into paper prose after supervisor feedback.

## Track D: Paper Preparation

### D1. Paper Outline v1

Goal:

Draft a CHI-style paper structure before study.

Deliverables:

- [x] Title options.
- [x] Abstract placeholder.
- [x] Introduction skeleton.
- [x] Contribution claims.
- [x] Method outline.

### D2. Figure Plan

Goal:

Decide figures needed for CHI submission.

Potential figures:

- System workflow.
- Bias profile interface.
- Rehearsal-to-reflection pipeline.
- Study procedure.
- Pre/post plan revision example.

Deliverables:

- [x] CHI figure plan v0.
- [x] Capture prototype screenshots.
- [ ] Create polished workflow diagram after supervisor feedback.

## Recommended Next 5 Tasks

1. Run one browser-based internal dry run using `/safebars/study` with a human/labmate.
2. Prepare a target participant list and scheduling table for 6-8 participants.
3. Add 8-10 more CHI/CSCW papers specifically on AI-assisted qualitative research tools and older-adult scam/fraud studies.
4. Refine study mode after supervisor feedback.
5. Run LLM-mode profile checks when API/network is stable.
