# SafeBARS: Completion Plan for the Three Supervisor Requirements

Date: 2026-06-29

Status: implementation and research-positioning update. Literature statements below distinguish an explicit paper finding or limitation from a SafeBARS inference. This is a focused update, not a completed systematic review.

## Executive Answer

The redesign now responds to all three supervisor requirements at the system-design level:

1. SafeBARS is positioned against the closest CHI, IUI, DIS, and adjacent ethics-review work rather than claiming novelty for multi-agent review in general.
2. The main interaction is an artifact-centered agent workflow, not a chat transcript placed inside a dashboard.
3. The target population is defined by a shared task—preparing sensitive human-facing protocols—across academic research, applied UX, service design, public-sector evaluation, and community research.

The remaining work is empirical. Expert review and a cross-domain formative/comparative study must show that the encounter schema is credible, that the agentic workflow adds value beyond a general chatbot, and that the broader audience actually recognizes the task as part of its practice.

## Closest Work and the Problem SafeBARS Carries Forward

The table uses “problem carried forward” rather than claiming that every paper explicitly requested the exact SafeBARS feature.

| Closest work | Venue | Explicit finding, scope, or limitation | SafeBARS design response | Evidence still required |
|---|---|---|---|---|
| *Simulacrum of Stories: Examining Large Language Models as Qualitative Research Participants* | CHI 2025 | LLM participant proxies can foreclose consent and agency, erase community perspectives, and lack situated depth. Its sample was primarily academic and US-based. | The system does not generate participant testimony. It inspects researcher-authored protocols, labels outputs as planning hypotheses, and converts situated unknowns into real-person handoffs. The proposed study recruits beyond academic HCI. | Test whether users understand the non-replacement boundary and whether unsupported community claims are rejected or handed off. |
| *Large Language Models in Qualitative Research: Uses, Tensions, and Intentions* | CHI 2025 | Researchers reported tensions around privacy, validity, bias, responsibility, researcher control, and imposed interpretations. The paper proposes intentional use, transparency and validation, researcher context, deep engagement, and attention to participant interests. | Tasks expose inputs, tools, dependencies, provenance, stop conditions, and outputs. Every issue requires a human accept/edit/reject/defer decision rather than passive consumption. | Compare provenance inspection, decision rationales, and calibrated reliance against a general LLM chat condition. |
| *InterFlow: Designing Unobtrusive AI to Empower Interviewers in Semi-Structured Interviews* | CHI 2026 | InterFlow supports live interviews through an adaptive script, timing support, summaries, and proactive follow-up suggestions; its contribution concerns agency-preserving support during time-sensitive interviewing. | SafeBARS occupies a different phase and object: before participant contact, it stress-tests the complete encounter across recruitment, consent, disclosure, withdrawal, escalation, and follow-up. | Show that pre-fieldwork traces reveal actionable missing transitions that live interview assistance or a generic review prompt does not make inspectable. |
| *CoBRA: Programming Cognitive Bias in Social Agents Using Classic Social Science Experiments* | CHI 2026 | Natural-language persona descriptions produce inconsistent behavior; CoBRA makes social-agent tendencies explicit and measurable through closed-loop calibration. | SafeBARS does not calibrate a synthetic person. It makes scenario conditions, routing reasons, tools, and stopping boundaries explicit and inspectable. Scenarios are test conditions, not behavioral predictions. | Check repeatability, task routing, passage validity, and unsupported claims across repeated runs and models. |
| *Writer-Defined AI Personas for On-Demand Feedback Generation* | CHI 2024 | Multiple personas can support contrast, but generated feedback may be verbose, repetitive, unspecific, and difficult to interpret as representative. | SafeBARS removes persona speech from the main workflow, limits LLM critique, requires passage IDs, deduplicates issue records, and preserves a bounded specialist-versus-boundary contestation. | Measure specificity, duplication, actionability, and whether users incorrectly treat outputs as representative. |
| *Interview AI-ssistant: Designing for Real-Time Human-AI Collaboration in Interview Preparation and Execution* | IUI Companion 2025 | The doctoral agenda identifies underexplored synchronous human-AI collaboration and asks how to support preparation and execution while considering interviewer and interviewee perspectives. | SafeBARS focuses on protocol responsibility before contact, including adverse paths outside the interview itself. It encodes mandatory checkpoints and real-person consultation rather than attempting to infer interviewee perspectives. | Demonstrate workflow value for protocol preparers and clarify that SafeBARS complements rather than competes with live interview assistance. |
| *Who Did What? Designing Avatars for Explainable Multi-Agent Systems in Knowledge Work* | DIS 2026 | Multi-agent systems can obscure which agent contributed what, weakening mental models and trust calibration. The study finds value in exposing expertise and contributions. | The audit plan exposes each agent’s goal, routing reason, priority, input passages, tools, prerequisites, stop condition, attempts, result summary, and output IDs. | Study which explanation fields users actually inspect and whether they support better contestation rather than decorative transparency. |
| *Compass vs Railway Tracks: Unpacking User Mental Models for Communicating Long-Horizon Work to Humans vs. AI* | DIS 2026 | Professionals over-specify AI work because current agents struggle to infer intent, prioritize, and judge. The paper proposes outcome alignment, test runs, and intelligent check-ins. | The Orchestrator proposes a material-dependent plan; the researcher confirms scope; tasks are priority-routed; bounded traces act as test runs; specialist tasks can be rerun; human decisions gate revision. | Observe whether plan confirmation and reruns reduce rigid prompting while preserving control. |
| *Mirror: A Multi-Agent System for AI-Assisted Ethics Review* | arXiv 2026, direct collision | Mirror already implements rule-grounded expedited review, specialist deliberation, unresolved issues, and committee-level recommendations. | SafeBARS does not claim to automate ethics review. Its distinct object is researcher-facing rehearsal of relational and procedural encounter breakdowns, followed by epistemic handoff rather than an approval or committee verdict. | Keep Mirror as the strongest collision and empirically demonstrate the encounter-rehearsal distinction. |

