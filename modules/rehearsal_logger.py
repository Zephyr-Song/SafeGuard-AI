"""
Session export helpers for SafeBARS.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class RehearsalLogger:
    def __init__(self, data_dir: str = "data/safebars"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def export_json(self, session_data: Dict[str, Any]) -> str:
        path = os.path.join(self.data_dir, f"{session_data['id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        return path

    def export_markdown(self, session_data: Dict[str, Any], report: Dict[str, Any]) -> str:
        path = os.path.join(self.data_dir, f"{session_data['id']}.md")
        plan = session_data.get("research_plan", {})
        stakeholder = session_data.get("stakeholder", {})
        lines = [
            f"# SafeBARS Rehearsal Session {session_data['id']}",
            "",
            f"Exported: {datetime.now().isoformat()}",
            "",
            "## Limitation",
            "",
            "This synthetic stakeholder rehearsal is not participant evidence and does not represent a real community.",
            "",
            "## Research Plan",
            "",
            f"- Title: {plan.get('title', '')}",
            f"- Goal: {plan.get('goal', '')}",
            f"- Target community: {plan.get('target_community', '')}",
            f"- Planned method: {plan.get('planned_method', '')}",
            "",
            "## Stakeholder",
            "",
            f"- Role: {stakeholder.get('display_name', '')}",
            f"- Description: {stakeholder.get('description', '')}",
            "",
            "## Conversation",
            "",
        ]
        for turn in session_data.get("turns", []):
            lines.extend([f"**{turn.get('speaker', '').title()}**", "", turn.get("text", ""), ""])

        revised_plan = session_data.get("revised_plan", "")
        if revised_plan:
            lines.extend(["## Revised Research Plan", "", revised_plan, ""])

        lines.extend(["## Reflection Report", ""])
        for key, values in report.items():
            lines.extend([f"### {key.replace('_', ' ').title()}", ""])
            if isinstance(values, list):
                for item in values:
                    if isinstance(item, dict):
                        signal = item.get("signal", "note")
                        quote = item.get("quote", "")
                        interpretation = item.get("interpretation", "")
                        lines.append(f"- **{signal}**: {interpretation}")
                        if quote:
                            lines.append(f"  - Evidence: {quote}")
                    else:
                        lines.append(f"- {item}")
            else:
                lines.append(str(values))
            lines.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return path

    def export_comparison(self, comparison_data: Dict[str, Any]) -> Dict[str, str]:
        session_id = comparison_data.get("session_id", "unknown_session")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{session_id}_comparison_{timestamp}"
        json_path = os.path.join(self.data_dir, f"{base_name}.json")
        md_path = os.path.join(self.data_dir, f"{base_name}.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(comparison_data, f, ensure_ascii=False, indent=2)

        lines = [
            f"# SafeBARS Provider Comparison {base_name}",
            "",
            f"Exported: {datetime.now().isoformat()}",
            "",
            "## Limitation",
            "",
            "This provider comparison is for rehearsal and debugging. It is not participant evidence and does not validate claims about real communities.",
            "",
            "## Prompt",
            "",
            comparison_data.get("message", ""),
            "",
            "## Summary",
            "",
        ]

        summary = comparison_data.get("comparison_summary", {})
        for key, values in summary.items():
            title = key.replace("_", " ").title()
            lines.extend([f"### {title}", ""])
            if isinstance(values, list):
                if values:
                    for value in values:
                        lines.append(f"- {value}")
                else:
                    lines.append("- None")
            else:
                lines.append(str(values))
            lines.append("")

        lines.extend(["## Responses", ""])
        for response in comparison_data.get("responses", []):
            lines.extend([
                f"### {response.get('label', response.get('provider_id', 'Provider'))}",
                "",
                f"- Provider ID: {response.get('provider_id', '')}",
                f"- Model: {response.get('model', '')}",
                f"- Key hint: {response.get('key_hint', '')}",
                f"- OK: {response.get('ok', False)}",
                "",
            ])
            analysis = response.get("analysis", {})
            if analysis:
                lines.extend([
                    "Analysis:",
                    "",
                    f"- Assessment: {analysis.get('concise_assessment', '')}",
                    f"- Risk categories: {', '.join(analysis.get('risk_categories', [])) or 'None'}",
                    f"- Boundary markers: {', '.join(analysis.get('boundary_markers', [])) or 'None'}",
                    f"- Overtrust warnings: {', '.join(analysis.get('overtrust_warnings', [])) or 'None'}",
                    f"- Revision cues: {', '.join(analysis.get('useful_revision_cues', [])) or 'None'}",
                    "",
                ])
            lines.extend(["Response:", "", response.get("text", ""), ""])

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return {
            "json_path": json_path,
            "markdown_path": md_path,
        }
