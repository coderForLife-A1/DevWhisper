"""Real-time live session transcript and volume view."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QPushButton, QProgressBar,
)
from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtGui import QFont


class LiveSessionView(QWidget):
    """Displays real-time incoming meeting audio transcript and session status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._elapsed_seconds = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick_timer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Info
        header = QHBoxLayout()
        self.status_label = QLabel("🔴 Live Recording Session")
        self.status_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #ef4444;")
        header.addWidget(self.status_label)

        header.addStretch()

        self.source_badge = QLabel("WASAPI Loopback + Mic")
        self.source_badge.setStyleSheet(
            "background-color: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 4px; border: 1px solid #334155; font-size: 11px;"
        )
        header.addWidget(self.source_badge)

        self.duration_label = QLabel("00:00")
        self.duration_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.duration_label.setStyleSheet("color: #f8fafc;")
        header.addWidget(self.duration_label)

        layout.addLayout(header)

        # Volume / Audio Activity Meter
        meter_layout = QHBoxLayout()
        meter_label = QLabel("Audio Activity:")
        meter_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        meter_layout.addWidget(meter_label)

        self.audio_meter = QProgressBar()
        self.audio_meter.setRange(0, 100)
        self.audio_meter.setValue(0)
        self.audio_meter.setFixedHeight(6)
        self.audio_meter.setTextVisible(False)
        meter_layout.addWidget(self.audio_meter)
        layout.addLayout(meter_layout)

        # Real-time Transcript Area
        self.transcript_area = QTextEdit()
        self.transcript_area.setReadOnly(True)
        self.transcript_area.setFont(QFont("Consolas", 11))
        self.transcript_area.setPlaceholderText(
            "Listening to meeting audio... Transcripts from whisper.cpp will stream in real-time here."
        )
        layout.addWidget(self.transcript_area)

        # Controls
        controls = QHBoxLayout()
        self.hint_label = QLabel("💡 Press Ctrl+Shift+R or click Stop to finish and extract tasks.")
        self.hint_label.setStyleSheet("color: #64748b; font-style: italic;")
        controls.addWidget(self.hint_label)

        controls.addStretch()

        self.btn_stop = QPushButton("⏹️ Stop & Extract Notes")
        self.btn_stop.setObjectName("btnDanger")
        self.btn_stop.setMinimumHeight(38)
        controls.addWidget(self.btn_stop)

        layout.addLayout(controls)

    def start_session(self, title: str, source: str):
        self.status_label.setText(f"🔴 Live: {title}")
        self.source_badge.setText(f"Source: {source}")
        self.transcript_area.clear()
        self._elapsed_seconds = 0
        self.duration_label.setText("00:00")
        self._timer.start()

    def stop_session(self):
        self._timer.stop()
        self.audio_meter.setValue(0)
        self.status_label.setText("⏳ Extracting Structured Notes with Ollama...")
        self.status_label.setStyleSheet("color: #eab308;")

    def _tick_timer(self):
        self._elapsed_seconds += 1
        mins, secs = divmod(self._elapsed_seconds, 60)
        self.duration_label.setText(f"{mins:02d}:{secs:02d}")

    @Slot(str)
    def append_transcript(self, text: str):
        cleaned = text.strip()
        if cleaned:
            self.transcript_area.append(cleaned)
            scrollbar = self.transcript_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    @Slot(float)
    def set_audio_level(self, level: float):
        self.audio_meter.setValue(int(min(1.0, max(0.0, level)) * 100))

