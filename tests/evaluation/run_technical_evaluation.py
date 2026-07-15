"""Deterministic technical evaluation runner for SafeBARS.

Runs every seeded protocol case (see ``seed_cases.py``) through the framework
selector and asserts the workflow behaves as specified in
``research/chi2027/75_revised_contribution_rqs_and_mvp.md``:

* the dual-path routing (human_subjects / ict_research / ai_research) is correct;
* the activated framework set matches the pathway;
* the seeded missing transition is surfaced as ``missing`` rather than hidden;
* every documented/partial dimension links back to at least one source passage;
* repeated runs are deterministic (no silent model variance in this offline path).

This is a *spec-conformance* check, not an ethics-reasoning validation. It runs
fully offline and is intended to be wired into CI so regressions fail the build.

Usage:
    python tests/evaluation/run_technical_evaluation.py [--quiet] [--json-out PATH]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
from typing import Any, Dict, List, Tuple

_HERE = pathlib.Path(__file__).resolve().parent

# Allow running both as a standalone script and being imported by pytest,
# regardless of whether ``tests/evaluation`` is treated as a package.
try:
    from . import seed_cases  # imported as a package
    from modules.framework_selector import select_framework_path
except ImportError:  # script execution or non-package import
    sys.path.insert(0, str(_HERE.parent.parent))
    _seed_spec = importlib.util.spec_from_file_location(
        "seed_cases", str(_HERE / "seed_cases.py")
    )
    seed_cases = importlib.util.module_from_spec(_seed_spec)
    _seed_spec.loader.exec_module(seed_cases)
    from modules.framework_selector import select_framework_path


def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """Run one seed case and return its checks."""
    project = seed_cases.case_to_project(case)
    passages = case.get("passages", [])

    selection = select_framework_path(project, passages=passages)
    selection_again = select_framework_path(project, passages=passages)

    dims = {d["id"]: d for d in selection["dimensions"]}
    selected_fw = {f["id"] for f in selection["frameworks"]}
    expected_fw = set(case["expected_frameworks"])

    checks: Dict[str, Any] = {}

    # 1. Pathway routing.
    checks["pathway"] = (selection["pathway"] == case["expected_pathway"], selection["pathway"])

    # 2. Activated framework set.
    checks["frameworks"] = (selected_fw == expected_fw, sorted(selected_fw))

    # 3. Seeded missing transition is surfaced, not hidden.
    seeded = case["seeded_missing_dimension"]
    seeded_coverage = dims.get(seeded, {}).get("coverage")
    checks["seeded_missing"] = (seeded_coverage == "missing", seeded_coverage)

    # 4. Passage provenance: documented/partial dims cite a source passage.
    provenance_ok = True
    for d in selection["dimensions"]:
        if d["coverage"] in ("documented", "partial") and not d["source_passage_ids"]:
            provenance_ok = False
            break
    checks["passage_refs"] = (provenance_ok, "ok" if provenance_ok else "missing refs")

    # 5. Confidence is reported.
    checks["confidence"] = (
        bool(selection.get("confidence", {}).get("level")),
        selection.get("confidence", {}).get("level"),
    )

    # 6. Determinism across repeated runs.
    deterministic = json.dumps(selection, sort_keys=True) == json.dumps(
        selection_again, sort_keys=True
    )
    checks["deterministic"] = (deterministic, "ok" if deterministic else "differs")

    passed = all(value[0] for value in checks.values())
    return {
        "id": case["id"],
        "domain": case["domain"],
        "note": case.get("note", ""),
        "expected_pathway": case["expected_pathway"],
        "checks": checks,
        "passed": passed,
    }


def run_all() -> Tuple[List[Dict[str, Any]], Dict[str, Any], int]:
    """Evaluate every seed case. Returns (results, summary, failed_count)."""
    cases = seed_cases.get_seed_cases()
    results = [evaluate_case(c) for c in cases]

    counts = {"pathway": 0, "frameworks": 0, "seeded_missing": 0,
              "passage_refs": 0, "confidence": 0, "deterministic": 0}
    for r in results:
        for key in counts:
            if r["checks"][key][0]:
                counts[key] += 1

    failed = sum(1 for r in results if not r["passed"])
    domains = {}
    for r in results:
        domains.setdefault(r["domain"], {"total": 0, "passed": 0})
        domains[r["domain"]]["total"] += 1
        domains[r["domain"]]["passed"] += 1 if r["passed"] else 0

    summary = {
        "total_cases": len(results),
        "passed_cases": len(results) - failed,
        "failed_cases": failed,
        "check_totals": {k: {"passed": v, "total": len(results)} for k, v in counts.items()},
        "by_domain": domains,
    }
    return results, summary, failed


def _print_report(results: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    print("=" * 72)
    print("SafeBARS Technical Evaluation (offline, deterministic)")
    print("=" * 72)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['id']:<8} {r['domain']:<18} {r['expected_pathway']:<14}")
        if not r["passed"]:
            for key, (ok, got) in r["checks"].items():
                if not ok:
                    print(f"        - {key}: got {got}")
            print(f"        note: {r['note']}")
    print("-" * 72)
    print(f"Cases: {summary['passed_cases']}/{summary['total_cases']} passed "
          f"({summary['failed_cases']} failed)")
    for key, c in summary["check_totals"].items():
        print(f"  {key:<14} {c['passed']}/{c['total']}")
    print("=" * 72)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SafeBARS offline technical evaluation")
    parser.add_argument("--quiet", action="store_true", help="Suppress the per-case report")
    parser.add_argument("--json-out", default=str(_HERE / "results.json"),
                        help="Path for JSON results")
    args = parser.parse_args(argv)

    results, summary, failed = run_all()
    if not args.quiet:
        _print_report(results, summary)

    out_path = args.json_out
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "results": results}, fh, ensure_ascii=False, indent=2)
    except OSError as exc:  # pragma: no cover - environment dependent
        print(f"Warning: could not write JSON results to {out_path}: {exc}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
