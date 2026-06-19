# Paper Example Figure Text

Last updated: 2026-06-19

Purpose: prepare text that can be converted into CHI paper figures or slide screenshots.

## Figure 1: SafeBARS Workflow

Caption draft:

> SafeBARS supports a bounded pre-fieldwork rehearsal workflow. Researchers enter a sensitive research plan, select or adjust a synthetic stakeholder profile, rehearse interview questions or procedures, compare provider responses, generate a reflection report, and write a revised plan. The system frames synthetic stakeholder output as planning prompts rather than participant evidence.

Flow:

1. Research plan input.
2. Stakeholder role and risk-response profile.
3. Rehearsal chat.
4. Provider comparison.
5. Reflection report.
6. Revised plan.
7. Export for analysis.

## Figure 2: Bias / Risk-Response Profile

Caption draft:

> SafeBARS exposes risk-response profile dimensions as functional rehearsal controls. These controls do not measure real people; they help researchers inspect how study plans might be challenged under different concerns, such as privacy sensitivity, shame/stigma sensitivity, institutional distrust, and participant burden.

Suggested visible dimensions:

- privacy sensitivity;
- shame/stigma sensitivity;
- institutional distrust;
- distress sensitivity;
- participant burden sensitivity;
- victim-blaming risk.

## Figure 3: Example Rehearsal Response

Prompt:

> Would you be comfortable if I ask how much money you lost and why you believed the message?

Synthetic stakeholder response excerpt:

> I would feel uncomfortable with that wording. It sounds like you already think I did something wrong... A safer question might ask what made the message seem trustworthy at the time.

System interpretation:

> Privacy/data risk and shame/judgment risk. Revise the question to make exact loss optional, avoid blame, and explain why each detail is needed.

Caption draft:

> Example SafeBARS rehearsal turn. The synthetic stakeholder response is not treated as participant evidence; it is converted into a planning interpretation that helps the researcher revise interview wording.

## Figure 4: Provider Comparison

Caption draft:

> Provider comparison shows how different response sources surface or miss planning risks. The comparison is designed for trust calibration: disagreement, generic responses, and provider failures remind researchers not to treat any model response as ground truth.

Columns/cards:

- Template fallback.
- Zhipu.
- Aliyun Bailian.
- Tencent TokenHub.
- Xunfei MaaS DeepSeek V4 Flash.
- Optional generic provider.

Key fields:

- assessment;
- risks;
- boundary cues;
- revision cues;
- response text;
- error detail if unavailable.

## Figure 5: Pre/Post Plan Revision

Caption draft:

> Example artifact change from internal dry run. Before SafeBARS, the plan asked participants how much money they lost and why they believed a scam message. After rehearsal, the revised plan makes exact loss optional, reframes belief as perceived trustworthiness, adds recording choices, and identifies questions for real stakeholder verification.

Before:

> Ask: How much money did you lose? Why did you believe the message? We will record the session for analysis.

After:

> Make loss amount optional. Ask what made the message seem trustworthy at the time. Explain recording choices and anonymization before any sensitive question. Ask real stakeholders which examples are useful without creating embarrassment or distress.

## Figure 6: Planned Study Data Flow

Caption draft:

> Planned formative study data flow. Participants produce an initial plan, use SafeBARS for rehearsal, generate a reflection report, and write a revised plan. Analysis compares pre/post artifacts and interview accounts to examine risk identification, plan revision, and trust calibration.

Flow:

1. Initial plan.
2. Pre-tool risk notes.
3. SafeBARS interaction logs.
4. Reflection report.
5. Revised plan.
6. Post-study interview.
7. Coding and thematic analysis.

