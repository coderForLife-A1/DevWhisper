"""State machine and data model for an active recording session."""
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any


class SessionState(Enum):
    IDLE = auto()
    RECORDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class MeetingSession:
    """Manages lifecycle and collected transcript segments for a meeting."""
    state: SessionState = SessionState.IDLE
    title: str = ""
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    source: str = "Manual"  # "Manual", "Zoom", "Google Meet"
    transcript_segments: List[str] = field(default_factory=list)
    full_transcript: str = ""
    extraction_result: Optional[Any] = None
    error: Optional[str] = None

    def start(self, title: str = "", source: str = "Manual"):
        self.state = SessionState.RECORDING
        self.started_at = datetime.now()
        self.ended_at = None
        self.source = source
        self.title = title or f"Meeting ({self.started_at.strftime('%b %d, %I:%M %p')})"
        self.transcript_segments = []
        self.full_transcript = ""
        self.extraction_result = None
        self.error = None

    def add_transcript_segment(self, text: str):
        cleaned = text.strip()
        if cleaned:
            self.transcript_segments.append(cleaned)
            self.full_transcript = "\n".join(self.transcript_segments)

    def stop_recording(self):
        self.state = SessionState.PROCESSING
        self.ended_at = datetime.now()

    def complete(self, result: Any):
        self.state = SessionState.COMPLETED
        self.extraction_result = result

    def fail(self, error_message: str):
        self.state = SessionState.FAILED
        self.error = error_message

    @property
    def duration_seconds(self) -> int:
        if self.started_at:
            end = self.ended_at or datetime.now()
            return max(0, int((end - self.started_at).total_seconds()))
        return 0

