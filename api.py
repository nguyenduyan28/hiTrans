from flask import Flask, request, jsonify
from google import genai
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')

client = genai.Client(api_key=GEMINI_API)

@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"detected_language": "unknown"}), 400

    prompt = f'''
    Detect the language of this text: "{text}"
    Output in JSON format:
    {{
      "detected_language": "language_code"
    }}
    Return only pure JSON, no markdown or extra text.
    '''

    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        clean_response = response.text.strip('```json').strip('```').strip()
        detected_data = json.loads(clean_response)
        return jsonify(detected_data)
    except Exception as e:
        return jsonify({"detected_language": "unknown", "error": str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'unknown')
    target_lang = data.get('target_lang', 'vi')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    prompt = f'''
    Translate the following text from {source_lang} to {target_lang}:
    "{text}"
    Output in JSON format:
    {{
      "translated_text": "translated result here"
    }}
    Return only pure JSON, no markdown or extra text.
    '''

    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        clean_response = response.text.strip('```json').strip('```').strip()
        translated_data = json.loads(clean_response)
        return jsonify(translated_data)
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
