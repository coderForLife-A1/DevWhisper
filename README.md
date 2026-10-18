# 🔒 DevWhisper Desktop

> **100% Offline, Privacy-First AI Meeting Notes & Task Extractor for Developers**  
> Native Windows desktop app capturing Google Meet and Zoom audio via WASAPI loopback with zero cloud dependencies.

---

## 💡 Why DevWhisper?

Standard AI meeting assistants (Otter, Fathom, Fireflies) upload sensitive client audio recordings to third-party cloud servers. This violates client NDAs, risks proprietary IP leaks, and incurs recurring token fees.

**DevWhisper keeps 100% of execution on your local machine:**
- **Zero Cloud Leakage:** Audio streams and transcripts never leave `localhost` or system RAM.
- **Direct Google Meet & Zoom Capture:** Records both sides of the call simultaneously (system speaker audio via WASAPI loopback + your microphone) without needing meeting bots or invite permissions.
- **Developer-Focused Context:** Open-weight coding models (`qwen2.5-coder:7b`) extract structured technical tasks, priority tags, assignees, and client email drafts instead of generic chatter.
- **Searchable Meeting Vault:** Local SQLite database with FTS5 full-text search across all meeting transcripts.
- **Always-Available System Tray App:** Runs quietly in the background; start or stop recording anywhere via `Ctrl + Shift + R`.

---

## 📐 System Architecture

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

## 🛠️ Tech Stack

- **Desktop GUI:** [PySide6](https://pypi.org/project/PySide6/) (Qt 6) with dark modern theme, system tray integration, and custom SVG/QPainter icons.
- **Audio Capture & DSP:** [PyAudioWPatch](https://pypi.org/project/PyAudioWPatch/) (WASAPI loopback + microphone capture), [NumPy](https://numpy.org/), and [SciPy](https://scipy.org/) (rational polyphase resampling to 16kHz mono).
- **Speech-to-Text:** [whisper.cpp](https://github.com/ggerganov/whisper.cpp) via [pywhispercpp](https://pypi.org/project/pywhispercpp/) (`base.en` ggml quantized model).
- **Local LLM Extraction:** [Ollama](https://ollama.com/) serving `qwen2.5-coder:7b` with structured output enforced by [Pydantic v2](https://docs.pydantic.dev/).
- **Storage:** Local SQLite database with **FTS5 (Full-Text Search)** stored in `~/.devwhisper/meetings.db`.
- **System Surveillance & Hooks:** `psutil` + `pywin32` for window title detection; `pynput` for global hotkeys.

---

## 🚀 Getting Started

### Prerequisites

1. **Windows 10 / 11 (64-bit)**
2. **Python 3.10+**
3. **Ollama** installed and running locally ([Download Ollama](https://ollama.com))

### 1. Pull the Coding Model

```bash
ollama pull qwen2.5-coder:7b
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

*(Optional: If installing as an editable package)*
```bash
pip install -e .
```

### 3. Launch DevWhisper Desktop

```bash
python run.py
```
*DevWhisper will launch into your Windows System Tray (near the clock).*

---

## ⌨️ Shortcuts & How to Use

| Action | Shortcut / Trigger | Description |
|---|---|---|
| **Toggle Recording** | `Ctrl + Shift + R` | Start or stop recording from anywhere in Windows |
| **Tray Context Menu** | Right-click tray icon | Quick actions to start recording, open dashboard, or settings |
| **Live View** | Double-click tray or open window | Shows real-time auto-scrolling transcript and audio meter |
| **Auto-Detection** | Automatic background check | Detects active Zoom meetings or Google Meet browser tabs |
| **Search Vault** | Dashboard search bar | Real-time full-text search across all past transcripts |
| **Export Notes** | "Copy Markdown" / "Copy Email" | One-click copy formatted meeting notes to clipboard |

---

## 📁 Repository Structure

```
DevWhisper/
├── AGENTS.md               # Local agent guidance & zero-cloud laws
├── README.md               # Project documentation
├── requirements.txt        # Frozen dependencies
├── pyproject.toml          # Packaging configuration
├── run.py                  # Desktop application launcher
│
├── devwhisper/             # Main application package
│   ├── app.py              # Application coordinator & event wiring
│   ├── audio/              # WASAPI loopback, mic capture & dual mixer
│   ├── core/               # Models, whisper.cpp & Ollama extractor
│   ├── engine/             # Multi-threaded QThread workers & session state
│   ├── storage/            # SQLite database with FTS5 search
│   ├── ui/                 # PySide6 desktop views, system tray & theme
│   └── utils/              # Config, global hotkeys & meeting detector
│
├── legacy/                 # Archived browser-based upload prototype
└── tests/                  # Automated pytest suite
```

---

## 🧪 Testing

To run the automated test suite verifying audio mixing math, Pydantic schemas, and SQLite FTS5 persistence:

```bash
python -m pytest tests/ -v
```