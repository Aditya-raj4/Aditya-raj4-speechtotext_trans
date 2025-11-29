# clientApp.py
import os
import base64
import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from PyPDF2 import PdfReader
import textToSPeech  # your TTS module

# Environment locale (keeps libraries happy with utf-8)
os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)

# Optional: set an upload limit (16 MB here — adjust as needed)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    """
    Expects JSON: { data: "<text>", source_lang: "auto", target_lang: "en" }
    Returns JSON: { data: "<base64-audio>" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    data = payload.get('data')
    source_lang = payload.get('source_lang', 'auto')
    target_lang = payload.get('target_lang', 'en')

    if not data:
        return jsonify({"error": "No text provided"}), 400

    try:
        result = textToSPeech.text2Speech(data, source_lang, target_lang)
        # assuming text2Speech returns bytes; encode to base64 string for JSON transport
        if isinstance(result, bytes):
            b64 = base64.b64encode(result).decode("utf-8")
            return jsonify({"data": b64})
        # if already returns a base64 str
        return jsonify({"data": result})
    except Exception as e:
        return jsonify({"error": f"TTS failed: {str(e)}"}), 500


@app.route("/speechToText", methods=['POST'])
@cross_origin()
def speechToTextRoute():
    """
    Accepts:
      - multipart/form-data with field 'file' (uploaded audio file), OR
      - application/json with { "audio": "<base64 string>" }
    Returns:
      - JSON { text: "..."} on success or { error: "..." } on failure
    """
    import speechToText  # your STT module

    # 1) File upload (multipart/form-data)
    if 'file' in request.files:
        audio_file = request.files.get('file')
        if audio_file and audio_file.filename != '':
            try:
                audio_bytes = audio_file.read()
                b64 = base64.b64encode(audio_bytes).decode('utf-8')
                result = speechToText.speech_to_text(b64)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": f"Failed to process uploaded file: {str(e)}"}), 500
        return jsonify({"error": "Uploaded file is empty"}), 400

    # 2) JSON with base64 audio
    payload = request.get_json(force=True, silent=True) or {}
    audio_b64 = payload.get('audio')
    if audio_b64:
        try:
            result = speechToText.speech_to_text(audio_b64)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": f"Failed to process base64 audio: {str(e)}"}), 500

    # nothing provided
    return jsonify({"error": "No audio provided. Send a file or base64 in JSON under 'audio'."}), 400


@app.route("/pdfToSpeech", methods=['POST'])
@cross_origin()
def pdfToSpeechRoute():
    """
    Accepts multipart/form-data with 'file' (PDF), optional form fields:
      - source_lang (default 'auto'), target_lang (default 'en')
    Returns JSON: { data: "<base64-audio>" } or { error: "..." }
    """
    pdf_file = request.files.get('file')
    if pdf_file is None:
        return jsonify({"error": "No PDF file provided"}), 400

    source_lang = request.form.get('source_lang', 'auto')
    target_lang = request.form.get('target_lang', 'en')

    try:
        reader = PdfReader(pdf_file)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            return jsonify({"error": "No extractable text found in the PDF"}), 400

        # Limit text length to avoid very large TTS requests
        MAX_CHARS = 4000
        if len(full_text) > MAX_CHARS:
            full_text = full_text[:MAX_CHARS]

        result = textToSPeech.text2Speech(full_text, source_lang, target_lang)
        if isinstance(result, bytes):
            b64 = base64.b64encode(result).decode("utf-8")
            return jsonify({"data": b64})
        return jsonify({"data": result})

    except Exception as e:
        return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500


if __name__ == "__main__":
    # dev mode; change host/port as needed for deployment
    app.run(host='127.0.0.1', port=5000, debug=True)



#My name is Aditya Raj. I live in Bengaluru, India.