# SafeBARS Quantitative Figure Package

Date: 26 July 2026

## Decision

SafeBARS now has a reproducible technical-evidence figure package in
`research/chi2027/figures/`. It is designed to support the paper's technical
evaluation without presenting seeded cases or development telemetry as human
research evidence.

The current controlling research plan is
`CURRENT_CANONICAL_PLAN.md`, supported by files 86-90. Both
`83_supervisor_feedback_ai_ethics_and_study_plan.md` and the older
`40_figure_plan_v0.md` are retained provenance and should not control the final
study or CHI figure sequence.

## Figures available now

1. **Submitted-evidence coverage matrix** — 21 fictional cases × 11 possible
   framework dimensions, with pathway-specific not-applicable cells and the
   author-planted omission marked.
2. **Passage-grounded evidence figure** — 21 cases, 67 passages, 159 dimension
   assessments, 79/79 evidence-linked non-missing outputs, and 80 explicit
   missing-evidence outputs; includes pathway-normalized raw counts.
3. **Seeded corpus composition** — domain × pathway balance, adaptive review
   load, and planted/detected omission taxonomy.
4. **Specification-conformance appendix matrix** — 21 cases × 6 checks,
   totalling 126/126 passing assertions.

Each figure is stored as PNG, SVG, and PDF. The generator exports tidy CSV and a
manifest so every plotted number can be inspected.

## Figures that must wait for real data

### RQ1: SafeBARS versus general LLM chat

Use participant-level paired estimation plots for:

- application completeness;
- safeguard specificity;
- evidence traceability;
- revision actionability;
- appropriate uncertainty and handoff quality;
- unsupported normative or compliance claims;
- task time; and
- workload.

Show individual paired observations and effect sizes with confidence intervals.
Do not use a leaderboard or simple mean-only bar chart.

### RQ2–RQ3: contestation and expert work

After genuine expert review, visualize:

- accept, edit, reject, and defer decisions;
- correctly routed and sufficiently evidenced handoffs;
- clarification requests;
- expert triage time;
- linked researcher revisions; and
- provenance confidence.

Do not plot the current local database as study data. Its sessions and expert
actions are development/demo records without participant consent, experimental
conditions, independent ratings, or verified expert identity.

## Reproduction

```powershell
python scripts/generate_safebars_paper_figures.py
```

The script fails if the core totals become internally inconsistent. Regenerate
and freeze the figure package at the paper's final analysis commit.
