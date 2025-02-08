import os
from dotenv import load_dotenv
import openai
from openai import OpenAI

# .env dosyasını yükle
load_dotenv()

# API anahtarını ayarla
openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Yeni API çağrısı
response = client.chat.completions.create(
    model="gpt-4o-mini",  # "gpt-4o-mini" modelini kontrol edin (varsa bu şekilde yazın)
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Bu bir test mesajıdır. GPT-4o Mini modeli çalışıyor mu?"}
    ]
)

# Yanıtı yazdır
print("OpenAI'den Gelen Yanıt:")
print(response.choices[0].message)