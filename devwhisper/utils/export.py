"""Export utilities for meeting notes and transcripts."""
from typing import Dict, Any


def format_meeting_markdown(meeting_data: Dict[str, Any]) -> str:
    """Format full meeting details into clean GitHub-flavored markdown."""
    title = meeting_data.get("title", "Meeting")
    date_str = meeting_data.get("started_at", "")[:19].replace("T", " ")
    source = meeting_data.get("source", "Manual")
    summary = meeting_data.get("summary", "No summary available.")
    action_items = meeting_data.get("action_items", [])
    email = meeting_data.get("client_email", "")
    transcript = meeting_data.get("transcript", "")

    lines = [
        f"# 🎙️ {title}",
        f"**Date:** {date_str} | **Source:** {source}",
        "",
        "## 📝 Executive Summary",
        summary,
        "",
        "## ✅ Action Items",
    ]

    if not action_items:
        lines.append("_No action items recorded._")
    else:
        for idx, item in enumerate(action_items, 1):
            title_text = item.get("title", "Task")
            priority = item.get("priority", "Med")
            assignee = item.get("assignee", "Unassigned")
            details = item.get("details", "")
            lines.append(f"{idx}. **[{priority}]** {title_text} _(@{assignee})_")
            if details:
                lines.append(f"   - {details}")

    if email:
        lines.extend([
            "",
            "## 📧 Client Follow-Up Draft",
            email,
        ])

    if transcript:
        lines.extend([
            "",
            "## 📜 Timestamped Transcript",
            "```text",
            transcript,
            "```",
        ])

    return "\n".join(lines)

