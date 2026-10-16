"""Main application window hosting Dashboard, Live View, and Review views."""
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QToolBar, QStatusBar,
    QWidget, QMessageBox,
)
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtCore import Qt

from .dashboard import DashboardView
from .live_view import LiveSessionView
from .review_view import MeetingReviewView


class MainWindow(QMainWindow):
    """Primary window container with navigation toolbar and stack views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevWhisper — Offline AI Meeting Notes")
        self.resize(1020, 700)

        # Central Stacked Widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.dashboard = DashboardView()
        self.live_view = LiveSessionView()
        self.review_view = MeetingReviewView()

        self.stack.addWidget(self.dashboard)    # Index 0
        self.stack.addWidget(self.live_view)     # Index 1
        self.stack.addWidget(self.review_view)   # Index 2

        # Top Navigation Toolbar
        toolbar = QToolBar("Main Navigation", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.nav_dashboard = QAction("📋 Dashboard", self)
        self.nav_dashboard.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        toolbar.addAction(self.nav_dashboard)

        self.nav_live = QAction("🔴 Live Recording", self)
        self.nav_live.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        toolbar.addAction(self.nav_live)

        self.nav_review = QAction("📄 Meeting Review", self)
        self.nav_review.triggered.connect(lambda: self.stack.setCurrentIndex(2))
        toolbar.addAction(self.nav_review)

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("DevWhisper Ready • 100% Offline (Ollama + whisper.cpp)")

    def show_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.show()
        self.activateWindow()

    def show_live_view(self):
        self.stack.setCurrentIndex(1)
        self.show()
        self.activateWindow()

    def show_review(self, meeting_data: dict):
        self.review_view.load_meeting(meeting_data)
        self.stack.setCurrentIndex(2)
        self.show()
        self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """Minimize to system tray on window close button."""
        event.ignore()
        self.hide()
        self.status.showMessage("DevWhisper minimized to system tray.")

