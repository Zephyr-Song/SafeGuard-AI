import json
import tempfile
import unittest
from pathlib import Path

from modules.encounter_engine import EncounterEngine, SAMPLE_PROJECT
from modules.llm_client import LLMProvider


class EncounterEngineTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "encounters.db"
        self.engine = EncounterEngine(db_path=str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_sample(self):
        payload = json.loads(json.dumps(SAMPLE_PROJECT))
        payload["use_llm"] = False
        return self.engine.create_session(payload)

    def test_provider_summary_does_not_expose_key_or_fingerprint(self):
        provider = LLMProvider(
            id="test",
            label="Test provider",
            api_key="secret-provider-key",
            base_url="https://example.invalid/v1",
            model="test-model",
        )

        summary = provider.public_dict()

        self.assertNotIn("api_key", summary)
        self.assertNotIn("key_hint", summary)
        self.assertNotIn("secret-provider-key", json.dumps(summary))

    def test_session_builds_nine_stage_encounter_map_and_persists(self):
        session = self.create_sample()

        self.assertEqual(len(session["encounter_map"]), 9)
        self.assertTrue(all(stage["included"] for stage in session["encounter_map"]))
        self.assertEqual(session["status"], "mapped")
        self.assertEqual(session["audit_plan"][0]["kind"], "orchestrator")
        self.assertEqual(session["audit_plan"][0]["status"], "completed")
        self.assertEqual(
            len([task for task in session["audit_plan"] if task["kind"] == "scenario"]),
            6,
        )
        self.assertTrue(all(task["tools"] for task in session["audit_plan"]))
        self.assertTrue(all(task["stop_condition"] for task in session["audit_plan"]))

        reloaded = self.engine.get_session(session["id"])
        self.assertEqual(reloaded["project"]["title"], SAMPLE_PROJECT["project"]["title"])
        self.assertEqual(reloaded["artifacts"]["interview"], SAMPLE_PROJECT["artifacts"]["interview"])

    def test_audit_produces_traces_grounded_issues_and_handoffs(self):
        session = self.create_sample()
        audited = self.engine.run_audit(
            session["id"],
            ["participant_distress", "partial_withdrawal", "institutional_distrust"],
        )

        self.assertEqual(len(audited["traces"]), 3)
        self.assertGreaterEqual(len(audited["issues"]), 1)
        self.assertGreaterEqual(len(audited["handoffs"]), 1)
        self.assertEqual(audited["status"], "audited")
        self.assertEqual(
            len({trace["uncertainty"] for trace in audited["traces"]}),
            3,
            "Each scenario should explain its own epistemic boundary.",
        )

        source_ids = {
            passage_id
            for issue in audited["issues"]
            for passage_id in issue["source_passage_ids"]
        }
        self.assertTrue(source_ids)
        self.assertTrue(all("-" in source_id for source_id in source_ids))
        self.assertTrue(all(issue["boundary_note"] for issue in audited["issues"]))
        self.assertTrue(all(len(issue["agent_positions"]) == 2 for issue in audited["issues"]))
        self.assertTrue(
            all(issue["contestation_status"] == "human_resolution_required" for issue in audited["issues"])
        )

        planned_scenarios = [
            task for task in audited["audit_plan"] if task["kind"] == "scenario"
        ]
        self.assertEqual(len(planned_scenarios), 3)
        self.assertTrue(all(task["status"] in {"completed", "paused"} for task in planned_scenarios))
        self.assertEqual(
            next(task for task in audited["audit_plan"] if task["kind"] == "boundary_handoff")["status"],
            "completed",
        )

        issues_by_id = {issue["id"]: issue for issue in audited["issues"]}
        self.assertTrue(
            any(source_id.startswith(("CON-", "SAF-", "FOL-")) for source_id in issues_by_id["issue_partial_withdrawal"]["source_passage_ids"])
        )
        self.assertFalse(
            any(source_id.startswith("REC-") for source_id in issues_by_id["issue_partial_withdrawal"]["source_passage_ids"])
        )

    def test_decision_is_recorded_in_ledger_and_event_log(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        issue = audited["issues"][0]

        decided = self.engine.record_decision(
            session["id"],
            issue["id"],
            "defer",
            "A safeguarding advisor needs to check the local referral route.",
            "Add a named local support contact after partner review.",
        )

        saved_issue = next(item for item in decided["issues"] if item["id"] == issue["id"])
        self.assertEqual(saved_issue["decision"], "defer")
        self.assertIn("safeguarding advisor", saved_issue["decision_rationale"])
        self.assertEqual(decided["event_log"][-1]["event_type"], "issue_decision")

    def test_llm_handoff_boundaries_are_contextual_and_not_severity_labels(self):
        psychological = self.engine._llm_boundary_explanation(
            "Lack of psychological support protocol",
            "psychological_safety",
            "research psychologist or mental health professional",
        )
        data_protection = self.engine._llm_boundary_explanation(
            "Insufficient data protection measures",
            "data_protection",
            "data protection officer or IT security specialist",
        )

        self.assertIn("psychological support", psychological)
        self.assertIn("access, storage, retention, and deletion", data_protection)
        self.assertNotEqual(psychological, data_protection)
        self.assertNotIn(psychological.strip().lower(), {"high", "medium", "low"})
        self.assertNotIn(data_protection.strip().lower(), {"high", "medium", "low"})

    def test_plan_can_be_rescoped_and_one_specialist_task_rerun(self):
        session = self.create_sample()
        planned = self.engine.update_audit_plan(
            session["id"], ["participant_distress", "partial_withdrawal"]
        )
        scenario_tasks = [task for task in planned["audit_plan"] if task["kind"] == "scenario"]
        self.assertEqual(
            [task["scenario_id"] for task in scenario_tasks],
            ["participant_distress", "partial_withdrawal"],
        )
        self.assertEqual(planned["event_log"][-1]["event_type"], "audit_plan_updated")

        audited = self.engine.run_audit(session["id"], planned["selected_scenarios"])
        task = next(
            item
            for item in audited["audit_plan"]
            if item.get("scenario_id") == "partial_withdrawal"
        )
        rerun = self.engine.rerun_task(session["id"], task["id"])
        rerun_task = next(item for item in rerun["audit_plan"] if item["id"] == task["id"])
        self.assertEqual(rerun_task["attempts"], 2)
        self.assertEqual(rerun["event_log"][-1]["event_type"], "audit_task_rerun")
        self.assertEqual(
            len([trace for trace in rerun["traces"] if trace["scenario_id"] == "partial_withdrawal"]),
            1,
        )

        issue = next(
            item for item in rerun["issues"] if item.get("trigger_trace_id") == "trace_partial_withdrawal"
        )
        self.engine.record_decision(session["id"], issue["id"], "accept", "Keep this revision.")
        with self.assertRaises(ValueError):
            self.engine.rerun_task(session["id"], task["id"])
        with self.assertRaises(ValueError):
            self.engine.update_audit_plan(session["id"], ["partial_withdrawal"])

    def test_handoff_routes_to_expert_and_records_review(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        handoff = next(
            item for item in audited["handoffs"] if item["issue_id"] == "issue_partial_withdrawal"
        )
        issue = next(item for item in audited["issues"] if item["id"] == handoff["issue_id"])
        reviewed_passage_id = issue["source_passage_ids"][0]
        self.assertEqual(handoff["recommended_role"], "ethics_board")
        self.assertEqual(handoff["priority"], "high")
        self.assertTrue(handoff["triage_factors"])

        reviewed = self.engine.review_handoff(
            session_id=session["id"],
            handoff_id=handoff["id"],
            action="advise",
            reviewer_role="ethics_board",
            reviewer_name="School ethics advisor",
            advice="Clarify the deletion limit and the latest point at which withdrawal remains possible.",
            rationale="The current text does not distinguish raw recordings from de-identified extracts.",
            advice_type="required_change",
            responsible_actor="Principal investigator",
            closure_evidence="A revised withdrawal paragraph names the deletion boundary and responsible contact.",
            reviewed_passage_ids=[reviewed_passage_id],
        )
        saved = next(item for item in reviewed["handoffs"] if item["id"] == handoff["id"])
        self.assertEqual(saved["status"], "advised")
        self.assertEqual(saved["assigned_role"], "ethics_board")
        self.assertEqual(saved["assigned_reviewer_name"], "School ethics advisor")
        self.assertIn("deletion limit", saved["expert_advice"])
        self.assertEqual(saved["advice_type"], "required_change")
        self.assertEqual(saved["responsible_actor"], "Principal investigator")
        self.assertIn("withdrawal paragraph", saved["closure_evidence"])
        self.assertEqual(saved["reviewed_passage_ids"], [reviewed_passage_id])
        self.assertTrue(saved["evidence_reviewed"])
        self.assertEqual(len(saved["review_history"]), 1)
        self.assertEqual(saved["review_history"][0]["advice_type"], "required_change")
        self.assertEqual(
            saved["review_history"][0]["reviewed_passage_ids"],
            [reviewed_passage_id],
        )
        self.assertEqual(reviewed["event_log"][-1]["event_type"], "expert_handoff_review")

        summary = self.engine.expert_summary(session["id"])
        self.assertEqual(summary["counts"]["advised"], 1)
        self.assertTrue(summary["queue"][0]["closure_record_complete"])
        self.assertFalse(summary["queue"][0]["legacy_resolution"])
        self.assertEqual(summary["queue"][0]["issue"]["title"], handoff["question"].removeprefix("How should the project address: ").removesuffix("?"))

    def test_required_change_cannot_close_until_researcher_responds(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        handoff = next(
            item for item in audited["handoffs"] if item["issue_id"] == "issue_partial_withdrawal"
        )
        issue = next(item for item in audited["issues"] if item["id"] == handoff["issue_id"])
        reviewed_passage_id = issue["source_passage_ids"][0]
        structured_review = {
            "session_id": session["id"],
            "handoff_id": handoff["id"],
            "reviewer_role": "ethics_board",
            "reviewer_name": "School ethics advisor",
            "advice": "Revise the withdrawal procedure before recruitment begins.",
            "rationale": "Participants need a clear and usable boundary for deletion requests.",
            "advice_type": "required_change",
            "responsible_actor": "Principal investigator",
            "closure_evidence": "A revised protocol paragraph states the deadline, contact, and deletion process.",
            "reviewed_passage_ids": [reviewed_passage_id],
        }

        with self.assertRaisesRegex(ValueError, "evidence would be sufficient"):
            self.engine.review_handoff(
                **{
                    **structured_review,
                    "action": "advise",
                    "closure_evidence": "",
                }
            )
        unchanged = self.engine.get_session(session["id"])
        unchanged_handoff = next(
            item for item in unchanged["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(unchanged_handoff["status"], "open")
        self.assertEqual(unchanged_handoff["review_history"], [])

        with self.assertRaisesRegex(ValueError, "unknown protocol passage"):
            self.engine.review_handoff(
                **{
                    **structured_review,
                    "action": "advise",
                    "reviewed_passage_ids": ["CON-999"],
                }
            )
        unchanged = self.engine.get_session(session["id"])
        unchanged_handoff = next(
            item for item in unchanged["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(unchanged_handoff["status"], "open")
        self.assertEqual(unchanged_handoff["review_history"], [])

        advised = self.engine.review_handoff(**structured_review, action="advise")
        advised_handoff = next(
            item for item in advised["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(advised_handoff["status"], "advised")

        with self.assertRaisesRegex(ValueError, "has not responded"):
            self.engine.review_handoff(**structured_review, action="resolve")
        still_open = self.engine.get_session(session["id"])
        still_open_handoff = next(
            item for item in still_open["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(still_open_handoff["status"], "advised")
        self.assertEqual(len(still_open_handoff["review_history"]), 1)
        self.assertFalse(still_open_handoff["resolved_at"])

        responded = self.engine.respond_to_handoff(
            session["id"],
            handoff["id"],
            "The deletion deadline, responsible contact, and confirmation step are now explicit.",
            "Participants may request deletion until anonymised analysis begins by contacting the principal investigator.",
        )
        responded_handoff = next(
            item for item in responded["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(responded_handoff["status"], "researcher_revised")

        resolved = self.engine.review_handoff(**structured_review, action="resolve")
        resolved_handoff = next(
            item for item in resolved["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(resolved_handoff["status"], "resolved")
        self.assertTrue(resolved_handoff["resolved_at"])
        self.assertEqual(len(resolved_handoff["review_history"]), 2)

        summary = self.engine.expert_summary(session["id"])
        saved_summary = next(
            item for item in summary["queue"] if item["id"] == handoff["id"]
        )
        self.assertTrue(saved_summary["closure_record_complete"])
        self.assertFalse(saved_summary["legacy_resolution"])
        self.assertEqual(summary["counts"]["resolved"], 1)
        self.assertEqual(summary["counts"]["unresolved"], 0)

    def test_legacy_resolved_handoff_remains_closed_but_is_flagged(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        legacy_handoff = audited["handoffs"][0]
        legacy_handoff["status"] = "resolved"
        legacy_handoff["resolved_at"] = "2025-01-01T00:00:00+00:00"
        legacy_handoff["expert_advice"] = "Legacy advice recorded before structured closure fields existed."
        legacy_handoff["expert_rationale"] = "Legacy ethical rationale retained for the audit trail."
        legacy_handoff["review_history"] = [
            {
                "action": "resolve",
                "reviewer_role": "ethics_board",
                "reviewer_name": "Legacy reviewer",
                "advice": legacy_handoff["expert_advice"],
                "rationale": legacy_handoff["expert_rationale"],
                "timestamp": "2025-01-01T00:00:00+00:00",
            }
        ]
        for field in (
            "advice_type",
            "advice_type_label",
            "responsible_actor",
            "closure_evidence",
            "reviewed_passage_ids",
            "evidence_gap_acknowledged",
            "evidence_reviewed",
            "evidence_reviewed_at",
        ):
            legacy_handoff.pop(field, None)
        self.engine.store.save(audited)

        reloaded = self.engine.get_session(session["id"])
        reloaded_handoff = next(
            item for item in reloaded["handoffs"] if item["id"] == legacy_handoff["id"]
        )
        self.assertEqual(reloaded_handoff["status"], "resolved")
        self.assertEqual(reloaded_handoff["review_history"][0]["action"], "resolve")

        summary = self.engine.expert_summary(session["id"])
        legacy_summary = next(
            item for item in summary["queue"] if item["id"] == legacy_handoff["id"]
        )
        self.assertEqual(legacy_summary["status"], "resolved")
        self.assertFalse(legacy_summary["closure_record_complete"])
        self.assertTrue(legacy_summary["legacy_resolution"])
        self.assertEqual(summary["counts"]["resolved"], 1)
        self.assertEqual(summary["counts"]["unresolved"], 0)

    def test_redirect_and_reopen_ignore_non_substantive_draft_fields(self):
        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        handoff = next(
            item for item in audited["handoffs"] if item["issue_id"] == "issue_partial_withdrawal"
        )
        issue = next(item for item in audited["issues"] if item["id"] == handoff["issue_id"])
        reviewed_passage_id = issue["source_passage_ids"][0]
        original_advice = (
            "Keep a named deletion contact and make the withdrawal deadline easy to locate."
        )
        original_rationale = (
            "A visible contact supports participant control without adding unnecessary collection."
        )
        original_actor = "Principal investigator"
        original_closure_evidence = (
            "The final protocol names the contact and shows the deletion deadline."
        )
        advised = self.engine.review_handoff(
            session_id=session["id"],
            handoff_id=handoff["id"],
            action="advise",
            reviewer_role="ethics_board",
            reviewer_name="School ethics advisor",
            advice_type="optional_recommendation",
            advice=original_advice,
            rationale=original_rationale,
            responsible_actor=original_actor,
            closure_evidence=original_closure_evidence,
            reviewed_passage_ids=[reviewed_passage_id],
        )
        advised_handoff = next(
            item for item in advised["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(len(advised_handoff["review_history"]), 1)

        redirected = self.engine.review_handoff(
            session_id=session["id"],
            handoff_id=handoff["id"],
            action="redirect",
            reviewer_role="ethics_board",
            reviewer_name="School ethics advisor",
            redirect_role="data_governance",
            advice_type="required_change",
            advice="half draft",
            rationale="unfinished",
            responsible_actor="TBD",
            closure_evidence="not final",
            reviewed_passage_ids=[reviewed_passage_id],
        )
        redirected_handoff = next(
            item for item in redirected["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(redirected_handoff["status"], "redirected")
        self.assertEqual(redirected_handoff["expert_advice"], original_advice)
        self.assertEqual(redirected_handoff["expert_rationale"], original_rationale)
        self.assertEqual(
            redirected_handoff["advice_type"],
            "optional_recommendation",
        )
        self.assertEqual(redirected_handoff["responsible_actor"], original_actor)
        self.assertEqual(
            redirected_handoff["closure_evidence"],
            original_closure_evidence,
        )
        redirect_event = redirected_handoff["review_history"][-1]
        self.assertEqual(redirect_event["action"], "redirect")
        for draft_field in (
            "advice",
            "rationale",
            "advice_type",
            "responsible_actor",
            "closure_evidence",
            "reviewed_passage_ids",
        ):
            self.assertNotIn(draft_field, redirect_event)

        resolved = self.engine.review_handoff(
            session_id=session["id"],
            handoff_id=handoff["id"],
            action="resolve",
            reviewer_role="data_governance",
            reviewer_name="Data protection reviewer",
        )
        resolved_handoff = next(
            item for item in resolved["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(resolved_handoff["status"], "resolved")

        reopened = self.engine.review_handoff(
            session_id=session["id"],
            handoff_id=handoff["id"],
            action="reopen",
            reviewer_role="data_governance",
            reviewer_name="Data protection reviewer",
            advice_type="required_change",
            advice="different half draft",
            rationale="still unfinished",
            responsible_actor="Unknown",
            closure_evidence="draft only",
            reviewed_passage_ids=[reviewed_passage_id],
        )
        reopened_handoff = next(
            item for item in reopened["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(reopened_handoff["status"], "open")
        self.assertEqual(reopened_handoff["expert_advice"], original_advice)
        self.assertEqual(reopened_handoff["expert_rationale"], original_rationale)
        self.assertEqual(reopened_handoff["advice_type"], "optional_recommendation")
        self.assertEqual(reopened_handoff["responsible_actor"], original_actor)
        self.assertEqual(
            reopened_handoff["closure_evidence"],
            original_closure_evidence,
        )
        self.assertEqual(reopened_handoff["reviewed_passage_ids"], [])
        self.assertFalse(reopened_handoff["evidence_reviewed"])
        reopen_event = reopened_handoff["review_history"][-1]
        self.assertEqual(reopen_event["action"], "reopen")
        for draft_field in (
            "advice",
            "rationale",
            "advice_type",
            "responsible_actor",
            "closure_evidence",
            "reviewed_passage_ids",
        ):
            self.assertNotIn(draft_field, reopen_event)

    def test_mixed_z_and_offset_timestamps_use_chronological_order(self):
        earlier_z = "2025-01-01T10:00:00Z"
        later_offset = "2025-01-01T10:00:00.500000+00:00"
        researcher_response_at = "2025-01-01T10:00:00.750000Z"
        evidence_reviewed_at = "2025-01-01T10:00:01+00:00"
        self.assertEqual(
            self.engine._latest_timestamp([earlier_z, later_offset]),
            later_offset,
        )
        self.assertTrue(
            self.engine._timestamp_after(researcher_response_at, later_offset)
        )
        self.assertTrue(
            self.engine._timestamp_at_or_after(
                evidence_reviewed_at,
                researcher_response_at,
            )
        )

        session = self.create_sample()
        audited = self.engine.run_audit(session["id"], ["partial_withdrawal"])
        handoff = next(
            item for item in audited["handoffs"] if item["issue_id"] == "issue_partial_withdrawal"
        )
        issue = next(item for item in audited["issues"] if item["id"] == handoff["issue_id"])
        reviewed_passage_id = issue["source_passage_ids"][0]
        structured_review = {
            "session_id": session["id"],
            "handoff_id": handoff["id"],
            "reviewer_role": "ethics_board",
            "reviewer_name": "School ethics advisor",
            "advice_type": "required_change",
            "advice": "Revise the withdrawal procedure before recruitment begins.",
            "rationale": "Participants need a clear and usable boundary for deletion requests.",
            "responsible_actor": "Principal investigator",
            "closure_evidence": (
                "A revised protocol paragraph states the deadline, contact, and deletion process."
            ),
            "reviewed_passage_ids": [reviewed_passage_id],
        }
        advised = self.engine.review_handoff(**structured_review, action="advise")
        saved_handoff = next(
            item for item in advised["handoffs"] if item["id"] == handoff["id"]
        )
        saved_handoff["review_history"][0]["timestamp"] = earlier_z
        saved_handoff["review_history"].append(
            {
                **saved_handoff["review_history"][0],
                "timestamp": later_offset,
            }
        )
        saved_handoff["researcher_response"] = "The requested revision is now in the protocol."
        saved_handoff["researcher_revised_text"] = (
            "Participants may request deletion until anonymised analysis begins."
        )
        saved_handoff["researcher_responded_at"] = researcher_response_at
        saved_handoff["status"] = "researcher_revised"
        saved_handoff["evidence_reviewed"] = True
        saved_handoff["evidence_reviewed_at"] = evidence_reviewed_at
        saved_handoff["reviewed_passage_ids"] = [reviewed_passage_id]
        self.engine.store.save(advised)

        before_close = self.engine.expert_summary(session["id"])
        summary_handoff = next(
            item for item in before_close["queue"] if item["id"] == handoff["id"]
        )
        self.assertTrue(summary_handoff["evidence_review_current"])
        self.assertTrue(summary_handoff["closure_record_complete"])

        resolved = self.engine.review_handoff(
            session_id=session["id"],
            handoff_id=handoff["id"],
            action="resolve",
            reviewer_role="ethics_board",
            reviewer_name="School ethics advisor",
        )
        resolved_handoff = next(
            item for item in resolved["handoffs"] if item["id"] == handoff["id"]
        )
        self.assertEqual(resolved_handoff["status"], "resolved")


    def test_update_tradeoff_deliberations_validates_and_persists(self):
        session = self.create_sample()

        # Happy path: valid positions + rationale are stored.
        updated = self.engine.update_tradeoff_deliberations(
            session["id"],
            [
                {"id": "recruitment_reach", "value": 72, "rationale": "Broader access is justified by community need."},
                {"id": "data_richness_privacy", "value": 40, "rationale": "Minimize identifiable data for this sensitive topic."},
            ],
        )
        stored = updated["tradeoff_deliberations"]
        self.assertEqual(stored["recruitment_reach"]["value"], 72)
        self.assertEqual(
            stored["recruitment_reach"]["rationale"],
            "Broader access is justified by community need.",
        )
        # Persisted to the store, not only in memory.
        reloaded = self.engine.get_session(session["id"])
        self.assertEqual(
            reloaded["tradeoff_deliberations"]["data_richness_privacy"]["value"], 40
        )

    def test_update_tradeoff_deliberations_rejects_invalid_values(self):
        session = self.create_sample()

        # Out-of-range positions are rejected with a clear error.
        with self.assertRaises(ValueError):
            self.engine.update_tradeoff_deliberations(
                session["id"], [{"id": "recruitment_reach", "value": 150}]
            )
        with self.assertRaises(ValueError):
            self.engine.update_tradeoff_deliberations(
                session["id"], [{"id": "recruitment_reach", "value": -5}]
            )

        # Submitting only unrecognized trade-off ids is rejected because the
        # deliberation would record nothing.
        with self.assertRaises(ValueError):
            self.engine.update_tradeoff_deliberations(
                session["id"], [{"id": "not_a_real_tradeoff", "value": 50}]
            )

        # A recognized id among others is kept; the bad id is ignored and a
        # valid deliberation is still saved.
        updated = self.engine.update_tradeoff_deliberations(
            session["id"],
            [
                {"id": "recruitment_reach", "value": 60},
                {"id": "ghost_tradeoff", "value": 99},
            ],
        )
        self.assertIn("recruitment_reach", updated["tradeoff_deliberations"])
        self.assertNotIn("ghost_tradeoff", updated["tradeoff_deliberations"])

    def test_update_tradeoff_deliberations_caps_rationale_length(self):
        session = self.create_sample()
        updated = self.engine.update_tradeoff_deliberations(
            session["id"],
            [{"id": "recruitment_reach", "value": 50, "rationale": "x" * 5000}],
        )
        self.assertEqual(
            len(updated["tradeoff_deliberations"]["recruitment_reach"]["rationale"]), 2000
        )


if __name__ == "__main__":
    unittest.main()
