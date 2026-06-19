# Paper Pattern Extraction for SafeBARS

Last updated: 2026-06-19

Purpose: extract reusable CHI paper patterns from the most relevant papers. This file is meant to support writing, study design, and supervisor discussion.

## Extraction Table

| Paper | Problem framing | Contribution structure | Study / evidence pattern | What SafeBARS should imitate | What SafeBARS should avoid |
|---|---|---|---|---|---|
| CoBRA: Programming Cognitive Bias in Social Agents Using Classic Social Science Experiments | Persona prompts are implicit and inconsistent for controlling LLM social agents. | Toolkit plus measurement/regulation primitives for controllable agent behavior. | Technical evaluation around bias measurement and regulation across models. | Use explicit bias/risk-response profiles instead of vague personas. Show workflow primitives clearly. | Do not frame SafeBARS as a benchmark or claim psychometric validity for sliders. |
| Simulacrum of Stories | LLM-generated participants can appear plausible but create ethical and epistemological problems. | Interview study plus conceptual critique of LLMs as qualitative participant proxies. | Interviews with qualitative researchers; findings around consent, agency, contextual depth, and legitimacy. | Make the non-replacement boundary central. Study researchers, not simulated "accuracy." | Do not claim synthetic stakeholders produce data about real vulnerable groups. |
| Large Language Models in Qualitative Research | Researchers are already using LLMs, but norms, intentions, and ethical boundaries are unclear. | Empirical account of uses/tensions plus design principles for LLM-assisted research tools. | Interviews with qualitative researchers across research stages. | Frame SafeBARS as intentional tooling that constrains LLM use toward ethical reflection. | Do not present LLM use as generic productivity improvement. |
| AI-Driven Co-Construction of Synthetic Personas | Early-stage user research often needs lightweight ways to reason about possible users. | Synthetic persona co-construction system and exploratory study. | Prototype-based user-research workflow study. | Position SafeBARS against synthetic-persona ideation tools by emphasizing safety rehearsal. | Do not let reviewers think SafeBARS is just "personas with chat." |
| Human-AI Collaboration in Thematic Analysis using ChatGPT | Generative AI may help qualitative analysis, but researchers need trustworthy collaboration patterns. | User study plus design recommendations for human-AI collaboration. | User study with 10 qualitative researchers performing thematic analysis. | Use task-based evaluation with researcher artifacts before and after tool use. | Do not evaluate only self-reported usefulness. Capture artifacts. |
| Auntie, Please Don't Fall for Those Smooth Talkers | Senior-targeted online fraud is socially and relationally mediated, not just an individual literacy problem. | Thematic analysis of social media data plus taxonomy and conceptual framework. | Inductive thematic analysis of RedNote posts/comments. | Use ecosystem framing: older adults, family helpers, community workers, institutions. | Do not reduce older adults to passive victims or deficit narratives. |
| ROLESafe | Static anti-fraud instruction limits engagement and transfer; role-based simulation may help older adults practice. | Role-based intervention plus between-subjects experiment. | 144 older adults in China; roles include Experiencer, Helper, Observer. | Borrow the idea that roles matter, but apply roles to research rehearsal rather than end-user training. | Do not position SafeBARS as anti-fraud education for older adults. |
| Hear Us, then Protect Us | Older adults need safeguards against deepfake scams that respect autonomy and lived concerns. | Participatory design around scam interventions. | Participatory work with older adults. | Use autonomy, dignity, and participatory caution as domain grounding. | Do not design paternalistic safety scripts. |

## Reusable Problem Sentences

### CoBRA-like sentence

Existing LLM role-play systems often rely on natural-language personas, but such descriptions provide weak control over the behavioral tendencies that matter in sensitive research rehearsal.

### Simulacrum-like sentence

Although LLM-generated stakeholders may produce plausible narratives, treating those narratives as participant evidence risks bypassing consent, agency, and situated lived experience.

