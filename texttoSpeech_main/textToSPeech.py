from gtts import gTTS
from deep_translator import GoogleTranslator
import base64
import os

def text2Speech(data, source_lang='auto', target_lang='en'):
    try:
        # Step 1: Validate input
        if not data or not isinstance(data, str):
            raise ValueError("Input text must be a non-empty string")

        # Step 2: Translate text safely
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_text = translator.translate(data)

        if not translated_text:
            raise ValueError("Translation failed or returned empty text")

        # Step 3: Convert translated text to speech
        tts = gTTS(text=translated_text, lang=target_lang, slow=False)
        output_file = "converted-file.mp3"
        tts.save(output_file)

        # Step 4: Encode the audio to base64
        with open(output_file, "rb") as file:
            encoded_audio = base64.b64encode(file.read())

        # Step 5: Clean up temporary file
        if os.path.exists(output_file):
            os.remove(output_file)

        return encoded_audio

    except Exception as e:
        error_message = f"Error during processing: {str(e)}"
        print(error_message)
        return base64.b64encode(error_message.encode("utf-8"))
