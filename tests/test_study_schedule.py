from scripts.generate_safebars_study_schedule import build_assignments, validate_balance


def test_twenty_four_participant_schedule_balances_sequences_cases_and_conditions():
    rows = build_assignments(24, seed=20260727, study_id="SB-CHI27")
    balance = validate_balance(rows)

    assert len(rows) == 48
    assert balance["participant_count"] == 24
    assert set(balance["sequence_counts"].values()) == {3}
    assert set(balance["case_condition_counts"].values()) == {6}
    assert balance["first_condition_counts"] == {
        "general_chat": 12,
        "safebars_full": 12,
    }

    by_participant = {}
    for row in rows:
        by_participant.setdefault(row["participant_id"], []).append(row)

    for tasks in by_participant.values():
        assert {task["task_order"] for task in tasks} == {1, 2}
        assert {task["condition"] for task in tasks} == {
            "general_chat",
            "safebars_full",
        }
        case_ids = {task["case_id"] for task in tasks}
        assert sum(case_id.endswith("_AI") and "NON_AI" not in case_id for case_id in case_ids) == 1
        assert sum("NON_AI" in case_id for case_id in case_ids) == 1


def test_schedule_is_reproducible_for_fixed_seed():
    first = build_assignments(24, seed=1234, study_id="SB-CHI27")
    second = build_assignments(24, seed=1234, study_id="SB-CHI27")
    assert first == second
