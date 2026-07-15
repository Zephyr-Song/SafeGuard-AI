# SafeBARS

> **Agentic ethics-preparation workspace for sensitive human-facing research.**

SafeBARS helps researchers scaffold protocol materials, stress-test pre-fieldwork
encounters, expose unresolved value tensions, and hand questions that require
authority or situated knowledge to real experts.

**SafeBARS does _not_ issue ethics approval, compliance decisions, or predictions
about participant behaviour.** Every AI output is a *planning hypothesis*, not
evidence, an approval, or a substitute for community or reviewer judgment.

---

## Table of contents

- [What it is](#what-it-is)
- [Research context](#research-context)
- [System architecture](#system-architecture)
- [Three parties](#three-parties)
- [Key features](#key-features)
- [API summary](#api-summary)
- [Export types](#export-types)
- [Run locally](#run-locally)
- [Configuration & security](#configuration--security)
- [Validation](#validation)
- [Deployment boundary](#deployment-boundary)
- [Framework sources](#framework-sources)
- [How to cite](#how-to-cite)
- [License & status](#license--status)

---

## What it is

Sensitive research (trauma, violence, addiction, marginalised communities) faces
ethical challenges that static IRB review struggles to catch: power asymmetries,
inadequate consent, privacy leakage, and harm that only emerges in the field.
SafeBARS models the research protocol as a sequence of *encounters* and uses a
bounded multi-agent system to rehearse where those encounters can break down —
before real fieldwork begins.

## Research context

SafeBARS is developed as a research prototype for the CHI 2027 submission
*“SafeBARS: A Three-Way Collaborative Platform for AI-Assisted Research Ethics
Review”*. The design contributions are:

1. **Encounter stress-testing** — treating a protocol as inspectable encounter
   maps that can be traced for breakdowns.
2. **Bounded multi-agent audit** — orchestrator, breakdown-scenario,
   relationship-and-power, and boundary-and-handoff types that stop at their
   epistemic limits instead of fabricating judgements.
3. **Framework-driven scaffolding** — Belmont / Menlo / NIST AI RMF / VSD / ESR
   coverage checks that shape what the system asks for, never what it decides.
4. **Human-in-the-loop handoff** — unresolved situated questions are routed to
   real experts with provenance and version history.

The project knowledge base (design rationale, related work, study protocol) is
maintained separately in Notion.

## System architecture

```
                 ┌─────────────────────────────────────────────┐
   Browser  ───▶ │  Flask app (app.py)                          │
                 │   • /safebars        researcher workspace    │
                 │   • /safebars/expert expert caseload         │
                 │   • /safebars/v1     rehearsal prototype      │
                 │   • security headers, 404/500, rate limiting │
                 └───────────────┬─────────────────────────────┘
                                 │  /api/safebars/v2/*  (Blueprint)
                 ┌───────────────▼─────────────────────────────┐
                 │  modules/encounter_api.py  (role-gated REST) │
                 └───┬───────────────┬───────────────┬─────────┘
                     │               │               │
            ┌────────▼──────┐ ┌──────▼────────┐ ┌────▼──────────────┐
            │ encounter_    │ │ encounter_    │ │ ethics_framework / │
            │ engine.py     │ │ store.py      │ │ ethics_application │
            │ (audit logic) │ │ (SQLite JSON) │ │ (coverage checks)  │
            └────────┬──────┘ └───────────────┘ └───────────────────┘
                     │ bounded LLM calls
            ┌────────▼──────────────────────────────────────────┐
            │ modules/llm_client.py — unified client for         │
            │ GLM-4 · Qwen-Plus · Hunyuan · DeepSeek · OpenAI     │
            └───────────────────────────────────────────────────┘
                 │ renders
            ┌────▼─────────────────────────────────────────────┐
            │ modules/encounter_report.py — Word/PDF generation │
            └───────────────────────────────────────────────────┘
```

| Module | Responsibility |
|--------|----------------|
| `app.py` | Flask entry point, page routes, security middleware, rate limiting |
| `config.py` | Provider and feature configuration |
| `modules/llm_client.py` | Provider-agnostic LLM client (5 providers) with structured error reporting |
| `modules/encounter_engine.py` | Core bounded encounter-audit workflow |
| `modules/encounter_store.py` | SQLite persistence, event log, HMAC access tokens |
| `modules/scenarios.py` | Scenario library, encounter-stage definitions, sample data |
| `modules/encounter_api.py` | Role-gated v2 REST API (Blueprint) |
| `modules/encounter_report.py` | Word/PDF report generation |
| `modules/ethics_framework.py` | Belmont/Menlo/NIST/VSD/ESR coverage + expert routing |
| `modules/ethics_application.py` | Application-profile completeness checks |
| `modules/ratelimit.py` | In-memory rate limiting for LLM-backed endpoints |
| `templates/` | `safebars_v2.html`, `safebars_expert.html`, `safebars.html`, … |

## Three parties

- **Researcher:** completes guided intake, inspects framework coverage, runs
  bounded audits, decides on issues, responds to experts, and exports drafts.
- **AI agents:** create a material-dependent task plan, trace breakdown
  scenarios, preserve provenance, stop at epistemic boundaries, and recommend a
  reviewer role.
- **Ethics or domain expert:** reviews prioritized handoffs, requests
  clarification, redirects, advises, resolves, or reopens issues.

## Key features

- six-question guided intake that populates structured protocol fields, with one
  conditional AI-governance follow-up;
- Belmont baseline with conditional Menlo and NIST AI RMF extensions;
- Value Sensitive Design-informed trade-off exploration;
- Ethics Dandelion evidence visualization and a connected Trade-off Dandelion
  comparing parameter lean, linked framework dimensions, framework family, and
  evidence coverage;
- inspectable agent plans, sources, tools, dependencies, and stopping rules;
- researcher/expert capability tokens with separate API permissions;
- rotatable expert invitations and browser-local expert caseload;
- expert-advice-to-researcher-revision linkage;
- immutable human review history through protocol versioning;
- generic human-research and AI-enabled application profiles;
- field-level draft completeness checks;
- JSON, Word, PDF, ethics-application, research-design, per-case
  expert-summary, and expert-caseload exports.

## API summary

All v2 endpoints live under `/api/safebars/v2/` and require a per-session role
token (`X-SafeBARS-Access` header).

| Method | Path | Role | Purpose |
|--------|------|------|---------|
| GET | `/options` | — | Scenarios, frameworks, providers |
| POST | `/sessions` | researcher | Create session + encounter map |
| GET | `/sessions/<id>` | researcher | Fetch session |
| PATCH | `/sessions/<id>/map` | researcher | Save encounter scope |
| POST | `/sessions/<id>/audit` | researcher | Run bounded audit |
| POST | `/sessions/<id>/tasks/<tid>/rerun` | researcher | Re-run one check |
| POST | `/sessions/<id>/issues/<iid>/decision` | researcher | Record decision |
| PATCH | `/sessions/<id>/tradeoffs` | researcher | Save trade-off positions |
| POST | `/sessions/<id>/access/rotate-expert` | researcher | Rotate expert token |
| POST | `/sessions/<id>/handoffs/<hid>/review` | expert | Advise / redirect / resolve |
| GET | `/sessions/<id>/export*` | researcher | JSON / DOCX / PDF exports |

Legacy rehearsal endpoints (`/api/safebars/*`) back the v1 interface.

## Export types

- **Application draft (.docx):** submission-oriented sections, completeness
  gaps, researcher revisions, and unresolved expert questions. Transfer this
  material into the institution's current official form.
- **Research design (.docx):** researcher-facing methods and fieldwork plan
  covering participants, recruitment, procedures, consent, safeguards, data, AI
  oversight, trade-offs, expert dependencies, and next actions.
- **Full audit report (.docx/.pdf):** internal evidence record containing
  framework mapping, encounter stages, scenario traces, issue ledger, sources,
  agent plan, handoffs, and event history. Use it for supervision, team review,
  or research evaluation rather than as the application form itself.
- **Expert review summary / caseload summary (.docx):** one-protocol review
  record or a cross-application summary of accessible ethics drafts, gaps,
  priorities, advice, researcher responses, and linked revisions.

Saved trade-off positions and researcher rationales flow into the research-design
document and the expert caseload summary. The visualization uses the
synthesized-data principle of An et al.'s CHI EA 2020 Dandelion Diagram while
explicitly adapting it from classroom position/orientation data to connected
ethics-design parameters.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate   # or: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000/safebars>.

Important routes:

- `/safebars` — researcher workspace;
- `/safebars/expert` — browser-local expert caseload;
- `/safebars/expert/<session_id>` — one invited expert review;
- `/safebars/brief` — supervisor-facing concept brief;
- `/safebars/v1` — preserved earlier rehearsal interface;
- `/healthz` — deployment health check.

> **Note:** `debug=True` is gated behind `FLASK_DEBUG=1` and is **off by
> default**. Never enable it in a shared or production deployment.

## Configuration & security

Copy `.env.example` to `.env` and set only the providers you intend to use.
Local secret files are ignored by Git.

Security-related settings:

```dotenv
SAFEBARS_REQUIRE_ROLE_AUTH=1
ENABLE_DEMO_AUTH=0
FLASK_SECRET_KEY=replace_with_a_long_random_value
FLASK_DEBUG=0
```

- `SAFEBARS_REQUIRE_ROLE_AUTH=1` protects each v2 session with separate
  researcher and expert capability tokens (HMAC-verified, constant-time compare).
- Optional outer HTTP Basic Auth can be enabled for a closed demonstration with
  `ENABLE_DEMO_AUTH=1`, `SAFEBARS_DEMO_USER`, and `SAFEBARS_DEMO_PASSWORD`.
- Production responses carry `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Content-Security-Policy`, and (in production) HSTS.

## Validation

```bash
pytest tests/ -v
```

The suite runs offline (the engine falls back to deterministic responses when no
LLM provider is configured) and covers the audit engine, ethics-framework
routing, application profiles, report exports, role authorization, expert
invitation rotation, revision linkage, and protocol versioning. A GitHub Actions
workflow runs the suite on every push and pull request.

## Deployment boundary

`render.yaml` configures a single-worker Render demonstration. The free plan uses
ephemeral local storage, so SQLite sessions and invitation tokens can disappear
after a restart or redeploy. Use a persistent database and institution-managed
identity before handling real or confidential ethics applications.

See [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for deployment steps and
[research/chi2027/](research/chi2027/) for the current research and
implementation boundary.

## Framework sources

- The Belmont Report: respect for persons, beneficence, and justice.
- The Menlo Report Companion: ICT and data-research extension.
- NIST AI Risk Management Framework 1.0: Govern, Map, Measure, and Manage.
- Value Sensitive Design: stakeholder and value-tension investigation.
- Ethics and Society Review: interdisciplinary expert review and iteration.

Frameworks inform prompts and mappings; they do not turn SafeBARS into an
approving authority.

## How to cite

```bibtex
@misc{song2026safebars,
  title        = {SafeBARS: A Three-Way Collaborative Platform for AI-Assisted Research Ethics Review},
  author       = {Song, Jincheng},
  year         = {2026},
  note         = {CHI 2027 submission (under review). SafeBARS is an agentic ethics-preparation workspace for sensitive human-facing research.},
  howpublished = {\url{https://github.com/Zephyr-Song/SafeGuard-AI}}
}
```

## License & status

This repository is a research prototype. Code is provided for review and
reproducibility of the associated study; check the repository license file
before redistribution. The system is **not** a certified ethics-review tool.
