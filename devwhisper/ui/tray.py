"""System tray icon and context menu."""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt


def create_tray_icon(is_recording: bool = False) -> QIcon:
    """Generate a clean colored circular badge icon dynamically."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    if is_recording:
        painter.setBrush(QColor("#ef4444"))  # Bright Red
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        # Inner pulse dot
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(11, 11, 10, 10)
    else:
        painter.setBrush(QColor("#3b82f6"))  # Blue
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        # Mic symbol silhouette
        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(12, 8, 8, 12, 4, 4)
        painter.drawRect(15, 20, 2, 4)
        painter.drawRect(12, 24, 8, 2)

    painter.end()
    return QIcon(pixmap)


class DevWhisperTray(QSystemTrayIcon):
    """System tray manager for background meeting surveillance and quick toggles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_idle = create_tray_icon(is_recording=False)
        self.icon_rec = create_tray_icon(is_recording=True)

        self.setIcon(self.icon_idle)
        self.setToolTip("DevWhisper — 100% Offline AI Meeting Notes")

        # Context Menu
        self.menu = QMenu()

        self.action_record = QAction("🔴 Start Recording", self)
        self.menu.addAction(self.action_record)

        self.menu.addSeparator()

        self.action_dashboard = QAction("📋 Open Dashboard", self)
        self.menu.addAction(self.action_dashboard)

        self.action_settings = QAction("⚙️ Settings", self)
        self.menu.addAction(self.action_settings)

        self.menu.addSeparator()

        self.action_quit = QAction("Quit DevWhisper", self)
        self.menu.addAction(self.action_quit)

        self.setContextMenu(self.menu)

    def set_recording(self, recording: bool):
        if recording:
            self.setIcon(self.icon_rec)
            self.setToolTip("DevWhisper — 🔴 Recording Meeting (Loopback + Mic)")
            self.action_record.setText("⏹️ Stop Recording")
        else:
            self.setIcon(self.icon_idle)
            self.setToolTip("DevWhisper — Idle (Ready to record)")
            self.action_record.setText("🔴 Start Recording")

