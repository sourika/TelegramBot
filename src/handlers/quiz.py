import asyncio
import logging

import aiofiles
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from handlers.start import start_handler
from utils.chatgpt_client import ChatGPTClient
from keyboards.inline_keyboards import get_topic_keyboard, get_quiz_next_keyboard

logger = logging.getLogger(__name__)
chatgpt_client = ChatGPTClient()
CHOOSE_TOPIC, ASK_QUESTION, QUIZ_NEXT = 4, 5, 6
IMAGE_PATH = "../images/Quiz.jpg"


def parse_chatgpt_verdict(text: str) -> bool | None:
    """Tries to understand ChatGPT's 'Yes' or 'No' answer."""
    text_lower = text.strip().lower()
    if "yes" in text_lower and "no" not in text_lower:
        return True
    if "no" in text_lower and "yes" not in text_lower:
        return False
    logger.warning(f"Could not definitively determine ChatGPT's verdict: {text}")
    return None


async def start_quiz_handler(update: Update, context: CallbackContext) -> int:
    """Starts the quiz or offers to change the topic, initializes counters
    if they don't exist. Sends an image only on the very first run."""
    query = update.callback_query
    message = update.effective_message
    chat_id = update.effective_chat.id

    if not message or not chat_id:
        logger.error("start_quiz_handler could not determine the message or chat.")
        return ConversationHandler.END

    if "quiz_total_questions" not in context.user_data:
        context.user_data["quiz_total_questions"] = 0
        logger.info(f"User {chat_id}: quiz_total_questions initialized to 0.")
    if "quiz_correct_answers" not in context.user_data:
        context.user_data["quiz_correct_answers"] = 0
        logger.info(f"User {chat_id}: quiz_correct_answers initialized to 0.")
    if "quiz_generation_history" not in context.user_data:
        context.user_data["quiz_generation_history"] = []
    if "quiz_photo_sent_this_session" not in context.user_data:
        context.user_data["quiz_photo_sent_this_session"] = False

    score = context.user_data["quiz_correct_answers"]
    total_q = context.user_data["quiz_total_questions"]

    keyboard = get_topic_keyboard()
    text_to_send = f"Your current score: {score} out of {total_q}.\nSelect a topic:"

    if not context.user_data.get("quiz_photo_sent_this_session", False):
        try:
            async with aiofiles.open(IMAGE_PATH, "rb") as f:
                photo_bytes = await f.read()
                await context.bot.send_photo(chat_id=chat_id, photo=photo_bytes)
            context.user_data["quiz_photo_sent_this_session"] = True
        except FileNotFoundError as e:
            logger.error(f"Error sending quiz image (file not found): {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Failed to load the image, but let's start the quiz!",
            )
            context.user_data["quiz_photo_sent_this_session"] = True

    if query:
        await query.answer()
        try:
            if query.message:
                await query.edit_message_reply_markup(reply_markup=None)
        except Exception as e:
            logger.error(
                f"Failed to remove the keyboard "
                f"when changing the topic (this is not critical): {e}"
            )
    try:
        await context.bot.send_message(
            chat_id=chat_id, text=text_to_send, reply_markup=keyboard
        )
    except Exception as e:
        logger.error(
            f"Critical error: failed to send the topic selection message. Error: {e}"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="An error occurred. Please try again, starting with /start.",
        )
        return ConversationHandler.END

    return CHOOSE_TOPIC


async def choose_topic_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    topic = query.data.split("_")[-1]
    context.user_data["quiz_topic"] = topic
    context.user_data["quiz_generation_history"] = []
    logger.info(
        f"User {query.from_user.id} chose topic '{topic}'. "
        f"Quiz question history cleared."
    )

    await query.edit_message_text(
        f"Topic: {context.user_data['quiz_topic']}. Preparing a question..."
    )
    return await ask_question_handler(update, context)


