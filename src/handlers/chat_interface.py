"""Handlers for the direct ChatGPT interface feature (/talk command)."""

import logging

import aiofiles
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.chatgpt_client import ChatGPTClient
from keyboards.inline_keyboards import get_finish_keyboard

from config import ROOT_DIR

logger = logging.getLogger(__name__)
chatgpt_client = ChatGPTClient()
GPT_INTERFACE = 1
IMAGE_PATH = ROOT_DIR / "images" / "ChatGPT.jpg"


async def start_gpt_handler(update: Update, context: CallbackContext) -> int:
    message = update.message
    chat_id = message.chat.id
    context.user_data["gpt_system_prompt"] = (
        "You are an AI assistant. Try to answer completely and friendly."
    )
    context.user_data["gpt_history"] = []

    logger.info(
        f"User {chat_id} started a /gpt session. System prompt set. History cleared."
    )

    try:
        async with aiofiles.open(IMAGE_PATH, "rb") as f:
            photo_bytes = await f.read()
            await context.bot.send_photo(chat_id=chat_id, photo=photo_bytes)
            keyboard = get_finish_keyboard(finish_callback="finish_gpt_dialog")
        await message.reply_text(
            "I am ready to answer your questions. What would you like to know?",
            reply_markup=keyboard,
        )
        logger.info(
            f"CHAT_DATA at end of start_gpt_handler "
            f"(returning GPT_INTERFACE): {context.chat_data}"
        )
        return GPT_INTERFACE
    except FileNotFoundError as e:
        logger.error(f"Error sending image (file not found): {e}")
        await message.reply_text(
            "Failed to load the picture, but I am ready to answer "
            "your questions! To exit, use /start."
        )
        return GPT_INTERFACE
    except Exception as e:
        logger.error(f"General error in start_gpt_handler: {e}")
        await message.reply_text("An error occurred while starting GPT. Try /start.")
        return ConversationHandler.END


async def gpt_conversation_handler(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text
    chat_id = update.message.chat.id
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        history = context.user_data.get("gpt_history", [])
        system_prompt_for_session = context.user_data.get("gpt_system_prompt")

        response = await chatgpt_client.ask(
            current_user_prompt=user_message,
            history=history,
            system_prompt=system_prompt_for_session,
        )

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": response})
        context.user_data["gpt_history"] = history

        max_history_turns = 5
        if len(context.user_data["gpt_history"]) > max_history_turns * 2:
            context.user_data["gpt_history"] = context.user_data["gpt_history"][
                -(max_history_turns * 2) :
            ]

        keyboard = get_finish_keyboard(finish_callback="finish_gpt_dialog")
        await update.message.reply_text(response, reply_markup=keyboard)
        return GPT_INTERFACE
    except Exception as e:
        logger.error(f"Error in gpt_conversation_handler: {e}")
        keyboard = get_finish_keyboard(finish_callback="finish_gpt_dialog")
        await update.message.reply_text(
            "Failed to get a response. Try /start or press 'Finish'.",
            reply_markup=keyboard,
        )
        return GPT_INTERFACE
