"""Module for creating the main reply keyboard."""

from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard():
    keyboard = [
        ([KeyboardButton("💡 Interesting Fact"), KeyboardButton("🤖 ChatGPT")]),
        ([KeyboardButton("👥 Chat with Personality"), KeyboardButton("❓ Quiz")]),
        (
            [
                KeyboardButton("🌐 Translator"),
                KeyboardButton("🎤 Voice-to-Voice Conversations"),
            ]
        ),
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
