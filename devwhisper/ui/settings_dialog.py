"""Settings dialog for models, audio devices, gains, and hotkeys."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPushButton, QFormLayout, QGroupBox,
)
from PySide6.QtCore import Qt

from devwhisper.utils.config import AppConfig
from devwhisper.audio.devices import AudioDeviceManager


class SettingsDialog(QDialog):
    """Configuration modal for AI models and audio preferences."""

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DevWhisper Settings")
        self.setMinimumWidth(480)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # AI Models Group
        ai_group = QGroupBox("Local AI Models (Offline)")
        ai_layout = QFormLayout(ai_group)

        self.whisper_combo = QComboBox()
        self.whisper_combo.addItems(["tiny.en", "base.en", "small.en", "medium.en"])
        self.whisper_combo.setCurrentText(config.whisper_model)
        ai_layout.addRow("Whisper Model:", self.whisper_combo)

        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(config.whisper_threads)
        ai_layout.addRow("Whisper CPU Threads:", self.threads_spin)

        self.ollama_input = QLineEdit()
        self.ollama_input.setText(config.ollama_model)
        ai_layout.addRow("Ollama Model Tag:", self.ollama_input)

        layout.addWidget(ai_group)

        # Audio & Streaming Group
        audio_group = QGroupBox("Audio Capture & Gain Settings")
        audio_layout = QFormLayout(audio_group)

        self.chunk_spin = QSpinBox()
        self.chunk_spin.setRange(5, 60)
        self.chunk_spin.setValue(config.chunk_duration_sec)
        self.chunk_spin.setSuffix(" seconds")
        audio_layout.addRow("Chunk Duration:", self.chunk_spin)

        self.loopback_gain = QDoubleSpinBox()
        self.loopback_gain.setRange(0.0, 2.0)
        self.loopback_gain.setSingleStep(0.1)
        self.loopback_gain.setValue(config.loopback_gain)
        audio_layout.addRow("Remote Audio (Loopback) Gain:", self.loopback_gain)

        self.mic_gain = QDoubleSpinBox()
        self.mic_gain.setRange(0.0, 2.0)
        self.mic_gain.setSingleStep(0.1)
        self.mic_gain.setValue(config.mic_gain)
        audio_layout.addRow("Microphone Gain:", self.mic_gain)

        # List detected audio devices
        try:
            dev_mgr = AudioDeviceManager()
            lb = dev_mgr.get_default_loopback()
            mic = dev_mgr.get_default_microphone()
            dev_info = f"Loopback: {lb['name'][:30]}...\nMic: {mic['name'][:30]}..."
            dev_mgr.close()
        except Exception:
            dev_info = "Default WASAPI endpoints"

        dev_label = QLabel(dev_info)
        dev_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        audio_layout.addRow("Active Devices:", dev_label)

        layout.addWidget(audio_group)

        # Integrations Group
        integ_group = QGroupBox("Integrations & Hotkeys")
        integ_layout = QFormLayout(integ_group)

        self.auto_detect = QCheckBox("Auto-detect Google Meet and Zoom windows")
        self.auto_detect.setChecked(config.auto_detect_meetings)
        integ_layout.addRow(self.auto_detect)

        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(config.hotkey_toggle)
        integ_layout.addRow("Global Toggle Hotkey:", self.hotkey_input)

        layout.addWidget(integ_group)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self._save)
        btns.addWidget(btn_save)

        layout.addLayout(btns)

    def _save(self):
        self.config.whisper_model = self.whisper_combo.currentText()
        self.config.whisper_threads = self.threads_spin.value()
        self.config.ollama_model = self.ollama_input.text().strip() or "qwen2.5-coder:7b"
        self.config.chunk_duration_sec = self.chunk_spin.value()
        self.config.loopback_gain = self.loopback_gain.value()
        self.config.mic_gain = self.mic_gain.value()
        self.config.auto_detect_meetings = self.auto_detect.isChecked()
        self.config.hotkey_toggle = self.hotkey_input.text().strip() or "<ctrl>+<shift>+r"
        self.config.save()
        self.accept()