## Defensible Originality Claim

Do not claim:

- the first multi-agent research-protocol reviewer;
- the first AI tool for interview preparation;
- the first controllable social agent;
- the first use of multiple AI perspectives;
- automated ethics approval or community representation.

Use this narrower claim:

> SafeBARS investigates an inspectable and non-substitutive agentic workflow for stress-testing how sensitive human-facing protocols respond when an encounter changes direction. It links breakdowns to exact materials, preserves specialist-boundary contestation, requires passage-level human decisions, and turns situated unknowns into named consultation tasks for real people.

## Agentic Features Implemented in the Current Prototype

### Material-dependent task planning

The Encounter Orchestrator now produces a structured `audit_plan`. Each task records:

- bounded goal and agent owner;
- priority and material-specific routing reason;
- input passage IDs;
- non-chat tools;
- dependencies;
- explicit stop condition;
- status, attempt count, outputs, and result summary.

Scenario tasks are prioritized from the submitted artifacts and encounter-map scope. Missing context is routed as a high-priority probe; possible safeguards are routed for responsibility-aware review; an excluded stage causes a documented pause rather than invented analysis.

### Human scope checkpoint

Researchers can change encounter-stage scope and selected scenarios, then choose **Update task plan** before execution. The system regenerates the plan and records the update in the event log.

### Conditional specialist execution

The engine executes selected scenario tasks in priority order, runs a relationship and responsibility check, optionally invokes a bounded LLM critic only when configured, and releases the Boundary and Handoff task after selected specialist work finishes.

### Bounded task reruns

A researcher can rerun one scenario, relationship, or optional LLM task. The system refreshes the boundary and handoff state afterward. It refuses to rerun a task if doing so would silently overwrite an existing human decision.

### Structured contestation

Each issue preserves two visible positions:

- the specialist’s proposed protocol action;
- the Boundary and Handoff Agent’s statement of what generated analysis cannot settle.

No model vote or synthetic consensus resolves the tension. The researcher must accept, edit, reject, or defer.

### Inspectable shared state

The encounter map, traces, issue ledger, decisions, handoffs, task attempts, and event history are persistent structured objects rather than hidden chat history. JSON, Word, and PDF exports provide both machine-readable and human-readable records.

## What Is Still Not Strong Enough to Claim

- The current routing logic is a bounded, transparent MVP, not evidence of general autonomous reasoning.
- The deterministic checks provide reproducibility but do not establish semantic validity.
- The optional LLM critic is deliberately constrained and should not be presented as an ethics expert.
- Structured contestation is implemented, but its effect on user judgment has not been studied.
- Cross-domain significance remains a hypothesis until users outside HCI recognize and use the workflow.

## Broader Significance and Formative Study

### Shared task

