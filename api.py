from flask import Flask, request, jsonify
import google.generativeai as genai
import json
import re  # Thêm regex để lọc JSON
import logging  # Thêm logging
from dotenv import load_dotenv
import os
from flask_caching import Cache

app = Flask(__name__)
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')

genai.configure(api_key=GEMINI_API)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})

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
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        clean_response = response.text.strip('```json').strip('```').strip()
        logger.info(f"Detect response raw: {response.text}")
        # Lọc chỉ lấy JSON đầu tiên
        json_match = re.search(r'\{.*?\}', clean_response, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            detected_data = json.loads(clean_json)
            return jsonify(detected_data)
        else:
            raise ValueError("No valid JSON found in response")
    except ValueError as ve:
        logger.error(f"Invalid JSON in detect: {str(ve)}, response: {response.text}")
        return jsonify({"detected_language": "unknown", "error": str(ve)}), 500
    except Exception as e:
        logger.error(f"Detect failed: {str(e)}")
        return jsonify({"detected_language": "unknown", "error": str(e)}), 500

@app.route('/translate', methods=['POST'])
@cache.cached(key_prefix=lambda: json.dumps(request.json, sort_keys=True))
def translate_text():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'unknown')
    target_lang = data.get('target_lang', 'vi')
    model_name = data.get('model', 'gemini-2.0-flash')
    temperature = data.get('temperature', 0.5)
    style = data.get('style', 'casual')
    translate_full = data.get('translate_full', False)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    valid_models = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-2.0-flash',
        'gemini-2.5-pro-preview-03-25'
    ]
    if model_name not in valid_models:
        return jsonify({"error": f"Invalid model: {model_name}. Valid models: {valid_models}"}), 400

    style_desc = {
        "academic": "academic tone suitable for scholarly writing",
        "professional": "formal tone suitable for professional documents",
        "casual": "casual conversational tone"
    }.get(style, "casual conversational tone")

    max_length = 2000
    if len(text) > max_length:
        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        translated_chunks = []
        try:
            model = genai.GenerativeModel(model_name, generation_config={"temperature": float(temperature)})
            for chunk in chunks:
                prompt = f'''
                Translate the following text from {source_lang} to {target_lang} with a {style_desc}:
                "{chunk}"
                Output in JSON format:
                {{
                  "translated_text": "translated result here"
                }}
                Return only pure JSON, no markdown or extra text.
                '''
                response = model.generate_content(prompt)
                clean_response = response.text.strip('```json').strip('```').strip()
                logger.info(f"Translate chunk response raw: {response.text}")
                # Lọc chỉ lấy JSON đầu tiên
                json_match = re.search(r'\{.*?\}', clean_response, re.DOTALL)
                if json_match:
                    clean_json = json_match.group(0)
                    translated_data = json.loads(clean_json)
                    translated_chunks.append(translated_data["translated_text"])
                else:
                    raise ValueError("No valid JSON found in response")
            return jsonify({"translated_text": " ".join(translated_chunks)})
        except ValueError as ve:
            logger.error(f"Invalid JSON in translate chunk: {str(ve)}, response: {response.text}")
            return jsonify({"error": f"Invalid JSON response: {str(ve)}"}), 500
        except Exception as e:
            logger.error(f"Translate chunk failed: {str(e)}")
            return jsonify({"error": f"Translation failed: {str(e)}"}), 500
    else:
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
            model = genai.GenerativeModel(model_name, generation_config={"temperature": float(temperature)})
            response = model.generate_content(prompt)
            clean_response = response.text.strip('```json').strip('```').strip()
            logger.info(f"Translate response raw: {response.text}")
            # Lọc chỉ lấy JSON đầu tiên
            json_match = re.search(r'\{.*?\}', clean_response, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
                translated_data = json.loads(clean_json)
                return jsonify(translated_data)
            else:
                raise ValueError("No valid JSON found in response")
        except ValueError as ve:
            logger.error(f"Invalid JSON in translate: {str(ve)}, response: {response.text}")
            return jsonify({"error": f"Invalid JSON response: {str(ve)}"}), 500
        except Exception as e:
            logger.error(f"Translate failed: {str(e)}")
            return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
