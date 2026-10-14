# 🔒 DevWhisper

> **100% Offline, Privacy-First AI Meeting & Developer Task Extractor**
> Built for freelancers, agencies, and engineering consultants who deal with strict client NDAs and cannot upload sensitive audio to cloud servers.

---

## 💡 Why DevWhisper?

Standard AI meeting assistants (like Otter, Fathom, or Fireflies) upload client audio recordings to foreign cloud servers. This violates client NDAs, risks IP leaks, and incurs monthly per-token SaaS fees.

**DevWhisper solves this by keeping 100% of execution on your local machine:**
- **Zero Cloud Leakage:** Audio files stay on local disk and RAM—zero external network calls.
- **Developer-Aware Context:** Uses open-weight coding models (`Qwen2.5-Coder`) to extract technical tasks, API specs, and GitHub-ready issue definitions instead of generic meeting chatter.
- **$0 Running Cost:** Runs indefinitely on local GPUs or Apple Silicon via quantized open-source inference.

---

## 🛠️ Architecture & Tech Stack

- **Speech-to-Text:** `whisper.cpp` (via `pywhispercpp`) for low-latency local transcription.
- **Local Inference Engine:** `Ollama` serving open-weight LLMs (`qwen2.5-coder:7b` / `llama-3.2-3b`).
- **Backend Service:** FastAPI running locally on `localhost:8000`.
- **Frontend Dashboard:** Lightweight HTML5 / TailwindCSS interface.

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+** installed.
2. **Ollama** installed and running locally. Download from [ollama.com](https://ollama.com).

### 1. Pull the Local Model

```bash
ollama pull qwen2.5-coder:7b