async def ask_question_handler(update: Update, context: CallbackContext) -> int:
    """Asks a question received from ChatGPT, with options A, B, C, D in the text."""
    query = update.callback_query
    message = update.message or (query.message if query else None)

    if not message:
        logger.error("ask_question_handler: message is None.")
        if query:
            await query.answer("An error occurred.", show_alert=True)
        return ConversationHandler.END

    chat_id = message.chat.id
    topic = context.user_data.get("quiz_topic", "General Knowledge")
    quiz_history = context.user_data.get("quiz_generation_history", [])
    if not quiz_history:
        prompt_for_question = f"""
    Generate a quiz question on the topic '{topic}'.
    In the response, first write the question itself.
    Then, on new lines, write four answer options, labeled A), B), C), D).
    The answer options must not be repeated.
    After that, on a COMPLETELY NEW LINE, after the marker 'CORRECT ANSWER:',
    provide only the LETTER of the correct answer (A, B, C, or D).

    Example:
    What city is the capital of France?
    A) Berlin
    B) Madrid
    C) Paris
    D) Rome
    CORRECT ANSWER: C
    """
    else:
        prompt_for_question = (
            f"Great, now generate another, completely different "
            f"question on the same topic ('{topic}'), in the same format."
        )
    max_attempts = 3
    question_text_with_options = None
    correct_answer_letter = None

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        for attempt in range(1, max_attempts + 1):
            logger.info(
                f"Generating question (attempt {attempt}/{max_attempts}): "
                f"topic '{topic}'"
            )
            full_response_text = await chatgpt_client.ask(
                current_user_prompt=prompt_for_question, history=quiz_history
            )

            parts = full_response_text.split("CORRECT ANSWER:")
            if len(parts) == 2:
                parsed_question = parts[0].strip()
                parsed_letter = parts[1].strip().upper()

                if parsed_letter in ["A", "B", "C", "D"]:
                    question_text_with_options = parsed_question
                    correct_answer_letter = parsed_letter

                    quiz_history.append(
                        {"role": "user", "content": prompt_for_question}
                    )
                    quiz_history.append(
                        {"role": "assistant", "content": full_response_text}
                    )
                    context.user_data["quiz_generation_history"] = quiz_history
                    logger.info("Question successfully generated and saved to history.")
                    break
                else:
                    logger.warning(
                        f"Incorrect answer letter from ChatGPT: {parsed_letter}"
                    )

            logger.warning(
                f"Attempt {attempt} failed: could not split ChatGPT's response or "
                f"incorrect letter format. Response: {full_response_text[:200]}..."
            )
            if attempt < max_attempts:
                await asyncio.sleep(1)

        if not question_text_with_options or not correct_answer_letter:
            logger.error(
                f"Failed to generate a valid question after {max_attempts} attempts."
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text="Unfortunately, a question could not be generated. "
                "Please try selecting another topic or /start.",
            )

            next_action_keyboard = get_quiz_next_keyboard()
            await context.bot.send_message(
                chat_id=chat_id,
                text="What should we do next?",
                reply_markup=next_action_keyboard,
            )
            return QUIZ_NEXT

        context.user_data["current_quiz_question_text"] = question_text_with_options
        context.user_data["current_quiz_correct_letter"] = correct_answer_letter

        await context.bot.send_message(chat_id=chat_id, text=question_text_with_options)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Type the letter of your answer (A, B, C, or D):",
            reply_markup=ReplyKeyboardRemove(),
        )

        context.user_data["quiz_total_questions"] = (
            context.user_data.get("quiz_total_questions", 0) + 1
        )
        logger.info(
            f"User {chat_id}: total questions updated "
            f"to {context.user_data['quiz_total_questions']}."
        )

        return ASK_QUESTION
    except Exception as e:
        logger.error(f"Critical error in ask_question_handler: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="An error occurred while generating the question. Please try /start.",
        )
        return ConversationHandler.END


