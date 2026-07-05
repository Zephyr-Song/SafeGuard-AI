# SafeBARS

SafeBARS is an agentic ethics-preparation workspace for sensitive human-facing research. It helps researchers scaffold protocol materials, stress-test pre-fieldwork encounters, expose unresolved value tensions, and hand questions that require authority or situated knowledge to real experts.

SafeBARS does **not** issue ethics approval, compliance decisions, or predictions about participant behaviour.

## Current MVP

The application supports three parties:

- **Researcher:** completes guided intake, inspects framework coverage, runs bounded audits, decides on issues, responds to experts, and exports drafts.
- **AI agents:** create a material-dependent task plan, trace breakdown scenarios, preserve provenance, stop at epistemic boundaries, and recommend a reviewer role.
- **Ethics or domain expert:** reviews prioritized handoffs, requests clarification, redirects, advises, resolves, or reopens issues.

Key features:

- six-question guided intake that populates structured protocol fields, with one conditional AI-governance follow-up;
- Belmont baseline with conditional Menlo and NIST AI RMF extensions;
- Value Sensitive Design-informed trade-off exploration;
- Ethics Dandelion evidence visualization and a connected Trade-off Dandelion comparing parameter lean, linked framework dimensions, framework family, and evidence coverage;
- inspectable agent plans, sources, tools, dependencies, and stopping rules;
- researcher/expert capability tokens with separate API permissions;
- rotatable expert invitations and browser-local expert caseload;
- expert-advice-to-researcher-revision linkage;
- immutable human review history through protocol versioning;
- generic human-research and AI-enabled application profiles;
- field-level draft completeness checks;
- JSON, Word, PDF, ethics-application, research-design, per-case expert-summary, and expert-caseload exports.

## Export types

- **Application draft (.docx):** submission-oriented sections, completeness gaps, researcher revisions, and unresolved expert questions. Transfer this material into the institution's current official form.
- **Research design (.docx):** researcher-facing methods and fieldwork plan covering participants, recruitment, procedures, consent, safeguards, data, AI oversight, trade-offs, expert dependencies, and next actions.
- **Full audit report (.docx/.pdf):** internal evidence record containing framework mapping, encounter stages, scenario traces, issue ledger, sources, agent plan, handoffs, and event history. Use it for supervision, team review, or research evaluation rather than as the application form itself.
- **Expert review summary / caseload summary (.docx):** one-protocol review record or a cross-application summary of accessible ethics drafts, gaps, priorities, advice, researcher responses, and linked revisions.

Saved trade-off positions and researcher rationales flow into the research-design document and the expert caseload summary. The visualization uses the synthesized-data principle of An et al.'s CHI EA 2020 Dandelion Diagram while explicitly adapting it from classroom position/orientation data to connected ethics-design parameters.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5050/safebars](http://127.0.0.1:5050/safebars).

Important routes:

- `/safebars` - researcher workspace;
- `/safebars/expert` - browser-local expert caseload;
- `/safebars/expert/<session_id>` - one invited expert review;
- `/safebars/brief` - supervisor-facing concept brief;
- `/safebars/v1` - preserved earlier rehearsal interface;
- `/healthz` - deployment health check.

## Configuration

Copy `.env.example` to `.env` and set only the providers you intend to use. Local secret files are ignored by Git.

Security-related settings:

```dotenv
SAFEBARS_REQUIRE_ROLE_AUTH=1
ENABLE_DEMO_AUTH=0
FLASK_SECRET_KEY=replace_with_a_long_random_value
```

`SAFEBARS_REQUIRE_ROLE_AUTH=1` protects each v2 session with separate researcher and expert capability tokens. Optional outer HTTP Basic Auth can be enabled for a closed demonstration with `ENABLE_DEMO_AUTH=1`, `SAFEBARS_DEMO_USER`, and `SAFEBARS_DEMO_PASSWORD`.

## Validation

```bash
python -m unittest discover -s tests -v
```

The automated suite covers the audit engine, ethics-framework routing, application profiles, report exports, role authorization, expert invitation rotation, revision linkage, and protocol versioning.

## Deployment boundary

`render.yaml` configures a single-worker Render demonstration. The free plan uses ephemeral local storage, so SQLite sessions and invitation tokens can disappear after a restart or redeploy. Use a persistent database and institution-managed identity before handling real or confidential ethics applications.

See [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for deployment steps and [research/chi2027/79_role_collaboration_and_application_adapter.md](research/chi2027/79_role_collaboration_and_application_adapter.md) for the current research and implementation boundary.

## Framework sources

- The Belmont Report: respect for persons, beneficence, and justice.
- The Menlo Report Companion: ICT and data-research extension.
- NIST AI Risk Management Framework 1.0: Govern, Map, Measure, and Manage.
- Value Sensitive Design: stakeholder and value-tension investigation.
- Ethics and Society Review: interdisciplinary expert review and iteration.

Frameworks inform prompts and mappings; they do not turn SafeBARS into an approving authority.
