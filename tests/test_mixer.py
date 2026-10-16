"""Tests for audio mixing and resampling math."""
import numpy as np
from devwhisper.audio.mixer import mix_streams, resample_audio


def test_resample_audio_length():
    # 1 second of 48kHz audio resampled to 16kHz
    orig_rate = 48000
    target_rate = 16000
    audio_48k = np.ones(48000, dtype=np.float32)
    resampled = resample_audio(audio_48k, orig_rate, target_rate)
    assert len(resampled) == 16000
    assert resampled.dtype == np.float32


def test_mix_streams_both_present():
    lb = np.array([0.5, 0.5, 0.5], dtype=np.float32)
    mic = np.array([0.2, 0.2, 0.2], dtype=np.float32)
    mixed = mix_streams(lb, mic, loopback_gain=0.6, mic_gain=0.4)
    # (0.5 * 0.6) + (0.2 * 0.4) = 0.30 + 0.08 = 0.38
    assert np.allclose(mixed, [0.38, 0.38, 0.38], atol=1e-5)


def test_mix_streams_handles_none():
    mic = np.array([0.5, -0.5], dtype=np.float32)
    mixed = mix_streams(None, mic, mic_gain=0.5)
    assert np.allclose(mixed, [0.25, -0.25])

    assert mix_streams(None, None) is None

