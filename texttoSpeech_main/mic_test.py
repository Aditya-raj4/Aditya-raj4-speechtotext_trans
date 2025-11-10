import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("🎤 Say something...")
    audio = r.listen(source)
    print("🧠 Recognizing...")

try:
    text = r.recognize_google(audio)
    print("✅ You said:", text)
except Exception as e:
    print("❌ Error:", e)
