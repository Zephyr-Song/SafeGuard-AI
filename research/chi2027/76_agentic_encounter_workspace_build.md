# SafeBARS V2: Agentic Encounter Workspace Build Memo

Date: 2026-06-27

## What Changed

SafeBARS is no longer centered on free-form conversation with a synthetic stakeholder. The primary workflow now stress-tests the researcher's protocol as an encounter:

1. submit recruitment, consent, interview, activity, safety, and follow-up materials;
2. inspect and edit a nine-stage encounter map;
3. run six bounded breakdown scenarios;
4. inspect passage-grounded traces and first unsupported transitions;
5. accept, edit, reject, or defer each issue;
6. assign unresolved questions to real stakeholders through epistemic handoffs;
7. export the complete session, decisions, handoffs, and event history.

The original rehearsal-chat interface remains available at `/safebars/v1` for comparison, but it is no longer the main research contribution.

## Implemented Agent Roles

- **Encounter Orchestrator:** indexes submitted passages and builds the editable encounter map.
- **Breakdown Scenario Agent:** follows six inspectable test conditions through the protocol and stops at unsupported transitions.
- **Relationship and Power Agent:** checks whether helpers, gatekeepers, responsibility, and authority are represented in the plan.
- **Boundary and Handoff Agent:** labels outputs as planning hypotheses and routes unresolved situated questions to real people.
- **Bounded LLM Critic (optional):** may add at most two passage-grounded issues; deterministic tracing remains available when no provider is configured.

## Current Interaction Objects

### Encounter map

Nine stages cover outreach, gatekeeping, consent, activity, sensitive disclosure, pause or withdrawal, escalation, debrief, and follow-up. Researchers can exclude irrelevant stages and add responsibility notes before running an audit.

### Breakdown trace

Each selected scenario produces a three-step trace containing the trigger, located protocol response, responsibility or handoff, source-passage IDs, first gap, and uncertainty statement.

### Decision ledger

Each issue contains exact source material, a proposed change, and a boundary statement. The researcher must explicitly accept, edit, reject, or defer it and may record revised text and a rationale.

### Epistemic handoff

Unresolved questions name why AI cannot settle them, who should be consulted, a suggested method, and when the consultation should happen.

## Technical Properties Relevant to the Study

- SQLite persistence preserves sessions while the current service filesystem remains available.
- If a free Render deployment replaces its ephemeral filesystem, the decision interface can rebuild the visible audit from the current browser state and then save the pending decision under a new session ID.
- Passage IDs preserve provenance from critique to submitted material.
- An append-only event table records mapping, audit, and decision actions.
- JSON export supports later qualitative coding of traces, decisions, rationales, and handoffs.
- The v1 route allows a future within-participant comparison between conversational rehearsal and encounter stress-testing.

The automatic rebuild is a usability recovery mechanism, not durable research-data storage. Before collecting study data, deploy a persistent database or disk and verify backup, access, retention, and deletion procedures.

## Demonstration Script

1. Open `/safebars` and select **Load sample**.
2. Select **Build encounter map** and point out that the object being modeled is the protocol, not a simulated person.
3. Review the nine stages and change one stage note or scope toggle.
4. Run the six scenario traces with the LLM toggle off to demonstrate the transparent baseline.
5. Open one trace and identify the first unsupported transition.
6. Open **Issue ledger**, inspect the cited passage, and defer one issue.
7. Open **Handoffs** to show how uncertainty becomes a real consultation task.
8. Export the session to show the decision and event record.

## Immediate Research Tasks

### Task 1: Scenario and stage validity review

Ask 2-3 methods, ethics, safeguarding, or qualitative-research experts to inspect the encounter schema and scenario library. The goal is not to evaluate usability yet, but to remove implausible categories, add missing transition types, and define what counts as a useful handoff.

### Task 2: Benchmark protocol set

Prepare 8-12 de-identified or public sensitive-study protocols spanning academic HCI, applied UX or service research, and community or health research. Each protocol should include enough recruitment, consent, activity, safety, and follow-up material for a fair audit.

### Task 3: Failure taxonomy and gold annotations

Two human reviewers independently annotate unsupported transitions, ambiguous responsibility, unsafe assumptions, and questions requiring situated knowledge. Disagreements should be preserved and discussed rather than forced into a single ground truth.

### Task 4: Comparative pilot

Compare three preparation conditions on the same protocol tasks:

- unaided document review;
- v1 conversational synthetic-stakeholder rehearsal;
- v2 encounter stress-testing.

Measure issue discovery, passage specificity, revision actionability, unsupported claims about communities, handoff quality, time, perceived control, and reasons for accepting or rejecting suggestions.

### Task 5: Think-aloud formative study

Recruit protocol preparers beyond only HCI researchers: qualitative researchers, UX researchers, service designers, community-engagement staff, research operations staff, and ethics or safeguarding advisors. The study should examine how they contest agent outputs and where they require real stakeholder engagement.

## Claims We Can and Cannot Make

SafeBARS can support claims about protocol inspection, researcher decision-making, provenance, contestability, and epistemic handoff. It cannot support claims that synthetic traces represent a community, predict participant behavior, replace formative work, approve ethics, or guarantee safety.

## Verification Completed

- Five automated engine and API tests pass.
- A browser workflow produced 9 encounter stages, 6 breakdown traces, and 3 contestable sample issues.
- Accept/edit/reject/defer decisions persist.
- An injected missing-session failure was recovered automatically before the pending decision was saved.
- Desktop and mobile browser checks show no horizontal overflow.
- The browser console showed no JavaScript errors during the tested workflow.
