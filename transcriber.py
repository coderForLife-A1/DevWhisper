# transcriber.py
import os
from pywhispercpp.model import Model

class AudioTranscriber:
    def __init__(self, model_name: str = "base.en"):
        # Auto-downloads small whisper.cpp model (ggml format) on first run
        self.model = Model(model_name, n_threads=6)

    def transcribe(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        segments = self.model.transcribe(audio_path)
        full_transcript = []
        for segment in segments:
            full_transcript.append(f"[{segment.t0/100:.1f}s] {segment.text}")
            
        return "\n".join(full_transcript)

# Quick Test
if __name__ == "__main__":
    transcriber = AudioTranscriber()
    # print(transcriber.transcribe("sample_meeting.wav"))