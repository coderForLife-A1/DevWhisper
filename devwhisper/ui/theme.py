"""Dark modern QSS styling for DevWhisper."""

DARK_THEME = """
QMainWindow, QDialog, QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}

QToolBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    padding: 6px;
    spacing: 12px;
}

QToolButton {
    background-color: #334155;
    color: #f8fafc;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
}

QToolButton:hover {
    background-color: #3b82f6;
}

QStatusBar {
    background-color: #1e293b;
    color: #94a3b8;
    border-top: 1px solid #334155;
}

QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #2563eb;
}

QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #3b82f6;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #475569;
    color: #94a3b8;
}

QPushButton#btnDanger {
    background-color: #dc2626;
}

QPushButton#btnDanger:hover {
    background-color: #b91c1c;
}

QPushButton#btnSuccess {
    background-color: #16a34a;
}

QPushButton#btnSuccess:hover {
    background-color: #15803d;
}

QTableWidget {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    gridline-color: #334155;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px;
    border: 1px solid #334155;
    font-weight: 600;
}

QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1e293b;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    border: 1px solid #334155;
    border-bottom: none;
}

QProgressBar {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    text-align: center;
    color: #f8fafc;
}

QProgressBar::chunk {
    background-color: #10b981;
    border-radius: 4px;
}

QScrollBar:vertical {
    background: #0f172a;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""

