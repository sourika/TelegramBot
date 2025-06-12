from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PERSONALITIES_KEYS = [
    "Albert Einstein",
    "Alexander Pushkin",
    "Bill Gates",
    "Michael Jackson",
]
PERSONALITIES_DISPLAY_WITH_EMOJI = {
    "Albert Einstein": "⚛️ Albert Einstein",
    "Alexander Pushkin": "🖋️ Alexander Pushkin",
    "Bill Gates": "💻 Bill Gates",
    "Michael Jackson": "🎤 Michael Jackson",
}
QUIZ_TOPICS = ["History", "Science", "Geography", "Art", "Sports"]
TARGET_LANGUAGES = {"Russian": "Russian", "German": "German", "French": "French"}


# --- General ---
def get_finish_keyboard(finish_callback="finish"):
    """Creates a keyboard with a single 'Finish' button."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Finish", callback_data=finish_callback)]]
    )


# --- Random Fact ---
def get_random_fact_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Another fact", callback_data="random_more")],
            [InlineKeyboardButton("Finish", callback_data="finish_random")],
        ]
    )


# --- Talk ---
def get_personality_keyboard():
    buttons = []
    for key in PERSONALITIES_KEYS:
        display_name = PERSONALITIES_DISPLAY_WITH_EMOJI.get(key, key)
        buttons.append(
            [InlineKeyboardButton(display_name, callback_data=f"talk_{key}")]
        )
    return InlineKeyboardMarkup(buttons)


def get_talk_action_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Choose another personality", callback_data="change_personality"
                )
            ],
            [InlineKeyboardButton("Finish", callback_data="finish_talk_dialog")],
        ]
    )


# --- Quiz ---
def get_topic_keyboard():
    buttons = [
        [InlineKeyboardButton(topic, callback_data=f"quiz_topic_{topic}")]
        for topic in QUIZ_TOPICS
    ]
    return InlineKeyboardMarkup(buttons)


def get_quiz_next_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Another question", callback_data="quiz_more")],
            [InlineKeyboardButton("Change topic", callback_data="quiz_change")],
            [InlineKeyboardButton("Finish quiz", callback_data="finish_quiz")],
        ]
    )


# --- Translator ---
def get_language_keyboard():
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
        for code, name in TARGET_LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(buttons)


def get_translate_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Change language", callback_data="change_lang")],
            [InlineKeyboardButton("Finish", callback_data="finish_translate")],
        ]
    )
