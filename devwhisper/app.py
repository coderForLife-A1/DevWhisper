"""DevWhisper Desktop Application bootstrap and event coordination."""
import sys
import pyaudiowpatch as pyaudio
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QThread, QTimer

from devwhisper.ui import MainWindow, DevWhisperTray, SettingsDialog, DARK_THEME
from devwhisper.utils import AppConfig, GlobalHotkeyManager, get_active_meetings
from devwhisper.storage import MeetingDatabase
from devwhisper.engine import MeetingSession, AudioCaptureWorker, TranscriptionWorker, ExtractionWorker
from devwhisper.audio import AudioDeviceManager, AudioStream


class DevWhisperApp:
    """Coordinator linking UI, audio capture, background threads, and storage."""

    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.qapp.setStyleSheet(DARK_THEME)

        self.config = AppConfig.load()
        self.db = MeetingDatabase()
        self.session = MeetingSession()

        # UI Components
        self.window = MainWindow()
        self.tray = DevWhisperTray()
        self.tray.show()

        # Audio and threads
        self.pa_instance = None
        self.audio_worker = None
        self.audio_thread = None
        self.transcribe_worker = None
        self.transcribe_thread = None
        self.extract_worker = None
        self.extract_thread = None

        # Setup meeting surveillance timer (checks for Google Meet / Zoom)
        self.detector_timer = QTimer()
        self.detector_timer.setInterval(4000)
        self.detector_timer.timeout.connect(self._check_for_meetings)
        if self.config.auto_detect_meetings:
            self.detector_timer.start()

        self._wire_signals()

        # Global hotkey
        self.hotkeys = GlobalHotkeyManager({
            self.config.hotkey_toggle: self.toggle_recording
        })
        self.hotkeys.start()

        # Initial dashboard populate
        self.refresh_dashboard()

    def _wire_signals(self):
        # Tray signals
        self.tray.action_record.triggered.connect(self.toggle_recording)
        self.tray.action_dashboard.triggered.connect(self.window.show_dashboard)
        self.tray.action_settings.triggered.connect(self.open_settings)
        self.tray.action_quit.triggered.connect(self.quit_app)

        # Dashboard signals
        self.window.dashboard.start_requested.connect(self.start_recording)
        self.window.dashboard.meeting_selected.connect(self.open_meeting_detail)
        self.window.dashboard.delete_requested.connect(self.delete_meeting)
        self.window.dashboard.search_input.textChanged.connect(self.search_meetings)

        # Live View signals
        self.window.live_view.btn_stop.clicked.connect(self.stop_recording)

    def refresh_dashboard(self):
        meetings = self.db.get_all_meetings()
        self.window.dashboard.load_meetings(meetings)

    def search_meetings(self, query: str):
        results = self.db.search_transcripts(query)
        self.window.dashboard.load_meetings(results)

    def open_meeting_detail(self, meeting_id: int):
        data = self.db.get_meeting_detail(meeting_id)
        if data:
            self.window.show_review(data)

    def delete_meeting(self, meeting_id: int):
        self.db.delete_meeting(meeting_id)
        self.refresh_dashboard()

    def open_settings(self):
        dialog = SettingsDialog(self.config, self.window)
        if dialog.exec():
            # Update hotkeys if changed
            self.hotkeys.stop()
            self.hotkeys = GlobalHotkeyManager({
                self.config.hotkey_toggle: self.toggle_recording
            })
            self.hotkeys.start()

    def toggle_recording(self):
        if self.session.state.name == "RECORDING":
            self.stop_recording()
        else:
            self.start_recording()

    def _check_for_meetings(self):
        """Auto-detect running Zoom or Google Meet sessions and notify."""
        if self.session.state.name == "RECORDING":
            return
        active = get_active_meetings()
        if active:
            first = active[0]
            # Show a discreet prompt in status bar
            self.window.status.showMessage(f"Detected {first['type']}: '{first['title'][:40]}...' (Press {self.config.hotkey_toggle} to record)")

    def start_recording(self, detected_source: str = "Manual"):
        if self.session.state.name == "RECORDING":
            return

        # Check for active meetings to auto-title
        active = get_active_meetings()
        if active and detected_source == "Manual":
            source = active[0]["type"]
            title = f"{source}: {active[0]['title'][:50]}"
        else:
            source = detected_source
            title = ""

        self.session.start(title=title, source=source)
        self.tray.set_recording(True)
        self.window.live_view.start_session(self.session.title, self.session.source)
        self.window.show_live_view()
        self.window.status.showMessage("Recording active • Capturing Loopback & Microphone")

        # Initialize audio capture
        try:
            self.pa_instance = pyaudio.PyAudio()
            dev_mgr = AudioDeviceManager()
            loopback_info = dev_mgr.get_default_loopback()
            mic_info = dev_mgr.get_default_microphone()
            dev_mgr.close()

            loopback_stream = AudioStream(loopback_info, self.pa_instance)
            mic_stream = AudioStream(mic_info, self.pa_instance)

            self.audio_worker = AudioCaptureWorker(
                loopback_stream,
                mic_stream,
                chunk_duration_sec=self.config.chunk_duration_sec,
                loopback_gain=self.config.loopback_gain,
                mic_gain=self.config.mic_gain,
            )
            self.audio_thread = QThread()
            self.audio_worker.moveToThread(self.audio_thread)
            self.audio_thread.started.connect(self.audio_worker.run)

            # Transcriber worker
            self.transcribe_worker = TranscriptionWorker(
                model_name=self.config.whisper_model,
                n_threads=self.config.whisper_threads,
            )
            self.transcribe_thread = QThread()
            self.transcribe_worker.moveToThread(self.transcribe_thread)

            # Wire streaming signals
            self.audio_worker.chunk_ready.connect(self.transcribe_worker.transcribe_chunk)
            self.audio_worker.audio_level.connect(self.window.live_view.set_audio_level)
            self.audio_worker.error.connect(lambda err: self.window.status.showMessage(f"Audio Error: {err}"))

            self.transcribe_worker.transcript_segment.connect(self.window.live_view.append_transcript)
            self.transcribe_worker.transcript_segment.connect(self.session.add_transcript_segment)
            self.transcribe_worker.error.connect(lambda err: self.window.status.showMessage(f"Whisper Error: {err}"))

            self.transcribe_thread.start()
            self.audio_thread.start()

        except Exception as e:
            self.session.fail(str(e))
            self.tray.set_recording(False)
            QMessageBox.critical(self.window, "Audio Initialization Error", str(e))

    def stop_recording(self):
        if self.session.state.name != "RECORDING":
            return

        self.tray.set_recording(False)
        self.window.live_view.stop_session()
        self.session.stop_recording()

        # Stop audio thread
        if self.audio_worker:
            self.audio_worker.stop()
        if self.audio_thread:
            self.audio_thread.quit()
            self.audio_thread.wait()
            self.audio_thread = None

        if self.transcribe_thread:
            self.transcribe_thread.quit()
            self.transcribe_thread.wait()
            self.transcribe_thread = None

        if self.pa_instance:
            self.pa_instance.terminate()
            self.pa_instance = None

        # Kick off Ollama extraction
        self.window.status.showMessage(f"Extracting notes using local Ollama ({self.config.ollama_model})...")
        self.extract_worker = ExtractionWorker(model_name=self.config.ollama_model)
        self.extract_thread = QThread()
        self.extract_worker.moveToThread(self.extract_thread)

        self.extract_thread.started.connect(
            lambda: self.extract_worker.extract(self.session.full_transcript)
        )
        self.extract_worker.extraction_done.connect(self._on_extraction_complete)
        self.extract_worker.error.connect(self._on_extraction_error)

        self.extract_thread.start()

    def _on_extraction_complete(self, result):
        if self.extract_thread:
            self.extract_thread.quit()
            self.extract_thread.wait()
            self.extract_thread = None

        self.session.complete(result)
        meeting_id = self.db.save_meeting(self.session)
        data = self.db.get_meeting_detail(meeting_id)

        self.refresh_dashboard()
        if data:
            self.window.show_review(data)
        self.window.status.showMessage("Meeting saved and processed successfully!")

    def _on_extraction_error(self, err_msg: str):
        if self.extract_thread:
            self.extract_thread.quit()
            self.extract_thread.wait()
            self.extract_thread = None

        self.session.fail(err_msg)
        # Still save whatever transcript was collected
        meeting_id = self.db.save_meeting(self.session)
        self.refresh_dashboard()
        self.window.status.showMessage(f"Extraction warning: {err_msg}")
        data = self.db.get_meeting_detail(meeting_id)
        if data:
            self.window.show_review(data)

    def quit_app(self):
        if self.session.state.name == "RECORDING":
            self.stop_recording()
        self.hotkeys.stop()
        self.detector_timer.stop()
        self.tray.hide()
        self.db.close()
        self.qapp.quit()


def main():
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    qapp.setApplicationName("DevWhisper")

    app_instance = DevWhisperApp(qapp)
    # Start minimized to tray, but show notification
    app_instance.tray.showMessage(
        "DevWhisper Active",
        f"DevWhisper is running offline in the system tray.\nPress {app_instance.config.hotkey_toggle} to record any meeting.",
        app_instance.tray.icon_idle,
        3000,
    )
    return qapp.exec()

