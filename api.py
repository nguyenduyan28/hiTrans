from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import json
from dotenv import load_dotenv
import os
from flask_caching import Cache

app = Flask(__name__)
CORS(app)
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')

client = genai.Client(api_key=GEMINI_API)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/translate', methods=['POST'])
@cache.cached(timeout=60, key_prefix=lambda: str(request.json))
def translate_text():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'en')
    target_lang = data.get('target_lang', 'vi')
    model = data.get('model', 'gemini-2.0-flash')
    temperature = data.get('temperature', 0.5)
    mode = data.get('mode', 'thông thường')
    translate_all = data.get('translate_all', False)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    style_desc = "học thuật" if mode == "học thuật" else "thông thường"
    prompt = f'''
    Translate the following text from {source_lang} to {target_lang} in the {style_desc} style:
    "{text}"
    - Style {style_desc}: {'Academic tone' if mode == 'học thuật' else 'Casual conversational tone'}.
    Use the {model} model with temperature {temperature}.
    Output in JSON format:
    {{
      "translated_text": "translated result here"
    }}
    Return only pure JSON, no markdown or extra text.
    '''

    response = client.models.generate_content(model=model, contents=prompt, temperature=temperature)
    clean_response = response.text.strip('```json').strip('```').strip()
    try:
        translated_data = json.loads(clean_response)
        return jsonify(translated_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid response from AI"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