### Qualitative-research-tool sentence

Researchers increasingly encounter LLMs across research workflows, yet existing tools provide limited support for intentional, bounded, and ethically calibrated use before fieldwork.

### Domain sentence

Online fraud prevention with older adults is a useful test context because research plans may trigger privacy concerns, shame, family tension, distrust, and distress.

## Reusable Contribution Pattern

SafeBARS can use a four-part contribution structure:

1. **Design framing:** synthetic stakeholders as pre-fieldwork rehearsal aids, not participant replacements.
2. **System:** a working prototype with risk-response profiles, rehearsal chat, provider comparison, reflection reporting, and revised-plan capture.
3. **Formative evidence:** a study of how researchers use SafeBARS to identify risks and revise sensitive research plans.
4. **Design implications:** guidance for building bounded synthetic-stakeholder tools for sensitive HCI research.

## Study Design Pattern to Copy

The strongest feasible study pattern is:

1. Give participants a flawed sensitive research plan.
2. Ask them to revise it once without SafeBARS or document their initial concerns.
3. Let them use SafeBARS to rehearse the plan.
4. Ask them to revise the plan again.
5. Interview them about usefulness, limits, overtrust, and what they would still verify with real stakeholders.
6. Analyze pre/post artifacts and interview transcripts.

This combines the artifact-based strength of AI-tool studies with the ethical caution of qualitative-research critique papers.

## What Reviewers Will Ask

### Is this replacing participants?

Answer:

No. The unit of analysis is researcher reflection and plan revision, not synthetic stakeholder realism. SafeBARS outputs planning prompts and risk signals, not empirical claims about communities.

### Why use LLMs at all?

Answer:

Because sensitive fieldwork planning benefits from interactive rehearsal. LLMs can create friction, objections, and alternative stakeholder perspectives quickly, but the system must keep those outputs bounded and inspectable.

### Why online fraud?

Answer:

Online fraud prevention is socially important and methodologically sensitive. It exposes concrete risks around privacy, shame, institutional distrust, family support, and victim-blaming.

### What is original?

Answer:

Prior work studies controllable agents, synthetic participants, AI-assisted qualitative research, and fraud interventions separately. SafeBARS combines these into a bounded pre-fieldwork rehearsal workflow for researchers.

## Writing Moves to Reuse

### Introduction move

Start with the risk of poorly prepared sensitive fieldwork, not with the technology. Then introduce LLM role-play as a tempting but dangerous shortcut. Finally position SafeBARS as a bounded alternative.

### Related work move

Do not organize related work as "LLMs, fraud, HCI." Organize by tension:

1. controllable agents make rehearsal possible;
2. synthetic participants make replacement dangerous;
3. participatory/action research makes preparation necessary;
4. fraud research makes the context sensitive;
5. trust calibration makes the interface design problem.

### Methods move

Treat participants as researchers/designers evaluating a research-preparation workflow. Their revised plans are the key artifacts.

### Discussion move

Discuss productive discomfort: the value is not that the synthetic stakeholder is correct, but that it forces the researcher to notice a fragile assumption.

## Source Notes

- CoBRA arXiv page states that CoBRA addresses inconsistent behavior from implicit natural-language descriptions and introduces bias measurement/regulation primitives: https://arxiv.org/abs/2509.13588
- Simulacrum of Stories reports interviews with 19 qualitative researchers and argues against LLMs as participant proxies: https://arxiv.org/abs/2409.19430
- Large Language Models in Qualitative Research reports interviews with 20 qualitative researchers about uses, tensions, and intentions: https://arxiv.org/abs/2410.07362
- Auntie paper analyzes RedNote posts/comments and develops a family-support ecosystem framing for senior-targeted online fraud: https://arxiv.org/abs/2501.10803
- ROLESafe reports a role-based anti-fraud intervention study with 144 older adults: https://arxiv.org/abs/2601.12324

