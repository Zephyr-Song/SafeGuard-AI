from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHI_DIR = REPO_ROOT / "research" / "chi2027"


def _read(name: str) -> str:
    return (CHI_DIR / name).read_text(encoding="utf-8")


def test_canonical_plan_has_exactly_three_research_questions():
    text = _read("CURRENT_CANONICAL_PLAN.md")
    headings = [
        line.strip()
        for line in text.splitlines()
        if line.startswith("### RQ")
    ]
    assert headings == [
        "### RQ1: Protocol-preparation quality",
        "### RQ2: Contestation and calibrated use",
        "### RQ3: Expert handoff work",
    ]
    assert not any(line.startswith("### RQ4") for line in text.splitlines())


def test_blueprint_protocol_and_timeline_share_the_frozen_design():
    filenames = [
        "CURRENT_CANONICAL_PLAN.md",
        "86_evalLM_blueprint_final_rqs.md",
        "87_46_day_chi_execution_plan.md",
        "88_final_comparative_study_protocol.md",
    ]
    documents = {name: _read(name) for name in filenames}

    for text in documents.values():
        assert "10.1145/3613904.3642216" in text
        lower = text.lower()
        assert (
            "general_chat" in lower
            or "general llm chat" in lower
            or "general-purpose llm chat" in lower
        )
        assert "safebars_full" in lower or "safebars" in lower

    assert "target 24" in documents["CURRENT_CANONICAL_PLAN.md"].lower()
    assert "target 24" in documents["88_final_comparative_study_protocol.md"].lower()
    assert "Recruitment target: **24" in documents[
        "87_46_day_chi_execution_plan.md"
    ]
    assert "24 participants" in documents["86_evalLM_blueprint_final_rqs.md"]
    assert "eight reviewers" not in documents["86_evalLM_blueprint_final_rqs.md"].lower()


def test_primary_index_is_fixed_to_four_components():
    text = _read("CURRENT_CANONICAL_PLAN.md")
    assert "information completeness" in text
    assert "safeguard specificity" in text
    assert "actionability" in text
    assert "evidence grounding and traceability" in text

    rubric = _read("90_blinded_artifact_quality_rubric.md")
    assert "unweighted mean of D1-D4" in rubric
    assert "D5-D7 are prespecified secondary outcomes" in rubric


def test_repository_does_not_claim_the_unsubmitted_manuscript_is_under_review():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "submission (under review)" not in readme
    assert "not under review at the time of this release" in readme
