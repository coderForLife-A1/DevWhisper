<div align="center">

# DevWhisper

### Private meeting intelligence for developers

Capture meeting audio, generate a live transcript, and turn technical conversations into structured notes — locally on Windows.

<p>
  <a href="#-features">Features</a> ·
  <a href="#-quick-start">Quick start</a> ·
  <a href="#-how-it-works">How it works</a> ·
  <a href="#-configuration">Configuration</a> ·
  <a href="#-development">Development</a>
</p>

![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-2563eb?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-16a34a?style=flat-square)
![Privacy](https://img.shields.io/badge/AI-local--only-7c3aed?style=flat-square)

</div>

> **Privacy is the product.** DevWhisper is designed for sensitive engineering discussions, client calls, and internal meetings where audio and transcripts should stay on your machine.

## ✨ Features

- **Local audio capture** — Mixes system audio through WASAPI loopback with microphone input.
- **Live transcription** — Uses whisper.cpp through `pywhispercpp` for responsive, on-device speech-to-text.
- **Structured meeting notes** — Uses a local Ollama model to extract a summary, prioritized action items, assignees, and a client follow-up email.
- **Meeting vault** — Stores meetings in local SQLite with FTS5 full-text search.
- **Windows-native workflow** — PySide6 desktop UI, system tray controls, global recording shortcut, and optional Zoom/Google Meet window detection.
- **Export-ready results** — Copy formatted notes or client email content from the review view.

## 🔒 Privacy and local execution

DevWhisper does not require a hosted AI account or cloud API. The application uses:

| Component | Local technology |
| --- | --- |
| System and microphone audio | PyAudioWPatch + Windows WASAPI |
| Speech-to-text | whisper.cpp via `pywhispercpp` |
| Note extraction | Ollama + Pydantic structured output |
| Meeting history | SQLite + FTS5 |
| Desktop interface | PySide6 |

Audio, transcripts, extracted notes, and configuration are kept on the local computer. Ollama must be running locally; no remote Ollama endpoint is configured by the application.

> **Important:** Local processing does not replace consent or your organization’s recording policy. Follow applicable laws and tell meeting participants when recording.

## 🚀 Quick start

### Prerequisites

- Windows 10 or Windows 11 (64-bit)
- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- A working microphone and Windows playback device

### 1. Install the local extraction model

```powershell
ollama pull qwen2.5-coder:7b
```

You can select another installed Ollama model later in the app settings.

### 2. Create an environment and install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands from an activated environment or use:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Launch DevWhisper

```powershell
python run.py
```

DevWhisper starts in the Windows system tray. Use **Ctrl + Shift + R** to start or stop recording.

> **First run:** `pywhispercpp` may download the configured whisper.cpp model (`base.en`) when the transcriber is initialized. Keep the machine online for that setup step, then use the application locally.

## 🎙️ How to use it

1. Start DevWhisper; it will remain available from the system tray.
2. Join a Zoom call or Google Meet, or start a manual session.
3. Press **Ctrl + Shift + R**, or use **Start recording** from the tray/dashboard.
4. Monitor the live transcript and audio level in the live view.
5. Stop recording when the meeting ends.
6. Wait for local Ollama extraction, then review the summary and action items.
7. Search previous meetings or copy the generated Markdown/email output.

### Controls

| Action | Default control |
| --- | --- |
| Toggle recording | `Ctrl + Shift + R` |
| Open dashboard | System tray → **Dashboard** |
| Open settings | System tray → **Settings** |
| Search meetings | Dashboard search field |
| Review notes | Select a meeting from the dashboard |

## 🧭 How it works

```text
System audio ─┐
              ├─> WASAPI capture ─> mix/resample to 16 kHz ─> whisper.cpp
Microphone ───┘                                      │
                                                     ▼
                                             Live transcript
                                                     │
                                                     ▼
                                      Local Ollama structured extraction
                                                     │
                                                     ▼
                                        SQLite meeting vault + UI review
```

The application runs capture, transcription, and extraction in background workers so the desktop interface remains responsive. Audio is mixed locally before transcription; the extraction schema is validated with Pydantic.

## ⚙️ Configuration

DevWhisper creates its local configuration under:

```text
%USERPROFILE%\.devwhisper\config.json
```

Defaults include:

| Setting | Default |
| --- | --- |
| Whisper model | `base.en` |
| Whisper threads | `6` |
| Ollama model | `qwen2.5-coder:7b` |
| Loopback gain | `0.7` |
| Microphone gain | `0.3` |
| Audio chunk duration | `10` seconds |
| Meeting detection | Enabled |

Meeting history is stored in the local SQLite database at `%USERPROFILE%\.devwhisper\meetings.db`.

## 🧰 Troubleshooting

**No audio is captured**

- Confirm Windows has the correct default playback and microphone devices.
- Check that the microphone is available to desktop applications in Windows privacy settings.
- Stop other applications that may exclusively control the audio device.

**Ollama extraction fails**

- Confirm Ollama is running with `ollama list`.
- Confirm the configured model exists with `ollama list`, or pull it with `ollama pull <model>`.
- The transcript is still saved when extraction cannot complete.

**The global shortcut does not work**

- Check the configured shortcut in Settings.
- Close another application that may be capturing `Ctrl + Shift + R`.

## 🗂️ Project layout

```text
DevWhisper/
├── devwhisper/
│   ├── audio/       # WASAPI loopback, microphone capture, and mixing
│   ├── core/        # Transcription, extraction, and Pydantic models
│   ├── engine/      # Session state and background workers
│   ├── storage/     # SQLite persistence and FTS5 search
│   ├── ui/          # PySide6 views, tray, and theme
│   └── utils/       # Configuration, hotkeys, export, and detection
├── tests/            # Automated tests
├── run.py            # Desktop launcher
├── requirements.txt  # Runtime and test dependencies
└── pyproject.toml    # Package metadata and console script
```

## 🧪 Development

Run the test suite:

```powershell
python -m pytest tests/ -v
```

Run the installed console entry point:

```powershell
devwhisper
```

For contributors, keep changes local-first and preserve the application’s graceful worker shutdown behavior. See [`AGENTS.md`](AGENTS.md) for repository-specific engineering guidance.

## 📄 License

DevWhisper is distributed under the [MIT License](LICENSE).
