"""
Heuristic helper for comparing initial and revised research plans.

This script does not replace qualitative coding. It produces quick hints for
the SafeBARS pre/post plan coding framework.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


CATEGORIES = {
    "stakeholder_coverage": ["family", "caregiver", "community", "worker", "partner", "platform", "bank", "police"],
    "privacy_data": ["privacy", "record", "recording", "anonymous", "anonym", "data", "storage", "confidential"],
    "distress_safety": ["distress", "pause", "skip", "withdraw", "stop", "support", "resource", "uncomfortable"],
    "victim_blaming_reduction": ["nonjudgmental", "trustworthy", "context", "decision", "avoid blame", "blame"],
    "participant_burden": ["shorter", "break", "optional", "alternative", "burden", "accessibility", "private"],
    "consent_clarity": ["consent", "voluntary", "choice", "skip", "withdraw", "recording choice"],
    "community_benefit_followup": ["follow-up", "resource", "benefit", "take-home", "community partner", "review"],
    "trust_calibration": ["verify", "real participants", "community partners", "not evidence", "synthetic"],
    "method_feasibility": ["schedule", "staff", "language", "accessible", "recruit", "location", "time"],
}


def hits(text: str) -> Dict[str, List[str]]:
    text_lower = text.lower()
    return {
        category: [term for term in terms if term in text_lower]
        for category, terms in CATEGORIES.items()
    }


def compare(initial: str, revised: str) -> Dict[str, Dict[str, List[str]]]:
    initial_hits = hits(initial)
    revised_hits = hits(revised)
    result = {}
    for category in CATEGORIES:
        added = sorted(set(revised_hits[category]) - set(initial_hits[category]))
        retained = sorted(set(revised_hits[category]) & set(initial_hits[category]))
        result[category] = {
            "initial_hits": initial_hits[category],
            "revised_hits": revised_hits[category],
            "added_terms": added,
            "retained_terms": retained,
            "coding_hint": "possible revision" if added else "no keyword-level change",
        }
    return result


def markdown_report(participant_id: str, comparison: Dict[str, Dict[str, List[str]]]) -> str:
    lines = [
        f"# Plan Comparison Hints for {participant_id}",
        "",
        "These are heuristic hints only. Use the coding framework for final qualitative coding.",
        "",
    ]
    for category, data in comparison.items():
        lines.extend([
            f"## {category.replace('_', ' ').title()}",
            "",
            f"- Initial hits: {', '.join(data['initial_hits']) or 'none'}",
            f"- Revised hits: {', '.join(data['revised_hits']) or 'none'}",
            f"- Added terms: {', '.join(data['added_terms']) or 'none'}",
            f"- Coding hint: {data['coding_hint']}",
            "",
        ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--participant", default="PXX")
    parser.add_argument("--initial", required=True)
    parser.add_argument("--revised", required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    initial_text = Path(args.initial).read_text(encoding="utf-8")
    revised_text = Path(args.revised).read_text(encoding="utf-8")
    comparison = compare(initial_text, revised_text)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.suffix.lower() == ".json":
            out_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            out_path.write_text(markdown_report(args.participant, comparison), encoding="utf-8")
        print(out_path)
    else:
        print(markdown_report(args.participant, comparison))


if __name__ == "__main__":
    main()

