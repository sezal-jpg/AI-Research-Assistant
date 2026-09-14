from google.cloud import texttospeech
from app.core.logger import logger

class TTSService:

    def __init__(self):
        logger.info("Initializing Google Cloud TTS service")
        self.client = None

    def _get_client(self):
        if self.client is None:
            logger.info("Creating Google Cloud TTS client")
            self.client = texttospeech.TextToSpeechClient()
            logger.info("Google Cloud TTS client initialized successfully")
        return self.client

    def speak_to_file(self, text: str, output_path: str):
        logger.info(f"Generating speech: {output_path}")

        try:
            input_text = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Chirp3-HD-Charon"
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            client = self._get_client()

            response = client.synthesize_speech(
                input=input_text,
                voice=voice,
                audio_config=audio_config
            )

            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            logger.info("Speech generated successfully")
            logger.info(f"Audio saved to {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return None

tts_service = TTSService()