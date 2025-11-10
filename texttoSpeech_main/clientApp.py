from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
import textToSPeech

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


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)


#My name is Aditya Raj. I live in Bengaluru, India.