async def check_answer_handler(update: Update, context: CallbackContext) -> int:
    """Sends the user's answer and the question to ChatGPT for verification."""
    user_answer_text = update.message.text.strip().upper()
    chat_id = update.message.chat.id

    question_asked = context.user_data.get("current_quiz_question_text")
    correct_letter = context.user_data.get("current_quiz_correct_letter")

    if not question_asked or not correct_letter:
        logger.error(
            "Error in check_answer_handler: question text or correct letter is missing."
        )
        await update.message.reply_text(
            "An internal error occurred. Please try the next question.",
            reply_markup=get_quiz_next_keyboard(),
        )
        return QUIZ_NEXT

    if user_answer_text not in ["A", "B", "C", "D"]:
        await update.message.reply_text(
            f"Please answer with one of the letters: "
            f"A, B, C, or D.\n\n{question_asked}",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ASK_QUESTION

    prompt_for_checking = f"""
    The correct answer option was marked with the letter: {correct_letter}.
    The user answered: {user_answer_text}.
    Did the user answer correctly? Answer with a single word: 'Yes' or 'No'.
    """

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        verdict_text = await chatgpt_client.ask(prompt_for_checking, max_tokens=10)
        is_correct = parse_chatgpt_verdict(verdict_text)

        current_correct_answers = context.user_data.get("quiz_correct_answers", 0)
        total_questions_asked = context.user_data.get("quiz_total_questions", 0)

        if is_correct is True:
            current_correct_answers += 1
            context.user_data["quiz_correct_answers"] = current_correct_answers
            result_text = "Correct! ✅\n"
        elif is_correct is False:
            result_text = f"Incorrect. ❌ The correct answer was: {correct_letter}.\n"
        else:
            logger.info("ChatGPT verdict unclear.")
            result_text = (
                "ChatGPT could not determine if you answered the question correctly. "
                "Therefore, it will not be counted in the quiz score.\n"
            )

        result_text += (
            f"Total score: {current_correct_answers} out of {total_questions_asked}."
        )
        logger.info(
            f"User {chat_id}: "
            f"score updated to {current_correct_answers}/{total_questions_asked}."
        )

    except Exception as e:
        logger.error(f"Error in check_answer_handler when contacting ChatGPT: {e}")
        result_text = "Could not check your answer. Let's try the next question."

    await update.message.reply_text(result_text, reply_markup=get_quiz_next_keyboard())
    return QUIZ_NEXT


async def finish_quiz_handler(update: Update, context: CallbackContext) -> int:
    """
    Ends the quiz, summarizes the results, clears quiz data, and calls start_handler.
    """
    query = update.callback_query
    effective_chat_id = update.effective_chat.id if update.effective_chat else None

    if query:
        await query.answer()
        if query.message:
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception as e:
                logger.info(
                    f"Failed to remove the inline keyboard in finish_quiz_handler: {e}"
                )

    score = context.user_data.get("quiz_correct_answers", 0)
    total = context.user_data.get("quiz_total_questions", 0)

    if total > 0:
        percentage = round((score / total) * 100)
        final_quiz_result_message = (
            f"**Quiz finished!** 🎉\n\n"
            f"Your final score:\n"
            f"Correct answers: {score} out of {total}\n"
            f"Percentage: {percentage}%\n\n"
            "Thanks for playing!"
        )
    else:
        final_quiz_result_message = (
            "🏁 Quiz finished, but you didn't answer any questions."
        )

    if effective_chat_id:
        await context.bot.send_message(
            chat_id=effective_chat_id,
            text=final_quiz_result_message,
            parse_mode="Markdown",
        )
    else:
        logger.warning(
            "finish_quiz_handler: effective_chat_id is None, cannot send final result."
        )

    quiz_keys_to_clear = [
        "quiz_total_questions",
        "quiz_correct_answers",
        "quiz_topic",
        "current_quiz_question_text",
        "current_quiz_correct_letter",
        "quiz_photo_sent_this_session",
        "quiz_generation_history",
    ]
    for key in quiz_keys_to_clear:
        context.user_data.pop(key, None)
    logger.info(f"Quiz data (keys: {quiz_keys_to_clear}) cleared.")

    await start_handler(update, context)

    return ConversationHandler.END
