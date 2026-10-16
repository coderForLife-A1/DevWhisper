"""SQLite storage for meeting history, transcripts, and action items."""
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = Path.home() / ".devwhisper" / "meetings.db"


class MeetingDatabase:
    """Manages SQLite storage and full-text search for DevWhisper sessions."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self._conn:
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds INTEGER DEFAULT 0,
                    source TEXT DEFAULT 'Manual',
                    audio_path TEXT,
                    status TEXT DEFAULT 'completed'
                );

                CREATE TABLE IF NOT EXISTS transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
                    full_text TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
                    summary TEXT NOT NULL,
                    client_email TEXT NOT NULL,
                    extracted_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extraction_id INTEGER NOT NULL REFERENCES extractions(id) ON DELETE CASCADE,
                    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    assignee TEXT NOT NULL,
                    details TEXT,
                    completed INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_meetings_started
                    ON meetings(started_at DESC);

                CREATE VIRTUAL TABLE IF NOT EXISTS transcript_fts
                    USING fts5(full_text, content=transcripts, content_rowid=id);
            """)

    def save_meeting(self, session) -> int:
        """Persist a completed meeting session and return its database ID."""
        with self._conn:
            cur = self._conn.execute(
                """INSERT INTO meetings
                   (title, started_at, ended_at, duration_seconds, source, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    session.title,
                    session.started_at.isoformat() if session.started_at else datetime.now().isoformat(),
                    session.ended_at.isoformat() if session.ended_at else None,
                    session.duration_seconds or 0,
                    session.source,
                    session.state.name.lower(),
                ),
            )
            meeting_id = cur.lastrowid

            # Save full transcript
            t_cur = self._conn.execute(
                "INSERT INTO transcripts (meeting_id, full_text) VALUES (?, ?)",
                (meeting_id, session.full_transcript or ""),
            )
            transcript_id = t_cur.lastrowid

            # Update FTS index
            if session.full_transcript:
                self._conn.execute(
                    "INSERT INTO transcript_fts(rowid, full_text) VALUES (?, ?)",
                    (transcript_id, session.full_transcript),
                )

            # Save extraction if available
            if session.extraction_result:
                ext = session.extraction_result
                e_cur = self._conn.execute(
                    """INSERT INTO extractions (meeting_id, summary, client_email)
                       VALUES (?, ?, ?)""",
                    (meeting_id, ext.summary, ext.client_email),
                )
                ext_id = e_cur.lastrowid

                for item in ext.action_items:
                    p_val = item.priority.value if hasattr(item.priority, "value") else str(item.priority)
                    a_val = item.assignee.value if hasattr(item.assignee, "value") else str(item.assignee)
                    self._conn.execute(
                        """INSERT INTO action_items
                           (extraction_id, meeting_id, title, priority, assignee, details)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (ext_id, meeting_id, item.title, p_val, a_val, item.details),
                    )

            return meeting_id

    def get_all_meetings(self) -> List[Dict[str, Any]]:
        """Retrieve all meetings sorted by start time descending."""
        rows = self._conn.execute(
            "SELECT * FROM meetings ORDER BY started_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_meeting_detail(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve detailed meeting record with transcript and action items."""
        row = self._conn.execute(
            "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
        ).fetchone()
        if not row:
            return None
        
        meeting = dict(row)

        t_row = self._conn.execute(
            "SELECT full_text FROM transcripts WHERE meeting_id = ?", (meeting_id,)
        ).fetchone()
        meeting["transcript"] = t_row["full_text"] if t_row else ""

        e_row = self._conn.execute(
            "SELECT id, summary, client_email FROM extractions WHERE meeting_id = ?", (meeting_id,)
        ).fetchone()
        if e_row:
            meeting["summary"] = e_row["summary"]
            meeting["client_email"] = e_row["client_email"]
            items = self._conn.execute(
                "SELECT title, priority, assignee, details, completed FROM action_items WHERE extraction_id = ?",
                (e_row["id"],),
            ).fetchall()
            meeting["action_items"] = [dict(i) for i in items]
        else:
            meeting["summary"] = ""
            meeting["client_email"] = ""
            meeting["action_items"] = []

        return meeting

    def search_transcripts(self, query: str) -> List[Dict[str, Any]]:
        """Search across transcripts using SQLite FTS5."""
        if not query.strip():
            return self.get_all_meetings()
        
        # Clean query for FTS5
        clean_q = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
        if not clean_q:
            return []
        
        rows = self._conn.execute(
            """SELECT m.id, m.title, m.started_at, m.duration_seconds, m.source,
                      snippet(transcript_fts, 0, '<b>', '</b>', '...', 16) as snippet
               FROM transcript_fts
               JOIN transcripts t ON t.id = transcript_fts.rowid
               JOIN meetings m ON m.id = t.meeting_id
               WHERE transcript_fts MATCH ?
               ORDER BY rank""",
            (f"{clean_q}*",),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_meeting(self, meeting_id: int):
        with self._conn:
            self._conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))

    def close(self):
        self._conn.close()

