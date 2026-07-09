# DELIAH

**Digital Enhanced Local Intelligence Assistant Hub**

> A privacy-first, local AI assistant with personality, voice, and modular architecture.

DELIAH runs entirely on your machine. Your conversations never leave your computer.

---

## Getting Started

Everything you need to get DELIAH running in under 10 minutes.

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Python](https://python.org) | 3.11+ | Backend server |
| [Ollama](https://ollama.ai) | Latest | Local LLM runtime |
| [Node.js](https://nodejs.org) | 18+ | Desktop app build |
| [Rust](https://rustup.rs) | Latest | Tauri compilation |
| (Optional) [Flutter](https://flutter.dev) | 3.22+ | Android companion |

### Step 1 -- Install Ollama

Ollama runs AI models locally on your machine.

```bash
# Install Ollama (Windows)
# Download from https://ollama.ai/download

# Install Ollama (macOS / Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the models DELIAH uses
ollama pull qwen2.5:7b
ollama pull deepseek-coder:6.7b

# Verify it's running
ollama list
```

The Ollama server must be running on `http://localhost:11434` (default).

### Step 2 -- Start the Backend

```bash
# Clone the repository
git clone https://github.com/gelliello/DELIAH.git
cd DELIAH

# Install Python dependencies
pip install -r backend/requirements.txt

# Start the DELIAH server
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend is ready when you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","ollama":"connected"}
```

### Step 3 -- Run the Desktop App

Open a **new terminal** (keep the backend running):

```bash
cd apps/windows
npm install
npm run dev
```

The DELIAH desktop window will open. You should see "Connected" in the header.

> **Tip:** To build a standalone .exe for distribution:
> ```bash
> npm run tauri build
> ```
> The executable will be in `apps/windows/src-tauri/target/release/`.

### Step 4 -- (Optional) Run the Android Companion

```bash
cd apps/android
flutter pub get
flutter run
```

The Android app connects to your desktop's backend over the local network.

---

## How It All Connects

```
                    DELIAH Architecture
                    ===================

  [Ollama]  <-->  [Backend]  <-->  [Desktop App]
  localhost       localhost         localhost
  :11434          :8000             (Tauri/React)
                      |
                      +---------> [Android App]
                                   (Flutter, same network)
```

**Ollama** runs AI models locally. **DELIAH Backend** is a Python/FastAPI server that talks to Ollama and manages memory, personality, and routing. **The Desktop App** is a Tauri wrapper around a React frontend that connects to the backend. **The Android App** is a Flutter companion that connects to the backend over WiFi.

### Connection Details

| Connection | Protocol | Default Address |
|-----------|----------|----------------|
| Backend to Ollama | HTTP | `http://localhost:11434` |
| Desktop to Backend | HTTP + WebSocket | `http://localhost:8000` |
| Android to Backend | HTTP + WebSocket | `http://<your-pc-ip>:8000` |

### Finding Your PC's IP (for Android)

```bash
# Windows
ipconfig | findstr "IPv4"

# macOS / Linux
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Then in the Android app settings, enter `http://192.168.x.x:8000`.

---

## Configuration

### Backend Settings

The backend can be configured via environment variables or `.env` file:

```bash
# Create a .env file in the project root
OLLAMA_URL=http://localhost:11434
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Model Configuration

Models are configured in `backend/core/model_router.py`. Each task type uses a different model:

| Task Type | Default Model | When Used |
|-----------|--------------|-----------|
| Coding | `deepseek-coder:6.7b` | Code, debugging, programming |
| Planning | `qwen2.5:7b` | Strategy, planning, analysis |
| General | `qwen2.5:7b` | Chat, knowledge, creativity |

To use different models, edit the `model_map` in `model_router.py`:

```python
self.model_map = {
    TaskType.CODING: "your-coding-model:latest",
    TaskType.PLANNING: "your-planning-model:latest",
    TaskType.GENERAL: "your-general-model:latest",
}
```

### Personality

DELIAH's personality is defined in `backend/personality/personality.json`. You can adjust traits, tone, and behavior.

---

## Features

### Multi-LLM Routing

DELIAH automatically detects what you're asking and routes to the best model:

- **Coding tasks** (write code, debug, refactor) go to a coding-optimized model
- **Planning tasks** (strategy, brainstorming) go to a reasoning model
- **General tasks** (chat, knowledge) go to a general-purpose model

### Streaming Responses

The desktop app supports real-time streaming via WebSocket. Responses appear word by word as DELIAH thinks.

### Memory System

DELIAH remembers your conversations and preferences locally using SQLite. Nothing is sent to the cloud.

### Personality Engine

A configurable personality system that gives DELIAH a consistent character -- helpful, creative, and warm.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Server info |
| `GET` | `/health` | Health check (Ollama + backend status) |
| `POST` | `/chat` | Send a message |
| `WS` | `/ws/chat` | Streaming chat via WebSocket |
| `POST` | `/chat/clear` | Clear conversation history |
| `GET` | `/memory` | Retrieve stored memories |
| `POST` | `/memory` | Store a memory |
| `POST` | `/memory/search` | Search memories |
| `GET` | `/personality` | Get personality info |
| `GET` | `/models` | List available Ollama models |
| `GET` | `/tasks` | List managed tasks |

### Chat Request

```json
POST /chat
{
  "message": "Write a hello world in Python",
  "mode": "coding"
}
```

### Response

```json
{
  "reply": "Here is a simple hello world program...",
  "task_type": "coding",
  "model": "deepseek-coder:6.7b"
}
```

---

## Troubleshooting

**"Offline" in the app header**
- Make sure the backend is running: `python -m uvicorn backend.api.main:app --reload`
- Check `http://localhost:8000/health` in your browser

**"Backend OK, Ollama down"**
- Make sure Ollama is running: `ollama serve`
- Check `http://localhost:11434` in your browser

**Model not found errors**
- Pull the required models: `ollama pull qwen2.5:7b` and `ollama pull deepseek-coder:6.7b`

**Android can't connect**
- Make sure your PC and phone are on the same WiFi network
- Use your PC's local IP (not `localhost`)
- Check firewall settings -- port 8000 must be open

**Build errors (Desktop)**
- Make sure Rust is installed: `rustc --version`
- Make sure Node.js is installed: `node --version`
- Try: `cd apps/windows && rm -rf node_modules && npm install`

---

## Project Structure

```
DELIAH/
├── backend/
│   ├── api/              # FastAPI server (main.py)
│   ├── core/             # AI Engine, Model Router, Task Manager
│   ├── personality/      # Personality, Mood, Behavior
│   ├── memory/           # SQLite Memory Manager
│   └── voice/            # STT, TTS, Wake Word
├── apps/
│   ├── windows/          # React + Tauri Desktop App
│   │   ├── src/          # React frontend (App.tsx, App.css)
│   │   └── src-tauri/    # Tauri shell (Rust)
│   └── android/          # Flutter Companion App
├── models/               # LLM Configuration
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD (auto-builds on push)
```

---

## Development

```bash
# Backend (auto-reload)
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Desktop app (dev mode with hot reload)
cd apps/android && npm run dev

# Desktop app (production build)
cd apps/windows && npm run tauri build
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT License -- see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Ollama](https://ollama.ai) -- Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) -- Python web framework
- [Tauri](https://tauri.app) -- Desktop app framework
- [Flutter](https://flutter.dev) -- Mobile app framework
- [DeepSeek](https://deepseek.com) -- Coding models
- [Qwen](https://qwen.ai) -- General models
