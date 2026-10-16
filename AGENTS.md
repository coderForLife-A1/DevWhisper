# 🤖 AGENTS.md — Local Agent Guidance & Project Context

> **Target Audience:** Autonomous coding agents and local AI harnesses operating on this repository.

---

## 🛑 MANDATORY CONSTRAINTS & OPERATING LAWS

1. **100% OFF-GRID / ZERO-CLOUD RULE:**
   - **NO external network calls or cloud SDKs.** Do NOT introduce OpenAI, Anthropic, LangChain Cloud, or third-party cloud API dependencies.
   - All compute, inference, audio streams, and SQLite records MUST execute on `localhost` or within local memory/disk.
   - Respect strict client NDA requirements: audio and transcribed text MUST NEVER be transmitted outside the host machine.

2. **SCHEMA INTEGRITY:**
   - Output enforcement relies on **Pydantic v2** models paired with Ollama's structured JSON schema feature (`format=ExtractionResult.model_json_schema()`).
   - If you modify `ExtractionResult` or `ActionItem` models in `devwhisper/core/models.py`, ensure UI views in `devwhisper/ui/` remain aligned.

3. **CLEAN SYSTEM LIFECYCLE:**
   - Background threads (`AudioCaptureWorker`, `TranscriptionWorker`, `ExtractionWorker`) must shut down gracefully when recording stops or when the application exits.

---

## 📐 SYSTEM ARCHITECTURE OVERVIEW

```
[ Google Meet / Zoom / Speaker Audio ] ──► [ WASAPI Loopback (PyAudioWPatch) ] ─┐
                                                                                 ├─► [ Audio Mixer (numpy/scipy) ] ──► [ whisper.cpp (16kHz) ]
[ Local User Voice ] ──────────────────► [ Microphone Input (PyAudioWPatch) ] ─┘                                            │
                                                                                                                            ▼
                                                                                                                   [ Real-time Transcript ]
                                                                                                                            │
                                                                                                                            ▼
[ PySide6 UI / Tray / FTS5 DB ] ◄────────────── [ Ollama LLM (qwen2.5-coder:7b) ] ◄────────────────────────────────────────┘
```

---

## 📁 REPOSITORY MAP

```
DevWhisper/
├── AGENTS.md                       # Local agent guidance & laws
├── README.md                       # User documentation & setup
├── requirements.txt                # Python package dependencies
├── pyproject.toml                  # Python packaging configuration
├── run.py                          # Desktop application launcher
│
├── devwhisper/                     # Core application package
│   ├── app.py                      # Main coordinator & lifecycle
│   ├── core/                       # Speech-to-text & LLM extraction
│   │   ├── models.py               # Pydantic v2 schema definitions
│   │   ├── transcriber.py          # pywhispercpp wrapper (file & streaming)
│   │   └── extractor.py            # Local Ollama structured extraction
│   ├── audio/                      # Audio capture subsystem
│   │   ├── capture.py              # PyAudioWPatch loopback stream handler
│   │   ├── devices.py              # WASAPI device enumeration
│   │   └── mixer.py                # Dual-stream mixing & resampling
│   ├── engine/                     # Session state & QThread workers
│   │   ├── session.py              # MeetingSession state machine
│   │   └── workers.py              # Background capture, transcription & extraction
│   ├── storage/                    # Local SQLite persistence
│   │   └── database.py             # SQLite database with FTS5 search
│   ├── ui/                         # PySide6 desktop interface
│   │   ├── main_window.py          # Primary window container
│   │   ├── tray.py                 # System tray icon with context menu
│   │   ├── live_view.py            # Real-time transcript view with audio meter
│   │   ├── dashboard.py            # Meeting history & search vault
│   │   ├── review_view.py          # Summary, Action Items, & Email tabs
│   │   ├── settings_dialog.py      # AI models & audio configuration
│   │   └── theme.py                # Modern dark QSS theme
│   └── utils/                      # Cross-cutting utilities
│       ├── config.py               # JSON configuration management
│       ├── hotkeys.py              # Global hotkeys (Ctrl+Shift+R)
│       ├── meeting_detector.py     # Meet/Zoom window title detection
│       └── export.py               # Markdown format generator
│
├── legacy/                         # Archived browser-based upload prototype
│   ├── web_app.py
│   └── index.html
└── tests/                          # Automated pytest suite
```

---

## 🧪 LOCAL DEV & TESTING COMMANDS

```bash
# 1. Run automated test suite
python -m pytest tests/ -v

# 2. Launch native desktop app
python run.py
```