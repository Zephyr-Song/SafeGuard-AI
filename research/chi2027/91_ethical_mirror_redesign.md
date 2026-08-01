# SafeBARS Ethical Mirror: Redesign Decision

Date: 2026-07-30
Status: implemented research-prototype direction; no human-study evidence yet

## One-sentence idea

SafeBARS Ethical Mirror helps computer-science researchers notice and act on
unintended consequences of proposed AI apps by gradually eliciting their own
value commitments, running bounded synthetic role probes, visualising the
commitment–design–consequence mismatch, and replaying the same probes after a
research-design revision.

## Single research question

> Compared with general-purpose LLM chat, how does a literature-grounded,
> multi-role Ethical Mirror that visualises discrepancies between researchers’
> stated values and plausible affected-party scenarios influence the
> recognition of unintended consequences and consequential revision of AI-app
> research plans?

This question combines the intended cognitive and behavioural contribution:
not merely whether participants can list more concerns, but whether they turn
reasoned concerns into inspectable design changes.

## Interaction mechanism

1. **Gradual elicitation.** Eight one-at-a-time questions move from research
   context and intended benefit to the direct encounter, AI authority, data,
   indirect effects, a researcher-authored value commitment, and a concrete
   redesign threshold.
2. **Conditional sensitive-data pause.** If the researcher proposes camera,
   biometric, demographic, health, disability, family-status, or similar
   inference, a ninth question asks why it is necessary and whether a less
   intrusive alternative is possible.
3. **Evidence lenses.** Nine literature-derived lenses show Missing, Claimed,
   Reasoned, or Action-linked plan evidence. These states are not an ethics
   score or approval decision.
4. **Bounded role probes.** Direct user, affected non-user, downstream
   deployer, adversarial reuser, and maintainer/auditor roles each have a
   distinct objective and stopping rule. A configured server-side model can
   enrich them in one batched call; deterministic probes remain available if
   every provider fails.
5. **Visible dissonance.** An interactive map connects “what I said I value” to
   a submitted plan passage, a possible consequence, and an affected position.
   The system does not label the researcher or project unethical.
6. **Researcher agency.** The researcher may revise, add a safeguard, contest
   with evidence, or leave the question for real affected people or experts.
7. **Counterfactual replay.** The same lenses and roles are applied to the
   revised plan. The ledger separates a recorded design change from tensions
   that remain open.

## Literature-to-design mapping

| Design decision | Primary grounding | Boundary |
|---|---|---|
| Routine anticipation across the lifecycle; concrete cases and perspectives | Do et al., CHI 2023, DOI 10.1145/3544548.3581347 | The paper does not define SafeBARS’s nine lenses or validate an ethics score. |
| Early reflection linked to mitigation commitments | Bernstein et al., PNAS 2021, DOI 10.1073/pnas.2117261118 | ESR is not institutional ethics approval. |
| Commitment–behaviour discrepancy | Priolo et al., PSPB 2019, DOI 10.1177/0146167219841621 | The interface must not shame, deceive, diagnose, or claim guaranteed behaviour change. |
| Stakeholder, time, value, and pervasiveness prompts | Friedman & Hendry, CHI 2012, DOI 10.1145/2207676.2208562 | Scenarios support imagination, not prediction. |
| Recurring AI-ethics principles | Jobin et al., Nature Machine Intelligence 2019, DOI 10.1038/s42256-019-0088-2 | Principle mentions alone are not actionable evidence. |
| Limits of LLM-generated personas | Salminen et al., CHI 2024, DOI 10.1145/3613904.3642036 | Synthetic roles are not testimony or participation. |

The nine lenses are an explicit SafeBARS design synthesis. Each lens exposes its
operational definition, sources, and interpretation boundary in the interface.

## Privacy decision: no demographic camera inference

SafeBARS does not estimate a researcher’s age, race or ethnicity, gender,
disability, family status, or other sensitive characteristic from a camera.
Those attributes are not needed to assess an AI-app research plan, and adding
the inference would introduce bias, privacy, validity, and review risks. The
researcher may optionally self-describe perspective context. Sensitive
attributes are discussed only when the proposed research design itself intends
to collect or infer them.

## Candidate experiment

### Participants and task

Recruit computer-science students or early-career researchers who are actively
developing an AI-app research idea. Use two matched, counterbalanced conditions:

- SafeBARS Ethical Mirror; and
- a general-purpose LLM chat using the same underlying model and time budget.

Participants revise a structured initial research plan in each condition. Use
counterbalanced matched cases for the main comparison; optionally include the
participant’s own idea after the controlled task as an ecological follow-up.

### Primary outcome

A blinded expert-rated **consequence-to-change quality** measure composed of:

1. breadth of materially affected positions;
2. causal specificity of unintended-consequence reasoning;
3. specificity and feasibility of consequential design revisions; and
4. traceability from a revision to plan evidence and an articulated concern.

The rubric and aggregation rule must be frozen before data collection.

### Secondary outcomes

- number and type of substantive design changes;
- proportion of concerns accepted, contested with evidence, or handed off;
- unresolved questions correctly kept open for real people or experts;
- perceived insight, autonomy, reactance, workload, and trust calibration; and
- interaction traces through commitments, scenarios, graph selections,
  responses, and replay.

### Qualitative analysis

Use stimulated-recall interviews with the participant’s own map and change
ledger. Analyse when the mirror produced genuine reframing, superficial
compliance, defensiveness, useful contestation, or recognition that synthetic
roles could not answer the question.

## Claim boundary

The implemented system and its deterministic tests demonstrate technical
functionality only. They are not evidence that cognitive dissonance occurred,
that researchers became more ethical, that harms were prevented, or that the
intervention outperforms general chat. Those claims require the approved human
study and blinded analysis.
