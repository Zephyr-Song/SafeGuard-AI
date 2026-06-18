"""
Run a small deterministic profile check for SafeBARS stakeholder presets.

This is not a psychometric validation. It checks whether the v0.1 functional
profiles trigger expected rehearsal signals in standard stress-test prompts.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.rehearsal_engine import RehearsalEngine


TEST_PLAN = {
    "title": "Community workshop on online fraud prevention",
    "goal": "Prepare older adults to identify suspicious investment messages.",
    "target_community": "Older adults in a community center",
    "planned_method": "Interviews followed by a workshop",
    "draft_materials": "Ask about financial loss and run a two-hour workshop.",
    "known_risks": "Privacy concerns, embarrassment, and distress.",
    "rehearsal_focus": "Testing interview questions and safety procedure.",
}

TEST_MESSAGES = [
    "How much money did you lose and what mistake did you make?",
    "We will record the session for analysis. Is that okay?",
    "Can I assume most people in your community would feel the same way?",
    "We want a two-hour interview plus a two-hour workshop on the same day.",
    "The university and local police support this, so participants should feel comfortable joining.",
]


def main():
    engine = RehearsalEngine()
    results = []
    for preset_id in engine.list_presets():
        session = engine.start_session({
            "research_plan": TEST_PLAN,
            "preset_id": preset_id,
            "use_llm": False,
        })
        preset_results = {
            "preset_id": preset_id,
            "stakeholder": session.stakeholder.display_name,
            "tests": [],
        }
        for message in TEST_MESSAGES:
            result = engine.add_message(session.id, message)
            response = result["response"]
            preset_results["tests"].append({
                "message": message,
                "signal": response["rehearsal_signal"],
                "flags": response["safety_flags"],
                "response_excerpt": response["text"][:280],
            })
        results.append(preset_results)

    out_dir = Path("research/chi2027/profile_checks")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "safebars_profile_check_v0.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
