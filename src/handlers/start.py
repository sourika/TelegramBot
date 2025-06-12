import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from keyboards.reply_keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: CallbackContext) -> int:
    """
    Handles the /start command.
    Sends a welcome message and the main keyboard.
    Ends any active conversation.
    """
    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        logger.error("start_handler: Could not determine user or chat.")
        return ConversationHandler.END

    reply_markup = get_main_menu_keyboard()

    welcome_text = (
        rf"Hi, {user.mention_html()}! 👋"
        "\n\nI'm your assistant bot."
        "\n\nWith me, you can:"
        "\n\n"
        "🔹 Get an interesting fact\n"
        "🔹 Ask ChatGPT questions\n"
        "🔹 Chat with famous personalities\n"
        "🔹 Take an interactive quiz\n"
        "🔹 Translate text\n"
        "🔹 Have voice conversations with ChatGPT"
    )
    await context.bot.send_message(
        chat_id=chat.id, text=welcome_text, reply_markup=reply_markup, parse_mode="HTML"
    )
    return ConversationHandler.END
