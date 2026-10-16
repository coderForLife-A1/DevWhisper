"""Background QThread workers for audio capture, transcription, and extraction."""
import time
from typing import Optional
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QThread

from devwhisper.audio.capture import AudioStream
from devwhisper.audio.mixer import mix_streams, resample_audio
from devwhisper.core.transcriber import AudioTranscriber
from devwhisper.core.extractor import process_transcript


class AudioCaptureWorker(QObject):
    """Continuously pulls from loopback and mic streams, mixes them, and emits 16kHz chunks."""

    chunk_ready = Signal(np.ndarray)
    audio_level = Signal(float)  # RMS level for UI meter
    error = Signal(str)

    SAMPLE_RATE = 16000

    def __init__(
        self,
        loopback_stream: Optional[AudioStream],
        mic_stream: Optional[AudioStream],
        chunk_duration_sec: int = 10,
        loopback_gain: float = 0.7,
        mic_gain: float = 0.3,
    ):
        super().__init__()
        self._loopback = loopback_stream
        self._mic = mic_stream
        self._chunk_duration = chunk_duration_sec
        self._loopback_gain = loopback_gain
        self._mic_gain = mic_gain
        self._is_running = False
        self._buffer = np.array([], dtype=np.float32)

    @Slot()
    def run(self):
        self._is_running = True
        try:
            if self._loopback:
                self._loopback.start()
            if self._mic:
                self._mic.start()
        except Exception as e:
            self.error.emit(f"Failed to start audio streams: {e}")
            return

        chunk_size = self.SAMPLE_RATE * self._chunk_duration

        while self._is_running:
            try:
                lb_data = self._loopback.read_available() if self._loopback else None
                mic_data = self._mic.read_available() if self._mic else None

                # Resample to 16kHz
                if lb_data is not None and len(lb_data) > 0:
                    lb_data = resample_audio(lb_data, self._loopback.native_rate, self.SAMPLE_RATE)
                if mic_data is not None and len(mic_data) > 0:
                    mic_data = resample_audio(mic_data, self._mic.native_rate, self.SAMPLE_RATE)

                mixed = mix_streams(lb_data, mic_data, self._loopback_gain, self._mic_gain)
                if mixed is not None and len(mixed) > 0:
                    self._buffer = np.concatenate([self._buffer, mixed])
                    
                    # Compute RMS volume metric
                    rms = float(np.sqrt(np.mean(mixed**2)))
                    self.audio_level.emit(min(1.0, rms * 5.0))

                # When buffer exceeds chunk duration, emit chunk
                if len(self._buffer) >= chunk_size:
                    chunk = self._buffer[:chunk_size]
                    self._buffer = self._buffer[chunk_size:]
                    self.chunk_ready.emit(chunk)

                QThread.msleep(80)

            except Exception as e:
                self.error.emit(f"Audio capture worker exception: {e}")
                break

    @Slot()
    def stop(self):
        self._is_running = False
        if self._loopback:
            self._loopback.stop()
        if self._mic:
            self._mic.stop()

        # Emit whatever remainder is in the buffer if > 1s of speech
        if len(self._buffer) >= self.SAMPLE_RATE:
            self.chunk_ready.emit(self._buffer)
        self._buffer = np.array([], dtype=np.float32)


class TranscriptionWorker(QObject):
    """Processes audio chunks through whisper.cpp."""

    transcript_segment = Signal(str)
    error = Signal(str)

    def __init__(self, model_name: str = "base.en", n_threads: int = 6):
        super().__init__()
        self._model_name = model_name
        self._n_threads = n_threads
        self._transcriber: Optional[AudioTranscriber] = None

    def _init_model(self):
        if self._transcriber is None:
            self._transcriber = AudioTranscriber(self._model_name, self._n_threads)

    @Slot(np.ndarray)
    def transcribe_chunk(self, audio_chunk: np.ndarray):
        try:
            self._init_model()
            text = self._transcriber.transcribe_array(audio_chunk)
            if text.strip():
                self.transcript_segment.emit(text)
        except Exception as e:
            self.error.emit(f"Transcription error: {e}")


class ExtractionWorker(QObject):
    """Invokes local Ollama LLM to extract tasks and summary."""

    extraction_done = Signal(object)
    error = Signal(str)

    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        super().__init__()
        self._model_name = model_name

    @Slot(str)
    def extract(self, full_transcript: str):
        if not full_transcript.strip():
            self.error.emit("Transcript is empty. Nothing to extract.")
            return

        try:
            result = process_transcript(full_transcript, self._model_name)
            self.extraction_done.emit(result)
        except Exception as e:
            self.error.emit(f"Extraction failed: {e}")

