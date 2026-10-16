# 🔒 DevWhisper Desktop

> **100% Offline, Privacy-First AI Meeting Notes & Task Extractor for Developers**  
> Native Windows desktop app capturing Google Meet and Zoom audio via WASAPI loopback with zero cloud dependencies.

---

## 💡 Why DevWhisper?

Standard AI meeting assistants (Otter, Fathom, Fireflies) upload audio to cloud servers. This violates client NDAs, risks proprietary IP leaks, and adds recurring token fees.

**DevWhisper operates 100% locally on your machine:**
- **Zero Cloud Leakage:** Audio and transcripts never leave `localhost` or RAM.
- **Direct Google Meet & Zoom Integration:** Captures both sides of the call (system audio loopback + microphone) using Windows WASAPI.
- **Developer-Focused Context:** Open-weight coding models (`qwen2.5-coder:7b`) extract structured technical tasks, priorities, and client emails.
- **Searchable Meeting Vault:** Local SQLite database with FTS5 full-text search across all meeting transcripts.
- **Global Hotkey & Tray App:** Lives in your Windows system tray; trigger recording anywhere via `Ctrl+Shift+R`.

---

## 🛠️ Tech Stack & Architecture

- **UI Framework:** PySide6 (Qt 6) with customized dark modern theme and system tray integration.
- **Audio Capture:** `PyAudioWPatch` (Windows WASAPI loopback + native microphone dual streaming).
- **Speech-to-Text:** `whisper.cpp` (`pywhispercpp` with local quantized models: `base.en`).
- **Local LLM Extraction:** `Ollama` serving `qwen2.5-coder:7b` with strict Pydantic v2 structured schemas.
- **Storage:** Local SQLite database with FTS5 search (`~/.devwhisper/meetings.db`).

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+** (64-bit Windows)
- **Ollama** running locally ([ollama.com](https://ollama.com))

```bash
# Pull the developer model in Ollama
ollama pull qwen2.5-coder:7b
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch DevWhisper Desktop

```bash
python run.py
```

---

## ⌨️ Global Shortcuts & Features

- **Toggle Recording:** `Ctrl + Shift + R` (Global system-wide hotkey)
- **Auto-Detection:** Automatically spots active Google Meet browser tabs and Zoom desktop meetings.
- **Review & Export:** View instant summaries, filterable action item tables, client follow-up drafts, and one-click copy to Markdown.
pip install -r requirements.txt
```

### 3. Launch DevWhisper Desktop

```bash
python run.py
```

---

## ⌨️ Global Shortcuts & Features

- **Toggle Recording:** `Ctrl + Shift + R` (Global system-wide hotkey)
- **Auto-Detection:** Automatically spots active Google Meet browser tabs and Zoom desktop meetings.
- **Review & Export:** View instant summaries, filterable action item tables, client follow-up drafts, and one-click copy to Markdown.