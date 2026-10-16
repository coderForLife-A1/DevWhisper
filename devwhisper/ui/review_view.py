"""Post-meeting review view with tabs for Summary, Action Items, Email, and Transcript."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView, QApplication, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from devwhisper.utils.export import format_meeting_markdown


class MeetingReviewView(QWidget):
    """Detailed inspection of an extracted meeting session."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_data = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        self.title_label = QLabel("📄 Meeting Intelligence")
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.addWidget(self.title_label)

        header.addStretch()

        self.btn_copy_markdown = QPushButton("📋 Copy Markdown")
        self.btn_copy_markdown.clicked.connect(self._copy_markdown)
        header.addWidget(self.btn_copy_markdown)

        layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Executive Summary
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Segoe UI", 12))
        self.tabs.addTab(self.summary_text, "📝 Summary")

        # Tab 2: Action Items Table
        self.action_table = QTableWidget()
        self.action_table.setColumnCount(4)
        self.action_table.setHorizontalHeaderLabels(["Priority", "Task Title", "Assignee", "Technical Details"])
        self.action_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.action_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.action_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.action_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.action_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabs.addTab(self.action_table, "✅ Action Items")

        # Tab 3: Client Follow-up Email
        self.email_text = QTextEdit()
        self.email_text.setReadOnly(True)
        self.email_text.setFont(QFont("Segoe UI", 12))
        self.tabs.addTab(self.email_text, "📧 Client Email Draft")

        # Tab 4: Full Transcript
        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        self.transcript_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.transcript_text, "📜 Full Transcript")

        # Quick Actions Bar
        actions_bar = QHBoxLayout()
        btn_copy_email = QPushButton("✉️ Copy Client Email")
        btn_copy_email.clicked.connect(lambda: self._copy_to_clipboard(self.email_text.toPlainText(), "Email copied!"))
        actions_bar.addWidget(btn_copy_email)

        btn_copy_actions = QPushButton("📋 Copy Action Items")
        btn_copy_actions.clicked.connect(self._copy_action_items)
        actions_bar.addWidget(btn_copy_actions)

        actions_bar.addStretch()
        layout.addLayout(actions_bar)

    def load_meeting(self, data: dict):
        self._current_data = data or {}
        title = data.get("title", "Meeting Notes")
        self.title_label.setText(f"📄 {title}")

        self.summary_text.setPlainText(data.get("summary", "No summary available."))
        self.email_text.setPlainText(data.get("client_email", "No email draft generated."))
        self.transcript_text.setPlainText(data.get("transcript", "No transcript recorded."))

        # Populate action items
        items = data.get("action_items", [])
        self.action_table.setRowCount(len(items))
        for row, item in enumerate(items):
            prio = item.get("priority", "Med")
            item_prio = QTableWidgetItem(f"[{prio}]")
            if prio == "High":
                item_prio.setForeground(Qt.red)
            elif prio == "Med":
                item_prio.setForeground(Qt.yellow)
            else:
                item_prio.setForeground(Qt.green)

            self.action_table.setItem(row, 0, item_prio)
            self.action_table.setItem(row, 1, QTableWidgetItem(item.get("title", "")))
            self.action_table.setItem(row, 2, QTableWidgetItem(item.get("assignee", "Unassigned")))
            self.action_table.setItem(row, 3, QTableWidgetItem(item.get("details", "")))

    def _copy_to_clipboard(self, text: str, success_msg: str):
        if text.strip():
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", success_msg)

    def _copy_markdown(self):
        md = format_meeting_markdown(self._current_data)
        self._copy_to_clipboard(md, "Full meeting Markdown notes copied to clipboard!")

    def _copy_action_items(self):
        items = self._current_data.get("action_items", [])
        if not items:
            return
        lines = []
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. [{item.get('priority')}] {item.get('title')} (@{item.get('assignee')}): {item.get('details')}")
        self._copy_to_clipboard("\n".join(lines), "Action items copied to clipboard!")

