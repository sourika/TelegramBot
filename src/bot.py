"""Main entry point for the Telegram bot, which ties all the handlers together."""

from config import TELEGRAM_BOT_TOKEN

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from utils.logger import setup_logger
from handlers.start import start_handler
from handlers.finish import finish_handler
from handlers.error import error_handler
from handlers.famous_personality import (
    start_talk_handler,
    choose_personality_handler,
    talk_to_personality_handler,
    change_personality_handler,
)
from handlers.quiz import (
    start_quiz_handler,
    choose_topic_handler,
    ask_question_handler,
    check_answer_handler,
    finish_quiz_handler,
)
from handlers.chat_interface import (
    start_gpt_handler,
    gpt_conversation_handler,
)
from handlers.random_fact import (
    start_random_handler,
    random_fact_handler,
)
from handlers.optional_features.translator import (
    start_translate_handler,
    choose_language_handler,
    translate_text_handler,
    change_language_handler,
)
from handlers.optional_features.voice_chatgpt import (
    start_voice_handler,
    process_voice_handler,
)


# --- State Definitions ---
(
    RANDOM_FACT,  # /random
    GPT_INTERFACE,  # /gpt
    CHOOSE_PERSONALITY,
    TALK_TO_PERSONALITY,  # /talk
    CHOOSE_TOPIC,
    ASK_QUESTION,
    QUIZ_NEXT,  # /quiz
    CHOOSE_LANGUAGE,
    TRANSLATING,  # /translate
    PROCESSING_VOICE,  # /voice
) = range(10)


setup_logger("")

logger = logging.getLogger(__name__)
logger.info("Environment variables loaded.")


def main():
    """Main function to run the bot."""
    token = TELEGRAM_BOT_TOKEN

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(finish_handler, pattern="^finish$"))

    # --- ConversationHandler for /random ---
    random_handler = ConversationHandler(
        name="fact_session",
        entry_points=[
            CommandHandler("random", start_random_handler),
            MessageHandler(
                filters.Regex("^💡 Interesting Fact$"), start_random_handler
            ),
        ],
        states={
            RANDOM_FACT: [
                CallbackQueryHandler(random_fact_handler, pattern="^random_more$"),
                CallbackQueryHandler(finish_handler, pattern="^finish_random$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        allow_reentry=True,
        per_message=False,
    )

    # --- ConversationHandler for /gpt ---
    gpt_handler = ConversationHandler(
        name="gpt_session",
        entry_points=[
            CommandHandler("gpt", start_gpt_handler),
            MessageHandler(filters.Regex("^🤖 ChatGPT$"), start_gpt_handler),
        ],
        states={
            GPT_INTERFACE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, gpt_conversation_handler
                ),
                CallbackQueryHandler(finish_handler, pattern="^finish_gpt_dialog$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        allow_reentry=True,
        per_message=False,
    )

    # --- ConversationHandler for /talk ---
    talk_handler = ConversationHandler(
        name="talk_session",
        entry_points=[
            CommandHandler("talk", start_talk_handler),
            MessageHandler(
                filters.Regex("^👥 Chat with Personality$"), start_talk_handler
            ),
        ],
        states={
            CHOOSE_PERSONALITY: [
                CallbackQueryHandler(choose_personality_handler, pattern="^talk_")
            ],
            TALK_TO_PERSONALITY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, talk_to_personality_handler
                ),
                CallbackQueryHandler(
                    change_personality_handler, pattern="^change_personality$"
                ),
                CallbackQueryHandler(finish_handler, pattern="^finish_talk_dialog$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        allow_reentry=True,
        per_message=False,
    )

    # --- ConversationHandler for /quiz ---
    quiz_handler = ConversationHandler(
        name="quiz_session",
        entry_points=[
            CommandHandler("quiz", start_quiz_handler),
            MessageHandler(filters.Regex("^❓ Quiz$"), start_quiz_handler),
        ],
        states={
            CHOOSE_TOPIC: [
                CallbackQueryHandler(choose_topic_handler, pattern="^quiz_topic_")
            ],
            ASK_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer_handler)
            ],
            QUIZ_NEXT: [
                CallbackQueryHandler(ask_question_handler, pattern="^quiz_more$"),
                CallbackQueryHandler(start_quiz_handler, pattern="^quiz_change$"),
                CallbackQueryHandler(finish_quiz_handler, pattern="^finish_quiz$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        allow_reentry=True,
        per_message=False,
    )

    # --- ConversationHandler for /translate ---
    translate_handler = ConversationHandler(
        name="translate_session",
        entry_points=[
            CommandHandler("translate", start_translate_handler),
            MessageHandler(filters.Regex("^🌐 Translator$"), start_translate_handler),
        ],
        states={
            CHOOSE_LANGUAGE: [
                CallbackQueryHandler(choose_language_handler, pattern="^lang_")
            ],
            TRANSLATING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text_handler),
                CallbackQueryHandler(change_language_handler, pattern="^change_lang$"),
                CallbackQueryHandler(finish_handler, pattern="^finish_translate$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        allow_reentry=True,
        per_message=False,
    )

    # --- ConversationHandler for /voice ---
    voice_handler = ConversationHandler(
        name="voice_session",
        entry_points=[
            CommandHandler("voice", start_voice_handler),
            MessageHandler(
                filters.Regex("^🎤 Voice-to-Voice Conversations$"), start_voice_handler
            ),
        ],
        states={
            PROCESSING_VOICE: [
                MessageHandler(filters.VOICE, process_voice_handler),
                CallbackQueryHandler(finish_handler, pattern="^finish_voice$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_handler)],
        allow_reentry=True,
        per_message=False,
    )

    application.add_handler(random_handler)
    application.add_handler(gpt_handler)
    application.add_handler(talk_handler)
    application.add_handler(quiz_handler)
    application.add_handler(translate_handler)
    application.add_handler(voice_handler)

    application.add_error_handler(error_handler)

    logger.info("Starting the bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
