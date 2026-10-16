"""Tests for SQLite persistence and full-text search."""
import pytest
from pathlib import Path
from devwhisper.storage.database import MeetingDatabase
from devwhisper.engine.session import MeetingSession
from devwhisper.core.models import ExtractionResult, ActionItem, Priority, Assignee


@pytest.fixture
def test_db(tmp_path: Path):
    db_file = tmp_path / "test_meetings.db"
    db = MeetingDatabase(db_file)
    yield db
    db.close()


def test_save_and_retrieve_meeting(test_db: MeetingDatabase):
    session = MeetingSession()
    session.start(title="Sprint Planning Meeting", source="Zoom")
    session.add_transcript_segment("[0.0s] Alice: We are deploying the auth service today.")
    session.add_transcript_segment("[5.2s] Bob: Yes, the Docker containers are ready.")
    session.stop_recording()

    extraction = ExtractionResult(
        summary="Sprint deployment sync.",
        action_items=[
            ActionItem(
                title="Deploy containers",
                priority=Priority.HIGH,
                assignee=Assignee.DEV,
                details="Push to AWS ECS",
            )
        ],
        client_email="Team is ready for release.",
    )
    session.complete(extraction)

    meeting_id = test_db.save_meeting(session)
    assert meeting_id > 0

    detail = test_db.get_meeting_detail(meeting_id)
    assert detail is not None
    assert detail["title"] == "Sprint Planning Meeting"
    assert "Alice: We are deploying" in detail["transcript"]
    assert len(detail["action_items"]) == 1
    assert detail["action_items"][0]["title"] == "Deploy containers"


def test_fts5_search(test_db: MeetingDatabase):
    s1 = MeetingSession()
    s1.start(title="Architecture Sync", source="Google Meet")
    s1.add_transcript_segment("Discussing Kubernetes ingress controller configuration and TLS certs.")
    s1.stop_recording()
    test_db.save_meeting(s1)

    s2 = MeetingSession()
    s2.start(title="Marketing Catchup", source="Zoom")
    s2.add_transcript_segment("Discussing quarterly revenue and social media campaigns.")
    s2.stop_recording()
    test_db.save_meeting(s2)

    results = test_db.search_transcripts("Kubernetes")
    assert len(results) == 1
    assert results[0]["title"] == "Architecture Sync"

