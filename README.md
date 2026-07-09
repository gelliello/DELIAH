# DELIAH

**Digital Enhanced Local Intelligence Assistant Hub**

> A privacy-first, local AI assistant with personality, voice, and modular architecture.

---

## Overview

DELIAH is a personal AI assistant that runs entirely on your machine. It combines the intelligence of modern LLMs with local processing, ensuring your data never leaves your device.

### Features

- **Privacy First** - All processing happens locally on your machine
- **Multi-LLM Support** - Specialized models for coding, planning, and general tasks
- **Intelligent Routing** - Automatic task detection and model selection
- **Personality Engine** - A unique AI personality with mood and behavior systems
- **Memory System** - Local SQLite-based memory that remembers your preferences
- **Voice Support** - Speech-to-text and text-to-speech capabilities
- **Plugin System** - Extensible architecture for custom integrations
- **Desktop + Mobile** - Windows desktop app with Android companion

---

## Architecture

```
Desktop (Windows)
├── React + TypeScript UI
├── Tauri Shell
│
DELIAH Core (Python)
├── FastAPI Server
├── AI Engine (Ollama)
├── Model Router
├── Personality Engine
├── Memory Manager (SQLite)
├── Voice Pipeline
│
Android Companion
├── Flutter App
└── Remote API Connection
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Ollama installed and running
- Node.js 20+
- (Optional) Flutter 3.22+ for Android

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Pull recommended models
ollama pull qwen2.5:7b
ollama pull deepseek-coder:6.7b

# Start the server
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Desktop App Setup

```bash
cd apps/windows
npm install
npm run dev
```

### Android Setup

```bash
cd apps/android
flutter pub get
flutter run
```

---

## Multi-LLM System

DELIAH automatically routes requests to the best model:

| Mode | Use Case | Recommended Models |
|------|----------|-------------------|
| **Coding** | Programming, debugging, code reviews | DeepSeek Coder, Qwen Coder |
| **Planning** | Strategy, project planning, analysis | Qwen, DeepSeek Reasoning |
| **General** | Conversations, knowledge, creativity | Qwen, Llama, Mistral |

### Manual Mode Selection

Prefix your message with a mode tag:

```
[coding] Write a Python web scraper
[planning] Design a microservice architecture
[general] Explain quantum computing
```

---

## Personality Engine

DELIAH has a unique personality system:

- **Traits**: Helpful, creative, curious, humorous, calm, friendly
- **Mood**: Dynamically adjusts based on conversation context
- **Behavior**: Adapts communication style to the situation
- **Identity**: Consistent character across all interactions

Configuration: `backend/personality/personality.json`

---

## Memory System

DELIAH remembers everything locally:

- **Conversations** - Chat history and context
- **Preferences** - Your settings and likes
- **Projects** - Important project information
- **Knowledge** - Facts and learned information

All stored in SQLite. No cloud. No data leaks.

---

## Voice Pipeline

```
Microphone → Speech-to-Text → DELIAH Core → Text-to-Speech → Speaker
```

### Supported Engines

| Component | Online | Offline |
|-----------|--------|---------|
| Speech-to-Text | Whisper API | Whisper (local) |
| Text-to-Speech | ElevenLabs | Piper TTS |
| Wake Word | - | OpenWakeWord |

---

## Plugin System

Extend DELIAH with plugins:

- Minecraft Integration
- Discord Bot
- Arduino Control
- Smart Home
- OBS Control
- Music Player
- Developer Tools

See `plugins/` for examples.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Server info |
| GET | `/health` | Health check |
| POST | `/chat` | Send message |
| WS | `/ws/chat` | Streaming chat |
| GET | `/memory` | Get memories |
| POST | `/memory` | Store memory |
| GET | `/personality` | Get personality info |
| GET | `/models` | List available models |
| GET | `/tasks` | List tasks |

---

## Project Structure

```
DELIAH/
├── backend/
│   ├── core/          # AI Engine, Model Router, Task Manager
│   ├── personality/   # Personality, Mood, Behavior
│   ├── memory/        # SQLite Memory Manager
│   ├── voice/         # STT, TTS, Wake Word
│   └── api/           # FastAPI Server
├── apps/
│   ├── windows/       # React + Tauri Desktop App
│   └── android/       # Flutter Companion App
├── models/            # LLM Configuration
├── plugins/           # Plugin System
├── docs/              # Documentation
└── .github/workflows/ # CI/CD
```

---

## Development Roadmap

### Phase 1 - Core
- FastAPI server
- Ollama integration
- Basic chat
- Memory system

### Phase 2 - Desktop
- React UI
- Model selection
- System dashboard

### Phase 3 - Personality
- Character system
- Memory rules
- Behavior adaptation

### Phase 4 - Voice
- Speech recognition
- ElevenLabs integration
- Wake word detection

### Phase 5 - Mobile
- Flutter companion app
- Desktop connection

### Phase 6 - Plugins
- Arduino integration
- Minecraft mod
- Streaming tools
- Smart home

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Tauri](https://tauri.app) - Desktop app framework
- [Flutter](https://flutter.dev) - Mobile app framework
- [DeepSeek](https://deepseek.com) - Coding models
- [Qwen](https://qwen.ai) - General models
