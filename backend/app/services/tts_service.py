import pyttsx3
from app.core.logger import logger

class TTSService:
        
   def speak_to_file(self, text: str, output_path: str):
    logger.info(f'Generating speech: {output_path}')
    engine = None

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'Zira' in voice.name:
                engine.setProperty('voice', voice.id)
                break

        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)

        engine.save_to_file(text, output_path)
        engine.runAndWait()
        engine.stop()

        logger.info('Speech generated successfully')
        return output_path

    except Exception as e:
        logger.error(f'TTS failed: {e}')
        return None

    finally:
        if engine is not None:
            try:
                engine.stop()
            except:
                pass 
        
tts_service=TTSService()        
                