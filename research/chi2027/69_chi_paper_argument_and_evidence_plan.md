# SafeBARS CHI Paper Argument and Evidence Plan

Last updated: 2026-06-19

Purpose: turn the SafeBARS prototype and study materials into a coherent CHI paper argument. This file should guide the next paper draft, supervisor discussion, and pilot/formative study.

## Working Title

SafeBARS: Bounded Synthetic Stakeholders for Rehearsing Sensitive HCI Fieldwork

Alternative titles:

- Rehearsal, Not Replacement: Bias-Calibrated Synthetic Stakeholders for Sensitive Research Planning
- SafeBARS: Calibrating Synthetic Stakeholder Rehearsal Before Sensitive Fieldwork
- From Synthetic Participants to Research Rehearsal: Designing SafeBARS for Sensitive Action Research

## One-Sentence Thesis

SafeBARS contributes a bounded way to use synthetic stakeholders before sensitive fieldwork: not as evidence about communities, but as controllable prompts that help researchers notice risks, revise study plans, and document what must still be verified with real stakeholders.

## Paper Type

The paper should be framed as:

> a formative HCI systems paper about a bounded AI scaffold for ethical pre-fieldwork research preparation.

It should not be framed as:

- a model benchmark paper;
- an anti-fraud intervention for older adults;
- a claim that LLMs can simulate vulnerable communities;
- a paper proving that synthetic stakeholders are accurate.

## Core Problem

Sensitive HCI and action research often begins with imperfect study plans. Researchers may draft interview questions, workshop scripts, or consent procedures that are technically reasonable but emotionally or ethically fragile.

In online fraud prevention research, this can appear as questions such as:

- "How much money did you lose?"
- "Why did you believe the message?"
- "Can your family member explain what happened?"
- "Can we record the workshop?"
- "What will you do differently next time?"

These questions may surface useful information, but they may also create shame, privacy concerns, victim-blaming, family tension, institutional distrust, or distress. Researchers need ways to identify such issues before fieldwork.

## Why Existing Approaches Are Not Enough

### Ordinary peer review is useful but limited

Supervisors and peers can review a study plan, but they may miss stakeholder-specific discomfort, privacy boundaries, or relational tensions.

### Real stakeholder consultation is necessary but not always the first step

Researchers still need real stakeholders. However, entering early meetings with avoidable risks can waste community partners' time or expose them to poorly prepared materials.

### Ordinary LLM role-play is tempting but dangerous

LLM persona role-play can quickly generate reactions, but it risks sounding like participant evidence. This is especially problematic for vulnerable communities because the generated response lacks consent, agency, and situated lived experience.

### SafeBARS's position

SafeBARS treats synthetic stakeholder output as a rehearsal signal. It is useful when it helps researchers ask:

- What assumption is fragile here?
- What wording could be safer?
- What procedure is missing?
- What do we still need to ask real people?

It is not useful when it is treated as:

- evidence about older adults;
- a substitute for formative study;
- proof that a plan is safe;
- a ranked model truth comparison.

## Related Work Argument

The related work should be organized around a tension, not around technologies.

### Thread 1: Controllable agents make rehearsal possible

CoBRA shows that natural-language persona descriptions can be too implicit and inconsistent for controlling social agents, and proposes explicit bias measurement and regulation primitives for LLM agents.

SafeBARS borrows the design move of explicit control, but changes the target. Instead of controlling cognitive bias for social simulation, SafeBARS exposes risk-response dimensions for research-plan rehearsal.

Useful citation anchor:

- CoBRA / Programmable Cognitive Bias in Social Agents: https://arxiv.org/abs/2509.13588

### Thread 2: Synthetic participants make replacement dangerous

Work such as "Simulacrum of Stories" warns that LLM-generated research participants can create a surrogate effect: generated accounts may appear plausible while bypassing consent, agency, contextual depth, and qualitative ways of knowing.

SafeBARS uses this critique as a design constraint. It deliberately frames outputs as prompts for researcher revision, not data from participants.

Useful citation anchor:

- Simulacrum of Stories: https://arxiv.org/abs/2409.19430

