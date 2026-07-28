# SafeBARS Reproducible Paper Figure Package

Status: technical-evidence figures generated from commit `3297298` and later.

These figures follow the evidence structure used by projects such as
Fraud-R1 and CoBRA—explicit cases, measurable checks, inspectable provenance,
and machine-readable outputs—without borrowing their metrics or claiming human
validation that SafeBARS has not yet conducted.

## Generate the package

From the repository root:

```powershell
python -m pip install -r research/chi2027/figures/requirements.txt
python scripts/generate_safebars_paper_figures.py
```

The generator reads the current production evaluator rather than the ignored,
outdated `tests/evaluation/results.json` snapshot. It writes:

- 300-dpi PNG for Word, slides, and quick review;
- SVG and PDF for vector-quality paper submission;
- tidy long-form CSV files;
- a JSON manifest with the source commit, input hashes, counts, and boundary;
- header-only schemas for the future comparative user study.

The plotting environment requires `matplotlib`, `numpy`, and `pandas`. These are
research-only dependencies and are intentionally not added to the web
application's production requirements.

## Current figures

### `fig01_submitted_evidence_coverage`

**Recommended paper location:** Technical evaluation or system validation.

**Caption:**

> **Submitted-evidence coverage on fictional seeded protocols.** Each row is
> one fictional protocol and each column is a framework dimension activated by
> its human-subjects, ICT, or AI-enabled review pathway. A black outline marks
> the dimension deliberately omitted by the case author. Coverage indicates
> whether relevant submitted material was located; it is not an ethics score,
> error rate, or approval prediction.

### `fig02_passage_grounded_evidence`

**Recommended paper location:** Technical evaluation; supports the provenance
mechanism described in the system section.

**Caption:**

> **Passage-grounded framework assessment on the seeded protocol suite.**
> SafeBARS produced 159 dimension-level assessments from 67 submitted passages.
> All 79 documented or partial assessments cited at least one submitted
> passage, while 80 dimensions were explicitly marked missing. Bars are
> normalized within pathway and annotated with raw counts. Pathways activate
> different review dimensions, so these distributions are not comparative
> accuracy scores.

### `fig03_seeded_corpus_composition`

**Recommended paper location:** Technical-evaluation method or appendix.

**Caption:**

> **Composition of the seeded SafeBARS technical-evaluation corpus.**
> Twenty-one fictional protocols are balanced across academic HCI,
> qualitative/social research, and applied UX/service research, and span
> human-subjects, ICT, and AI-enabled review pathways. Each case contains one
> deliberately omitted framework dimension. Counts reflect the authored test
> design rather than real-world prevalence or cross-domain generalization.

### `figA1_specification_conformance`

**Recommended paper location:** Appendix.

**Caption:**

> **Deterministic specification-conformance results for the SafeBARS seeded
> protocol suite.** Each row represents one fictional protocol and each column
> one executable check. All 126 assertions passed across 21 cases in three
> research domains. Cases were authored to test known routing, provenance, and
> omission-handling requirements; therefore, these results establish software
> conformance, not ethical correctness or real-world effectiveness.

## What these figures support

The current figure package supports only the following bounded statements:

- the implementation routes the authored cases through the expected pathway;
- the intended framework set is activated;
- non-missing outputs in this suite link back to submitted passages;
- deliberately planted missing dimensions are surfaced;
- repeated deterministic runs return the same structured result.

It does **not** support claims that SafeBARS:

- makes ethically correct recommendations;
- finds every important issue in real research protocols;
- improves researcher outcomes compared with general LLM chat;
- reduces expert workload;
- produces institutionally acceptable applications; or
- has been validated by ethics experts.

Those claims require independent held-out protocols, blinded expert ratings,
and the planned SafeBARS-versus-same-model-chat comparative study.

## Data files

`data/` contains:

- `technical_runs.csv`: frozen run metadata and source hashes;
- `technical_cases.csv`: one row per fictional protocol;
- `technical_checks.csv`: 126 case-check observations;
- `technical_dimensions.csv`: 159 dimension-level assessments;
- `technical_passages.csv`: 67 hashed source-passage records;
- `technical_frameworks.csv`: activated framework records;
- `technical_omissions.csv`: planted-versus-detected omission counts;
- `technical_pathways.csv`: pathway coverage summaries;
- `technical_lineage.csv`: count-and-unit cards used in the lineage figure;
- `manifest.json`: source commit, aggregate counts, and interpretation boundary.

`study_data_templates/` contains header-only schemas. Empty files are
intentional: no participant or expert result is fabricated before the study.

## Primary visual precedents

- Fraud-R1: [official repository](https://github.com/kaustpradalab/Fraud-R1)
  and [ACL 2025 paper](https://aclanthology.org/2025.findings-acl.226/).
- CoBRA: [official repository](https://github.com/AISmithLab/CoBRA) and
  [paper figures](https://arxiv.org/html/2509.13588v3).

SafeBARS borrows the evidence pattern—cases, comparisons, uncertainty, and
reproducible artifacts—not Fraud-R1's DSR metric or CoBRA's CBI metric.
