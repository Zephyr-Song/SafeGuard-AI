# SafeBARS Provider Comparison Mode Note

Last updated: 2026-06-17

## Purpose

Provider comparison mode lets the researcher send the same rehearsal prompt to:

- template fallback;
- configured Zhipu provider;
- configured Aliyun Bailian provider;
- optional OpenAI-compatible providers A/B.

The goal is not to decide which model is "correct." The goal is to inspect how different providers surface, miss, or overstate ethical and safety risks.

## Why This Matters For SafeBARS

SafeBARS is about bounded pre-fieldwork rehearsal, not participant replacement. Different LLMs may:

- notice different risks;
- phrase concerns with different levels of confidence;
- include or omit the non-replacement boundary;
- provide different revision cues;
- hallucinate or overgeneralize about real communities.

Comparing providers makes these differences visible to the researcher.

## Current UI Workflow

1. Open SafeBARS.
2. Start a session.
3. Type one rehearsal question.
4. Click `Compare Providers`.
5. Review:
   - provider response;
   - risk categories;
   - boundary cues;
   - revision cues;
   - overtrust warnings;
   - comparison summary.
6. Click `Export Comparison` to save the result.

## Current Heuristic Analysis

The comparison analyzer marks:

- risk categories, such as privacy/data handling, distress/shame, participant burden, consent, institutional trust, missing stakeholder/context, victim-blaming wording;
- boundary markers, such as "not evidence," "cannot replace," "real participants," "verify";
- overtrust warnings, such as language that sounds too general or definitive;
- useful revision cues, such as revise wording, clarify procedure, add participant choice, reduce burden, add support/follow-up, verify in real fieldwork.

## Exported Data

Comparison exports are saved in:

```text
data/safebars/
```

File pattern:

```text
safebars_<session_id>_comparison_<timestamp>.json
safebars_<session_id>_comparison_<timestamp>.md
```

The export includes:

- prompt;
- comparison summary;
- each provider's response;
- heuristic analysis for each response.

## How To Use In Self-Pilot

For a self-pilot, use 3-4 sensitive prompts:

1. Is "How much money did you lose and why did you believe the message?" okay?
2. Would recording the session create privacy concerns?
3. Is a two-hour workshop after the interview too much?
4. Does university or police support make participants more comfortable?

For each prompt:

- run provider comparison;
- export comparison;
- write a memo about which risks were surfaced or missed;
- note whether any provider sounded too authoritative;
- revise the research plan based on the comparison.

## What To Claim

Safe claim:

> Provider comparison helped inspect how different synthetic stakeholder generators surface or omit planning risks, making model variability visible during pre-fieldwork rehearsal.

Unsafe claim:

> The provider that gave the most detailed answer is the most accurate representation of real participants.

## Design Implication

For sensitive research planning, model diversity can be useful only when paired with boundary reminders, risk categorization, and researcher reflection. Otherwise, comparing models may simply make overtrust feel more convincing.
