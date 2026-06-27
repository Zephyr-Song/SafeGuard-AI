# SafeBARS Novelty Collision Audit

Date: 2026-06-27

Status: rapid structured scoping review for project decisions. This is not a completed systematic review and cannot establish that no prior work exists.

## Purpose

This memo tries to falsify the proposed SafeBARS novelty claim. It asks which parts of the project have already been covered, which papers create the strongest collision, and what contribution remains defensible for CHI 2027.

## Search Scope

### Venues and period

- CHI and CHI Extended Abstracts, 2023-2026;
- IUI and IUI Companion, 2024-2026;
- DIS, 2024-2026;
- adjacent ACM, ACL, and arXiv work when it creates a direct collision;
- selected current products to avoid presenting a product feature as a research novelty.

### Query families

1. synthetic participant, synthetic user, persona, stakeholder simulation;
2. qualitative research, user research, interview preparation, interview assistance;
3. research protocol, ethics review, IRB, consent, safety procedure;
4. multi-agent, agentic workflow, human oversight, confirmation, contestability;
5. pre-fieldwork, rehearsal, stress test, sensitive interview, vulnerable population.

### Inclusion rule

Include work that overlaps with at least two of the following:

- represents or simulates people;
- supports a research-method task;
- inspects or acts on a research artifact;
- coordinates multiple AI roles or steps;
- provides human control over agent actions;
- addresses ethics, privacy, representation, or sensitive interactions.

## Main Collision Finding

The broad claim below is no longer defensible:

> SafeBARS is the first multi-agent system for auditing research protocols before sensitive fieldwork.

The 2026 preprint *Mirror: A Multi-Agent System for AI-Assisted Ethics Review* already analyzes research dossiers through executable rules, evidence retrieval, specialist agents, structured deliberation, unresolved issues, and protocol-revision recommendations. It is a direct collision with any contribution framed mainly as multi-agent research ethics review.

SafeBARS must therefore avoid claiming novelty for:

- multi-agent review of research protocols;
- specialist agents covering consent, privacy, vulnerability, and risk;
- evidence-linked protocol findings;
- simulated committee deliberation;
- structured reports and revision recommendations;
- human-in-the-loop ethics review in general.

## Collision Matrix

