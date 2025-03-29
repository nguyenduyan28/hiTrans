from google import genai
import enum
from pydantic import BaseModel
import json

class Style(enum.Enum):
  Academic = "academic"
  Formal = "formal"
  


class Recipe(BaseModel):
  recipe_name : str
  rating: Style

client = genai.Client(api_key="AIzaSyDH-a0d0KdP8crAqojR89bDUPPoD2kq1MY")
chat = client.chats.create(model="gemini-2.0-flash")



eng_str = "This guy fuck a lot of girls."
prompt = f'''
Dịch câu {eng_str} sang tiếng Việt với phong cách được define trong như sau:
- Phong cách học thuật : Dịch theo hướng học thuật.
- Phong cách thông thường: Dịch theo văn nói trong đời sống.
Output đưa ra dưới dạng json như sau
[
  Recipe = {{'style' : str, 'translated_text' : list[str]}}
  Return: list[Recipe]
]
Chỉ đưa ra output dưới dạng JSON thuần, không trả về dưới dạng markdown, không ghi gì thêm.'''
respose =  client.models.generate_content(model='gemini-2.0-flash', contents=prompt)


print(respose.text)
lines = respose.text.split('\n')
lines.remove('```json')
lines.remove('```')
clean_response = ("\n".join(lines))

d = json.loads(clean_response)
for t in d:
  print(t)
