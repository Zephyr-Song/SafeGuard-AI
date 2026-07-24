"""Public technical-evidence payload and API regression tests."""

import importlib.util
import pathlib
import unittest

from app import app


_REPO = pathlib.Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "technical_evidence_evaluator",
    _REPO / "tests" / "evaluation" / "run_technical_evaluation.py",
)
_EVALUATOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_EVALUATOR)


class TechnicalEvidencePayloadTest(unittest.TestCase):
    def test_runtime_aggregate_matches_seeded_suite(self):
        evidence = _EVALUATOR.build_public_evidence()
        aggregate = evidence["aggregate"]

        self.assertEqual(aggregate["total_cases"], 21)
        self.assertEqual(aggregate["passed_cases"], 21)
        self.assertEqual(aggregate["failed_cases"], 0)
        self.assertEqual(aggregate["domain_count"], 3)
        self.assertEqual(
            aggregate["pathway_counts"],
            {"ai_research": 8, "human_subjects": 7, "ict_research": 6},
        )
        self.assertEqual(aggregate["project_type_counts"], {"ai": 8, "non_ai": 13})
        self.assertEqual(aggregate["total_passages"], 67)
        self.assertEqual(aggregate["dimension_assessments"], 159)
        self.assertEqual(
            aggregate["coverage_counts"],
            {"documented": 4, "partial": 75, "missing": 80},
        )
        self.assertEqual(aggregate["linked_non_missing_outputs"], 79)
        self.assertEqual(aggregate["missing_outputs"], 80)
        self.assertEqual(aggregate["seeded_omissions"], 21)
        self.assertEqual(aggregate["detected_seeded_omissions"], 21)
        self.assertEqual(aggregate["check_type_count"], 6)
        self.assertEqual(aggregate["assertions_total"], 126)
        self.assertEqual(aggregate["assertions_passed"], 126)
        self.assertEqual(aggregate["assertions_failed"], 0)

    def test_payload_has_explicit_evidence_boundary_and_case_matrix(self):
        evidence = _EVALUATOR.build_public_evidence()

        self.assertFalse(evidence["metadata"]["human_validated"])
        self.assertIn("commit_sha", evidence["metadata"])
        self.assertIn("fictional", evidence["metadata"]["dataset_label"].lower())
        self.assertIn("do not establish", evidence["metadata"]["boundary_statement"])
        self.assertEqual(evidence["source"]["calculation"], "runtime")
        self.assertFalse(evidence["source"]["ignored_snapshot_required"])
        self.assertEqual(len(evidence["cases"]), 21)

        check_ids = [
            definition["id"] for definition in evidence["aggregate"]["check_types"]
        ]
        self.assertEqual(
            check_ids,
            [
                "pathway",
                "frameworks",
                "seeded_missing",
                "passage_refs",
                "confidence",
                "deterministic",
            ],
        )
        for case in evidence["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(list(case["checks"]), check_ids)
                self.assertEqual(case["checks_total"], 6)
                self.assertEqual(case["checks_passed"], 6)
                self.assertTrue(case["seeded_missing_detected"])
                self.assertTrue(case["passed"])

    def test_evidence_values_are_deterministic(self):
        first = _EVALUATOR.build_public_evidence()
        second = _EVALUATOR.build_public_evidence()

        self.assertEqual(first["aggregate"], second["aggregate"])
        self.assertEqual(first["cases"], second["cases"])


class TechnicalEvidenceApiTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_public_read_only_endpoint(self):
        response = self.client.get("/api/safebars/v2/evidence/technical")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["evidence"]["aggregate"]["total_cases"], 21)
        self.assertFalse(payload["evidence"]["metadata"]["human_validated"])

    def test_workspace_exposes_validation_matrix_and_boundary(self):
        response = self.client.get("/safebars")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Evidence &amp; Validation", response.data)
        self.assertIn(b'id="evidenceMatrix"', response.data)
        self.assertIn(b"Synthetic seeded technical validation", response.data)
        self.assertIn(b"Human-study evidence is still pending", response.data)


if __name__ == "__main__":
    unittest.main()