### Thread 3: Researchers need intentional LLM tooling

Prior work on LLMs in qualitative research shows that researchers are already experimenting with LLMs, but need clearer norms, boundaries, and tools that align with qualitative values.

SafeBARS contributes one concrete version of intentional tooling: a pre-fieldwork scaffold that directs LLM use toward risk identification, trust calibration, and revision.

Useful citation anchor:

- Large Language Models in Qualitative Research: https://arxiv.org/abs/2410.07362

### Thread 4: AI research tools should be evaluated through artifacts

Human-AI qualitative workflow papers often evaluate how researchers use AI to produce or revise research artifacts, not whether AI is objectively correct.

SafeBARS should follow this pattern by comparing initial plans, rehearsal logs, reflection reports, and revised plans.

Useful citation anchor:

- Human-AI Collaboration in Thematic Analysis using ChatGPT: https://dl.acm.org/doi/10.1145/3613905.3650732

### Thread 5: Online fraud is a sensitive, relational test context

Online fraud prevention with older adults is not only a digital-literacy problem. It involves privacy, shame, family support, trust, reporting, autonomy, and community resources. This makes it a strong context for testing pre-fieldwork rehearsal.

SafeBARS should use online fraud as a concrete domain, while keeping the broader contribution about sensitive HCI fieldwork preparation.

## Refined Research Questions

### RQ1: Risk Identification

How do researchers use bounded synthetic stakeholders to identify ethical, emotional, and procedural risks in sensitive fieldwork plans?

Expected evidence:

- pre-tool risk notes;
- rehearsal prompts;
- risks surfaced in stakeholder responses;
- post-tool interview comments about what the tool helped them notice.

### RQ2: Plan Revision

How does SafeBARS shape concrete revisions to interview questions, workshop scripts, consent language, and safety procedures?

Expected evidence:

- initial plan versus revised plan;
- coded revision categories;
- participant explanations of why they changed wording or procedures.

### RQ3: Trust Calibration

What interface and workflow features help researchers treat synthetic stakeholder responses as rehearsal prompts rather than participant evidence?

Expected evidence:

- comments on limitation framing;
- provider comparison use;
- moments of skepticism or overtrust;
- documented "questions for real stakeholders."

## Evidence Chain

The CHI paper needs an evidence chain that looks like this:

1. Sensitive research plans contain risks that are easy to miss.
2. SafeBARS makes those risks inspectable through controlled stakeholder rehearsal.
3. Researchers use SafeBARS to revise concrete parts of their plans.
4. Researchers also identify boundaries and unresolved questions for real fieldwork.
5. Therefore, bounded synthetic stakeholders can support preparation without replacing participation.

## Data Artifacts Needed

| Artifact | Why it matters | Paper use |
|---|---|---|
| Initial plan | Shows baseline wording and procedure | Methods, findings example |
| Pre-tool risk notes | Shows what researcher noticed before SafeBARS | Pre/post comparison |
| Rehearsal log | Shows interaction with stakeholder profiles | System use and findings |
| Provider comparison output | Shows model variation and trust calibration | Trust calibration finding |
| Reflection report | Shows how chat becomes revision prompts | System figure and finding |
| Revised plan | Main evidence of concrete change | Findings table |
| Interview notes/transcript | Explains usefulness, limits, overtrust | Thematic findings |

## Coding Scheme for Findings

Use the following codes for pre/post plan analysis:

- `privacy_data_boundary`: adds or improves explanation of recording, anonymization, data access, or disclosure options.
- `non_blame_wording`: changes wording that could imply victim blame or poor judgment.
- `optional_disclosure`: makes financial loss, personal story, or emotional detail optional.
- `consent_withdrawal`: clarifies consent, skip, pause, or withdrawal rights.
- `distress_support`: adds support procedure, referral resource, break, or follow-up plan.
- `participant_burden`: reduces session length, task load, or disclosure pressure.
- `stakeholder_ecosystem`: adds family helpers, community workers, institutions, or partner review.
- `autonomy_boundary`: protects affected participants from being spoken for by helpers or institutions.
- `trust_calibration`: notes that synthetic output must be verified or should not be treated as evidence.
- `real_stakeholder_question`: documents a question that must be asked later in real fieldwork.

