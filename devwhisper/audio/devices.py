"""Audio device discovery using PyAudioWPatch."""
import pyaudiowpatch as pyaudio
from typing import List, Dict, Any, Optional


class AudioDeviceManager:
    """Discovers and inspects WASAPI loopback and microphone audio devices."""

    def __init__(self):
        self._pa = pyaudio.PyAudio()

    def get_default_loopback(self) -> Dict[str, Any]:
        """Get the default WASAPI loopback device for system audio (speakers/headphones)."""
        try:
            return self._pa.get_default_wasapi_loopback()
        except OSError as e:
            raise RuntimeError(
                "WASAPI loopback not available on this system. "
                "Ensure an active audio playback output is connected."
            ) from e

    def get_default_microphone(self) -> Dict[str, Any]:
        """Get the default microphone input device."""
        try:
            return self._pa.get_default_input_device_info()
        except OSError as e:
            raise RuntimeError("No default microphone found.") from e

    def list_input_devices(self) -> List[Dict[str, Any]]:
        """List all available input devices."""
        devices = []
        for i in range(self._pa.get_device_count()):
            info = self._pa.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                devices.append(info)
        return devices

    def list_wasapi_loopback_devices(self) -> List[Dict[str, Any]]:
        """List all available WASAPI loopback devices."""
        loopbacks = []
        for i in range(self._pa.get_device_count()):
            info = self._pa.get_device_info_by_index(i)
            if info.get("isLoopbackDevice", False):
                loopbacks.append(info)
        return loopbacks

    def get_pyaudio(self) -> pyaudio.PyAudio:
        return self._pa

    def close(self):
        self._pa.terminate()

