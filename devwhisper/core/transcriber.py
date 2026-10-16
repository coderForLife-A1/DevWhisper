"""Core speech-to-text transcriber wrapping whisper.cpp."""
import os
import numpy as np
from pywhispercpp.model import Model


class AudioTranscriber:
    def __init__(self, model_name: str = "base.en", n_threads: int = 6):
        # Auto-downloads whisper.cpp ggml model on first run if needed
        self.model = Model(model_name, n_threads=n_threads)

    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe from a file path (batch mode)."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        segments = self.model.transcribe(audio_path)
        return self._format_segments(segments)

    def transcribe_array(self, audio_data: np.ndarray) -> str:
        """Transcribe from a 16kHz mono float32 numpy array."""
        if audio_data is None or len(audio_data) == 0:
            return ""
        
        # Ensure float32 and flat
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        audio_data = audio_data.flatten()
        
        segments = self.model.transcribe(audio_data)
        return self._format_segments(segments)

    def transcribe(self, audio_path: str) -> str:
        """Backward compatibility for existing call signatures."""
        return self.transcribe_file(audio_path)

    @staticmethod
    def _format_segments(segments) -> str:
        formatted = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                # Segment t0 is in hundredths of seconds in pywhispercpp
                timestamp = f"[{segment.t0 / 100:.1f}s]"
                formatted.append(f"{timestamp} {text}")
        return "\n".join(formatted)

