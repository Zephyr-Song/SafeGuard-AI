"""pytest wrapper for the SafeBARS offline technical evaluation.

This reuses ``tests/evaluation/run_technical_evaluation.py`` so the same
deterministic checks run inside the normal ``pytest`` suite (and therefore in
CI). It asserts:

* every seeded protocol case routes to the expected dual-path;
* the activated framework set matches the pathway;
* each seeded missing transition is surfaced rather than hidden;
* documented/partial dimensions cite a source passage (provenance);
* repeated runs are deterministic.
"""

import importlib.util
import pathlib
import sys
import unittest

_REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO))

_SPEC = importlib.util.spec_from_file_location(
    "run_technical_evaluation",
    str(_REPO / "tests" / "evaluation" / "run_technical_evaluation.py"),
)
_eval = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_eval)

run_all = _eval.run_all
evaluate_case = _eval.evaluate_case
get_seed_cases = _eval.seed_cases.get_seed_cases


class TechnicalEvaluationTest(unittest.TestCase):
    def test_all_seed_cases_conform_to_spec(self):
        results, summary, failed = run_all()
        self.assertEqual(
            failed, 0,
            msg=f"{summary['failed_cases']} of {summary['total_cases']} cases failed: {summary}",
        )
        # The evaluation is expected to cover three study domains.
        self.assertEqual(len(summary["by_domain"]), 3)

    def test_expected_case_count(self):
        self.assertEqual(len(get_seed_cases()), 21)

    def test_each_case_individually(self):
        for case in get_seed_cases():
            with self.subTest(case=case["id"]):
                result = evaluate_case(case)
                self.assertTrue(result["passed"], result["checks"])


if __name__ == "__main__":
    unittest.main()
