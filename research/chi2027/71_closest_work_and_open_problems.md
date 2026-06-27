# SafeBARS Closest Work and Open-Problem Map

Date: 2026-06-27

Purpose: answer the supervisor's first question: which CHI/IUI/DIS papers are closest to SafeBARS, what unresolved problems do they expose, and which of those problems can SafeBARS credibly address in a short CHI 2027 project.

## Selection Logic

A paper is treated as close when it overlaps with at least two of these concerns:

1. LLM personas, simulated users, or social agents;
2. AI support for research, design, or evaluation work;
3. structured interaction beyond a single chatbot;
4. multi-agent coordination, control, or human oversight;
5. representational, ethical, or epistemic risk.

This is an initial nearest-neighbor set, not a claim that the literature search is complete.

## Closest Papers

| Priority | Paper | Venue | What it contributes | Unresolved issue exposed by the paper | SafeBARS response |
|---|---|---|---|---|---|
| 1 | CoBRA: Programming Cognitive Bias in Social Agents Using Classic Social Science Experiments | CHI 2026, Best Paper | Makes selected cognitive biases explicit, measurable, and regulatable rather than hiding them inside broad persona descriptions. | Controllability is evaluated for agent behavior, but not translated into a human-centered workflow for inspecting sensitive research protocols. Cognitive-bias control also does not by itself establish ethical or contextual validity. | Reuse explicit controls as bounded challenge settings, but change the target from simulating people to stress-testing researcher-authored artifacts. Record which setting triggered which critique and revision. |
| 2 | Simulacrum of Stories: Examining Large Language Models as Qualitative Research Participants | CHI 2025 | Shows that plausible synthetic interviews still foreclose consent and agency, lack contextual depth, and can delegitimize qualitative ways of knowing. Introduces the surrogate-effect critique. | The paper gives a strong reason not to replace participants, but leaves open what a legitimate, non-substitutive use of generated perspectives in research preparation could look like. | Make non-replacement an operational system property: agents cannot generate findings about a community; they can only flag risks, generate questions for real stakeholders, and propose edits to the researcher's protocol. |
| 3 | SimUser: Generating Usability Feedback by Simulating Various Users Interacting with Mobile Applications | CHI 2024 | Uses simulated users to traverse interfaces and generate usability feedback, demonstrating a task-oriented alternative to static personas. | Simulated feedback can be mistaken for user evidence, and usability-task simulation does not address consent, distress, power, or community relationships in sensitive fieldwork. | Use task-oriented agents to execute protocol checks and adverse scenarios, while labeling every output as a planning hypothesis and requiring real-stakeholder verification. |
| 4 | Writer-Defined AI Personas for On-Demand Feedback Generation | CHI 2024 | Lets writers define multiple audience personas and request feedback that can prompt text revision. | Users find persona definition difficult; feedback can be verbose, repetitive, unspecific, and influential despite limited representativity. | Replace free-form persona authoring with role cards and risk dimensions; produce issue cards tied to exact protocol passages; require accept, reject, or defer decisions for every proposed revision. |
| 5 | Deus Ex Machina and Personas from Large Language Models | CHI 2024 | Empirically examines the composition of LLM-generated personas and identifies stereotyping, positivity, cultural limitations, and uncertain representativeness. | More detailed personas can still produce invented specificity and stereotype vulnerable identities. More realism is not a sufficient safety strategy. | Do not generate demographic biographies. Use minimal stakeholder roles plus explicit situational concerns. Add a boundary agent that detects unsupported identity claims, invented lived experience, and stereotype-like generalizations. |
| 6 | Beyond ChatBots: ExploreLLM for Structured Thoughts and Personalized Model Responses | CHI 2024 | Shows how structured graphical controls can reduce the interaction burden of text-only chatbot exploration. | Structured interfaces improve navigation, but the problem of when users should intervene, verify, or reject LLM outputs remains open for high-stakes work. | Make the primary interface an inspectable protocol workspace: artifact parsing, risk coverage map, scenario queue, agent activity, disagreement map, and tracked revisions. Chat becomes optional evidence, not the main interaction. |
| 7 | Controlling AI Agent Participation in Group Conversations: A Human-Centered Approach | IUI 2025 | Develops controls over when, what, and where an agent responds, who controls it, and how participation is specified. | Agent participation can dominate a group, and control needs differ across moments and users. The paper focuses on group ideation rather than high-stakes review work. | Give researchers control over agent scope, turn order, stopping conditions, and escalation. Agents act only on selected artifacts and cannot silently edit or approve a protocol. |
| 8 | Designing with Multi-Agent Generative AI: Insights from Industry Early Adopters | DIS 2025 | Identifies practical needs for managing agent complexity, transparency, autonomy, and human oversight in multi-agent systems. | Adding agents can obscure responsibility and make workflows harder to inspect; role specialization alone does not guarantee useful collaboration. | Use a fixed, visible workflow with named responsibilities, inspectable handoffs, disagreement rather than forced consensus, and human approval gates before any revision is saved. |

