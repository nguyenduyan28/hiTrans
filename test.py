from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

GEMINI_API = os.getenv('GEMINI_API')

genai.configure(api_key=GEMINI_API)
def list_models():
    for i in genai.list_models():
        print(i.name)

if __name__ == "__main__":
    list_models()
