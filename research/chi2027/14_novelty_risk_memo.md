# Novelty Risk Memo

Last updated: 2026-06-16

## Purpose

This memo identifies papers and framings that could threaten the novelty of SafeBARS, then defines how the project should avoid those traps.

## Risk 1: "This is just CoBRA applied to scams"

### Why Reviewers Might Think This

The project explicitly borrows from CoBRA's idea of measuring and controlling bias in LLM agents.

### Why SafeBARS Is Different

CoBRA's main contribution is technical/methodological control of cognitive bias in LLM social agents. SafeBARS studies how bias-controlled synthetic stakeholders can scaffold human researchers' pre-fieldwork planning.

### How to Avoid the Risk

- Do not present SafeBARS as a better CBI or better agent control method.
- Present SafeBARS as a human-AI interaction system for research preparation.
- Use CoBRA as inspiration, not as the direct baseline.
- Evaluate human researcher outcomes, not only agent behavior.

## Risk 2: "This is just another synthetic users paper"

### Why Reviewers Might Think This

The system generates synthetic stakeholders, and synthetic users are already a growing topic.

### Why SafeBARS Is Different

SafeBARS does not use synthetic stakeholders as substitutes for real users or participants. It uses them as bounded rehearsal lenses to help researchers identify assumptions and risks before real engagement.

### How to Avoid the Risk

- Use "synthetic stakeholders" carefully.
- Avoid phrases like "simulate real participants."
- Include explicit limitation warnings in the system.
- Include "questions to verify with real participants" in every reflection report.
- Study trust calibration directly.

## Risk 3: "This duplicates ROLESafe or anti-fraud education work"

### Why Reviewers Might Think This

The current SafeGuard-AI prototype and demo domain involve online fraud.

### Why SafeBARS Is Different

ROLESafe targets older adults as learners and evaluates role-based fraud education. SafeBARS targets researchers who are preparing action research or interventions in digital safety contexts.

### How to Avoid the Risk

- Do not frame the paper as an anti-fraud learning intervention.
- Use online fraud as a high-risk example domain, not the whole contribution.
- Emphasize researcher-facing planning, ethics, and reflexivity.
- Include stakeholder roles beyond victim/learner, such as family helper and community worker.

## Risk 4: "This is just ChatGPT role-play with a dashboard"

### Why Reviewers Might Think This

The v1 implementation may use prompt-based calibration and a chat interface.

### Why SafeBARS Is Different

The research contribution is the structured workflow:

- Research plan input.
- Explicit stakeholder role coverage.
- Adjustable risk-response profiles.
- Rehearsal modes.
- Reflection analysis.
- Trust calibration.
- Pre/post research plan revision.

### How to Avoid the Risk

- Build a clear workflow, not only chat.
- Log pre/post plan revisions.
- Make bias profiles visible and adjustable.
- Show how the reflection dashboard changes researcher practice.
- Compare against ordinary LLM brainstorming in the pilot if time allows.

## Risk 5: "The bias scores are not validated"

### Why Reviewers Might Think This

The proposed 0-4 bias dimensions may look like psychological measurements.

### Why SafeBARS Is Different

SafeBARS uses these scores as functional rehearsal variables, not validated psychometric constructs.

### How to Avoid the Risk

- Say "risk-response profiles" instead of "true cognitive traits" when possible.
- Explicitly state that profiles do not measure real human vulnerability.
- Evaluate whether researchers find profiles useful for reflection.
- If possible, run a small monotonicity check to show profiles produce expected response changes.

## Risk 6: "The study is too small"

### Why Reviewers Might Think This

A 6-8 person formative study may look weak for a full CHI paper.

### How to Avoid the Risk

Preferred evidence package:

1. Formative interviews or study with 6-8 researchers.
2. Prototype iteration.
3. Small pilot comparison with 12-18 participants.

If only one study is possible:

- Make it deep and artifact-rich.
- Collect initial plans, interaction logs, revised plans, and interviews.
- Analyze plan revisions systematically.

## Risk 7: "The system could encourage replacing participants"

### Why Reviewers Might Think This

Any synthetic stakeholder system may be ethically suspicious.

### How to Avoid the Risk

- Build limitation warnings into the interface.
- Make "not a replacement" a core design principle.
- Include prompts that ask what must be verified with real participants.
- Discuss epistemic injustice and flattening risks.
- Use the study to examine whether the system actually helps or harms trust calibration.

## Risk 8: "The domain is too narrow"

### Why Reviewers Might Think This

If all examples are online fraud with older adults, reviewers may see SafeBARS as a niche fraud research tool.

### How to Avoid the Risk

- Present online fraud as the initial high-risk digital safety case.
- Design the framework to generalize to other sensitive domains.
- Include at least one additional demo scenario, such as AI safety education or digital privacy intervention.

## Strongest Current Novelty Claim

SafeBARS is novel because it reframes synthetic stakeholders from participant replacements into controllable rehearsal aids for high-risk action research, combining bias-profile control, reflection scaffolding, and trust calibration in a researcher-facing workflow.

## Weak Claims to Avoid

Avoid claiming:

- "We accurately simulate fraud victims."
- "Synthetic stakeholders replace formative interviews."
- "Our bias profiles measure real human cognitive biases."
- "Our system proves what real participants would say."
- "This is a general theory of human behavior."

## Strong Claims to Use

Use claims like:

- "SafeBARS helps researchers inspect assumptions before fieldwork."
- "Bias profiles make scenario assumptions explicit and adjustable."
- "Synthetic stakeholder rehearsal can reveal planning gaps that researchers can later verify with real participants."
- "The system is designed to support, not replace, participatory engagement."

