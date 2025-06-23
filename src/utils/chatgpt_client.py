from config import OPENAI_API_KEY
import os
from openai import AsyncOpenAI
import logging
import aiofiles

logger = logging.getLogger(__name__)


class ChatGPTClient:
    def __init__(self):
        """Initializes the client using openai.AsyncOpenAI."""
        self.api_key = OPENAI_API_KEY

        self.client = AsyncOpenAI(api_key=self.api_key, timeout=30.0)
        logger.info("ChatGPTClient (openai.AsyncClient) initialized.")

    async def ask(
        self,
        current_user_prompt: str,
        history: list = None,
        system_prompt: str = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1500,
    ) -> str:
        """
        Asynchronously sends a request to ChatGPT via the official SDK.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": current_user_prompt})

        logger.debug(f"Sending request to OpenAI SDK: {messages}")

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
            )

            logger.debug(f"Response from OpenAI SDK: {chat_completion}")

            if chat_completion.choices and chat_completion.choices[0].message:
                return chat_completion.choices[0].message.content.strip()
            else:
                logger.error(
                    f"Unexpected response format from OpenAI SDK: {chat_completion}"
                )
                return "Sorry, I received a strange response."

        except Exception as e:
            logger.exception("Error calling OpenAI API via SDK:")
            return f"An error occurred while contacting ChatGPT: {e}"

    async def transcribe(self, file_path: str) -> str | None:
        """
        Asynchronously transcribes speech from an audio file using the Whisper API.
        """
        logger.info(f"Sending file {file_path} to Whisper for transcription.")
        try:
            async with aiofiles.open(file_path, "rb") as audio_file:
                audio_bytes = await audio_file.read()

            transcription = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=(os.path.basename(file_path), audio_bytes),
                response_format="text",
            )
            return transcription.strip() if isinstance(transcription, str) else None
        except Exception:
            logger.exception("Error calling Whisper API via SDK:")
            return None

    async def text_to_speech(
        self, text_to_convert: str, model: str = "tts-1-hd", voice: str = "nova"
    ) -> bytes | None:
        """
        Converts text to speech using the OpenAI TTS API and returns audio (bytes).
        """
        logger.info(
            f"Converting text to speech (voice: {voice}): '{text_to_convert[:50]}...'"
        )
        try:
            response = await self.client.audio.speech.create(
                model=model, voice=voice, input=text_to_convert
            )
            return response.content
        except Exception:
            logger.exception("Error calling OpenAI TTS API via SDK:")
            return None