Recruit participants who have authored, adapted, facilitated, or reviewed a sensitive human-facing research, evaluation, consultation, or co-design protocol in the previous two years.

### Primary user groups

1. Academic HCI and UX researchers.
2. Qualitative and mixed-method researchers in health, education, communication, and social science.
3. Applied UX researchers, service designers, public-sector evaluators, and community or nonprofit research staff.

Methods, ethics, data-governance, accessibility, and safeguarding advisors are secondary expert reviewers rather than substitutes for primary protocol preparers.

### Cross-domain cases

Use one full standardized task and two transfer probes:

- online-fraud research and co-design;
- student mental-health service interviews;
- public-benefits access or service co-design.

The cases should share consent, privacy, power, withdrawal, disclosure, responsibility, and follow-up problems while differing in situated resources and decision owners.

### Staged evidence plan

1. **Schema review:** 2-3 methods, ethics, safeguarding, accessibility, or community-research experts inspect the nine encounter stages, six scenarios, routing rules, and handoff owners.
2. **Internal pilot:** 3-5 protocol preparers complete the task; revise only study-blocking usability and instrumentation problems.
3. **Formative comparison:** recruit 12-18 protocol preparers across the three groups. Compare a general LLM chat using a standard prompt with SafeBARS using the same underlying model where possible.
4. **Technical boundary set:** prepare 18-24 seeded protocol cases to test passage validity, known missing transitions, unsupported community claims, routing, task failure, and appropriate handoff generation.

### Outcomes

Do not use issue count as a proxy for ethical quality. Analyze:

- source-passage validity and specificity;
- non-duplicate breakdowns and concrete revisions;
- reasons for accepting, editing, rejecting, or deferring;
- unsupported claims about communities;
- quality and ownership of real-person handoffs;
- task-plan edits, reruns, and explanation fields inspected;
- perceived control, workload, usefulness, and calibrated reliance;
- similarities and differences across user groups and domains.

## Immediate Completion Checklist

- [x] Reframe away from synthetic participant evidence.
- [x] Identify direct novelty collisions.
- [x] Replace the chat-centered home screen.
- [x] Add structured encounter mapping and scenario traces.
- [x] Add passage-level provenance and human decisions.
- [x] Add epistemic handoffs.
- [x] Add visible material-dependent agent task plans.
- [x] Add task tools, dependencies, stop conditions, attempts, and outputs.
- [x] Add bounded specialist reruns with decision protection.
- [x] Add structured specialist-boundary contestation.
- [ ] Obtain expert validity feedback.
- [ ] Finalize three standardized cross-domain cases.
- [ ] Obtain institutional ethics approval.
- [ ] Run the pilot and formative comparison.
- [ ] Replace ephemeral deployment storage before collecting study data.

## Supervisor-Facing Update

> I treated the three comments as redesign requirements rather than presentation changes. First, I mapped the closest CHI, IUI, and DIS work and identified Mirror as a direct collision with broad multi-agent ethics-review claims. SafeBARS is now positioned around pre-fieldwork encounter breakdowns and epistemic handoff. Second, the main system is no longer a chatbot: an Orchestrator creates a material-dependent task plan, specialist agents use bounded tools over shared protocol state, each issue preserves provenance and contestation, and the workflow stops or hands off questions it cannot resolve. Third, I broadened the shared task from HCI research on vulnerable populations to preparation of sensitive human-facing protocols across academic qualitative research, UX and service design, public-sector evaluation, and community research. The remaining step is to validate these claims through expert review and a cross-domain formative comparison with general LLM chat.

## Primary Sources Checked

- Simulacrum of Stories, CHI 2025: https://doi.org/10.1145/3706598.3713220
- Large Language Models in Qualitative Research, CHI 2025: https://doi.org/10.1145/3706598.3713120
- Writer-Defined AI Personas, CHI 2024: https://doi.org/10.1145/3613904.3642406
- Interview AI-ssistant, IUI Companion 2025: https://doi.org/10.1145/3708557.3716148
- InterFlow, CHI 2026: https://doi.org/10.1145/3772318.3790866
- CoBRA, CHI 2026: https://doi.org/10.1145/3772318.3790804
- Who Did What?, DIS 2026: https://doi.org/10.1145/3800645.3812981
- Compass vs Railway Tracks, DIS 2026: https://doi.org/10.1145/3800645.3812956
- Mirror preprint: https://arxiv.org/abs/2602.13292
