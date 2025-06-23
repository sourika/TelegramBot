"""Centralized configuration module for the application.

Loads environment variables and defines project-wide constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

dotenv_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found. Check your environment variables.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Check your environment variables.")
