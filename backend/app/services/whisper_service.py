import av
from faster_whisper import WhisperModel
from app.core.logger import logger


class WhisperService:

    def __init__(self):
        logger.info("Loading Whisper model...")
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

        logger.info("Whisper model loaded successfully")

    def transcribe(self, audio_path: str):
        logger.info(f"Transcribing audio: {audio_path}")
        try:
            # Check whether the media file actually contains an audio stream.
            container = av.open(audio_path)

            audio_streams = list(container.streams.audio)

            container.close()

            if not audio_streams:
                logger.info(
                    f"No audio stream found in {audio_path}. "
                    "Skipping Whisper transcription."
                )
                return ""

            # Transcribe the audio/video file.
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5
            )

            transcript = []

            for segment in segments:
                text = segment.text.strip()

                if text:
                    transcript.append(text)
            text = " ".join(transcript).strip()

            logger.info(
                f"Transcription completed: {len(text)} characters"
            )

            return text

        except Exception as e:

            logger.error(
                f"Whisper transcription failed: {e}"
            )
            return ""

whisper_service = WhisperService()