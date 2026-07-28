"""Generate the frozen SafeBARS eight-sequence counterbalancing schedule.

The schedule contains pseudonymous participant codes only. It never stores
names, email addresses, recruitment contacts, or outcomes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random
from typing import Dict, List


SEQUENCES: List[Dict[str, str]] = [
    {
        "sequence_id": "S1",
        "task1_case": "A1_NON_AI",
        "task1_condition": "safebars_full",
        "task2_case": "B1_AI",
        "task2_condition": "general_chat",
    },
    {
        "sequence_id": "S2",
        "task1_case": "A1_NON_AI",
        "task1_condition": "general_chat",
        "task2_case": "B2_AI",
        "task2_condition": "safebars_full",
    },
    {
        "sequence_id": "S3",
        "task1_case": "A2_NON_AI",
        "task1_condition": "safebars_full",
        "task2_case": "B2_AI",
        "task2_condition": "general_chat",
    },
    {
        "sequence_id": "S4",
        "task1_case": "A2_NON_AI",
        "task1_condition": "general_chat",
        "task2_case": "B1_AI",
        "task2_condition": "safebars_full",
    },
    {
        "sequence_id": "S5",
        "task1_case": "B1_AI",
        "task1_condition": "safebars_full",
        "task2_case": "A1_NON_AI",
        "task2_condition": "general_chat",
    },
    {
        "sequence_id": "S6",
        "task1_case": "B1_AI",
        "task1_condition": "general_chat",
        "task2_case": "A2_NON_AI",
        "task2_condition": "safebars_full",
    },
    {
        "sequence_id": "S7",
        "task1_case": "B2_AI",
        "task1_condition": "safebars_full",
        "task2_case": "A2_NON_AI",
        "task2_condition": "general_chat",
    },
    {
        "sequence_id": "S8",
        "task1_case": "B2_AI",
        "task1_condition": "general_chat",
        "task2_case": "A1_NON_AI",
        "task2_condition": "safebars_full",
    },
]


def build_assignments(participants: int, seed: int, study_id: str) -> List[Dict[str, object]]:
    if participants < 8:
        raise ValueError("At least eight participants are required to cover every sequence.")

    sequence_ids = [
        SEQUENCES[index % len(SEQUENCES)]["sequence_id"]
        for index in range(participants)
    ]
    random.Random(seed).shuffle(sequence_ids)
    sequence_by_id = {item["sequence_id"]: item for item in SEQUENCES}

    rows: List[Dict[str, object]] = []
    for participant_number, sequence_id in enumerate(sequence_ids, start=1):
        participant_id = f"P{participant_number:03d}"
        sequence = sequence_by_id[sequence_id]
        for task_order in (1, 2):
            rows.append(
                {
                    "study_id": study_id,
                    "participant_id": participant_id,
                    "sequence_id": sequence_id,
                    "task_order": task_order,
                    "condition": sequence[f"task{task_order}_condition"],
                    "case_id": sequence[f"task{task_order}_case"],
                }
            )
    return rows


def validate_balance(rows: List[Dict[str, object]]) -> Dict[str, object]:
    by_sequence: Dict[str, int] = {}
    case_condition: Dict[str, int] = {}
    first_condition: Dict[str, int] = {}
    for row in rows:
        if row["task_order"] == 1:
            by_sequence[str(row["sequence_id"])] = (
                by_sequence.get(str(row["sequence_id"]), 0) + 1
            )
            first_condition[str(row["condition"])] = (
                first_condition.get(str(row["condition"]), 0) + 1
            )
        key = f"{row['case_id']}|{row['condition']}"
        case_condition[key] = case_condition.get(key, 0) + 1

    spread = max(by_sequence.values()) - min(by_sequence.values())
    if spread > 1:
        raise AssertionError("Sequence allocation differs by more than one participant.")

    return {
        "participant_count": len(rows) // 2,
        "task_count": len(rows),
        "sequence_counts": dict(sorted(by_sequence.items())),
        "case_condition_counts": dict(sorted(case_condition.items())),
        "first_condition_counts": dict(sorted(first_condition.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SafeBARS pseudonymous study assignments."
    )
    parser.add_argument("--participants", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--study-id", default="SB-CHI27")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/chi2027/study_materials/study_assignment_schedule.csv"
        ),
    )
    args = parser.parse_args()

    rows = build_assignments(args.participants, args.seed, args.study_id)
    balance = validate_balance(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    manifest_path = args.output.with_suffix(".manifest.json")
    manifest = {
        "study_id": args.study_id,
        "seed": args.seed,
        "schedule_file": args.output.name,
        "sequence_definitions": SEQUENCES,
        "balance": balance,
        "boundary": (
            "Pseudonymous assignment schedule only; no recruitment identity or "
            "study outcome is stored."
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output} and {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
