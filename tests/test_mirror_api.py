import tempfile
import unittest
from pathlib import Path

from app import app
import modules.mirror_api as mirror_api_module
from modules.mirror_engine import MirrorEngine

SAMPLE_MIRROR_PROJECT = {
    "title": "Agentic AI tutor study",
    "research_plan": (
        "We will build an LLM tutor for first-year programming students. "
        "The tutor will infer when a learner is struggling, recommend exercises, "
        "and automatically send a weekly risk label to the lecturer. "
        "We will recruit volunteers from one English-medium course and retain "
        "their prompts and tutor responses for model improvement."
    ),
    "value_commitments": [
        "Preserve learner autonomy",
        "Avoid unfair exclusion",
    ],
    "intake_answers": {
        "research_context": "Computer-science education in a university course.",
        "intended_change": "Help students improve early project ideas.",
        "direct_users": "Students preparing a project proposal.",
        "ai_role": "An LLM recommends revisions while an instructor remains responsible.",
        "data_materials": "Project pitches, prompts, feedback, and revision logs.",
        "affected_others": "Classmates and instructors may be affected by readiness labels.",
        "value_commitment": "Students should retain authorship and contest consequential feedback.",
        "stop_condition": "Labels begin affecting grades without an effective appeal route.",
        "optional_perspective_context": "The researcher is also a course tutor.",
        "unexpected_sensitive_field": "must not be persisted",
    },
}


class MirrorApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "mirror-api.db")
        self.original_engine = mirror_api_module.mirror_engine
        mirror_api_module.mirror_engine = MirrorEngine(db_path=self.db_path)
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def tearDown(self):
        mirror_api_module.mirror_engine = self.original_engine
        self.temp_dir.cleanup()

    def test_mirror_page_is_available_as_an_isolated_app(self):
        response = self.client.get("/safebars/mirror")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Ethical Mirror", html)
        self.assertIn('data-api-root="/api/safebars/mirror"', html)
        self.assertIn("safebars_mirror/mirror.css", html)
        self.assertIn("safebars_mirror/mirror.js", html)
        self.assertIn("Question 1 of 8", html)
        self.assertIn("asks one question at a time", html)
        self.assertIn("does not use the camera to estimate age", html)
        self.assertIn("Needs attention", html)
        self.assertNotIn("Strong tensions", html)

    def test_frontend_normalizes_the_structured_provenance_contract(self):
        project_root = Path(__file__).resolve().parents[1]
        javascript = (
            project_root / "static" / "safebars_mirror" / "mirror.js"
        ).read_text(encoding="utf-8")

        for contract_marker in (
            "item.role_label",
            "item.visualization?.frames",
            "item.first_person_probe",
            "item.provenance",
            "provenance.literature_ids",
            "designChoice.quote",
            "item.event_type",
            "revision.resolutions",
            "revision.after_snapshot",
            "revision.replay",
            "item.attention_required",
            "edge.needs_attention",
        ):
            with self.subTest(contract_marker=contract_marker):
                self.assertIn(contract_marker, javascript)

        for mojibake_marker in ("鈥", "鉁", "鈫", "鈱"):
            self.assertNotIn(mojibake_marker, javascript)

    def test_direct_user_question_has_starters_and_build_action_is_left_aligned(self):
        project_root = Path(__file__).resolve().parents[1]
        javascript = (
            project_root / "static" / "safebars_mirror" / "mirror.js"
        ).read_text(encoding="utf-8")
        template = (
            project_root / "templates" / "safebars_mirror.html"
        ).read_text(encoding="utf-8")
        stylesheet = (
            project_root / "static" / "safebars_mirror" / "mirror.css"
        ).read_text(encoding="utf-8")

        for starter in (
            "Student · preparing work",
            "Person · before a decision",
            "Worker · during a task",
            "Service user · seeking support",
            "Professional · reviewing a case",
        ):
            self.assertIn(starter, javascript)
        conversation_start = template.index('class="surface intake-conversation"')
        conversation_end = template.index("</article>", conversation_start)
        build_button = template.index('id="buildMirrorBtn"')
        self.assertLess(conversation_start, build_button)
        self.assertLess(build_button, conversation_end)
        self.assertLess(build_button, template.index('id="planValidation"'))
        self.assertIn(
            ".intake-build-actions {\n    justify-content: flex-start;",
            stylesheet,
        )
        self.assertIn("margin-top: auto;", stylesheet)

    def test_config_and_literature_make_every_lens_auditable(self):
        config_response = self.client.get("/api/safebars/mirror/config")
        self.assertEqual(config_response.status_code, 200)
        config = config_response.get_json()
        self.assertIs(config["success"], True)
        self.assertEqual(len(config["lenses"]), 9)
        self.assertIn("not an ethics score", config["interpretation_boundary"].lower())

        literature_response = self.client.get("/api/safebars/mirror/literature")
        self.assertEqual(literature_response.status_code, 200)
        literature_payload = literature_response.get_json()
        self.assertIs(literature_payload["success"], True)
        literature = literature_payload["literature"]
        literature_by_id = {item["id"]: item for item in literature}

        for source in literature:
            with self.subTest(source=source["id"]):
                self.assertTrue(source["title"])
                self.assertTrue(source["authors"])
                self.assertIsInstance(source["year"], int)
                self.assertTrue(source["venue"])
                self.assertTrue(source["doi"] or source["url"])
                self.assertTrue(source["design_use"])

        referenced_ids = set()
        for lens in config["lenses"]:
            self.assertTrue(lens["source_ids"])
            referenced_ids.update(lens["source_ids"])
            self.assertTrue(
                set(lens["source_ids"]).issubset(literature_by_id),
                f"{lens['id']} refers to literature absent from GET /literature",
            )

        all_dois = {str(item["doi"]).lower() for item in literature}
        self.assertIn("10.1145/3544548.3581347", all_dois)
        self.assertIn("10.1177/0146167219841621", all_dois)
        priolo = next(
            item
            for item in literature
            if str(item["doi"]).lower() == "10.1177/0146167219841621"
        )
        for author in (
            "Daniel Priolo",
            "Audrey Pelt",
            "Roxane Saint-Bauzel",
            "Lolita Rubens",
            "Dimitri Voisin",
            "Valerie Fointiat",
        ):
            self.assertIn(author, priolo["authors"])
        self.assertTrue(referenced_ids)

    def test_complete_api_workflow_is_persistent_and_traceable(self):
        created_response = self.client.post(
            "/api/safebars/mirror/sessions",
            json=SAMPLE_MIRROR_PROJECT,
        )
        self.assertEqual(created_response.status_code, 201)
        created_payload = created_response.get_json()
        self.assertIs(created_payload["success"], True)
        created = created_payload["session"]
        session_id = created["id"]
        for field in (
            "id",
            "title",
            "research_plan",
            "value_commitments",
            "lenses",
            "scenarios",
            "dissonance_edges",
            "revisions",
            "ledger",
            "boundary_notice",
        ):
            self.assertIn(field, created)
        self.assertEqual(
            created["intake_answers"]["research_context"],
            SAMPLE_MIRROR_PROJECT["intake_answers"]["research_context"],
        )
        self.assertNotIn("unexpected_sensitive_field", created["intake_answers"])

        analyzed_response = self.client.post(
            f"/api/safebars/mirror/sessions/{session_id}/analyze",
            json={"use_llm": False},
        )
        self.assertEqual(analyzed_response.status_code, 200)
        analyzed_payload = analyzed_response.get_json()
        self.assertIs(analyzed_payload["success"], True)
        analyzed = analyzed_payload["session"]
        edge = analyzed["dissonance_edges"][0]
        self.assertIn("attention_required", edge)
        self.assertIn("attention_basis", edge)

        revised_plan = (
            SAMPLE_MIRROR_PROJECT["research_plan"]
            + " Before any risk label is shared, the learner can inspect, contest, "
            "and request review by a named human researcher."
        )
        revisions_response = self.client.post(
            f"/api/safebars/mirror/sessions/{session_id}/revisions",
            json={
                "revised_plan": revised_plan,
                "resolutions": [
                    {
                        "edge_id": edge["id"],
                        "decision": "revise",
                        "rationale": "Add a contestable human checkpoint.",
                    }
                ],
            },
        )
        self.assertEqual(revisions_response.status_code, 200)
        revisions_payload = revisions_response.get_json()
        self.assertIs(revisions_payload["success"], True)
        self.assertTrue(revisions_payload["session"]["revisions"])

        replay_response = self.client.post(
            f"/api/safebars/mirror/sessions/{session_id}/replay",
            json={},
        )
        self.assertEqual(replay_response.status_code, 200)
        replay_payload = replay_response.get_json()
        self.assertIs(replay_payload["success"], True)
        replayed = replay_payload["session"]
        self.assertEqual(replayed["ledger"][-1]["event_type"], "replay_completed")

        fetched_response = self.client.get(
            f"/api/safebars/mirror/sessions/{session_id}"
        )
        self.assertEqual(fetched_response.status_code, 200)
        fetched_payload = fetched_response.get_json()
        self.assertIs(fetched_payload["success"], True)
        fetched = fetched_payload["session"]
        self.assertEqual(fetched["revisions"], replayed["revisions"])
        self.assertEqual(fetched["ledger"], replayed["ledger"])

    def test_errors_use_the_public_error_envelope(self):
        missing_plan = self.client.post(
            "/api/safebars/mirror/sessions",
            json={
                "title": "Incomplete",
                "research_plan": "",
                "value_commitments": ["Preserve autonomy"],
            },
        )
        self.assertEqual(missing_plan.status_code, 400)
        self.assertEqual(
            set(missing_plan.get_json()).intersection({"success", "error"}),
            {"success", "error"},
        )
        self.assertIs(missing_plan.get_json()["success"], False)
        self.assertTrue(missing_plan.get_json()["error"])

        unknown = self.client.get("/api/safebars/mirror/sessions/unknown")
        self.assertEqual(unknown.status_code, 404)
        self.assertIs(unknown.get_json()["success"], False)
        self.assertTrue(unknown.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
