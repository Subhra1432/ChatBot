# ChatBot - Code & Research Assistant

A modern, dark-themed chatbot GUI built with Python + Tkinter that runs locally on your machine. Supports multiple LLM providers and web search for coding and research tasks.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- **Modern Dark UI** - Tokyo Night-inspired color scheme with clean layout
- **Multiple LLM Providers** - Groq (FREE!) and OpenAI support
- **Web Search** - DuckDuckGo integration (no API key needed)
- **URL Fetcher** - Extract text content from any webpage
- **Chat Sessions** - Multiple conversations with session switching
- **Export** - Save chats as Markdown files
- **Slash Commands** - Quick actions via `/search`, `/fetch`, `/help`
- **Conversation Memory** - Context-aware with configurable history
- **Settings Panel** - In-app configuration for API keys, models, etc.

## Quick Start (from source)

### 1. Activate the virtual environment

```bash
cd ~/Desktop/ChatBot
source venv/bin/activate
```

### 2. Run the chatbot

```bash
python chatbot.py
```

### 3. Configure API Key (first time)

1. Click **Settings** in the top bar
2. Choose a provider:
   - **Groq** (Recommended - FREE): Get a key at [console.groq.com](https://console.groq.com)
   - **OpenAI**: Get a key at [platform.openai.com](https://platform.openai.com/api-keys)
3. Paste your API key and click **Save**

---

## Build Standalone App

### macOS (.app)

```bash
cd ~/Desktop/ChatBot
source venv/bin/activate
./build.sh
```

This creates **`dist/ChatBot.app`** (~30 MB).

**To install:**
1. Drag `dist/ChatBot.app` into `/Applications/`
2. First launch: macOS may block it -> Go to **System Settings -> Privacy & Security -> Open Anyway**
3. Place `config.json` next to the app (or configure via Settings inside the app)

### Windows (.exe)

On a Windows machine:

```cmd
cd Desktop\ChatBot
build_win.bat
```

This creates **`dist\ChatBot.exe`** (single file).

**To install:**
1. Copy `dist\ChatBot.exe` anywhere you like
2. Place `config.json` in the same folder as the `.exe`
3. Double-click `ChatBot.exe` to run

> **Note:** To build for Windows, you need Python 3.11+ with tkinter installed on a Windows machine. The build script will create the venv and install dependencies automatically.

---

## Commands

| Command | Description |
|---------|-------------|
| `/search <query>` | Search the web using DuckDuckGo |
| `/fetch <url>` | Extract text from a webpage |
| `/clear` | Clear conversation history |
| `/help` | Show available commands |

## Keyboard Shortcuts

- **Enter** - Send message
- **Shift+Enter** - New line in input

## Project Structure

```
ChatBot/
|-- chatbot.py          # Main GUI application
|-- api_client.py       # API client (LLM + web search)
|-- config.json         # Configuration file (API keys, model settings)
|-- requirements.txt    # Python dependencies
|-- build.sh            # macOS build script
|-- build_win.bat       # Windows build script
|-- build_macos.spec    # PyInstaller spec (macOS)
|-- build_windows.spec  # PyInstaller spec (Windows)
|-- create_icon.py      # App icon generator
|-- assets/             # App icons (.icns, .ico, .png)
|-- venv/               # Virtual environment
|-- dist/               # Built app output (after build)
|   |-- ChatBot.app     #   macOS app bundle
|   \-- config.json     #   Runtime config
\-- README.md           # This file
```

## Supported Models

### Groq (Free Tier)
- `llama-3.3-70b-versatile` (default)
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

### OpenAI
- `gpt-4o` / `gpt-4o-mini`
- `gpt-4-turbo` / `gpt-4`
- `gpt-3.5-turbo`

## License

MIT - free for personal use.
