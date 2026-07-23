# Adaptive Intake and Export Architecture

## Problem observed after deployment

The original guided intake used ten fixed questions. It was comprehensive, but it made the first interaction feel like a mandatory questionnaire and repeated fields that were already visible in the researcher workspace.

The export menu also described outputs mainly by file format. Users could not easily infer why they might need both an ethics application draft and a Word report.

## Revised intake

SafeBARS now asks six core questions:

1. research area, university or organisation, school or department, review
   pathway and jurisdiction, followed by the proposed aim, setting, method, and
   whether AI is involved;
2. participants, relationships, and recruitment;
3. consent and withdrawal;
4. questions, procedures, activities, accessibility, and alternatives;
5. risk, safeguarding, and support;
6. follow-up, complaints, and data management.

If the first answer indicates AI use, SafeBARS adds one structured conditional
supplement covering the AI purpose and decision role, data source and intended
population, performance and subgroup bias, disclosure and consent, privacy and
security, human oversight and monitoring, stopping and fallback, correction,
complaints, and accountable ownership. The supplement is informed by Makridis
et al. (2023) and Connelly et al. (2025), alongside NIST AI RMF.

Researchers may skip any question and refine the visible structured fields later. Missing or partial information remains visible in the application-readiness view rather than being hidden by forced completion.

## Export distinction

### Application draft

Purpose: help the researcher prepare submission-oriented content.

Includes:

- application profile and field completeness;
- project, recruitment, consent, procedures, risk, data, and AI sections;
- researcher decisions and revisions;
- unresolved expert and stakeholder handoffs;
- a prominent non-approval and institution-specific-form boundary.

### Full audit report

Purpose: preserve the internal reasoning and evidence trail.

Includes:

- framework-grounded ethics map;
- encounter stages and scenario traces;
- issue ledger and exact submitted passages;
- agent positions, tools, dependencies, stopping rules, and rerun state;
- expert handoffs and researcher responses;
- submitted materials and append-only event history.

The application draft is form-oriented; the full audit report is provenance-oriented. Neither is an approval decision.