## Expected Findings Shape

### Finding 1: SafeBARS helped researchers move from extractive questions to safer disclosure boundaries

Likely evidence:

- participants soften exact financial-loss questions;
- participants reframe "why did you believe it?" as "what made the message seem trustworthy at the time?";
- participants add skip or optional disclosure language.

Possible paper figure:

> Before/after plan excerpt with coded changes.

### Finding 2: Stakeholder profiles made hidden assumptions visible

Likely evidence:

- privacy-sensitive profile surfaces data handling;
- family-helper profile surfaces autonomy and consent boundaries;
- community-worker profile surfaces feasibility and follow-up support.

Possible paper figure:

> Profile dimensions mapped to surfaced risk categories.

### Finding 3: Provider comparison supported calibrated skepticism, but also created interpretation work

Likely evidence:

- participants notice that some providers are generic;
- participants treat consensus risks as prompts, not truth;
- participants are confused if comparison looks like a ranking.

Possible paper figure:

> Comparison summary showing consensus, unique risks, provider failure, and user interpretation.

### Finding 4: Reflection reports helped convert conversation into research artifacts

Likely evidence:

- participants use report categories to write revised plans;
- reports are useful when specific, less useful when generic;
- participants want exportable notes for supervisor or ethics review.

### Finding 5: Participants preserved the need for real stakeholder engagement

Likely evidence:

- participants explicitly list questions for older adults, family helpers, or community workers;
- participants reject synthetic responses as evidence;
- participants describe SafeBARS as "preparation" or "checklist expansion."

## Reviewer Concerns and Planned Answers

### Concern: This still replaces vulnerable participants

Answer:

The system and study are designed around non-replacement. The unit of analysis is researcher revision, not stakeholder realism. SafeBARS requires researchers to record what still needs real stakeholder verification.

### Concern: Why not just use a checklist?

Answer:

A checklist can name generic risks, but it cannot create interactive pushback, support multiple stakeholder roles, or expose how wording feels in context. SafeBARS should be compared conceptually to checklists by showing where interaction produces concrete revision.

### Concern: Why do we need provider comparison?

Answer:

Provider comparison is not for ranking truth. It is a trust-calibration feature: it reveals variation, generic responses, and failures so researchers do not over-rely on one fluent answer.

### Concern: Are the bias sliders validated?

Answer:

No. They are not psychometric measures. They are functional controls for rehearsal. The paper should avoid claiming validity and instead study how researchers interpret and use these controls.

### Concern: Is online fraud too narrow?

Answer:

Online fraud is the test context because it has concrete emotional, ethical, and relational risks. The broader contribution is a design pattern for sensitive pre-fieldwork rehearsal.

## What To Build Before Pilot

Must have:

- stable Send response;
- stable Compare Providers;
- clear non-replacement wording;
- export containing plan, log, comparison, reflection, and revision;
- no confusing hidden scroll in comparison area;
- example default plan with intentional risks;
- at least three stakeholder presets.

Nice to have:

- visual risk tags on responses;
- before/after plan diff;
- exportable PDF or Markdown report;
- short demo mode for supervisor meetings.

## What To Ask Supervisor

1. Is the central problem specific enough: rehearsal of sensitive online-fraud fieldwork before real stakeholder engagement?
2. Should the formative study recruit HCI/UX researchers only, or also include community researchers/practitioners?
3. Is online fraud with older adults the right domain anchor, or should it be broadened to sensitive community research?
4. Should the paper emphasize the system contribution, the study contribution, or the non-replacement design framework?
5. What minimum evidence would be enough for a CHI 2027 submission?

## Next Writing Step

Create paper draft v1 with these additions:

1. a sharper introduction that starts with a concrete risky interview question;
2. related work organized by the five tension threads above;
3. a system figure and one worked example;
4. methods section aligned with RQ1-RQ3;
5. findings placeholders rewritten as artifact-based claims.

