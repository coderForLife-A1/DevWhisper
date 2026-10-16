"""Tests for Pydantic models."""
from devwhisper.core.models import ActionItem, ExtractionResult, Priority, Assignee


def test_action_item_priority_normalization():
    item = ActionItem(
        title="Fix OAuth redirect",
        priority="high",
        assignee="dev",
        details="Inspect /api/callback",
    )
    assert item.priority == Priority.HIGH
    assert item.assignee == Assignee.DEV


def test_extraction_result_validation():
    json_data = {
        "summary": "Team discussed database migrations and frontend release.",
        "action_items": [
            {
                "title": "Run alembic upgrade",
                "priority": "High",
                "assignee": "Dev",
                "details": "Target staging first",
            }
        ],
        "client_email": "Hi Team, thanks for the sync today...",
    }
    result = ExtractionResult.model_validate(json_data)
    assert result.action_items[0].priority == Priority.HIGH
    assert len(result.action_items) == 1

