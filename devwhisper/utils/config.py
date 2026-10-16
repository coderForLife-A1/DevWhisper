"""Application configuration manager."""
import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_DIR = Path.home() / ".devwhisper"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "whisper_model": "base.en",
    "whisper_threads": 6,
    "ollama_model": "qwen2.5-coder:7b",
    "hotkey_toggle": "<ctrl>+<shift>+r",
    "loopback_gain": 0.7,
    "mic_gain": 0.3,
    "chunk_duration_sec": 10,  # 10s gives great responsiveness for live transcript
    "auto_detect_meetings": True,
}


@dataclass
class AppConfig:
    whisper_model: str = DEFAULTS["whisper_model"]
    whisper_threads: int = DEFAULTS["whisper_threads"]
    ollama_model: str = DEFAULTS["ollama_model"]
    hotkey_toggle: str = DEFAULTS["hotkey_toggle"]
    loopback_gain: float = DEFAULTS["loopback_gain"]
    mic_gain: float = DEFAULTS["mic_gain"]
    chunk_duration_sec: int = DEFAULTS["chunk_duration_sec"]
    auto_detect_meetings: bool = DEFAULTS["auto_detect_meetings"]

    @classmethod
    def load(cls) -> "AppConfig":
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**{k: data.get(k, v) for k, v in DEFAULTS.items()})
            except Exception:
                pass
        config = cls()
        config.save()
        return config

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

