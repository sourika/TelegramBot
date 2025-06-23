"""Handlers for the 'Chat with a Famous Personality' feature (/talk command)."""

import logging

import aiofiles
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.chatgpt_client import ChatGPTClient
from keyboards.inline_keyboards import (
    get_personality_keyboard,
    get_finish_keyboard,
    get_talk_action_keyboard,
)

from config import ROOT_DIR

logger = logging.getLogger(__name__)
chatgpt_client = ChatGPTClient()
CHOOSE_PERSONALITY, TALK_TO_PERSONALITY = 2, 3
IMAGE_PATH = ROOT_DIR / "images" / "Famous_people.jpg"
PERSONALITIES = {
    "Albert Einstein": (
        "You are Albert Einstein. Respond as a thoughtful, brilliant physicist. "
        "Explain complex topics like relativity and the universe with clarity, "
        "simple analogies, and a sense of scientific wonder. Strive to keep "
        "your explanations comprehensive yet under approximately 500 words."
    ),
    "Alexander Pushkin": (
        "You are Alexander Pushkin, the great Russian poet. "
        "Some of your responses must be in rhyming English verse. "
        "Maintain an eloquent, romantic style, rich with imagery, "
        "touching on themes like love, honor, and fate. Strive to keep your "
        "explanations comprehensive yet under approximately 500 words."
    ),
    "Bill Gates": (
        "You are Bill Gates. Respond analytically and pragmatically as "
        "a technologist and philanthropist. Discuss technology, AI, innovation, "
        "global health, and climate change with a forward-thinking, "
        "solution-oriented perspective. Strive to keep your explanations "
        "comprehensive yet under approximately 500 words."
    ),
    "Michael Jackson": (
        "You are Michael Jackson, the King of Pop. Respond with energy, "
        "creativity, and an inspiring, positive tone. Discuss music, "
        "dance, love, unity, and healing. Make your words feel rhythmic "
        "and engaging, reflecting your artistic spirit. Strive to keep your "
        "explanations comprehensive yet under approximately 500 words."
    ),
}


async def start_talk_handler(update: Update, context: CallbackContext) -> int:
    chat = update.effective_chat
    if not chat:
        logger.error("start_talk_handler could not determine the chat.")
        return ConversationHandler.END
    chat_id = chat.id
    personality_keyboard = get_personality_keyboard()
    message_to_reply = update.message or (
        update.callback_query.message if update.callback_query else None
    )

    try:
        async with aiofiles.open(IMAGE_PATH, "rb") as f:
            photo_bytes = await f.read()
            await context.bot.send_photo(chat_id=chat_id, photo=photo_bytes)
        if message_to_reply:
            await message_to_reply.reply_text(
                "Choose who you want to talk to:", reply_markup=personality_keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Choose who you want to talk to:",
                reply_markup=personality_keyboard,
            )
        return CHOOSE_PERSONALITY
    except FileNotFoundError as e:
        logger.error(f"Error sending image (file not found): {e}")
        if message_to_reply:
            await message_to_reply.reply_text(
                "Couldn't load the image, but no worries! Who do you want to talk to?",
                reply_markup=personality_keyboard,
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Couldn't load the image, but no worries! "
                "Who do you want to talk to?",
                reply_markup=personality_keyboard,
            )

        return CHOOSE_PERSONALITY
    except Exception as e:
        logger.error(f"Unexpected error in start_talk_handler: {e}")
        if message_to_reply:
            await message_to_reply.reply_text(
                "Oops, something went wrong! Please try /start."
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text="Oops, something went wrong! Please try /start."
            )
        return ConversationHandler.END


async def choose_personality_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    chosen_key = query.data.split("_")[1]

    if chosen_key not in PERSONALITIES:
        logger.error(
            f"Invalid personality key received from callback_data: {chosen_key}"
        )
        await query.edit_message_text(
            "An error occurred while selecting the personality. Please try again."
        )
        return CHOOSE_PERSONALITY

    context.user_data["personality_prompt"] = PERSONALITIES[chosen_key]
    context.user_data["personality_name"] = chosen_key

    finish_keyboard = get_finish_keyboard(finish_callback="finish_talk_dialog")
    await query.edit_message_text(
        text=f"{chosen_key} - great choice! Ask your question.",
        reply_markup=finish_keyboard,
    )
    return TALK_TO_PERSONALITY


async def talk_to_personality_handler(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text
    chat_id = update.message.chat_id
    personality_prompt = context.user_data.get("personality_prompt")

    if not personality_prompt:
        logger.warning(
            "personality_prompt not found in user_data for talk_to_personality_handler"
        )
        await update.message.reply_text(
            "It seems we haven't selected a personality. Please start with /talk."
        )
        return ConversationHandler.END

    talk_action_keyboard = get_talk_action_keyboard()
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        logger.info(f"Extracted personality_prompt: '{personality_prompt}'")
        response = await chatgpt_client.ask(
            user_message, system_prompt=personality_prompt
        )
        await update.message.reply_text(response, reply_markup=talk_action_keyboard)
        return TALK_TO_PERSONALITY
    except Exception as e:
        logger.error(f"Error in talk_to_personality_handler: {e}")
        await update.message.reply_text(
            "Failed to get a response.", reply_markup=talk_action_keyboard
        )
        return TALK_TO_PERSONALITY


async def change_personality_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    return await start_talk_handler(update, context)
