# Multi-Feature Telegram Assistant Bot

A sophisticated, asynchronous Telegram bot built with Python, leveraging the OpenAI API to provide a wide range of interactive and intelligent features. The bot is designed with a clean, modular architecture for easy extension and maintenance.

## ✨ Key Features

* **🤖 Full ChatGPT Interface:** Engage in direct, multi-turn conversations with the GPT model. The bot remembers the context of your current conversation.
* **🗣️ Chat with Famous Personalities:** Talk to AI-powered personas of historical figures and characters, each with a unique personality defined by a system prompt.
* **🎙️ Voice-to-Voice Conversations:** A complete voice-driven interaction cycle:
    1.  User sends a voice message.
    2.  The audio is transcribed to text using OpenAI's **Whisper API**.
    3.  The transcribed text is sent to ChatGPT for a response.
    4.  The text response is converted back to audio using OpenAI's **Text-to-Speech (TTS) API**.
    5.  The bot replies with a voice message.
* **❓ Interactive Quiz:** Test your knowledge on various subjects like History, Science, and Art. The bot generates questions, tracks your score, and remembers questions within a session to avoid repeats.
* **💡 Unique Random Facts:** Get interesting facts from ChatGPT. The bot keeps track of the facts it has already sent you in a session to avoid duplicates.
* **🌐 Text Translator:** Translate text into different languages using the power of the GPT model.
* **Stateful Conversations:** Uses `ConversationHandler` to manage user state across different features, ensuring a smooth user experience.
* **Clean Architecture:** The project is organized into logical modules for handlers, keyboards, and utilities, making the code easy to read and maintain.

## 🛠️ Technologies Used

* **Backend:** Python 3.10+
* **Telegram Framework:** `python-telegram-bot` (v20+, async)
* **AI Services:** `openai` (Official Python SDK for GPT, Whisper, and TTS)
* **Environment Management:** `python-dotenv`
* **File Handling:** `aiofiles` for asynchronous file operations
* **Code Quality:** Configured with `.flake8`, `.gitignore`, and `pre-commit` for linting and formatting.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* Python 3.10 or higher
* A Telegram Bot Token from [BotFather](https://t.me/BotFather)
* An OpenAI API Key from the [OpenAI Platform](https://platform.openai.com/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd TelegramBot
    ```

2.  **Create and activate a virtual environment:**
    * On Windows:
        ```bash
        python -m venv .venv
        .\.venv\Scripts\activate
        ```
    * On macOS/Linux:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  In the root directory of the project, create a file named `.env`.

2.  Add your secret keys to the `.env` file. This file is listed in `.gitignore` and will not be committed to your repository.
    ```env
    OPENAI_API_KEY="sk-..."
    TELEGRAM_BOT_TOKEN="..."
    ```

### Running the Bot

1.  Navigate to the source directory:
    ```bash
    cd src
    ```

2.  Run the main bot file:
    ```bash
    python bot.py
    ```

Your bot should now be running and responsive on Telegram!

## Project Structure

The project is organized to separate concerns and improve maintainability:

```text
TelegramBot/
├── .env                  # Stores environment variables (API keys)
├── .venv/                # Virtual environment directory
├── images/               # Static images used by the bot
├── src/                  # Main source code
│   ├── handlers/         # Logic for handling user commands and messages
│   │   ├── optional_features/ # Handlers for more complex features
│   │   └── ...           # Core feature handlers (start, quiz, etc.)
│   ├── keyboards/        # Creates inline and reply keyboards for the UI
│   ├── utils/            # Helper modules (ChatGPT client, logger, etc.)
│   └── bot.py            # Main application entry point
├── .gitignore            # Files to be ignored by Git
├── pyproject.toml        # Project metadata and configuration
├── README.md             # This file
└── requirements.txt      # Project dependencies

```
## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or want to add new features, feel free to fork the repository, make your changes, and open a pull request.
