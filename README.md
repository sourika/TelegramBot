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
* **Clean Architecture:** The project is organized into logical modules for handlers, keyboards, utilities, and a central config, making the code easy to read and maintain.

## 🛠️ Technologies Used

* **Backend:** Python 3.11+
* **Telegram Framework:** `python-telegram-bot` (v20+, async)
* **AI Services:** `openai` (Official Python SDK for GPT, Whisper, and TTS)
* **Dependency Management:** `Poetry`
* **Environment Variables:** `python-dotenv`
* **File Handling:** `aiofiles` for asynchronous file operations
* **Code Quality:** `pre-commit`, `black`, `flake8`

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

* Python 3.11 or higher
* [Poetry](https://python-poetry.org/docs/#installation) (follow the official instructions to install it)
* A Telegram Bot Token from [BotFather](https://t.me/BotFather)
* An OpenAI API Key from the [OpenAI Platform](https://platform.openai.com/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd TelegramBot
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```
    This single command will read the `pyproject.toml` file, create a dedicated virtual environment for the project, and install all the necessary dependencies specified in the `poetry.lock` file. This ensures a consistent and reproducible setup.

### Configuration

1.  In the root directory of the project, create a file named `.env`.

2.  Add your secret keys to the `.env` file. This file is listed in `.gitignore` and will not be committed to your repository.
    ```env
    OPENAI_API_KEY="sk-..."
    TELEGRAM_BOT_TOKEN="..."
    ```

### Running the Bot

Execute the main bot script using Poetry's `run` command. This ensures the script runs within the correct virtual environment.

```bash
    poetry run python src/bot.py
  ```

Your bot should now be running and responsive on Telegram!

## Project Structure

The project is organized to separate concerns and improve maintainability:

```text
TelegramBot/
├── .env                  # Stores environment variables (API keys)
├── images/               # Static images used by the bot
├── src/                  # Main source code
│   ├── config.py           # Central configuration, loads .env and defines global constants
│   ├── handlers/         # Logic for handling user commands and messages
│   ├── keyboards/        # Creates inline and reply keyboards for the UI
│   └── utils/            # Reusable utilities (OpenAI client, logger setup)
├── .gitignore            # Files to be ignored by Git
├── .pre-commit-config.yaml # Configuration for pre-commit hooks (black, flake8)
├── poetry.lock           # Exact versions of all dependencies for reproducible builds
├── pyproject.toml        # Project configuration, dependencies, and tool settings
└── README.md             # This file

```
## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or want to add new features, feel free to fork the repository, make your changes, and open a pull request.
