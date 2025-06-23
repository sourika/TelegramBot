"""Handler for gracefully finishing conversations."""

import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from handlers.start import start_handler

logger = logging.getLogger(__name__)


async def finish_handler(update: Update, context: CallbackContext) -> int:
    """Ends the current conversation and calls start_handler."""
    query = update.callback_query

    if query:
        await query.answer()
        if query.message:
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception as e:
                msg_id = "unknown"
                if query and query.message:
                    msg_id = query.message.message_id
                logger.error(
                    f"Failed to remove the inline keyboard in finish_handler "
                    f"(message ID: {msg_id}): {e}"
                )

    keys_to_clear = [
        "personality_prompt",
        "personality_name",
        "gpt_history",
        "gpt_system_prompt",
        "translate_lang",
    ]

    for key in keys_to_clear:
        context.user_data.pop(key, None)

    if query or update.message:
        logger.info(
            f"User data for the conversation (keys: {keys_to_clear}) "
            f"cleared in finish_handler."
        )

    await start_handler(update, context)

    return ConversationHandler.END
