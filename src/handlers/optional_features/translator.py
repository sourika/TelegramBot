"""Handlers for the text translator feature (/translate command)."""

import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.chatgpt_client import ChatGPTClient
from keyboards.inline_keyboards import (
    get_language_keyboard,
    get_translate_keyboard,
    TARGET_LANGUAGES,
)


logger = logging.getLogger(__name__)
chatgpt_client = ChatGPTClient()
CHOOSE_LANGUAGE, TRANSLATING = 7, 8


async def start_translate_handler(update: Update, _context: CallbackContext) -> int:
    """Starts the translation dialogue, prompts to select a language."""
    message_to_handle = update.effective_message
    if not message_to_handle:
        return ConversationHandler.END

    language_keyboard = get_language_keyboard()
    await message_to_handle.reply_text(
        "Select the language to translate to:", reply_markup=language_keyboard
    )
    return CHOOSE_LANGUAGE


async def choose_language_handler(update: Update, context: CallbackContext) -> int:
    """Handles language selection."""
    query = update.callback_query
    await query.answer()
    lang_name = query.data.split("_")[1]
    if lang_name not in TARGET_LANGUAGES:
        logger.warning(f"Unknown language selected: {lang_name}")
        await query.edit_message_text(
            "An error occurred, please select a language from the list."
        )
        return CHOOSE_LANGUAGE

    context.user_data["translate_lang"] = lang_name
    lang_display_name = TARGET_LANGUAGES[lang_name]
    await query.edit_message_text(
        f"You have selected {lang_display_name}. Send the text."
    )
    return TRANSLATING


async def translate_text_handler(update: Update, context: CallbackContext) -> int:
    """Receives text from the user and translates it."""
    user_message = update.message.text
    chat_id = update.message.chat.id
    dest_lang = context.user_data.get("translate_lang")

    if not dest_lang:
        logger.warning(
            "translate_text_handler called without a selected language in user_data."
        )
        await update.message.reply_text("First, select a language using /translate.")
        return ConversationHandler.END

    prompt = (
        f"Translate the following text into {dest_lang}. "
        f"Return only the translation itself, "
        f"without any extra phrases or comments:\n\n{user_message}"
    )
    translate_keyboard = get_translate_keyboard()
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        translated_text = await chatgpt_client.ask(prompt)
        await update.message.reply_text(
            f"Translation:\n\n{translated_text}", reply_markup=translate_keyboard
        )
        return TRANSLATING
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "Failed to translate.", reply_markup=translate_keyboard()
        )
        return TRANSLATING


async def change_language_handler(update: Update, context: CallbackContext) -> int:
    """Handles the 'Change language' button."""
    query = update.callback_query
    await query.answer()
    return await start_translate_handler(update, context)
