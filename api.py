from flask import Flask, request, jsonify
from google import genai
import json
from dotenv import load_dotenv
import os
from flask_caching import Cache

app = Flask(__name__)
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')

# Cấu hình Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})  # Cache 5 phút

client = genai.Client(api_key=GEMINI_API)

@app.route('/detect-language', methods=['POST'])
@cache.cached(key_prefix=lambda: json.dumps(request.json, sort_keys=True))
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
@cache.cached(key_prefix=lambda: json.dumps(request.json, sort_keys=True))
def translate_text():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'unknown')
    target_lang = data.get('target_lang', 'vi')
    model = data.get('model', 'gemini-2.0-flash')
    temperature = data.get('temperature', 0.5)
    style = data.get('style', 'casual')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    style_desc = {
        "academic": "academic tone suitable for scholarly writing",
        "professional": "formal tone suitable for professional documents",
        "casual": "casual conversational tone"
    }.get(style, "casual conversational tone")

    prompt = f'''
    Translate the following text from {source_lang} to {target_lang} with a {style_desc}:
    "{text}"
    Output in JSON format:
    {{
      "translated_text": "translated result here"
    }}
    Return only pure JSON, no markdown or extra text.
    '''

    try:
        response = client.models.generate_content(model=model, contents=prompt, temperature=temperature)
        clean_response = response.text.strip('```json').strip('```').strip()
        translated_data = json.loads(clean_response)
        return jsonify(translated_data)
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
