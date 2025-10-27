# Telegram Group Management Bot

This repository contains a modular and extensible **Telegram group‑management bot** written in Python.  
It is designed to provide advanced administration tools, automations, fun interactions, and integrations with external services such as Google's Gemini API, translation, weather, and dictionary APIs.  
All sensitive configuration (like API keys and bot tokens) is loaded from environment variables, ensuring secrets are not hard‑coded.

## Features

- **Modular architecture** – Each command category lives in its own module under `bot/handlers`, making it easy to add new features without impacting existing ones.
- **External integrations** – Built‑in services for interacting with Google’s Gemini API (via the `google‑genai` SDK), translation APIs, weather providers, and dictionary lookups.
- **Configuration via environment** – Uses `python‑dotenv` to load environment variables from a `.env` file during development. Required values are validated at runtime.
- **Asynchronous design** – Utilizes the latest `python‑telegram‑bot` (v22.5) asynchronous framework, enabling high concurrency and responsiveness.  
  The library requires Python ≥ 3.9 and supports modern Python syntax【490573782730153†L28-L35】.
- **Robust error handling** – Comprehensive try/except blocks throughout services and handlers prevent crashes and provide useful diagnostic logs.
- **Database abstraction** – Uses SQLAlchemy (v2.0+) with an async SQLite driver to persist data such as warnings, notes, and user statistics.
- **Extensible data storage** – Static data files (compliments, jokes, quotes, roasts) live in `bot/data/` and are easy to extend.

## Getting Started

1. **Install dependencies**:

   ```sh
   python -m pip install -r requirements.txt
   ```

2. **Configure environment**:

   - Copy `.env.example` to `.env` and fill in your Telegram bot token along with any API keys you intend to use (Gemini, weather, translation, dictionary).

3. **Run the bot**:

   ```sh
   python -m bot.main
   ```

   The bot will start polling for updates. Command handlers are registered automatically based on the modules found in `bot/handlers`.

4. **Development and testing**:

   - Commands are organized by category in `bot/handlers/`. Feel free to add new modules or functions as needed.  
   - Unit tests live in the `tests/` directory. Run them via:

     ```sh
     python -m pytest
     ```

## Project Structure

```
project-root/
├── README.md              # This file
├── requirements.txt       # Dependency pinning
├── .env.example           # Example environment configuration
├── bot/                   # Main bot package
│   ├── __init__.py
│   ├── config.py          # Configuration loader
│   ├── main.py            # Entry point that initializes the bot
│   ├── handlers/          # Command handler modules
│   ├── services/          # External API integrations
│   ├── utils/             # Logging, database, helper functions
│   └── data/              # Static JSON data for fun commands
├── tests/                 # Unit tests
└── Dockerfile             # Containerization (optional)
```

## Notes

This bot is designed to be **extensible** and **configurable**. If you are deploying to production or adding sensitive features, please review and harden the error handling, rate limits, and authentication flows to suit your needs.