| Work | Venue/year | Overlap with SafeBARS | Collision level | What it rules out as a novelty claim | Remaining distinction |
|---|---|---|---|---|---|
| Mirror: A Multi-Agent System for AI-Assisted Ethics Review | arXiv 2026 | Multi-agent protocol review, rule grounding, expert deliberation, revision recommendations | Very high | First multi-agent ethics or protocol-review system | Mirror targets institutional review, compliance, and committee-level assessment, primarily in life science. It does not study researcher-facing rehearsal of relational fieldwork breakdowns or epistemic handoff to communities. |
| Interview AI-ssistant | IUI Companion 2025 | AI assistance in interview preparation and execution | High | First AI tool for interview preparation | SafeBARS can focus on pre-contact risk rehearsal across a complete fieldwork protocol rather than interviewer performance and real-time assistance. |
| InterFlow | CHI 2026 | Proactive AI scaffolding for semi-structured interviewing, script adaptation, follow-up suggestions | High | First proactive AI support for qualitative interviewing; first non-chat interview interface | InterFlow operates during real interviews and optimizes flow and cognitive load. SafeBARS should operate before contact and examine relational and procedural failure paths. |
| CoBRA | CHI 2026 | Explicit control of social-agent behavior | High for controllability | First explicit or quantitative control of agent tendencies | SafeBARS can use controls to vary challenge conditions, but controllability is an implementation ingredient rather than the contribution. |
| Simulacrum of Stories | CHI 2025 | Critique of LLMs as qualitative participants | High for ethics framing | First non-replacement critique of synthetic participants | SafeBARS can operationalize non-replacement as system permissions, outputs, and handoff behavior. |
| HumanStudy-Bench | arXiv 2026 | Full-protocol execution with simulated participants and agent-design evaluation | High for protocol simulation | First system to execute human-study protocols with agents | SafeBARS must reject fidelity evaluation and instead study researcher reflection and protocol revisions. |
| Roleplay-doh | EMNLP 2024 | Expert-defined principles for controllable simulated patients in sensitive interactions | Medium-high | First expert-guided sensitive roleplay or principle-adherence pipeline | SafeBARS can stress-test researcher procedures without optimizing human realism or training a novice to interact with a realistic patient. |
| Agentic Audio Moderator vs Human Moderator | CHI 2026 | Agentic automation of think-aloud user studies with human intervention protocols | Medium-high | First agentic support for conducting user research | SafeBARS is not an automated moderator and should remain outside live data collection. |
| AI-Driven Co-Construction of Synthetic Personas | CHI EA 2026 | Synthetic personas for early user research | Medium-high | First early-stage synthetic-persona research tool | SafeBARS should not create synthetic customer insight or personas as findings. |
| Writer-Defined AI Personas | CHI 2024 | Multiple AI perspectives produce artifact feedback and revision | Medium-high | First persona-based multi-perspective feedback and revision | SafeBARS must add protocol-stage traces, failure scenarios, boundary checks, and real-stakeholder handoffs. |
| SimUser | CHI 2024 | Simulated users execute tasks and generate usability feedback | Medium | First task-oriented simulated-user evaluation | SafeBARS traces protocol responses to adverse fieldwork events rather than claiming usability evidence from simulated users. |
| Deus Ex Machina and Personas from LLMs | CHI 2024 | Bias and stereotype analysis of generated personas | Medium | First critique of persona representativity and stereotype risk | SafeBARS can avoid demographic biographies and detect unsupported community claims. |
| Disclose with Care | arXiv 2026 | Privacy controls for sensitive chatbot interviews | Medium | First privacy support for sensitive AI-mediated interviews | SafeBARS addresses the researcher's pre-fieldwork plan, not participant transcript editing after disclosure. |
| Qux360 | IUI 2026 Demo | Validation-first framework for AI-supported qualitative analysis | Medium | First transparent validation layer in AI qualitative research | SafeBARS operates before data collection and validates neither themes nor participant identification. |
| Large Language Models in Qualitative Research | CHI 2025 | Intentional use, privacy, transparency, context, participant interests | Medium | First design principles for intentional LLM use in qualitative work | SafeBARS can instantiate these principles in one pre-fieldwork workflow and empirically study their use. |
| AI for Qualitative User Research | CHI EA 2026 | Proactive AI scaffolding across diary, interview, and retrospective methods | Medium | First proactive in-situ AI scaffold for qualitative user research | SafeBARS is pre-fieldwork and risk-oriented, with no participant data or in-situ inference. |
| Magentic-UI | arXiv 2025 | Co-planning, co-tasking, action guards, inspectable agent workflow | Medium for interaction | First human-in-the-loop agent workflow or co-planning interface | SafeBARS can contribute domain-specific interaction needs, not general oversight primitives. |
| When Should Users Check? | CHI 2026 | Intermediate confirmation in multi-step agent tasks | Medium for oversight | First strategically placed human confirmation | SafeBARS should justify domain-specific checkpoints around normative uncertainty and real-world handoff rather than efficiency alone. |
| Controlling AI Agent Participation in Group Conversations | IUI 2025 | Controls over when, what, and where an agent participates | Medium for mixed initiative | First user control over agent participation | SafeBARS can apply participation control to protocol review, but cannot claim the control taxonomy itself. |
| Designing with Multi-Agent Generative AI | DIS 2025 | Transparency, complexity, autonomy, and human oversight | Medium for multi-agent framing | First HCI account of multi-agent workflow design challenges | SafeBARS can provide an empirical case in sensitive research preparation. |
| ExploreLLM | CHI EA 2024 | Structured interfaces beyond a chatbot | Medium for UI | First beyond-chat LLM interface | SafeBARS needs a domain-specific artifact and scenario workspace; graphical structure alone is not novel. |

## What the Search Did Not Find

Within this rapid search, no located CHI, IUI, or DIS paper combined all of the following:

1. preparation before participant or community contact;
2. sensitive social or behavioral fieldwork rather than institutional compliance review;
3. protocol-level rehearsal of relational breakdowns and adverse encounter sequences;
4. explicit refusal to treat generated perspectives as participant evidence;
5. passage-level revision decisions made by the researcher;
6. conversion of model uncertainty into consultation tasks for real stakeholders;
7. empirical evaluation of how protocol preparers inspect, reject, revise, and defer agent output.

This combination is a promising gap, not proof of global novelty. The claim must remain scoped to the literature actually reviewed.

## Strongest Remaining Research Problem

Institutional ethics review and AI-assisted interviewing are increasingly supported by LLM systems, but a different form of preparation remains underexplored: rehearsing how a research encounter may break down before fieldwork begins.

Sensitive fieldwork can fail without violating a simple rule. For example:

- a technically optional question may still feel blaming;
- a withdrawal script may be legally present but socially difficult to use;
- a family helper may unintentionally pressure disclosure;
- a referral plan may not specify who acts after distress;
- a reporting pathway may assume trust in an institution;
- the researcher may not know which question must be answered by a community partner rather than an AI system.

These are relational and procedural contingencies, not only compliance violations.

## Revised System Category

Use this category:

> Agentic encounter stress-testing for sensitive fieldwork preparation.

Avoid these primary categories:

- AI ethics review;
- automated IRB;
- synthetic participant research;
- interview assistant;
- multi-agent persona panel.

## Revised Differentiation from Mirror

