import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: CallbackContext) -> None:
    """Logs errors and sends a message to the user."""
    logger.error(msg="An error occurred:", exc_info=context.error)
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Oops! It seems something went wrong. "
                "Please try again a little later or use /start."
            )
        except Exception as e:
            logger.error(
                f"Failed to send error message to user (effective_message): {e}"
            )
    elif update and update.callback_query:
        try:
            await context.bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text="Oops! It seems something went wrong. "
                "Please try again a little later or use /start.",
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user (callback_query): {e}")
