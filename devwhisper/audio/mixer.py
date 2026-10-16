"""Resampling and dual-stream mixing utilities."""
from math import gcd
from typing import Optional
import numpy as np
from scipy.signal import resample_poly


def resample_audio(audio: np.ndarray, from_rate: int, to_rate: int = 16000) -> np.ndarray:
    """Resample 1D float32 audio to target sample rate using rational polyphase resampling."""
    if audio is None or len(audio) == 0:
        return np.array([], dtype=np.float32)
    if from_rate == to_rate:
        return audio.astype(np.float32)
    
    g = gcd(int(from_rate), int(to_rate))
    up = int(to_rate // g)
    down = int(from_rate // g)
    
    resampled = resample_poly(audio, up, down).astype(np.float32)
    return resampled


def mix_streams(
    loopback: Optional[np.ndarray],
    microphone: Optional[np.ndarray],
    loopback_gain: float = 0.7,
    mic_gain: float = 0.3,
) -> Optional[np.ndarray]:
    """Mix loopback (remote meeting voice) and microphone (local user) audio.
    
    Both inputs must already be resampled to 16kHz mono float32.
    """
    if (loopback is None or len(loopback) == 0) and (microphone is None or len(microphone) == 0):
        return None

    if loopback is None or len(loopback) == 0:
        return np.clip(microphone * mic_gain, -1.0, 1.0).astype(np.float32)

    if microphone is None or len(microphone) == 0:
        return np.clip(loopback * loopback_gain, -1.0, 1.0).astype(np.float32)

    max_len = max(len(loopback), len(microphone))
    lb = np.pad(loopback, (0, max_len - len(loopback)), mode="constant")
    mc = np.pad(microphone, (0, max_len - len(microphone)), mode="constant")

    mixed = (lb * loopback_gain) + (mc * mic_gain)
    return np.clip(mixed, -1.0, 1.0).astype(np.float32)

