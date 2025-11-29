import speech_recognition as sr
import base64
import io
from pydub import AudioSegment


def speech_to_text(audio_base64):
    try:
        # Debug: print the size of the received base64 audio
        print("Received audio size:", len(audio_base64))

        # Decode base64
        audio_data = base64.b64decode(audio_base64)
        audio_stream = io.BytesIO(audio_data)

        # Let pydub detect the format automatically
        sound = AudioSegment.from_file(audio_stream)  # no format specified

        # Convert to wav (SpeechRecognition works best with WAV)
        wav_io = io.BytesIO()
        sound.export(wav_io, format="wav")
        wav_io.seek(0)

        # Recognize speech
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return {"text": text}

    except Exception as e:
        return {"error": str(e)}