## What Existing Work Already Covers

SafeBARS should not claim novelty for any of the following by itself:

- simulating users or personas with an LLM;
- obtaining feedback from several personas;
- adding sliders to steer agent behavior;
- placing LLM responses beside a document;
- running multiple role-prompted agents;
- warning that synthetic participants are not real people;
- displaying several providers side by side.

These are ingredients, not a CHI contribution.

## Strongest Open Problem

The strongest tractable gap is:

> How can an inspectable, bounded multi-agent system proactively stress-test sensitive human-facing research protocols, produce traceable revisions, and preserve human and community epistemic authority without presenting synthetic stakeholders as participant evidence?

This gap connects the selected papers instead of merely sitting beside them:

- CoBRA supplies explicit behavioral control;
- Simulacrum supplies the non-replacement boundary;
- SimUser supplies task-oriented agent action;
- AI-persona work supplies multi-perspective feedback and its representational risks;
- ExploreLLM supplies the beyond-chat interaction requirement;
- IUI agent-control work supplies mixed-initiative control;
- DIS multi-agent work supplies transparency and oversight requirements.

## Proposed Originality Claim

SafeBARS is not a synthetic-participant system. It is an agentic protocol-auditing and revision environment for sensitive human-facing work. Its agents act on research artifacts, not as evidence-producing substitutes for people.

The original system contribution should combine four properties:

1. Artifact-centered agency: agents parse and inspect interview guides, consent language, workshop plans, recruitment text, and safety procedures.
2. Adversarial but bounded roles: agents search for different classes of failure without claiming lived experience or demographic representativity.
3. Traceable revision: each issue links the original passage, triggering scenario, agent rationale, proposed change, and researcher decision.
4. Epistemic handoff: uncertain claims become questions or consultation tasks for real participants, community partners, domain experts, or ethics reviewers.

## Candidate Research Questions After Step 1

### RQ1: Protocol Risk Discovery

How does an artifact-centered multi-agent audit help practitioners identify ethical, emotional, relational, and procedural risks in sensitive human-facing protocols?

### RQ2: Revision and Traceability

How do practitioners use, reject, or defer agent-generated critiques when revising protocols, and what traceability information supports those decisions?

### RQ3: Calibrated Reliance

How do explicit disagreement, uncertainty, and real-stakeholder handoff mechanisms shape practitioners' reliance on agent-generated critiques?

## Paper-by-Paper Design Requirements

SafeBARS v2 should satisfy the following requirements before a user study:

- From CoBRA: expose controllable behavior dimensions and test whether they produce distinguishable audit behavior.
- From Simulacrum: prohibit participant-replacement claims in prompts, labels, reports, and study measures.
- From SimUser: agents must carry out structured tasks, not wait passively for chat prompts.
- From Writer-Defined AI Personas: feedback must be passage-specific, concise, and revision-oriented.
- From Deus Ex Machina: avoid generated demographic biographies and detect unsupported identity generalizations.
- From ExploreLLM: the core workflow must remain usable without writing a sequence of chat prompts.
- From IUI 2025: users must control agent participation and interruption.
- From DIS 2025: expose agent roles, handoffs, disagreements, and approval points.

## Sources

- CoBRA project and paper: https://cobra.clawder.ai/ and https://arxiv.org/abs/2509.13588
- Simulacrum of Stories: https://doi.org/10.1145/3706598.3713220
- SimUser: https://doi.org/10.1145/3613904.3642481
- Writer-Defined AI Personas: https://doi.org/10.1145/3613904.3642406
- Deus Ex Machina and Personas from LLMs: https://doi.org/10.1145/3613904.3642036
- Beyond ChatBots: ExploreLLM: https://doi.org/10.1145/3613905.3651093
- Controlling AI Agent Participation: https://doi.org/10.1145/3708359.3712089
- Designing with Multi-Agent Generative AI: https://doi.org/10.1145/3715336.3735823

## Step 1 Decision

Proceed with the artifact-centered agentic protocol-audit framing. Do not invest further in making the synthetic stakeholder chat more human-like. The next design step is to specify the autonomous tasks, inter-agent handoffs, human control points, and visible artifacts that make this framing real.
