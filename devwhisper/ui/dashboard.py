"""Dashboard view showing historic meetings and full-text search."""
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QMessageBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class DashboardView(QWidget):
    """Historical meeting log and instant search."""

    meeting_selected = Signal(int)
    start_requested = Signal()
    delete_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("📋 Meeting Intelligence Vault")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.addWidget(title)

        header.addStretch()

        self.btn_new = QPushButton("🔴 Start Recording Now")
        self.btn_new.setObjectName("btnSuccess")
        self.btn_new.clicked.connect(self.start_requested.emit)
        header.addWidget(self.btn_new)

        layout.addLayout(header)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search past meeting transcripts, topics, or action items (FTS5)...")
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Meeting Title", "Date & Time", "Duration", "Platform", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        # Footer
        footer = QHBoxLayout()
        self.count_label = QLabel("0 meetings recorded")
        self.count_label.setStyleSheet("color: #64748b; font-size: 11px;")
        footer.addWidget(self.count_label)

        footer.addStretch()

        self.btn_delete = QPushButton("🗑️ Delete Selected")
        self.btn_delete.setObjectName("btnDanger")
        self.btn_delete.clicked.connect(self._on_delete)
        footer.addWidget(self.btn_delete)

        layout.addLayout(footer)

    def load_meetings(self, meetings: List[Dict[str, Any]]):
        self.table.setRowCount(len(meetings))
        self.count_label.setText(f"{len(meetings)} meetings stored locally (100% offline)")

        for row, m in enumerate(meetings):
            item_title = QTableWidgetItem(m.get("title", "Meeting"))
            item_title.setData(Qt.ItemDataRole.UserRole, m.get("id"))
            self.table.setItem(row, 0, item_title)

            dt = m.get("started_at", "")[:16].replace("T", " ")
            self.table.setItem(row, 1, QTableWidgetItem(dt))

            dur = m.get("duration_seconds", 0) or 0
            mins, secs = divmod(dur, 60)
            self.table.setItem(row, 2, QTableWidgetItem(f"{mins}m {secs:02d}s"))

            src = m.get("source", "Manual")
            self.table.setItem(row, 3, QTableWidgetItem(src))

            status = m.get("status", "completed").capitalize()
            self.table.setItem(row, 4, QTableWidgetItem(status))

    def _on_double_click(self, index):
        row = index.row()
        item = self.table.item(row, 0)
        if item:
            mid = item.data(Qt.ItemDataRole.UserRole)
            if mid:
                self.meeting_selected.emit(int(mid))

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        mid = item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to permanently delete '{item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(int(mid))

