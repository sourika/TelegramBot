import logging

import aiofiles
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.chatgpt_client import ChatGPTClient
from keyboards.inline_keyboards import get_random_fact_keyboard

logger = logging.getLogger(__name__)
chatgpt_client = ChatGPTClient()
RANDOM_FACT = 0
IMAGE_PATH = "../images/Fact.jpg"


async def start_random_handler(update: Update, context: CallbackContext) -> int:
    message = update.message
    if not message or not message.chat:
        logger.error("start_random_handler called without message or chat.")
        return ConversationHandler.END

    chat_id = message.chat.id

    context.user_data["fact_history"] = []
    logger.info(f"User {chat_id} started /random. Fact history cleared.")

    try:
        async with aiofiles.open(IMAGE_PATH, "rb") as f:
            photo_bytes = await f.read()
            await context.bot.send_photo(chat_id=chat_id, photo=photo_bytes)
    except FileNotFoundError as e:
        logger.error(f"Error sending image (file not found): {e}")
        await message.reply_text("Oops, the picture is lost... But no worries!")
    except Exception as e_photo:
        logger.error(f"Another error when sending photo for the fact: {e_photo}")

    prompt = (
        "Tell me one interesting fact. Start your answer strictly with "
        "'Interesting fact:' without any other words or expressions."
    )
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        fact = await chatgpt_client.ask(
            prompt, history=context.user_data["fact_history"]
        )
        if fact:
            context.user_data["fact_history"].append(
                {"role": "user", "content": prompt}
            )
            context.user_data["fact_history"].append(
                {"role": "assistant", "content": fact}
            )

        keyboard = get_random_fact_keyboard()
        await message.reply_text(fact, reply_markup=keyboard)
        return RANDOM_FACT

    except Exception as e:
        logger.error(f"Error in start_random_handler: {e}")
        await message.reply_text(
            "Oops, I can't find an interesting fact. Please try /start."
        )
        return ConversationHandler.END


async def random_fact_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    message = query.message

    if not message:
        logger.warning("Failed to get 'message' from CallbackQuery...")
        await query.answer(
            text="Action cannot be performed (message not found).", show_alert=True
        )
        return RANDOM_FACT

    chat_id = message.chat.id
    fact_history = context.user_data.get("fact_history", [])

    prompt = (
        "Tell me another interesting fact, different from the previous ones. "
        "Start your answer strictly with 'Interesting fact:'"
    )
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        fact = await chatgpt_client.ask(prompt, history=fact_history)
        if fact:
            fact_history.append({"role": "user", "content": prompt})
            fact_history.append({"role": "assistant", "content": fact})

        context.user_data["fact_history"] = fact_history

        keyboard = get_random_fact_keyboard()
        await query.edit_message_text(fact, reply_markup=keyboard)
        return RANDOM_FACT
    except Exception as e:
        logger.error(f"Error in random_fact_handler: {e}")
        await query.edit_message_text(
            "Oops, I can't find a new fact right now. Try again?",
            reply_markup=get_random_fact_keyboard(),
        )
        return RANDOM_FACT
