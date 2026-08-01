import json
import tempfile
import unittest
from pathlib import Path

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
}


class FakeRoleProbeClient:
    active_provider_id = "test_provider"

    def __init__(self):
        self.calls = []

    @staticmethod
    def is_configured():
        return True

    def chat_with_provider_detailed(self, provider_id, messages, **kwargs):
        self.calls.append(
            {"provider_id": provider_id, "messages": messages, "kwargs": kwargs}
        )
        role_ids = [
            "direct_user",
            "affected_non_user",
            "downstream_deployer",
            "adversarial_reuser",
            "maintainer_auditor",
        ]
        return {
            "ok": True,
            "model": "test-model",
            "text": json.dumps(
                {
                    "role_probes": [
                        {
                            "agent_id": role_id,
                            "first_person_probe": (
                                f"As the {role_id}, I need a visible way to question "
                                "how this plan affects me."
                            ),
                            "consequence": (
                                f"The {role_id} may face a consequential output "
                                "without a sufficiently specific review path."
                            ),
                            "question_for_real_people": (
                                "Which part of this scenario fits or fails in practice?"
                            ),
                            "revision_lever": (
                                "Add a named checkpoint and validate it with affected people."
                            ),
                        }
                        for role_id in role_ids
                    ],
                    "cross_role_questions": [
                        "Which role has authority to stop the deployment?"
                    ],
                }
            ),
        }


class FailoverRoleProbeClient(FakeRoleProbeClient):
    active_provider_id = "malformed_provider"

    @staticmethod
    def configured_provider_summaries():
        return [
            {"id": "malformed_provider"},
            {"id": "valid_provider"},
        ]

    def chat_with_provider_detailed(self, provider_id, messages, **kwargs):
        if provider_id == "malformed_provider":
            self.calls.append(
                {"provider_id": provider_id, "messages": messages, "kwargs": kwargs}
            )
            return {
                "ok": True,
                "model": "malformed-model",
                "text": "This provider returned prose instead of the JSON contract.",
            }
        return super().chat_with_provider_detailed(provider_id, messages, **kwargs)


class MirrorEngineTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "mirror.db")
        self.engine = MirrorEngine(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_session_has_nine_literature_grounded_non_scoring_lenses(self):
        session = self.engine.create_session(SAMPLE_MIRROR_PROJECT)

        self.assertEqual(len(session["lenses"]), 9)
        self.assertEqual(len({item["id"] for item in session["lenses"]}), 9)
        self.assertIn("not an ethics score", session["boundary_notice"].lower())

        allowed_states = {"Missing", "Claimed", "Reasoned", "Action-linked"}
        for lens in session["lenses"]:
            with self.subTest(lens=lens["id"]):
                self.assertTrue(lens["label"])
                self.assertTrue(lens["prompt"])
                self.assertTrue(lens["operational_definition"])
                self.assertTrue(lens["source_ids"])
                self.assertTrue(lens["boundary"])
                self.assertIn(lens["state"], allowed_states)
                self.assertNotIn("score", lens)
                self.assertNotIn("percentage", lens)

    def test_analysis_keeps_synthetic_roles_bounded_and_edges_traceable(self):
        created = self.engine.create_session(SAMPLE_MIRROR_PROJECT)
        session = self.engine.analyze_session(created["id"], use_llm=False)

        self.assertTrue(session["scenarios"])
        self.assertTrue(session["dissonance_edges"])
        self.assertGreaterEqual(
            len({scenario["role_id"] for scenario in session["scenarios"]}),
            3,
            "The analysis should expose multiple bounded perspectives, not one chatbot voice.",
        )

        for scenario in session["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.assertIs(scenario["synthetic"], True)
                notice = scenario["boundary_notice"].lower()
                self.assertIn("synthetic", notice)
                self.assertTrue(
                    "not testimony" in notice
                    or "does not replace" in notice
                    or "not evidence of lived experience" in notice
                )

        lens_ids = {item["id"] for item in session["lenses"]}
        commitments = set(session["value_commitments"])
        for edge in session["dissonance_edges"]:
            with self.subTest(edge=edge["id"]):
                self.assertIn(edge["commitment"]["text"], commitments)
                self.assertTrue(edge["design_choice"]["passage_id"])
                self.assertTrue(edge["design_choice"]["quote"])
                self.assertTrue(edge["scenario"]["id"])
                self.assertIs(edge["scenario"]["synthetic"], True)
                self.assertTrue(edge["consequence"])
                self.assertTrue(edge["affected_party"])
                self.assertEqual(edge["status"], "open")
                self.assertIsInstance(edge["attention_required"], bool)
                self.assertEqual(
                    edge["attention_rule"],
                    "no_linked_lens_has_action_linked_evidence",
                )
                self.assertIn("not an ethics", edge["attention_basis"].lower())

                provenance = edge["provenance"]
                self.assertTrue(provenance["source_passage"]["passage_id"])
                self.assertTrue(provenance["source_passage"]["quote"])
                self.assertTrue(provenance["lens_ids"])
                self.assertTrue(provenance["literature_ids"])
                self.assertTrue(set(provenance["lens_ids"]).issubset(lens_ids))
                visual_types = {item["type"] for item in edge["visual_path"]}
                self.assertTrue(
                    {"commitment", "design", "scenario", "consequence", "choice"}.issubset(
                        visual_types
                    )
                )

    def test_pause_threshold_uses_a_distinct_monitoring_probe(self):
        value_commitment = (
            "Students should be able to understand and appeal consequential feedback."
        )
        pause_threshold = (
            "The research team will pause or redesign the app if students cannot "
            "meaningfully appeal a readiness label."
        )
        session = self.engine.create_session(
            {
                **SAMPLE_MIRROR_PROJECT,
                "value_commitments": [value_commitment, pause_threshold],
            }
        )
        agents_by_commitment = {
            edge["commitment"]["text"]: edge["scenario"]["agent_id"]
            for edge in session["dissonance_edges"]
        }

        self.assertEqual(agents_by_commitment[value_commitment], "direct_user")
        self.assertEqual(agents_by_commitment[pause_threshold], "maintainer_auditor")

    def test_attention_view_separates_focus_paths_without_an_ethics_score(self):
        value_commitment = (
            "Students should retain authorship and be able to understand, reject, "
            "and contest consequential AI feedback."
        )
        pause_condition = (
            "Readiness labels begin shaping grades or access to supervision, or some student groups "
            "are repeatedly misclassified without an effective appeal route."
        )
        pause_threshold = (
            "The research team will pause or redesign the app if " + pause_condition
        )
        research_plan = "\n\n".join(
            (
                "Research area and context\nComputer-science education in university project-design classes.",
                "Intended change\nHelp students turn an early research idea into a clearer, more feasible project proposal when individual supervision is limited.",
                "Direct users and encounter\nUndergraduate and master’s students would use the app while preparing project pitches; instructors may later view class-level feedback.",
                "AI role and decision authority\nAn LLM would retrieve related papers, generate novelty and method feedback, and attach a readiness label. It would advise rather than grade.",
                "Data and materials\nStudent project pitches, prompts, generated feedback, revision histories, clicks, and a short usefulness survey would be collected.",
                "People affected without direct use\nStudents who do not use the tool, classmates compared through the dashboard, and instructors whose attention may be directed by readiness labels could still be affected.",
                f"Researcher-authored value commitment\n{value_commitment}",
                f"Pause or redesign condition\n{pause_condition}",
            )
        )
        created = self.engine.create_session(
            {
                "title": "Guided attention-filter example",
                "research_plan": research_plan,
                "value_commitments": [value_commitment, pause_threshold],
            }
        )
        analyzed = self.engine.analyze_session(created["id"], use_llm=False)
        edges_by_agent = {
            edge["scenario"]["agent_id"]: edge
            for edge in analyzed["dissonance_edges"]
        }

        self.assertIs(edges_by_agent["direct_user"]["attention_required"], False)
        self.assertIs(edges_by_agent["maintainer_auditor"]["attention_required"], True)
        self.assertGreaterEqual(
            len(edges_by_agent["maintainer_auditor"]["attention_lens_ids"]),
            2,
        )

    def test_revision_and_replay_ledger_survives_engine_restart(self):
        created = self.engine.create_session(SAMPLE_MIRROR_PROJECT)
        analyzed = self.engine.analyze_session(created["id"], use_llm=False)
        edge = analyzed["dissonance_edges"][0]
        revised_plan = (
            SAMPLE_MIRROR_PROJECT["research_plan"].replace(
                "automatically send a weekly risk label to the lecturer",
                "show a provisional risk explanation to the learner and require "
                "their confirmation before a named lecturer reviews it",
            )
        )
        resolutions = [
            {
                "edge_id": edge["id"],
                "decision": "revise",
                "rationale": "The learner needs a contestable human checkpoint.",
            }
        ]

        revised = self.engine.add_revision(
            created["id"],
            revised_plan=revised_plan,
            resolutions=resolutions,
        )
        self.assertTrue(revised["revisions"])
        self.assertEqual(revised["revisions"][-1]["revised_plan"], revised_plan)

        restarted = MirrorEngine(db_path=self.db_path)
        persisted = restarted.get_session(created["id"])
        self.assertEqual(persisted["revisions"], revised["revisions"])
        self.assertEqual(persisted["research_plan"], SAMPLE_MIRROR_PROJECT["research_plan"])

        replayed = restarted.replay_session(created["id"])
        event_names = [item["event_type"] for item in replayed["ledger"]]
        self.assertIn("session_created", event_names)
        self.assertIn("analysis_completed", event_names)
        self.assertIn("revision_added", event_names)
        self.assertEqual(event_names[-1], "replay_completed")
        replayed_revision = replayed["revisions"][-1]
        self.assertEqual(replayed_revision["id"], revised["revisions"][-1]["id"])
        self.assertEqual(replayed_revision["revised_plan"], revised_plan)
        self.assertEqual(replayed_revision["resolutions"], resolutions)
        self.assertEqual(replayed_revision["status"], "replayed")
        self.assertTrue(replayed_revision["after_snapshot"])
        self.assertTrue(replayed_revision["replay"])
        self.assertTrue(
            all(
                item["status"] in {"open", "resolved", "transferred"}
                for item in replayed["dissonance_edges"]
            )
        )

    def test_configured_llm_enriches_bounded_roles_without_scoring_lenses(self):
        client = FakeRoleProbeClient()
        engine = MirrorEngine(db_path=self.db_path, llm_client=client)
        created = engine.create_session(SAMPLE_MIRROR_PROJECT)
        before_states = {
            lens["id"]: lens["state"] for lens in created["lenses"]
        }

        analyzed = engine.analyze_session(created["id"], use_llm=True)

        self.assertEqual(len(client.calls), 1)
        self.assertIs(analyzed["analysis_mode"]["llm_used"], True)
        self.assertEqual(
            analyzed["analysis_mode"]["execution_model"],
            "single_batched_call_with_separate_role_contracts",
        )
        self.assertIs(analyzed["analysis_mode"]["llm_affects_evidence_states"], False)
        self.assertEqual(analyzed["analysis_mode"]["role_probe_count"], 5)
        self.assertEqual(
            {lens["id"]: lens["state"] for lens in analyzed["lenses"]},
            before_states,
        )
        for scenario in analyzed["scenarios"]:
            with self.subTest(scenario=scenario["agent_id"]):
                self.assertEqual(
                    scenario["generation_mode"],
                    "llm_batched_bounded_role_probe",
                )
                self.assertTrue(scenario["deterministic_seed"])
                self.assertEqual(
                    scenario["model_enrichment"]["provider_id"], "test_provider"
                )
                self.assertIn("synthetic", scenario["boundary_notice"].lower())
                self.assertNotIn("age", scenario["first_person_probe"].lower())

    def test_llm_failover_skips_malformed_success_and_remembers_valid_provider(self):
        client = FailoverRoleProbeClient()
        engine = MirrorEngine(db_path=self.db_path, llm_client=client)
        created = engine.create_session(SAMPLE_MIRROR_PROJECT)

        analyzed = engine.analyze_session(created["id"], use_llm=True)

        self.assertIs(analyzed["analysis_mode"]["llm_used"], True)
        self.assertEqual(analyzed["analysis_mode"]["provider_id"], "valid_provider")
        self.assertEqual(
            analyzed["analysis_mode"]["provider_attempts"],
            [
                {
                    "provider_id": "malformed_provider",
                    "status": "invalid_response",
                },
                {"provider_id": "valid_provider", "status": "used"},
            ],
        )

        second = engine.create_session(
            {
                **SAMPLE_MIRROR_PROJECT,
                "title": "Second provider preference check",
            }
        )
        before_second = len(client.calls)
        second_analysis = engine.analyze_session(second["id"], use_llm=True)
        second_calls = client.calls[before_second:]

        self.assertIs(second_analysis["analysis_mode"]["llm_used"], True)
        self.assertEqual(second_calls[0]["provider_id"], "valid_provider")


if __name__ == "__main__":
    unittest.main()
