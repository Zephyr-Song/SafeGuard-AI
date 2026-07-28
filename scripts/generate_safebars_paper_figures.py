"""Generate reproducible, paper-ready SafeBARS technical-evidence figures.

The inputs are the current production evaluator and its fictional seeded case
suite. The resulting figures demonstrate deterministic specification
conformance and submitted-evidence traceability. They do not demonstrate
ethical correctness, institutional approval, expert agreement, or user-study
benefit.

Usage:
    python scripts/generate_safebars_paper_figures.py
    python scripts/generate_safebars_paper_figures.py --output-dir PATH
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from modules.framework_selector import select_framework_path  # noqa: E402
from modules.technical_evidence import (  # noqa: E402
    CHECK_DEFINITIONS,
    build_public_evidence,
)
from modules.technical_evidence_cases import (  # noqa: E402
    case_to_project,
    get_seed_cases,
)


DEFAULT_OUTPUT = REPO / "research" / "chi2027" / "figures"
DATA_DIRNAME = "data"
FIGURE_PACKAGE_VERSION = "1.0"

COLORS = {
    "ink": "#172A2F",
    "muted": "#5E7076",
    "line": "#D6DFE2",
    "grid": "#E8EDEF",
    "paper": "#FFFFFF",
    "panel": "#F7F9F9",
    "green": "#267A5B",
    "green_light": "#D9EEE5",
    "amber": "#D99A2B",
    "amber_light": "#F7E8C6",
    "red": "#BE4D4D",
    "red_light": "#F3D8D8",
    "blue": "#326F9E",
    "blue_light": "#DCEAF4",
    "teal": "#148486",
    "grey": "#C9D2D5",
    "grey_light": "#EFF2F3",
    "purple": "#765A9B",
}

DOMAIN_LABELS = {
    "academic_hci": "Academic HCI",
    "qualitative_social": "Qualitative / social",
    "applied_ux_service": "Applied UX / service",
}

DOMAIN_COLORS = {
    "academic_hci": "#2D7F70",
    "qualitative_social": "#4D75A3",
    "applied_ux_service": "#9A6B42",
}

PATHWAY_LABELS = {
    "human_subjects": "Human-subjects",
    "ict_research": "ICT / Menlo",
    "ai_research": "AI-enabled",
}

PATHWAY_COLORS = {
    "human_subjects": "#6B8E62",
    "ict_research": "#3977A8",
    "ai_research": "#79589F",
}

DIMENSION_ORDER = [
    "respect",
    "beneficence",
    "justice",
    "law_public_interest",
    "value_tensions",
    "societal_review",
    "ai_govern",
    "ai_map",
    "ai_review_pathway",
    "ai_measure",
    "ai_manage",
]

DIMENSION_SHORT_LABELS = {
    "respect": "Respect",
    "beneficence": "Beneficence",
    "justice": "Justice",
    "law_public_interest": "Law &\npublic interest",
    "value_tensions": "Value\ntensions",
    "societal_review": "Societal\nreview",
    "ai_govern": "AI role &\ngovernance",
    "ai_map": "AI data &\npopulation",
    "ai_review_pathway": "AI review\npathway",
    "ai_measure": "AI\nmeasurement",
    "ai_manage": "AI risk\nmanagement",
}

COVERAGE_COLORS = {
    "not_applicable": COLORS["grey_light"],
    "missing": COLORS["red_light"],
    "partial": COLORS["amber_light"],
    "documented": COLORS["green_light"],
}

BOUNDARY_TEXT = (
    "Synthetic seeded technical validation; not a human study. "
    "Coverage is not an ethics score or institutional approval."
)


def configure_matplotlib() -> None:
    """Apply a compact, colorblind-conscious paper style."""
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 9,
            "axes.edgecolor": COLORS["line"],
            "axes.linewidth": 0.8,
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "text.color": COLORS["ink"],
            "figure.facecolor": COLORS["paper"],
            "axes.facecolor": COLORS["paper"],
            "savefig.facecolor": COLORS["paper"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def current_commit() -> str:
    """Return the current Git commit without changing repository config."""
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={REPO.as_posix()}",
                "rev-parse",
                "HEAD",
            ],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def file_sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def json_cell(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def build_tables() -> Dict[str, Any]:
    """Build evidence and tidy tables from the current production modules."""
    evidence = build_public_evidence()
    public_cases = {case["id"]: case for case in evidence["cases"]}
    source_cases = get_seed_cases()
    generated_at = utc_now()
    commit = current_commit()
    run_id = f"technical-{commit[:12] if commit != 'unknown' else generated_at[:10]}"

    case_rows: List[Dict[str, Any]] = []
    check_rows: List[Dict[str, Any]] = []
    dimension_rows: List[Dict[str, Any]] = []
    passage_rows: List[Dict[str, Any]] = []
    framework_rows: List[Dict[str, Any]] = []
    dimension_labels: Dict[str, str] = {}

    check_label_by_id = {
        definition["id"]: definition["label"] for definition in CHECK_DEFINITIONS
    }

    for case in source_cases:
        public = public_cases[case["id"]]
        selection = select_framework_path(
            case_to_project(case), passages=case.get("passages", [])
        )

        case_rows.append(
            {
                "run_id": run_id,
                "case_id": public["id"],
                "title": public["title"],
                "domain": public["domain"],
                "uses_ai": public["uses_ai"],
                "observed_pathway": public["pathway"],
                "expected_pathway": case["expected_pathway"],
                "passage_n": public["passage_count"],
                "dimension_n": public["dimension_assessments"],
                "framework_n": public["framework_count"],
                "documented_n": public["coverage_counts"]["documented"],
                "partial_n": public["coverage_counts"]["partial"],
                "missing_n": public["coverage_counts"]["missing"],
                "linked_nonmissing_n": public["linked_non_missing_outputs"],
                "seeded_omission_dimension": public[
                    "seeded_missing_dimension"
                ],
                "seeded_omission_detected": public[
                    "seeded_missing_detected"
                ],
                "checks_passed_n": public["checks_passed"],
                "checks_total_n": public["checks_total"],
                "case_passed": public["passed"],
            }
        )

        for definition in CHECK_DEFINITIONS:
            check_id = definition["id"]
            check = public["checks"][check_id]
            check_rows.append(
                {
                    "run_id": run_id,
                    "case_id": public["id"],
                    "domain": public["domain"],
                    "pathway": public["pathway"],
                    "check_id": check_id,
                    "check_label": check_label_by_id[check_id],
                    "observed_value_json": json_cell(check["observed"]),
                    "passed": bool(check["passed"]),
                }
            )

        for dimension in selection["dimensions"]:
            dimension_labels[dimension["id"]] = dimension["label"]
            source_count = len(dimension.get("source_passage_ids", []))
            dimension_rows.append(
                {
                    "run_id": run_id,
                    "case_id": public["id"],
                    "domain": public["domain"],
                    "pathway": public["pathway"],
                    "uses_ai": public["uses_ai"],
                    "dimension_id": dimension["id"],
                    "dimension_label": dimension["label"],
                    "framework_id": dimension["framework"],
                    "coverage": dimension["coverage"],
                    "evidence_count": dimension.get("evidence_count", 0),
                    "source_passage_count": source_count,
                    "related_passage_count": len(
                        dimension.get("related_passage_ids", [])
                    ),
                    "seeded_omission": (
                        dimension["id"] == public["seeded_missing_dimension"]
                    ),
                    "nonmissing_has_provenance": (
                        dimension["coverage"] == "missing" or source_count > 0
                    ),
                    "coverage_reason": dimension.get("coverage_reason", ""),
                }
            )

        for passage in case.get("passages", []):
            passage_rows.append(
                {
                    "run_id": run_id,
                    "case_id": public["id"],
                    "passage_id": passage["id"],
                    "artifact_type": passage["artifact_type"],
                    "text_sha256": hashlib.sha256(
                        passage["text"].encode("utf-8")
                    ).hexdigest(),
                    "character_n": len(passage["text"]),
                }
            )

        expected_frameworks = set(case["expected_frameworks"])
        for framework in selection["frameworks"]:
            framework_rows.append(
                {
                    "run_id": run_id,
                    "case_id": public["id"],
                    "pathway": public["pathway"],
                    "framework_id": framework["id"],
                    "framework_name": framework["name"],
                    "expected": framework["id"] in expected_frameworks,
                    "activated": True,
                }
            )

    cases_df = pd.DataFrame(case_rows)
    checks_df = pd.DataFrame(check_rows)
    dimensions_df = pd.DataFrame(dimension_rows)
    passages_df = pd.DataFrame(passage_rows)
    frameworks_df = pd.DataFrame(framework_rows)

    omission_df = (
        cases_df.groupby("seeded_omission_dimension", as_index=False)
        .agg(
            seeded_n=("case_id", "count"),
            detected_n=("seeded_omission_detected", "sum"),
        )
        .rename(columns={"seeded_omission_dimension": "dimension_id"})
    )
    omission_df["dimension_label"] = omission_df["dimension_id"].map(
        dimension_labels
    )
    omission_df["detection_rate"] = (
        omission_df["detected_n"] / omission_df["seeded_n"]
    )
    omission_df.insert(0, "run_id", run_id)

    pathway_df = (
        dimensions_df.groupby(["pathway", "coverage"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for status in ("documented", "partial", "missing"):
        if status not in pathway_df:
            pathway_df[status] = 0
    pathway_case_counts = cases_df.groupby("observed_pathway").size()
    pathway_framework_counts = (
        frameworks_df.groupby("pathway")["framework_id"].nunique()
    )
    pathway_dimension_counts = (
        dimensions_df.groupby("pathway").size()
        / dimensions_df.groupby("pathway")["case_id"].nunique()
    ).astype(int).to_dict()
    pathway_df["case_n"] = pathway_df["pathway"].map(pathway_case_counts)
    pathway_df["dimensions_per_case"] = pathway_df["pathway"].map(
        pathway_dimension_counts
    )
    pathway_df["frameworks_per_case"] = pathway_df["pathway"].map(
        pathway_framework_counts
    )
    pathway_df["assessment_n"] = pathway_df[
        ["documented", "partial", "missing"]
    ].sum(axis=1)
    pathway_df.insert(0, "run_id", run_id)

    aggregate = evidence["aggregate"]
    lineage_df = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "stage_order": 1,
                "stage": "fictional_seeded_cases",
                "count": aggregate["total_cases"],
                "unit": "cases",
                "note": "Author-designed technical protocols",
            },
            {
                "run_id": run_id,
                "stage_order": 2,
                "stage": "submitted_passages",
                "count": aggregate["total_passages"],
                "unit": "passages",
                "note": "One passage can support multiple assessments",
            },
            {
                "run_id": run_id,
                "stage_order": 3,
                "stage": "framework_assessments",
                "count": aggregate["dimension_assessments"],
                "unit": "dimension assessments",
                "note": "Pathway-dependent review dimensions",
            },
            {
                "run_id": run_id,
                "stage_order": 4,
                "stage": "evidence_linked_nonmissing",
                "count": aggregate["linked_non_missing_outputs"],
                "unit": "assessments",
                "note": "Documented or partial, each with a passage reference",
            },
            {
                "run_id": run_id,
                "stage_order": 5,
                "stage": "missing_submitted_evidence",
                "count": aggregate["missing_outputs"],
                "unit": "assessments",
                "note": "Absence of submitted evidence, not proof of non-compliance",
            },
            {
                "run_id": run_id,
                "stage_order": 6,
                "stage": "planted_omissions_detected",
                "count": aggregate["detected_seeded_omissions"],
                "unit": "known planted omissions",
                "note": "Only these 21 missing dimensions are independent seeded positives",
            },
        ]
    )

    run_df = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "commit_sha": commit,
                "generated_at_utc": generated_at,
                "figure_package_version": FIGURE_PACKAGE_VERSION,
                "dataset_label": evidence["metadata"]["dataset_label"],
                "evidence_level": evidence["metadata"]["evidence_level"],
                "human_validated": False,
                "case_n": aggregate["total_cases"],
                "assertion_n": aggregate["assertions_total"],
                "boundary_statement": evidence["metadata"][
                    "boundary_statement"
                ],
                "evaluator_sha256": file_sha256(
                    REPO / "modules" / "technical_evidence.py"
                ),
                "case_corpus_sha256": file_sha256(
                    REPO / "modules" / "technical_evidence_cases.py"
                ),
            }
        ]
    )

    assert len(cases_df) == aggregate["total_cases"] == 21
    assert len(checks_df) == aggregate["assertions_total"] == 126
    assert checks_df["passed"].sum() == aggregate["assertions_passed"] == 126
    assert len(passages_df) == aggregate["total_passages"] == 67
    assert len(dimensions_df) == aggregate["dimension_assessments"] == 159
    assert (
        int((dimensions_df["coverage"] != "missing").sum())
        == aggregate["linked_non_missing_outputs"]
        == 79
    )
    assert dimensions_df.loc[
        dimensions_df["coverage"] != "missing", "nonmissing_has_provenance"
    ].all()
    assert int(cases_df["seeded_omission_detected"].sum()) == 21
    assert int(pathway_df["assessment_n"].sum()) == 159
    assert set(dimensions_df["coverage"]) <= {
        "documented",
        "partial",
        "missing",
    }

    return {
        "evidence": evidence,
        "commit": commit,
        "generated_at": generated_at,
        "run_id": run_id,
        "runs": run_df,
        "cases": cases_df,
        "checks": checks_df,
        "dimensions": dimensions_df,
        "passages": passages_df,
        "frameworks": frameworks_df,
        "omissions": omission_df,
        "pathways": pathway_df,
        "lineage": lineage_df,
    }


def write_tables(package: Dict[str, Any], output_dir: pathlib.Path) -> None:
    data_dir = output_dir / DATA_DIRNAME
    data_dir.mkdir(parents=True, exist_ok=True)
    table_names = (
        "runs",
        "cases",
        "checks",
        "dimensions",
        "passages",
        "frameworks",
        "omissions",
        "pathways",
        "lineage",
    )
    for table_name in table_names:
        package[table_name].to_csv(
            data_dir / f"technical_{table_name}.csv",
            index=False,
            encoding="utf-8",
        )

    manifest = {
        "run_id": package["run_id"],
        "commit_sha": package["commit"],
        "generated_at_utc": package["generated_at"],
        "figure_package_version": FIGURE_PACKAGE_VERSION,
        "boundary": BOUNDARY_TEXT,
        "source_modules": [
            "modules/technical_evidence.py",
            "modules/technical_evidence_cases.py",
            "modules/framework_selector.py",
        ],
        "counts": package["evidence"]["aggregate"],
        "figures": [
            "fig01_submitted_evidence_coverage",
            "fig02_passage_grounded_evidence",
            "fig03_seeded_corpus_composition",
            "figA1_specification_conformance",
        ],
    }
    (data_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_figure(
    fig: mpl.figure.Figure, output_dir: pathlib.Path, stem: str
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def add_figure_header(
    fig: mpl.figure.Figure, title: str, subtitle: str
) -> None:
    fig.text(
        0.035,
        0.973,
        title,
        ha="left",
        va="top",
        fontsize=15,
        fontweight="bold",
        color=COLORS["ink"],
    )
    fig.text(
        0.035,
        0.935,
        subtitle,
        ha="left",
        va="top",
        fontsize=9,
        color=COLORS["muted"],
    )


def add_figure_footer(
    fig: mpl.figure.Figure, commit: str, generated_at: str
) -> None:
    commit_label = commit[:12] if commit != "unknown" else "unknown"
    fig.text(
        0.035,
        0.014,
        f"{BOUNDARY_TEXT}  Source commit: {commit_label} · generated {generated_at[:10]}",
        ha="left",
        va="bottom",
        fontsize=6.7,
        color=COLORS["muted"],
    )


def plot_submitted_evidence_coverage(
    package: Dict[str, Any], output_dir: pathlib.Path
) -> None:
    """Figure 1: case-by-dimension submitted-evidence coverage."""
    cases_df = package["cases"].copy()
    dimensions_df = package["dimensions"].copy()
    case_order = cases_df["case_id"].tolist()

    coverage_value = {
        "not_applicable": -1,
        "missing": 0,
        "partial": 1,
        "documented": 2,
    }
    matrix = np.full((len(case_order), len(DIMENSION_ORDER)), -1, dtype=float)
    seeded_cells = []
    for row_idx, case_id in enumerate(case_order):
        subset = dimensions_df[dimensions_df["case_id"] == case_id]
        for _, row in subset.iterrows():
            if row["dimension_id"] not in DIMENSION_ORDER:
                continue
            col_idx = DIMENSION_ORDER.index(row["dimension_id"])
            matrix[row_idx, col_idx] = coverage_value[row["coverage"]]
            if bool(row["seeded_omission"]):
                seeded_cells.append((row_idx, col_idx))

    cmap = ListedColormap(
        [
            COVERAGE_COLORS["not_applicable"],
            COVERAGE_COLORS["missing"],
            COVERAGE_COLORS["partial"],
            COVERAGE_COLORS["documented"],
        ]
    )
    norm = BoundaryNorm([-1.5, -0.5, 0.5, 1.5, 2.5], cmap.N)

    fig = plt.figure(figsize=(11.4, 8.2))
    grid = fig.add_gridspec(
        1,
        2,
        width_ratios=[0.17, 0.83],
        left=0.035,
        right=0.98,
        top=0.77,
        bottom=0.10,
        wspace=0.015,
    )
    ax_meta = fig.add_subplot(grid[0, 0])
    ax = fig.add_subplot(grid[0, 1])

    add_figure_header(
        fig,
        "Submitted-evidence coverage on fictional seeded protocols",
        (
            "Each cell reports whether a pathway-activated framework dimension "
            "was documented, partial, or missing in submitted material."
        ),
    )

    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto", interpolation="none")
    ax.set_xticks(range(len(DIMENSION_ORDER)))
    ax.set_xticklabels(
        [DIMENSION_SHORT_LABELS[dimension] for dimension in DIMENSION_ORDER],
        rotation=-35,
        ha="right",
        va="bottom",
        rotation_mode="anchor",
        fontsize=8,
    )
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", pad=7, length=0)
    ax.set_yticks(range(len(case_order)))
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)

    for x in np.arange(-0.5, len(DIMENSION_ORDER), 1):
        ax.axvline(x, color=COLORS["paper"], linewidth=1.5)
    for y in np.arange(-0.5, len(case_order), 1):
        ax.axhline(y, color=COLORS["paper"], linewidth=1.5)
    for y in (6.5, 13.5):
        ax.axhline(y, color=COLORS["ink"], linewidth=1.2)

    for row_idx, col_idx in seeded_cells:
        ax.add_patch(
            Rectangle(
                (col_idx - 0.43, row_idx - 0.43),
                0.86,
                0.86,
                fill=False,
                edgecolor=COLORS["ink"],
                linewidth=1.5,
                joinstyle="round",
            )
        )
        ax.plot(
            col_idx + 0.28,
            row_idx - 0.28,
            marker="o",
            markersize=2.8,
            color=COLORS["ink"],
            clip_on=False,
        )

    ax_meta.set_xlim(0, 1)
    ax_meta.set_ylim(len(case_order) - 0.5, -0.5)
    ax_meta.axis("off")
    for row_idx, case_id in enumerate(case_order):
        row = cases_df[cases_df["case_id"] == case_id].iloc[0]
        domain_color = DOMAIN_COLORS[row["domain"]]
        pathway_color = PATHWAY_COLORS[row["observed_pathway"]]
        ax_meta.add_patch(
            Rectangle(
                (0.00, row_idx - 0.40),
                0.035,
                0.80,
                facecolor=domain_color,
                edgecolor="none",
            )
        )
        ax_meta.text(
            0.07,
            row_idx,
            case_id,
            va="center",
            ha="left",
            fontsize=7.8,
            fontweight="bold",
        )
        ax_meta.text(
            0.48,
            row_idx,
            PATHWAY_LABELS[row["observed_pathway"]],
            va="center",
            ha="left",
            fontsize=6.7,
            color=pathway_color,
        )
        if bool(row["uses_ai"]):
            ax_meta.text(
                0.98,
                row_idx,
                "AI",
                va="center",
                ha="right",
                fontsize=6.4,
                fontweight="bold",
                color=COLORS["purple"],
            )
    for y in (6.5, 13.5):
        ax_meta.plot([0, 1], [y, y], color=COLORS["ink"], linewidth=1.2)

    for start, end, domain in (
        (0, 6, "academic_hci"),
        (7, 13, "qualitative_social"),
        (14, 20, "applied_ux_service"),
    ):
        ax_meta.text(
            0.00,
            start - 0.54,
            DOMAIN_LABELS[domain].upper(),
            va="bottom",
            ha="left",
            fontsize=6.7,
            fontweight="bold",
            color=DOMAIN_COLORS[domain],
        )

    legend_elements = [
        Rectangle(
            (0, 0),
            1,
            1,
            facecolor=COVERAGE_COLORS["documented"],
            edgecolor=COLORS["green"],
            label="Documented",
        ),
        Rectangle(
            (0, 0),
            1,
            1,
            facecolor=COVERAGE_COLORS["partial"],
            edgecolor=COLORS["amber"],
            label="Partial",
        ),
        Rectangle(
            (0, 0),
            1,
            1,
            facecolor=COVERAGE_COLORS["missing"],
            edgecolor=COLORS["red"],
            label="Missing",
        ),
        Rectangle(
            (0, 0),
            1,
            1,
            facecolor=COVERAGE_COLORS["not_applicable"],
            edgecolor=COLORS["grey"],
            label="Not activated",
        ),
        Rectangle(
            (0, 0),
            1,
            1,
            fill=False,
            edgecolor=COLORS["ink"],
            linewidth=1.5,
            label="Author-planted omission",
        ),
    ]
    fig.legend(
        handles=legend_elements,
        loc="upper left",
        bbox_to_anchor=(0.035, 0.895),
        ncol=5,
        frameon=False,
        fontsize=7.5,
        handlelength=1.6,
        columnspacing=1.3,
    )
    add_figure_footer(fig, package["commit"], package["generated_at"])
    save_figure(fig, output_dir, "fig01_submitted_evidence_coverage")


def draw_metric_card(
    ax: mpl.axes.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    value: str,
    label: str,
    note: str,
    accent: str,
) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=COLORS["paper"],
        edgecolor=COLORS["line"],
        linewidth=1,
    )
    ax.add_patch(patch)
    ax.add_patch(
        Rectangle(
            (x, y),
            0.012,
            height,
            facecolor=accent,
            edgecolor="none",
        )
    )
    ax.text(
        x + 0.035,
        y + height * 0.63,
        value,
        fontsize=18,
        fontweight="bold",
        color=accent,
        va="center",
    )
    ax.text(
        x + 0.035,
        y + height * 0.37,
        label,
        fontsize=8,
        fontweight="bold",
        va="center",
    )
    ax.text(
        x + 0.035,
        y + height * 0.16,
        note,
        fontsize=6.5,
        color=COLORS["muted"],
        va="center",
    )


def plot_passage_grounded_evidence(
    package: Dict[str, Any], output_dir: pathlib.Path
) -> None:
    """Figure 2: evidence lineage and pathway-normalized coverage."""
    aggregate = package["evidence"]["aggregate"]
    pathway_df = package["pathways"].set_index("pathway")

    fig = plt.figure(figsize=(11.4, 7.4))
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=[0.52, 0.48],
        width_ratios=[0.67, 0.33],
        left=0.05,
        right=0.98,
        top=0.86,
        bottom=0.22,
        hspace=0.28,
        wspace=0.18,
    )
    ax_flow = fig.add_subplot(grid[0, :])
    ax_bars = fig.add_subplot(grid[1, 0])
    ax_trace = fig.add_subplot(grid[1, 1])

    add_figure_header(
        fig,
        "Passage-grounded framework assessment",
        (
            "Counts preserve their units: cases, submitted passages, and "
            "dimension-level assessments are linked but are not interchangeable."
        ),
    )

    ax_flow.set_xlim(0, 1)
    ax_flow.set_ylim(0, 1)
    ax_flow.axis("off")
    card_y = 0.35
    card_h = 0.44
    positions = [
        (0.00, 0.15, str(aggregate["total_cases"]), "Fictional cases", "3 authored domains", COLORS["teal"]),
        (0.205, 0.15, str(aggregate["total_passages"]), "Submitted passages", "67 source excerpts", COLORS["blue"]),
        (0.41, 0.17, str(aggregate["dimension_assessments"]), "Framework assessments", "Pathway-dependent", COLORS["purple"]),
        (0.64, 0.15, str(aggregate["linked_non_missing_outputs"]), "Evidence-linked", "Documented / partial", COLORS["green"]),
        (0.845, 0.15, str(aggregate["missing_outputs"]), "Marked missing", "Submitted evidence absent", COLORS["red"]),
    ]
    for x, width, value, label, note, accent in positions:
        draw_metric_card(
            ax_flow, x, card_y, width, card_h, value, label, note, accent
        )

    arrow_pairs = [(0.15, 0.205), (0.355, 0.41), (0.58, 0.64)]
    for start_x, end_x in arrow_pairs:
        arrow = FancyArrowPatch(
            (start_x + 0.006, card_y + card_h / 2),
            (end_x - 0.006, card_y + card_h / 2),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1,
            linestyle="dashed",
            color=COLORS["grey"],
        )
        ax_flow.add_patch(arrow)

    split_x = 0.61
    ax_flow.plot(
        [split_x, split_x, 0.625, 0.625],
        [card_y + card_h / 2, 0.82, 0.82, card_y + card_h / 2],
        color=COLORS["grey"],
        linewidth=1,
        linestyle="dashed",
    )
    arrow_missing = FancyArrowPatch(
        (0.83, card_y + card_h / 2),
        (0.845, card_y + card_h / 2),
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=1,
        linestyle="dashed",
        color=COLORS["grey"],
    )
    ax_flow.add_patch(arrow_missing)
    ax_flow.text(
        0.50,
        0.18,
        "One passage may support multiple assessments",
        ha="center",
        va="center",
        fontsize=7,
        color=COLORS["muted"],
    )
    ax_flow.text(
        0.925,
        0.24,
        (
            f"{aggregate['detected_seeded_omissions']}/"
            f"{aggregate['seeded_omissions']} planted gaps detected\n"
            "59 other missing fields are not independent ground truth"
        ),
        ha="center",
        va="top",
        fontsize=6.7,
        color=COLORS["muted"],
        linespacing=1.3,
    )

    pathways = ["human_subjects", "ict_research", "ai_research"]
    y = np.arange(len(pathways))
    left = np.zeros(len(pathways))
    status_order = ["documented", "partial", "missing"]
    status_colors = {
        "documented": COLORS["green"],
        "partial": COLORS["amber"],
        "missing": COLORS["red"],
    }
    for status in status_order:
        values = np.array(
            [
                pathway_df.loc[pathway, status]
                / pathway_df.loc[pathway, "assessment_n"]
                * 100
                for pathway in pathways
            ]
        )
        bars = ax_bars.barh(
            y,
            values,
            left=left,
            height=0.48,
            color=status_colors[status],
            edgecolor=COLORS["paper"],
            linewidth=0.8,
            label=status.title(),
        )
        raw_values = [int(pathway_df.loc[pathway, status]) for pathway in pathways]
        for bar, raw, pct in zip(bars, raw_values, values):
            if pct >= 8:
                ax_bars.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    str(raw),
                    ha="center",
                    va="center",
                    fontsize=7,
                    fontweight="bold",
                    color=COLORS["paper"]
                    if status != "partial"
                    else COLORS["ink"],
                )
        left += values

    ax_bars.set_yticks(y)
    ax_bars.set_yticklabels([PATHWAY_LABELS[pathway] for pathway in pathways])
    ax_bars.invert_yaxis()
    ax_bars.set_xlim(0, 100)
    ax_bars.set_xlabel("Share of activated dimension assessments (%)")
    ax_bars.set_title(
        "A  Submitted-evidence coverage by pathway",
        loc="left",
        pad=12,
    )
    ax_bars.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax_bars.set_axisbelow(True)
    ax_bars.spines[["top", "right", "left"]].set_visible(False)
    for idx, pathway in enumerate(pathways):
        total = int(pathway_df.loc[pathway, "assessment_n"])
        ax_bars.text(
            102,
            idx,
            f"n={total}",
            va="center",
            ha="left",
            fontsize=7,
            color=COLORS["muted"],
            clip_on=False,
        )

    ax_trace.set_xlim(0, 1)
    ax_trace.set_ylim(0, 1)
    ax_trace.axis("off")
    ax_trace.set_title(
        "B  Traceability checks",
        loc="left",
        pad=12,
    )
    ax_trace.add_patch(
        FancyBboxPatch(
            (0.02, 0.44),
            0.96,
            0.46,
            boxstyle="round,pad=0.02,rounding_size=0.025",
            facecolor=COLORS["green_light"],
            edgecolor=COLORS["green"],
            linewidth=1,
        )
    )
    ax_trace.text(
        0.09,
        0.74,
        "79 / 79",
        fontsize=24,
        fontweight="bold",
        color=COLORS["green"],
        va="center",
    )
    ax_trace.text(
        0.09,
        0.57,
        "non-missing assessments cited\na submitted source passage",
        fontsize=8.5,
        fontweight="bold",
        linespacing=1.35,
        va="center",
    )
    ax_trace.add_patch(
        FancyBboxPatch(
            (0.02, 0.08),
            0.96,
            0.25,
            boxstyle="round,pad=0.02,rounding_size=0.025",
            facecolor=COLORS["grey_light"],
            edgecolor=COLORS["line"],
            linewidth=1,
        )
    )
    ax_trace.text(
        0.09,
        0.22,
        "Offline deterministic evaluator · no LLM calls",
        fontsize=8,
        fontweight="bold",
        va="center",
    )
    ax_trace.text(
        0.09,
        0.13,
        "Passing establishes specification conformance only.",
        fontsize=7,
        color=COLORS["muted"],
        va="center",
    )

    fig.text(
        0.05,
        0.095,
        (
            "Raw counts are printed inside bars. Pathways activate different "
            "numbers of dimensions (Human 5, ICT 6, AI 11), so distributions "
            "are not comparative accuracy scores."
        ),
        fontsize=7,
        color=COLORS["muted"],
    )
    coverage_handles, coverage_labels = ax_bars.get_legend_handles_labels()
    fig.legend(
        coverage_handles,
        coverage_labels,
        loc="center left",
        bbox_to_anchor=(0.05, 0.060),
        ncol=3,
        frameon=False,
        fontsize=7.5,
        handlelength=1.8,
        columnspacing=1.6,
    )
    add_figure_footer(fig, package["commit"], package["generated_at"])
    save_figure(fig, output_dir, "fig02_passage_grounded_evidence")


def plot_seeded_corpus_composition(
    package: Dict[str, Any], output_dir: pathlib.Path
) -> None:
    """Figure 3: corpus balance, adaptive routing, and planted gaps."""
    cases_df = package["cases"]
    omission_df = package["omissions"].copy()
    pathway_df = package["pathways"].set_index("pathway")

    domains = ["academic_hci", "qualitative_social", "applied_ux_service"]
    pathways = ["human_subjects", "ict_research", "ai_research"]
    composition = np.zeros((len(domains), len(pathways)), dtype=int)
    for row_idx, domain in enumerate(domains):
        for col_idx, pathway in enumerate(pathways):
            composition[row_idx, col_idx] = int(
                (
                    (cases_df["domain"] == domain)
                    & (cases_df["observed_pathway"] == pathway)
                ).sum()
            )

    fig = plt.figure(figsize=(11.4, 6.8))
    grid = fig.add_gridspec(
        1,
        3,
        width_ratios=[0.34, 0.27, 0.39],
        left=0.055,
        right=0.98,
        top=0.84,
        bottom=0.13,
        wspace=0.28,
    )
    ax_comp = fig.add_subplot(grid[0, 0])
    ax_route = fig.add_subplot(grid[0, 1])
    ax_omit = fig.add_subplot(grid[0, 2])

    add_figure_header(
        fig,
        "Composition of the seeded technical-evaluation corpus",
        (
            "Twenty-one fictional cases cover three research domains, three "
            "review pathways, and ten deliberately omitted dimensions."
        ),
    )

    comp_cmap = ListedColormap(
        [COLORS["grey_light"], COLORS["blue_light"], "#9EC6DE", COLORS["blue"]]
    )
    comp_norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], comp_cmap.N)
    ax_comp.imshow(
        composition,
        cmap=comp_cmap,
        norm=comp_norm,
        aspect="equal",
        interpolation="none",
    )
    for row_idx in range(composition.shape[0]):
        for col_idx in range(composition.shape[1]):
            value = composition[row_idx, col_idx]
            ax_comp.text(
                col_idx,
                row_idx,
                str(value),
                ha="center",
                va="center",
                fontsize=15,
                fontweight="bold",
                color=COLORS["paper"] if value == 3 else COLORS["ink"],
            )
    ax_comp.set_xticks(range(len(pathways)))
    ax_comp.set_xticklabels(
        ["Human", "ICT", "AI"],
        fontsize=8,
    )
    ax_comp.set_yticks(range(len(domains)))
    ax_comp.set_yticklabels([DOMAIN_LABELS[domain] for domain in domains])
    ax_comp.tick_params(length=0, pad=7)
    ax_comp.set_title("A  Domain × pathway cases", loc="left", pad=16)
    for x in np.arange(-0.5, len(pathways), 1):
        ax_comp.axvline(x, color=COLORS["paper"], linewidth=2)
    for y in np.arange(-0.5, len(domains), 1):
        ax_comp.axhline(y, color=COLORS["paper"], linewidth=2)
    ax_comp.text(
        0.0,
        -0.20,
        "Counts encode authored test cases, not real-world prevalence.",
        transform=ax_comp.transAxes,
        fontsize=6.8,
        color=COLORS["muted"],
        va="top",
    )

    route_metrics = [
        ("Cases", "case_n"),
        ("Dimensions\nper case", "dimensions_per_case"),
        ("Frameworks\nper case", "frameworks_per_case"),
    ]
    x_positions = np.arange(len(route_metrics))
    for row_idx, pathway in enumerate(pathways):
        values = [
            int(pathway_df.loc[pathway, field])
            for _, field in route_metrics
        ]
        for x_value, value in zip(x_positions, values):
            ax_route.scatter(
                x_value,
                row_idx,
                s=650,
                color=PATHWAY_COLORS[pathway],
                edgecolor=COLORS["paper"],
                linewidth=1.5,
                zorder=2,
            )
            ax_route.text(
                x_value,
                row_idx,
                str(value),
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=COLORS["paper"],
                zorder=3,
            )
    ax_route.set_xticks(x_positions)
    ax_route.set_xticklabels([label for label, _ in route_metrics], fontsize=8)
    ax_route.set_yticks(range(len(pathways)))
    ax_route.set_yticklabels([PATHWAY_LABELS[pathway] for pathway in pathways])
    for label, pathway in zip(ax_route.get_yticklabels(), pathways):
        label.set_color(PATHWAY_COLORS[pathway])
        label.set_fontweight("bold")
    ax_route.set_xlim(-0.55, len(route_metrics) - 0.45)
    ax_route.set_ylim(len(pathways) - 0.45, -0.55)
    for x_value in np.arange(-0.5, len(route_metrics), 1):
        ax_route.axvline(
            x_value,
            color=COLORS["grid"],
            linewidth=0.8,
            zorder=0,
        )
    ax_route.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax_route.tick_params(axis="both", length=0, pad=8)
    ax_route.set_title("B  Adaptive review load", loc="left", pad=16)
    ax_route.text(
        0.0,
        -0.07,
        "Counts reflect routing design, not pathway performance.",
        transform=ax_route.transAxes,
        fontsize=6.8,
        color=COLORS["muted"],
        va="top",
    )

    omission_df = omission_df.sort_values(
        ["seeded_n", "dimension_label"], ascending=[True, True]
    )
    y = np.arange(len(omission_df))
    ax_omit.hlines(
        y,
        0,
        omission_df["seeded_n"],
        color=COLORS["green_light"],
        linewidth=5,
        zorder=1,
    )
    ax_omit.scatter(
        omission_df["seeded_n"],
        y,
        s=58,
        facecolor=COLORS["paper"],
        edgecolor=COLORS["ink"],
        linewidth=1.2,
        label="Planted",
        zorder=2,
    )
    ax_omit.scatter(
        omission_df["detected_n"],
        y,
        s=20,
        facecolor=COLORS["green"],
        edgecolor=COLORS["green"],
        label="Detected",
        zorder=3,
    )
    for idx, row in omission_df.reset_index(drop=True).iterrows():
        ax_omit.text(
            row["seeded_n"] + 0.12,
            idx,
            f"{int(row['detected_n'])}/{int(row['seeded_n'])}",
            va="center",
            fontsize=7,
            fontweight="bold",
            color=COLORS["green"],
        )
    ax_omit.set_yticks(y)
    ax_omit.set_yticklabels(omission_df["dimension_label"], fontsize=7.5)
    ax_omit.set_xlim(0, 3.65)
    ax_omit.set_xticks([0, 1, 2, 3])
    ax_omit.set_xlabel("Authored cases")
    ax_omit.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax_omit.set_axisbelow(True)
    ax_omit.spines[["top", "right", "left"]].set_visible(False)
    ax_omit.tick_params(axis="y", length=0)
    ax_omit.set_title("C  Planted omission taxonomy", loc="left", pad=16)
    ax_omit.text(
        0.0,
        -0.075,
        "Open ring = planted · filled dot = detected",
        transform=ax_omit.transAxes,
        fontsize=6.8,
        color=COLORS["muted"],
        va="top",
    )

    add_figure_footer(fig, package["commit"], package["generated_at"])
    save_figure(fig, output_dir, "fig03_seeded_corpus_composition")


def plot_specification_conformance(
    package: Dict[str, Any], output_dir: pathlib.Path
) -> None:
    """Appendix figure: 21 cases by 6 executable checks."""
    checks_df = package["checks"]
    cases_df = package["cases"]
    case_order = cases_df["case_id"].tolist()
    check_order = [definition["id"] for definition in CHECK_DEFINITIONS]
    matrix = np.zeros((len(case_order), len(check_order)), dtype=int)
    for row_idx, case_id in enumerate(case_order):
        subset = checks_df[checks_df["case_id"] == case_id].set_index(
            "check_id"
        )
        for col_idx, check_id in enumerate(check_order):
            matrix[row_idx, col_idx] = int(bool(subset.loc[check_id, "passed"]))

    cmap = ListedColormap([COLORS["red_light"], COLORS["green"]])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)
    fig = plt.figure(figsize=(9.8, 7.5))
    grid = fig.add_gridspec(
        1,
        2,
        width_ratios=[0.75, 0.25],
        left=0.09,
        right=0.97,
        top=0.84,
        bottom=0.11,
        wspace=0.22,
    )
    ax = fig.add_subplot(grid[0, 0])
    ax_summary = fig.add_subplot(grid[0, 1])

    add_figure_header(
        fig,
        "Deterministic specification-conformance matrix",
        (
            "Each row is one fictional protocol and each column one executable "
            "acceptance check in the offline SafeBARS evaluator."
        ),
    )

    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto", interpolation="none")
    ax.set_xticks(range(len(check_order)))
    ax.set_xticklabels(
        [
            "Pathway\nrouting",
            "Framework\nactivation",
            "Seeded gap\nsurfaced",
            "Passage\nreferences",
            "Confidence\nreported",
            "Repeated run\ndeterministic",
        ],
        fontsize=7.5,
    )
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=8)
    ax.set_yticks(range(len(case_order)))
    ax.set_yticklabels(case_order, fontsize=7.2)
    ax.tick_params(axis="y", length=0)
    for row_idx in range(matrix.shape[0]):
        for col_idx in range(matrix.shape[1]):
            ax.text(
                col_idx,
                row_idx,
                "✓" if matrix[row_idx, col_idx] else "×",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                color=COLORS["paper"]
                if matrix[row_idx, col_idx]
                else COLORS["red"],
            )
    for x in np.arange(-0.5, len(check_order), 1):
        ax.axvline(x, color=COLORS["paper"], linewidth=1.5)
    for y in np.arange(-0.5, len(case_order), 1):
        ax.axhline(y, color=COLORS["paper"], linewidth=1.5)
    for y in (6.5, 13.5):
        ax.axhline(y, color=COLORS["ink"], linewidth=1.2)

    totals = (
        checks_df.groupby("check_id")["passed"].agg(["sum", "count"]).loc[
            check_order
        ]
    )
    y = np.arange(len(check_order))
    ax_summary.barh(
        y,
        totals["count"],
        color=COLORS["grey_light"],
        edgecolor="none",
        height=0.55,
    )
    ax_summary.barh(
        y,
        totals["sum"],
        color=COLORS["green"],
        edgecolor="none",
        height=0.55,
    )
    for row_idx, check_id in enumerate(check_order):
        ax_summary.text(
            21.45,
            row_idx,
            f"{int(totals.loc[check_id, 'sum'])}/"
            f"{int(totals.loc[check_id, 'count'])}",
            va="center",
            fontsize=7,
            fontweight="bold",
        )
    ax_summary.set_yticks(y)
    ax_summary.set_yticklabels([])
    ax_summary.invert_yaxis()
    ax_summary.set_xlim(0, 25)
    ax_summary.set_xticks([0, 7, 14, 21])
    ax_summary.set_xlabel("Cases passed")
    ax_summary.grid(axis="x", color=COLORS["grid"], linewidth=0.8)
    ax_summary.set_axisbelow(True)
    ax_summary.spines[["top", "right", "left"]].set_visible(False)
    ax_summary.tick_params(axis="y", length=0)
    ax_summary.set_title(
        "Check totals\n126 / 126 assertions passed",
        loc="left",
        pad=12,
        color=COLORS["green"],
    )
    short_check_labels = [
        "Pathway routing",
        "Framework activation",
        "Seeded gap surfaced",
        "Passage references",
        "Confidence reported",
        "Repeated run deterministic",
    ]
    for row_idx, label in enumerate(short_check_labels):
        ax_summary.text(
            0.7,
            row_idx,
            label,
            ha="left",
            va="center",
            fontsize=6.7,
            fontweight="bold",
            color=COLORS["paper"],
        )

    add_figure_footer(fig, package["commit"], package["generated_at"])
    save_figure(fig, output_dir, "figA1_specification_conformance")


def write_study_templates(output_dir: pathlib.Path) -> None:
    """Create header-only schemas for future real comparative-study results."""
    templates_dir = output_dir / "study_data_templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    schemas = {
        "participants_template.csv": [
            "participant_id",
            "sequence_id",
            "expertise_group",
            "consented",
            "task1_completed",
            "task2_completed",
            "withdrawn",
            "excluded",
            "exclusion_reason",
        ],
        "task_outcomes_template.csv": [
            "participant_id",
            "sequence_id",
            "case_id",
            "condition",
            "task_order",
            "ai_enabled_case",
            "artifact_id",
            "task_completed",
            "task_elapsed_seconds",
            "time_to_first_revision_seconds",
            "substantive_revision_n",
            "source_grounded_revision_n",
            "unsupported_claim_n",
            "appropriate_deferral_n",
            "final_artifact_chars",
            "chat_turn_n",
            "model_error_n",
            "perceived_control_mean",
            "verification_reliance_mean",
            "confidence_mean",
            "nasa_tlx_mental",
            "nasa_tlx_temporal",
            "nasa_tlx_performance",
            "nasa_tlx_effort",
            "nasa_tlx_frustration",
        ],
        "expert_ratings_template.csv": [
            "artifact_id",
            "participant_id",
            "case_id",
            "condition",
            "rater_id",
            "criterion",
            "score",
            "rationale",
            "condition_guess",
            "condition_guess_confidence",
        ],
        "handoff_outcomes_template.csv": [
            "participant_id",
            "case_id",
            "condition",
            "handoff_id",
            "packet_format",
            "expert_id",
            "recommended_role",
            "assigned_role",
            "expert_routing_rating",
            "expert_evidence_sufficiency_rating",
            "expert_actionability_rating",
            "expert_provenance_confidence",
            "clarification_requested",
            "time_to_first_decision_seconds",
            "total_triage_seconds",
            "consequential_issue_n",
            "revision_linked",
        ],
        "revision_units_template.csv": [
            "participant_id",
            "case_id",
            "condition",
            "revision_id",
            "artifact_section",
            "revision_type",
            "substantive",
            "exact_source_cited",
            "decision_rationale_present",
            "suggestion_uptake",
            "unsupported_claim",
            "coder_id",
        ],
    }
    for filename, columns in schemas.items():
        pd.DataFrame(columns=columns).to_csv(
            templates_dir / filename,
            index=False,
            encoding="utf-8",
        )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate SafeBARS paper-ready technical-evidence figures"
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT,
        help="Directory for figures and tidy data",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    configure_matplotlib()
    output_dir = args.output_dir.resolve()
    package = build_tables()
    write_tables(package, output_dir)
    plot_submitted_evidence_coverage(package, output_dir)
    plot_passage_grounded_evidence(package, output_dir)
    plot_seeded_corpus_composition(package, output_dir)
    plot_specification_conformance(package, output_dir)
    write_study_templates(output_dir)

    print(f"Generated SafeBARS figure package in {output_dir}")
    print(
        "Figures: fig01, fig02, fig03, figA1 (PNG/SVG/PDF); "
        "data: 9 tidy CSV files + manifest.json"
    )
    print(BOUNDARY_TEXT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
