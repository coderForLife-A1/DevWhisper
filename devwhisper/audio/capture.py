"""Live audio stream capture using PyAudioWPatch callbacks."""
import queue
from typing import Optional, Dict, Any
import numpy as np
import pyaudiowpatch as pyaudio

CHUNK_FRAMES = 512


class AudioStream:
    """Captures continuous audio from a WASAPI loopback or Microphone input."""

    def __init__(self, device_info: Dict[str, Any], pa_instance: pyaudio.PyAudio):
        self._pa = pa_instance
        self._device = device_info
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[pyaudio.Stream] = None
        self._is_running = False

        self._native_rate = int(device_info["defaultSampleRate"])
        self._channels = int(device_info["maxInputChannels"])

    @property
    def native_rate(self) -> int:
        return self._native_rate

    @property
    def channels(self) -> int:
        return self._channels

    @property
    def is_running(self) -> bool:
        return self._is_running

    def _callback(self, in_data, frame_count, time_info, status):
        if not self._is_running:
            return (None, pyaudio.paComplete)
        
        # Audio from pyaudio.paFloat32 is 32-bit floating point [-1.0, 1.0]
        audio = np.frombuffer(in_data, dtype=np.float32)
        if self._channels > 1:
            audio = audio.reshape(-1, self._channels).mean(axis=1)
        self._queue.put(audio)
        return (in_data, pyaudio.paContinue)

    def start(self):
        if self._is_running:
            return
        self._is_running = True
        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=self._channels,
            rate=self._native_rate,
            input=True,
            input_device_index=self._device["index"],
            frames_per_buffer=CHUNK_FRAMES,
            stream_callback=self._callback,
        )

    def stop(self):
        self._is_running = False
        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def read_available(self) -> Optional[np.ndarray]:
        """Drain queued audio blocks and return as a single contiguous array."""
        chunks = []
        while not self._queue.empty():
            try:
                chunk = self._queue.get_nowait()
                chunks.append(chunk)
            except queue.Empty:
                break
        if not chunks:
            return None
        return np.concatenate(chunks).astype(np.float32)

