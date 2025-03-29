from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')

client = genai.Client(api_key=GEMINI_API)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    eng_str = data.get('text', '')
    mode = data.get('mode', 'thông thường')  # Mặc định là thông thường nếu không có mode
    if not eng_str:
        return jsonify({"error": "No text provided"}), 400

    # Chỉ dịch theo mode được chọn
    style_desc = "học thuật" if mode == "học thuật" else "thông thường"
    prompt = f'''
    Dịch câu "{eng_str}" sang tiếng Việt theo phong cách {style_desc}:
    - Phong cách {style_desc}: {'Dịch theo hướng học thuật' if mode == 'học thuật' else 'Dịch theo văn nói trong đời sống'}.
    Output đưa ra dưới dạng json như sau
    [
      {{"style": "{style_desc}", "translated_text": ["kết quả dịch"]}}
    ]
    Chỉ đưa ra output dưới dạng JSON thuần, không trả về dưới dạng markdown, không ghi gì thêm.
    '''

    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    clean_response = response.text.strip('```json').strip('```').strip()
    try:
        translated_data = json.loads(clean_response)
        print(jsonify(translated_data))
        return jsonify(translated_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid response from AI"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)