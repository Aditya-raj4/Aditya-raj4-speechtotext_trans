from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
import textToSPeech
from PyPDF2 import PdfReader  # <-- NEW

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)


@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    data = request.json.get('data')
    source_lang = request.json.get('source_lang', 'auto')
    target_lang = request.json.get('target_lang', 'en')

    result = textToSPeech.text2Speech(data, source_lang, target_lang)
    return {"data": result.decode("utf-8")}


@app.route("/speechToText", methods=['POST'])
@cross_origin()
def speechToTextRoute():
    import speechToText
    data = request.json.get('audio')
    result = speechToText.speech_to_text(data)
    return jsonify(result)


# 🆕 New route: PDF → Text → Speech
@app.route("/pdfToSpeech", methods=['POST'])
@cross_origin()
def pdfToSpeechRoute():
    """
    Accepts a PDF file upload, extracts text,
    sends it to textToSPeech.text2Speech,
    and returns base64-encoded MP3 just like /predict.
    """

    pdf_file = request.files.get('file')
    if pdf_file is None:
        return jsonify({"error": "No PDF file provided"}), 400

    # Reuse same language settings
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

        # Optional: avoid gTTS failure on very large PDFs
        MAX_CHARS = 4000
        if len(full_text) > MAX_CHARS:
            full_text = full_text[:MAX_CHARS]

        result = textToSPeech.text2Speech(full_text, source_lang, target_lang)
        return {"data": result.decode("utf-8")}

    except Exception as e:
        return jsonify({"error": f"Failed to process PDF: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)




#My name is Aditya Raj. I live in Bengaluru, India.