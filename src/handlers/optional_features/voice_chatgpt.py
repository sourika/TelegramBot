"""Handlers for the voice-to-voice conversation feature (/voice command)."""

import logging
import aiofiles.os as aio_os
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from keyboards.inline_keyboards import get_finish_keyboard
from utils.chatgpt_client import ChatGPTClient

logger = logging.getLogger(__name__)

chatgpt_client = ChatGPTClient()

PROCESSING_VOICE = 9


async def remove_file_async(file_path: str) -> None:
    """Asynchronously and safely deletes a file from the disk."""
    try:
        if await aio_os.path.exists(file_path):
            await aio_os.remove(file_path)
            logger.info(f"Temporary file {file_path} successfully deleted.")
    except Exception as e:
        logger.error(f"Failed to delete temporary file {file_path}: {e}")


async def start_voice_handler(update: Update, _context: CallbackContext) -> int:
    """Starts the voice interaction."""
    await update.message.reply_text("Send me a voice message. To exit, press /start.")
    return PROCESSING_VOICE


async def process_voice_handler(update: Update, context: CallbackContext) -> int:
    """
    Full cycle of voice message processing: Speech-to-Text -> Chat -> Text-to-Speech.
    """
    message = update.message
    chat_id = update.effective_chat.id if update.effective_chat else None

    if not message or not message.voice or not chat_id:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.warning(f"User {user_id} sent a non-voice message in /voice mode.")
        await context.bot.send_message(
            chat_id=chat_id,
            text="I am expecting a voice message 🎤. "
            "Please record and send it, or use /start to exit.",
        )
        return PROCESSING_VOICE

    voice = message.voice
    file_path = f"voice_temp_{voice.file_id}.ogg"

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")
        voice_file = await context.bot.get_file(voice.file_id)
        await voice_file.download_to_drive(file_path)

        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        transcription = await chatgpt_client.transcribe(file_path)

        if not transcription:
            await message.reply_text(
                "Unfortunately, I could not recognize the speech. "
                "Please try recording the message again."
            )
            return PROCESSING_VOICE

        await message.reply_text(f"You said: *{transcription}*", parse_mode="Markdown")

        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        chatgpt_response = await chatgpt_client.ask(transcription)

        await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")
        audio_response_bytes = await chatgpt_client.text_to_speech(chatgpt_response)
        keyboard = get_finish_keyboard(finish_callback="finish_voice")

        if audio_response_bytes:
            await context.bot.send_voice(
                chat_id=chat_id, voice=audio_response_bytes, reply_markup=keyboard
            )
        else:
            logger.warning("Failed to convert text to speech, sending as text.")
            await message.reply_text(
                f"ChatGPT response (audio was not generated):\n{chatgpt_response}",
                reply_markup=keyboard,
            )

        return PROCESSING_VOICE

    except Exception as e:
        logger.error(f"Critical error during voice processing: {e}")
        if chat_id:
            await context.bot.send_message(
                chat_id=chat_id, text="An unexpected error occurred. Please try /start."
            )
        return ConversationHandler.END

    finally:
        await remove_file_async(file_path)
