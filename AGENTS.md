# 🤖 AGENTS.md — Local Agent Guidance & Project Context

> **Target Audience:** Autonomous coding agents, local LLM harnesses, and AI IDE assistants (Cursor, Windsurf, Claude Code, Ollama/vLLM agents) operating on this repository.

---

## 🛑 MANDATORY CONSTRAINTS & OPERATING LAWS

1. **100% OFF-GRID / ZERO-CLOUD RULE:**
   - **NO external network calls or cloud SDKs.** Do NOT introduce OpenAI, Anthropic, LangChain Cloud, or third-party cloud API dependencies.
   - All compute, inference, and data processing MUST execute on `localhost` or within local memory/disk.
   - Respect strict client NDA requirements: audio and transcribed text MUST NEVER be transmitted outside the host machine.

2. **SCHEMA INTEGRITY:**
   - Output enforcement relies on **Pydantic v2** models paired with Ollama's structured JSON schema feature (`format=ExtractionResult.model_json_schema()`).
   - If you modify `ExtractionResult` or `ActionItem` models in `extractor.py`, you **MUST** update the frontend schema handling in `index.html` to prevent parser breakdowns.

3. **CLEAN SYSTEM LIFECYCLE:**
   - Always ensure temporary audio streams (`temp_*`) generated during API processing are deleted in a `finally` block in `app.py`. Do not leave stray media files on the local filesystem.

---

## 📐 SYSTEM ARCHITECTURE OVERVIEW

DevWhisper uses a decoupled four-tier local execution stack:

[ Frontend: index.html ]
│
│ HTTP POST (Multipart Audio Upload)
▼
[ Local API: app.py (FastAPI @ localhost:8000) ]
│
├───► [ Speech-to-Text: transcriber.py (pywhispercpp / C++ Base) ]
│           │
│           ▼ Timestamped Transcript String
│
└───► [ LLM Extraction: extractor.py (Ollama / qwen2.5-coder:7b) ]
│
▼ Validated Pydantic JSON Payload

---

## 📁 REPOSITORY MAP

DevWhisper/
├── AGENTS.md          # Context & instructions for AI agents
├── .gitignore          # Prevents committing local audio, venv, and binary weights
├── README.md           # Human-facing installation and usage instructions
├── requirements.txt    # Frozen Python dependencies
├── app.py              # FastAPI server orchestrating the local pipeline
├── transcriber.py      # AudioTranscriber class wrapping pywhispercpp
├── extractor.py        # Ollama interface & Pydantic structured extraction logic
└── index.html          # Lightweight TailwindCSS single-page dashboard

---

## 🛠️ CORE COMPONENT SPECIFICATIONS

### 1. `transcriber.py`
- Uses `pywhispercpp` with the `base.en` model.
- Converts audio files (`.wav`, `.mp3`, `.m4a`) into timestamped strings (`[0.0s] text...`).
- **Agent Rule:** Keep C++ whisper configuration optimized for local thread execution.

### 2. `extractor.py`
- Interfaces with local `ollama` serving `qwen2.5-coder:7b` (or `llama-3.2-3b`).
- Enforces strict JSON output via Pydantic:
  - `summary`: Brief overview of the technical call.
  - `action_items`: Array of objects containing `title`, `priority` (High/Med/Low), `assignee` (Dev/Client/Unassigned), and `details`.
  - `client_email`: Markdown draft of a client follow-up email.
- **Agent Rule:** Maintain system prompts that prioritize technical developer context (API endpoints, frameworks, git tasks) over generic business summaries.

### 3. `app.py`
- Serves endpoint `POST /api/process`.
- Manages local file buffers and coordinates transcription + LLM parsing sequentially.
- **Agent Rule:** Keep CORS configured for `127.0.0.1` / `localhost` only.

### 4. `index.html`
- Standalone HTML5 dashboard styled with TailwindCSS.
- Direct upload interface to local API; renders copyable Markdown email text and formatted task JSON.

---

## 🧪 LOCAL DEV & TESTING COMMANDS

```bash
# 1. Ensure Ollama is active with the correct coding model
ollama pull qwen2.5-coder:7b

# 2. Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Start local API server
python app.py

# 4. Run isolated module tests
python transcriber.py
python extractor.py