| Dimension | Mirror | SafeBARS revised direction |
|---|---|---|
| Primary user | Ethics committee or institutional reviewer | Researcher or practitioner preparing fieldwork |
| Primary goal | Compliance and committee-level ethical assessment | Reflection on encounter breakdowns and revision before contact |
| Main knowledge source | Regulations, ethics corpus, expert review dimensions | Research artifacts, scenario templates, relationship and safety heuristics |
| Agent roles | Ethics, law, medicine, life science, disciplinary expert, social representative, PI, secretary | Encounter planner, breakdown scenario agent, relationship and power agent, boundary critic, revision and handoff agent |
| Main output | Compliance verdicts, committee assessment, recommendations | Failure traces, passage-level revision options, unresolved questions, real-person handoff tasks |
| Treatment of uncertainty | Unresolved committee issue | Explicit reason to pause simulation and consult a named real stakeholder |
| Evaluation | Model benchmarks and expert assessment | Human-centered study of researcher decisions, contestability, reflection, and protocol change |
| Authority claim | Support for institutional ethics review | No ethics approval, compliance, or participant-knowledge claim |

## Revised Differentiation from Interview AI-ssistant and InterFlow

| Dimension | Interview support systems | SafeBARS revised direction |
|---|---|---|
| Time | Preparation plus live interview, or live interview | Before recruitment or participant contact |
| Main problem | Interviewer cognitive load, flow, follow-up, and rapport | Whether the entire encounter plan can respond to sensitive breakdowns |
| Input | Interview script and live conversation | Recruitment, consent, questions, activity scripts, safety, data, and follow-up procedures |
| Output | Suggested questions, summaries, script navigation | Scenario traces, missing response paths, revisions, and stakeholder handoffs |
| Participant data | May process live conversation | Must not require real participant data |

## Claims We Can and Cannot Make

### Do not claim

- first multi-agent research ethics reviewer;
- first agentic system for research protocols;
- first AI interview-preparation tool;
- first controllable synthetic stakeholder;
- first structured interface beyond chat;
- first human-in-the-loop multi-agent workflow;
- proof that generated stakeholder reactions are realistic;
- proof that SafeBARS makes research ethical or safe.

### Candidate defensible claim

> We design and study an agentic encounter stress-testing workflow that helps protocol preparers trace relational and procedural breakdowns, make passage-level revision decisions, and convert model limitations into explicit questions for real stakeholders before sensitive fieldwork.

Use “to our knowledge” only after a documented database search and supervisor review.

## Design Changes Required by the Audit

### Remove or demote

- “Ethics and Safety Auditor” as the system's central identity;
- committee-style agent debate;
- provider consensus as a signal of correctness;
- synthetic participant chat as the primary screen;
- generic ethical-risk report sections;
- claims about bias calibration without behavioral validation.

### Add or prioritize

1. Encounter map: recruitment, arrival, consent, activity, disclosure, pause, withdrawal, follow-up, and escalation stages.
2. Breakdown scenario traces: the agent walks through what the protocol says should happen after a specific event and stops at missing transitions.
3. Relationship and power map: who can pressure, support, gatekeep, receive disclosures, or take responsibility.
4. Passage-level issue provenance: every concern links to a protocol passage, scenario step, heuristic, and uncertainty note.
5. Epistemic handoff: unresolved questions are assigned to a real participant group, community partner, methods expert, domain professional, or ethics reviewer.
6. Decision ledger: accept, edit, reject, or defer each proposed change with a researcher rationale.
7. Boundary critic: remove unsupported claims about what a community thinks, feels, or will do.

## Updated Novelty Risk Assessment

- Multi-agent architecture novelty: low.
- Synthetic stakeholder novelty: low.
- Protocol review novelty: low after Mirror.
- Sensitive qualitative-research context novelty: medium.
- Encounter-breakdown rehearsal novelty: medium-high based on the reviewed set.
- Epistemic handoff as a first-class interaction object: medium-high based on the reviewed set.
- Human study of contestable agent-supported protocol revision: medium-high based on the reviewed set.

The paper should make its contribution through the last three items, supported by empirical evidence, rather than through the number of agents or models.

## Sources Added in This Audit

- Mirror: https://arxiv.org/abs/2602.13292
- Interview AI-ssistant: https://doi.org/10.1145/3708557.3716148
- InterFlow: https://doi.org/10.1145/3772318.3790866
- Qux360: https://research.ibm.com/publications/qux360-a-validation-framework-for-improving-reliability-and-transparency-of-ai-supported-qualitative-analysis
- HumanStudy-Bench: https://arxiv.org/abs/2602.00685
- Agentic Audio Moderator: https://doi.org/10.1145/3772318.3791653
- AI for Qualitative User Research: https://doi.org/10.1145/3772363.3799210
- When Should Users Check?: https://doi.org/10.1145/3772318.3790655
- Roleplay-doh: https://aclanthology.org/2024.emnlp-main.591/
- Disclose with Care: https://arxiv.org/abs/2602.01387
- Magentic-UI: https://arxiv.org/abs/2507.22358

## Collision Audit Decision

Continue the project, but pivot the main novelty claim away from multi-agent ethics review. The next prototype should demonstrate encounter-stage modeling, failure-path tracing, and epistemic handoff. Without those three capabilities, the system remains too close to Mirror, generic agent-review systems, and AI interview assistants.
